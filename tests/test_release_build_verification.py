import json
import subprocess
import sys

from waveforge_studio.release_build import write_release_build
from waveforge_studio.release_build_zip import write_release_build_zip
from waveforge_studio.release_build_verification import verify_release_build, write_release_build_verification, validate_release_build_verification


def _setup(tmp_path, with_zip=True):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','one','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','two','--out',str(tmp_path/'two'),'--seed','123','--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    b=tmp_path/'release_build'
    write_release_build(tmp_path,b,title='Golden Signal Release',include_tags=['has-zip'])
    if with_zip:
        write_release_build_zip(b)
    return env, b


def test_release_build_verification(tmp_path):
    env,b=_setup(tmp_path,with_zip=True)
    r=verify_release_build(b)
    assert r['schema']=='waveforge.release_build_verification.v2_alpha'
    assert r['summary']['passed']

    w=write_release_build_verification(b)
    for f in ['release_build_verification.json','release_build_verification_receipt.json','RELEASE_BUILD_VERIFICATION.md']:
        assert (b/f).exists()
    assert not validate_release_build_verification(w)
    bad=json.loads(json.dumps(w)); bad['summary']['check_count']=0
    assert validate_release_build_verification(bad)

    (b/'release_build.zip').unlink()
    (b/'release_build_zip_manifest.json').unlink()
    (b/'release_build_zip_receipt.json').unlink()
    non=verify_release_build(b,strict=False)
    assert any(c['status']=='warning' for c in non['checks'])
    strict=verify_release_build(b,strict=True)
    assert not strict['summary']['passed']

    # corrupt zip hash mismatch
    write_release_build_zip(b)
    rec=json.loads((b/'release_build_zip_receipt.json').read_text(encoding='utf-8')); rec['zip_file_sha256']='0'*64
    (b/'release_build_zip_receipt.json').write_text(json.dumps(rec,indent=2,sort_keys=True),encoding='utf-8')
    badhash=verify_release_build(b)
    assert any(c['id']=='check_123_release_build_zip_sha256' and c['status']=='failed' for c in badhash['checks'])

    # missing deck zip is error
    (b/'release_deck/release_deck.zip').unlink()
    missdeck=verify_release_build(b)
    assert any(c['path']=='release_deck/release_deck.zip' and c['status']=='failed' for c in missdeck['checks'])

    # stage hash mismatch
    m=json.loads((b/'release_build_manifest.json').read_text(encoding='utf-8')); m['stages']['gallery']['hash']='bad'
    (b/'release_build_manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    mismatch=verify_release_build(b)
    assert any(c['category']=='consistency' and c['status'] in {'failed','warning'} for c in mismatch['checks'])

    r1=subprocess.run([sys.executable,'-m','waveforge_studio.cli','verify-release-build',str(b)],capture_output=True,text=True,env=env)
    assert r1.returncode in {0,1}
    write_release_build_verification(b)
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build-verification-validate',str(b/'release_build_verification.json')],capture_output=True,text=True,env=env).returncode==0


def test_release_build_verify_flags(tmp_path):
    env,_=_setup(tmp_path/'x',with_zip=True)
    out=tmp_path/'inline'
    r=subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build',str(tmp_path/'x'),'--out',str(out),'--title','Golden Signal Release','--include-tag','has-zip','--zip','--verify'],capture_output=True,text=True,env=env)
    assert r.returncode==0 and (out/'release_build_verification.json').exists()
    out2=tmp_path/'inline2'
    r2=subprocess.run([sys.executable,'-m','waveforge_studio.cli','release-build',str(tmp_path/'x'),'--out',str(out2),'--title','Golden Signal Release','--include-tag','has-zip','--verify'],capture_output=True,text=True,env=env)
    assert r2.returncode==0 and (out2/'release_build_verification.json').exists()

    rep=json.loads((out/'release_build_verification.json').read_text(encoding='utf-8'))
    assert all((c.get('path') is None) or (not str(c.get('path')).startswith('/')) for c in rep['checks'])
    assert all(not str(v.get('path')).startswith('/') for v in rep['artifacts'].values())
