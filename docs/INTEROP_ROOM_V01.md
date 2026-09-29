# WaveForgeStudio Interop Room v0.1

WaveForgeStudio Interop Room is a live browser receiver for the existing Parallax Creative Interop v2 ParaCut handoff.

The authoritative receiver remains the Python WaveForge adapter.

The browser room mirrors the same contract so humans and browser agents can execute Acceptance 003 live.

## Same-origin source

The room reads:

```text
parallax-paracut-waveforge-v2
```

from browser storage.

## Live API

The room installs:

```js
window.WaveForge
```

with:

```js
WaveForge.bridge.receive()
WaveForge.bridge.import()

WaveForge.release.reference()

WaveForge.receipts.latest()
WaveForge.state()
```

## Verification

The browser receiver independently validates:

- `parallax.bridge.v2`;
- `parallax.creative-interop.v2`;
- ParaCut → WaveForge route;
- local-only + explicit-user-action boundaries;
- every explicit false authority field;
- native RenderPlan required fields;
- transfer ID / plan ID binding;
- positive `planRevision`;
- canonical RenderPlan SHA-256;
- creative lineage hash syntax/cardinality;
- `lineageRef`.

## Freshness

The room preserves the Python receiver freshness doctrine using consumer-owned browser storage:

```text
first revision            → accept
higher revision           → accept + advance
same revision + same hash → replay
lower revision            → reject stale
same revision + new hash  → reject equivocation
```

The room does not use timestamps as freshness authority.

## Intake receipt

Accepted handoffs produce the same semantic intake shape:

```text
waveforge.paracut_bridge_intake.v2_alpha
```

with a receipt binding:

- intake hash;
- bridge hash;
- RenderPlan content hash;
- creative-lineage hash;
- creative-manifest hash.

## Interop release reference

The Python adapter and browser room expose:

```text
waveforge.interop_release_reference.v1
```

This object packages evidence from an accepted RenderPlan.

It explicitly contains:

```text
mediaRendered = false
finalRelease  = false
```

and denies:

```text
render
network
subprocess
publish
automatic import
media acquisition
```

It is useful for Acceptance 003 backward tracing without fabricating a media render or WaveForge final release.

## Browser storage output

The release reference is written to:

```text
parallax-waveforge-release-reference-v1
```

## Native site tools

When WebMCP is available:

```text
waveforge_get_interop_state
waveforge_receive_paracut_handoff
waveforge_accept_paracut_revision
waveforge_create_release_reference
```

all delegate to the same `window.WaveForge` browser runtime.

## CineSwarm boundary

CineSwarm remains an unratified receiver.

The Interop Room does not contact CineSwarm and does not reinterpret an interop release reference as a final-release CineSwarm packet.

The existing final-release CineSwarm extension remains a separate contract.

## Conformance

Repository CI executes:

1. authoritative Python tests;
2. browser Interop Room smoke under Node 22.

The browser smoke covers verification, acceptance, replay, stale rollback rejection, equivocation rejection, intake receipt, and release-reference creation.
