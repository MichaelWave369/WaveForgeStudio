# CineSwarm Release Reference Extension

**Extension ID:** `parallax.creative-interop.v2.cineswarm-reference`  
**Sender:** WaveForgeStudio  
**Target:** CineSwarm  
**Receiver status:** `ratified_receiver`

## Purpose

This extension lets WaveForgeStudio prepare a bounded, hash-bound reference to a completed WaveForge final release for the ratified CineSwarm receiver.

Ratification means the two repositories agree on the reference format and its verification boundary. It does **not** grant execution authority.

## Packet

WaveForgeStudio emits:

```text
schema:           parallax.bridge.v2
source:           WaveForgeStudio
target:           CineSwarm
interopProfile:   parallax.creative-interop.v2
extensionProfile: parallax.creative-interop.v2.cineswarm-reference
extensionStatus:  ratified_receiver
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

The CineSwarm receiver independently verifies the packet. A valid packet can produce only a reference receipt pending separate explicit human acceptance.

## Why media acquisition is explicitly false

CineSwarm has media, provider, and archival capabilities of its own.

Receiving a WaveForge release reference MUST NOT be interpreted as permission to search for, download, import, acquire, publish, render, execute, or replace media.

The creative handoff and every later authority domain remain separate.

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

## Ratification evidence

Receiver-side adoption is implemented in `MichaelWave369/CineSwarm` by `@parallax-network/cineswarm-bridge@0.27.0`.

The receiver:

1. independently validates the canonical native payload hash;
2. binds `transferId` to the WaveForge final-release SHA-256;
3. verifies optional Creative Interop v2 lineage;
4. rejects every authority escalation;
5. recognizes historical `unratified_receiver` packets only for provenance/debugging;
6. refuses to issue a receiver receipt for those historical unratified packets;
7. emits only `REFERENCE_RECEIVED_PENDING_HUMAN_ACCEPTANCE` for a valid ratified packet.

Receiver adoption was merged in CineSwarm PR #3 before this sender-side status transition.

WaveForgeStudio may therefore truthfully say:

> CineSwarm has a ratified receiver for this reference format.

It still MUST NOT say:

> CineSwarm imported, rendered, acquired, published, or otherwise acted on the referenced release

unless a separate authorized action and receipt establish that fact.
