import assert from 'node:assert/strict';
import {
  createMemoryStorage,
  createWaveForgeInteropRoom,
  sha256Prefixed,
} from '../interop-room/runtime.js';

function lineage() {
  return {
    profile: 'parallax.creative-interop.v2',
    sourceBridgeSchema: 'parallax.bridge.v2',
    sourceTransferId: 'creative-v2:acceptance-003',
    creativeManifestHash: 'sha256:' + '1'.repeat(64),
    baseContentHash: 'sha256:' + '2'.repeat(64),
    overlayContentHashes: ['sha256:' + '3'.repeat(64)],
    semanticOverlayCount: 1,
    auralithCaptureHash: 'sha256:' + '4'.repeat(64),
    auralithReceiptHash: 'sha256:' + '5'.repeat(64),
    paraCutAssetHashes: ['sha256:' + '2'.repeat(64), 'sha256:' + '3'.repeat(64)],
  };
}

async function bridge(revision = 1) {
  const plan = {
    plan_id: 'plan-acceptance-003',
    job_id: 'job-acceptance-003',
    project_id: 'interop-acceptance-003',
    output_uri: './exports/acceptance-003.mp4',
    preset: {
      preset_id: 'preset_wide_1080p',
      name: 'Wide 1080p',
      platform: 'wide',
      width: 1920,
      height: 1080,
      fps: 30,
      video_codec: 'h264',
      audio_codec: 'aac',
      container: 'mp4',
    },
    duration_seconds: 12,
    inputs: [],
    clips: [],
    filter_graph: [],
    argv: [],
    warnings: ['Interop Room does not render media.'],
    created_at: '2026-09-29T03:30:00Z',
  };
  const creativeLineage = lineage();
  return {
    schema: 'parallax.bridge.v2',
    protocol: 'parallax-bridge',
    version: 2,
    interopProfile: 'parallax.creative-interop.v2',
    transferId: 'paracut-waveforge-v2:' + plan.plan_id,
    source: 'ParaCut',
    target: 'WaveForgeStudio',
    createdAt: plan.created_at,
    localOnly: true,
    payloadType: 'application/vnd.paracut.render-plan+json',
    payloadRefOrInline: { native: plan },
    contentHash: await sha256Prefixed(plan),
    planRevision: revision,
    creativeLineage,
    trustLabels: ['creative-lineage-bound'],
    warnings: [],
    compatibilityNotes: [],
    lineageRef: creativeLineage.creativeManifestHash,
    requiresUserAction: true,
    authority: {
      realRenderingAuthorized: false,
      networkAuthorized: false,
      subprocessAuthorized: false,
      automaticImportAuthorized: false,
      publishAuthorized: false,
    },
  };
}

const initial = await bridge(2);
const storage = createMemoryStorage({
  'parallax-paracut-waveforge-v2': initial,
});
const room = createWaveForgeInteropRoom({ storage });

const received = await room.bridge.receive();
assert.equal(received.transferId, initial.transferId);

const accepted = await room.bridge.import();
assert.equal(accepted.freshnessStatus, 'accepted');
assert.equal(accepted.intake.plan_revision, 2);
assert.equal(accepted.intake.source_content_hash, initial.contentHash);
assert.equal(accepted.intake.creative_lineage.auralithCaptureHash, lineage().auralithCaptureHash);
assert.equal(accepted.intake.safety.real_rendering_allowed, false);

const replay = await room.bridge.import();
assert.equal(replay.freshnessStatus, 'replay');

const reference = await room.release.reference();
assert.equal(reference.schema, 'waveforge.interop_release_reference.v1');
assert.equal(reference.mediaRendered, false);
assert.equal(reference.finalRelease, false);
assert.equal(reference.source.render_plan_hash, initial.contentHash);
assert.equal(reference.source.creative_manifest_hash, lineage().creativeManifestHash);
assert.equal(reference.authority.renderAuthorized, false);
assert.equal(reference.authority.publishAuthorized, false);
assert.match(reference.receipt.release_reference_hash, /^sha256:[0-9a-f]{64}$/);

const storedRelease = JSON.parse(storage.getItem('parallax-waveforge-release-reference-v1'));
assert.equal(storedRelease.receipt.release_reference_hash, reference.receipt.release_reference_hash);

const stale = await bridge(1);
storage.setItem('parallax-paracut-waveforge-v2', JSON.stringify(stale));
await assert.rejects(
  room.bridge.import(),
  /STALE_REVISION/,
);

const equivocation = await bridge(2);
equivocation.payloadRefOrInline.native.output_uri = './exports/equivocation.mp4';
equivocation.contentHash = await sha256Prefixed(equivocation.payloadRefOrInline.native);
storage.setItem('parallax-paracut-waveforge-v2', JSON.stringify(equivocation));
await assert.rejects(
  room.bridge.import(),
  /REVISION_EQUIVOCATION/,
);

console.log('WaveForge Interop Room v0.1 browser smoke passed', {
  planHash: initial.contentHash,
  releaseReferenceHash: reference.receipt.release_reference_hash,
  freshness: replay.freshnessStatus,
});
