import json
import subprocess
import sys

from waveforge_studio.gallery_collection import create_gallery_collection_manifest, read_gallery_collection_info, validate_gallery_collection_manifest, write_gallery_collection


def _prep(tmp_path):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','one','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','two','--out',str(tmp_path/'two'),'--seed','123','--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','gallery',str(tmp_path),'--out',str(tmp_path/'gallery')],check=True,env=env)
    gm=json.loads((tmp_path/'gallery/gallery_manifest.json').read_text(encoding='utf-8'))
    return env, gm


def test_collection_manifest_and_writer(tmp_path):
    env, gm = _prep(tmp_path)
    m = create_gallery_collection_manifest(gm)
    assert m['schema']=='waveforge.gallery_collection_manifest.v1_alpha'
    assert m['run_count']==len(gm['runs'])

    paths=[gm['runs'][1]['run_path'], 'missing_path', gm['runs'][0]['run_path']]
    m2=create_gallery_collection_manifest(gm, include_run_paths=paths)
    assert [r['run_path'] for r in m2['runs']] == [gm['runs'][1]['run_path'], gm['runs'][0]['run_path']]
    assert 'missing_path' in m2['selection']['missing_run_paths']

    m3=create_gallery_collection_manifest(gm, include_tags=['has-zip'])
    assert all('has-zip' in r.get('tags',[]) for r in m3['runs'])
    m4=create_gallery_collection_manifest(gm, exclude_tags=['has-zip'])
    assert all('has-zip' not in r.get('tags',[]) for r in m4['runs'])
    assert m3['available_tags']==sorted(m3['available_tags'])

    m5=create_gallery_collection_manifest(gm, include_tags=['has-zip'])
    assert m3['receipt']['collection_hash']==m5['receipt']['collection_hash']
    assert not validate_gallery_collection_manifest(m)
    bad=json.loads(json.dumps(m)); bad['collection_policy']['external_calls_allowed']=True
    assert validate_gallery_collection_manifest(bad)
    bad2=json.loads(json.dumps(m)); bad2['run_count']=999
    assert validate_gallery_collection_manifest(bad2)

    out=write_gallery_collection(tmp_path/'gallery/gallery_manifest.json', title='Golden Signal Showcase', include_tags=['has-zip'])
    c=tmp_path/'gallery/collection'
    for f in ['index.html','collection_manifest.json','collection_receipt.json','COLLECTION_SUMMARY.md']:
        assert (c/f).exists()
    info=read_gallery_collection_info(c)
    assert info['index_exists'] and info['contains_waveforge']
    for r in out['runs']:
        for v in r['links'].values():
            if v: assert not v.startswith('/')

    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','collection',str(tmp_path/'gallery/gallery_manifest.json'),'--out',str(tmp_path/'gallery/collection2'),'--title','Golden Signal Showcase','--include-tag','has-zip'],capture_output=True,text=True,env=env)
    assert r.returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','collection-validate',str(tmp_path/'gallery/collection2/collection_manifest.json')],capture_output=True,text=True,env=env).returncode==0
