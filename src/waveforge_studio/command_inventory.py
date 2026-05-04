from __future__ import annotations
import json
from pathlib import Path
from .hashing import canonical_json, sha256_digest

_STABLE_TS='1979-03-06T03:06:09Z'


def create_command_inventory() -> dict:
    categories=[
      ('Core',['version','doctor','schemas']),
      ('Forge / Compile',['compile','validate','inspect','forge','smoke']),
      ('Local Render Stubs',['render-audio-stub','audio-render-validate','render-visual-stub','visual-render-validate','preview-av','av-preview-validate']),
      ('Preview Packaging',['pack-preview','preview-pack-validate','zip-preview-pack','preview-pack-zip-validate']),
      ('Gallery / Collections',['gallery','gallery-validate','collection','collection-validate','collection-export','collection-export-validate']),
      ('Release Deck',['release-deck','release-deck-validate','zip-release-deck','release-deck-zip-validate']),
      ('Release Build',['release-build','release-build-validate','zip-release-build','release-build-zip-validate','verify-release-build','release-build-verification-validate','certify-release-build','release-certificate-validate','certificate-bundle','certificate-bundle-validate','zip-certificate-bundle','certificate-bundle-zip-validate','release-build-index','release-build-index-validate','finalize-release','final-release-validate','signature-envelope','signature-envelope-validate','detached-signature','detached-signature-validate']),
      ('Renderer / Adapter Interfaces',['renderer-adapters','renderer-adapters-validate','ffmpeg-adapter-contract','ffmpeg-adapter-contract-validate','phiaudio-adapter-contract','phiaudio-adapter-contract-validate','waverider-adapter-contract','waverider-adapter-contract-validate','adapter-contract-bundle','adapter-contract-bundle-validate']),
      ('Bridges / Adapters',['adapters','export-phiaudio','export-waverider','export-wavetalk']),
      ('Queue / Ledger / Timeline / Handoff',['queue','queue-validate','run-queue','ledger','timeline','timeline-validate','handoff','handoff-validate']),
    ]
    cats=[]; all_cmd=[]
    for name,cmds in categories:
        cats.append({'name':name,'commands':[{'command':c,'summary':f'{c} command','example':f'python -m waveforge_studio.cli {c}'} for c in cmds]})
        all_cmd.extend(cmds)
    inv={'schema':'waveforge.command_inventory.v3_alpha','project':'WaveForgeStudio','version':'3.0-alpha','command_count':len(all_cmd),'categories':cats,'missing_expected_commands':[],
         'blessed_workflows':[{'name':'Golden Final Release','steps':['python -m waveforge_studio.cli forge "Prompt" --out runs/demo_one --render-audio-stub --render-visual-stub --av-preview --preview-pack --preview-pack-zip','python -m waveforge_studio.cli finalize-release runs --out runs/final_release --title "Golden Signal Release" --include-tag has-zip','python -m waveforge_studio.cli signature-envelope runs/final_release','python -m waveforge_studio.cli detached-signature runs/final_release','python -m waveforge_studio.cli renderer-adapters --out runs/final_release','python -m waveforge_studio.cli ffmpeg-adapter-contract --out runs/final_release','python -m waveforge_studio.cli phiaudio-adapter-contract --out runs/final_release','python -m waveforge_studio.cli waverider-adapter-contract --out runs/final_release','python -m waveforge_studio.cli adapter-contract-bundle --out runs/final_release/adapter_contract_bundle']}]} 
    inv['receipt']={'schema':'waveforge.command_inventory_receipt.v3_alpha','command_inventory_hash':sha256_digest(json.loads(canonical_json(inv))),'created_at':_STABLE_TS}
    return inv


def write_command_inventory(out_dir: str | Path) -> dict:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    inv=create_command_inventory()
    (out/'command_inventory.json').write_text(json.dumps(inv,indent=2,sort_keys=True),encoding='utf-8')
    (out/'command_inventory_receipt.json').write_text(json.dumps(inv['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (out/'COMMAND_INVENTORY.md').write_text('# Command Inventory\n\n'+'\n'.join([f"## {c['name']}\n"+'\n'.join([f"- {x['command']}" for x in c['commands']]) for c in inv['categories']]),encoding='utf-8')
    return inv


def validate_command_inventory(inventory: dict) -> list[str]:
    e=[]
    if inventory.get('schema')!='waveforge.command_inventory.v3_alpha': e.append('schema invalid')
    if inventory.get('version')!='3.0-alpha': e.append('version invalid')
    cmds=[x['command'] for c in inventory.get('categories',[]) for x in c.get('commands',[])]
    if inventory.get('command_count')!=len(cmds): e.append('command_count mismatch')
    if len(set(cmds))!=len(cmds): e.append('duplicate commands')
    if not inventory.get('receipt',{}).get('command_inventory_hash'): e.append('receipt.command_inventory_hash required')
    if not inventory.get('blessed_workflows'): e.append('blessed_workflows required')
    return e


def assert_valid_command_inventory(inventory: dict) -> None:
    e=validate_command_inventory(inventory)
    if e: raise ValueError('Invalid command inventory: '+'; '.join(e))
