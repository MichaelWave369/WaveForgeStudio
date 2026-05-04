import json, subprocess, sys
from waveforge_studio.final_release import write_final_release
from waveforge_studio.detached_signature import create_detached_signature_manifest, write_detached_signature_manifest, validate_detached_signature_manifest, read_detached_signature_info
from waveforge_studio.signature_envelope import create_signature_envelope

def _setup(tmp_path):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Detached Demo One','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Detached Demo Two','--out',str(tmp_path/'two'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    write_final_release(tmp_path, tmp_path/'final_release', title='Golden Signal Release', include_tags=['has-zip'])
    return env, tmp_path/'final_release'

def test_detached_signature(tmp_path):
    env, d = _setup(tmp_path)
    e=create_signature_envelope(d)
    m=create_detached_signature_manifest(d)
    assert m['schema']=='waveforge.detached_signature_manifest.v3_alpha'
    assert m['signature_status']=='unsigned_dry_run'
    assert m['signing_request']['payload_hash']==e['signing_payload']['payload_hash']
    assert m['signature']['signature_value'] is None and m['signature']['signature_file'] is None and m['signature']['public_key_id'] is None
    assert not validate_detached_signature_manifest(m)
    bad=json.loads(json.dumps(m)); bad['detached_signature_policy']['cryptographic_signature']=True; assert validate_detached_signature_manifest(bad)
    bad2=json.loads(json.dumps(m)); bad2['signature']['signature_value']='x'; assert validate_detached_signature_manifest(bad2)
    bad3=json.loads(json.dumps(m)); bad3['outputs']['manifest']='/x'; assert validate_detached_signature_manifest(bad3)
    (d/'signature_envelope.json').unlink(missing_ok=True)
    w=write_detached_signature_manifest(d)
    assert (d/'signature_envelope.json').exists()
    assert (d/'detached_signature_manifest.json').exists() and (d/'detached_signature_receipt.json').exists() and (d/'DETACHED_SIGNATURE.md').exists()
    info=read_detached_signature_info(d)
    assert info['manifest_exists'] and info['contains_waveforge']
    m2=create_detached_signature_manifest(d)
    assert w['receipt']['detached_signature_manifest_hash']==m2['receipt']['detached_signature_manifest_hash']
    assert 'no cryptographic signature was created' in (d/'DETACHED_SIGNATURE.md').read_text(encoding='utf-8').lower()
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','detached-signature',str(d)],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','detached-signature-validate',str(d/'detached_signature_manifest.json')],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final_inline'),'--title','Golden Signal Release','--include-tag','has-zip','--signature-envelope','--detached-signature'],capture_output=True,text=True,env=env).returncode==0
    assert (tmp_path/'final_inline/detached_signature_manifest.json').exists()
