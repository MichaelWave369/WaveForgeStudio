# CineSwarm Release Reference Extension

**Extension ID:** `parallax.creative-interop.v2.cineswarm-reference`  
**Sender:** WaveForgeStudio  
**Target:** CineSwarm  
**Receiver status:** `unratified_receiver`

## Purpose

This extension lets WaveForgeStudio prepare a bounded, hash-bound reference to a completed WaveForge final release for a future CineSwarm receiver.

It deliberately stops at the packet boundary.

The current GitHub connection does not authorize writes to the CineSwarm repository, so this repository does not claim receiver adoption.

## Packet

WaveForgeStudio emits:

```text
schema:           parallax.bridge.v2
source:           WaveForgeStudio
target:           CineSwarm
interopProfile:   parallax.creative-interop.v2
extensionProfile: parallax.creative-interop.v2.cineswarm-reference
extensionStatus:  unratified_receiver
```

The native payload contains a reference to:

- WaveForge final-release manifest schema;
- title;
- final-release SHA-256;
- verification status;
- certificate status;
- index path;
- release-build ZIP path;
- certificate-bundle ZIP path;
- manifest path;
- receipt path;
- optional Creative Interop v2 lineage.

## Authority boundary

The packet MUST keep all of these false:

```text
automatic import
network
subprocess
render
publish
media acquisition
```

and MUST keep:

```text
localOnly = true
requiresUserAction = true
```

A future CineSwarm receiver must independently verify the packet and require explicit human acceptance.

## Why media acquisition is explicitly false

CineSwarm may have media-library or acquisition capabilities of its own.

Receiving a WaveForge release reference MUST NOT be interpreted as permission to search for, download, import, acquire, publish, or replace media.

The creative handoff and any library/acquisition policy remain separate authority domains.

## Usage

```python
from waveforge_studio.adapters.cineswarm_reference import (
    create_cineswarm_release_reference,
)

packet = create_cineswarm_release_reference(
    final_release_manifest,
    creative_lineage=optional_lineage,
)
```

The function only builds a local data packet. It performs no network request.

## Ratification requirement

This extension remains unratified until an authorized CineSwarm repository:

1. defines its receiver-side validation;
2. independently verifies `contentHash`;
3. preserves the explicit human-action boundary;
4. rejects authority escalation;
5. passes its native tests;
6. records an explicit human adoption decision.

Until then, WaveForgeStudio may truthfully say:

> a CineSwarm-compatible reference packet can be produced

but MUST NOT say:

> CineSwarm accepted or imported the release.
