import subprocess
import sys

from waveforge_studio.release_build import write_release_build
from waveforge_studio.release_build_zip import write_release_build_zip
from waveforge_studio.release_build_verification import write_release_build_verification
from waveforge_studio.release_certificate import write_release_certificate
from waveforge_studio.certificate_bundle import create_certificate_bundle_manifest, write_certificate_bundle, validate_certificate_bundle_manifest, read_certificate_bundle_info


def _setup(tmp_path):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','one','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','two','--out',str(tmp_path/'two'),'--seed','123','--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    b=tmp_path/'release_build'
    write_release_build(tmp_path,b,title='Golden Signal Release',include_tags=['has-zip'])
    write_release_build_zip(b); write_release_build_verification(b); write_release_certificate(b)
    return env,b


def test_certificate_bundle(tmp_path):
    env,b=_setup(tmp_path)
    m=create_certificate_bundle_manifest(b)
    assert m['schema']=='waveforge.certificate_bundle_manifest.v2_alpha'
    assert not any(e['target']=='release_build.zip' for e in m['evidence'])
    m2=create_certificate_bundle_manifest(b,include_zip_file=True)
    assert any(e['target']=='release_build.zip' for e in m2['evidence'])
    assert m['required_missing']==[]
    assert not validate_certificate_bundle_manifest(m)
    bad=dict(m); bad['bundle_policy']=dict(m['bundle_policy']); bad['bundle_policy']['external_calls_allowed']=True
    assert validate_certificate_bundle_manifest(bad)
    bad2=dict(m); bad2['required_missing']=['x']
    assert validate_certificate_bundle_manifest(bad2)

    w=write_certificate_bundle(b)
    for f in ['certificate_bundle/certificate_bundle_manifest.json','certificate_bundle/certificate_bundle_receipt.json','certificate_bundle/CERTIFICATE_BUNDLE_SUMMARY.md','certificate_bundle/release_certificate.json','certificate_bundle/release_build_verification.json','certificate_bundle/release_build_manifest.json']:
        assert (b/f).exists()

    (b/'release_certificate.json').unlink()
    write_certificate_bundle(b)
    assert (b/'release_certificate.json').exists()

    info=read_certificate_bundle_info(b/'certificate_bundle')
    assert info['certificate_exists'] and info['contains_waveforge']

    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','certificate-bundle',str(b)],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','certificate-bundle-validate',str(b/'certificate_bundle/certificate_bundle_manifest.json')],capture_output=True,text=True,env=env).returncode==0

    out=tmp_path/'inline'
    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build',str(tmp_path),'--out',str(out),'--title','Golden Signal Release','--include-tag','has-zip','--zip','--verify','--certify','--certificate-bundle'],capture_output=True,text=True,env=env)
    assert r.returncode==0 and (out/'certificate_bundle/certificate_bundle_manifest.json').exists()
    out2=tmp_path/'inline2'
    r2=subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build',str(tmp_path),'--out',str(out2),'--title','Golden Signal Release','--include-tag','has-zip','--zip','--verify','--certify','--certificate-bundle','--certificate-bundle-include-zip'],capture_output=True,text=True,env=env)
    assert r2.returncode==0 and (out2/'certificate_bundle/release_build.zip').exists()

    w1=write_certificate_bundle(b); w2=write_certificate_bundle(b)
    assert w1['receipt']['certificate_bundle_hash']==w2['receipt']['certificate_bundle_hash']
    assert all(not str(e['target']).startswith('/') for e in w1['evidence'])
