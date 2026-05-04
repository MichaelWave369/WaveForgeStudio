import json
import subprocess
import sys
from waveforge_studio.command_inventory import create_command_inventory, write_command_inventory, validate_command_inventory

def test_command_inventory(tmp_path):
    inv=create_command_inventory()
    assert inv['schema']=='waveforge.command_inventory.v3_alpha'
    cmds=[x['command'] for c in inv['categories'] for x in c['commands']]
    assert inv['command_count']==len(cmds)
    assert len(cmds)==len(set(cmds))
    assert any('finalize-release' in s for w in inv['blessed_workflows'] for s in w['steps'])
    w=write_command_inventory(tmp_path)
    for f in ['command_inventory.json','command_inventory_receipt.json','COMMAND_INVENTORY.md']:
        assert (tmp_path/f).exists()
    bad=json.loads(json.dumps(w)); bad['categories'][0]['commands'].append(bad['categories'][0]['commands'][0])
    assert validate_command_inventory(bad)

    env={'PYTHONPATH':'src'}
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','command-inventory','--out',str(tmp_path/'cli')],capture_output=True,text=True,env=env).returncode==0
    assert subprocess.run([sys.executable,'-m','waveforge_studio.cli','command-inventory-validate',str(tmp_path/'cli/command_inventory.json')],capture_output=True,text=True,env=env).returncode==0
