import json
import subprocess
import sys
from zipfile import ZipFile

from waveforge_studio.release_deck_zip import create_release_deck_zip_manifest, read_release_deck_zip_info, validate_release_deck_zip_manifest, write_release_deck_zip


def _setup(tmp_path):
    env={"PYTHONPATH":"src"}
    cmds=[
      ['forge','one','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],
      ['forge','two','--out',str(tmp_path/'two'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],
      ['gallery',str(tmp_path),'--out',str(tmp_path/'gallery')],
      ['collection',str(tmp_path/'gallery/gallery_manifest.json'),'--out',str(tmp_path/'gallery/collection'),'--title','Golden Signal Release','--include-tag','has-zip'],
      ['collection-export',str(tmp_path/'gallery/collection/collection_manifest.json'),'--out',str(tmp_path/'gallery/collection_export')],
      ['release-deck',str(tmp_path/'gallery/collection_export/collection_export_manifest.json'),'--out',str(tmp_path/'gallery/collection_export/release_deck'),'--title','Golden Signal Release Deck']]
    for c in cmds: subprocess.run([sys.executable,'-m','waveforge_studio.cli',*c],check=True,env=env)
    return env, tmp_path/'gallery/collection_export/release_deck'


def test_release_deck_zip(tmp_path):
    env, deck = _setup(tmp_path)
    m=create_release_deck_zip_manifest(deck)
    assert m['schema']=='waveforge.release_deck_zip_manifest.v2_alpha'
    m2=create_release_deck_zip_manifest(deck)
    assert m['receipt']['release_deck_zip_hash']==m2['receipt']['release_deck_zip_hash']
    bad=json.loads(json.dumps(m)); bad['files']=[f for f in bad['files'] if f['path']!='index.html']
    assert validate_release_deck_zip_manifest(bad)
    bad2=json.loads(json.dumps(m)); bad2['zip_policy']['external_calls_allowed']=True
    assert validate_release_deck_zip_manifest(bad2)

    w=write_release_deck_zip(deck)
    for f in ['release_deck.zip','release_deck_zip_manifest.json','release_deck_zip_receipt.json','RELEASE_DECK_ZIP_SUMMARY.md']:
        assert (deck/f).exists()
    info=read_release_deck_zip_info(deck/'release_deck.zip')
    assert info['exists'] and info['contains_index'] and info['contains_markdown'] and info['card_count']>0 and info['sha256']

    env2, deck2 = _setup(tmp_path/'b')
    w2=write_release_deck_zip(deck2)
    assert w['receipt']['zip_file_sha256']==w2['receipt']['zip_file_sha256']

    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','zip-release-deck',str(deck)],capture_output=True,text=True,env=env)
    assert r.returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-deck-zip-validate',str(deck/'release_deck_zip_manifest.json')],capture_output=True,text=True,env=env).returncode==0

    with ZipFile(deck/'release_deck.zip','r') as zf:
        names=zf.namelist()
        assert 'release_deck_zip_manifest.json' not in names and 'release_deck_zip_receipt.json' not in names and 'RELEASE_DECK_ZIP_SUMMARY.md' not in names
        assert all(not n.startswith('/') for n in names)
