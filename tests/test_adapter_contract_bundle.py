import json, subprocess, sys
from waveforge_studio.adapter_contract_bundle import create_adapter_contract_bundle_manifest, write_adapter_contract_bundle, validate_adapter_contract_bundle_manifest, read_adapter_contract_bundle_info

def test_adapter_contract_bundle(tmp_path):
    m=create_adapter_contract_bundle_manifest()
    assert m['schema']=='waveforge.adapter_contract_bundle_manifest.v3_alpha'
    assert all(k in m['contracts'] for k in ['renderer_adapters','ffmpeg','phiaudio','waverider'])
    assert m['contract_count']==4 and m['future_runtime_count']==3
    assert m['bundle_policy']['real_rendering'] is False and m['bundle_policy']['runtime_execution'] is False and m['bundle_policy']['model_execution'] is False
    w=write_adapter_contract_bundle(tmp_path/'bundle')
    assert not validate_adapter_contract_bundle_manifest(w)
    bad=json.loads(json.dumps(w)); bad['bundle_policy']['runtime_execution']=True; assert validate_adapter_contract_bundle_manifest(bad)
    bad2=json.loads(json.dumps(w)); bad2['required_missing']=['x']; assert validate_adapter_contract_bundle_manifest(bad2)
    bad3=json.loads(json.dumps(w)); bad3['evidence'][0]['target']='/x'; assert validate_adapter_contract_bundle_manifest(bad3)
    for f in ['adapter_contract_bundle_manifest.json','adapter_contract_bundle_receipt.json','ADAPTER_CONTRACT_BUNDLE.md','renderer_adapter_manifest.json','ffmpeg_adapter_contract.json','phiaudio_adapter_contract.json','waverider_adapter_contract.json']:
        assert (tmp_path/'bundle'/f).exists()
    info=read_adapter_contract_bundle_info(tmp_path/'bundle'); assert info['renderer_manifest_exists'] and info['ffmpeg_contract_exists'] and info['phiaudio_contract_exists'] and info['waverider_contract_exists'] and info['contains_waveforge']
    env={"PYTHONPATH":"src"}
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','adapter-contract-bundle','--out',str(tmp_path/'cli')],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','adapter-contract-bundle-validate',str(tmp_path/'cli/adapter_contract_bundle_manifest.json')],capture_output=True,text=True,env=env).returncode==0
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Adapter Bundle Demo One','--out',str(tmp_path/'one'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    subprocess.run([sys.executable,'-m','waveforge_studio.cli','forge','Adapter Bundle Demo Two','--out',str(tmp_path/'two'),'--render-audio-stub','--render-visual-stub','--av-preview','--preview-pack','--preview-pack-zip'],check=True,env=env)
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final'),'--title','Golden Signal Release','--include-tag','has-zip','--adapter-contract-bundle'],capture_output=True,text=True,env=env).returncode==0
    assert (tmp_path/'final/adapter_contract_bundle/adapter_contract_bundle_manifest.json').exists()
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','finalize-release',str(tmp_path),'--out',str(tmp_path/'final2'),'--title','Golden Signal Release','--include-tag','has-zip','--renderer-adapters','--ffmpeg-adapter-contract','--phiaudio-adapter-contract','--waverider-adapter-contract','--adapter-contract-bundle','--signature-envelope','--detached-signature'],capture_output=True,text=True,env=env).returncode==0
    assert w['receipt']['adapter_contract_bundle_hash']==write_adapter_contract_bundle(tmp_path/'bundle2')['receipt']['adapter_contract_bundle_hash']
    assert 'no renderer runtime is executed' in (tmp_path/'bundle'/'ADAPTER_CONTRACT_BUNDLE.md').read_text(encoding='utf-8').lower()
