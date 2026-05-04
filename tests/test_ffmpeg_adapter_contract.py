import json, subprocess, sys
from waveforge_studio.ffmpeg_adapter_contract import create_ffmpeg_adapter_contract, write_ffmpeg_adapter_contract, validate_ffmpeg_adapter_contract, read_ffmpeg_adapter_contract_info

def test_ffmpeg_adapter_contract(tmp_path):
    c=create_ffmpeg_adapter_contract()
    assert c['schema']=='waveforge.ffmpeg_adapter_contract.v3_alpha'
    assert c['adapter_id']=='ffmpeg_optional_future'
    assert c['status']=='disabled_contract'
    p=c['execution_policy']
    assert p['execution_enabled'] is False and p['requires_ffmpeg'] is True and p['requires_subprocess'] is True and p['video_rendering'] is False and p['muxing_enabled'] is False
    assert not validate_ffmpeg_adapter_contract(c)
    bad=json.loads(json.dumps(c)); bad['execution_policy']['execution_enabled']=True; assert validate_ffmpeg_adapter_contract(bad)
    bad2=json.loads(json.dumps(c)); bad2['execution_policy']['requires_operator_enablement']=False; assert validate_ffmpeg_adapter_contract(bad2)
    bad3=json.loads(json.dumps(c)); bad3['outputs']['contract']='/x'; assert validate_ffmpeg_adapter_contract(bad3)
    w=write_ffmpeg_adapter_contract(tmp_path)
    assert (tmp_path/'ffmpeg_adapter_contract.json').exists() and (tmp_path/'ffmpeg_adapter_contract_receipt.json').exists() and (tmp_path/'FFMPEG_ADAPTER_CONTRACT.md').exists()
    info=read_ffmpeg_adapter_contract_info(tmp_path); assert info['contract_exists'] and info['contains_waveforge']
    env={"PYTHONPATH":"src"}
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','ffmpeg-adapter-contract','--out',str(tmp_path/'cli')],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','ffmpeg-adapter-contract-validate',str(tmp_path/'cli/ffmpeg_adapter_contract.json')],capture_output=True,text=True,env=env).returncode==0
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','FFmpeg Contract Demo One','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','FFmpeg Contract Demo Two','--out',str(tmp_path/'two'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final'),'--title','Golden Signal Release','--include-tag','has-zip','--ffmpeg-adapter-contract'],capture_output=True,text=True,env=env).returncode==0
    assert (tmp_path/'final/ffmpeg_adapter_contract.json').exists()
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final2'),'--title','Golden Signal Release','--include-tag','has-zip','--renderer-adapters','--ffmpeg-adapter-contract'],capture_output=True,text=True,env=env).returncode==0
    assert (tmp_path/'final2/renderer_adapter_manifest.json').exists() and (tmp_path/'final2/ffmpeg_adapter_contract.json').exists()
    assert c['receipt']['ffmpeg_adapter_contract_hash']==create_ffmpeg_adapter_contract()['receipt']['ffmpeg_adapter_contract_hash']
    assert 'ffmpeg is not executed' in (tmp_path/'FFMPEG_ADAPTER_CONTRACT.md').read_text(encoding='utf-8').lower()
