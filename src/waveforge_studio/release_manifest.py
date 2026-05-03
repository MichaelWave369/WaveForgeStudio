from __future__ import annotations
import json
from pathlib import Path
from .artifact_ledger import create_artifact_ledger
from .hashing import canonical_json, sha256_digest
from .alpha_artifacts import REQUIRED_ALPHA_ARTIFACTS
from .version import __version__, RELEASE_NAME, DOCTRINE, DEFAULT_RELEASE_TIMESTAMP

def create_release_manifest(root_dir:str|Path, packet:dict|None=None)->dict:
    root=Path(root_dir)
    ledger=create_artifact_ledger(root)
    present=[f['path'] for f in ledger['files']]
    missing=[x for x in REQUIRED_ALPHA_ARTIFACTS if x not in present]
    effective_missing=[x for x in missing if x not in {"release_manifest.json", "artifact_ledger.json"}]
    m={"schema":"waveforge.release_manifest.v0","project":"WaveForgeStudio","version":__version__,"release_name":RELEASE_NAME,"doctrine":DOCTRINE,"created_at":DEFAULT_RELEASE_TIMESTAMP,"source_packet_hash":(packet or {}).get('receipt',{}).get('packet_hash',''),"artifact_ledger_hash":ledger['receipt']['ledger_hash'],"required_alpha_artifacts":REQUIRED_ALPHA_ARTIFACTS,"present_artifacts":present,"missing_artifacts":missing,"alpha_ready":len(effective_missing)==0,"limitations":["No real media rendering is performed.","No external APIs are called.","All renderer integrations are deterministic contracts or stubs."]}
    m['receipt']={"schema":"waveforge.release_manifest_receipt.v0","release_hash":sha256_digest(json.loads(canonical_json(m))),"created_at":DEFAULT_RELEASE_TIMESTAMP}
    return m

def write_release_manifest(root_dir:str|Path, packet:dict|None=None)->dict:
    out=Path(root_dir); out.mkdir(parents=True,exist_ok=True)
    m=create_release_manifest(out,packet)
    (out/'release_manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True),encoding='utf-8')
    (out/'release_manifest_receipt.json').write_text(json.dumps(m['receipt'],indent=2,sort_keys=True),encoding='utf-8')
    (out/'RELEASE_MANIFEST.md').write_text(f"# Release Manifest\n\n- alpha_ready: {m['alpha_ready']}\n- release_hash: {m['receipt']['release_hash']}\n",encoding='utf-8')
    return m
