import json
import subprocess
import sys

from waveforge_studio.release_build import write_release_build
from waveforge_studio.release_build_verification import write_release_build_verification
from waveforge_studio.release_build_zip import write_release_build_zip
from waveforge_studio.release_certificate import create_release_certificate, write_release_certificate, validate_release_certificate


def _setup(tmp_path):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','one','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','two','--out',str(tmp_path/'two'),'--seed','123','--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    b=tmp_path/'release_build'
    write_release_build(tmp_path,b,title='Golden Signal Release',include_tags=['has-zip'])
    write_release_build_zip(b)
    write_release_build_verification(b,strict=False)
    return env,b


def test_release_certificate(tmp_path):
    env,b=_setup(tmp_path)
    c=create_release_certificate(b)
    assert c['schema']=='waveforge.release_certificate.v2_alpha'
    assert c['certificate_status'] in {'certified','certified_with_warnings'}
    w=write_release_certificate(b)
    for f in ['release_certificate.json','release_certificate_receipt.json','RELEASE_CERTIFICATE.md']:
        assert (b/f).exists()
    assert not validate_release_certificate(w)
    bad=json.loads(json.dumps(w)); bad['certificate_status']='bad'
    assert validate_release_certificate(bad)
    bad2=json.loads(json.dumps(w)); bad2['certificate_status']='certified'; bad2['verification']['passed']=False
    assert validate_release_certificate(bad2)

    (b/'release_build_verification.json').unlink()
    write_release_certificate(b)
    assert (b/'release_build_verification.json').exists()

    (b/'release_build_zip_manifest.json').unlink()
    c2=write_release_certificate(b)
    assert c2['hashes']['release_build_zip_hash'] is None

    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','certify-release-build',str(b)],capture_output=True,text=True,env=env)
    assert r.returncode==0
    r2=subprocess.run([sys.executable,'-m','waveforge_studio.cli','certify-release-build',str(b),'--require-passed'],capture_output=True,text=True,env=env)
    assert r2.returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-certificate-validate',str(b/'release_certificate.json')],capture_output=True,text=True,env=env).returncode==0

    out=tmp_path/'inline'
    r3=subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build',str(tmp_path),'--out',str(out),'--title','Golden Signal Release','--include-tag','has-zip','--zip','--verify','--certify'],capture_output=True,text=True,env=env)
    assert r3.returncode==0 and (out/'release_certificate.json').exists()

    c3=write_release_certificate(b)
    c4=write_release_certificate(b)
    assert c3['receipt']['release_certificate_hash']==c4['receipt']['release_certificate_hash']
    assert 'not cryptographically signed' in (b/'RELEASE_CERTIFICATE.md').read_text(encoding='utf-8').lower()
