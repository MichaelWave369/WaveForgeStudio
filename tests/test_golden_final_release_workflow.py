import json, subprocess, sys

def test_golden_final_release_workflow(tmp_path):
    env={'PYTHONPATH':'src'}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Golden Demo One','--out',str(tmp_path/'golden_demo_one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Golden Demo Two','--out',str(tmp_path/'golden_demo_two'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final_release'),'--title','Golden Signal Release','--include-tag','has-zip'],check=True,env=env)
    fr=tmp_path/'final_release'
    for p in ['index.html','release_build.zip','certificate_bundle/certificate_bundle.zip','final_release_manifest.json','final_release_receipt.json','FINAL_RELEASE_SUMMARY.md','RELEASE_CERTIFICATE.md','RELEASE_BUILD_VERIFICATION.md']:
        assert (fr/p).exists()
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','final-release-validate',str(fr/'final_release_manifest.json')],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','verify-release-build',str(fr),'--strict'],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-certificate-validate',str(fr/'release_certificate.json')],capture_output=True,text=True,env=env).returncode==0
    m=json.loads((fr/'final_release_manifest.json').read_text(encoding='utf-8'))
    assert m['stages']['verification']['passed'] is True
    assert m['stages']['certificate']['certificate_status'] in {'certified','certified_with_warnings'}
    assert all(not str(v['path']).startswith('/') for v in m['stages'].values())
