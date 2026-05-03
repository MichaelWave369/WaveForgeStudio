import json
import subprocess
import sys

from waveforge_studio.release_build import write_release_build
from waveforge_studio.release_build_zip import write_release_build_zip
from waveforge_studio.release_build_verification import write_release_build_verification
from waveforge_studio.release_certificate import write_release_certificate
from waveforge_studio.certificate_bundle import write_certificate_bundle
from waveforge_studio.certificate_bundle_zip import write_certificate_bundle_zip
from waveforge_studio.release_build_index import create_release_build_index_manifest, write_release_build_index, validate_release_build_index_manifest, read_release_build_index_info


def _setup(tmp_path, full=True):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','one','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','two','--out',str(tmp_path/'two'),'--seed','123','--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    b=tmp_path/'release_build'
    write_release_build(tmp_path,b,title='Golden Signal Release',include_tags=['has-zip'])
    if full:
        write_release_build_zip(b); write_release_build_verification(b); write_release_certificate(b); write_certificate_bundle(b); write_certificate_bundle_zip(b/'certificate_bundle')
    return env,b


def test_release_build_index(tmp_path):
    env,b=_setup(tmp_path,full=True)
    m=create_release_build_index_manifest(b)
    assert m['schema']=='waveforge.release_build_index_manifest.v2_alpha'
    m2=create_release_build_index_manifest(b)
    assert m['receipt']['release_build_index_hash']==m2['receipt']['release_build_index_hash']

    env2,b2=_setup(tmp_path/'missing',full=False)
    m_missing=create_release_build_index_manifest(b2)
    assert m_missing['links']['certificate_bundle_zip']['present'] is False

    assert not validate_release_build_index_manifest(m)
    bad=json.loads(json.dumps(m)); bad['index_policy']['external_calls_allowed']=True
    assert validate_release_build_index_manifest(bad)
    bad2=json.loads(json.dumps(m)); bad2['links']['gallery']['path']='/abs'
    assert validate_release_build_index_manifest(bad2)

    w=write_release_build_index(b)
    for f in ['index.html','release_build_index_manifest.json','release_build_index_receipt.json','RELEASE_BUILD_INDEX_SUMMARY.md']:
        assert (b/f).exists()
    info=read_release_build_index_info(b)
    assert info['index_exists'] and info['contains_waveforge']

    html=(b/'index.html').read_text(encoding='utf-8')
    for s in ['Open Release Deck','Open Gallery','Download Release Build ZIP','Download Certificate Bundle ZIP','View Release Certificate','View Verification Report']:
        assert s in html

    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build-index',str(b)],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build-index-validate',str(b/'release_build_index_manifest.json')],capture_output=True,text=True,env=env).returncode==0

    out=tmp_path/'inline'
    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build',str(tmp_path),'--out',str(out),'--title','Golden Signal Release','--include-tag','has-zip','--zip','--verify','--certify','--certificate-bundle','--certificate-bundle-zip','--index'],capture_output=True,text=True,env=env)
    assert r.returncode==0 and (out/'index.html').exists()

    m3=create_release_build_index_manifest(b)
    assert all(not str(v['path']).startswith('/') for v in m3['links'].values())
