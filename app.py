import streamlit as st
import pydicom
import pandas as pd
import io
import base64
import warnings
from pathlib import Path
from copy import deepcopy

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="DICOM Tag Validator | SwiftMR",
    page_icon="🏥",
    layout="wide"
)

# ── Logo ─────────────────────────────────────────────
def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

logo_b64 = get_image_base64("SwiftMR Logo.png")
logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}" style="width:44px;height:44px;object-fit:contain;">'
    if logo_b64 else "🏥"
)
sidebar_logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}" style="width:48px;height:48px;object-fit:contain;">'
    if logo_b64 else "🏥"
)

# ── Custom CSS ───────────────────────────────────────
st.markdown("""
<style>
@media (prefers-color-scheme: dark) {
    .stApp { background-color: #0f1117 !important; }
    .airs-header {
        background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%) !important;
        border-bottom: 2px solid #00d4ff !important;
    }
    .airs-title p { color: #8892a4 !important; }
    .airs-badge {
        background: rgba(0,212,255,0.1) !important;
        border: 1px solid rgba(0,212,255,0.3) !important;
        color: #00d4ff !important;
    }
    .summary-card {
        background: linear-gradient(135deg, #1a1f2e, #141820) !important;
        border: 1px solid #2a3040 !important;
    }
    .section-card {
        background: linear-gradient(135deg, #1a1f2e, #141820) !important;
        border: 1px solid #2a3040 !important;
    }
    .metric-card {
        background: #1a1f2e !important;
        border: 1px solid #2a3040 !important;
    }
    .metric-value { color: #e8eaf0 !important; }
    .metric-label { color: #8892a4 !important; }
    .tag-table-header {
        background: #1e2535 !important;
        color: #8892a4 !important;
    }
    .tag-row-present { background: rgba(0,200,100,0.05) !important; }
    .tag-row-missing-req { background: rgba(255,60,60,0.08) !important; }
    .tag-row-missing-opt { background: rgba(255,180,0,0.05) !important; }
    .tag-name-text { color: #c8d0dc !important; }
    .tag-code-text {
        color: #00d4ff !important;
        background: rgba(0,212,255,0.08) !important;
    }
    .tag-vr-text {
        color: #8892a4 !important;
        background: #1e2535 !important;
    }
    .tag-value-text { color: #a0aab8 !important; }
    .sidebar-section-title {
        color: #00d4ff !important;
        border-bottom: 1px solid #2a3040 !important;
    }
    .manufacturer-badge {
        background: rgba(0,212,255,0.1) !important;
        border: 1px solid rgba(0,212,255,0.3) !important;
        color: #00d4ff !important;
    }
}

@media (prefers-color-scheme: light) {
    .stApp { background-color: #f0f4f8 !important; }
    .airs-header {
        background: linear-gradient(135deg, #ffffff 0%, #e8f0fe 100%) !important;
        border-bottom: 2px solid #0066ff !important;
    }
    .airs-title p { color: #5a6a7a !important; }
    .airs-badge {
        background: rgba(0,102,255,0.1) !important;
        border: 1px solid rgba(0,102,255,0.3) !important;
        color: #0066ff !important;
    }
    .summary-card {
        background: linear-gradient(135deg, #ffffff, #f5f8ff) !important;
        border: 1px solid #d0d8e8 !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08) !important;
    }
    .section-card {
        background: linear-gradient(135deg, #ffffff, #f5f8ff) !important;
        border: 1px solid #d0d8e8 !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    }
    .metric-card {
        background: #ffffff !important;
        border: 1px solid #d0d8e8 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }
    .metric-value { color: #1a2030 !important; }
    .metric-label { color: #5a6a7a !important; }
    .tag-table-header {
        background: #e8eef8 !important;
        color: #5a6a7a !important;
    }
    .tag-row-present { background: rgba(0,180,80,0.04) !important; }
    .tag-row-missing-req { background: rgba(255,60,60,0.06) !important; }
    .tag-row-missing-opt { background: rgba(255,180,0,0.04) !important; }
    .tag-name-text { color: #2a3a4a !important; }
    .tag-code-text {
        color: #0055cc !important;
        background: rgba(0,102,255,0.08) !important;
    }
    .tag-vr-text {
        color: #5a6a7a !important;
        background: #e8eef8 !important;
    }
    .tag-value-text { color: #4a5a6a !important; }
    .sidebar-section-title {
        color: #0066ff !important;
        border-bottom: 1px solid #d0d8e8 !important;
    }
    .manufacturer-badge {
        background: rgba(0,102,255,0.1) !important;
        border: 1px solid rgba(0,102,255,0.3) !important;
        color: #0066ff !important;
    }
}

.airs-header {
    display: flex; align-items: center; gap: 16px;
    padding: 20px 28px;
    margin-bottom: 32px;
    border-radius: 0 0 16px 16px;
}
.airs-logo-box {
    width: 52px; height: 52px;
    background: transparent;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.airs-title h1 {
    margin: 0; font-size: 22px; font-weight: 800;
    background: linear-gradient(90deg, #00d4ff, #0066ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
}
.airs-title p { margin: 2px 0 0; font-size: 13px; letter-spacing: 1px; }
.airs-badge {
    margin-left: auto;
    padding: 6px 14px;
    border-radius: 20px; font-size: 12px;
    font-weight: 600; letter-spacing: 1px;
}
.summary-card {
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
}
.section-card {
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.section-title {
    font-size: 16px; font-weight: 700;
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 16px;
}
.metric-card {
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
}
.metric-value {
    font-size: 32px; font-weight: 800;
    line-height: 1.1;
}
.metric-label {
    font-size: 12px; font-weight: 600;
    letter-spacing: 1px; text-transform: uppercase;
    margin-top: 4px;
}
.overall-pass {
    background: linear-gradient(135deg, rgba(0,200,100,0.15), rgba(0,150,80,0.1)) !important;
    border: 2px solid rgba(0,200,100,0.4) !important;
}
.overall-fail {
    background: linear-gradient(135deg, rgba(255,60,60,0.15), rgba(200,0,0,0.1)) !important;
    border: 2px solid rgba(255,60,60,0.4) !important;
}
.overall-warning {
    background: linear-gradient(135deg, rgba(255,180,0,0.15), rgba(200,140,0,0.1)) !important;
    border: 2px solid rgba(255,180,0,0.4) !important;
}
.overall-title {
    font-size: 28px; font-weight: 900;
    letter-spacing: 2px; margin-bottom: 4px;
}
.overall-sub { font-size: 14px; opacity: 0.8; }
.tag-table-header {
    display: grid;
    grid-template-columns: 2fr 1.2fr 0.6fr 0.8fr 2fr 1fr;
    padding: 8px 12px;
    border-radius: 8px 8px 0 0;
    font-size: 11px; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 2px;
}
.tag-row {
    display: grid;
    grid-template-columns: 2fr 1.2fr 0.6fr 0.8fr 2fr 1fr;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 2px;
    align-items: center;
}
.tag-name-text { font-size: 13px; font-weight: 500; }
.tag-code-text {
    font-family: monospace; font-size: 11px;
    padding: 2px 6px; border-radius: 4px;
    display: inline-block;
}
.tag-vr-text {
    font-size: 11px; padding: 2px 6px;
    border-radius: 4px; font-family: monospace;
    display: inline-block;
}
.tag-value-text { font-size: 12px; }
.status-badge {
    display: inline-flex; align-items: center;
    gap: 4px; padding: 3px 10px;
    border-radius: 20px; font-size: 11px; font-weight: 700;
}
.status-present {
    background: rgba(0,200,100,0.15);
    color: #00c864; border: 1px solid rgba(0,200,100,0.3);
}
.status-missing-req {
    background: rgba(255,60,60,0.15);
    color: #ff4444; border: 1px solid rgba(255,60,60,0.3);
}
.status-missing-opt {
    background: rgba(255,180,0,0.15);
    color: #ffb400; border: 1px solid rgba(255,180,0,0.3);
}
.manufacturer-badge {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 16px; border-radius: 20px;
    font-size: 13px; font-weight: 700;
    margin: 4px;
}
.sidebar-section-title {
    font-size: 12px; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 10px; padding-bottom: 6px;
}
.phi-warning {
    background: linear-gradient(135deg, rgba(255,80,80,0.12), rgba(200,0,0,0.08));
    border: 1.5px solid rgba(255,80,80,0.5);
    border-left: 4px solid #ff4444;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────
st.markdown(f"""
<div class="airs-header">
    <div class="airs-logo-box">{logo_html}</div>
    <div class="airs-title">
        <h1>SwiftMR</h1>
        <p>DICOM Tag Validator &nbsp;·&nbsp; Internal Tool</p>
    </div>
    <div class="airs-badge">v1.0</div>
</div>
""", unsafe_allow_html=True)

# ── Tag Definitions ──────────────────────────────────

REQUIRED_TAGS = [
    {"name": "Instance Number",           "tag": "(0020,0013)", "vr": "IS",  "purpose": ""},
    {"name": "Series Number",             "tag": "(0020,0011)", "vr": "IS",  "purpose": "Derived"},
    {"name": "Image Type",                "tag": "(0008,0008)", "vr": "CS",  "purpose": "3D"},
    {"name": "Series Description",        "tag": "(0008,103E)", "vr": "LO",  "purpose": "SWI"},
    {"name": "Pixel Data",                "tag": "(7FE0,0010)", "vr": "OB",  "purpose": ""},
    {"name": "Pixel Representation",      "tag": "(0028,0103)", "vr": "US",  "purpose": ""},
    {"name": "Bits Stored",               "tag": "(0028,0101)", "vr": "US",  "purpose": ""},
    {"name": "Rows",                      "tag": "(0028,0010)", "vr": "US",  "purpose": ""},
    {"name": "Columns",                   "tag": "(0028,0011)", "vr": "US",  "purpose": ""},
    {"name": "Pixel Spacing",             "tag": "(0028,0030)", "vr": "DS",  "purpose": ""},
    {"name": "Window Center",             "tag": "(0028,1050)", "vr": "DS",  "purpose": "MIP"},
    {"name": "Window Width",              "tag": "(0028,1051)", "vr": "DS",  "purpose": "MIP"},
    {"name": "Image Orientation Patient", "tag": "(0020,0037)", "vr": "DS",  "purpose": "post"},
    {"name": "Image Position Patient",    "tag": "(0020,0032)", "vr": "DS",  "purpose": ""},
    {"name": "Spacing Between Slices",    "tag": "(0018,0088)", "vr": "DS",  "purpose": "post"},
    {"name": "Slice Thickness",           "tag": "(0018,0050)", "vr": "DS",  "purpose": "post"},
    {"name": "Image Position Patient",    "tag": "(0020,0032)", "vr": "DS",  "purpose": ""},
]

OPTIONAL_TAGS = [
    {"name": "Overlay Bits Allocated",              "tag": "(6000,0100)", "vr": "US",  "purpose": ""},
    {"name": "Overlay Bit Position",                "tag": "(6000,0102)", "vr": "US",  "purpose": ""},
    {"name": "Overlay Data",                        "tag": "(6000,3000)", "vr": "OB",  "purpose": ""},
    {"name": "Overlay Rows",                        "tag": "(6000,0010)", "vr": "US",  "purpose": ""},
    {"name": "Overlay Columns",                     "tag": "(6000,0011)", "vr": "US",  "purpose": ""},
    {"name": "Diffusion b-value",                   "tag": "(0018,9087)", "vr": "FD",  "purpose": ""},
    {"name": "Slice Location",                      "tag": "(0020,1041)", "vr": "DS",  "purpose": "Slice Interpol"},
    {"name": "Manufacturer",                        "tag": "(0008,0070)", "vr": "LO",  "purpose": ""},
    {"name": "Number of Averages",                  "tag": "(0018,0083)", "vr": "DS",  "purpose": ""},
    {"name": "Percent Sampling",                    "tag": "(0018,0093)", "vr": "DS",  "purpose": ""},
    {"name": "Acquisition Matrix",                  "tag": "(0018,1310)", "vr": "US",  "purpose": ""},
    {"name": "Derivation Description",              "tag": "(0008,2111)", "vr": "ST",  "purpose": ""},
    {"name": "In-Plane Phase Encoding Direction",   "tag": "(0018,1312)", "vr": "CS",  "purpose": ""},
    {"name": "Percent Phase Field of View",         "tag": "(0018,0094)", "vr": "DS",  "purpose": ""},
    {"name": "Request Attributes Sequence",         "tag": "(0040,0275)", "vr": "SQ",  "purpose": "Fonar"},
    {"name": "Per-frame Functional Groups Sequence","tag": "(5200,9230)", "vr": "SQ",  "purpose": "Fonar"},
    {"name": "Derivation Code Sequence",            "tag": "(0008,9215)", "vr": "SQ",  "purpose": "GE Subtraction"},
    {"name": "Field of View Dimensions",            "tag": "(0018,1149)", "vr": "IS",  "purpose": "Paramed"},
]

MANUFACTURER_TAGS = {
    "Philips": [
        {"name": "Volume Based Calculation Technique", "tag": "(2005,140F)", "vr": "CS"},
        {"name": "Image Plane Number",                 "tag": "(2001,100A)", "vr": "IS"},
        {"name": "MRSeriesNrOfSlices",                 "tag": "(2001,1018)", "vr": "SL"},
        {"name": "Stack",                              "tag": "(2001,105F)", "vr": "SQ"},
        {"name": "MRImageOffCentreAP",                 "tag": "(2005,1008)", "vr": "FL"},
        {"name": "MRImageOffCentreFH",                 "tag": "(2005,1009)", "vr": "FL"},
        {"name": "MRImageOffCentreRL",                 "tag": "(2005,100A)", "vr": "FL"},
        {"name": "SeriesDerivationDescription",        "tag": "(2001,10CC)", "vr": "ST"},
        {"name": "Philips Private Creator",            "tag": "(2005,0014)", "vr": "LO"},
        {"name": "Parallel Reduction Factor In-Plane", "tag": "(2005,140F)", "vr": "FD"},
        {"name": "MR Acquisition Phase Encoding Steps","tag": "(2005,140F)", "vr": "US"},
    ],
    "Siemens": [
        {"name": "Siemens Private Creator",  "tag": "(0051,0010)", "vr": "LO"},
        {"name": "Siemens Private Creator",  "tag": "(0021,0010)", "vr": "LO"},
        {"name": "Siemens Private Creator",  "tag": "(0019,0010)", "vr": "LO"},
        {"name": "pat factor",               "tag": "(0051,1011)", "vr": "LO"},
        {"name": "pat factor",               "tag": "(0021,1009)", "vr": "LO"},
        {"name": "acquisition matrix",       "tag": "(0051,100B)", "vr": "LO"},
        {"name": "CSA HEADER1",              "tag": "(0029,1020)", "vr": "LO"},
        {"name": "CSA HEADER2",              "tag": "(0021,1019)", "vr": "LO"},
        {"name": "psd name1",                "tag": "(0019,109C)", "vr": "LO"},
        {"name": "psd name2",                "tag": "(0019,109E)", "vr": "LO"},
        {"name": "pseq id1",                 "tag": "(0019,1012)", "vr": "SS"},
        {"name": "pseq id2",                 "tag": "(0025,1006)", "vr": "SS"},
        {"name": "pseq id3",                 "tag": "(0027,1032)", "vr": "SS"},
        {"name": "diffusion b-value",        "tag": "(0019,100C)", "vr": "IS"},
        {"name": "SQ Per-frame Functional",  "tag": "(5200,9230)", "vr": "FD"},
    ],
    "GE": [
        {"name": "GE Private Creator",       "tag": "(0043,0010)", "vr": "LO"},
        {"name": "GE Private Creator",       "tag": "(0027,0010)", "vr": "LO"},
        {"name": "pat type",                 "tag": "(0043,1084)", "vr": "LO"},
        {"name": "pat factor",               "tag": "(0043,1083)", "vr": "DS"},
        {"name": "Image Type (real/imag)",   "tag": "(0043,102F)", "vr": "SS"},
        {"name": "Vas collapse flag",        "tag": "(0043,1030)", "vr": "SS"},
        {"name": "Functional Protocol",      "tag": "(0051,1006)", "vr": "LT"},
        {"name": "PDB Header",               "tag": "(0025,101B)", "vr": "OB"},
        {"name": "Derivation Code Sequence", "tag": "(0008,9215)", "vr": "SQ"},
        {"name": "number of freq enc steps", "tag": "(0027,1060)", "vr": "FL"},
        {"name": "number of phase enc steps","tag": "(0027,1061)", "vr": "FL"},
    ],
    "Canon (Toshiba)": [
        {"name": "TOSHIBA_MEC",  "tag": "(0029,1001)", "vr": "SQ"},
        {"name": "TOSHIBA_MEC",  "tag": "(0029,1002)", "vr": "SQ"},
        {"name": "TOSHIBA_MEC",  "tag": "(700D,0010)", "vr": "LO"},
        {"name": "TOSHIBA_MEC",  "tag": "(700D,1011)", "vr": "US"},
        {"name": "TOSHIBA_MEC",  "tag": "(700D,1014)", "vr": "SL"},
        {"name": "TOSHIBA_MEC",  "tag": "(700D,1016)", "vr": "LO"},
        {"name": "TOSHIBA_MEC",  "tag": "(700D,1018)", "vr": "SS"},
        {"name": "TOSHIBA_MEC",  "tag": "(700D,1019)", "vr": "OB"},
    ],
    "Esaote": [
        {"name": "V1", "tag": "(0011,1001)", "vr": "OB"},
        {"name": "V1", "tag": "(0011,1002)", "vr": "DS"},
        {"name": "V1", "tag": "(0011,1003)", "vr": "DS"},
        {"name": "V1", "tag": "(0011,1004)", "vr": "DS"},
        {"name": "V1", "tag": "(0011,1008)", "vr": "DS"},
    ],
    "Fonar": [
        {"name": "MMCPrivate", "tag": "(0029,102F)", "vr": ""},
        {"name": "MMCPrivate", "tag": "(0029,1032)", "vr": ""},
        {"name": "MMCPrivate", "tag": "(0029,10D7)", "vr": ""},
        {"name": "Request Attributes Sequence",          "tag": "(0040,0275)", "vr": "SQ"},
        {"name": "Per-frame Functional Groups Sequence", "tag": "(5200,9230)", "vr": "SQ"},
    ],
    "Hyperfine": [
        {"name": "Hyperfine Private Creator", "tag": "(351B,0010)", "vr": "LO"},
        {"name": "Hyperfine Private Creator", "tag": "(351B,1001)", "vr": ""},
        {"name": "Hyperfine Private Creator", "tag": "(351B,1002)", "vr": ""},
        {"name": "Hyperfine Private Creator", "tag": "(351B,1003)", "vr": ""},
        {"name": "Hyperfine Private Creator", "tag": "(351B,1004)", "vr": ""},
        {"name": "Hyperfine Private Creator", "tag": "(351B,1005)", "vr": ""},
        {"name": "Hyperfine Private Creator", "tag": "(351B,1006)", "vr": ""},
    ],
    "Paramed": [
        {"name": "Field of View Dimensions", "tag": "(0018,1149)", "vr": "IS"},
        {"name": "acquisition voxel size",   "tag": "(0011,1017)", "vr": "LO"},
    ],
}

MANUFACTURER_KEYWORDS = {
    "Philips":        ["philips"],
    "Siemens":        ["siemens"],
    "GE":             ["ge medical", "ge healthcare", "general electric"],
    "Canon (Toshiba)":["canon", "toshiba"],
    "Esaote":         ["esaote"],
    "Fonar":          ["fonar"],
    "Hyperfine":      ["hyperfine"],
    "Paramed":        ["paramed"],
}

# ── Utility Functions ────────────────────────────────
def parse_tag_str(tag_str):
    """(GGGG,EEEE) → pydicom Tag"""
    tag_str = tag_str.strip("()")
    group, element = tag_str.split(",")
    return pydicom.tag.Tag(int(group, 16), int(element, 16))


def get_tag_value(ds, tag_str):
    """태그 값 반환, 없으면 None"""
    try:
        tag = parse_tag_str(tag_str)
        if tag in ds:
            elem = ds[tag]
            if isinstance(elem.value, bytes):
                return f"[Binary {len(elem.value)} bytes]"
            elif elem.VR == "SQ":
                return f"[Sequence {len(elem.value)} item(s)]"
            else:
                val = str(elem.value)
                return val[:80] + "..." if len(val) > 80 else val
        return None
    except Exception:
        return None


def detect_manufacturer(ds):
    """제조사 자동 감지"""
    try:
        tag = pydicom.tag.Tag(0x0008, 0x0070)
        if tag in ds:
            mfr = str(ds[tag].value).lower()
            for name, keywords in MANUFACTURER_KEYWORDS.items():
                if any(k in mfr for k in keywords):
                    return name, str(ds[tag].value)
    except Exception:
        pass
    return None, "Unknown"


def validate_tags(ds, tag_list, required=True):
    """태그 검증 후 결과 반환"""
    results = []
    for t in tag_list:
        value = get_tag_value(ds, t["tag"])
        present = value is not None
        results.append({
            "name":     t["name"],
            "tag":      t["tag"],
            "vr":       t.get("vr", ""),
            "purpose":  t.get("purpose", ""),
            "present":  present,
            "value":    value if present else "MISSING",
            "required": required,
        })
    return results


def render_tag_table(results):
    """태그 테이블 HTML 렌더링"""
    html = """
    <div class="tag-table-header">
        <span>Name</span>
        <span>Tag</span>
        <span>VR</span>
        <span>Purpose</span>
        <span>Value</span>
        <span>Status</span>
    </div>
    """
    for r in results:
        if r["present"]:
            row_cls    = "tag-row tag-row-present"
            status_cls = "status-badge status-present"
            status_txt = "✅ Present"
        elif r["required"]:
            row_cls    = "tag-row tag-row-missing-req"
            status_cls = "status-badge status-missing-req"
            status_txt = "❌ Missing"
        else:
            row_cls    = "tag-row tag-row-missing-opt"
            status_cls = "status-badge status-missing-opt"
            status_txt = "⚠️ Missing"

        html += f"""
        <div class="{row_cls}">
            <span class="tag-name-text">{r['name']}</span>
            <span class="tag-code-text">{r['tag']}</span>
            <span class="tag-vr-text">{r['vr']}</span>
            <span class="tag-value-text" style="font-size:11px;opacity:0.7;">{r['purpose']}</span>
            <span class="tag-value-text">{r['value']}</span>
            <span class="{status_cls}">{status_txt}</span>
        </div>
        """
    return html


def build_export_df(req_results, opt_results, mfr_results, mfr_name):
    """CSV 내보내기용 DataFrame"""
    rows = []
    for r in req_results:
        rows.append({
            "Category": "Required",
            "Name": r["name"],
            "Tag": r["tag"],
            "VR": r["vr"],
            "Purpose": r["purpose"],
            "Status": "Present" if r["present"] else "MISSING",
            "Value": r["value"],
        })
    for r in opt_results:
        rows.append({
            "Category": "Optional",
            "Name": r["name"],
            "Tag": r["tag"],
            "VR": r["vr"],
            "Purpose": r["purpose"],
            "Status": "Present" if r["present"] else "Missing",
            "Value": r["value"],
        })
    for r in mfr_results:
        rows.append({
            "Category": f"Manufacturer ({mfr_name})",
            "Name": r["name"],
            "Tag": r["tag"],
            "VR": r["vr"],
            "Purpose": r.get("purpose", ""),
            "Status": "Present" if r["present"] else "Missing",
            "Value": r["value"],
        })
    return pd.DataFrame(rows)


# ════════════════════════════════════════════════════
# PHI WARNING
# ════════════════════════════════════════════════════
st.markdown("""
<div class="phi-warning">
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
        <span style="font-size:20px;">🔒</span>
        <span style="font-size:15px; font-weight:800; color:#ff4444; letter-spacing:1px;">
            HIPAA & GDPR WARNING
        </span>
    </div>
    <div style="font-size:13px; line-height:1.8;">
        ⚠️ This tool runs on <b>Streamlit Cloud (external server)</b>.<br>
        ⚠️ <b>DO NOT upload files containing PHI (Protected Health Information)</b>.<br>
        ⚠️ Uploading real patient data may violate <b>HIPAA</b> and <b>GDPR</b> regulations.<br>
        ✅ Only use <b>fully anonymized or de-identified DICOM files</b>.
    </div>
</div>
""", unsafe_allow_html=True)

phi_confirmed = st.checkbox(
    "✅ I confirm that this file does NOT contain any PHI (Protected Health Information) "
    "and is fully anonymized.",
    key="phi_confirm"
)
if not phi_confirmed:
    st.warning("⛔ Please confirm the above statement before uploading any files.")
    st.stop()


# ════════════════════════════════════════════════════
# UPLOAD
# ════════════════════════════════════════════════════
st.markdown("""
<div class="section-card">
  <div class="section-title">
    <div style="width:32px;height:32px;background:linear-gradient(135deg,#00d4ff,#0066ff);
        border-radius:50%;display:flex;align-items:center;justify-content:center;
        font-weight:800;color:white;font-size:15px;flex-shrink:0;">1</div>
    Upload DICOM File
  </div>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload a DICOM file for tag validation",
    type=["dcm", "DCM"],
    help="Upload a single DICOM file to validate required tags for SwiftMR processing"
)

if uploaded:
    file_bytes = uploaded.read()
    try:
        ds = pydicom.dcmread(io.BytesIO(file_bytes), force=True)
        st.success(f"✅ Loaded: **{uploaded.name}** — {len(ds)} tags found")
    except Exception as e:
        st.error(f"❌ Failed to read DICOM file: {e}")
        st.stop()

    # ── 제조사 감지 ──────────────────────────────────
    mfr_name, mfr_raw = detect_manufacturer(ds)

    # ── 태그 검증 ────────────────────────────────────
    req_results = validate_tags(ds, REQUIRED_TAGS, required=True)
    opt_results = validate_tags(ds, OPTIONAL_TAGS, required=False)
    mfr_results = []
    if mfr_name and mfr_name in MANUFACTURER_TAGS:
        mfr_results = validate_tags(ds, MANUFACTURER_TAGS[mfr_name], required=False)

    # ── 통계 계산 ────────────────────────────────────
    req_total   = len(req_results)
    req_present = sum(1 for r in req_results if r["present"])
    req_missing = req_total - req_present

    opt_total   = len(opt_results)
    opt_present = sum(1 for r in opt_results if r["present"])

    mfr_total   = len(mfr_results)
    mfr_present = sum(1 for r in mfr_results if r["present"])

    # ── Overall Result ───────────────────────────────
    if req_missing == 0:
        overall_cls   = "overall-pass"
        overall_icon  = "✅"
        overall_title = "PASS"
        overall_sub   = "All required tags are present. SwiftMR processing is possible."
    else:
        overall_cls   = "overall-fail"
        overall_icon  = "❌"
        overall_title = "FAIL"
        overall_sub   = (
            f"{req_missing} required tag(s) are missing. "
            "SwiftMR processing cannot proceed."
        )

    # ════════════════════════════════════════════════
    # OVERALL SUMMARY
    # ════════════════════════════════════════════════
    st.markdown(f"""
    <div class="summary-card {overall_cls}">
        <div class="overall-title">{overall_icon} {overall_title}</div>
        <div class="overall-sub">{overall_sub}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics ──────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (c1, str(req_present),  "Required Present",  "#00c864"),
        (c2, str(req_missing),  "Required Missing",  "#ff4444"),
        (c3, str(opt_present),  "Optional Present",  "#00d4ff"),
        (c4, str(opt_total - opt_present), "Optional Missing", "#ffb400"),
        (c5, mfr_raw if mfr_raw != "Unknown" else "—",
             "Manufacturer", "#a78bfa"),
    ]
    for col, val, label, color in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color};">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Manufacturer Badge ───────────────────────────
    if mfr_name:
        st.markdown(f"""
        <div style="margin-bottom:16px;">
            <span class="manufacturer-badge">
                🏭 Detected Manufacturer: <b>{mfr_name}</b>
                &nbsp;·&nbsp; Raw Value: <i>{mfr_raw}</i>
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="margin-bottom:16px;">
            <span class="manufacturer-badge">
                🏭 Manufacturer: <b>Unknown</b>
                &nbsp;·&nbsp; Private tags not validated
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # SECTION 1: Required Tags
    # ════════════════════════════════════════════════
    req_color = "#ff4444" if req_missing > 0 else "#00c864"
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title">
            🔴 Required Tags
            <span style="font-size:13px;font-weight:600;color:{req_color};margin-left:8px;">
                {req_present}/{req_total} Present
            </span>
        </div>
        {render_tag_table(req_results)}
    </div>
    """, unsafe_allow_html=True)

    # ── Missing Required Tags 강조 ───────────────────
    missing_req = [r for r in req_results if not r["present"]]
    if missing_req:
        st.markdown("""
        <div style="
            background: rgba(255,60,60,0.1);
            border: 1.5px solid rgba(255,60,60,0.4);
            border-left: 4px solid #ff4444;
            border-radius: 12px;
            padding: 14px 20px;
            margin: 8px 0 16px;
        ">
            <div style="font-weight:800;color:#ff4444;margin-bottom:8px;font-size:14px;">
                ❌ Missing Required Tags — SwiftMR Cannot Process This File
            </div>
        """ + "".join([
            f'<div style="font-size:13px;margin:4px 0;">• <b>{r["name"]}</b> '
            f'<span style="font-family:monospace;font-size:11px;opacity:0.7;">{r["tag"]}</span></div>'
            for r in missing_req
        ]) + "</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # SECTION 2: Optional Tags
    # ════════════════════════════════════════════════
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title">
            🟡 Optional Tags
            <span style="font-size:13px;font-weight:600;color:#ffb400;margin-left:8px;">
                {opt_present}/{opt_total} Present
            </span>
        </div>
        {render_tag_table(opt_results)}
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # SECTION 3: Manufacturer Private Tags
    # ════════════════════════════════════════════════
    if mfr_name and mfr_results:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">
                🏭 {mfr_name} Private Tags
                <span style="font-size:13px;font-weight:600;color:#00d4ff;margin-left:8px;">
                    {mfr_present}/{mfr_total} Present
                </span>
            </div>
            {render_tag_table(mfr_results)}
        </div>
        """, unsafe_allow_html=True)
    elif not mfr_name:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">🏭 Manufacturer Private Tags</div>
            <div style="font-size:13px;opacity:0.6;padding:8px 0;">
                ℹ️ Manufacturer could not be detected.
                Private tag validation is skipped.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # EXPORT
    # ════════════════════════════════════════════════
    st.markdown("""
    <div class="section-card">
        <div class="section-title">📥 Export Report</div>
    </div>
    """, unsafe_allow_html=True)

    export_df = build_export_df(req_results, opt_results, mfr_results, mfr_name or "Unknown")

    col1, col2 = st.columns(2)
    with col1:
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download CSV Report",
            data=csv_data,
            file_name=f"dicom_tag_report_{uploaded.name.replace('.dcm','')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Tag Report")

            ws = writer.sheets["Tag Report"]
            from openpyxl.styles import PatternFill, Font
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                status = row[5].value
                if status == "MISSING":
                    for cell in row:
                        cell.fill = PatternFill("solid", fgColor="FFCCCC")
                elif status == "Missing":
                    for cell in row:
                        cell.fill = PatternFill("solid", fgColor="FFF3CC")
                elif status == "Present":
                    for cell in row:
                        cell.fill = PatternFill("solid", fgColor="CCFFDD")

        st.download_button(
            label="⬇️ Download Excel Report",
            data=excel_buf.getvalue(),
            file_name=f"dicom_tag_report_{uploaded.name.replace('.dcm','')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # ── Raw DataFrame Preview ────────────────────────
    with st.expander("📊 Preview Full Report Table", expanded=False):
        st.dataframe(export_df, use_container_width=True, hide_index=True, height=400)


# ── Sidebar ──────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:16px 0 20px;">
        <div style="width:56px;height:56px;margin:0 auto 10px;
            display:flex;align-items:center;justify-content:center;">
            {sidebar_logo_html}
        </div>
        <div style="font-size:14px;font-weight:800;letter-spacing:2px;
            background:linear-gradient(90deg,#00d4ff,#0066ff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            SwiftMR</div>
        <div style="font-size:11px;color:#8892a4;margin-top:2px;letter-spacing:1px;">
            DICOM Tag Validator</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section-title">📋 Validation Rules</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:13px;line-height:1.8;">
        <div style="margin-bottom:6px;">
            <span style="color:#ff4444;font-weight:700;">❌ FAIL</span>
            &nbsp;— Required tag missing<br>
            <span style="font-size:11px;opacity:0.7;">SwiftMR cannot process</span>
        </div>
        <div style="margin-bottom:6px;">
            <span style="color:#ffb400;font-weight:700;">⚠️ WARNING</span>
            &nbsp;— Optional tag missing<br>
            <span style="font-size:11px;opacity:0.7;">Some features may be limited</span>
        </div>
        <div>
            <span style="color:#00c864;font-weight:700;">✅ PASS</span>
            &nbsp;— All required tags present<br>
            <span style="font-size:11px;opacity:0.7;">Ready for SwiftMR processing</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section-title">🏭 Supported Manufacturers</div>', unsafe_allow_html=True)
    for mfr in MANUFACTURER_TAGS.keys():
        st.markdown(f"""
        <div style="font-size:13px;padding:3px 0;">
            · {mfr}
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section-title">⚠️ Notes</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:13px;line-height:1.8;">
        🔒 Files are processed in memory only<br>
        🚫 Do NOT upload real patient data (PHI)<br>
        📦 Single DICOM file validation only<br>
        🏭 Private tags validated per manufacturer
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="text-align:center;font-size:11px;color:#4a5568;padding:8px 0;">
        © 2024 AIRS Medical Inc.<br>All rights reserved.
    </div>
    """, unsafe_allow_html=True)
