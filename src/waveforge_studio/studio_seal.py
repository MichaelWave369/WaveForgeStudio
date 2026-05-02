from __future__ import annotations
from pathlib import Path
from .version import __version__, RELEASE_NAME, DOCTRINE

def write_studio_seal(root_dir:str|Path, release_manifest:dict)->Path:
    out=Path(root_dir); out.mkdir(parents=True,exist_ok=True)
    p=out/'STUDIO_SEAL.md'
    p.write_text(f"# WaveForgeStudio Studio Seal\n\n- Version: {__version__}\n- Release: {RELEASE_NAME}\n- Doctrine: {DOCTRINE}\n- Source Packet Hash: {release_manifest.get('source_packet_hash')}\n- Artifact Ledger Hash: {release_manifest.get('artifact_ledger_hash')}\n- Release Hash: {release_manifest.get('receipt',{}).get('release_hash')}\n- alpha_ready: {release_manifest.get('alpha_ready')}\n- required artifacts: {len(release_manifest.get('required_alpha_artifacts',[]))}\n- missing artifacts: {len(release_manifest.get('missing_artifacts',[]))}\n\nAlpha studio seal only — no media rendered.\n\n3 pillars. 6 tracks. 9 jobs. One governed audiovisual artifact.\n",encoding='utf-8')
    return p
