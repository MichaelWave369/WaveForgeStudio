import json
import subprocess
import sys
from zipfile import ZipFile

from waveforge_studio.release_build import write_release_build
from waveforge_studio.release_build_zip import write_release_build_zip
from waveforge_studio.release_build_verification import write_release_build_verification
from waveforge_studio.release_certificate import write_release_certificate
from waveforge_studio.certificate_bundle import write_certificate_bundle
from waveforge_studio.certificate_bundle_zip import create_certificate_bundle_zip_manifest, write_certificate_bundle_zip, validate_certificate_bundle_zip_manifest, read_certificate_bundle_zip_info


def _setup(tmp_path):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','one','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','two','--out',str(tmp_path/'two'),'--seed','123','--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    b=tmp_path/'release_build'
    write_release_build(tmp_path,b,title='Golden Signal Release',include_tags=['has-zip'])
    write_release_build_zip(b); write_release_build_verification(b); write_release_certificate(b); write_certificate_bundle(b)
    return env,b/'certificate_bundle'


def test_certificate_bundle_zip(tmp_path):
    env,bundle=_setup(tmp_path)
    m=create_certificate_bundle_zip_manifest(bundle)
    assert m['schema']=='waveforge.certificate_bundle_zip_manifest.v2_alpha'
    m2=create_certificate_bundle_zip_manifest(bundle)
    assert m['receipt']['certificate_bundle_zip_hash']==m2['receipt']['certificate_bundle_zip_hash']
    bad=json.loads(json.dumps(m)); bad['files']=[f for f in bad['files'] if f['path']!='certificate_bundle_manifest.json']
    assert validate_certificate_bundle_zip_manifest(bad)
    bad2=json.loads(json.dumps(m)); bad2['zip_policy']['external_calls_allowed']=True
    assert validate_certificate_bundle_zip_manifest(bad2)

    w=write_certificate_bundle_zip(bundle)
    for f in ['certificate_bundle.zip','certificate_bundle_zip_manifest.json','certificate_bundle_zip_receipt.json','CERTIFICATE_BUNDLE_ZIP_SUMMARY.md']:
        assert (bundle/f).exists()
    info=read_certificate_bundle_zip_info(bundle/'certificate_bundle.zip')
    assert info['exists'] and info['contains_certificate'] and info['contains_verification'] and info['contains_bundle_manifest'] and info['sha256']

    w2=write_certificate_bundle_zip(bundle)
    assert w['receipt']['zip_file_sha256']==w2['receipt']['zip_file_sha256']

    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','zip-certificate-bundle',str(bundle)],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','certificate-bundle-zip-validate',str(bundle/'certificate_bundle_zip_manifest.json')],capture_output=True,text=True,env=env).returncode==0

    out=tmp_path/'inline'
    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build',str(tmp_path),'--out',str(out),'--title','Golden Signal Release','--include-tag','has-zip','--zip','--verify','--certify','--certificate-bundle','--certificate-bundle-zip'],capture_output=True,text=True,env=env)
    assert r.returncode==0 and (out/'certificate_bundle/certificate_bundle.zip').exists()

    with ZipFile(bundle/'certificate_bundle.zip','r') as zf:
        names=zf.namelist()
        assert 'certificate_bundle_zip_manifest.json' not in names and 'certificate_bundle_zip_receipt.json' not in names and 'CERTIFICATE_BUNDLE_ZIP_SUMMARY.md' not in names
        assert all(not n.startswith('/') for n in names)
