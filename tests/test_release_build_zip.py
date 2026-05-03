import json
import subprocess
import sys
from zipfile import ZipFile

from waveforge_studio.release_build import write_release_build
from waveforge_studio.release_build_zip import create_release_build_zip_manifest, read_release_build_zip_info, validate_release_build_zip_manifest, write_release_build_zip


def _setup(tmp_path):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','one','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','two','--out',str(tmp_path/'two'),'--seed','123','--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    write_release_build(tmp_path, tmp_path/'release_build', title='Golden Signal Release', include_tags=['has-zip'])
    return env, tmp_path/'release_build'


def test_release_build_zip(tmp_path):
    env, build_dir = _setup(tmp_path)
    m=create_release_build_zip_manifest(build_dir)
    assert m['schema']=='waveforge.release_build_zip_manifest.v2_alpha'
    m2=create_release_build_zip_manifest(build_dir)
    assert m['receipt']['release_build_zip_hash']==m2['receipt']['release_build_zip_hash']

    bad=json.loads(json.dumps(m)); bad['files']=[f for f in bad['files'] if f['path']!='release_build_manifest.json']
    assert validate_release_build_zip_manifest(bad)
    bad2=json.loads(json.dumps(m)); bad2['zip_policy']['external_calls_allowed']=True
    assert validate_release_build_zip_manifest(bad2)

    w=write_release_build_zip(build_dir)
    for f in ['release_build.zip','release_build_zip_manifest.json','release_build_zip_receipt.json','RELEASE_BUILD_ZIP_SUMMARY.md']:
        assert (build_dir/f).exists()

    info=read_release_build_zip_info(build_dir/'release_build.zip')
    assert info['exists'] and info['contains_release_build_manifest'] and info['contains_gallery_manifest'] and info['contains_collection_manifest'] and info['contains_release_deck_zip'] and info['sha256']

    w2=write_release_build_zip(build_dir)
    assert w['receipt']['zip_file_sha256']==w2['receipt']['zip_file_sha256']

    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','zip-release-build',str(build_dir)],capture_output=True,text=True,env=env)
    assert r.returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build-zip-validate',str(build_dir/'release_build_zip_manifest.json')],capture_output=True,text=True,env=env).returncode==0

    rb=subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build',str(tmp_path),'--out',str(tmp_path/'release_build_inline'),'--title','Golden Signal Release','--include-tag','has-zip','--zip'],capture_output=True,text=True,env=env)
    assert rb.returncode==0
    assert (tmp_path/'release_build_inline/release_build.zip').exists()

    with ZipFile(build_dir/'release_build.zip','r') as zf:
        names=zf.namelist()
        assert 'release_build_zip_manifest.json' not in names and 'release_build_zip_receipt.json' not in names and 'RELEASE_BUILD_ZIP_SUMMARY.md' not in names
        assert all(not n.startswith('/') for n in names)
