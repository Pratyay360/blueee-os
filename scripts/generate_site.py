#!/usr/bin/env python3
"""
Static Site Generator for Blueee OS ISO Downloads & Releases.
Generates a modern, responsive static website with GoFile download links,
embedded QR codes, rebase commands, verification instructions, and API JSON feeds.
"""

import os
import sys
import json
import glob
import argparse
from datetime import datetime, timezone
import urllib.parse
import html

DEFAULT_METADATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "downloads.json")
DEFAULT_DATA_DIR = "site-data"
DEFAULT_OUTPUT_DIR = "_site"

def parse_args():
    parser = argparse.ArgumentParser(description="Generate Blueee OS static download site")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help="Directory containing matrix ISO metadata JSON files")
    parser.add_argument("--metadata-file", default=DEFAULT_METADATA_FILE, help="Base/persistent downloads.json metadata file")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Output directory for static site")
    return parser.parse_args()

def load_base_metadata(metadata_file):
    if os.path.isfile(metadata_file):
        with open(metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "project": {
            "name": "Blueee OS",
            "description": "Custom Fedora Atomic desktop images with CachyOS BORE Kernel and standard Fedora kernels. Built with BlueBuild.",
            "repository": "https://github.com/Pratyay360/blueee-os",
            "documentation": "https://github.com/Pratyay360/blueee-os#readme"
        },
        "images": []
    }

def merge_matrix_artifacts(data, data_dir):
    if not os.path.isdir(data_dir):
        return data

    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    images_by_id = {item["id"]: item for item in data.get("images", [])}

    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                item_data = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to parse {jf}: {e}", file=sys.stderr)
            continue

        name = item_data.get("name") or os.path.splitext(os.path.basename(jf))[0]
        url = item_data.get("url", "").strip()
        qrcode = item_data.get("qrcode", "").strip()

        if url and not qrcode:
            encoded_url = urllib.parse.quote(url, safe="")
            qrcode = f"https://api.qrserver.com/v1/create-qr-code/?size=256x256&data={encoded_url}"

        if name in images_by_id:
            target = images_by_id[name]
            if url:
                target["url"] = url
            if qrcode:
                target["qrcode"] = qrcode
            if item_data.get("size"):
                target["size"] = item_data["size"]
            if item_data.get("sha256"):
                target["sha256"] = item_data["sha256"]
            if item_data.get("filename"):
                target["filename"] = item_data["filename"]
            if item_data.get("image"):
                target["image"] = item_data["image"]
            target["updated_at"] = item_data.get("updated_at") or datetime.now(timezone.utc).isoformat()
            if item_data.get("run_id"):
                target["run_id"] = item_data["run_id"]
            if item_data.get("commit_sha"):
                target["commit_sha"] = item_data["commit_sha"]
        else:
            new_item = {
                "id": name,
                "name": name.replace("-", " ").title(),
                "tag": "latest",
                "description": f"Blueee OS {name} image",
                "desktop": "Other",
                "kernel": "Standard",
                "category": "catchy" if "catchy" in name.lower() else "standard",
                "image": item_data.get("image", f"ghcr.io/pratyay360/{name}:latest"),
                "quay_image": f"quay.io/pratyay360/{name}:latest",
                "filename": item_data.get("filename", f"{name}.iso"),
                "url": url,
                "qrcode": qrcode,
                "size": item_data.get("size", ""),
                "sha256": item_data.get("sha256", ""),
                "updated_at": item_data.get("updated_at") or datetime.now(timezone.utc).isoformat()
            }
            images_by_id[name] = new_item
            data.setdefault("images", []).append(new_item)

    return data

def generate_html(data):
    project = data.get("project", {})
    images = data.get("images", [])
    now_str = datetime.now(timezone.utc).strftime("%B %d, %Y %H:%M UTC")

    # Render Cards
    cards_html = []
    for img in images:
        img_id = html.escape(img.get("id", ""))
        name = html.escape(img.get("name", img_id))
        desc = html.escape(img.get("description", ""))
        desktop = html.escape(img.get("desktop", "Desktop"))
        kernel = html.escape(img.get("kernel", "Standard"))
        category = html.escape(img.get("category", "standard"))
        image_uri = html.escape(img.get("image", ""))
        quay_uri = html.escape(img.get("quay_image", ""))
        filename = html.escape(img.get("filename", f"{img_id}.iso"))
        url = img.get("url", "").strip()
        qrcode = img.get("qrcode", "").strip()
        size = html.escape(img.get("size", ""))
        sha256 = html.escape(img.get("sha256", ""))
        updated_at = img.get("updated_at", "")

        is_catchy = "catchy" in category.lower() or "catchy" in kernel.lower()
        kernel_badge_class = "badge-catchy" if is_catchy else "badge-standard"
        kernel_icon = "⚡" if is_catchy else "🐧"

        rebase_ghcr = f"sudo rpm-ostree rebase ostree-unverified-registry:{image_uri}"
        rebase_quay = f"sudo rpm-ostree rebase ostree-unverified-registry:{quay_uri}" if quay_uri else ""
        cosign_verify = f"cosign verify --key cosign.pub {image_uri}"

        # QR and Download button
        if url:
            if not qrcode:
                encoded_url = urllib.parse.quote(url, safe="")
                qrcode = f"https://api.qrserver.com/v1/create-qr-code/?size=256x256&data={encoded_url}"
            safe_url = html.escape(url)
            safe_qrcode = html.escape(qrcode)
            download_section = f"""
            <div class="download-action-group">
              <a href="{safe_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" title="Download {filename} from GoFile">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                Download ISO (GoFile)
              </a>
              <button class="btn btn-secondary copy-btn" data-clipboard="{safe_url}" title="Copy GoFile download link">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                Copy Link
              </button>
            </div>
            <div class="qr-embed-card">
              <div class="qr-image-wrapper" onclick="openQrModal('{safe_qrcode}', '{name}')" title="Click to view high-res QR code">
                <img src="{safe_qrcode}" alt="Scan QR code to download {name} ISO" class="qr-image" width="160" height="160" loading="lazy" />
                <div class="qr-overlay"><span class="qr-overlay-text">🔍 Enlarge</span></div>
              </div>
              <div class="qr-info">
                <div class="qr-label"><span class="pulse-dot"></span> Mobile Fast Download</div>
                <p class="qr-helper">Scan with phone camera to download directly to your mobile device</p>
                <span class="qr-link-preview">{safe_url}</span>
              </div>
            </div>
            """
        else:
            download_section = f"""
            <div class="download-action-group">
              <button class="btn btn-disabled" disabled>
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                ISO Pending Build
              </button>
              <button class="btn btn-secondary copy-btn" data-clipboard="{rebase_ghcr}" title="Copy rpm-ostree rebase command">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                Rebase Instead
              </button>
            </div>
            <div class="qr-embed-card qr-pending">
              <div class="qr-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><rect x="7" y="7" width="3" height="3"/><rect x="14" y="7" width="3" height="3"/><rect x="7" y="14" width="3" height="3"/><path d="M14 14h3v3h-3z"/></svg>
              </div>
              <div class="qr-info">
                <div class="qr-label">QR Code Pending</div>
                <p class="qr-helper">QR code will be available immediately after the next ISO build runs</p>
              </div>
            </div>
            """

        meta_chips = []
        if size:
            meta_chips.append(f'<span class="meta-chip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg> {size}</span>')
        meta_chips.append(f'<span class="meta-chip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg> {filename}</span>')
        if updated_at:
            short_date = updated_at.split("T")[0]
            meta_chips.append(f'<span class="meta-chip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> {short_date}</span>')
        meta_chips_html = "".join(meta_chips)

        sha_html = ""
        if sha256:
            sha_html = f"""
            <div class="checksum-block">
              <span class="cs-label">SHA-256 Checksum</span>
              <div class="cs-value-row">
                <code class="cs-code" title="{sha256}">{sha256[:16]}...{sha256[-12:]}</code>
                <button class="cs-copy copy-btn" data-clipboard="{sha256}" title="Copy SHA-256">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </button>
              </div>
            </div>
            """

        card = f"""
        <article class="iso-card" data-desktop="{desktop.lower()}" data-category="{category.lower()}" data-name="{name.lower()}">
          <div class="card-header">
            <div class="badges-row">
              <span class="badge badge-desktop">{desktop}</span>
              <span class="badge {kernel_badge_class}">{kernel_icon} {kernel}</span>
              <span class="badge badge-tag">{html.escape(img.get("tag", "latest"))}</span>
            </div>
            <h3 class="card-title">{name}</h3>
            <p class="card-desc">{desc}</p>
          </div>

          <div class="meta-chips-row">
            {meta_chips_html}
          </div>

          {download_section}

          {sha_html}

          <div class="code-snippets">
            <div class="snippet-header">
              <span class="snippet-title">Container Rebase (No Flash Required)</span>
              <button class="snippet-copy-btn copy-btn" data-clipboard="{rebase_ghcr}" title="Copy rebase command">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                Copy
              </button>
            </div>
            <pre class="snippet-pre"><code>{html.escape(rebase_ghcr)}</code></pre>
          </div>

          <div class="code-snippets snippet-small">
            <div class="snippet-header">
              <span class="snippet-title">Cosign Signature Verification</span>
              <button class="snippet-copy-btn copy-btn" data-clipboard="{cosign_verify}" title="Copy verification command">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                Copy
              </button>
            </div>
            <pre class="snippet-pre"><code>{html.escape(cosign_verify)}</code></pre>
          </div>
        </article>
        """
        cards_html.append(card)

    cards_joined = "\n".join(cards_html)
    total_images = len(images)
    ready_images = sum(1 for img in images if img.get("url"))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blueee OS - ISO Downloads & Releases</title>
  <meta name="description" content="Download Blueee OS bootable ISOs and container images for Fedora Atomic desktops with CachyOS BORE kernel.">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2338bdf8'%3E%3Cpath d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/%3E%3C/svg%3E">
  <style>
    :root {{
      --bg: #0b0f19;
      --card-bg: rgba(22, 30, 49, 0.7);
      --card-border: rgba(56, 189, 248, 0.15);
      --card-border-hover: rgba(56, 189, 248, 0.4);
      --card-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6);
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --primary: #38bdf8;
      --primary-hover: #0ea5e9;
      --primary-glow: rgba(56, 189, 248, 0.25);
      --accent-cachy: #f59e0b;
      --accent-gnome: #10b981;
      --accent-kde: #6366f1;
      --code-bg: #060911;
      --code-border: #1e293b;
      --radius: 16px;
      --font: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: var(--font);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-image: 
        radial-gradient(circle at 15% 10%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 85% 30%, rgba(99, 102, 241, 0.07) 0%, transparent 45%),
        radial-gradient(circle at 50% 90%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
      background-attachment: fixed;
    }}

    a {{
      color: var(--primary);
      text-decoration: none;
      transition: color 0.2s;
    }}
    a:hover {{
      color: var(--primary-hover);
    }}

    .container {{
      width: 100%;
      max-width: 1320px;
      margin: 0 auto;
      padding: 0 24px;
    }}

    /* Header */
    header.hero {{
      padding: 60px 0 36px;
      text-align: center;
      position: relative;
    }}
    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.25);
      color: var(--primary);
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 20px;
      letter-spacing: 0.5px;
    }}
    .hero-title {{
      font-size: clamp(2.4rem, 5vw, 3.6rem);
      font-weight: 800;
      letter-spacing: -1px;
      background: linear-gradient(135deg, #ffffff 30%, #38bdf8 70%, #818cf8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 16px;
    }}
    .hero-subtitle {{
      font-size: clamp(1rem, 2vw, 1.25rem);
      color: var(--text-muted);
      max-width: 760px;
      margin: 0 auto 28px;
    }}
    .hero-actions {{
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 12px;
    }}

    /* Controls: Search and Filters */
    .controls-panel {{
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: var(--radius);
      padding: 20px 24px;
      margin-bottom: 36px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      box-shadow: var(--card-shadow);
    }}
    .search-row {{
      display: flex;
      gap: 12px;
      align-items: center;
    }}
    .search-input-wrap {{
      position: relative;
      flex: 1;
    }}
    .search-icon {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      width: 18px;
      height: 18px;
      color: var(--text-dim);
      pointer-events: none;
    }}
    .search-input {{
      width: 100%;
      background: var(--code-bg);
      border: 1px solid var(--code-border);
      color: var(--text);
      padding: 12px 14px 12px 42px;
      border-radius: 10px;
      font-size: 0.95rem;
      outline: none;
      transition: all 0.2s;
    }}
    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 2px var(--primary-glow);
    }}
    .filter-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .filter-label {{
      font-size: 0.82rem;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.8px;
      font-weight: 700;
      margin-right: 4px;
    }}
    .filter-btn {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: var(--text-muted);
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .filter-btn:hover {{
      background: rgba(255, 255, 255, 0.1);
      color: var(--text);
    }}
    .filter-btn.active {{
      background: var(--primary);
      color: #030712;
      border-color: var(--primary);
      font-weight: 600;
    }}
    .stats-counter {{
      margin-left: auto;
      font-size: 0.88rem;
      color: var(--text-muted);
    }}

    /* Grid */
    .iso-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 28px;
      margin-bottom: 60px;
    }}

    /* Card */
    .iso-card {{
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: var(--radius);
      padding: 24px;
      display: flex;
      flex-direction: column;
      box-shadow: var(--card-shadow);
      transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
      position: relative;
    }}
    .iso-card:hover {{
      transform: translateY(-4px);
      border-color: var(--card-border-hover);
      box-shadow: 0 16px 36px -12px rgba(56, 189, 248, 0.15);
    }}

    .card-header {{
      margin-bottom: 16px;
    }}
    .badges-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 12px;
    }}
    .badge {{
      font-size: 0.75rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .badge-desktop {{
      background: rgba(99, 102, 241, 0.15);
      border: 1px solid rgba(99, 102, 241, 0.3);
      color: #a5b4fc;
    }}
    .badge-catchy {{
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.3);
      color: #fcd34d;
    }}
    .badge-standard {{
      background: rgba(148, 163, 184, 0.15);
      border: 1px solid rgba(148, 163, 184, 0.3);
      color: #cbd5e1;
    }}
    .badge-tag {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: var(--text-dim);
    }}

    .card-title {{
      font-size: 1.4rem;
      font-weight: 700;
      color: #fff;
      margin-bottom: 6px;
    }}
    .card-desc {{
      font-size: 0.88rem;
      color: var(--text-muted);
      min-height: 42px;
    }}

    .meta-chips-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 20px;
    }}
    .meta-chip {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 0.78rem;
      color: var(--text-dim);
      background: rgba(0, 0, 0, 0.25);
      padding: 3px 8px;
      border-radius: 6px;
      border: 1px solid rgba(255, 255, 255, 0.04);
    }}
    .meta-chip svg {{
      width: 12px;
      height: 12px;
    }}

    /* Buttons */
    .download-action-group {{
      display: flex;
      gap: 10px;
      margin-bottom: 16px;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      font-size: 0.9rem;
      font-weight: 600;
      padding: 10px 16px;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s;
      border: none;
      text-decoration: none;
    }}
    .btn-primary {{
      flex: 1;
      background: var(--primary);
      color: #030712;
      box-shadow: 0 4px 14px rgba(56, 189, 248, 0.3);
    }}
    .btn-primary:hover {{
      background: var(--primary-hover);
      color: #030712;
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(56, 189, 248, 0.4);
    }}
    .btn-secondary {{
      background: rgba(255, 255, 255, 0.08);
      color: var(--text);
      border: 1px solid rgba(255, 255, 255, 0.12);
    }}
    .btn-secondary:hover {{
      background: rgba(255, 255, 255, 0.15);
      color: #fff;
    }}
    .btn-disabled {{
      flex: 1;
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-dim);
      cursor: not-allowed;
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .btn-icon {{
      width: 16px;
      height: 16px;
    }}

    /* QR Code Card */
    .qr-embed-card {{
      display: flex;
      align-items: center;
      gap: 16px;
      background: rgba(6, 9, 17, 0.6);
      border: 1px solid var(--code-border);
      border-radius: 12px;
      padding: 12px;
      margin-bottom: 16px;
    }}
    .qr-image-wrapper {{
      position: relative;
      width: 100px;
      height: 100px;
      background: #ffffff;
      padding: 6px;
      border-radius: 8px;
      cursor: pointer;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .qr-image-wrapper:hover {{
      transform: scale(1.04);
      box-shadow: 0 6px 16px rgba(56, 189, 248, 0.3);
    }}
    .qr-image {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }}
    .qr-overlay {{
      position: absolute;
      inset: 0;
      background: rgba(15, 23, 42, 0.7);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.2s;
    }}
    .qr-image-wrapper:hover .qr-overlay {{
      opacity: 1;
    }}
    .qr-overlay-text {{
      color: #fff;
      font-size: 0.75rem;
      font-weight: 700;
    }}
    .qr-info {{
      flex: 1;
      min-width: 0;
    }}
    .qr-label {{
      font-size: 0.85rem;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 4px;
    }}
    .pulse-dot {{
      width: 7px;
      height: 7px;
      background: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 8px #10b981;
      display: inline-block;
    }}
    .qr-helper {{
      font-size: 0.78rem;
      color: var(--text-dim);
      line-height: 1.35;
      margin-bottom: 6px;
    }}
    .qr-link-preview {{
      display: block;
      font-size: 0.72rem;
      font-family: monospace;
      color: var(--primary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .qr-placeholder {{
      width: 100px;
      height: 100px;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-dim);
      flex-shrink: 0;
    }}
    .qr-placeholder svg {{
      width: 36px;
      height: 36px;
      opacity: 0.5;
    }}

    /* Checksum */
    .checksum-block {{
      background: rgba(6, 9, 17, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 8px 12px;
      margin-bottom: 16px;
    }}
    .cs-label {{
      font-size: 0.72rem;
      color: var(--text-dim);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      display: block;
      margin-bottom: 2px;
    }}
    .cs-value-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }}
    .cs-code {{
      font-family: monospace;
      font-size: 0.78rem;
      color: var(--text-muted);
    }}
    .cs-copy {{
      background: none;
      border: none;
      color: var(--text-dim);
      cursor: pointer;
      padding: 2px;
      display: flex;
      align-items: center;
      transition: color 0.15s;
    }}
    .cs-copy:hover {{
      color: var(--primary);
    }}
    .cs-copy svg {{
      width: 14px;
      height: 14px;
    }}

    /* Snippets */
    .code-snippets {{
      background: var(--code-bg);
      border: 1px solid var(--code-border);
      border-radius: 10px;
      padding: 10px 12px;
      margin-top: 10px;
    }}
    .snippet-small {{
      margin-top: 8px;
    }}
    .snippet-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }}
    .snippet-title {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-dim);
      font-weight: 700;
    }}
    .snippet-copy-btn {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: var(--text-muted);
      font-size: 0.7rem;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 4px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s;
    }}
    .snippet-copy-btn:hover {{
      background: rgba(255, 255, 255, 0.12);
      color: #fff;
    }}
    .snippet-copy-btn svg {{
      width: 11px;
      height: 11px;
    }}
    .snippet-pre {{
      margin: 0;
      overflow-x: auto;
    }}
    .snippet-pre code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.76rem;
      color: #38bdf8;
      white-space: pre;
    }}

    /* Guide Section */
    .guide-section {{
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: var(--radius);
      padding: 36px 32px;
      margin-bottom: 60px;
    }}
    .guide-title {{
      font-size: 1.6rem;
      font-weight: 700;
      margin-bottom: 24px;
      color: #fff;
    }}
    .guide-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 24px;
    }}
    .guide-card {{
      background: rgba(6, 9, 17, 0.5);
      border: 1px solid var(--code-border);
      border-radius: 12px;
      padding: 20px;
    }}
    .guide-step-num {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 8px;
      background: var(--primary-glow);
      color: var(--primary);
      font-weight: 800;
      font-size: 0.85rem;
      margin-bottom: 12px;
    }}
    .guide-card h4 {{
      font-size: 1.05rem;
      margin-bottom: 8px;
      color: #fff;
    }}
    .guide-card p {{
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.5;
      margin-bottom: 10px;
    }}
    .guide-card code {{
      font-family: monospace;
      background: rgba(255, 255, 255, 0.07);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.8rem;
      color: #e2e8f0;
    }}

    /* Footer */
    footer {{
      margin-top: auto;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      padding: 36px 0;
      background: rgba(6, 9, 17, 0.8);
      font-size: 0.85rem;
      color: var(--text-dim);
    }}
    .footer-content {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }}
    .footer-links {{
      display: flex;
      gap: 20px;
    }}

    /* QR Modal */
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(3, 7, 18, 0.85);
      backdrop-filter: blur(8px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 20px;
    }}
    .modal-backdrop.show {{
      display: flex;
    }}
    .modal-box {{
      background: #0f172a;
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 32px;
      max-width: 420px;
      width: 100%;
      text-align: center;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
      position: relative;
    }}
    .modal-close {{
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
    }}
    .modal-close:hover {{
      color: #fff;
    }}
    .modal-qr {{
      width: 256px;
      height: 256px;
      background: #fff;
      padding: 12px;
      border-radius: 12px;
      margin: 16px auto;
      display: block;
    }}
    .modal-title {{
      font-size: 1.25rem;
      color: #fff;
      font-weight: 700;
    }}
    .modal-desc {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 6px;
    }}

    /* Toast Notification */
    .toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #10b981;
      color: #030712;
      font-weight: 700;
      font-size: 0.88rem;
      padding: 10px 18px;
      border-radius: 10px;
      box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
      display: flex;
      align-items: center;
      gap: 8px;
      opacity: 0;
      transform: translateY(12px);
      transition: all 0.25s ease;
      pointer-events: none;
      z-index: 1001;
    }}
    .toast.show {{
      opacity: 1;
      transform: translateY(0);
    }}

    @media (max-width: 768px) {{
      .iso-grid {{
        grid-template-columns: 1fr;
      }}
      .controls-panel {{
        padding: 16px;
      }}
      .search-row {{
        flex-direction: column;
      }}
      .stats-counter {{
        margin-left: 0;
        width: 100%;
        text-align: right;
      }}
      .footer-content {{
        flex-direction: column;
        text-align: center;
      }}
    }}
  </style>
</head>
<body>

  <header class="hero">
    <div class="container">
      <div class="hero-badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
        Fedora 44 Atomic • BlueBuild • CachyOS Kernel
      </div>
      <h1 class="hero-title">{html.escape(project.get("name", "Blueee OS"))} ISO Downloads</h1>
      <p class="hero-subtitle">{html.escape(project.get("description", "Custom Fedora Atomic desktop images with CachyOS BORE Kernel. Built with BlueBuild."))}</p>
      
      <div class="hero-actions">
        <a href="#downloads" class="btn btn-primary">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
          Browse ISO Downloads ({ready_images}/{total_images} Ready)
        </a>
        <a href="{html.escape(project.get("repository", "https://github.com/Pratyay360/blueee-os"))}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
          GitHub Repository
        </a>
      </div>
    </div>
  </header>

  <main class="container" id="downloads">
    <div class="controls-panel">
      <div class="search-row">
        <div class="search-input-wrap">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input type="text" id="searchInput" class="search-input" placeholder="Search by name, desktop environment, kernel, or tag..." autocomplete="off">
        </div>
        <div class="stats-counter" id="statsCounter">Showing {total_images} of {total_images} images</div>
      </div>

      <div class="filter-pills">
        <span class="filter-label">Desktop:</span>
        <button class="filter-btn active" data-filter="all">All</button>
        <button class="filter-btn" data-filter="kde plasma">KDE Plasma</button>
        <button class="filter-btn" data-filter="gnome">GNOME</button>
        <button class="filter-btn" data-filter="cosmic">COSMIC</button>
        <button class="filter-btn" data-filter="sway">Sway</button>
      </div>

      <div class="filter-pills">
        <span class="filter-label">Kernel:</span>
        <button class="filter-btn active" data-category="all">All Kernels</button>
        <button class="filter-btn" data-category="catchy">⚡ CachyOS BORE Kernel</button>
        <button class="filter-btn" data-category="standard">🐧 Fedora Standard Kernel</button>
      </div>
    </div>

    <div class="iso-grid" id="isoGrid">
      {cards_joined}
    </div>

    <section class="guide-section">
      <h2 class="guide-title">Installation & Usage Guide</h2>
      <div class="guide-grid">
        <div class="guide-card">
          <div class="guide-step-num">1</div>
          <h4>Download ISO or Scan QR</h4>
          <p>Download directly to your PC or scan the embedded QR code on your smartphone/tablet to save the ISO.</p>
          <code>balenaEtcher / Rufus / dd</code>
        </div>
        <div class="guide-card">
          <div class="guide-step-num">2</div>
          <h4>Flash to USB Drive</h4>
          <p>Use Rufus (in DD mode), balenaEtcher, or Fedora Media Writer to write the downloaded ISO to a USB flash drive.</p>
          <code>sudo dd if=image.iso of=/dev/sdX bs=4M status=progress</code>
        </div>
        <div class="guide-card">
          <div class="guide-step-num">3</div>
          <h4>In-place Rebase (Alternative)</h4>
          <p>Already on Fedora Silverblue, Kinoite, or an Atomic spin? You don't need to reinstall. Rebase directly via rpm-ostree.</p>
          <code>sudo rpm-ostree rebase ostree-unverified-registry:...</code>
        </div>
        <div class="guide-card">
          <div class="guide-step-num">4</div>
          <h4>Cosign Verification</h4>
          <p>All container builds are cryptographically signed using Cosign and verified against the repository public key.</p>
          <code>cosign verify --key cosign.pub ghcr.io/...</code>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="container footer-content">
      <div>
        <p><strong>Blueee OS</strong> • Built automatically with BlueBuild & GitHub Actions</p>
        <p>Site updated: {now_str}</p>
      </div>
      <div class="footer-links">
        <a href="downloads.json" target="_blank">Downloads JSON API</a>
        <a href="{html.escape(project.get("repository", "https://github.com/Pratyay360/blueee-os"))}" target="_blank">GitHub</a>
        <a href="https://gofile.io" target="_blank" rel="noopener noreferrer">GoFile Mirror</a>
      </div>
    </div>
  </footer>

  <!-- QR Modal -->
  <div class="modal-backdrop" id="qrModal" onclick="closeQrModal(event)">
    <div class="modal-box" onclick="event.stopPropagation()">
      <button class="modal-close" onclick="closeQrModal()">&times;</button>
      <h3 class="modal-title" id="modalTitle">Scan to Download</h3>
      <p class="modal-desc">Point your phone camera at the QR code to open the GoFile download page.</p>
      <img id="modalQrImg" src="" alt="Enlarged QR Code" class="modal-qr" />
      <div id="modalLink" class="qr-link-preview" style="margin-top:12px; font-size:0.8rem;"></div>
    </div>
  </div>

  <!-- Toast -->
  <div class="toast" id="toast">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
    <span id="toastMsg">Copied to clipboard!</span>
  </div>

  <script>
    // Copy to clipboard with toast notification
    document.querySelectorAll('.copy-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const text = btn.getAttribute('data-clipboard');
        if (!text) return;
        navigator.clipboard.writeText(text).then(() => {{
          showToast('Copied to clipboard!');
        }}).catch(err => {{
          // fallback
          const textarea = document.createElement('textarea');
          textarea.value = text;
          document.body.appendChild(textarea);
          textarea.select();
          document.execCommand('copy');
          document.body.removeChild(textarea);
          showToast('Copied to clipboard!');
        }});
      }});
    }});

    function showToast(message) {{
      const toast = document.getElementById('toast');
      const toastMsg = document.getElementById('toastMsg');
      toastMsg.textContent = message;
      toast.classList.add('show');
      setTimeout(() => {{
        toast.classList.remove('show');
      }}, 2200);
    }}

    // QR Modal
    function openQrModal(url, title) {{
      const modal = document.getElementById('qrModal');
      const img = document.getElementById('modalQrImg');
      const modalTitle = document.getElementById('modalTitle');
      const modalLink = document.getElementById('modalLink');
      img.src = url;
      modalTitle.textContent = title + ' - Scan to Download';
      modalLink.textContent = url;
      modal.classList.add('show');
    }}

    function closeQrModal(e) {{
      const modal = document.getElementById('qrModal');
      modal.classList.remove('show');
    }}

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') closeQrModal();
    }});

    // Live search and filtering
    const searchInput = document.getElementById('searchInput');
    const desktopButtons = document.querySelectorAll('.filter-pills button[data-filter]');
    const categoryButtons = document.querySelectorAll('.filter-pills button[data-category]');
    const cards = document.querySelectorAll('.iso-card');
    const statsCounter = document.getElementById('statsCounter');

    let currentDesktop = 'all';
    let currentCategory = 'all';
    let currentSearch = '';

    function applyFilters() {{
      let visible = 0;
      cards.forEach(card => {{
        const cardDesktop = card.getAttribute('data-desktop') || '';
        const cardCategory = card.getAttribute('data-category') || '';
        const cardName = card.getAttribute('data-name') || '';
        const textContent = card.textContent.toLowerCase();

        const matchDesktop = (currentDesktop === 'all') || (cardDesktop.includes(currentDesktop));
        const matchCategory = (currentCategory === 'all') || (cardCategory === currentCategory);
        const matchSearch = (!currentSearch) || (textContent.includes(currentSearch));

        if (matchDesktop && matchCategory && matchSearch) {{
          card.style.display = 'flex';
          visible++;
        }} else {{
          card.style.display = 'none';
        }}
      }});
      statsCounter.textContent = `Showing ${{visible}} of ${{cards.length}} images`;
    }}

    searchInput.addEventListener('input', (e) => {{
      currentSearch = e.target.value.toLowerCase().trim();
      applyFilters();
    }});

    desktopButtons.forEach(btn => {{
      btn.addEventListener('click', () => {{
        desktopButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentDesktop = btn.getAttribute('data-filter');
        applyFilters();
      }});
    }});

    categoryButtons.forEach(btn => {{
      btn.addEventListener('click', () => {{
        categoryButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentCategory = btn.getAttribute('data-category');
        applyFilters();
      }});
    }});
  </script>
</body>
</html>
"""
    return html_content

def generate_summary_md(data):
    images = data.get("images", [])
    lines = [
        "# 🚀 Blueee OS - ISO Builds & GoFile Links",
        "",
        "| Flavor | Kernel | Desktop | Size | GoFile Download | QR Code (Scan to Download) |",
        "| :--- | :--- | :--- | :--- | :--- | :---: |"
    ]
    for img in images:
        name = img.get("name", img.get("id", ""))
        kernel = img.get("kernel", "Standard")
        desktop = img.get("desktop", "")
        size = img.get("size", "-")
        url = img.get("url", "")
        qrcode = img.get("qrcode", "")
        if url:
            link_md = f"[{name} ISO]({url})"
            qr_md = f'<img src="{qrcode}" width="120" height="120" alt="QR for {name}" />'
        else:
            link_md = "*Pending*"
            qr_md = "-"
        lines.append(f"| **{name}** | {kernel} | {desktop} | {size} | {link_md} | {qr_md} |")
    lines.append("")
    return "\n".join(lines)

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    data = load_base_metadata(args.metadata_file)
    data = merge_matrix_artifacts(data, args.data_dir)

    # Save merged data back to base metadata file if writable
    try:
        os.makedirs(os.path.dirname(os.path.abspath(args.metadata_file)), exist_ok=True)
        with open(args.metadata_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        print(f"Note: Base metadata file {args.metadata_file} not updated ({e}); continuing.")

    # Save API data to _site/downloads.json
    site_json = os.path.join(args.output_dir, "downloads.json")
    with open(site_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Generate _site/index.html
    html_content = generate_html(data)
    site_html = os.path.join(args.output_dir, "index.html")
    with open(site_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Generate summary for GitHub Actions ($GITHUB_STEP_SUMMARY)
    summary_md = generate_summary_md(data)
    summary_path = os.path.join(args.output_dir, "summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_md)

    # Add .nojekyll for GitHub Pages
    nojekyll_path = os.path.join(args.output_dir, ".nojekyll")
    with open(nojekyll_path, "w", encoding="utf-8") as f:
        f.write("")

    print(f"Static site successfully generated in '{args.output_dir}':")
    print(f" - {site_html}")
    print(f" - {site_json}")
    print(f" - {summary_path}")
    print(f" - {nojekyll_path}")

if __name__ == "__main__":
    main()
