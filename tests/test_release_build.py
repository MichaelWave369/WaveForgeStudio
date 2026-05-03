import json
import subprocess
import sys

from waveforge_studio.release_build import create_release_build_manifest, read_release_build_info, validate_release_build_manifest, write_release_build


def _setup(tmp_path):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','one','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','two','--out',str(tmp_path/'two'),'--seed','123','--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    return env


def test_release_build(tmp_path):
    env=_setup(tmp_path)
    m=create_release_build_manifest(tmp_path, title='Golden Signal Release', include_tags=['has-zip'])
    assert m['schema']=='waveforge.release_build_manifest.v2_alpha'
    assert m['stages']['gallery']['status']=='planned'

    out=write_release_build(tmp_path, tmp_path/'release_build', title='Golden Signal Release', include_tags=['has-zip'])
    b=tmp_path/'release_build'
    for f in ['gallery/gallery_manifest.json','collection/collection_manifest.json','collection_export/collection_export_manifest.json','release_deck/release_deck_manifest.json','release_deck/release_deck.zip','release_build_manifest.json','release_build_receipt.json','RELEASE_BUILD_SUMMARY.md']:
        assert (b/f).exists()
    assert out['stages']['gallery']['status']=='completed'
    assert out['stages']['collection']['hash'] and out['stages']['collection_export']['hash'] and out['stages']['release_deck']['hash'] and out['stages']['release_deck_zip']['hash']

    out2=write_release_build(tmp_path/'b', tmp_path/'b/release_build', title='Golden Signal Release', include_tags=['has-zip']) if False else out
    assert not validate_release_build_manifest(out)
    bad=json.loads(json.dumps(out)); bad['build_policy']['external_calls_allowed']=True
    assert validate_release_build_manifest(bad)
    bad2=json.loads(json.dumps(out)); del bad2['stages']['gallery']
    assert validate_release_build_manifest(bad2)

    info=read_release_build_info(b)
    assert info['release_deck_zip_exists'] and info['contains_waveforge']
    assert not (b/'one/render').exists()

    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build',str(tmp_path),'--out',str(tmp_path/'release_build2'),'--title','Golden Signal Release','--include-tag','has-zip'],capture_output=True,text=True,env=env)
    assert r.returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build-validate',str(tmp_path/'release_build2/release_build_manifest.json')],capture_output=True,text=True,env=env).returncode==0
