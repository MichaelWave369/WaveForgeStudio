import json
import subprocess
import sys

from waveforge_studio.collection_export import create_collection_export_manifest, read_collection_export_info, validate_collection_export_manifest, write_collection_export


def _setup(tmp_path):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','one','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','two','--out',str(tmp_path/'two'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','gallery',str(tmp_path),'--out',str(tmp_path/'gallery')],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','collection',str(tmp_path/'gallery/gallery_manifest.json'),'--out',str(tmp_path/'gallery/collection'),'--title','Golden Signal Release'],check=True,env=env)
    cm=json.loads((tmp_path/'gallery/collection/collection_manifest.json').read_text(encoding='utf-8'))
    return env, cm


def test_collection_export(tmp_path):
    env, cm = _setup(tmp_path)
    m=create_collection_export_manifest(cm, tmp_path/'gallery/collection/collection_manifest.json')
    assert m['schema']=='waveforge.collection_export_manifest.v1_alpha'
    assert [r['run_path'] for r in m['runs']] == [r['run_path'] for r in cm['runs']]
    m2=create_collection_export_manifest(cm, tmp_path/'gallery/collection/collection_manifest.json')
    assert m['receipt']['collection_export_hash']==m2['receipt']['collection_export_hash']
    assert m['missing_zip_count']>=1
    assert not validate_collection_export_manifest(m)
    bad=json.loads(json.dumps(m)); bad['export_policy']['external_calls_allowed']=True
    assert validate_collection_export_manifest(bad)
    bad2=json.loads(json.dumps(m)); bad2['run_count']=999
    assert validate_collection_export_manifest(bad2)

    out=write_collection_export(tmp_path/'gallery/collection/collection_manifest.json')
    e=tmp_path/'gallery/collection/collection_export'
    for f in ['index.html','collection_export_manifest.json','collection_export_receipt.json','COLLECTION_EXPORT_SUMMARY.md','collection/collection_manifest.json']:
        assert (e/f).exists()
    assert any((e/'runs'/r['export_id']/'run_summary.json').exists() for r in out['runs'])
    assert any((e/'runs'/r['export_id']/'preview_pack.zip').exists() for r in out['runs'] if r['present']['preview_pack_zip'])
    info=read_collection_export_info(e)
    assert info['index_exists'] and info['contains_waveforge']
    # no full run directory copy
    assert not (e/'runs/one/render').exists()
    for r in out['runs']:
        for v in r['target'].values():
            assert not str(v).startswith('/')

    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','collection-export',str(tmp_path/'gallery/collection/collection_manifest.json'),'--out',str(tmp_path/'gallery/collection/collection_export2')],capture_output=True,text=True,env=env)
    assert r.returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','collection-export-validate',str(tmp_path/'gallery/collection/collection_export2/collection_export_manifest.json')],capture_output=True,text=True,env=env).returncode==0
