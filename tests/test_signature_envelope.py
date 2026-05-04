import json
import subprocess
import sys

from waveforge_studio.final_release import write_final_release
from waveforge_studio.signature_envelope import (
    create_signature_envelope,
    read_signature_envelope_info,
    validate_signature_envelope,
    write_signature_envelope,
)


def _setup_final(tmp_path):
    env={"PYTHONPATH":"src"}
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Signature Demo One','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Signature Demo Two','--out',str(tmp_path/'two'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    write_final_release(tmp_path, tmp_path/'final_release', title='Golden Signal Release', include_tags=['has-zip'])
    return env, tmp_path/'final_release'


def test_signature_envelope(tmp_path):
    env, final_dir = _setup_final(tmp_path)
    e = create_signature_envelope(final_dir)
    assert e['schema'] == 'waveforge.signature_envelope.v3_alpha'
    assert e['envelope_status'] == 'unsigned'
    assert e['signature']['status'] == 'unsigned'
    assert e['signature']['signature_value'] is None
    assert e['signing_payload']['payload_hash']
    assert e['source_artifacts']['command_inventory']['command_inventory_hash']
    assert e['source_artifacts']['schema_registry']['schema_registry_hash']
    assert not validate_signature_envelope(e)

    bad = json.loads(json.dumps(e)); bad['signature_policy']['cryptographic_signature'] = True
    assert validate_signature_envelope(bad)
    bad2 = json.loads(json.dumps(e)); bad2['signature']['signature_value'] = 'abc'
    assert validate_signature_envelope(bad2)
    bad3 = json.loads(json.dumps(e)); bad3['source_artifacts']['release_build_zip']['path'] = '/abs.zip'
    assert validate_signature_envelope(bad3)

    w = write_signature_envelope(final_dir)
    assert (final_dir/'signature_envelope.json').exists()
    assert (final_dir/'signature_envelope_receipt.json').exists()
    assert (final_dir/'SIGNATURE_ENVELOPE.md').exists()
    info = read_signature_envelope_info(final_dir)
    assert info['envelope_exists'] and info['contains_waveforge']

    e2 = create_signature_envelope(final_dir)
    assert e['receipt']['signature_envelope_hash'] == e2['receipt']['signature_envelope_hash']
    assert e['signing_payload']['payload_hash'] == e2['signing_payload']['payload_hash']
    assert 'not cryptographically signed' in (final_dir/'SIGNATURE_ENVELOPE.md').read_text(encoding='utf-8').lower()

    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','signature-envelope',str(final_dir)],capture_output=True,text=True,env=env).returncode == 0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','signature-envelope-validate',str(final_dir/'signature_envelope.json')],capture_output=True,text=True,env=env).returncode == 0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final_inline'),'--title','Golden Signal Release','--include-tag','has-zip','--signature-envelope'],capture_output=True,text=True,env=env).returncode == 0
    assert (tmp_path/'final_inline/signature_envelope.json').exists()
