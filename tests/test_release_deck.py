import json
import subprocess
import sys

from waveforge_studio.release_deck import create_release_deck_manifest, read_release_deck_info, validate_release_deck_manifest, write_release_deck


def _setup(tmp_path):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','one','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','two','--out',str(tmp_path/'two'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','gallery',str(tmp_path),'--out',str(tmp_path/'gallery')],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','collection',str(tmp_path/'gallery/gallery_manifest.json'),'--out',str(tmp_path/'gallery/collection'),'--title','Golden Signal Release','--include-tag','has-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','collection-export',str(tmp_path/'gallery/collection/collection_manifest.json'),'--out',str(tmp_path/'gallery/collection_export')],check=True,env=env)
    cem=json.loads((tmp_path/'gallery/collection_export/collection_export_manifest.json').read_text(encoding='utf-8'))
    return env,cem


def test_release_deck(tmp_path):
    env,cem=_setup(tmp_path)
    m=create_release_deck_manifest(cem, tmp_path/'gallery/collection_export/collection_export_manifest.json', title=None)
    assert m['schema']=='waveforge.release_deck_manifest.v2_alpha'
    assert m['title']=='Golden Signal Release'
    assert m['card_count']==len(cem['runs'])
    assert [c['run_path'] for c in m['cards']] == [r['run_path'] for r in cem['runs']]
    m2=create_release_deck_manifest(cem, tmp_path/'gallery/collection_export/collection_export_manifest.json')
    assert m['receipt']['release_deck_hash']==m2['receipt']['release_deck_hash']
    assert not validate_release_deck_manifest(m)
    bad=json.loads(json.dumps(m)); bad['deck_policy']['external_calls_allowed']=True
    assert validate_release_deck_manifest(bad)
    bad2=json.loads(json.dumps(m)); bad2['card_count']=999
    assert validate_release_deck_manifest(bad2)

    out=write_release_deck(tmp_path/'gallery/collection_export/collection_export_manifest.json')
    d=tmp_path/'gallery/collection_export/release_deck'
    for f in ['index.html','RELEASE_DECK.md','release_deck_manifest.json','release_deck_receipt.json','cards/card_001.html']:
        assert (d/f).exists()
    info=read_release_deck_info(d)
    assert info['index_exists'] and info['contains_waveforge']
    assert not (d/'runs').exists()
    for c in out['cards']:
        for v in c['links'].values():
            if v: assert not v.startswith('/')

    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-deck',str(tmp_path/'gallery/collection_export/collection_export_manifest.json'),'--out',str(tmp_path/'gallery/collection_export/release_deck2'),'--title','Golden Signal Release Deck'],capture_output=True,text=True,env=env)
    assert r.returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-deck-validate',str(tmp_path/'gallery/collection_export/release_deck2/release_deck_manifest.json')],capture_output=True,text=True,env=env).returncode==0
