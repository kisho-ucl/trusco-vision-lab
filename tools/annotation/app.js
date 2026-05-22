const state = {
  manifest: { version: 1, labels: ["Inspect", "Sort", "Transport", "Other", "Unclear"], clips: [] },
  index: 0,
  annotations: {},
  selectedLabel: null
};

const storageKey = "har-warehouse-annotation-v0";

const els = {
  manifestInput: document.getElementById("manifestInput"),
  loadSampleButton: document.getElementById("loadSampleButton"),
  exportButton: document.getElementById("exportButton"),
  manifestSummary: document.getElementById("manifestSummary"),
  progressBar: document.getElementById("progressBar"),
  clipVideo: document.getElementById("clipVideo"),
  clipImage: document.getElementById("clipImage"),
  emptyMedia: document.getElementById("emptyMedia"),
  prevButton: document.getElementById("prevButton"),
  nextButton: document.getElementById("nextButton"),
  clipCounter: document.getElementById("clipCounter"),
  clipTitle: document.getElementById("clipTitle"),
  currentLabel: document.getElementById("currentLabel"),
  metadataList: document.getElementById("metadataList"),
  labelGrid: document.getElementById("labelGrid"),
  noteInput: document.getElementById("noteInput"),
  saveButton: document.getElementById("saveButton"),
  clearButton: document.getElementById("clearButton"),
  queueSummary: document.getElementById("queueSummary"),
  clipQueue: document.getElementById("clipQueue")
};

function getCurrentClip() {
  return state.manifest.clips[state.index] || null;
}

function loadSavedAnnotations() {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
    state.annotations = saved.annotations || {};
  } catch {
    state.annotations = {};
  }
}

function persistAnnotations() {
  localStorage.setItem(storageKey, JSON.stringify({ annotations: state.annotations }));
}

function setManifest(manifest) {
  state.manifest = {
    version: manifest.version || 1,
    labels: manifest.labels && manifest.labels.length ? manifest.labels : state.manifest.labels,
    clips: Array.isArray(manifest.clips) ? manifest.clips : []
  };
  state.index = 0;
  state.selectedLabel = null;
  render();
}

async function loadSampleManifest() {
  const response = await fetch("sample_manifest.json");
  const manifest = await response.json();
  setManifest(manifest);
}

function handleManifestFile(file) {
  const reader = new FileReader();
  reader.onload = () => {
    const manifest = JSON.parse(String(reader.result));
    setManifest(manifest);
  };
  reader.readAsText(file);
}

function selectLabel(label) {
  state.selectedLabel = label;
  renderLabels();
  updateCurrentLabel();
}

function getConfidence() {
  const checked = document.querySelector("input[name='confidence']:checked");
  return checked ? checked.value : "medium";
}

function setConfidence(value) {
  const radio = document.querySelector(`input[name='confidence'][value='${value || "medium"}']`);
  if (radio) radio.checked = true;
}

function saveCurrentAnnotation() {
  const clip = getCurrentClip();
  if (!clip || !state.selectedLabel) return;

  state.annotations[clip.clip_id] = {
    clip_id: clip.clip_id,
    label: state.selectedLabel,
    confidence: getConfidence(),
    note: els.noteInput.value.trim(),
    annotated_at: new Date().toISOString()
  };
  persistAnnotations();
  goToIndex(Math.min(state.index + 1, state.manifest.clips.length - 1));
}

function clearCurrentAnnotation() {
  const clip = getCurrentClip();
  if (!clip) return;
  delete state.annotations[clip.clip_id];
  state.selectedLabel = null;
  els.noteInput.value = "";
  setConfidence("medium");
  persistAnnotations();
  render();
}

function goToIndex(index) {
  if (!state.manifest.clips.length) return;
  state.index = Math.max(0, Math.min(index, state.manifest.clips.length - 1));
  const clip = getCurrentClip();
  const annotation = clip ? state.annotations[clip.clip_id] : null;
  state.selectedLabel = annotation ? annotation.label : null;
  els.noteInput.value = annotation ? annotation.note : "";
  setConfidence(annotation ? annotation.confidence : "medium");
  render();
}

function exportJsonl() {
  const rows = state.manifest.clips
    .map((clip) => state.annotations[clip.clip_id])
    .filter(Boolean)
    .map((annotation) => JSON.stringify(annotation));
  const blob = new Blob([rows.join("\n") + (rows.length ? "\n" : "")], { type: "application/jsonl" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "annotations.jsonl";
  link.click();
  URL.revokeObjectURL(url);
}

function formatTrackSummary(summary) {
  if (!summary) return "none";
  const parts = [];
  if (summary.distance_m !== undefined) parts.push(`distance ${summary.distance_m} m`);
  if (summary.dominant_zone) parts.push(`dominant ${summary.dominant_zone}`);
  if (Array.isArray(summary.zone_transitions)) parts.push(`transitions ${summary.zone_transitions.join(" -> ")}`);
  return parts.join(", ") || "none";
}

function renderMedia(clip) {
  els.clipVideo.style.display = "none";
  els.clipImage.style.display = "none";
  els.emptyMedia.style.display = "flex";
  els.clipVideo.removeAttribute("src");
  els.clipImage.removeAttribute("src");

  if (!clip) return;

  if (clip.video_url) {
    els.clipVideo.src = clip.video_url;
    els.clipVideo.style.display = "block";
    els.emptyMedia.style.display = "none";
  } else if (clip.thumbnail_url) {
    els.clipImage.src = clip.thumbnail_url;
    els.clipImage.alt = `Thumbnail for ${clip.clip_id}`;
    els.clipImage.style.display = "block";
    els.emptyMedia.style.display = "none";
  }
}

function renderMetadata(clip) {
  els.metadataList.innerHTML = "";
  if (!clip) return;

  const rows = [
    ["Worker", clip.worker_id || "unknown"],
    ["Camera", clip.camera_id || "unknown"],
    ["Start", clip.start_time || "unknown"],
    ["End", clip.end_time || "unknown"],
    ["Duration", clip.duration_sec !== undefined ? `${clip.duration_sec} sec` : "unknown"],
    ["Zone hint", clip.zone_hint || "none"],
    ["Track", formatTrackSummary(clip.track_summary)]
  ];

  for (const [label, value] of rows) {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    els.metadataList.append(dt, dd);
  }
}

function renderLabels() {
  els.labelGrid.innerHTML = "";
  state.manifest.labels.forEach((label, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "label-button";
    button.textContent = `${index + 1}. ${label}`;
    if (state.selectedLabel === label) button.classList.add("is-selected");
    button.addEventListener("click", () => selectLabel(label));
    els.labelGrid.append(button);
  });
}

function updateCurrentLabel() {
  const clip = getCurrentClip();
  const annotation = clip ? state.annotations[clip.clip_id] : null;
  const label = state.selectedLabel || (annotation ? annotation.label : null);
  els.currentLabel.textContent = label || "unlabeled";
  els.currentLabel.classList.toggle("is-labeled", Boolean(label));
}

function renderQueue() {
  els.clipQueue.innerHTML = "";
  state.manifest.clips.forEach((clip, index) => {
    const annotation = state.annotations[clip.clip_id];
    const item = document.createElement("li");
    item.className = "queue-item";
    if (index === state.index) item.classList.add("is-active");
    if (annotation) item.classList.add("is-labeled");

    const button = document.createElement("button");
    button.type = "button";
    button.innerHTML = `
      <span class="queue-title">${clip.clip_id || `clip-${index + 1}`}</span>
      <span class="queue-meta">${annotation ? annotation.label : "unlabeled"} / ${clip.zone_hint || "no zone"}</span>
    `;
    button.addEventListener("click", () => goToIndex(index));
    item.append(button);
    els.clipQueue.append(item);
  });
}

function renderProgress() {
  const total = state.manifest.clips.length;
  const labeled = state.manifest.clips.filter((clip) => state.annotations[clip.clip_id]).length;
  const percent = total ? Math.round((labeled / total) * 100) : 0;
  els.progressBar.style.width = `${percent}%`;
  els.queueSummary.textContent = `${labeled} / ${total} labeled`;
  els.manifestSummary.textContent = total ? `${total} clips loaded, ${percent}% complete.` : "Load a clip manifest to begin.";
  els.clipCounter.textContent = total ? `${state.index + 1} / ${total}` : "0 / 0";
}

function render() {
  const clip = getCurrentClip();
  const annotation = clip ? state.annotations[clip.clip_id] : null;
  state.selectedLabel = annotation ? annotation.label : state.selectedLabel;

  els.clipTitle.textContent = clip ? clip.clip_id : "No clip selected";
  els.noteInput.value = annotation ? annotation.note : els.noteInput.value;
  setConfidence(annotation ? annotation.confidence : getConfidence());

  renderMedia(clip);
  renderMetadata(clip);
  renderLabels();
  updateCurrentLabel();
  renderQueue();
  renderProgress();
}

function handleKeydown(event) {
  const activeTag = document.activeElement ? document.activeElement.tagName : "";
  if (activeTag === "TEXTAREA" || activeTag === "INPUT") return;

  const number = Number(event.key);
  if (number >= 1 && number <= state.manifest.labels.length) {
    selectLabel(state.manifest.labels[number - 1]);
    saveCurrentAnnotation();
  } else if (event.key === "ArrowRight") {
    goToIndex(state.index + 1);
  } else if (event.key === "ArrowLeft") {
    goToIndex(state.index - 1);
  }
}

els.manifestInput.addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (file) handleManifestFile(file);
});
els.loadSampleButton.addEventListener("click", loadSampleManifest);
els.exportButton.addEventListener("click", exportJsonl);
els.prevButton.addEventListener("click", () => goToIndex(state.index - 1));
els.nextButton.addEventListener("click", () => goToIndex(state.index + 1));
els.saveButton.addEventListener("click", saveCurrentAnnotation);
els.clearButton.addEventListener("click", clearCurrentAnnotation);
document.addEventListener("keydown", handleKeydown);

loadSavedAnnotations();
render();
