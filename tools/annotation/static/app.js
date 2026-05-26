'use strict';

const LABEL_COLORS = {
  Inspect:   '#2761DE',
  Sort:      '#35aa58',
  Transport: '#c94942',
  Other:     '#778899',
  Unclear:   '#aa8855',
};

const state = {
  manifest:    null,
  annotations: {},     // clip_id → saved annotation object
  clipIdx:     0,
  frameIdx:    0,
  segments:    [],     // [{start, end, label, note}], 0-based frame indices
  selectedSeg: null,   // index into segments, or null
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function currentClip() {
  return state.manifest?.clips[state.clipIdx] ?? null;
}

function frameCount() {
  return currentClip()?.frame_count ?? 1;
}

function imgUrl(clip, frameIdx) {
  const num = String(frameIdx + 1).padStart(6, '0');
  return `/clips/${clip.image_folder}/${num}.jpg`;
}

function defaultSegments(count) {
  return [{ start: 0, end: count - 1, label: null, note: '' }];
}

// Convert saved annotation (1-based) → in-memory segments (0-based)
function segmentsFromAnnotation(ann, count) {
  if (!ann?.work_segments?.length) return defaultSegments(count);
  return ann.work_segments.map(s => ({
    start: s.start_frame - 1,
    end:   s.end_frame   - 1,
    label: s.label ?? null,
    note:  s.note  ?? '',
  }));
}

// Convert in-memory segments (0-based) → save payload (1-based)
function buildSavePayload(clip) {
  return {
    clip_id: clip.clip_id,
    work_segments: state.segments.map(s => ({
      start_frame: s.start + 1,
      end_frame:   s.end   + 1,
      label:       s.label,
      note:        s.note,
    })),
  };
}

function isFullyLabeled(clipId) {
  const ann = state.annotations[clipId];
  return ann?.work_segments?.length > 0 && ann.work_segments.every(s => s.label);
}

// ── Render ────────────────────────────────────────────────────────────────────

function renderFrame() {
  const clip = currentClip();
  if (!clip) return;
  document.getElementById('frameImg').src = imgUrl(clip, state.frameIdx);
  document.getElementById('frameCounter').textContent =
    `Frame ${state.frameIdx + 1} / ${frameCount()}`;
  renderPlayhead();
}

function renderPlayhead() {
  const n = frameCount();
  const pct = n > 1 ? (state.frameIdx / (n - 1)) * 100 : 0;
  document.getElementById('playhead').style.left = `${pct}%`;
}

function renderSegmentBars() {
  const n = frameCount();
  const container = document.getElementById('segmentBars');
  container.innerHTML = '';
  state.segments.forEach((seg, i) => {
    const left  = (seg.start / n) * 100;
    const width = ((seg.end - seg.start + 1) / n) * 100;
    const bar = document.createElement('div');
    bar.className = 'segment-bar' + (i === state.selectedSeg ? ' is-selected' : '');
    bar.style.left       = `${left}%`;
    bar.style.width      = `${width}%`;
    bar.style.background = seg.label ? (LABEL_COLORS[seg.label] ?? '#666') : '#444';
    bar.textContent      = seg.label ?? 'unlabeled';
    bar.dataset.segIdx   = i;
    bar.addEventListener('click', () => selectSegment(i));
    container.append(bar);
  });
}

function renderFrameTicks() {
  const n = frameCount();
  const container = document.getElementById('timelineTicks');
  container.innerHTML = '';
  for (let i = 0; i < n; i++) {
    const tick = document.createElement('div');
    tick.className = 'tick';
    tick.style.left = n > 1 ? `${(i / (n - 1)) * 100}%` : '0%';
    if (i === 0 || i === n - 1 || (i + 1) % 5 === 0) {
      const lbl = document.createElement('span');
      lbl.className = 'tick-label';
      lbl.textContent = i + 1;
      tick.append(lbl);
    }
    container.append(tick);
  }
}

function renderMeta() {
  const clip = currentClip();
  document.getElementById('clipId').textContent = clip?.clip_id ?? '–';
  const dl = document.getElementById('metaList');
  dl.innerHTML = '';
  if (!clip) return;
  const rows = [
    ['Camera',   clip.camera_id],
    ['Zone',     clip.zone_hint],
    ['Start',    clip.start_time?.slice(0, 19).replace('T', ' ')],
    ['End',      clip.end_time?.slice(0, 19).replace('T', ' ')],
    ['Duration', clip.duration_sec != null ? `${clip.duration_sec}s` : null],
    ['Frames',   clip.frame_count],
  ];
  rows.forEach(([k, v]) => {
    const dt = document.createElement('dt');
    dt.textContent = k;
    const dd = document.createElement('dd');
    dd.textContent = v ?? '–';
    dl.append(dt, dd);
  });
}

function renderLabelButtons() {
  const container = document.getElementById('labelButtons');
  container.innerHTML = '';
  const labels = state.manifest?.labels ?? [];
  const activeSeg = state.selectedSeg !== null ? state.segments[state.selectedSeg] : null;
  labels.forEach((label, i) => {
    const btn = document.createElement('button');
    btn.className = 'label-btn' + (activeSeg?.label === label ? ' is-active' : '');
    btn.style.setProperty('--label-color', LABEL_COLORS[label] ?? '#666');
    btn.textContent = `${i + 1}. ${label}`;
    btn.disabled = state.selectedSeg === null;
    btn.addEventListener('click', () => applyLabel(label));
    container.append(btn);
  });
}

function renderNoteInput() {
  const seg = state.selectedSeg !== null ? state.segments[state.selectedSeg] : null;
  const ta = document.getElementById('noteInput');
  ta.value    = seg?.note ?? '';
  ta.disabled = state.selectedSeg === null;
}

function renderProgress() {
  const clips = state.manifest?.clips ?? [];
  const total   = clips.length;
  const labeled = clips.filter(c => isFullyLabeled(c.clip_id)).length;
  const pct = total ? (labeled / total) * 100 : 0;
  document.getElementById('progressFill').style.width = `${pct}%`;
  document.getElementById('progressLabel').textContent = `${labeled} / ${total} labeled`;
  document.getElementById('clipCounter').textContent =
    total ? `${state.clipIdx + 1} / ${total}` : '– / –';
}

function renderAll() {
  renderMeta();
  renderFrameTicks();
  renderSegmentBars();
  renderFrame();
  renderLabelButtons();
  renderNoteInput();
  renderProgress();
}

// ── Actions ───────────────────────────────────────────────────────────────────

function loadClip(idx) {
  const clips = state.manifest?.clips ?? [];
  if (!clips.length) return;
  state.clipIdx    = Math.max(0, Math.min(idx, clips.length - 1));
  state.frameIdx   = 0;
  state.selectedSeg = null;
  const clip = currentClip();
  state.segments = segmentsFromAnnotation(state.annotations[clip.clip_id], clip.frame_count);
  renderAll();
}

function setFrame(idx) {
  state.frameIdx = Math.max(0, Math.min(idx, frameCount() - 1));
  renderFrame();
}

function selectSegment(i) {
  state.selectedSeg = (state.selectedSeg === i) ? null : i;
  renderSegmentBars();
  renderLabelButtons();
  renderNoteInput();
}

function applyLabel(label) {
  if (state.selectedSeg === null) return;
  state.segments[state.selectedSeg].label = label;
  renderSegmentBars();
  renderLabelButtons();
}

async function saveAnnotation() {
  const clip = currentClip();
  if (!clip) return;
  const payload = buildSavePayload(clip);
  const res = await fetch('/api/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (res.ok) {
    state.annotations[clip.clip_id] = payload;
    renderProgress();
    const btn = document.getElementById('saveBtn');
    btn.textContent = 'Saved ✓';
    setTimeout(() => { btn.textContent = 'Save'; }, 1500);
  }
}

function exportJsonl() {
  const lines = Object.values(state.annotations).map(a => JSON.stringify(a));
  const blob = new Blob([lines.join('\n') + '\n'], { type: 'application/jsonl' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = 'annotations.jsonl'; a.click();
  URL.revokeObjectURL(url);
}

// ── Timeline interaction ──────────────────────────────────────────────────────

function xToFrame(clientX) {
  const track = document.getElementById('timelineTrack');
  const rect  = track.getBoundingClientRect();
  const pct   = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
  return Math.round(pct * (frameCount() - 1));
}

function setupTimelineDrag() {
  const track = document.getElementById('timelineTrack');
  let dragging = false;
  track.addEventListener('mousedown', e => { dragging = true; setFrame(xToFrame(e.clientX)); });
  document.addEventListener('mousemove', e => { if (dragging) setFrame(xToFrame(e.clientX)); });
  document.addEventListener('mouseup',   () => { dragging = false; });
}

// ── Keyboard ─────────────────────────────────────────────────────────────────

document.addEventListener('keydown', e => {
  if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return;
  if (e.key === 'ArrowRight') { setFrame(state.frameIdx + 1); return; }
  if (e.key === 'ArrowLeft')  { setFrame(state.frameIdx - 1); return; }
  if (e.key === 'Escape') {
    state.selectedSeg = null;
    renderSegmentBars(); renderLabelButtons(); renderNoteInput();
    return;
  }
  const n = Number(e.key);
  const labels = state.manifest?.labels ?? [];
  if (n >= 1 && n <= labels.length && state.selectedSeg !== null) {
    applyLabel(labels[n - 1]);
  }
});

// ── Note sync ─────────────────────────────────────────────────────────────────

document.getElementById('noteInput').addEventListener('input', e => {
  if (state.selectedSeg === null) return;
  state.segments[state.selectedSeg].note = e.target.value;
});

// ── Button listeners ──────────────────────────────────────────────────────────

document.getElementById('prevClip').addEventListener('click', () => loadClip(state.clipIdx - 1));
document.getElementById('nextClip').addEventListener('click', () => loadClip(state.clipIdx + 1));
document.getElementById('saveBtn').addEventListener('click', saveAnnotation);
document.getElementById('exportBtn').addEventListener('click', exportJsonl);

// Boundary operations (Step 3)
document.getElementById('addBoundaryBtn').disabled = true;
document.getElementById('delBoundaryBtn').disabled = true;

// ── Init ──────────────────────────────────────────────────────────────────────

async function init() {
  const [mRes, aRes] = await Promise.all([
    fetch('/api/manifest'),
    fetch('/api/annotations'),
  ]);
  state.manifest    = await mRes.json();
  state.annotations = await aRes.json();
  loadClip(0);
  setupTimelineDrag();
}

init();
