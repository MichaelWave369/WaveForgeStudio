import json
import subprocess
import sys

from waveforge_studio.final_release import create_final_release_manifest, write_final_release, validate_final_release_manifest, read_final_release_info


def _setup_runs(tmp_path):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Final Release Demo One','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Final Release Demo Two','--out',str(tmp_path/'two'),'--seed','123','--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    return env


def test_final_release(tmp_path):
    env=_setup_runs(tmp_path)
    p=create_final_release_manifest(tmp_path,title='Golden Signal Release',include_tags=['has-zip'])
    assert p['schema']=='waveforge.final_release_manifest.v2_alpha'
    assert p['stages']['release_build']['status']=='planned'

    w=write_final_release(tmp_path,tmp_path/'final_release',title='Golden Signal Release',include_tags=['has-zip'])
    f=tmp_path/'final_release'
    for path in ['index.html','release_build.zip','certificate_bundle/certificate_bundle.zip','final_release_manifest.json','final_release_receipt.json','FINAL_RELEASE_SUMMARY.md']:
        assert (f/path).exists()
    assert all(w['stages'][k]['status']=='completed' for k in ['release_build','release_build_zip','verification','certificate','certificate_bundle','certificate_bundle_zip','index'])
    assert w['stages']['verification']['passed'] is True
    assert w['stages']['certificate']['certificate_status'] in {'certified','certified_with_warnings'}

    w2=write_final_release(tmp_path,tmp_path/'final_release_2',title='Golden Signal Release',include_tags=['has-zip'])
    assert not validate_final_release_manifest(w)
    bad=json.loads(json.dumps(w)); bad['final_policy']['external_calls_allowed']=True
    assert validate_final_release_manifest(bad)
    bad2=json.loads(json.dumps(w)); del bad2['stages']['index']
    assert validate_final_release_manifest(bad2)

    info=read_final_release_info(f)
    assert info['index_exists'] and info['release_build_zip_exists'] and info['certificate_bundle_zip_exists'] and info['contains_waveforge']

    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final_release_cli'),'--title','Golden Signal Release','--include-tag','has-zip'],capture_output=True,text=True,env=env)
    assert r.returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','final-release-validate',str(tmp_path/'final_release_cli/final_release_manifest.json')],capture_output=True,text=True,env=env).returncode==0
