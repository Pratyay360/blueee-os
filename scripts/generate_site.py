#!/usr/bin/env python3
"""
Static Site Generator for Blueee OS ISO Downloads & Releases.

Generates a modern, responsive static website with GoFile download links,
embedded QR codes, rebase commands, verification instructions, and API JSON feeds.
"""

import argparse
import html
import json
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_METADATA_FILE = Path(__file__).resolve().parent.parent / "data" / "downloads.json"
DEFAULT_DATA_DIR = "site-data"
DEFAULT_OUTPUT_DIR = "_site"

ICON_DOWNLOAD = (
    '<svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 '
    '5-5M12 15V3"/></svg>'
)
ICON_COPY = (
    '<svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>'
    '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'
)
ICON_CLOCK = (
    '<svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2"><circle cx="12" cy="12" r="10"></circle>'
    '<polyline points="12 6 12 12 16 14"></polyline></svg>'
)
ICON_FILE = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>'
    '<polyline points="14 2 14 8 20 8"></polyline></svg>'
)
ICON_PACKAGE = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 '
    '1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>'
)
ICON_GITHUB = (
    '<svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 '
    '0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23'
    '-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225'
    '-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99'
    '.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23'
    '-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04'
    '.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 '
    '1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 '
    '2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>'
)
ICON_SEARCH = (
    '<svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2"><circle cx="11" cy="11" r="8"></circle>'
    '<line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>'
)
ICON_QR_PLACEHOLDER = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">'
    '<rect x="3" y="3" width="18" height="18" rx="2"/><rect x="7" y="7" width="3" height="3"/>'
    '<rect x="14" y="7" width="3" height="3"/><rect x="7" y="14" width="3" height="3"/>'
    '<path d="M14 14h3v3h-3z"/></svg>'
)

DESKTOP_HINTS = {
    "kde plasma": "Pick this if you like a familiar, Windows-like desktop that just works.",
    "gnome": "Pick this if you want something clean and simple out of the box.",
    "cosmic": "Pick this if you like trying new, tidy desktops.",
    "sway": "Pick this if you live in the keyboard and like tiling.",
}

CSS = """
:root {
  --bg: #111417;
  --card-bg: #1a1e23;
  --card-border: #2b3138;
  --text: #e8eaed;
  --text-muted: #9aa3ad;
  --text-dim: #6b7480;
  --primary: #4da3d8;
  --primary-hover: #3b8fc2;
  --code-bg: #14171b;
  --code-border: #2b3138;
  --radius: 8px;
  --font: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.55;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

a {
  color: var(--primary);
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}

.container {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}

header.hero {
  padding: 48px 0 28px;
  text-align: left;
  border-bottom: 1px solid var(--card-border);
}
.hero-badge {
  display: inline-block;
  border: 1px solid var(--card-border);
  color: var(--text-muted);
  background: var(--card-bg);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  margin-bottom: 16px;
}
.hero-title {
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--text);
  margin-bottom: 10px;
}
.hero-subtitle {
  font-size: 1rem;
  color: var(--text-muted);
  max-width: 640px;
  margin: 0 0 20px;
}
.hero-note {
  font-size: 0.9rem;
  color: var(--text-dim);
  max-width: 640px;
  margin: 0 0 20px;
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.controls-panel {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--radius);
  padding: 16px;
  margin: 28px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.search-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.search-input-wrap {
  position: relative;
  flex: 1;
}
.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: var(--text-dim);
  pointer-events: none;
}
.search-input {
  width: 100%;
  background: var(--code-bg);
  border: 1px solid var(--code-border);
  color: var(--text);
  padding: 10px 12px 10px 38px;
  border-radius: 6px;
  font-size: 0.95rem;
  outline: none;
}
.search-input:focus {
  border-color: var(--primary);
}
.filter-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.filter-label {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 600;
  margin-right: 4px;
}
.filter-btn {
  background: transparent;
  border: 1px solid var(--card-border);
  color: var(--text-muted);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
}
.filter-btn:hover {
  border-color: var(--text-dim);
  color: var(--text);
}
.filter-btn.active {
  background: var(--text);
  color: var(--bg);
  border-color: var(--text);
}
.stats-counter {
  margin-left: auto;
  font-size: 0.88rem;
  color: var(--text-muted);
}

.iso-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 48px;
}

.iso-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  flex-direction: column;
}
.iso-card:hover {
  border-color: var(--text-dim);
}

.card-header {
  margin-bottom: 16px;
}
.badges-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}
.badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid var(--card-border);
}
.badge-desktop {
  background: var(--code-bg);
  color: var(--text-muted);
}
.badge-cachy {
  background: #2a2214;
  border-color: #5a4a2a;
  color: #e0c080;
}
.badge-standard {
  background: var(--code-bg);
  color: var(--text-muted);
}
.badge-tag {
  background: transparent;
  color: var(--text-dim);
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}
.card-desc {
  font-size: 0.9rem;
  color: var(--text-muted);
}
.card-human {
  font-size: 0.88rem;
  color: var(--text-dim);
  margin-top: 8px;
  font-style: italic;
}

.meta-chips-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}
.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.8rem;
  color: var(--text-muted);
}
.meta-chip svg {
  width: 12px;
  height: 12px;
}

.download-action-group {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 9px 14px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  text-decoration: none;
}
.btn-primary {
  flex: 1;
  background: var(--primary);
  color: #0c1116;
}
.btn-primary:hover {
  background: var(--primary-hover);
  text-decoration: none;
}
.btn-secondary {
  background: transparent;
  color: var(--text);
  border-color: var(--card-border);
}
.btn-secondary:hover {
  border-color: var(--text-dim);
}
.btn-disabled {
  flex: 1;
  background: var(--code-bg);
  color: var(--text-dim);
  cursor: not-allowed;
  border-color: var(--card-border);
}
.btn-icon {
  width: 16px;
  height: 16px;
}

.qr-embed-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--code-bg);
  border: 1px solid var(--code-border);
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 14px;
}
.qr-image-wrapper {
  width: 88px;
  height: 88px;
  background: #fff;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  flex-shrink: 0;
}
.qr-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}
.qr-info {
  flex: 1;
  min-width: 0;
}
.qr-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 2px;
}
.qr-helper {
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-bottom: 4px;
}
.qr-link-preview {
  display: block;
  font-size: 0.72rem;
  font-family: monospace;
  color: var(--primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.qr-placeholder {
  width: 88px;
  height: 88px;
  background: var(--code-bg);
  border: 1px dashed var(--card-border);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-dim);
  flex-shrink: 0;
}
.qr-placeholder svg {
  width: 36px;
  height: 36px;
  opacity: 0.5;
}

.checksum-block {
  border-top: 1px solid var(--card-border);
  padding: 10px 0;
  margin-bottom: 12px;
}
.cs-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 600;
  display: block;
  margin-bottom: 2px;
}
.cs-value-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.cs-code {
  font-family: monospace;
  font-size: 0.78rem;
  color: var(--text-muted);
}
.cs-copy {
  background: none;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
}
.cs-copy:hover {
  color: var(--text);
}
.cs-copy svg {
  width: 14px;
  height: 14px;
}

.code-snippets {
  background: var(--code-bg);
  border: 1px solid var(--code-border);
  border-radius: 6px;
  padding: 10px 12px;
  margin-top: 10px;
}
.snippet-small {
  margin-top: 8px;
}
.snippet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.snippet-title {
  font-size: 0.82rem;
  color: var(--text-muted);
  font-weight: 600;
}
.snippet-copy-btn {
  background: transparent;
  border: 1px solid var(--card-border);
  color: var(--text-muted);
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.snippet-copy-btn:hover {
  color: var(--text);
  border-color: var(--text-dim);
}
.snippet-copy-btn svg {
  width: 11px;
  height: 11px;
}
.snippet-pre {
  margin: 0;
  overflow-x: auto;
}
.snippet-pre code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.78rem;
  color: var(--text-muted);
  white-space: pre-wrap;
  word-break: break-all;
}

.guide-section {
  border-top: 1px solid var(--card-border);
  padding: 32px 0;
  margin-bottom: 40px;
}
.guide-title {
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text);
}
.guide-intro {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin-bottom: 20px;
  max-width: 640px;
}
.guide-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}
.guide-card {
  border: 1px solid var(--card-border);
  border-radius: 6px;
  padding: 16px;
  background: var(--card-bg);
}
.guide-step-num {
  font-size: 0.8rem;
  color: var(--text-dim);
  font-weight: 600;
  margin-bottom: 6px;
}
.guide-card h4 {
  font-size: 1rem;
  margin-bottom: 6px;
  color: var(--text);
}
.guide-card p {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.guide-card code {
  font-family: monospace;
  background: var(--code-bg);
  border: 1px solid var(--code-border);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.maintainer-note {
  border: 1px solid var(--card-border);
  border-left: 3px solid var(--primary);
  background: var(--card-bg);
  border-radius: 0 6px 6px 0;
  padding: 16px 18px;
  margin-bottom: 40px;
  font-size: 0.92rem;
  color: var(--text-muted);
}
.maintainer-note strong {
  color: var(--text);
}

footer {
  margin-top: auto;
  border-top: 1px solid var(--card-border);
  padding: 28px 0;
  font-size: 0.85rem;
  color: var(--text-dim);
}
.footer-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}
.footer-links {
  display: flex;
  gap: 20px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}
.modal-backdrop.show {
  display: flex;
}
.modal-box {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  padding: 24px;
  max-width: 380px;
  width: 100%;
  text-align: center;
  position: relative;
}
.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
  padding: 4px 8px;
}
.modal-close:hover {
  color: var(--text);
}
.modal-qr {
  width: 220px;
  height: 220px;
  background: #fff;
  padding: 8px;
  border-radius: 4px;
  margin: 16px auto;
  display: block;
}
.modal-title {
  font-size: 1.1rem;
  color: var(--text);
  font-weight: 700;
}
.modal-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 6px;
}

.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: var(--text);
  color: var(--bg);
  font-size: 0.88rem;
  padding: 10px 16px;
  border-radius: 6px;
  opacity: 0;
  pointer-events: none;
  z-index: 1001;
}
.toast.show {
  opacity: 1;
}

@media (max-width: 768px) {
  .iso-grid {
    grid-template-columns: 1fr;
  }
  .controls-panel {
    padding: 16px;
  }
  .search-row {
    flex-direction: column;
  }
  .stats-counter {
    margin-left: 0;
    width: 100%;
    text-align: right;
  }
  .footer-content {
    flex-direction: column;
    text-align: center;
  }
}
"""

JS = """
document.querySelectorAll('.copy-btn').forEach((btn) => {
  btn.addEventListener('click', async () => {
    const text = btn.getAttribute('data-clipboard');
    if (!text) return;

    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    }
    showToast('Copied.');
  });
});

function showToast(message) {
  const toast = document.getElementById('toast');
  const toastMsg = document.getElementById('toastMsg');
  toastMsg.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2200);
}

function openQrModal(url, title) {
  const modal = document.getElementById('qrModal');
  const img = document.getElementById('modalQrImg');
  const modalTitle = document.getElementById('modalTitle');
  const modalLink = document.getElementById('modalLink');

  img.src = url;
  modalTitle.textContent = title;
  modalLink.textContent = url;
  modal.classList.add('show');
}

function closeQrModal() {
  document.getElementById('qrModal').classList.remove('show');
}

document.querySelectorAll('.qr-image-wrapper').forEach((el) => {
  el.addEventListener('click', () => {
    openQrModal(el.dataset.qr, el.dataset.title);
  });
});

document.getElementById('qrModal').addEventListener('click', closeQrModal);
document.querySelector('.modal-box').addEventListener('click', (event) => {
  event.stopPropagation();
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeQrModal();
});

const searchInput = document.getElementById('searchInput');
const desktopButtons = document.querySelectorAll('.filter-pills button[data-filter]');
const categoryButtons = document.querySelectorAll('.filter-pills button[data-category]');
const cards = Array.from(document.querySelectorAll('.iso-card'));
const statsCounter = document.getElementById('statsCounter');

let currentDesktop = 'all';
let currentCategory = 'all';
let currentSearch = '';

function applyFilters() {
  let visible = 0;

  cards.forEach((card) => {
    const cardDesktop = card.getAttribute('data-desktop') || '';
    const cardCategory = card.getAttribute('data-category') || '';
    const textContent = card.textContent.toLowerCase();

    const matchDesktop = currentDesktop === 'all' || cardDesktop.includes(currentDesktop);
    const matchCategory = currentCategory === 'all' || cardCategory === currentCategory;
    const matchSearch = !currentSearch || textContent.includes(currentSearch);

    if (matchDesktop && matchCategory && matchSearch) {
      card.style.display = 'flex';
      visible++;
    } else {
      card.style.display = 'none';
    }
  });

  statsCounter.textContent = `Showing ${visible} of ${cards.length}`;
}

searchInput.addEventListener('input', (event) => {
  currentSearch = event.target.value.toLowerCase().trim();
  applyFilters();
});

desktopButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    desktopButtons.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    currentDesktop = btn.getAttribute('data-filter');
    applyFilters();
  });
});

categoryButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    categoryButtons.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    currentCategory = btn.getAttribute('data-category');
    applyFilters();
  });
});
"""


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Blueee OS static download site")
    parser.add_argument(
        "--data-dir",
        default=DEFAULT_DATA_DIR,
        help="Directory containing matrix ISO metadata JSON files",
    )
    parser.add_argument(
        "--metadata-file",
        default=str(DEFAULT_METADATA_FILE),
        help="Base/persistent downloads.json metadata file",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for static site",
    )
    return parser.parse_args()


def load_base_metadata(metadata_file: Path) -> dict:
    if metadata_file.is_file():
        with metadata_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "project": {
            "name": "Blueee OS",
            "description": "Custom Fedora Atomic desktop images with Cachy Kernel.",
            "repository": "https://github.com/Pratyay360/blueee-os",
            "documentation": "https://github.com/Pratyay360/blueee-os#readme",
        },
        "images": [],
    }


def make_qr_url(url: str) -> str:
    encoded_url = urllib.parse.quote(url, safe="")
    return f"https://api.qrserver.com/v1/create-qr-code/?size=256x256&data={encoded_url}"


def merge_matrix_artifacts(data: dict, data_dir: Path) -> dict:
    if not data_dir.is_dir():
        return data

    images_by_id = {item["id"]: item for item in data.get("images", [])}

    for json_file in sorted(data_dir.glob("*.json")):
        try:
            with json_file.open("r", encoding="utf-8") as f:
                item_data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Warning: Failed to parse {json_file}: {exc}", file=sys.stderr)
            continue

        name = item_data.get("name") or json_file.stem
        url = (item_data.get("url") or "").strip()
        qrcode = (item_data.get("qrcode") or "").strip()

        if url and not qrcode:
            qrcode = make_qr_url(url)

        if name in images_by_id:
            target = images_by_id[name]
            if url:
                target["url"] = url
            if qrcode:
                target["qrcode"] = qrcode

            for key in ("size", "sha256", "filename", "image", "run_id", "commit_sha"):
                if item_data.get(key):
                    target[key] = item_data[key]

            target["updated_at"] = (
                item_data.get("updated_at") or datetime.now(timezone.utc).isoformat()
            )
        else:
            new_item = {
                "id": name,
                "name": name.replace("-", " ").title(),
                "tag": "latest",
                "description": f"Blueee OS {name} image",
                "desktop": "Other",
                "kernel": "Standard",
                "category": "cachy" if "cachy" in name.lower() else "standard",
                "image": item_data.get("image", f"ghcr.io/pratyay360/{name}:latest"),
                "quay_image": f"quay.io/pratyay360/{name}:latest",
                "filename": item_data.get("filename", f"{name}.iso"),
                "url": url,
                "qrcode": qrcode,
                "size": item_data.get("size", ""),
                "sha256": item_data.get("sha256", ""),
                "updated_at": (
                    item_data.get("updated_at") or datetime.now(timezone.utc).isoformat()
                ),
            }
            images_by_id[name] = new_item
            data.setdefault("images", []).append(new_item)

    return data


def render_card(img: dict) -> str:
    img_id_raw = str(img.get("id", ""))
    name_raw = str(img.get("name", img_id_raw))
    desc_raw = str(img.get("description", ""))
    desktop_raw = str(img.get("desktop", "Desktop"))
    kernel_raw = str(img.get("kernel", "Standard"))
    category_raw = str(img.get("category", "standard"))
    image_uri_raw = str(img.get("image", ""))
    filename_raw = str(img.get("filename", f"{img_id_raw}.iso"))
    url = str(img.get("url", "")).strip()
    qrcode = str(img.get("qrcode", "")).strip()
    size_raw = str(img.get("size", ""))
    sha256_raw = str(img.get("sha256", ""))
    updated_at_raw = str(img.get("updated_at", ""))
    tag_raw = str(img.get("tag", "latest"))

    name = html.escape(name_raw)
    desc = html.escape(desc_raw)
    desktop = html.escape(desktop_raw)
    kernel = html.escape(kernel_raw)
    category = html.escape(category_raw)
    filename = html.escape(filename_raw)
    size = html.escape(size_raw)
    sha256 = html.escape(sha256_raw)
    tag = html.escape(tag_raw)

    is_cachy = "cachy" in category_raw.lower() or "cachy" in kernel_raw.lower()
    kernel_badge_class = "badge-cachy" if is_cachy else "badge-standard"

    human_hint = DESKTOP_HINTS.get(desktop_raw.lower(), "")
    human_hint_html = (
        f'<p class="card-human">{html.escape(human_hint)}</p>' if human_hint else ""
    )

    rebase_ghcr = f"sudo rpm-ostree rebase ostree-unverified-registry:{image_uri_raw}"
    cosign_verify = f"cosign verify --key cosign.pub {image_uri_raw}"

    if url:
        qr = qrcode or make_qr_url(url)
        download_section = f"""
        <div class="download-action-group">
          <a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" title="Download {filename} from GoFile">
            {ICON_DOWNLOAD}
            Download ISO
          </a>
          <button class="btn btn-secondary copy-btn" data-clipboard="{html.escape(url)}" title="Copy download link">
            {ICON_COPY}
            Copy link
          </button>
        </div>
        <div class="qr-embed-card">
          <div class="qr-image-wrapper" data-qr="{html.escape(qr)}" data-title="{name}" title="Click to enlarge QR code">
            <img src="{html.escape(qr)}" alt="QR code to download {name} ISO" class="qr-image" width="160" height="160" loading="lazy" />
          </div>
          <div class="qr-info">
            <div class="qr-label">Send to your phone</div>
            <p class="qr-helper">Scan this with your phone camera to open the download there.</p>
            <span class="qr-link-preview">{html.escape(url)}</span>
          </div>
        </div>
        """
    else:
        download_section = f"""
        <div class="download-action-group">
          <button class="btn btn-disabled" disabled>
            {ICON_CLOCK}
            Still building
          </button>
          <button class="btn btn-secondary copy-btn" data-clipboard="{html.escape(rebase_ghcr)}" title="Copy rebase command">
            {ICON_COPY}
            Use rebase instead
          </button>
        </div>
        <div class="qr-embed-card qr-pending">
          <div class="qr-placeholder">
            {ICON_QR_PLACEHOLDER}
          </div>
          <div class="qr-info">
            <div class="qr-label">No file yet</div>
            <p class="qr-helper">This ISO hasn't finished building. The download and QR code will show up here when it's ready.</p>
          </div>
        </div>
        """

    meta_chips = []
    if size:
        meta_chips.append(f'<span class="meta-chip">{ICON_PACKAGE} {size}</span>')
    meta_chips.append(f'<span class="meta-chip">{ICON_FILE} {filename}</span>')
    if updated_at_raw:
        short_date = html.escape(updated_at_raw.split("T")[0])
        meta_chips.append(f'<span class="meta-chip">{ICON_CLOCK} {short_date}</span>')
    meta_chips_html = "".join(meta_chips)

    if sha256:
        sha_html = f"""
        <div class="checksum-block">
          <span class="cs-label">Checksum (sha256) — optional</span>
          <div class="cs-value-row">
            <code class="cs-code" title="{sha256}">{sha256[:16]}...{sha256[-12:]}</code>
            <button class="cs-copy copy-btn" data-clipboard="{sha256}" title="Copy SHA-256">
              {ICON_COPY}
            </button>
          </div>
        </div>
        """
    else:
        sha_html = ""

    return f"""
    <article class="iso-card" data-desktop="{html.escape(desktop_raw.lower())}" data-category="{html.escape(category_raw.lower())}" data-name="{html.escape(name_raw.lower())}">
      <div class="card-header">
        <div class="badges-row">
          <span class="badge badge-desktop">{desktop}</span>
          <span class="badge {kernel_badge_class}">{kernel}</span>
          <span class="badge badge-tag">{tag}</span>
        </div>
        <h3 class="card-title">{name}</h3>
        <p class="card-desc">{desc}</p>
        {human_hint_html}
      </div>

      <div class="meta-chips-row">
        {meta_chips_html}
      </div>

      {download_section}

      {sha_html}

      <div class="code-snippets">
        <div class="snippet-header">
          <span class="snippet-title">Already on Fedora Atomic? Skip the USB stick:</span>
          <button class="snippet-copy-btn copy-btn" data-clipboard="{html.escape(rebase_ghcr)}" title="Copy rebase command">
            {ICON_COPY}
            Copy
          </button>
        </div>
        <pre class="snippet-pre"><code>{html.escape(rebase_ghcr)}</code></pre>
      </div>

      <div class="code-snippets snippet-small">
        <div class="snippet-header">
          <span class="snippet-title">Check the signature if you like:</span>
          <button class="snippet-copy-btn copy-btn" data-clipboard="{html.escape(cosign_verify)}" title="Copy verification command">
            {ICON_COPY}
            Copy
          </button>
        </div>
        <pre class="snippet-pre"><code>{html.escape(cosign_verify)}</code></pre>
      </div>
    </article>
    """


def generate_html(data: dict) -> str:
    project = data.get("project", {})
    images = data.get("images", [])
    now_str = datetime.now(timezone.utc).strftime("%B %d, %Y %H:%M UTC")

    cards_joined = "\n".join(render_card(img) for img in images)
    total_images = len(images)
    ready_images = sum(1 for img in images if img.get("url"))

    project_name = html.escape(project.get("name", "Blueee OS"))
    project_description = html.escape(
        project.get(
            "description",
            "Fedora Atomic desktops that are ready to use, with a faster kernel option if you want it.",
        )
    )
    repository = html.escape(
        project.get("repository", "https://github.com/Pratyay360/blueee-os")
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blueee OS - ISO Downloads & Releases</title>
  <meta name="description" content="Download Blueee OS bootable ISOs and container images for Fedora Atomic desktops with CachyOS BORE kernel.">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2338bdf8'%3E%3Cpath d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/%3E%3C/svg%3E">
  <style>
{CSS}
  </style>
</head>
<body>

  <header class="hero">
    <div class="container">
      <div class="hero-badge">Fedora Atomic images, rebuilt regularly</div>
      <h1 class="hero-title">Get {project_name}</h1>
      <p class="hero-subtitle">{project_description}</p>
      <p class="hero-note">If you're not sure which one to pick: KDE if you want familiar, GNOME if you want simple. {ready_images} of {total_images} ISOs are ready right now — the rest can still be installed with one rebase command.</p>

      <div class="hero-actions">
        <a href="#downloads" class="btn btn-primary">
          {ICON_DOWNLOAD}
          See the downloads
        </a>
        <a href="{repository}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary">
          {ICON_GITHUB}
          Look at the code
        </a>
      </div>
    </div>
  </header>

  <main class="container" id="downloads">
    <div class="controls-panel">
      <div class="search-row">
        <div class="search-input-wrap">
          {ICON_SEARCH}
          <input type="text" id="searchInput" class="search-input" placeholder="Try 'kde', 'gaming', 'lightweight'..." autocomplete="off">
        </div>
        <div class="stats-counter" id="statsCounter">Showing {total_images} of {total_images}</div>
      </div>

      <div class="filter-pills">
        <span class="filter-label">Desktop:</span>
        <button class="filter-btn active" data-filter="all">Everything</button>
        <button class="filter-btn" data-filter="kde plasma">KDE</button>
        <button class="filter-btn" data-filter="gnome">GNOME</button>
        <button class="filter-btn" data-filter="cosmic">COSMIC</button>
        <button class="filter-btn" data-filter="sway">Sway</button>
      </div>

      <div class="filter-pills">
        <span class="filter-label">Kernel:</span>
        <button class="filter-btn active" data-category="all">Any kernel</button>
        <button class="filter-btn" data-category="cachy">CachyOS (faster)</button>
        <button class="filter-btn" data-category="standard">Fedora stock</button>
      </div>
    </div>

    <div class="iso-grid" id="isoGrid">
      {cards_joined}
    </div>

    <section class="guide-section">
      <h2 class="guide-title">How this usually goes</h2>
      <p class="guide-intro">Nothing fancy here. Grab a file, flash it, or skip the USB entirely if you're already on Atomic.</p>
      <div class="guide-grid">
        <div class="guide-card">
          <div class="guide-step-num">Step 1</div>
          <h4>Grab the ISO</h4>
          <p>Download it here, or scan the QR code to open the same link on your phone.</p>
        </div>
        <div class="guide-card">
          <div class="guide-step-num">Step 2</div>
          <h4>Put it on a USB stick</h4>
          <p>Rufus (in DD mode), Fedora Media Writer, or balenaEtcher all work fine.</p>
          <code>sudo dd if=image.iso of=/dev/sdX bs=4M status=progress</code>
        </div>
        <div class="guide-card">
          <div class="guide-step-num">Step 3 — optional</div>
          <h4>Or just rebase</h4>
          <p>Already on Silverblue, Kinoite, or another Atomic desktop? Copy the rebase command from the card you want. No reinstall needed.</p>
          <code>sudo rpm-ostree rebase ostree-unverified-registry:...</code>
        </div>
        <div class="guide-card">
          <div class="guide-step-num">If you're careful</div>
          <h4>Check the signature</h4>
          <p>Every image is signed. Most people skip this, but it's there if you want it.</p>
          <code>cosign verify --key cosign.pub ghcr.io/...</code>
        </div>
      </div>
    </section>

    <div class="maintainer-note">
      <strong>A quick note:</strong> I build and test these images myself. CachyOS kernel builds feel snappier for games and heavy multitasking, stock Fedora builds are the calmer default. Either way, you can switch later — it's Atomic, that's the point.
    </div>
  </main>

  <footer>
    <div class="container footer-content">
      <div>
        <p><strong>Blueee OS</strong> — put together with BlueBuild. I use these builds day to day.</p>
        <p>Last updated: {now_str} • Something off? Open an issue on GitHub.</p>
      </div>
      <div class="footer-links">
        <a href="downloads.json" target="_blank">downloads.json</a>
        <a href="{repository}" target="_blank">GitHub</a>
        <a href="https://gofile.io/d/Q6Cp6x" target="_blank" rel="noopener noreferrer">GoFile</a>
      </div>
    </div>
  </footer>

  <div class="modal-backdrop" id="qrModal">
    <div class="modal-box">
      <button class="modal-close" onclick="closeQrModal()">&times;</button>
      <h3 class="modal-title" id="modalTitle">Scan to download</h3>
      <p class="modal-desc">Point your phone camera at this to open the download.</p>
      <img id="modalQrImg" src="" alt="QR Code" class="modal-qr" />
      <div id="modalLink" class="qr-link-preview" style="margin-top:12px; font-size:0.8rem;"></div>
    </div>
  </div>

  <div class="toast" id="toast">
    <span id="toastMsg">Copied.</span>
  </div>

  <script>
{JS}
  </script>
</body>
</html>
"""


def md_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def generate_summary_md(data: dict) -> str:
    images = data.get("images", [])
    lines = [
        "# 🚀 Blueee OS ",
        "",
        "| Flavor | Kernel | Desktop | Size | GoFile Download | QR Code (Scan to Download) |",
        "| :--- | :--- | :--- | :--- | :--- | :---: |",
    ]

    for img in images:
        name = md_escape(img.get("name", img.get("id", "")))
        kernel = md_escape(img.get("kernel", "Standard"))
        desktop = md_escape(img.get("desktop", ""))
        size = md_escape(img.get("size", "-"))
        url = img.get("url", "")
        qrcode = img.get("qrcode", "")

        if url:
            link_md = f"[{name} ISO]({url})"
            qr_md = (
                f'<img src="{html.escape(qrcode)}" width="120" height="120" '
                f'alt="QR for {html.escape(name)}" />'
            )
        else:
            link_md = "*Pending*"
            qr_md = "-"

        lines.append(
            f"| **{name}** | {kernel} | {desktop} | {size} | {link_md} | {qr_md} |"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    args = parse_args()
    data_dir = Path(args.data_dir)
    metadata_file = Path(args.metadata_file)
    output_dir = Path(args.output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_base_metadata(metadata_file)
    data = merge_matrix_artifacts(data, data_dir)

    try:
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with metadata_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as exc:
        print(f"Note: Base metadata file {metadata_file} not updated ({exc}); continuing.")

    with (output_dir / "downloads.json").open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    html_content = generate_html(data)
    with (output_dir / "index.html").open("w", encoding="utf-8") as f:
        f.write(html_content)

    summary_md = generate_summary_md(data)
    with (output_dir / "summary.md").open("w", encoding="utf-8") as f:
        f.write(summary_md)

    (output_dir / ".nojekyll").write_text("", encoding="utf-8")

    print(f"Static site successfully generated in '{output_dir}':")
    print(f" - {output_dir / 'index.html'}")
    print(f" - {output_dir / 'downloads.json'}")
    print(f" - {output_dir / 'summary.md'}")
    print(f" - {output_dir / '.nojekyll'}")


if __name__ == "__main__":
    main()
