import json, subprocess, sys
from waveforge_studio.phiaudio_adapter_contract import create_phiaudio_adapter_contract, write_phiaudio_adapter_contract, validate_phiaudio_adapter_contract, read_phiaudio_adapter_contract_info

def test_phiaudio_adapter_contract(tmp_path):
    c=create_phiaudio_adapter_contract()
    assert c['schema']=='waveforge.phiaudio_adapter_contract.v3_alpha'
    assert c['adapter_id']=='phiaudio_runtime_future'
    assert c['status']=='disabled_contract'
    p=c['execution_policy']
    assert p['execution_enabled'] is False and p['requires_external_runtime'] is True and p['audio_model_execution'] is False and p['real_audio_generation'] is False
    assert not validate_phiaudio_adapter_contract(c)
    bad=json.loads(json.dumps(c)); bad['execution_policy']['execution_enabled']=True; assert validate_phiaudio_adapter_contract(bad)
    bad2=json.loads(json.dumps(c)); bad2['execution_policy']['requires_operator_enablement']=False; assert validate_phiaudio_adapter_contract(bad2)
    bad3=json.loads(json.dumps(c)); bad3['outputs']['contract']='/x'; assert validate_phiaudio_adapter_contract(bad3)
    assert c['relationship_to_phiaudio_bridge']['bridge_artifact']=='phiaudio/phiaudio_bundle.json'
    write_phiaudio_adapter_contract(tmp_path)
    assert (tmp_path/'phiaudio_adapter_contract.json').exists() and (tmp_path/'phiaudio_adapter_contract_receipt.json').exists() and (tmp_path/'PHIAUDIO_ADAPTER_CONTRACT.md').exists()
    info=read_phiaudio_adapter_contract_info(tmp_path); assert info['contract_exists'] and info['contains_waveforge']
    env={"PYTHONPATH":"src"}
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','phiaudio-adapter-contract','--out',str(tmp_path/'cli')],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','phiaudio-adapter-contract-validate',str(tmp_path/'cli/phiaudio_adapter_contract.json')],capture_output=True,text=True,env=env).returncode==0
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','PHIAudio Contract Demo One','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','PHIAudio Contract Demo Two','--out',str(tmp_path/'two'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final'),'--title','Golden Signal Release','--include-tag','has-zip','--phiaudio-adapter-contract'],capture_output=True,text=True,env=env).returncode==0
    assert (tmp_path/'final/phiaudio_adapter_contract.json').exists()
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final2'),'--title','Golden Signal Release','--include-tag','has-zip','--renderer-adapters','--phiaudio-adapter-contract'],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final3'),'--title','Golden Signal Release','--include-tag','has-zip','--ffmpeg-adapter-contract','--phiaudio-adapter-contract'],capture_output=True,text=True,env=env).returncode==0
    assert c['receipt']['phiaudio_adapter_contract_hash']==create_phiaudio_adapter_contract()['receipt']['phiaudio_adapter_contract_hash']
    assert 'phiaudio runtime is not executed' in (tmp_path/'PHIAUDIO_ADAPTER_CONTRACT.md').read_text(encoding='utf-8').lower()
