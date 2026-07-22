import streamlit as st
import pydicom
import pandas as pd
import io
import base64
import zipfile
import warnings
from pathlib import Path

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
    .file-problem-card {
        background: rgba(255,60,60,0.08) !important;
        border: 1px solid rgba(255,60,60,0.3) !important;
    }
    .file-warn-card {
        background: rgba(255,180,0,0.08) !important;
        border: 1px solid rgba(255,180,0,0.3) !important;
    }
    .file-ok-card {
        background: rgba(0,200,100,0.05) !important;
        border: 1px solid rgba(0,200,100,0.2) !important;
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
    .file-problem-card {
        background: rgba(255,60,60,0.06) !important;
        border: 1px solid rgba(255,60,60,0.3) !important;
    }
    .file-warn-card {
        background: rgba(255,180,0,0.06) !important;
        border: 1px solid rgba(255,180,0,0.3) !important;
    }
    .file-ok-card {
        background: rgba(0,200,100,0.04) !important;
        border: 1px solid rgba(0,200,100,0.2) !important;
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
    font-size: 28px; font-weight: 800;
    line-height: 1.1;
}
.metric-label {
    font-size: 11px; font-weight: 600;
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
.file-problem-card {
    border-radius: 12px; padding: 12px 16px;
    margin-bottom: 8px;
}
.file-warn-card {
    border-radius: 12px; padding: 12px 16px;
    margin-bottom: 8px;
}
.file-ok-card {
    border-radius: 12px; padding: 12px 16px;
    margin-bottom: 8px;
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

# ════════════════════════════════════════════════════
# Tag Definitions
# ════════════════════════════════════════════════════
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
]

OPTIONAL_TAGS = [
    {"name": "Overlay Bits Allocated",               "tag": "(6000,0100)", "vr": "US", "purpose": ""},
    {"name": "Overlay Bit Position",                 "tag": "(6000,0102)", "vr": "US", "purpose": ""},
    {"name": "Overlay Data",                         "tag": "(6000,3000)", "vr": "OB", "purpose": ""},
    {"name": "Overlay Rows",                         "tag": "(6000,0010)", "vr": "US", "purpose": ""},
    {"name": "Overlay Columns",                      "tag": "(6000,0011)", "vr": "US", "purpose": ""},
    {"name": "Diffusion b-value",                    "tag": "(0018,9087)", "vr": "FD", "purpose": ""},
    {"name": "Slice Location",                       "tag": "(0020,1041)", "vr": "DS", "purpose": "Slice Interpol"},
    {"name": "Manufacturer",                         "tag": "(0008,0070)", "vr": "LO", "purpose": ""},
    {"name": "Number of Averages",                   "tag": "(0018,0083)", "vr": "DS", "purpose": ""},
    {"name": "Percent Sampling",                     "tag": "(0018,0093)", "vr": "DS", "purpose": ""},
    {"name": "Acquisition Matrix",                   "tag": "(0018,1310)", "vr": "US", "purpose": ""},
    {"name": "Derivation Description",               "tag": "(0008,2111)", "vr": "ST", "purpose": ""},
    {"name": "In-Plane Phase Encoding Direction",    "tag": "(0018,1312)", "vr": "CS", "purpose": ""},
    {"name": "Percent Phase Field of View",          "tag": "(0018,0094)", "vr": "DS", "purpose": ""},
    {"name": "Request Attributes Sequence",          "tag": "(0040,0275)", "vr": "SQ", "purpose": "Fonar"},
    {"name": "Per-frame Functional Groups Sequence", "tag": "(5200,9230)", "vr": "SQ", "purpose": "Fonar"},
    {"name": "Derivation Code Sequence",             "tag": "(0008,9215)", "vr": "SQ", "purpose": "GE Subtraction"},
    {"name": "Field of View Dimensions",             "tag": "(0018,1149)", "vr": "IS", "purpose": "Paramed"},
]

MANUFACTURER_TAGS = {
    "Philips": [
        {"name": "Volume Based Calculation Technique",  "tag": "(2005,140F)", "vr": "CS"},
        {"name": "Image Plane Number",                  "tag": "(2001,100A)", "vr": "IS"},
        {"name": "MRSeriesNrOfSlices",                  "tag": "(2001,1018)", "vr": "SL"},
        {"name": "Stack",                               "tag": "(2001,105F)", "vr": "SQ"},
        {"name": "MRImageOffCentreAP",                  "tag": "(2005,1008)", "vr": "FL"},
        {"name": "MRImageOffCentreFH",                  "tag": "(2005,1009)", "vr": "FL"},
        {"name": "MRImageOffCentreRL",                  "tag": "(2005,100A)", "vr": "FL"},
        {"name": "SeriesDerivationDescription",         "tag": "(2001,10CC)", "vr": "ST"},
        {"name": "Philips Private Creator",             "tag": "(2005,0014)", "vr": "LO"},
        {"name": "Parallel Reduction Factor In-Plane",  "tag": "(2005,140F)", "vr": "FD"},
        {"name": "MR Acquisition Phase Encoding Steps", "tag": "(2005,140F)", "vr": "US"},
    ],
    "Siemens": [
        {"name": "Siemens Private Creator", "tag": "(0051,0010)", "vr": "LO"},
        {"name": "Siemens Private Creator", "tag": "(0021,0010)", "vr": "LO"},
        {"name": "Siemens Private Creator", "tag": "(0019,0010)", "vr": "LO"},
        {"name": "pat factor",              "tag": "(0051,1011)", "vr": "LO"},
        {"name": "pat factor",              "tag": "(0021,1009)", "vr": "LO"},
        {"name": "acquisition matrix",      "tag": "(0051,100B)", "vr": "LO"},
        {"name": "CSA HEADER1",             "tag": "(0029,1020)", "vr": "LO"},
        {"name": "CSA HEADER2",             "tag": "(0021,1019)", "vr": "LO"},
        {"name": "psd name1",               "tag": "(0019,109C)", "vr": "LO"},
        {"name": "psd name2",               "tag": "(0019,109E)", "vr": "LO"},
        {"name": "pseq id1",                "tag": "(0019,1012)", "vr": "SS"},
        {"name": "pseq id2",                "tag": "(0025,1006)", "vr": "SS"},
        {"name": "pseq id3",                "tag": "(0027,1032)", "vr": "SS"},
        {"name": "diffusion b-value",       "tag": "(0019,100C)", "vr": "IS"},
        {"name": "SQ Per-frame Functional", "tag": "(5200,9230)", "vr": "FD"},
    ],
    "GE": [
        {"name": "GE Private Creator",        "tag": "(0043,0010)", "vr": "LO"},
        {"name": "GE Private Creator",        "tag": "(0027,0010)", "vr": "LO"},
        {"name": "pat type",                  "tag": "(0043,1084)", "vr": "LO"},
        {"name": "pat factor",                "tag": "(0043,1083)", "vr": "DS"},
        {"name": "Image Type (real/imag)",    "tag": "(0043,102F)", "vr": "SS"},
        {"name": "Vas collapse flag",         "tag": "(0043,1030)", "vr": "SS"},
        {"name": "Functional Protocol",       "tag": "(0051,1006)", "vr": "LT"},
        {"name": "PDB Header",                "tag": "(0025,101B)", "vr": "OB"},
        {"name": "Derivation Code Sequence",  "tag": "(0008,9215)", "vr": "SQ"},
        {"name": "number of freq enc steps",  "tag": "(0027,1060)", "vr": "FL"},
        {"name": "number of phase enc steps", "tag": "(0027,1061)", "vr": "FL"},
    ],
    "Canon (Toshiba)": [
        {"name": "TOSHIBA_MEC", "tag": "(0029,1001)", "vr": "SQ"},
        {"name": "TOSHIBA_MEC", "tag": "(0029,1002)", "vr": "SQ"},
        {"name": "TOSHIBA_MEC", "tag": "(700D,0010)", "vr": "LO"},
        {"name": "TOSHIBA_MEC", "tag": "(700D,1011)", "vr": "US"},
        {"name": "TOSHIBA_MEC", "tag": "(700D,1014)", "vr": "SL"},
        {"name": "TOSHIBA_MEC", "tag": "(700D,1016)", "vr": "LO"},
        {"name": "TOSHIBA_MEC", "tag": "(700D,1018)", "vr": "SS"},
        {"name": "TOSHIBA_MEC", "tag": "(700D,1019)", "vr": "OB"},
    ],
    "Esaote": [
        {"name": "V1", "tag": "(0011,1001)", "vr": "OB"},
        {"name": "V1", "tag": "(0011,1002)", "vr": "DS"},
        {"name": "V1", "tag": "(0011,1003)", "vr": "DS"},
        {"name": "V1", "tag": "(0011,1004)", "vr": "DS"},
        {"name": "V1", "tag": "(0011,1008)", "vr": "DS"},
    ],
    "Fonar": [
        {"name": "MMCPrivate",                           "tag": "(0029,102F)", "vr": ""},
        {"name": "MMCPrivate",                           "tag": "(0029,1032)", "vr": ""},
        {"name": "MMCPrivate",                           "tag": "(0029,10D7)", "vr": ""},
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
    "Philips":         ["philips"],
    "Siemens":         ["siemens"],
    "GE":              ["ge medical", "ge healthcare", "general electric"],
    "Canon (Toshiba)": ["canon", "toshiba"],
    "Esaote":          ["esaote"],
    "Fonar":           ["fonar"],
    "Hyperfine":       ["hyperfine"],
    "Paramed":         ["paramed"],
}

# ════════════════════════════════════════════════════
# Utility Functions
# ════════════════════════════════════════════════════
def parse_tag_str(tag_str):
    tag_str = tag_str.strip("()")
    group, element = tag_str.split(",")
    return pydicom.tag.Tag(int(group, 16), int(element, 16))


def get_tag_value(ds, tag_str):
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


def validate_single_file(fname, file_bytes):
    """단일 DICOM 파일 전체 검증 → dict 반환"""
    try:
        ds = pydicom.dcmread(io.BytesIO(file_bytes), force=True)
    except Exception as e:
        return {"filename": fname, "error": str(e)}

    mfr_name, mfr_raw = detect_manufacturer(ds)
    req_results = validate_tags(ds, REQUIRED_TAGS, required=True)
    opt_results = validate_tags(ds, OPTIONAL_TAGS, required=False)
    mfr_results = []
    if mfr_name and mfr_name in MANUFACTURER_TAGS:
        mfr_results = validate_tags(ds, MANUFACTURER_TAGS[mfr_name], required=False)

    req_missing = sum(1 for r in req_results if not r["present"])
    opt_missing = sum(1 for r in opt_results if not r["present"])

    if req_missing == 0:
        status = "PASS"
    else:
        status = "FAIL"

    return {
        "filename":    fname,
        "error":       None,
        "status":      status,
        "ds":          ds,
        "mfr_name":    mfr_name,
        "mfr_raw":     mfr_raw,
        "req_results": req_results,
        "opt_results": opt_results,
        "mfr_results": mfr_results,
        "req_total":   len(req_results),
        "req_present": len(req_results) - req_missing,
        "req_missing": req_missing,
        "opt_total":   len(opt_results),
        "opt_present": len(opt_results) - opt_missing,
        "opt_missing": opt_missing,
        "mfr_total":   len(mfr_results),
        "mfr_present": sum(1 for r in mfr_results if r["present"]),
    }


def load_files_from_upload(uploaded_file):
    """업로드 파일 → {filename: bytes} dict 반환"""
    file_dict = {}
    name = uploaded_file.name.lower()

    if name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(uploaded_file.read())) as zf:
            for zname in zf.namelist():
                zname_lower = zname.lower()
                # __MACOSX 등 숨김 폴더 제외
                if zname_lower.startswith("__") or zname_lower.startswith("."):
                    continue
                if zname_lower.endswith(".dcm") or zname_lower.endswith(".dicom"):
                    file_dict[Path(zname).name] = zf.read(zname)
                # 확장자 없는 파일도 DICOM일 수 있음
                elif "." not in Path(zname).name:
                    try:
                        data = zf.read(zname)
                        pydicom.dcmread(io.BytesIO(data), force=True)
                        file_dict[Path(zname).name] = data
                    except Exception:
                        pass
    else:
        file_dict[uploaded_file.name] = uploaded_file.read()

    return file_dict


def render_tag_table(results):
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


def build_export_df(result):
    rows = []
    for r in result["req_results"]:
        rows.append({
            "File":     result["filename"],
            "Category": "Required",
            "Name":     r["name"],
            "Tag":      r["tag"],
            "VR":       r["vr"],
            "Purpose":  r["purpose"],
            "Status":   "Present" if r["present"] else "MISSING",
            "Value":    r["value"],
        })
    for r in result["opt_results"]:
        rows.append({
            "File":     result["filename"],
            "Category": "Optional",
            "Name":     r["name"],
            "Tag":      r["tag"],
            "VR":       r["vr"],
            "Purpose":  r["purpose"],
            "Status":   "Present" if r["present"] else "Missing",
            "Value":    r["value"],
        })
    for r in result["mfr_results"]:
        rows.append({
            "File":     result["filename"],
            "Category": f"Manufacturer ({result['mfr_name']})",
            "Name":     r["name"],
            "Tag":      r["tag"],
            "VR":       r["vr"],
            "Purpose":  r.get("purpose", ""),
            "Status":   "Present" if r["present"] else "Missing",
            "Value":    r["value"],
        })
    return pd.DataFrame(rows)


def build_all_export_df(all_results):
    dfs = []
    for r in all_results:
        if r.get("error"):
            continue
        dfs.append(build_export_df(r))
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


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
    <div style="width:32px;height:32px;
        background:linear-gradient(135deg,#00d4ff,#0066ff);
        border-radius:50%;display:flex;align-items:center;
        justify-content:center;font-weight:800;color:white;
        font-size:15px;flex-shrink:0;">1</div>
    Upload DICOM File
  </div>
  <div style="font-size:13px;opacity:0.7;margin-top:-8px;">
    Supports single <b>.dcm</b> file or <b>.zip</b> archive containing multiple DICOM files
  </div>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload a DICOM file or ZIP archive",
    type=["dcm", "DCM", "zip", "ZIP"],
    help="Single .dcm file or .zip containing multiple DICOM files"
)

if uploaded:
    # ── 파일 로드 ─────────────────────────────────────
    with st.spinner("📂 Loading files..."):
        file_dict = load_files_from_upload(uploaded)

    if not file_dict:
        st.error("❌ No valid DICOM files found in the uploaded file.")
        st.stop()

    total_files = len(file_dict)
    st.success(
        f"✅ **{uploaded.name}** — "
        f"{'ZIP archive' if uploaded.name.lower().endswith('.zip') else 'Single DICOM'} | "
        f"**{total_files}** DICOM file(s) detected"
    )

    # ── 전체 검증 ─────────────────────────────────────
    with st.spinner("🔍 Validating all DICOM tags..."):
        all_results = []
        progress = st.progress(0)
        for i, (fname, fbytes) in enumerate(file_dict.items()):
            all_results.append(validate_single_file(fname, fbytes))
            progress.progress((i + 1) / total_files)
        progress.empty()

    # ── 통계 집계 ─────────────────────────────────────
    valid_results  = [r for r in all_results if not r.get("error")]
    error_results  = [r for r in all_results if r.get("error")]
    fail_results   = [r for r in valid_results if r["status"] == "FAIL"]
    pass_results   = [r for r in valid_results if r["status"] == "PASS"]

    total_pass  = len(pass_results)
    total_fail  = len(fail_results)
    total_error = len(error_results)

    # 가장 문제 있는 파일 (missing required tags 가장 많은 순)
    worst_files = sorted(fail_results, key=lambda x: x["req_missing"], reverse=True)

    # ════════════════════════════════════════════════
    # SECTION 2: Overall Summary
    # ════════════════════════════════════════════════
    st.markdown("""
    <div class="section-card">
      <div class="section-title">
        <div style="width:32px;height:32px;
            background:linear-gradient(135deg,#00d4ff,#0066ff);
            border-radius:50%;display:flex;align-items:center;
            justify-content:center;font-weight:800;color:white;
            font-size:15px;flex-shrink:0;">2</div>
        Overall Summary
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Overall Pass/Fail 판정
    if total_fail == 0 and total_error == 0:
        overall_cls   = "overall-pass"
        overall_icon  = "✅"
        overall_title = "ALL PASS"
        overall_sub   = f"All {total_files} DICOM file(s) have all required tags. SwiftMR processing is possible."
    elif total_fail == total_files:
        overall_cls   = "overall-fail"
        overall_icon  = "❌"
        overall_title = "ALL FAIL"
        overall_sub   = f"All {total_files} DICOM file(s) are missing required tags. SwiftMR cannot process."
    else:
        overall_cls   = "overall-warning"
        overall_icon  = "⚠️"
        overall_title = "PARTIAL FAIL"
        overall_sub   = (
            f"{total_fail} of {total_files} file(s) are missing required tags. "
            "Please review the problematic files below."
        )

    st.markdown(f"""
    <div class="summary-card {overall_cls}">
        <div class="overall-title">{overall_icon} {overall_title}</div>
        <div class="overall-sub">{overall_sub}</div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#00d4ff;">{total_files}</div>
            <div class="metric-label">Total Files</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#00c864;">{total_pass}</div>
            <div class="metric-label">✅ Pass</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#ff4444;">{total_fail}</div>
            <div class="metric-label">❌ Fail</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#ffb400;">{total_error}</div>
            <div class="metric-label">⚠️ Error</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        pass_rate = int(total_pass / total_files * 100) if total_files > 0 else 0
        rate_color = "#00c864" if pass_rate == 100 else "#ffb400" if pass_rate > 0 else "#ff4444"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{rate_color};">{pass_rate}%</div>
            <div class="metric-label">Pass Rate</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # SECTION 3: Most Problematic Files
    # ════════════════════════════════════════════════
    if worst_files:
        st.markdown("""
        <div class="section-card">
          <div class="section-title">
            <div style="width:32px;height:32px;
                background:linear-gradient(135deg,#ff4444,#cc0000);
                border-radius:50%;display:flex;align-items:center;
                justify-content:center;font-weight:800;color:white;
                font-size:15px;flex-shrink:0;">3</div>
            Most Problematic Files
            <span style="font-size:13px;font-weight:500;opacity:0.7;margin-left:4px;">
              — Sorted by missing required tags (worst first)
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        for rank, r in enumerate(worst_files[:10], 1):  # 최대 10개
            missing_tags = [x for x in r["req_results"] if not x["present"]]
            missing_names = ", ".join([f'<b>{x["name"]}</b>' for x in missing_tags])

            st.markdown(f"""
            <div class="file-problem-card">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                    <span style="font-size:18px;font-weight:900;color:#ff4444;">#{rank}</span>
                    <span style="font-size:14px;font-weight:700;">{r['filename']}</span>
                    <span style="margin-left:auto;font-size:12px;
                        background:rgba(255,60,60,0.2);color:#ff4444;
                        padding:2px 10px;border-radius:20px;font-weight:700;">
                        ❌ {r['req_missing']} Required Missing
                    </span>
                </div>
                <div style="font-size:12px;opacity:0.8;line-height:1.6;">
                    🏭 Manufacturer: <b>{r['mfr_raw']}</b> &nbsp;·&nbsp;
                    Required: {r['req_present']}/{r['req_total']} &nbsp;·&nbsp;
                    Optional: {r['opt_present']}/{r['opt_total']}
                </div>
                <div style="font-size:12px;margin-top:6px;color:#ff6666;">
                    Missing: {missing_names}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Error 파일 표시
    if error_results:
        st.markdown("<br>", unsafe_allow_html=True)
        for r in error_results:
            st.markdown(f"""
            <div class="file-problem-card">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:14px;font-weight:700;">{r['filename']}</span>
                    <span style="margin-left:auto;font-size:12px;
                        background:rgba(255,60,60,0.2);color:#ff4444;
                        padding:2px 10px;border-radius:20px;font-weight:700;">
                        ⚠️ Read Error
                    </span>
                </div>
                <div style="font-size:12px;opacity:0.7;margin-top:4px;">
                    {r['error']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # SECTION 4: File-by-File Detail (Dropdown)
    # ════════════════════════════════════════════════
    st.markdown("""
    <div class="section-card">
      <div class="section-title">
        <div style="width:32px;height:32px;
            background:linear-gradient(135deg,#00d4ff,#0066ff);
            border-radius:50%;display:flex;align-items:center;
            justify-content:center;font-weight:800;color:white;
            font-size:15px;flex-shrink:0;">4</div>
        File-by-File Detail
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 드롭다운 옵션 생성 (상태 아이콘 포함)
    def make_label(r):
        if r.get("error"):
            return f"⚠️  {r['filename']}  [ERROR]"
        icon = "✅" if r["status"] == "PASS" else "❌"
        missing_info = f"  — {r['req_missing']} req missing" if r["req_missing"] > 0 else ""
        return f"{icon}  {r['filename']}{missing_info}"

    dropdown_options = [make_label(r) for r in all_results]

    # 가장 문제 있는 파일을 기본 선택
    default_idx = 0
    if worst_files:
        worst_fname = worst_files[0]["filename"]
        for i, r in enumerate(all_results):
            if r["filename"] == worst_fname:
                default_idx = i
                break

    selected_label = st.selectbox(
        "Select a file to view detailed tag report",
        options=dropdown_options,
        index=default_idx,
        key="file_selector"
    )

    selected_result = all_results[dropdown_options.index(selected_label)]

    st.markdown("<br>", unsafe_allow_html=True)

    if selected_result.get("error"):
        st.error(f"❌ Cannot read file: **{selected_result['filename']}**\n\n{selected_result['error']}")
    else:
        r = selected_result

        # 파일 상태 배너
        if r["status"] == "PASS":
            banner_cls = "overall-pass"
            banner_icon = "✅"
            banner_title = "PASS"
            banner_sub = "All required tags are present. SwiftMR processing is possible."
        else:
            banner_cls = "overall-fail"
            banner_icon = "❌"
            banner_title = "FAIL"
            banner_sub = f"{r['req_missing']} required tag(s) missing. SwiftMR cannot process this file."

        st.markdown(f"""
        <div class="summary-card {banner_cls}" style="padding:16px 20px;margin-bottom:16px;">
            <div style="font-size:20px;font-weight:900;letter-spacing:1px;margin-bottom:2px;">
                {banner_icon} {banner_title} — {r['filename']}
            </div>
            <div style="font-size:13px;opacity:0.8;">{banner_sub}</div>
        </div>
        """, unsafe_allow_html=True)

        # 파일 메트릭
        fc1, fc2, fc3, fc4, fc5 = st.columns(5)
        file_metrics = [
            (fc1, str(r["req_present"]),  "Required Present",  "#00c864"),
            (fc2, str(r["req_missing"]),  "Required Missing",  "#ff4444"),
            (fc3, str(r["opt_present"]),  "Optional Present",  "#00d4ff"),
            (fc4, str(r["opt_missing"]),  "Optional Missing",  "#ffb400"),
            (fc5, r["mfr_raw"] if r["mfr_raw"] != "Unknown" else "—",
             "Manufacturer", "#a78bfa"),
        ]
        for col, val, label, color in file_metrics:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color:{color};font-size:22px;">{val}</div>
                    <div class="metric-label">{label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Manufacturer Badge
        if r["mfr_name"]:
            st.markdown(f"""
            <div style="margin-bottom:16px;">
                <span class="manufacturer-badge">
                    🏭 Detected: <b>{r['mfr_name']}</b>
                    &nbsp;·&nbsp; Raw: <i>{r['mfr_raw']}</i>
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Missing Required Tags 강조 박스
        missing_req = [x for x in r["req_results"] if not x["present"]]
        if missing_req:
            st.markdown("""
            <div style="
                background: rgba(255,60,60,0.1);
                border: 1.5px solid rgba(255,60,60,0.4);
                border-left: 4px solid #ff4444;
                border-radius: 12px;
                padding: 14px 20px;
                margin-bottom: 16px;
            ">
                <div style="font-weight:800;color:#ff4444;margin-bottom:8px;font-size:14px;">
                    ❌ Missing Required Tags — SwiftMR Cannot Process This File
                </div>
            """ + "".join([
                f'<div style="font-size:13px;margin:4px 0;">'
                f'• <b>{x["name"]}</b> '
                f'<span style="font-family:monospace;font-size:11px;opacity:0.7;">{x["tag"]}</span>'
                f'</div>'
                for x in missing_req
            ]) + "</div>", unsafe_allow_html=True)

        # Required Tags 테이블
        req_color = "#ff4444" if r["req_missing"] > 0 else "#00c864"
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">
                🔴 Required Tags
                <span style="font-size:13px;font-weight:600;color:{req_color};margin-left:8px;">
                    {r['req_present']}/{r['req_total']} Present
                </span>
            </div>
            {render_tag_table(r['req_results'])}
        </div>
        """, unsafe_allow_html=True)

        # Optional Tags 테이블
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">
                🟡 Optional Tags
                <span style="font-size:13px;font-weight:600;color:#ffb400;margin-left:8px;">
                    {r['opt_present']}/{r['opt_total']} Present
                </span>
            </div>
            {render_tag_table(r['opt_results'])}
        </div>
        """, unsafe_allow_html=True)

        # Manufacturer Private Tags 테이블
        if r["mfr_name"] and r["mfr_results"]:
            st.markdown(f"""
            <div class="section-card">
                <div class="section-title">
                    🏭 {r['mfr_name']} Private Tags
                    <span style="font-size:13px;font-weight:600;color:#00d4ff;margin-left:8px;">
                        {r['mfr_present']}/{r['mfr_total']} Present
                    </span>
                </div>
                {render_tag_table(r['mfr_results'])}
            </div>
            """, unsafe_allow_html=True)
        elif not r["mfr_name"]:
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
    # SECTION 5: Export
    # ════════════════════════════════════════════════
    st.markdown("""
    <div class="section-card">
      <div class="section-title">
        <div style="width:32px;height:32px;
            background:linear-gradient(135deg,#00d4ff,#0066ff);
            border-radius:50%;display:flex;align-items:center;
            justify-content:center;font-weight:800;color:white;
            font-size:15px;flex-shrink:0;">5</div>
        Export Report
      </div>
    </div>
    """, unsafe_allow_html=True)

    export_tab1, export_tab2 = st.tabs(["📄 Current File", "📦 All Files"])

    with export_tab1:
        if not selected_result.get("error"):
            df_single = build_export_df(selected_result)
            col1, col2 = st.columns(2)
            with col1:
                csv_data = df_single.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"tag_report_{selected_result['filename'].replace('.dcm','')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col2:
                excel_buf = io.BytesIO()
                with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                    df_single.to_excel(writer, index=False, sheet_name="Tag Report")
                    ws = writer.sheets["Tag Report"]
                    from openpyxl.styles import PatternFill
                    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                        status = row[6].value
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
                    label="⬇️ Download Excel",
                    data=excel_buf.getvalue(),
                    file_name=f"tag_report_{selected_result['filename'].replace('.dcm','')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            with st.expander("📊 Preview Table", expanded=False):
                st.dataframe(df_single, use_container_width=True, hide_index=True, height=400)

    with export_tab2:
        df_all = build_all_export_df(all_results)
        if not df_all.empty:
            col1, col2 = st.columns(2)
            with col1:
                csv_all = df_all.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download All CSV",
                    data=csv_all,
                    file_name=f"tag_report_ALL_{uploaded.name.replace('.zip','').replace('.dcm','')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col2:
                excel_all_buf = io.BytesIO()
                with pd.ExcelWriter(excel_all_buf, engine="openpyxl") as writer:
                    # 전체 시트
                    df_all.to_excel(writer, index=False, sheet_name="All Files")
                    ws = writer.sheets["All Files"]
                    from openpyxl.styles import PatternFill
                    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                        status = row[6].value
                        if status == "MISSING":
                            for cell in row:
                                cell.fill = PatternFill("solid", fgColor="FFCCCC")
                        elif status == "Missing":
                            for cell in row:
                                cell.fill = PatternFill("solid", fgColor="FFF3CC")
                        elif status == "Present":
                            for cell in row:
                                cell.fill = PatternFill("solid", fgColor="CCFFDD")
                    # Summary 시트
                    summary_rows = []
                    for res in all_results:
                        if res.get("error"):
                            summary_rows.append({
                                "Filename": res["filename"],
                                "Status": "ERROR",
                                "Manufacturer": "—",
                                "Required Present": "—",
                                "Required Missing": "—",
                                "Optional Present": "—",
                                "Error": res["error"],
                            })
                        else:
                            summary_rows.append({
                                "Filename": res["filename"],
                                "Status": res["status"],
                                "Manufacturer": res["mfr_raw"],
                                "Required Present": res["req_present"],
                                "Required Missing": res["req_missing"],
                                "Optional Present": res["opt_present"],
                                "Error": "",
                            })
                    df_summary = pd.DataFrame(summary_rows)
                    df_summary.to_excel(writer, index=False, sheet_name="Summary")
                    ws2 = writer.sheets["Summary"]
                    for row in ws2.iter_rows(min_row=2, max_row=ws2.max_row):
                        status = row[1].value
                        if status == "FAIL":
                            for cell in row:
                                cell.fill = PatternFill("solid", fgColor="FFCCCC")
                        elif status == "PASS":
                            for cell in row:
                                cell.fill = PatternFill("solid", fgColor="CCFFDD")
                        elif status == "ERROR":
                            for cell in row:
                                cell.fill = PatternFill("solid", fgColor="FFE5CC")

                st.download_button(
                    label="⬇️ Download All Excel",
                    data=excel_all_buf.getvalue(),
                    file_name=f"tag_report_ALL_{uploaded.name.replace('.zip','').replace('.dcm','')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            with st.expander("📊 Preview All Files Table", expanded=False):
                st.dataframe(df_all, use_container_width=True, hide_index=True, height=400)


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

    st.markdown('<div class="sidebar-section-title">📁 Supported Upload</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:13px;line-height:1.8;">
        📄 Single <b>.dcm</b> file<br>
        📦 <b>.zip</b> archive with multiple DICOM files<br>
        <span style="font-size:11px;opacity:0.6;">
        (Extension-less DICOM files inside ZIP are also detected)
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section-title">🏭 Supported Manufacturers</div>', unsafe_allow_html=True)
    for mfr in MANUFACTURER_TAGS.keys():
        st.markdown(f'<div style="font-size:13px;padding:3px 0;">· {mfr}</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section-title">⚠️ Notes</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:13px;line-height:1.8;">
        🔒 Files processed in memory only<br>
        🚫 Do NOT upload real patient data (PHI)<br>
        📦 ZIP archive supported<br>
        🏭 Private tags validated per manufacturer
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="text-align:center;font-size:11px;color:#4a5568;padding:8px 0;">
        © 2024 AIRS Medical Inc.<br>All rights reserved.
    </div>
    """, unsafe_allow_html=True)
