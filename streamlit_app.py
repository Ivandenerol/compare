import streamlit as st
import difflib
import re
import io
from datetime import datetime

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FortiWeb Config Comparator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg: #0d1117;
    --surface: #161b22;
    --surface2: #1c2128;
    --border: #30363d;
    --accent: #00d4aa;
    --accent2: #ff6b6b;
    --accent3: #ffd93d;
    --text: #e6edf3;
    --text-muted: #7d8590;
    --added: #1a4731;
    --added-text: #3fb950;
    --removed: #3d1a1a;
    --removed-text: #f85149;
    --changed: #3d3210;
    --changed-text: #e3b341;
    --mono: 'JetBrains Mono', monospace;
    --sans: 'Syne', sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--surface) !important; }

h1, h2, h3, h4 { font-family: var(--sans) !important; color: var(--text) !important; }

/* Upload zones */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 8px !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stMetricValue"] { font-family: var(--mono) !important; font-size: 2rem !important; }

/* Diff blocks */
.diff-added {
    background: var(--added);
    color: var(--added-text);
    font-family: var(--mono);
    font-size: 0.78rem;
    padding: 2px 8px;
    border-left: 3px solid var(--added-text);
    white-space: pre-wrap;
    word-break: break-all;
}
.diff-removed {
    background: var(--removed);
    color: var(--removed-text);
    font-family: var(--mono);
    font-size: 0.78rem;
    padding: 2px 8px;
    border-left: 3px solid var(--removed-text);
    white-space: pre-wrap;
    word-break: break-all;
}
.diff-context {
    background: var(--surface2);
    color: var(--text-muted);
    font-family: var(--mono);
    font-size: 0.78rem;
    padding: 2px 8px;
    white-space: pre-wrap;
    word-break: break-all;
}
.diff-hunk {
    background: #1d2d3e;
    color: #58a6ff;
    font-family: var(--mono);
    font-size: 0.78rem;
    padding: 2px 8px;
}

/* Section cards */
.section-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
}
.section-title {
    font-family: var(--sans);
    font-weight: 700;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 12px;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    font-family: var(--mono);
    margin: 2px;
}
.badge-added   { background: var(--added);   color: var(--added-text); }
.badge-removed { background: var(--removed); color: var(--removed-text); }
.badge-changed { background: var(--changed); color: var(--changed-text); }

/* Header banner */
.hero {
    text-align: center;
    padding: 40px 0 20px;
}
.hero-title {
    font-family: var(--sans);
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent), #00a8ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}
.hero-sub {
    color: var(--text-muted);
    font-size: 1rem;
    font-family: var(--mono);
}

/* Device info pills */
.device-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 30px;
    padding: 6px 16px;
    font-family: var(--mono);
    font-size: 0.82rem;
}
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot-old { background: var(--accent2); }
.dot-new { background: var(--accent); }

/* Expander styling */
details { border: 1px solid var(--border) !important; border-radius: 8px !important; }
summary { font-family: var(--mono) !important; font-size: 0.85rem !important; }

/* Buttons */
[data-testid="stDownloadButton"] > button {
    background: var(--accent) !important;
    color: #0d1117 !important;
    font-family: var(--mono) !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
}

/* Recommendation list */
.rec-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.88rem;
}
.rec-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }

/* Hide streamlit branding */
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }

/* Tab styling */
[data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 8px; }
[data-baseweb="tab"] { color: var(--text-muted) !important; font-family: var(--mono) !important; }
[aria-selected="true"] { color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Core Parser ─────────────────────────────────────────────────────────────

def extract_text_lines(file_bytes: bytes) -> list[str]:
    """Extract meaningful config text lines from a FortiWeb .conf file (may contain binary/gzip blobs)."""
    lines = []
    in_cert = False

    for raw_line in file_bytes.split(b'\n'):
        try:
            line = raw_line.decode('utf-8', errors='ignore').rstrip()
        except Exception:
            continue

        # Skip lines with lots of non-printable characters (binary blobs)
        non_print = sum(1 for c in line if ord(c) < 9 or (13 < ord(c) < 32))
        if non_print > 3:
            continue

        # Track and skip cert/key blocks
        if '-----BEGIN CERTIFICATE-----' in line or '-----BEGIN ENCRYPTED PRIVATE KEY-----' in line:
            in_cert = True
        if '-----END CERTIFICATE-----' in line or '-----END ENCRYPTED PRIVATE KEY-----' in line:
            in_cert = False
            continue
        if in_cert:
            continue

        stripped = line.strip()
        if not stripped:
            continue

        # Keep only meaningful config lines
        meaningful_prefixes = (
            'set ', 'edit ', 'config ', 'end', 'next',
            '#', '[', 'image_version=', 'model=', 'name=',
            'magic=', 'version=', 'type=', 'domain=', 'encrypt=',
            'compress=', '-------'
        )
        if any(stripped.startswith(p) for p in meaningful_prefixes):
            lines.append(line)

    return lines


def parse_header(lines: list[str]) -> dict:
    """Extract header metadata from config lines."""
    info = {}
    for line in lines:
        s = line.strip()
        for key in ['image_version', 'model', 'magic', 'version', 'type']:
            if s.startswith(f'{key}='):
                info[key] = s.split('=', 1)[1]
        if s.startswith('-------') and '-------' in s[7:]:
            parts = [p.strip() for p in s.strip('-').split('-------') if p.strip()]
            if len(parts) >= 2:
                info.setdefault('timestamp', parts[1])
            if len(parts) >= 1 and not info.get('build_stamp'):
                info['build_stamp'] = parts[0]
        if s.startswith('#config-version='):
            info['config_version'] = s[1:]
    return info


def categorize_diff(old_lines: list[str], new_lines: list[str]) -> dict:
    """Run diff and group changes into logical categories."""

    categories = {
        "hardware": {"label": "Hardware / Model", "icon": "🖥️", "changes": []},
        "system_global": {"label": "System Global", "icon": "⚙️", "changes": []},
        "network": {"label": "Network Interface & Routing", "icon": "🌐", "changes": []},
        "admin_users": {"label": "Admin Users & Passwords", "icon": "👤", "changes": []},
        "dashboard": {"label": "Dashboard Widgets", "icon": "📊", "changes": []},
        "waf_policy": {"label": "WAF / Security Policies", "icon": "🛡️", "changes": []},
        "cookie": {"label": "Cookie Security", "icon": "🍪", "changes": []},
        "certificates": {"label": "Certificates", "icon": "🔐", "changes": []},
        "license": {"label": "License / Contract", "icon": "📄", "changes": []},
        "report": {"label": "Report Configuration", "icon": "📋", "changes": []},
        "server_pool": {"label": "Server Pool / Policy IDs", "icon": "🔗", "changes": []},
        "other": {"label": "Other", "icon": "📦", "changes": []},
    }

    keyword_map = [
        (["image_version=", "model=", "config-version", "FGBK", "file_split", "build_stamp"], "hardware"),
        (["set hostname", "set admin-sport", "set admin-port", "set admintimeout", "set timezone",
          "set https-certificate", "set contract-update", "set threat-analytics", "set admin-tls",
          "set encrypt", "config system global", "config system settings"], "system_global"),
        (["set ip ", "set allowaccess", "set gateway", "set device port", "set status down",
          "set status up", "set description", "secondaryip", "classless_static_route",
          "config system interface", "edit \"port"], "network"),
        (["set passwd", "set password", "edit \"hadi\"", "edit \"rda\"", "edit \"msd\"",
          "edit \"cah\"", "edit \"DGMInfraIT\"", "edit \"deskciso\"", "edit \"delivery\"",
          "edit \"admin\"", "set access-profile", "passwd-set-time", "history-password",
          "config system admin", "set ftp-passwd", "set email ", "set type cloud"], "admin_users"),
        (["dashboard", "widget", "widget-table", "gui-dashboard", "fortiview", "sysres",
          "attacksummary", "policysummary", "sysop", "fortiguard", "x-pos", "height",
          "layout-type"], "dashboard"),
        (["waf", "csrf", "mitb", "cors", "cloaking", "sql", "xss", "http-header-security",
          "syntax-based", "parameter-validation", "hidden-fields", "http-protocol",
          "cookie-security", "websocket", "xml-validation", "x-forwarded-for",
          "set profile-id", "set http-content", "country-list", "signature_id",
          "match-target", "concatenate-type", "add-x-content", "x-xss", "x-frame",
          "sameorigin", "security-mode", "http-only", "samesite", "gitlab"], "waf_policy"),
        (["cookie-security", "security-mode", "http-only", "samesite", "set cookie"], "cookie"),
        (["certificate", "private-key", "intermediate-ca", "bankntbsyariah"], "certificates"),
        (["edit \"0", "edit \"1", "edit \"2", "edit \"3", "edit \"4", "edit \"5",
          "edit \"6", "edit \"7", "edit \"8", "edit \"9",
          "set type cloud", "threat-analytics"], "license"),
        (["Report_", "report", "on_demand", "custom_company", "custom_header",
          "custom_footer", "output_file", "filter_string"], "report"),
        (["server-pool-id", "server-id", "policy-id", "http-content-routing-id",
          "set profile-id"], "server_pool"),
    ]

    def classify(line: str) -> str:
        lower = line.lower()
        for keywords, cat in keyword_map:
            if any(kw.lower() in lower for kw in keywords):
                return cat
        return "other"

    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    opcodes = matcher.get_opcodes()

    raw_changes = []
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            continue
        old_chunk = old_lines[i1:i2]
        new_chunk = new_lines[j1:j2]
        all_lines = old_chunk + new_chunk
        # Classify by the most prominent keyword
        cat_votes = {}
        for line in all_lines:
            c = classify(line)
            cat_votes[c] = cat_votes.get(c, 0) + 1
        cat = max(cat_votes, key=cat_votes.get) if cat_votes else "other"

        raw_changes.append({
            "tag": tag,
            "old": old_chunk,
            "new": new_chunk,
            "category": cat,
        })

    for ch in raw_changes:
        categories[ch["category"]]["changes"].append(ch)

    return categories


def build_txt_report(header_old, header_new, categories, filename_old, filename_new) -> str:
    """Build a plain-text report string."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    sep = "=" * 80

    lines.append(sep)
    lines.append("  FORTIWEB CONFIG COMPARATOR — LAPORAN PERBEDAAN")
    lines.append(f"  File Lama : {filename_old}")
    lines.append(f"  File Baru : {filename_new}")
    lines.append(f"  Dibuat    : {now}")
    lines.append(sep)
    lines.append("")

    lines.append("INFORMASI PERANGKAT")
    lines.append("-" * 40)
    lines.append(f"  Model Lama  : {header_old.get('model', 'N/A')}")
    lines.append(f"  Model Baru  : {header_new.get('model', 'N/A')}")
    lines.append(f"  Firmware Lama  : {header_old.get('image_version', 'N/A')}")
    lines.append(f"  Firmware Baru  : {header_new.get('image_version', 'N/A')}")
    lines.append(f"  Waktu Backup Lama : {header_old.get('timestamp', 'N/A')}")
    lines.append(f"  Waktu Backup Baru : {header_new.get('timestamp', 'N/A')}")
    lines.append("")

    total_adds = total_dels = total_changes = 0

    for cat_key, cat in categories.items():
        changes = cat["changes"]
        if not changes:
            continue

        adds = sum(1 for c in changes if c["tag"] == "insert")
        dels = sum(1 for c in changes if c["tag"] == "delete")
        chgs = sum(1 for c in changes if c["tag"] == "replace")
        total_adds += adds
        total_dels += dels
        total_changes += chgs

        lines.append(sep)
        lines.append(f"  {cat['icon']}  {cat['label'].upper()}")
        lines.append(f"  Ditambah: {adds}  |  Dihapus: {dels}  |  Diubah: {chgs}")
        lines.append(sep)

        for ch in changes:
            if ch["tag"] == "replace":
                for l in ch["old"]:
                    lines.append(f"  - {l.strip()}")
                for l in ch["new"]:
                    lines.append(f"  + {l.strip()}")
            elif ch["tag"] == "delete":
                for l in ch["old"]:
                    lines.append(f"  - {l.strip()}")
            elif ch["tag"] == "insert":
                for l in ch["new"]:
                    lines.append(f"  + {l.strip()}")
            lines.append("")

    lines.append(sep)
    lines.append("  RINGKASAN")
    lines.append(sep)
    lines.append(f"  Total Ditambah : {total_adds} blok")
    lines.append(f"  Total Dihapus  : {total_dels} blok")
    lines.append(f"  Total Diubah   : {total_changes} blok")
    lines.append(sep)

    return "\n".join(lines)


def render_diff_block(changes: list[dict], max_lines_per_chunk: int = 30):
    """Render diff HTML for a list of change chunks."""
    html_parts = []
    for ch in changes:
        if ch["tag"] == "replace":
            for line in ch["old"][:max_lines_per_chunk]:
                html_parts.append(f'<div class="diff-removed">- {_esc(line)}</div>')
            if len(ch["old"]) > max_lines_per_chunk:
                html_parts.append(f'<div class="diff-hunk">  ... {len(ch["old"]) - max_lines_per_chunk} baris lagi (terpotong) ...</div>')
            for line in ch["new"][:max_lines_per_chunk]:
                html_parts.append(f'<div class="diff-added">+ {_esc(line)}</div>')
            if len(ch["new"]) > max_lines_per_chunk:
                html_parts.append(f'<div class="diff-hunk">  ... {len(ch["new"]) - max_lines_per_chunk} baris lagi (terpotong) ...</div>')
        elif ch["tag"] == "delete":
            for line in ch["old"][:max_lines_per_chunk]:
                html_parts.append(f'<div class="diff-removed">- {_esc(line)}</div>')
            if len(ch["old"]) > max_lines_per_chunk:
                html_parts.append(f'<div class="diff-hunk">  ... {len(ch["old"]) - max_lines_per_chunk} baris lagi (terpotong) ...</div>')
        elif ch["tag"] == "insert":
            for line in ch["new"][:max_lines_per_chunk]:
                html_parts.append(f'<div class="diff-added">+ {_esc(line)}</div>')
            if len(ch["new"]) > max_lines_per_chunk:
                html_parts.append(f'<div class="diff-hunk">  ... {len(ch["new"]) - max_lines_per_chunk} baris lagi (terpotong) ...</div>')
        html_parts.append('<div style="height:4px"></div>')

    return "".join(html_parts)


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def count_changes(categories):
    total = {"added": 0, "removed": 0, "changed": 0, "sections": 0}
    for cat in categories.values():
        if cat["changes"]:
            total["sections"] += 1
        for ch in cat["changes"]:
            if ch["tag"] == "insert":
                total["added"] += 1
            elif ch["tag"] == "delete":
                total["removed"] += 1
            elif ch["tag"] == "replace":
                total["changed"] += 1
    return total


# ─── Smart Summary ───────────────────────────────────────────────────────────

def get_smart_recommendations(categories, header_old, header_new) -> list[dict]:
    recs = []

    # Model change
    m_old = header_old.get("model", "")
    m_new = header_new.get("model", "")
    if m_old != m_new:
        recs.append({"icon": "🖥️", "text": f"Migrasi perangkat terdeteksi: {m_old} → {m_new}. Pastikan semua lisensi sudah dipindahkan."})

    # Cookie security
    cookie_changes = categories.get("cookie", {}).get("changes", []) + categories.get("waf_policy", {}).get("changes", [])
    all_cookie_text = " ".join(l for c in cookie_changes for l in c["old"] + c["new"])
    if "signed" in all_cookie_text and "encrypted" in all_cookie_text:
        recs.append({"icon": "🍪", "text": "Cookie security mode berubah antara 'signed' dan 'encrypted'. Verifikasi konfigurasi cookie di perangkat baru."})

    # WAF policy changes
    waf_changes = categories.get("waf_policy", {}).get("changes", [])
    if waf_changes:
        waf_keywords = {
            "csrf": "CSRF Protection",
            "mitb": "Man-in-the-Browser Protection",
            "cors": "CORS Protection",
            "sql": "SQL/XSS Detection",
            "cloaking": "Link Cloaking",
            "parameter-validation": "Parameter Validation",
            "hidden-fields": "Hidden Fields Protection",
        }
        all_waf = " ".join(l for c in waf_changes for l in c["old"] + c["new"]).lower()
        for kw, label in waf_keywords.items():
            if kw in all_waf:
                recs.append({"icon": "🛡️", "text": f"{label} terdeteksi berubah. Pastikan policy ini dikonfigurasi dengan benar di perangkat baru."})

    # Network changes
    net_changes = categories.get("network", {}).get("changes", [])
    if net_changes:
        all_net = " ".join(l for c in net_changes for l in c["old"] + c["new"])
        if "gateway" in all_net.lower():
            recs.append({"icon": "🌐", "text": "Default gateway berubah. Pastikan routing sudah benar di perangkat baru."})
        if "allowaccess" in all_net.lower():
            recs.append({"icon": "🔒", "text": "Allowaccess interface berubah. Review akses management (SSH, SNMP, HTTP/HTTPS)."})

    # Admin users
    admin_changes = categories.get("admin_users", {}).get("changes", [])
    all_admin = " ".join(l for c in admin_changes for l in c["old"] + c["new"])
    for chunk in admin_changes:
        for l in chunk["old"]:
            if 'edit "' in l and l not in [ll for c2 in admin_changes for ll in c2["new"]]:
                uname = re.findall(r'edit "([^"]+)"', l)
                if uname:
                    recs.append({"icon": "👤", "text": f"User admin '{uname[0]}' mungkin dihapus atau diubah. Verifikasi daftar admin."})
                break

    # Report
    if categories.get("report", {}).get("changes", []):
        recs.append({"icon": "📋", "text": "Konfigurasi Report berubah. Pastikan template laporan sudah di-migrate ke perangkat baru."})

    # Server pool IDs
    pool_changes = categories.get("server_pool", {}).get("changes", [])
    if len(pool_changes) > 5:
        recs.append({"icon": "🔗", "text": f"Terdeteksi {len(pool_changes)} perubahan Server Pool / Policy ID. Ini normal untuk migrasi perangkat — ID di-generate ulang otomatis."})

    if not recs:
        recs.append({"icon": "✅", "text": "Tidak ada rekomendasi khusus. Perubahan terlihat wajar."})

    return recs


# ─── Main App ────────────────────────────────────────────────────────────────

def main():
    # Hero header
    st.markdown("""
    <div class="hero">
        <div class="hero-title">🛡️ FortiWeb Config Comparator</div>
        <div class="hero-sub">Upload dua backup config FortiWeb (.conf) untuk membandingkan perbedaannya</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # File upload
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div style="color:#7d8590;font-size:0.8rem;font-family:JetBrains Mono;margin-bottom:6px;">● CONFIG LAMA</div>', unsafe_allow_html=True)
        file_old = st.file_uploader("Upload Config Lama", type=["conf", "txt", ""], key="old", label_visibility="collapsed")
    with col2:
        st.markdown('<div style="color:#00d4aa;font-size:0.8rem;font-family:JetBrains Mono;margin-bottom:6px;">● CONFIG BARU</div>', unsafe_allow_html=True)
        file_new = st.file_uploader("Upload Config Baru", type=["conf", "txt", ""], key="new", label_visibility="collapsed")

    if not file_old or not file_new:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;color:#7d8590;font-family:JetBrains Mono;font-size:0.85rem;">
            Upload kedua file config di atas untuk mulai membandingkan
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Process ──
    with st.spinner("Memproses dan membandingkan konfigurasi..."):
        bytes_old = file_old.read()
        bytes_new = file_new.read()

        lines_old = extract_text_lines(bytes_old)
        lines_new = extract_text_lines(bytes_new)

        header_old = parse_header(lines_old)
        header_new = parse_header(lines_new)

        categories = categorize_diff(lines_old, lines_new)
        stats = count_changes(categories)

    # ── Device Info Banner ──
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([5, 1, 5])
    with c1:
        st.markdown(f"""
        <div class="device-pill">
            <span class="dot dot-old"></span>
            <b>{header_old.get('model', 'Unknown')}</b> &nbsp;|&nbsp; {header_old.get('image_version', 'N/A')}
        </div>
        <div style="color:#7d8590;font-size:0.75rem;font-family:JetBrains Mono;margin-top:6px;padding-left:6px;">
            {file_old.name} &nbsp;|&nbsp; {header_old.get('timestamp', '')}
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="text-align:center;font-size:1.5rem;padding-top:8px;">→</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="device-pill">
            <span class="dot dot-new"></span>
            <b>{header_new.get('model', 'Unknown')}</b> &nbsp;|&nbsp; {header_new.get('image_version', 'N/A')}
        </div>
        <div style="color:#7d8590;font-size:0.75rem;font-family:JetBrains Mono;margin-top:6px;padding-left:6px;">
            {file_new.name} &nbsp;|&nbsp; {header_new.get('timestamp', '')}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Summary Metrics ──
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🟢 Ditambah", stats["added"], help="Blok konfigurasi yang ada di config BARU tapi tidak di config lama")
    with m2:
        st.metric("🔴 Dihapus", stats["removed"], help="Blok konfigurasi yang ada di config LAMA tapi tidak di config baru")
    with m3:
        st.metric("🟡 Diubah", stats["changed"], help="Blok konfigurasi yang berubah nilainya")
    with m4:
        st.metric("📂 Seksi Berubah", stats["sections"], help="Jumlah kategori konfigurasi yang memiliki perbedaan")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──
    tab_diff, tab_summary, tab_rec = st.tabs(["🔍 Detail Perbedaan", "📊 Ringkasan Per Kategori", "💡 Rekomendasi"])

    # ─── TAB 1: Detail Diff ───────────────────────────────────────────────
    with tab_diff:
        st.markdown("<br>", unsafe_allow_html=True)

        has_any = False
        for cat_key, cat in categories.items():
            if not cat["changes"]:
                continue
            has_any = True

            changes = cat["changes"]
            n_add = sum(1 for c in changes if c["tag"] == "insert")
            n_del = sum(1 for c in changes if c["tag"] == "delete")
            n_chg = sum(1 for c in changes if c["tag"] == "replace")

            badges = ""
            if n_add: badges += f'<span class="badge badge-added">+{n_add} ditambah</span>'
            if n_del: badges += f'<span class="badge badge-removed">-{n_del} dihapus</span>'
            if n_chg: badges += f'<span class="badge badge-changed">~{n_chg} diubah</span>'

            label = f"{cat['icon']} {cat['label']}  ({len(changes)} perubahan)"

            # Skip server_pool by default (too many ID changes, not meaningful)
            default_open = cat_key != "server_pool"

            with st.expander(label, expanded=default_open):
                st.markdown(badges, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                diff_html = render_diff_block(changes)
                st.markdown(
                    f'<div style="background:#161b22;border-radius:8px;padding:8px;overflow-x:auto;">{diff_html}</div>',
                    unsafe_allow_html=True
                )

        if not has_any:
            st.success("✅ Tidak ada perbedaan yang ditemukan. Kedua config identik (pada bagian yang bisa dibaca).")

    # ─── TAB 2: Ringkasan Per Kategori ───────────────────────────────────
    with tab_summary:
        st.markdown("<br>", unsafe_allow_html=True)

        rows = []
        for cat in categories.values():
            changes = cat["changes"]
            if not changes:
                continue
            n_add = sum(1 for c in changes if c["tag"] == "insert")
            n_del = sum(1 for c in changes if c["tag"] == "delete")
            n_chg = sum(1 for c in changes if c["tag"] == "replace")
            rows.append({
                "Kategori": f"{cat['icon']} {cat['label']}",
                "Ditambah ✅": n_add,
                "Dihapus ❌": n_del,
                "Diubah 🔄": n_chg,
                "Total": n_add + n_del + n_chg,
            })

        if rows:
            import pandas as pd
            df = pd.DataFrame(rows).sort_values("Total", ascending=False)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Ditambah ✅": st.column_config.NumberColumn(format="%d"),
                    "Dihapus ❌": st.column_config.NumberColumn(format="%d"),
                    "Diubah 🔄": st.column_config.NumberColumn(format="%d"),
                    "Total": st.column_config.ProgressColumn(min_value=0, max_value=max(r["Total"] for r in rows)),
                }
            )

            # Highlight notable sections
            st.markdown("#### Catatan Penting")
            notable = {
                "network": "⚠️ Konfigurasi jaringan/IP berubah — pastikan konektivitas tidak terganggu.",
                "admin_users": "⚠️ Ada perubahan pada akun admin — verifikasi siapa yang ditambah/dihapus.",
                "waf_policy": "⚠️ Policy WAF berubah — review apakah semua proteksi sudah ter-migrate.",
                "cookie": "⚠️ Cookie security berubah — potensi dampak ke keamanan session.",
                "certificates": "ℹ️ Sertifikat SSL berbeda — pastikan sertifikat baru masih valid.",
                "license": "ℹ️ Lisensi berbeda — normal jika beda perangkat.",
                "server_pool": "ℹ️ Server Pool/Policy ID berbeda — normal, ID di-generate otomatis per perangkat.",
            }
            for cat_key, note in notable.items():
                if categories.get(cat_key, {}).get("changes"):
                    st.markdown(f"- {note}")

    # ─── TAB 3: Rekomendasi ───────────────────────────────────────────────
    with tab_rec:
        st.markdown("<br>", unsafe_allow_html=True)
        recs = get_smart_recommendations(categories, header_old, header_new)
        st.markdown("#### Hal-hal yang Perlu Diperhatikan")
        for r in recs:
            st.markdown(f"""
            <div class="rec-item">
                <span class="rec-icon">{r['icon']}</span>
                <span>{r['text']}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Download Report ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    col_dl, _ = st.columns([2, 5])
    with col_dl:
        report_txt = build_txt_report(header_old, header_new, categories, file_old.name, file_new.name)
        st.download_button(
            label="⬇️ Download Laporan (.txt)",
            data=report_txt.encode("utf-8"),
            file_name=f"fortiweb_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
        )

    st.markdown("""
    <div style="text-align:center;color:#7d8590;font-size:0.75rem;font-family:JetBrains Mono;padding:20px 0 10px;">
        FortiWeb Config Comparator — sertifikat & private key tidak ditampilkan demi keamanan
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
