import json
import subprocess
import sys

from waveforge_studio.demo_gallery import create_gallery_manifest, discover_waveforge_runs, read_gallery_info, validate_gallery_manifest, write_demo_gallery


def test_discover_empty(tmp_path):
    assert discover_waveforge_runs(tmp_path) == []


def test_gallery_end_to_end(tmp_path):
    env={"PYTHONPATH":"src"}
    run1=tmp_path/'demo1'; run2=tmp_path/'demo2'
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','one','--out',str(run1)],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','two','--out',str(run2),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)

    runs=discover_waveforge_runs(tmp_path)
    assert len(runs) >= 2
    assert runs == sorted(runs, key=lambda x: x['run_path'])

    m1=create_gallery_manifest(tmp_path)
    m2=create_gallery_manifest(tmp_path)
    assert m1['schema']=='waveforge.demo_gallery_manifest.v1_alpha'
    assert m1['receipt']['gallery_hash']==m2['receipt']['gallery_hash']
    assert not validate_gallery_manifest(m1)

    bad=json.loads(json.dumps(m1)); bad['gallery_policy']['external_calls_allowed']=True
    assert validate_gallery_manifest(bad)
    bad2=json.loads(json.dumps(m1)); bad2['run_count']=999
    assert validate_gallery_manifest(bad2)

    m=write_demo_gallery(tmp_path)
    g=tmp_path/'gallery'
    for f in ['index.html','gallery_manifest.json','gallery_receipt.json','GALLERY_SUMMARY.md']:
        assert (g/f).exists()
    info=read_gallery_info(g)
    assert info['index_exists'] and info['contains_waveforge']
    assert any(r['present']['preview_pack_zip'] for r in m['runs'])
    for r in m['runs']:
        for v in r['links'].values():
            if v:
                assert not v.startswith('/')

    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','gallery',str(tmp_path),'--out',str(tmp_path/'gallery2')],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','gallery-validate',str(tmp_path/'gallery2/gallery_manifest.json')],capture_output=True,text=True,env=env).returncode==0
