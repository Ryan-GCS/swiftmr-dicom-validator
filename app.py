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
    .phi-notice {
        background: linear-gradient(135deg, rgba(0,180,100,0.10), rgba(0,120,80,0.08)) !important;
        border: 1.5px solid rgba(0,200,120,0.4) !important;
        border-left: 4px solid #00c878 !important;
    }
    .cat1-header {
        background: linear-gradient(135deg, rgba(255,60,60,0.15), rgba(200,0,0,0.08)) !important;
        border: 1px solid rgba(255,60,60,0.3) !important;
    }
    .cat2-header {
        background: linear-gradient(135deg, rgba(255,140,0,0.15), rgba(200,100,0,0.08)) !important;
        border: 1px solid rgba(255,140,0,0.3) !important;
    }
    .cat3-header {
        background: linear-gradient(135deg, rgba(0,180,255,0.12), rgba(0,100,200,0.08)) !important;
        border: 1px solid rgba(0,180,255,0.3) !important;
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
    .phi-notice {
        background: linear-gradient(135deg, rgba(0,180,100,0.08), rgba(0,120,80,0.05)) !important;
        border: 1.5px solid rgba(0,180,100,0.4) !important;
        border-left: 4px solid #00a86b !important;
    }
    .cat1-header {
        background: linear-gradient(135deg, rgba(255,60,60,0.10), rgba(200,0,0,0.05)) !important;
        border: 1px solid rgba(255,60,60,0.3) !important;
    }
    .cat2-header {
        background: linear-gradient(135deg, rgba(255,140,0,0.10), rgba(200,100,0,0.05)) !important;
        border: 1px solid rgba(255,140,0,0.3) !important;
    }
    .cat3-header {
        background: linear-gradient(135deg, rgba(0,180,255,0.08), rgba(0,100,200,0.05)) !important;
        border: 1px solid rgba(0,180,255,0.3) !important;
    }
}
.airs-header {
    display: flex; align-items: center; gap: 16px;
    padding: 20px 28px; margin-bottom: 24px;
    border-radius: 0 0 16px 16px;
}
.airs-logo-box {
    width: 52px; height: 52px; background: transparent;
    border-radius: 12px; display: flex; align-items: center;
    justify-content: center; flex-shrink: 0;
}
.airs-title h1 {
    margin: 0; font-size: 22px; font-weight: 800;
    background: linear-gradient(90deg, #00d4ff, #0066ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
}
.airs-title p { margin: 2px 0 0; font-size: 13px; letter-spacing: 1px; }
.airs-badge {
    margin-left: auto; padding: 6px 14px;
    border-radius: 20px; font-size: 12px; font-weight: 600; letter-spacing: 1px;
}
.summary-card { border-radius: 16px; padding: 24px 28px; margin-bottom: 20px; }
.section-card  { border-radius: 16px; padding: 20px 24px; margin-bottom: 16px; }
.section-title {
    font-size: 16px; font-weight: 700;
    display: flex; align-items: center; gap: 10px; margin-bottom: 16px;
}
.metric-card { border-radius: 12px; padding: 16px 20px; text-align: center; }
.metric-value { font-size: 28px; font-weight: 800; line-height: 1.1; }
.metric-label {
    font-size: 11px; font-weight: 600;
    letter-spacing: 1px; text-transform: uppercase; margin-top: 4px;
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
.overall-title { font-size: 28px; font-weight: 900; letter-spacing: 2px; margin-bottom: 4px; }
.overall-sub   { font-size: 14px; opacity: 0.8; }
.manufacturer-badge {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 700; margin: 4px;
}
.sidebar-section-title {
    font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 10px; padding-bottom: 6px;
}
.phi-notice    { border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; }
.file-problem-card { border-radius: 12px; padding: 12px 16px; margin-bottom: 8px; }
.cat1-header   { border-radius: 12px; padding: 14px 20px; margin-bottom: 12px; }
.cat2-header   { border-radius: 12px; padding: 14px 20px; margin-bottom: 12px; }
.cat3-header   { border-radius: 12px; padding: 14px 20px; margin-bottom: 12px; }
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

# 1. Mandatory-Public
CAT1_MANDATORY = [
    {"name": "Instance Number",           "tag": (0x0020,0x0013), "vr": "IS", "purpose": "",              "mandatory": True},
    {"name": "Series Number",             "tag": (0x0020,0x0011), "vr": "IS", "purpose": "Derived",       "mandatory": True},
    {"name": "Image Type",                "tag": (0x0008,0x0008), "vr": "CS", "purpose": "(3D)",          "mandatory": True},
    {"name": "Series Description",        "tag": (0x0008,0x103E), "vr": "LO", "purpose": "SWI",           "mandatory": True},
    {"name": "Pixel Data",                "tag": (0x7FE0,0x0010), "vr": "OB", "purpose": "",              "mandatory": True},
    {"name": "Pixel Representation",      "tag": (0x0028,0x0103), "vr": "US", "purpose": "",              "mandatory": True},
    {"name": "Bits Stored",               "tag": (0x0028,0x0101), "vr": "US", "purpose": "",              "mandatory": True},
    {"name": "Rows",                      "tag": (0x0028,0x0010), "vr": "US", "purpose": "",              "mandatory": True},
    {"name": "Columns",                   "tag": (0x0028,0x0011), "vr": "US", "purpose": "",              "mandatory": True},
    {"name": "Pixel Spacing",             "tag": (0x0028,0x0030), "vr": "DS", "purpose": "",              "mandatory": True},
    {"name": "Window Center",             "tag": (0x0028,0x1050), "vr": "DS", "purpose": "MIP",           "mandatory": True},
    {"name": "Window Width",              "tag": (0x0028,0x1051), "vr": "DS", "purpose": "MIP",           "mandatory": True},
    {"name": "Image Orientation Patient", "tag": (0x0020,0x0037), "vr": "DS", "purpose": "post",          "mandatory": True},
    {"name": "Image Position Patient",    "tag": (0x0020,0x0032), "vr": "DS", "purpose": "",              "mandatory": True},
    {"name": "Spacing Between Slices",    "tag": (0x0018,0x0088), "vr": "DS", "purpose": "post",          "mandatory": True},
    {"name": "Slice Thickness",           "tag": (0x0018,0x0050), "vr": "DS", "purpose": "post",          "mandatory": True},
    # optional
    {"name": "Overlay Bits Allocated",    "tag": (0x6000,0x0100), "vr": "US", "purpose": "",              "mandatory": False},
    {"name": "Overlay Bit Position",      "tag": (0x6000,0x0102), "vr": "US", "purpose": "",              "mandatory": False},
    {"name": "Overlay Data",              "tag": (0x6000,0x3000), "vr": "OB", "purpose": "",              "mandatory": False},
    {"name": "Overlay Rows",              "tag": (0x6000,0x0010), "vr": "US", "purpose": "",              "mandatory": False},
    {"name": "Overlay Columns",           "tag": (0x6000,0x0011), "vr": "US", "purpose": "",              "mandatory": False},
    {"name": "Diffusion b-value",         "tag": (0x0018,0x9087), "vr": "FD", "purpose": "",              "mandatory": False},
    {"name": "Slice Location",            "tag": (0x0020,0x1041), "vr": "DS", "purpose": "Slice Interpol","mandatory": False},
]

# 2. Required-Public
CAT2_TAGS = [
    {"name": "Manufacturer",                         "tag": (0x0008,0x0070), "vr": "LO", "note": ""},
    {"name": "Number of Averages",                   "tag": (0x0018,0x0083), "vr": "DS", "note": ""},
    {"name": "Percent Sampling",                     "tag": (0x0018,0x0093), "vr": "DS", "note": ""},
    {"name": "Acquisition Matrix",                   "tag": (0x0018,0x1310), "vr": "US", "note": ""},
    {"name": "Derivation Description",               "tag": (0x0008,0x2111), "vr": "ST", "note": ""},
    {"name": "In-Plane Phase Encoding Direction",    "tag": (0x0018,0x1312), "vr": "CS", "note": ""},
    {"name": "Rows",                                 "tag": (0x0028,0x0010), "vr": "US", "note": ""},
    {"name": "Columns",                              "tag": (0x0028,0x0011), "vr": "US", "note": ""},
    {"name": "Percent Phase Field of View",          "tag": (0x0018,0x0094), "vr": "DS", "note": ""},
    {"name": "Spacing Between Slices",               "tag": (0x0018,0x0088), "vr": "DS", "note": ""},
    {"name": "Slice Thickness",                      "tag": (0x0018,0x0050), "vr": "DS", "note": ""},
    {"name": "Image Orientation Patient",            "tag": (0x0020,0x0037), "vr": "DS", "note": ""},
    {"name": "Image Position Patient",               "tag": (0x0020,0x0032), "vr": "DS", "note": ""},
    {"name": "Request Attributes Sequence",          "tag": (0x0040,0x0275), "vr": "SQ", "note": "Fonar / Other"},
    {"name": "Per-frame Functional Groups Sequence", "tag": (0x5200,0x9230), "vr": "SQ", "note": "Fonar / Other"},
    {"name": "Derivation Code Sequence",             "tag": (0x0008,0x9215), "vr": "SQ", "note": "GE / Subtraction"},
    {"name": "Field of View Dimensions",             "tag": (0x0018,0x1149), "vr": "IS", "note": "Paramed"},
]

# 3. Required-Private-MRI
CAT3_TAGS = [
    # Philips
    {"name": "Volume Based Calculation Technique",      "tag": (0x2005,0x140F), "vr": "CS", "manufacturer": "Philips",         "note": "post / [0](0008,9207)"},
    {"name": "Parallel Reduction Factor In-Plane",      "tag": (0x2005,0x140F), "vr": "FD", "manufacturer": "Philips",         "note": "[0](0018,9069)"},
    {"name": "MR Acquisition Phase Encoding Steps",     "tag": (0x2005,0x140F), "vr": "US", "manufacturer": "Philips",         "note": "[0](0018,9058)"},
    {"name": "MR Acquisition Frequency Encoding Steps", "tag": (0x2005,0x140F), "vr": "US", "manufacturer": "Philips",         "note": "[0](0018,9058)"},
    {"name": "Philips Private Creator",                 "tag": (0x2005,0x0014), "vr": "LO", "manufacturer": "Philips",         "note": ""},
    {"name": "Image Plane Number",                      "tag": (0x2001,0x100A), "vr": "IS", "manufacturer": "Philips",         "note": ""},
    {"name": "MRSeriesNrOfSlices",                      "tag": (0x2001,0x1018), "vr": "SL", "manufacturer": "Philips",         "note": ""},
    {"name": "Stack",                                   "tag": (0x2001,0x105F), "vr": "SQ", "manufacturer": "Philips",         "note": ""},
    {"name": "MRImageOffCentreAP",                      "tag": (0x2005,0x1008), "vr": "FL", "manufacturer": "Philips",         "note": ""},
    {"name": "MRImageOffCentreFH",                      "tag": (0x2005,0x1009), "vr": "FL", "manufacturer": "Philips",         "note": ""},
    {"name": "MRImageOffCentreRL",                      "tag": (0x2005,0x100A), "vr": "FL", "manufacturer": "Philips",         "note": ""},
    {"name": "SeriesDerivationDescription",             "tag": (0x2001,0x10CC), "vr": "ST", "manufacturer": "Philips",         "note": ""},
    # Siemens
    {"name": "Siemens Private Creator",                 "tag": (0x0051,0x0010), "vr": "LO", "manufacturer": "Siemens",         "note": ""},
    {"name": "Siemens Private Creator",                 "tag": (0x0021,0x0010), "vr": "LO", "manufacturer": "Siemens",         "note": ""},
    {"name": "Siemens Private Creator",                 "tag": (0x0019,0x0010), "vr": "LO", "manufacturer": "Siemens",         "note": ""},
    {"name": "pat factor",                              "tag": (0x0051,0x1011), "vr": "LO", "manufacturer": "Siemens",         "note": ""},
    {"name": "pat factor",                              "tag": (0x0021,0x1009), "vr": "LO", "manufacturer": "Siemens",         "note": ""},
    {"name": "acquisition matrix",                     "tag": (0x0051,0x100B), "vr": "LO", "manufacturer": "Siemens",         "note": ""},
    {"name": "diffusion b-value",                      "tag": (0x0019,0x100C), "vr": "IS", "manufacturer": "Siemens",         "note": ""},
    {"name": "CSA HEADER1",                             "tag": (0x0029,0x1020), "vr": "LO", "manufacturer": "Siemens",         "note": ""},
    {"name": "CSA HEADER2",                             "tag": (0x0021,0x1019), "vr": "LO", "manufacturer": "Siemens",         "note": ""},
    {"name": "psd name1",                               "tag": (0x0019,0x109C), "vr": "LO", "manufacturer": "Siemens",         "note": ""},
    {"name": "psd name2",                               "tag": (0x0019,0x109E), "vr": "LO", "manufacturer": "Siemens",         "note": ""},
    {"name": "pseq id1",                                "tag": (0x0019,0x1012), "vr": "SS", "manufacturer": "Siemens",         "note": ""},
    {"name": "pseq id2",                                "tag": (0x0025,0x1006), "vr": "SS", "manufacturer": "Siemens",         "note": ""},
    {"name": "pseq id3",                                "tag": (0x0027,0x1032), "vr": "SS", "manufacturer": "Siemens",         "note": ""},
    {"name": "slice resolution",                        "tag": (0x0019,0x1017), "vr": "DS", "manufacturer": "Siemens",         "note": ""},
    {"name": "SQ Per-frame Functional Groups Sequence", "tag": (0x5200,0x9230), "vr": "FD", "manufacturer": "Siemens",         "note": "[0](0018,9115)[0](0018,9069)"},
    # GE
    {"name": "GE Private Creator",                      "tag": (0x0043,0x0010), "vr": "LO", "manufacturer": "GE",              "note": ""},
    {"name": "GE Private Creator",                      "tag": (0x0027,0x0010), "vr": "LO", "manufacturer": "GE",              "note": ""},
    {"name": "pat type",                                "tag": (0x0043,0x1084), "vr": "LO", "manufacturer": "GE",              "note": ""},
    {"name": "pat factor",                              "tag": (0x0043,0x1083), "vr": "DS", "manufacturer": "GE",              "note": ""},
    {"name": "number of frequency encoding steps",      "tag": (0x0027,0x1060), "vr": "FL", "manufacturer": "GE",              "note": ""},
    {"name": "number of phase encoding steps in-plane", "tag": (0x0027,0x1061), "vr": "FL", "manufacturer": "GE",              "note": ""},
    {"name": "Image Type (real/imaginary/phase/mag)",   "tag": (0x0043,0x102F), "vr": "SS", "manufacturer": "GE",              "note": ""},
    {"name": "Functional Protocol",                     "tag": (0x0051,0x1006), "vr": "LT", "manufacturer": "GE",              "note": "ADC source bvalue"},
    {"name": "PDB Header",                              "tag": (0x0025,0x101B), "vr": "OB", "manufacturer": "GE",              "note": ""},
    {"name": "Vas collapse flag",                       "tag": (0x0043,0x1030), "vr": "SS", "manufacturer": "GE",              "note": ""},
    # Canon (Toshiba)
    {"name": "TOSHIBA_MEC",                             "tag": (0x0029,0x1001), "vr": "SQ", "manufacturer": "Canon (Toshiba)", "note": ""},
    {"name": "TOSHIBA_MEC",                             "tag": (0x0029,0x1002), "vr": "SQ", "manufacturer": "Canon (Toshiba)", "note": ""},
    {"name": "TOSHIBA_MEC",                             "tag": (0x700D,0x0010), "vr": "LO", "manufacturer": "Canon (Toshiba)", "note": ""},
    {"name": "TOSHIBA_MEC",                             "tag": (0x700D,0x1011), "vr": "US", "manufacturer": "Canon (Toshiba)", "note": ""},
    {"name": "TOSHIBA_MEC",                             "tag": (0x700D,0x1014), "vr": "SL", "manufacturer": "Canon (Toshiba)", "note": ""},
    {"name": "TOSHIBA_MEC",                             "tag": (0x700D,0x1016), "vr": "LO", "manufacturer": "Canon (Toshiba)", "note": ""},
    {"name": "TOSHIBA_MEC",                             "tag": (0x700D,0x1018), "vr": "SS", "manufacturer": "Canon (Toshiba)", "note": ""},
    {"name": "TOSHIBA_MEC",                             "tag": (0x700D,0x1019), "vr": "OB", "manufacturer": "Canon (Toshiba)", "note": ""},
    # Esaote
    {"name": "V1",                                      "tag": (0x0011,0x1001), "vr": "OB", "manufacturer": "Esaote",          "note": ""},
    {"name": "V1",                                      "tag": (0x0011,0x1002), "vr": "DS", "manufacturer": "Esaote",          "note": ""},
    {"name": "V1",                                      "tag": (0x0011,0x1003), "vr": "DS", "manufacturer": "Esaote",          "note": ""},
    {"name": "V1",                                      "tag": (0x0011,0x1004), "vr": "DS", "manufacturer": "Esaote",          "note": ""},
    {"name": "V1",                                      "tag": (0x0011,0x1008), "vr": "DS", "manufacturer": "Esaote",          "note": ""},
    # Fonar
    {"name": "MMCPrivate",                              "tag": (0x0029,0x102F), "vr": "",   "manufacturer": "Fonar",           "note": ""},
    {"name": "MMCPrivate",                              "tag": (0x0029,0x1032), "vr": "",   "manufacturer": "Fonar",           "note": ""},
    {"name": "MMCPrivate",                              "tag": (0x0029,0x10D7), "vr": "",   "manufacturer": "Fonar",           "note": ""},
    # Hyperfine
    {"name": "Hyperfine Private Creator",               "tag": (0x351B,0x0010), "vr": "LO", "manufacturer": "Hyperfine",       "note": ""},
    {"name": "Hyperfine Private Creator",               "tag": (0x351B,0x1001), "vr": "",   "manufacturer": "Hyperfine",       "note": ""},
    {"name": "Hyperfine Private Creator",               "tag": (0x351B,0x1002), "vr": "",   "manufacturer": "Hyperfine",       "note": ""},
    {"name": "Hyperfine Private Creator",               "tag": (0x351B,0x1003), "vr": "",   "manufacturer": "Hyperfine",       "note": ""},
    {"name": "Hyperfine Private Creator",               "tag": (0x351B,0x1004), "vr": "",   "manufacturer": "Hyperfine",       "note": ""},
    {"name": "Hyperfine Private Creator",               "tag": (0x351B,0x1005), "vr": "",   "manufacturer": "Hyperfine",       "note": ""},
    {"name": "Hyperfine Private Creator",               "tag": (0x351B,0x1006), "vr": "",   "manufacturer": "Hyperfine",       "note": ""},
    # Paramed
    {"name": "acquisition voxel size",                  "tag": (0x0011,0x1017), "vr": "LO", "manufacturer": "Paramed",         "note": ""},
    {"name": "slice resolution",                        "tag": (0x0021,0x101B), "vr": "DS", "manufacturer": "Paramed",         "note": ""},
]

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
# Core Functions — pydicom Tag 객체 직접 사용
# ════════════════════════════════════════════════════
def get_tag_value(ds, tag_tuple):
    """
    tag_tuple: (0x0020, 0x0013) 형식의 tuple
    pydicom Tag 객체로 직접 조회 → 공백/포맷 문제 완전 해결
    """
    try:
        tag = pydicom.tag.Tag(tag_tuple[0], tag_tuple[1])
        if tag in ds:
            elem = ds[tag]
            if elem.VR == "SQ":
                return f"[Sequence {len(elem.value)} item(s)]"
            val = elem.value
            if isinstance(val, bytes):
                return f"[Binary {len(val)} bytes]"
            if isinstance(val, pydicom.multival.MultiValue):
                items = [str(v) for v in val]
                joined = ", ".join(items)
                return joined[:80] + "..." if len(joined) > 80 else joined
            s = str(val)
            return s[:80] + "..." if len(s) > 80 else s
        return None
    except Exception:
        return None


def tag_to_str(tag_tuple):
    """(0x0020, 0x0013) → '(0020,0013)' 표시용 문자열"""
    return f"({tag_tuple[0]:04X},{tag_tuple[1]:04X})"


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


def validate_cat1(ds):
    results = []
    for t in CAT1_MANDATORY:
        value   = get_tag_value(ds, t["tag"])
        present = value is not None
        results.append({
            "Name":      t["name"],
            "Tag":       tag_to_str(t["tag"]),
            "VR":        t["vr"],
            "Purpose":   t["purpose"],
            "Type":      "🔴 Mandatory" if t["mandatory"] else "🟡 Optional",
            "Value":     value if present else "MISSING",
            "Status":    "✅  Present" if present else ("❌  Missing" if t["mandatory"] else "⚠️  Missing"),
            "_present":  present,
            "_mandatory": t["mandatory"],
        })
    return results


def validate_cat2(ds):
    results = []
    for t in CAT2_TAGS:
        value   = get_tag_value(ds, t["tag"])
        present = value is not None
        results.append({
            "Name":    t["name"],
            "Tag":     tag_to_str(t["tag"]),
            "VR":      t["vr"],
            "Note":    t["note"],
            "Value":   value if present else "MISSING",
            "Status":  "✅  Present" if present else "⚠️  Missing",
            "_present": present,
        })
    return results


def validate_cat3(ds, mfr_name):
    results = []
    for t in CAT3_TAGS:
        value   = get_tag_value(ds, t["tag"])
        present = value is not None
        results.append({
            "Manufacturer": t["manufacturer"],
            "Name":         t["name"],
            "Tag":          tag_to_str(t["tag"]),
            "VR":           t["vr"],
            "Note":         t["note"],
            "Value":        value if present else "MISSING",
            "Status":       "✅  Present" if present else "⚠️  Missing",
            "_present":     present,
            "_detected":    (mfr_name is not None and t["manufacturer"] == mfr_name),
        })
    return results


def validate_single_file(fname, file_bytes):
    try:
        ds = pydicom.dcmread(io.BytesIO(file_bytes), force=True)
    except Exception as e:
        return {"filename": fname, "error": str(e)}

    mfr_name, mfr_raw = detect_manufacturer(ds)
    cat1 = validate_cat1(ds)
    cat2 = validate_cat2(ds)
    cat3 = validate_cat3(ds, mfr_name)

    cat1_mand_missing = sum(1 for r in cat1 if r["_mandatory"] and not r["_present"])
    cat1_mand_total   = sum(1 for r in cat1 if r["_mandatory"])
    cat1_opt_total    = sum(1 for r in cat1 if not r["_mandatory"])
    cat1_opt_present  = sum(1 for r in cat1 if not r["_mandatory"] and r["_present"])
    cat2_missing      = sum(1 for r in cat2 if not r["_present"])
    cat3_missing      = sum(1 for r in cat3 if not r["_present"])
    cat3_mfr          = [r for r in cat3 if r["_detected"]]
    cat3_mfr_missing  = sum(1 for r in cat3_mfr if not r["_present"])

    return {
        "filename":               fname,
        "error":                  None,
        "status":                 "PASS" if cat1_mand_missing == 0 else "FAIL",
        "mfr_name":               mfr_name,
        "mfr_raw":                mfr_raw,
        "cat1":                   cat1,
        "cat2":                   cat2,
        "cat3":                   cat3,
        "cat1_mandatory_total":   cat1_mand_total,
        "cat1_mandatory_present": cat1_mand_total - cat1_mand_missing,
        "cat1_mandatory_missing": cat1_mand_missing,
        "cat1_optional_total":    cat1_opt_total,
        "cat1_optional_present":  cat1_opt_present,
        "cat2_total":             len(cat2),
        "cat2_present":           len(cat2) - cat2_missing,
        "cat2_missing":           cat2_missing,
        "cat3_total":             len(cat3),
        "cat3_present":           len(cat3) - cat3_missing,
        "cat3_missing":           cat3_missing,
        "cat3_mfr_total":         len(cat3_mfr),
        "cat3_mfr_present":       len(cat3_mfr) - cat3_mfr_missing,
        "cat3_mfr_missing":       cat3_mfr_missing,
    }


def load_files_from_upload(uploaded_file):
    file_dict = {}
    name = uploaded_file.name.lower()
    if name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(uploaded_file.read())) as zf:
            for zname in zf.namelist():
                zl = zname.lower()
                if zl.startswith("__") or zl.startswith("."):
                    continue
                if zl.endswith(".dcm") or zl.endswith(".dicom"):
                    file_dict[Path(zname).name] = zf.read(zname)
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


def to_display_df(results, cols):
    df = pd.DataFrame(results)
    return df[[c for c in cols if c in df.columns]]


def style_df(df):
    def row_style(row):
        s = str(row.get("Status", ""))
        if "❌" in s:
            return ["background-color: rgba(255,60,60,0.15)"] * len(row)
        elif "⚠️" in s:
            return ["background-color: rgba(255,180,0,0.10)"] * len(row)
        else:
            return ["background-color: rgba(0,200,100,0.08)"] * len(row)
    return df.style.apply(row_style, axis=1)


def build_export_df(result):
    rows = []
    for r in result["cat1"]:
        rows.append({
            "File": result["filename"], "Category": "1. Mandatory-Public",
            "Type": "Mandatory" if r["_mandatory"] else "Optional",
            "Manufacturer": "—",
            "Name": r["Name"], "Tag": r["Tag"], "VR": r["VR"],
            "Purpose/Note": r["Purpose"],
            "Status": "Present" if r["_present"] else ("MISSING" if r["_mandatory"] else "Missing"),
            "Value": r["Value"],
        })
    for r in result["cat2"]:
        rows.append({
            "File": result["filename"], "Category": "2. Required-Public",
            "Type": "Required", "Manufacturer": "—",
            "Name": r["Name"], "Tag": r["Tag"], "VR": r["VR"],
            "Purpose/Note": r["Note"],
            "Status": "Present" if r["_present"] else "Missing",
            "Value": r["Value"],
        })
    for r in result["cat3"]:
        rows.append({
            "File": result["filename"], "Category": "3. Required-Private-MRI",
            "Type": "Required", "Manufacturer": r["Manufacturer"],
            "Name": r["Name"], "Tag": r["Tag"], "VR": r["VR"],
            "Purpose/Note": r["Note"],
            "Status": "Present" if r["_present"] else "Missing",
            "Value": r["Value"],
        })
    return pd.DataFrame(rows)


def excel_export(df, summary_df=None):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Tag Report")
        ws = writer.sheets["Tag Report"]
        from openpyxl.styles import PatternFill
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            status = row[8].value if len(row) > 8 else ""
            if status == "MISSING":
                fill = PatternFill("solid", fgColor="FFCCCC")
            elif status == "Missing":
                fill = PatternFill("solid", fgColor="FFF3CC")
            else:
                fill = PatternFill("solid", fgColor="CCFFDD")
            for cell in row:
                cell.fill = fill
        if summary_df is not None:
            summary_df.to_excel(writer, index=False, sheet_name="Summary")
            ws2 = writer.sheets["Summary"]
            for row in ws2.iter_rows(min_row=2, max_row=ws2.max_row):
                status = row[1].value if len(row) > 1 else ""
                if status == "FAIL":
                    fill = PatternFill("solid", fgColor="FFCCCC")
                elif status == "PASS":
                    fill = PatternFill("solid", fgColor="CCFFDD")
                else:
                    fill = PatternFill("solid", fgColor="FFE5CC")
                for cell in row:
                    cell.fill = fill
    return buf.getvalue()


# ════════════════════════════════════════════════════
# PHI NOTICE
# ════════════════════════════════════════════════════
st.markdown("""
<div class="phi-notice">
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        <span style="font-size:20px;">🔐</span>
        <span style="font-size:15px; font-weight:800; letter-spacing:1px;">
            Privacy & Data Handling Notice
        </span>
    </div>
    <div style="font-size:13px; line-height:2.0;">
        📋 This tool is designed for <b>internal QA and compatibility validation</b> purposes only.<br>
        🔄 Uploaded files are processed <b>entirely in memory</b> and are
            <b>never stored, logged, or retained</b> on any server.<br>
        🗑️ All data is <b>automatically cleared</b> when the session ends or the page is refreshed.<br>
        ✅ Files containing <b>PHI (Protected Health Information)</b> may be uploaded
            for validation purposes, as no data is persisted beyond the active session.<br>
        ⚠️ However, it is <b>strongly recommended</b> to use
            <b>de-identified or anonymized DICOM files</b> whenever possible.
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# UPLOAD
# ════════════════════════════════════════════════════
st.markdown("""
<div class="section-card">
  <div class="section-title">
    <div style="width:32px;height:32px;
        background:linear-gradient(135deg,#00d4ff,#0066ff);
        border-radius:50%;display:flex;align-items:center;
        justify-content:center;font-weight:800;color:white;font-size:15px;flex-shrink:0;">1</div>
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
    with st.spinner("📂 Loading files..."):
        file_dict = load_files_from_upload(uploaded)

    if not file_dict:
        st.error("❌ No valid DICOM files found.")
        st.stop()

    total_files = len(file_dict)
    st.success(
        f"✅ **{uploaded.name}** — "
        f"{'ZIP archive' if uploaded.name.lower().endswith('.zip') else 'Single DICOM'} | "
        f"**{total_files}** DICOM file(s) detected"
    )

    with st.spinner("🔍 Validating all DICOM tags..."):
        all_results = []
        progress = st.progress(0)
        for i, (fname, fbytes) in enumerate(file_dict.items()):
            all_results.append(validate_single_file(fname, fbytes))
            progress.progress((i + 1) / total_files)
        progress.empty()

    valid_results = [r for r in all_results if not r.get("error")]
    error_results = [r for r in all_results if r.get("error")]
    fail_results  = [r for r in valid_results if r["status"] == "FAIL"]
    pass_results  = [r for r in valid_results if r["status"] == "PASS"]
    worst_files   = sorted(fail_results, key=lambda x: x["cat1_mandatory_missing"], reverse=True)
    total_pass    = len(pass_results)
    total_fail    = len(fail_results)
    total_error   = len(error_results)

    # ════════════════════════════════════════════════
    # Overall Summary
    # ════════════════════════════════════════════════
    st.markdown("""
    <div class="section-card">
      <div class="section-title">
        <div style="width:32px;height:32px;
            background:linear-gradient(135deg,#00d4ff,#0066ff);
            border-radius:50%;display:flex;align-items:center;
            justify-content:center;font-weight:800;color:white;font-size:15px;flex-shrink:0;">2</div>
        Overall Summary
        <span style="font-size:13px;font-weight:400;opacity:0.6;margin-left:4px;">
          — Based on Category 1 Mandatory tags
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if total_fail == 0 and total_error == 0:
        oc, oi, ot = "overall-pass", "✅", "ALL PASS"
        os_ = f"All {total_files} file(s) have all Mandatory-Public tags. SwiftMR processing is possible."
    elif total_fail == total_files:
        oc, oi, ot = "overall-fail", "❌", "ALL FAIL"
        os_ = f"All {total_files} file(s) are missing Mandatory-Public tags. SwiftMR cannot process."
    else:
        oc, oi, ot = "overall-warning", "⚠️", "PARTIAL FAIL"
        os_ = f"{total_fail} of {total_files} file(s) are missing Mandatory-Public tags."

    st.markdown(f"""
    <div class="summary-card {oc}">
        <div class="overall-title">{oi} {ot}</div>
        <div class="overall-sub">{os_}</div>
    </div>
    """, unsafe_allow_html=True)

    pass_rate  = int(total_pass / total_files * 100) if total_files > 0 else 0
    rate_color = "#00c864" if pass_rate == 100 else "#ffb400" if pass_rate > 0 else "#ff4444"
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, label, color in [
        (c1, str(total_files), "Total Files", "#00d4ff"),
        (c2, str(total_pass),  "✅ Pass",      "#00c864"),
        (c3, str(total_fail),  "❌ Fail",      "#ff4444"),
        (c4, str(total_error), "⚠️ Error",     "#ffb400"),
        (c5, f"{pass_rate}%",  "Pass Rate",   rate_color),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color};">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # Most Problematic Files
    # ════════════════════════════════════════════════
    if worst_files:
        st.markdown("""
        <div class="section-card">
          <div class="section-title">
            <div style="width:32px;height:32px;
                background:linear-gradient(135deg,#ff4444,#cc0000);
                border-radius:50%;display:flex;align-items:center;
                justify-content:center;font-weight:800;color:white;font-size:15px;flex-shrink:0;">3</div>
            Most Problematic Files
            <span style="font-size:13px;font-weight:400;opacity:0.6;margin-left:4px;">
              — Sorted by Cat.1 Mandatory missing (worst first)
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        for rank, r in enumerate(worst_files[:10], 1):
            missing_tags  = [x for x in r["cat1"] if x["_mandatory"] and not x["_present"]]
            missing_names = " · ".join([f'<b>{x["Name"]}</b>' for x in missing_tags])
            st.markdown(f"""
            <div class="file-problem-card">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                    <span style="font-size:18px;font-weight:900;color:#ff4444;">#{rank}</span>
                    <span style="font-size:14px;font-weight:700;">{r['filename']}</span>
                    <span style="margin-left:auto;font-size:12px;
                        background:rgba(255,60,60,0.2);color:#ff4444;
                        padding:2px 10px;border-radius:20px;font-weight:700;">
                        ❌ Cat.1 Mandatory: {r['cat1_mandatory_missing']} Missing
                    </span>
                </div>
                <div style="font-size:12px;opacity:0.8;line-height:1.8;">
                    🏭 Manufacturer: <b>{r['mfr_raw']}</b> &nbsp;·&nbsp;
                    Cat.1 Mandatory: {r['cat1_mandatory_present']}/{r['cat1_mandatory_total']} &nbsp;·&nbsp;
                    Cat.2: {r['cat2_present']}/{r['cat2_total']} &nbsp;·&nbsp;
                    Cat.3: {r['cat3_present']}/{r['cat3_total']}
                </div>
                <div style="font-size:12px;margin-top:6px;color:#ff6666;">
                    Missing: {missing_names}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if error_results:
        for r in error_results:
            st.markdown(f"""
            <div class="file-problem-card">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:14px;font-weight:700;">{r['filename']}</span>
                    <span style="margin-left:auto;font-size:12px;
                        background:rgba(255,60,60,0.2);color:#ff4444;
                        padding:2px 10px;border-radius:20px;font-weight:700;">⚠️ Read Error</span>
                </div>
                <div style="font-size:12px;opacity:0.7;margin-top:4px;">{r['error']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # File-by-File Detail
    # ════════════════════════════════════════════════
    st.markdown("""
    <div class="section-card">
      <div class="section-title">
        <div style="width:32px;height:32px;
            background:linear-gradient(135deg,#00d4ff,#0066ff);
            border-radius:50%;display:flex;align-items:center;
            justify-content:center;font-weight:800;color:white;font-size:15px;flex-shrink:0;">4</div>
        File-by-File Detail
      </div>
    </div>
    """, unsafe_allow_html=True)

    def make_label(r):
        if r.get("error"):
            return f"⚠️  {r['filename']}  [ERROR]"
        icon = "✅" if r["status"] == "PASS" else "❌"
        miss = f"  — Cat.1 Mandatory {r['cat1_mandatory_missing']} missing" if r["cat1_mandatory_missing"] > 0 else ""
        return f"{icon}  {r['filename']}{miss}"

    dropdown_options = [make_label(r) for r in all_results]
    default_idx = 0
    if worst_files:
        wf = worst_files[0]["filename"]
        for i, r in enumerate(all_results):
            if r["filename"] == wf:
                default_idx = i
                break

    selected_label  = st.selectbox(
        "Select a file to view detailed tag report",
        options=dropdown_options,
        index=default_idx,
        key="file_selector"
    )
    selected_result = all_results[dropdown_options.index(selected_label)]
    st.markdown("<br>", unsafe_allow_html=True)

    if selected_result.get("error"):
        st.error(f"❌ Cannot read: **{selected_result['filename']}**\n\n{selected_result['error']}")
    else:
        r = selected_result

        # 파일 상태 배너
        if r["status"] == "PASS":
            bc, bi, bt = "overall-pass", "✅", "PASS"
            bs = "All Mandatory-Public tags present. SwiftMR processing is possible."
        else:
            bc, bi, bt = "overall-fail", "❌", "FAIL"
            bs = f"{r['cat1_mandatory_missing']} Mandatory-Public tag(s) missing. SwiftMR cannot process."

        st.markdown(f"""
        <div class="summary-card {bc}" style="padding:16px 20px;margin-bottom:16px;">
            <div style="font-size:20px;font-weight:900;letter-spacing:1px;margin-bottom:2px;">
                {bi} {bt} — {r['filename']}
            </div>
            <div style="font-size:13px;opacity:0.8;">{bs}</div>
        </div>
        """, unsafe_allow_html=True)

        # Manufacturer
        mfr_display = r['mfr_name'] if r['mfr_name'] else "Unknown / Not Detected"
        mfr_raw_display = r['mfr_raw'] if r['mfr_raw'] != "Unknown" else "—"
        st.markdown(f"""
        <div style="margin-bottom:16px;">
            <span class="manufacturer-badge">
                🏭 Detected Manufacturer: <b>{mfr_display}</b>
                &nbsp;·&nbsp; Raw Value: <i>{mfr_raw_display}</i>
            </span>
        </div>
        """, unsafe_allow_html=True)

        # ── Category 1 ───────────────────────────────
        mand_color = "#ff4444" if r["cat1_mandatory_missing"] > 0 else "#00c864"
        st.markdown(f"""
        <div class="cat1-header">
            <div style="font-size:17px;font-weight:800;margin-bottom:6px;">
                🔴 Category 1 — Mandatory-Public
            </div>
            <div style="font-size:13px;opacity:0.85;line-height:1.8;">
                Mandatory: <span style="color:{mand_color};font-weight:700;">
                    {r['cat1_mandatory_present']}/{r['cat1_mandatory_total']} Present
                </span>
                &nbsp;·&nbsp;
                Optional: <span style="color:#ffb400;font-weight:600;">
                    {r['cat1_optional_present']}/{r['cat1_optional_total']} Present
                </span>
                &nbsp;·&nbsp;
                <span style="opacity:0.7;font-size:12px;">
                    PASS/FAIL is determined by Mandatory tags only
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        missing_mand = [x for x in r["cat1"] if x["_mandatory"] and not x["_present"]]
        if missing_mand:
            items = "".join([
                f'<div style="font-size:13px;margin:3px 0;">• <b>{x["Name"]}</b> '
                f'<span style="font-family:monospace;font-size:11px;opacity:0.6;">{x["Tag"]}</span></div>'
                for x in missing_mand
            ])
            st.markdown(f"""
            <div style="background:rgba(255,60,60,0.1);border:1.5px solid rgba(255,60,60,0.4);
                border-left:4px solid #ff4444;border-radius:12px;padding:14px 20px;margin-bottom:12px;">
                <div style="font-weight:800;color:#ff4444;margin-bottom:8px;font-size:14px;">
                    ❌ Missing Mandatory Tags — SwiftMR Cannot Process This File
                </div>{items}
            </div>
            """, unsafe_allow_html=True)

        df_cat1 = to_display_df(r["cat1"], ["Name","Tag","VR","Purpose","Type","Value","Status"])
        st.dataframe(
            style_df(df_cat1),
            use_container_width=True, hide_index=True,
            height=min(50 + len(df_cat1) * 35, 650),
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Category 2 ───────────────────────────────
        cat2_color = "#ffb400" if r["cat2_missing"] > 0 else "#00c864"
        st.markdown(f"""
        <div class="cat2-header">
            <div style="font-size:17px;font-weight:800;margin-bottom:6px;">
                🟠 Category 2 — Required-Public
            </div>
            <div style="font-size:13px;opacity:0.85;line-height:1.8;">
                <span style="color:{cat2_color};font-weight:700;">
                    {r['cat2_present']}/{r['cat2_total']} Present
                </span>
                &nbsp;·&nbsp;
                <span style="opacity:0.7;font-size:12px;">
                    Missing tags may limit some SwiftMR features
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        df_cat2 = to_display_df(r["cat2"], ["Name","Tag","VR","Note","Value","Status"])
        st.dataframe(
            style_df(df_cat2),
            use_container_width=True, hide_index=True,
            height=min(50 + len(df_cat2) * 35, 650),
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Category 3 ───────────────────────────────
        cat3_color = "#ffb400" if r["cat3_missing"] > 0 else "#00c864"
        mfr_info   = ""
        if r["mfr_name"]:
            mfr_c    = "#ffb400" if r["cat3_mfr_missing"] > 0 else "#00c864"
            mfr_info = (
                f"&nbsp;·&nbsp; <b>{r['mfr_name']}</b> tags: "
                f"<span style='color:{mfr_c};font-weight:700;'>"
                f"{r['cat3_mfr_present']}/{r['cat3_mfr_total']} Present</span>"
            )

        st.markdown(f"""
        <div class="cat3-header">
            <div style="font-size:17px;font-weight:800;margin-bottom:6px;">
                🔵 Category 3 — Required-Private-MRI
            </div>
            <div style="font-size:13px;opacity:0.85;line-height:1.8;">
                All manufacturers: <span style="color:{cat3_color};font-weight:700;">
                    {r['cat3_present']}/{r['cat3_total']} Present
                </span>
                {mfr_info}
                &nbsp;·&nbsp;
                <span style="opacity:0.7;font-size:12px;">
                    Detected manufacturer rows are highlighted
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        mfr_list       = sorted(set(t["manufacturer"] for t in CAT3_TAGS))
        filter_options = ["All Manufacturers"] + mfr_list
        default_filter = filter_options.index(r["mfr_name"]) if r["mfr_name"] and r["mfr_name"] in filter_options else 0

        selected_mfr  = st.selectbox(
            "Filter by Manufacturer",
            options=filter_options,
            index=default_filter,
            key="cat3_mfr_filter"
        )
        cat3_filtered = r["cat3"] if selected_mfr == "All Manufacturers" else [
            x for x in r["cat3"] if x["Manufacturer"] == selected_mfr
        ]

        def style_cat3(df):
            def row_style(row):
                s        = str(row.get("Status", ""))
                detected = row.get("Manufacturer", "") == r["mfr_name"]
                if "⚠️" in s:
                    bg = "rgba(255,180,0,0.18)" if detected else "rgba(255,180,0,0.08)"
                elif "✅" in s:
                    bg = "rgba(0,200,100,0.15)" if detected else "rgba(0,200,100,0.06)"
                else:
                    bg = ""
                return [f"background-color: {bg}"] * len(row)
            return df.style.apply(row_style, axis=1)

        df_cat3 = to_display_df(cat3_filtered, ["Manufacturer","Name","Tag","VR","Note","Value","Status"])
        st.dataframe(
            style_cat3(df_cat3),
            use_container_width=True, hide_index=True,
            height=min(50 + len(df_cat3) * 35, 700),
        )

        if r["mfr_name"]:
            st.caption(
                f"💡 Detected manufacturer: **{r['mfr_name']}** — "
                f"rows for this manufacturer are highlighted with stronger color."
            )
        else:
            st.caption("ℹ️ Manufacturer not detected. All manufacturers shown without highlighting.")

        st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # Export
    # ════════════════════════════════════════════════
    st.markdown("""
    <div class="section-card">
      <div class="section-title">
        <div style="width:32px;height:32px;
            background:linear-gradient(135deg,#00d4ff,#0066ff);
            border-radius:50%;display:flex;align-items:center;
            justify-content:center;font-weight:800;color:white;font-size:15px;flex-shrink:0;">5</div>
        Export Report
      </div>
    </div>
    """, unsafe_allow_html=True)

    export_tab1, export_tab2 = st.tabs(["📄 Current File", "📦 All Files"])

    with export_tab1:
        if not selected_result.get("error"):
            df_export = build_export_df(selected_result)
            col1, col2 = st.columns(2)
            base = selected_result["filename"].replace(".dcm","")
            with col1:
                st.download_button(
                    "⬇️ Download CSV",
                    data=df_export.to_csv(index=False).encode("utf-8"),
                    file_name=f"tag_report_{base}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col2:
                st.download_button(
                    "⬇️ Download Excel",
                    data=excel_export(df_export),
                    file_name=f"tag_report_{base}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            with st.expander("📊 Preview", expanded=False):
                st.dataframe(df_export, use_container_width=True, hide_index=True, height=400)

    with export_tab2:
        valid_for_export = [r for r in all_results if not r.get("error")]
        if valid_for_export:
            all_dfs   = [build_export_df(r) for r in valid_for_export]
            df_all    = pd.concat(all_dfs, ignore_index=True)
            base_name = uploaded.name.replace(".zip","").replace(".dcm","")

            # Summary DataFrame
            summary_rows = []
            for res in all_results:
                if res.get("error"):
                    summary_rows.append({
                        "Filename": res["filename"], "Status": "ERROR",
                        "Manufacturer": "—",
                        "Cat1 Mandatory Present": "—", "Cat1 Mandatory Missing": "—",
                        "Cat1 Optional Present": "—",
                        "Cat2 Present": "—", "Cat2 Missing": "—",
                        "Cat3 Present": "—", "Cat3 Missing": "—",
                        "Error": res["error"],
                    })
                else:
                    summary_rows.append({
                        "Filename": res["filename"], "Status": res["status"],
                        "Manufacturer": res["mfr_raw"],
                        "Cat1 Mandatory Present": res["cat1_mandatory_present"],
                        "Cat1 Mandatory Missing": res["cat1_mandatory_missing"],
                        "Cat1 Optional Present":  res["cat1_optional_present"],
                        "Cat2 Present": res["cat2_present"],
                        "Cat2 Missing": res["cat2_missing"],
                        "Cat3 Present": res["cat3_present"],
                        "Cat3 Missing": res["cat3_missing"],
                        "Error": "",
                    })
            df_summary = pd.DataFrame(summary_rows)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "⬇️ Download All CSV",
                    data=df_all.to_csv(index=False).encode("utf-8"),
                    file_name=f"tag_report_ALL_{base_name}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col2:
                st.download_button(
                    "⬇️ Download All Excel",
                    data=excel_export(df_all, df_summary),
                    file_name=f"tag_report_ALL_{base_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            with st.expander("📊 Preview All Files", expanded=False):
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

    st.markdown('<div class="sidebar-section-title">📋 Categories</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:13px;line-height:2.0;">
        <div style="margin-bottom:8px;">
            <span style="color:#ff4444;font-weight:700;">🔴 Cat.1 Mandatory-Public</span><br>
            <span style="font-size:11px;opacity:0.7;">
                PASS/FAIL basis · Missing = cannot process
            </span>
        </div>
        <div style="margin-bottom:8px;">
            <span style="color:#ff8c00;font-weight:700;">🟠 Cat.2 Required-Public</span><br>
            <span style="font-size:11px;opacity:0.7;">
                Public standard tags · Missing = limited features
            </span>
        </div>
        <div>
            <span style="color:#00d4ff;font-weight:700;">🔵 Cat.3 Required-Private-MRI</span><br>
            <span style="font-size:11px;opacity:0.7;">
                Manufacturer private tags · All + detected highlighted
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section-title">📊 Status Legend</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:13px;line-height:1.9;">
        <span style="color:#ff4444;font-weight:700;">❌ Missing</span>
        — Mandatory tag absent (FAIL)<br>
        <span style="color:#ffb400;font-weight:700;">⚠️ Missing</span>
        — Optional/Required tag absent<br>
        <span style="color:#00c864;font-weight:700;">✅ Present</span>
        — Tag found in DICOM file
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section-title">🏭 Supported Manufacturers</div>', unsafe_allow_html=True)
    for mfr in MANUFACTURER_KEYWORDS.keys():
        st.markdown(f'<div style="font-size:13px;padding:3px 0;">· {mfr}</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section-title">🔐 Data Privacy</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:12px;line-height:1.9;opacity:0.85;">
        🔄 Processed <b>in memory only</b><br>
        🗑️ Auto-cleared on session end<br>
        💾 <b>No data stored</b> on server<br>
        ✅ PHI files: one-time session use<br>
        ⚠️ De-identified files recommended
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="text-align:center;font-size:11px;color:#4a5568;padding:8px 0;">
        © 2024 AIRS Medical Inc.<br>All rights reserved.
    </div>
    """, unsafe_allow_html=True)
