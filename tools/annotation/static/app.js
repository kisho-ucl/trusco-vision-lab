'use strict';

const LABEL_COLORS = {
  Inspect:         '#2761DE',
  Sort:            '#35aa58',
  Transport:       '#c94942',
  Other:           '#778899',
  Unclear:         '#aa8855',
  // Exception sub-labels
  'No Person':     '#dc2626',  // red
  'Tracking Lost': '#7c3aed',  // purple
  'ID Switch':     '#0891b2',  // cyan
  'Exception':     '#64748b',  // slate
};

const EXCEPTION_LABELS = ['No Person', 'Tracking Lost', 'ID Switch', 'Exception'];

const WAREHOUSE_W = 3932;
const WAREHOUSE_H = 2312;

const state = {
  manifest:      null,
  annotations:   {},      // clip_id → saved annotation object
  clipIdx:       0,
  frameIdx:      0,
  segments:      [],      // [{start, end, label, note}], 0-based frame indices
  selectedSeg:   null,    // index into segments, or null
  exceptionMode: false,   // whether exception sub-panel is open
  personId:      null,    // assigned person ID (0-38) for current clip
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
    clip_id:   clip.clip_id,
    person_id: state.personId,
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

// ── Render: frame viewer ──────────────────────────────────────────────────────

function renderFrame() {
  const clip = currentClip();
  if (!clip) return;
  const img = document.getElementById('frameImg');
  img.classList.remove('anim-exit-fwd', 'anim-exit-bwd', 'anim-enter-fwd', 'anim-enter-bwd', 'no-transition');
  img.src = imgUrl(clip, state.frameIdx);
  document.getElementById('frameCounter').textContent =
    `Frame ${state.frameIdx + 1} / ${frameCount()}`;
  updateGhostFrames(clip, state.frameIdx);
}

function updateGhostFrames(clip, idx) {
  const prev = document.getElementById('framePrev');
  const next = document.getElementById('frameNext');
  if (!clip) { prev.style.visibility = next.style.visibility = 'hidden'; return; }
  if (idx > 0) {
    prev.src = imgUrl(clip, idx - 1);
    prev.style.visibility = 'visible';
  } else {
    prev.style.visibility = 'hidden';
  }
  if (idx < clip.frame_count - 1) {
    next.src = imgUrl(clip, idx + 1);
    next.style.visibility = 'visible';
  } else {
    next.style.visibility = 'hidden';
  }
}


// ── Render: trajectory panel ──────────────────────────────────────────────────

function renderTrajectory() {
  const svg = document.getElementById('trajectorySvg');
  svg.querySelectorAll('.traj-elem').forEach(el => el.remove());

  const clip = currentClip();
  const traj = clip?.trajectory;
  if (!traj?.length) return;

  const ns = 'http://www.w3.org/2000/svg';
  const COLOR = '#ef4444';
  const MARKER_R = 55;
  const FONT_SIZE = 140;
  const PAD = 22;

  // Full trajectory — faint reference (always visible even at frame 0)
  const allPts = traj.filter(Boolean);
  if (allPts.length > 1) {
    const bgPoly = document.createElementNS(ns, 'polyline');
    bgPoly.classList.add('traj-elem');
    bgPoly.setAttribute('points', allPts.map(([x, y]) => `${x},${y}`).join(' '));
    bgPoly.setAttribute('fill', 'none');
    bgPoly.setAttribute('stroke', 'rgba(239,68,68,0.18)');
    bgPoly.setAttribute('stroke-width', '14');
    bgPoly.setAttribute('stroke-linecap', 'round');
    bgPoly.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(bgPoly);
  }

  // Past trajectory — bright overlay
  const pastPts = traj.slice(0, state.frameIdx + 1).filter(Boolean);
  if (pastPts.length > 1) {
    const poly = document.createElementNS(ns, 'polyline');
    poly.classList.add('traj-elem');
    poly.setAttribute('points', pastPts.map(([x, y]) => `${x},${y}`).join(' '));
    poly.setAttribute('fill', 'none');
    poly.setAttribute('stroke', 'rgba(239,68,68,0.75)');
    poly.setAttribute('stroke-width', '14');
    poly.setAttribute('stroke-linecap', 'round');
    poly.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(poly);
  }

  const pt = traj[state.frameIdx] ?? traj.find(Boolean);
  if (!pt) return;

  // Marker circle
  const circle = document.createElementNS(ns, 'circle');
  circle.classList.add('traj-elem');
  circle.setAttribute('cx', pt[0]);
  circle.setAttribute('cy', pt[1]);
  circle.setAttribute('r', MARKER_R);
  circle.setAttribute('fill', COLOR);
  circle.setAttribute('stroke', '#fff');
  circle.setAttribute('stroke-width', '8');
  svg.appendChild(circle);

  // Leader line direction: avoid edges
  const goLeft = pt[0] > WAREHOUSE_W * 0.6;
  const goDown = pt[1] < 300;
  const dx = goLeft ? -110 : 110;
  const dy = goDown  ?  160 : -160;
  const angle = Math.atan2(dy, dx);
  const lx = pt[0] + dx;
  const ly = pt[1] + dy;

  const line = document.createElementNS(ns, 'line');
  line.classList.add('traj-elem');
  line.setAttribute('x1', pt[0] + Math.cos(angle) * MARKER_R);
  line.setAttribute('y1', pt[1] + Math.sin(angle) * MARKER_R);
  line.setAttribute('x2', lx);
  line.setAttribute('y2', ly);
  line.setAttribute('stroke', COLOR);
  line.setAttribute('stroke-width', '6');
  line.setAttribute('stroke-dasharray', '20,10');
  svg.appendChild(line);

  // Text label — add to SVG to measure, then wrap with background rect
  const anchor = goLeft ? 'end' : 'start';
  const textX   = goLeft ? lx - 24 : lx + 24;
  const labelStr = `Current Position  (${Math.round(pt[0])}, ${Math.round(pt[1])})`;

  const text = document.createElementNS(ns, 'text');
  text.classList.add('traj-elem');
  text.setAttribute('x', textX);
  text.setAttribute('y', ly);
  text.setAttribute('font-size', FONT_SIZE);
  text.setAttribute('font-family', 'system-ui, sans-serif');
  text.setAttribute('font-weight', '700');
  text.setAttribute('fill', COLOR);
  text.setAttribute('text-anchor', anchor);
  text.setAttribute('dominant-baseline', 'central');
  text.textContent = labelStr;
  svg.appendChild(text);

  const bb = text.getBBox();
  svg.removeChild(text);

  const bg = document.createElementNS(ns, 'rect');
  bg.classList.add('traj-elem');
  bg.setAttribute('x',      bb.x - PAD);
  bg.setAttribute('y',      bb.y - PAD * 0.5);
  bg.setAttribute('width',  bb.width  + PAD * 2);
  bg.setAttribute('height', bb.height + PAD);
  bg.setAttribute('rx', '12');
  bg.setAttribute('fill', 'rgba(0,0,0,0.82)');
  svg.appendChild(bg);
  svg.appendChild(text);
}

// ── Render: thumbnail strip ───────────────────────────────────────────────────

function renderThumbnails() {
  const clip = currentClip();
  const strip = document.getElementById('thumbnailStrip');
  strip.innerHTML = '';
  if (!clip) return;
  const boundaryStarts = new Set(state.segments.slice(1).map(s => s.start));
  for (let i = 0; i < clip.frame_count; i++) {
    if (boundaryStarts.has(i)) {
      const div = document.createElement('div');
      div.className = 'thumb-boundary';
      strip.appendChild(div);
    }
    const img = document.createElement('img');
    img.src = imgUrl(clip, i);
    img.className = 'thumb' + (i === state.frameIdx ? ' is-current' : '');
    img.dataset.frameIdx = i;
    img.addEventListener('click', () => setFrame(Number(img.dataset.frameIdx)));
    strip.appendChild(img);
  }
  scrollThumbIntoView(state.frameIdx);
}

function updateThumbnailHighlight(prevIdx, newIdx) {
  const strip = document.getElementById('thumbnailStrip');
  const prev = strip.querySelector(`.thumb[data-frame-idx="${prevIdx}"]`);
  const next = strip.querySelector(`.thumb[data-frame-idx="${newIdx}"]`);
  if (prev) prev.classList.remove('is-current');
  if (next) { next.classList.add('is-current'); next.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' }); }
}

function scrollThumbIntoView(idx) {
  const strip = document.getElementById('thumbnailStrip');
  const thumb = strip.querySelector(`.thumb[data-frame-idx="${idx}"]`);
  if (thumb) thumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
}

// ── Render: segment bars ──────────────────────────────────────────────────────

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

    // Drag handle at right boundary (not after last segment)
    if (i < state.segments.length - 1) {
      const handle = document.createElement('div');
      handle.className = 'seg-handle';
      handle.style.left = `${left + width}%`;
      handle.dataset.boundaryIdx = i;
      container.append(handle);
    }
  });

  // Playhead — current frame position
  const playhead = document.createElement('div');
  playhead.className = 'seg-playhead';
  playhead.style.left = `${(state.frameIdx / Math.max(1, n - 1)) * 100}%`;
  container.append(playhead);
}

function updatePlayhead() {
  const el = document.querySelector('.seg-playhead');
  if (!el) return;
  const n = frameCount();
  el.style.left = `${(state.frameIdx / Math.max(1, n - 1)) * 100}%`;
}

function updateThumbnailBoundaries() {
  const strip = document.getElementById('thumbnailStrip');
  strip.querySelectorAll('.thumb-boundary').forEach(el => el.remove());
  state.segments.slice(1).forEach(seg => {
    const thumb = strip.querySelector(`.thumb[data-frame-idx="${seg.start}"]`);
    if (thumb) {
      const div = document.createElement('div');
      div.className = 'thumb-boundary';
      strip.insertBefore(div, thumb);
    }
  });
}

// ── Render: meta / labels / note / progress ───────────────────────────────────

function renderMeta() {
  const clip = currentClip();
  document.getElementById('clipId').textContent = clip?.clip_id ?? '–';
  const dl = document.getElementById('metaList');
  dl.innerHTML = '';
  if (!clip) return;
  const rows = [
    ['Camera',   Array.isArray(clip.cameras) ? clip.cameras.join(', ') : (clip.camera_id ?? '–')],
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
  const disabled = state.selectedSeg === null;

  if (state.exceptionMode) {
    // ── Exception sub-panel ──
    const back = document.createElement('button');
    back.className = 'label-btn exception-back';
    back.textContent = '← Back';
    back.addEventListener('click', () => { state.exceptionMode = false; renderLabelButtons(); });
    container.append(back);

    EXCEPTION_LABELS.forEach(label => {
      const btn = document.createElement('button');
      btn.className = 'label-btn' + (activeSeg?.label === label ? ' is-active' : '');
      btn.style.setProperty('--label-color', LABEL_COLORS[label] ?? '#92400e');
      btn.textContent = label;
      btn.disabled = disabled;
      btn.addEventListener('click', () => {
        applyLabel(label);
        state.exceptionMode = false;
        renderLabelButtons();
      });
      container.append(btn);
    });

  } else {
    // ── Normal labels ──
    labels.forEach((label, i) => {
      const btn = document.createElement('button');
      btn.className = 'label-btn' + (activeSeg?.label === label ? ' is-active' : '');
      btn.style.setProperty('--label-color', LABEL_COLORS[label] ?? '#666');
      btn.textContent = `${i + 1}. ${label}`;
      btn.disabled = disabled;
      btn.addEventListener('click', () => applyLabel(label));
      container.append(btn);
    });

    // Exception toggle button
    const isExcLabel = activeSeg && EXCEPTION_LABELS.includes(activeSeg.label);
    const excBtn = document.createElement('button');
    excBtn.className = 'label-btn exception-toggle' + (isExcLabel ? ' is-active' : '');
    excBtn.textContent = 'Exception ▾';
    excBtn.disabled = disabled;
    excBtn.addEventListener('click', () => { state.exceptionMode = true; renderLabelButtons(); });
    container.append(excBtn);
  }
}

function renderNoteInput() {
  const seg = state.selectedSeg !== null ? state.segments[state.selectedSeg] : null;
  const ta = document.getElementById('noteInput');
  ta.value    = seg?.note ?? '';
  ta.disabled = state.selectedSeg === null;
}

function renderProgress() {
  const clips = state.manifest?.clips ?? [];
  const total     = clips.length;
  const labeled   = clips.filter(c => isFullyLabeled(c.clip_id)).length;
  const remaining = total - labeled;
  const pct = total ? (labeled / total) * 100 : 0;
  document.getElementById('progressFill').style.width = `${pct}%`;
  document.getElementById('progressLabel').textContent =
    `${labeled} labeled · ${remaining} remaining`;
  document.getElementById('clipCounter').textContent =
    total ? `${state.clipIdx + 1} / ${total}` : '– / –';
}

function renderPersonId() {
  document.getElementById('personIdSelect').value = state.personId ?? '';
}

function renderAll() {
  renderMeta();
  renderPersonId();
  renderThumbnails();
  renderSegmentBars();
  renderFrame();
  renderTrajectory();
  renderLabelButtons();
  renderNoteInput();
  renderProgress();
}

// ── Actions ───────────────────────────────────────────────────────────────────

async function loadClip(idx) {
  const clips = state.manifest?.clips ?? [];
  if (!clips.length) return;
  const newIdx = Math.max(0, Math.min(idx, clips.length - 1));

  // Auto-save before leaving the current clip (skip on initial load where idx stays 0)
  if (state.manifest && newIdx !== state.clipIdx) {
    await autoSaveCurrentClip();
  }

  state.clipIdx       = newIdx;
  state.frameIdx      = 0;
  state.selectedSeg   = null;
  state.exceptionMode = false;
  const clip = currentClip();
  const ann = state.annotations[clip.clip_id];
  state.segments = segmentsFromAnnotation(ann, clip.frame_count);
  state.personId = ann?.person_id ?? null;
  renderAll();
}

function setFrame(idx) {
  const prev = state.frameIdx;
  const newIdx = Math.max(0, Math.min(idx, frameCount() - 1));
  if (newIdx === prev) return;
  state.frameIdx = newIdx;
  renderFrame();
  updateThumbnailHighlight(prev, newIdx);
  renderTrajectory();
  updatePlayhead();
}

// ── Boundary operations ───────────────────────────────────────────────────────

function addBoundary() {
  const f = state.frameIdx;
  const i = state.segments.findIndex(s => s.start <= f && s.end >= f);
  if (i === -1) return;
  const seg = state.segments[i];
  if (f >= seg.end) return; // no room for a new segment after this frame

  const right = { start: f + 1, end: seg.end, label: null, note: '' };
  state.segments[i] = { ...seg, end: f };
  state.segments.splice(i + 1, 0, right);
  state.selectedSeg = i + 1;
  renderSegmentBars();
  renderLabelButtons();
  renderNoteInput();
  updateThumbnailBoundaries();
}

function deleteBoundary() {
  const i = state.selectedSeg;
  if (i === null || i >= state.segments.length - 1) return; // no right boundary
  const left  = state.segments[i];
  const right = state.segments[i + 1];
  // Front absorbs rear: keep left's label, extend to right's end
  state.segments[i] = { ...left, end: right.end };
  state.segments.splice(i + 1, 1);
  renderSegmentBars();
  renderLabelButtons();
  renderNoteInput();
  updateThumbnailBoundaries();
}

function moveBoundary(boundaryIdx, newFrame) {
  const left  = state.segments[boundaryIdx];
  const right = state.segments[boundaryIdx + 1];
  const f = Math.max(left.start, Math.min(right.end - 1, newFrame));
  state.segments[boundaryIdx]     = { ...left,  end:   f };
  state.segments[boundaryIdx + 1] = { ...right, start: f + 1 };
  renderSegmentBars();
  updateThumbnailBoundaries();
}

function setupBoundaryDrag() {
  const container = document.getElementById('segmentBars');
  let draggingIdx = null;

  container.addEventListener('mousedown', e => {
    const handle = e.target.closest('.seg-handle');
    if (!handle) return;
    draggingIdx = Number(handle.dataset.boundaryIdx);
    e.preventDefault();
    e.stopPropagation();
  });
  document.addEventListener('mousemove', e => {
    if (draggingIdx === null) return;
    const rect = container.getBoundingClientRect();
    const pct  = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    moveBoundary(draggingIdx, Math.round(pct * (frameCount() - 1)));
  });
  document.addEventListener('mouseup', () => { draggingIdx = null; });
}

function selectSegment(i) {
  state.selectedSeg = (state.selectedSeg === i) ? null : i;
  state.exceptionMode = false;
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

// Auto-save the current clip to the server (silent, no UI feedback).
// Only saves if there's something to save (labels/notes exist, or a previous annotation exists).
async function autoSaveCurrentClip() {
  const clip = currentClip();
  if (!clip) return;
  const hasContent  = state.segments.some(s => s.label || s.note);
  const hadPrevious = !!state.annotations[clip.clip_id];
  if (!hasContent && !hadPrevious) return;
  const payload = buildSavePayload(clip);
  try {
    const res = await fetch('/api/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      state.annotations[clip.clip_id] = payload;
      renderProgress();
    }
  } catch (_) { /* network error — ignore */ }
}

function importAnnotations(file) {
  const reader = new FileReader();
  reader.onload = e => {
    const lines = e.target.result.split('\n').filter(l => l.trim());
    let count = 0;
    lines.forEach(line => {
      try {
        const entry = JSON.parse(line);
        if (entry.clip_id) { state.annotations[entry.clip_id] = entry; count++; }
      } catch (_) {}
    });
    // Refresh current clip's segments from imported data
    const clip = currentClip();
    if (clip) {
      state.segments     = segmentsFromAnnotation(state.annotations[clip.clip_id], clip.frame_count);
      state.selectedSeg  = null;
      state.exceptionMode = false;
      renderAll();
    } else {
      renderProgress();
    }
    const btn = document.getElementById('importBtn');
    btn.textContent = `Imported ${count} ✓`;
    setTimeout(() => { btn.textContent = 'Import'; }, 2000);
  };
  reader.readAsText(file);
}

async function exportJsonl() {
  await autoSaveCurrentClip();   // make sure the current clip is included
  const lines = Object.values(state.annotations).map(a => JSON.stringify(a));
  const blob = new Blob([lines.join('\n') + '\n'], { type: 'application/jsonl' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = 'annotations.jsonl'; a.click();
  URL.revokeObjectURL(url);
}

// ── Keyboard ─────────────────────────────────────────────────────────────────

document.addEventListener('keydown', e => {
  if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return;
  if (e.key === 'ArrowRight') { e.preventDefault(); setFrame(state.frameIdx + 1); return; }
  if (e.key === 'ArrowLeft')  { e.preventDefault(); setFrame(state.frameIdx - 1); return; }
  if (e.key === 'b' || e.key === 'B') { addBoundary(); return; }
  if (e.key === 'e' || e.key === 'E') {
    if (state.selectedSeg !== null) {
      state.exceptionMode = !state.exceptionMode;
      renderLabelButtons();
    }
    return;
  }
  if (e.key === 'Escape') {
    const lb = document.getElementById('lightbox');
    if (lb.classList.contains('is-open')) { lb.classList.remove('is-open'); return; }
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

// Person ID select
document.getElementById('personIdSelect').addEventListener('change', e => {
  state.personId = e.target.value === '' ? null : Number(e.target.value);
});

// Bibs lightbox
document.getElementById('bibsThumb').addEventListener('click', () =>
  document.getElementById('lightbox').classList.add('is-open'));
document.getElementById('lightbox').addEventListener('click', () =>
  document.getElementById('lightbox').classList.remove('is-open'));

document.getElementById('prevClip').addEventListener('click', () => loadClip(state.clipIdx - 1));
document.getElementById('nextClip').addEventListener('click', () => loadClip(state.clipIdx + 1));
document.getElementById('importBtn').addEventListener('click', () => document.getElementById('importFile').click());
document.getElementById('importFile').addEventListener('change', e => {
  const file = e.target.files[0];
  if (file) importAnnotations(file);
  e.target.value = '';  // reset so the same file can be re-imported
});
document.getElementById('exportBtn').addEventListener('click', exportJsonl);

document.getElementById('addBoundaryBtn').addEventListener('click', addBoundary);
document.getElementById('delBoundaryBtn').addEventListener('click', deleteBoundary);

// ── Init ──────────────────────────────────────────────────────────────────────

async function init() {
  // Populate Person ID options 0-38
  const sel = document.getElementById('personIdSelect');
  for (let i = 0; i <= 38; i++) {
    const opt = document.createElement('option');
    opt.value = i; opt.textContent = i;
    sel.appendChild(opt);
  }

  const [mRes, aRes] = await Promise.all([
    fetch('/api/manifest'),
    fetch('/api/annotations'),
  ]);
  state.manifest    = await mRes.json();
  state.annotations = await aRes.json();
  setupBoundaryDrag();
  loadClip(0);
}

init();
