import json, subprocess, sys
from waveforge_studio.renderer_adapters import create_renderer_adapter_manifest, write_renderer_adapter_manifest, validate_renderer_adapter_manifest, read_renderer_adapter_info

def test_renderer_adapters(tmp_path):
    m=create_renderer_adapter_manifest()
    assert m['schema']=='waveforge.renderer_adapter_manifest.v3_alpha'
    ids=[a['adapter_id'] for a in m['adapters']]
    assert "local_audio_stub" in ids and "local_visual_stub" in ids and "local_av_preview" in ids
    assert any(a['adapter_id']=='ffmpeg_optional_future' and a.get('contract_artifact')=='ffmpeg_adapter_contract.json' for a in m['future_adapters'])
    assert any(a['adapter_id']=='phiaudio_runtime_future' and a.get('contract_artifact')=='phiaudio_adapter_contract.json' for a in m['future_adapters'])
    assert m['adapter_policy']['execution_enabled'] is False
    assert len(ids+ [a['adapter_id'] for a in m['future_adapters']])==len(set(ids+ [a['adapter_id'] for a in m['future_adapters']]))
    assert all(a['execution_enabled'] is False and a['safe_by_default'] is False for a in m['future_adapters'])
    assert not validate_renderer_adapter_manifest(m)
    bad=json.loads(json.dumps(m)); bad['adapter_policy']['external_calls_allowed']=True; assert validate_renderer_adapter_manifest(bad)
    bad2=json.loads(json.dumps(m)); bad2['future_adapters'][0]['execution_enabled']=True; assert validate_renderer_adapter_manifest(bad2)
    bad3=json.loads(json.dumps(m)); bad3['future_adapters'][0]['adapter_id']=bad3['adapters'][0]['adapter_id']; assert validate_renderer_adapter_manifest(bad3)
    w=write_renderer_adapter_manifest(tmp_path)
    assert (tmp_path/'renderer_adapter_manifest.json').exists() and (tmp_path/'renderer_adapter_receipt.json').exists() and (tmp_path/'RENDERER_ADAPTERS.md').exists()
    info=read_renderer_adapter_info(tmp_path)
    assert info['manifest_exists'] and info['contains_waveforge']
    env={"PYTHONPATH":"src"}
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','renderer-adapters','--out',str(tmp_path/'cli')],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','renderer-adapters-validate',str(tmp_path/'cli/renderer_adapter_manifest.json')],capture_output=True,text=True,env=env).returncode==0
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Adapter Demo One','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Adapter Demo Two','--out',str(tmp_path/'two'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final'),'--title','Golden Signal Release','--include-tag','has-zip','--renderer-adapters'],capture_output=True,text=True,env=env).returncode==0
    assert (tmp_path/'final/renderer_adapter_manifest.json').exists()
    m2=create_renderer_adapter_manifest(); assert m['receipt']['renderer_adapter_manifest_hash']==m2['receipt']['renderer_adapter_manifest_hash']
    assert 'no real rendering' in (tmp_path/'RENDERER_ADAPTERS.md').read_text(encoding='utf-8').lower()
