import json, subprocess, sys
from waveforge_studio.waverider_adapter_contract import create_waverider_adapter_contract, write_waverider_adapter_contract, validate_waverider_adapter_contract, read_waverider_adapter_contract_info

def test_waverider_adapter_contract(tmp_path):
    c=create_waverider_adapter_contract()
    assert c['schema']=='waveforge.waverider_adapter_contract.v3_alpha'
    assert c['adapter_id']=='waverider_runtime_future'
    assert c['status']=='disabled_contract'
    p=c['execution_policy']
    assert p['execution_enabled'] is False and p['requires_external_runtime'] is True and p['visual_model_execution'] is False and p['video_model_execution'] is False and p['real_visual_generation'] is False and p['real_video_generation'] is False
    assert not validate_waverider_adapter_contract(c)
    bad=json.loads(json.dumps(c)); bad['execution_policy']['execution_enabled']=True; assert validate_waverider_adapter_contract(bad)
    bad2=json.loads(json.dumps(c)); bad2['execution_policy']['requires_operator_enablement']=False; assert validate_waverider_adapter_contract(bad2)
    bad3=json.loads(json.dumps(c)); bad3['outputs']['contract']='/x'; assert validate_waverider_adapter_contract(bad3)
    assert c['relationship_to_waverider_bridge']['bridge_artifact']=='waverider/waverider_bundle.json'
    assert c['relationship_to_renderer_handoff']['handoff_artifact']=='renderer_handoff.json'
    assert c['relationship_to_av_timeline']['timeline_artifact']=='av_timeline.json'
    write_waverider_adapter_contract(tmp_path)
    assert (tmp_path/'waverider_adapter_contract.json').exists() and (tmp_path/'waverider_adapter_contract_receipt.json').exists() and (tmp_path/'WAVERIDER_ADAPTER_CONTRACT.md').exists()
    info=read_waverider_adapter_contract_info(tmp_path); assert info['contract_exists'] and info['contains_waveforge']
    env={"PYTHONPATH":"src"}
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','waverider-adapter-contract','--out',str(tmp_path/'cli')],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','waverider-adapter-contract-validate',str(tmp_path/'cli/waverider_adapter_contract.json')],capture_output=True,text=True,env=env).returncode==0
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','WaveRider Contract Demo One','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','WaveRider Contract Demo Two','--out',str(tmp_path/'two'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final'),'--title','Golden Signal Release','--include-tag','has-zip','--waverider-adapter-contract'],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final2'),'--title','Golden Signal Release','--include-tag','has-zip','--renderer-adapters','--waverider-adapter-contract'],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final3'),'--title','Golden Signal Release','--include-tag','has-zip','--ffmpeg-adapter-contract','--phiaudio-adapter-contract','--waverider-adapter-contract'],capture_output=True,text=True,env=env).returncode==0
    assert c['receipt']['waverider_adapter_contract_hash']==create_waverider_adapter_contract()['receipt']['waverider_adapter_contract_hash']
    assert 'waverider runtime is not executed' in (tmp_path/'WAVERIDER_ADAPTER_CONTRACT.md').read_text(encoding='utf-8').lower()
