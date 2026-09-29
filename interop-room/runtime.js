const SOURCE_KEY = 'parallax-paracut-waveforge-v2';
const FRESHNESS_KEY = 'waveforge-interop-freshness-v1';
const STATE_KEY = 'waveforge-interop-room-v1';
const RELEASE_KEY = 'parallax-waveforge-release-reference-v1';

const isSha256 = value => /^sha256:[0-9a-fA-F]{64}$/.test(String(value || ''));

export function stableJson(value) {
  if (Array.isArray(value)) return '[' + value.map(stableJson).join(',') + ']';
  if (value && typeof value === 'object') {
    const entries = Object.entries(value).sort(([a], [b]) => a.localeCompare(b));
    return '{' + entries.map(([key, item]) => JSON.stringify(key) + ':' + stableJson(item)).join(',') + '}';
  }
  const encoded = JSON.stringify(value);
  if (encoded === undefined) throw new Error('WAVEFORGE_INTEROP_UNSUPPORTED_CANONICAL_VALUE');
  return encoded;
}

const bytesToHex = bytes => Array.from(bytes, value => value.toString(16).padStart(2, '0')).join('');

export async function sha256Hex(value) {
  const bytes = new TextEncoder().encode(typeof value === 'string' ? value : stableJson(value));
  const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return bytesToHex(new Uint8Array(digest));
}

export async function sha256Prefixed(value) {
  return 'sha256:' + await sha256Hex(value);
}

function storageGet(storage, key) {
  try {
    const raw = storage?.getItem?.(key);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function storageSet(storage, key, value) {
  if (!storage?.setItem) return false;
  storage.setItem(key, JSON.stringify(value));
  return true;
}

export function createMemoryStorage(seed = {}) {
  const map = new Map(Object.entries(seed).map(([key, value]) => [key, typeof value === 'string' ? value : JSON.stringify(value)]));
  return {
    getItem: key => map.has(key) ? map.get(key) : null,
    setItem: (key, value) => { map.set(key, String(value)); },
    removeItem: key => { map.delete(key); },
    dump: () => Object.fromEntries(map.entries()),
  };
}

function validateLineage(lineage) {
  if (!lineage || lineage.profile !== 'parallax.creative-interop.v2') {
    throw new Error('WAVEFORGE_INTEROP_LINEAGE_PROFILE_INVALID');
  }
  if (lineage.sourceBridgeSchema !== 'parallax.bridge.v2') {
    throw new Error('WAVEFORGE_INTEROP_LINEAGE_SOURCE_SCHEMA_INVALID');
  }
  if (!lineage.sourceTransferId) throw new Error('WAVEFORGE_INTEROP_LINEAGE_TRANSFER_ID_REQUIRED');
  if (!isSha256(lineage.creativeManifestHash)) throw new Error('WAVEFORGE_INTEROP_CREATIVE_MANIFEST_HASH_INVALID');
  if (!isSha256(lineage.baseContentHash)) throw new Error('WAVEFORGE_INTEROP_BASE_HASH_INVALID');
  const count = Number(lineage.semanticOverlayCount);
  if (!Number.isInteger(count) || count < 0 || count > 16) throw new Error('WAVEFORGE_INTEROP_OVERLAY_COUNT_INVALID');
  if (!Array.isArray(lineage.overlayContentHashes) || lineage.overlayContentHashes.length !== count) {
    throw new Error('WAVEFORGE_INTEROP_OVERLAY_HASH_COUNT_INVALID');
  }
  lineage.overlayContentHashes.forEach(hash => {
    if (!isSha256(hash)) throw new Error('WAVEFORGE_INTEROP_OVERLAY_HASH_INVALID');
  });
  for (const key of ['auralithCaptureHash', 'auralithReceiptHash']) {
    if (lineage[key] != null && !isSha256(lineage[key])) throw new Error('WAVEFORGE_INTEROP_EVIDENCE_HASH_INVALID');
  }
  if (lineage.paraCutAssetHashes != null) {
    if (!Array.isArray(lineage.paraCutAssetHashes)) throw new Error('WAVEFORGE_INTEROP_ASSET_HASHES_INVALID');
    lineage.paraCutAssetHashes.forEach(hash => {
      if (!isSha256(hash)) throw new Error('WAVEFORGE_INTEROP_ASSET_HASH_INVALID');
    });
  }
  return {
    ...lineage,
    creativeManifestHash: lineage.creativeManifestHash.toLowerCase(),
    baseContentHash: lineage.baseContentHash.toLowerCase(),
    overlayContentHashes: lineage.overlayContentHashes.map(hash => hash.toLowerCase()),
    ...(lineage.auralithCaptureHash ? { auralithCaptureHash: lineage.auralithCaptureHash.toLowerCase() } : {}),
    ...(lineage.auralithReceiptHash ? { auralithReceiptHash: lineage.auralithReceiptHash.toLowerCase() } : {}),
    ...(lineage.paraCutAssetHashes ? { paraCutAssetHashes: lineage.paraCutAssetHashes.map(hash => hash.toLowerCase()) } : {}),
  };
}

export async function verifyParaCutBridgeV2(bridge) {
  if (!bridge || bridge.schema !== 'parallax.bridge.v2' || bridge.protocol !== 'parallax-bridge' || bridge.version !== 2) {
    throw new Error('WAVEFORGE_INTEROP_PARALLAX_V2_REQUIRED');
  }
  if (bridge.interopProfile !== 'parallax.creative-interop.v2') throw new Error('WAVEFORGE_INTEROP_PROFILE_INVALID');
  if (bridge.source !== 'ParaCut' || bridge.target !== 'WaveForgeStudio') throw new Error('WAVEFORGE_INTEROP_ROUTE_INVALID');
  if (bridge.localOnly !== true || bridge.requiresUserAction !== true) throw new Error('WAVEFORGE_INTEROP_AUTHORITY_BOUNDARY_INVALID');
  if (bridge.payloadType !== 'application/vnd.paracut.render-plan+json') throw new Error('WAVEFORGE_INTEROP_PAYLOAD_TYPE_INVALID');

  const authority = bridge.authority || {};
  for (const key of ['realRenderingAuthorized', 'networkAuthorized', 'subprocessAuthorized', 'automaticImportAuthorized', 'publishAuthorized']) {
    if (authority[key] !== false) throw new Error('WAVEFORGE_INTEROP_AUTHORITY_ESCALATION_' + key);
  }

  const plan = bridge.payloadRefOrInline?.native;
  if (!plan || typeof plan !== 'object') throw new Error('WAVEFORGE_INTEROP_RENDER_PLAN_REQUIRED');
  for (const key of ['plan_id', 'job_id', 'project_id', 'output_uri', 'created_at']) {
    if (!plan[key]) throw new Error('WAVEFORGE_INTEROP_RENDER_PLAN_FIELD_' + key);
  }
  if (bridge.transferId !== 'paracut-waveforge-v2:' + plan.plan_id) {
    throw new Error('WAVEFORGE_INTEROP_TRANSFER_ID_MISMATCH');
  }
  const revision = Number(bridge.planRevision);
  if (!Number.isInteger(revision) || revision < 1) throw new Error('WAVEFORGE_INTEROP_PLAN_REVISION_INVALID');
  if (!isSha256(bridge.contentHash)) throw new Error('WAVEFORGE_INTEROP_PLAN_HASH_INVALID');
  const actualPlanHash = await sha256Prefixed(plan);
  if (actualPlanHash.toLowerCase() !== bridge.contentHash.toLowerCase()) {
    throw new Error('WAVEFORGE_INTEROP_RENDER_PLAN_HASH_MISMATCH');
  }

  const lineage = validateLineage(bridge.creativeLineage);
  if (bridge.lineageRef !== lineage.creativeManifestHash) throw new Error('WAVEFORGE_INTEROP_LINEAGE_REF_MISMATCH');

  return { plan, lineage, revision, planHash: bridge.contentHash.toLowerCase() };
}

async function buildIntake(bridge) {
  const verified = await verifyParaCutBridgeV2(bridge);
  const bridgeHash = await sha256Hex(bridge);
  const creativeLineageHash = await sha256Prefixed(verified.lineage);
  const intake = {
    schema: 'waveforge.paracut_bridge_intake.v2_alpha',
    project: 'WaveForgeStudio',
    source_system: 'ParaCut',
    source_bridge_schema: 'parallax.bridge.v2',
    interop_profile: 'parallax.creative-interop.v2',
    transfer_id: bridge.transferId,
    received_at: bridge.createdAt,
    source_content_hash: verified.planHash,
    bridge_hash: bridgeHash,
    render_plan: verified.plan,
    plan_revision: verified.revision,
    creative_lineage: verified.lineage,
    creative_lineage_hash: creativeLineageHash,
    lineage: {
      source_project_id: verified.plan.project_id,
      source_job_id: verified.plan.job_id,
      source_plan_id: verified.plan.plan_id,
      creative_manifest_hash: verified.lineage.creativeManifestHash,
    },
    warnings: Array.isArray(bridge.warnings) ? bridge.warnings : [],
    safety: {
      reference_only: true,
      handoff_only: true,
      requires_user_action: true,
      external_calls_allowed: false,
      subprocess_allowed: false,
      network_allowed: false,
      real_rendering_allowed: false,
      auto_import_into_media_packet: false,
      publish_allowed: false,
    },
  };
  const intakeHash = await sha256Hex(intake);
  intake.receipt = {
    schema: 'waveforge.paracut_bridge_intake_receipt.v2_alpha',
    intake_hash: intakeHash,
    bridge_hash: bridgeHash,
    source_content_hash: verified.planHash,
    creative_lineage_hash: creativeLineageHash,
    creative_manifest_hash: verified.lineage.creativeManifestHash,
    created_at: bridge.createdAt,
  };
  return intake;
}

export async function createInteropReleaseReference(intake) {
  if (!intake || intake.schema !== 'waveforge.paracut_bridge_intake.v2_alpha') {
    throw new Error('WAVEFORGE_INTEROP_V2_INTAKE_REQUIRED');
  }
  const plan = intake.render_plan;
  const lineage = intake.creative_lineage;
  const body = {
    schema: 'waveforge.interop_release_reference.v1',
    project: 'WaveForgeStudio',
    created_at: intake.received_at,
    source: {
      transfer_id: intake.transfer_id,
      plan_id: plan.plan_id,
      project_id: plan.project_id,
      plan_revision: intake.plan_revision,
      render_plan_hash: intake.source_content_hash,
      creative_lineage_hash: intake.creative_lineage_hash,
      creative_manifest_hash: lineage.creativeManifestHash,
    },
    planned_output: {
      uri: plan.output_uri,
      preset: plan.preset ?? null,
      duration_seconds: plan.duration_seconds ?? null,
    },
    mediaRendered: false,
    finalRelease: false,
    authority: {
      renderAuthorized: false,
      networkAuthorized: false,
      subprocessAuthorized: false,
      publishAuthorized: false,
      automaticImportAuthorized: false,
      mediaAcquisitionAuthorized: false,
    },
    notes: [
      'Reference-only packaging evidence from an accepted ParaCut RenderPlan.',
      'No media was rendered by creating this reference.',
      'This object is not a WaveForge final release manifest.',
    ],
  };
  return {
    ...body,
    receipt: {
      schema: 'waveforge.interop_release_reference_receipt.v1',
      release_reference_hash: await sha256Prefixed(body),
      created_at: intake.received_at,
    },
  };
}

export function createWaveForgeInteropRoom({ storage = globalThis.localStorage } = {}) {
  let state = storageGet(storage, STATE_KEY) || {
    schema: 'waveforge.interop-room.state.v1',
    roomVersion: '0.1.0',
    intake: null,
    freshnessStatus: null,
    releaseReference: null,
    latestReceipt: null,
  };

  const persist = () => storageSet(storage, STATE_KEY, state);

  const receive = async () => {
    const bridge = storageGet(storage, SOURCE_KEY);
    if (!bridge) throw new Error('WAVEFORGE_INTEROP_NO_PARACUT_V2_HANDOFF');
    await verifyParaCutBridgeV2(bridge);
    return bridge;
  };

  const accept = async () => {
    const bridge = await receive();
    const intake = await buildIntake(bridge);
    const projectId = String(intake.render_plan.project_id);
    const ledger = storageGet(storage, FRESHNESS_KEY) || {};
    const current = ledger[projectId];
    const revision = intake.plan_revision;
    const bridgeHash = intake.bridge_hash;

    let freshnessStatus = 'accepted';
    if (current) {
      if (revision < current.plan_revision) throw new Error('WAVEFORGE_INTEROP_STALE_REVISION');
      if (revision === current.plan_revision) {
        if (bridgeHash !== current.bridge_hash) throw new Error('WAVEFORGE_INTEROP_REVISION_EQUIVOCATION');
        freshnessStatus = 'replay';
      }
    }
    if (freshnessStatus === 'accepted') {
      ledger[projectId] = {
        plan_revision: revision,
        plan_id: intake.render_plan.plan_id,
        bridge_hash: bridgeHash,
      };
      storageSet(storage, FRESHNESS_KEY, ledger);
    }

    state = {
      ...state,
      intake,
      freshnessStatus,
      releaseReference: null,
      latestReceipt: intake.receipt,
    };
    persist();
    return snapshot();
  };

  const releaseReference = async () => {
    if (!state.intake) throw new Error('WAVEFORGE_INTEROP_ACCEPTED_INTAKE_REQUIRED');
    const reference = await createInteropReleaseReference(state.intake);
    storageSet(storage, RELEASE_KEY, reference);
    state = {
      ...state,
      releaseReference: reference,
      latestReceipt: reference.receipt,
    };
    persist();
    return reference;
  };

  const snapshot = () => ({
    schema: state.schema,
    roomVersion: state.roomVersion,
    freshnessStatus: state.freshnessStatus,
    intake: state.intake ? {
      schema: state.intake.schema,
      transfer_id: state.intake.transfer_id,
      received_at: state.intake.received_at,
      source_content_hash: state.intake.source_content_hash,
      bridge_hash: state.intake.bridge_hash,
      plan_revision: state.intake.plan_revision,
      creative_lineage_hash: state.intake.creative_lineage_hash,
      creative_lineage: state.intake.creative_lineage,
      render_plan: state.intake.render_plan,
      safety: state.intake.safety,
      receipt: state.intake.receipt,
    } : null,
    releaseReference: state.releaseReference,
    latestReceipt: state.latestReceipt,
  });

  return Object.freeze({
    schema: 'waveforge.interop-room.v1',
    version: '0.1.0',
    capabilities: () => ({
      sourceKey: SOURCE_KEY,
      releaseKey: RELEASE_KEY,
      planRevisionFreshness: true,
      mediaRendered: false,
      finalRelease: false,
      renderAuthority: false,
      networkAuthority: false,
      publishAuthority: false,
      cineSwarmReceiverRatified: false,
    }),
    bridge: Object.freeze({ receive, import: accept }),
    release: Object.freeze({ reference: releaseReference }),
    receipts: Object.freeze({ latest: () => state.latestReceipt }),
    state: snapshot,
  });
}

export function installWaveForgeInteropRoom(target = globalThis.window, options = {}) {
  const api = createWaveForgeInteropRoom(options);
  if (target) target.WaveForge = api;
  return api;
}

export const WAVEFORGE_INTEROP_STORAGE_KEYS = Object.freeze({
  source: SOURCE_KEY,
  freshness: FRESHNESS_KEY,
  state: STATE_KEY,
  release: RELEASE_KEY,
});
