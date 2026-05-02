from __future__ import annotations

from .audio_graph import build_audio_graph
from .constants import C_STAR, DEFAULT_SEED, DEFAULT_STRUCTURE, LAMBDA, OMEGA_C, PHI
from .formula_compiler import compile_formula
from .receipts import create_receipt
from .sync_lattice import build_sync_lattice
from .visual_graph import build_visual_graph


def create_media_packet(
    prompt: str,
    duration_seconds: int = 72,
    seed: int = DEFAULT_SEED,
    mode: str = "mythic-reel",
) -> dict:
    formula = compile_formula(duration_seconds)
    audio = build_audio_graph(prompt, duration_seconds, seed)
    visual = build_visual_graph(prompt, duration_seconds, seed)
    sync = build_sync_lattice(audio, visual, duration_seconds)
    governance = {
        "sgl_policy": "intent-first-governance",
        "sml_memory": "lineage-receipt-enabled",
        "continuity_mode": "sovereign-replay-safe",
        "coherence_threshold": C_STAR,
    }

    packet = {
        "schema": "waveforge.media_packet.v0",
        "project": "WaveForgeStudio",
        "seed": seed,
        "mode": mode,
        "duration_seconds": duration_seconds,
        "intent": {
            "prompt": prompt,
            "archetype": "sovereign_signal",
            "purpose": "compile governed audiovisual artifact",
        },
        "structure": {
            "pattern": DEFAULT_STRUCTURE,
            "phi": PHI,
            "lambda": LAMBDA,
            "c_star": C_STAR,
            "omega_c": OMEGA_C,
            "fib_timing": formula["fib_timing"],
            "acts": formula["acts"],
            "scenes": formula["scenes"],
            "sync_beats": formula["sync_beats"],
            "phi_cuts": formula["phi_cuts"],
        },
        "audio": audio,
        "visual": visual,
        "sync": sync,
        "governance": governance,
    }
    packet["receipt"] = create_receipt(packet)
    return packet
