import { installWaveForgeInteropRoom } from './runtime.js';

const api = installWaveForgeInteropRoom(window, { storage: window.localStorage });
const $ = selector => document.querySelector(selector);
const status = $('#status');

const shortHash = value => value ? String(value).slice(0, 18) + '…' : '—';
const esc = value => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;');

function render() {
  const state = api.state();
  const intake = state.intake;

  $('#source-state').innerHTML = intake
    ? '<strong>ParaCut v2 intake accepted</strong>' +
      '<span>Freshness: ' + esc(state.freshnessStatus) + '</span>' +
      '<span>Revision ' + esc(intake.plan_revision) + '</span>' +
      '<code>' + esc(intake.source_content_hash) + '</code>'
    : '<span>No accepted ParaCut handoff yet.</span>';

  $('#lineage-state').innerHTML = intake
    ? '<dl>' +
      '<dt>Creative manifest</dt><dd><code>' + esc(intake.creative_lineage.creativeManifestHash) + '</code></dd>' +
      '<dt>Auralith capture</dt><dd><code>' + esc(intake.creative_lineage.auralithCaptureHash || 'not observed') + '</code></dd>' +
      '<dt>Auralith receipt</dt><dd><code>' + esc(intake.creative_lineage.auralithReceiptHash || 'not observed') + '</code></dd>' +
      '<dt>Lineage hash</dt><dd><code>' + esc(intake.creative_lineage_hash) + '</code></dd>' +
      '</dl>'
    : '<span>Lineage appears after accepted intake.</span>';

  $('#plan-state').innerHTML = intake
    ? '<strong>' + esc(intake.render_plan.plan_id) + '</strong>' +
      '<span>Output planned only: ' + esc(intake.render_plan.output_uri) + '</span>' +
      '<span>' + esc(intake.render_plan.duration_seconds) + ' seconds</span>' +
      '<span>' + esc(intake.render_plan.clips?.length || 0) + ' clip(s)</span>'
    : '<span>No RenderPlan accepted yet.</span>';

  const ref = state.releaseReference;
  $('#release-state').innerHTML = ref
    ? '<strong>Interop release reference ready</strong>' +
      '<code>' + esc(ref.receipt.release_reference_hash) + '</code>' +
      '<span>mediaRendered: false</span>' +
      '<span>finalRelease: false</span>' +
      '<span>CineSwarm receiver: unratified</span>'
    : '<span>No release reference yet.</span>';

  $('#receipt-state').innerHTML = state.latestReceipt
    ? '<code>' + esc(state.latestReceipt.release_reference_hash || state.latestReceipt.intake_hash || '') + '</code>' +
      '<span>' + esc(state.latestReceipt.schema) + '</span>'
    : '<span>No receipt yet.</span>';
}

async function run(label, task) {
  status.textContent = label + '…';
  status.dataset.kind = 'working';
  try {
    const result = await task();
    status.textContent = label + ' ✓';
    status.dataset.kind = 'ok';
    render();
    return result;
  } catch (error) {
    status.textContent = String(error?.message || error);
    status.dataset.kind = 'error';
    throw error;
  }
}

$('#receive').addEventListener('click', () => run('Verified ParaCut handoff', async () => {
  const bridge = await api.bridge.receive();
  return {
    transferId: bridge.transferId,
    contentHash: bridge.contentHash,
    planRevision: bridge.planRevision,
  };
}));

$('#accept').addEventListener('click', () => run('Accepted revision', () => api.bridge.import()));
$('#release').addEventListener('click', () => run('Created non-rendered release reference', () => api.release.reference()));

async function installSiteTools() {
  const modelContext = document.modelContext || navigator.modelContext;
  if (!modelContext?.registerTool) return;

  const defs = [
    {
      name: 'waveforge_get_interop_state',
      title: 'Get WaveForge Interop Room state',
      description: 'Read the current ParaCut intake, creative lineage, freshness status, receipt, and release-reference status.',
      readOnly: true,
      execute: async () => JSON.stringify({ ok: true, state: api.state() }),
    },
    {
      name: 'waveforge_receive_paracut_handoff',
      title: 'Verify ParaCut handoff',
      description: 'Independently verify the current local ParaCut Creative Interop v2 RenderPlan handoff without accepting its revision.',
      execute: async () => {
        const bridge = await api.bridge.receive();
        return JSON.stringify({ ok: true, transfer: {
          transferId: bridge.transferId,
          contentHash: bridge.contentHash,
          planRevision: bridge.planRevision,
          lineageRef: bridge.lineageRef,
          authority: bridge.authority,
        } });
      },
    },
    {
      name: 'waveforge_accept_paracut_revision',
      title: 'Accept ParaCut revision',
      description: 'Verify and accept the ParaCut handoff under consumer-owned monotonic planRevision freshness rules.',
      execute: async () => JSON.stringify({ ok: true, state: await api.bridge.import() }),
    },
    {
      name: 'waveforge_create_release_reference',
      title: 'Create WaveForge interop release reference',
      description: 'Create a hash-bound packaging reference from the accepted RenderPlan. This does not render media and is not a WaveForge final release.',
      execute: async () => {
        const reference = await api.release.reference();
        return JSON.stringify({ ok: true, reference });
      },
    },
  ];

  const controller = new AbortController();
  for (const def of defs) {
    await modelContext.registerTool({
      name: def.name,
      title: def.title,
      description: def.description,
      inputSchema: { type: 'object', properties: {}, additionalProperties: false },
      annotations: {
        readOnlyHint: Boolean(def.readOnly),
        untrustedContentHint: true,
        consequentialHint: false,
      },
      execute: def.execute,
    }, { signal: controller.signal });
  }

  window.waveForgeInteropSiteTools = Object.freeze({
    version: '0.1.0',
    registered: defs.map(item => item.name),
    stop: () => controller.abort(),
  });
}

render();
installSiteTools().catch(error => console.warn('[WaveForge] site-tool install failed', error));
