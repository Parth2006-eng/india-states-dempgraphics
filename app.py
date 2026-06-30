import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import re

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India State Explorer",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── DATA ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    data = {
        "State": [
            "Andaman and Nicobar","Andhra Pradesh","Arunachal Pradesh","Assam","Bihar",
            "Chandigarh","Chhattisgarh","Dādra and Nagar Haveli and Damān and Diu","Delhi",
            "Goa","Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir","Jharkhand",
            "Karnataka","Kerala","Ladakh","Lakshadweep","Madhya Pradesh","Maharashtra",
            "Manipur","Meghalaya","Mizoram","Nagaland","Orissa","Puducherry","Punjab",
            "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh",
            "Uttaranchal","West Bengal"
        ],
        "ID": [
            "INAN","INAP","INAR","INAS","INBR",
            "INCH","INCT","INDH","INDL",
            "INGA","INGJ","INHR","INHP","INJK","INJH",
            "INKA","INKL","INLA","INLD","INMP","INMH",
            "INMN","INML","INMZ","INNL","INOR","INPY","INPB",
            "INRJ","INSK","INTN","INTG","INTR","INUP",
            "INUT","INWB"
        ],
        # Demographics
        "Population (Millions)": [
            0.38, 49.4, 1.38, 31.2, 104.1,
            1.06, 25.5, 0.59, 16.8,
            1.46, 60.4, 25.4, 6.86, 12.5, 33.0,
            61.1, 33.4, 0.27, 0.07, 72.6, 112.4,
            2.86, 2.97, 1.09, 1.98, 41.97, 1.24, 27.7,
            68.5, 0.61, 72.1, 35.0, 3.67, 199.8,
            10.1, 91.3
        ],
        "Area (1000 km²)": [
            8.25, 162.9, 83.7, 78.4, 94.2,
            0.11, 135.2, 0.49, 1.48,
            3.7, 196.0, 44.2, 55.7, 42.2, 79.7,
            191.8, 38.9, 59.1, 0.03, 308.3, 307.7,
            22.3, 22.4, 21.1, 16.6, 155.7, 0.48, 50.4,
            342.2, 7.1, 130.1, 112.1, 10.5, 240.9,
            53.5, 88.8
        ],
        "Literacy Rate (%)": [
            86.3, 67.4, 66.9, 73.2, 63.8,
            86.4, 71.0, 77.7, 86.3,
            88.7, 79.3, 76.6, 83.8, 68.7, 67.6,
            75.6, 94.0, 77.7, 92.3, 70.6, 82.9,
            79.9, 75.5, 91.6, 80.1, 73.5, 86.6, 76.7,
            67.1, 82.2, 80.3, 66.4, 87.8, 67.7,
            79.6, 77.1
        ],
        "Sex Ratio (F per 1000 M)": [
            876, 993, 938, 958, 918,
            818, 991, 774, 868,
            973, 919, 879, 972, 889, 948,
            973, 1084, 790, 946, 931, 929,
            987, 986, 976, 931, 979, 1037, 895,
            928, 890, 996, 988, 960, 912,
            963, 950
        ],
        # Economy
        "GDP (Billion ₹)": [
            82, 10280, 310, 4460, 8480,
            1200, 4020, 450, 9800,
            920, 21800, 10100, 2200, 2350, 4350,
            23600, 11200, 250, 12, 13900, 39500,
            530, 470, 340, 380, 8100, 720, 7100,
            15600, 450, 23500, 13800, 610, 25600,
            3400, 17100
        ],
        "Per Capita Income (₹ Thousands)": [
            215, 211, 221, 143, 51,
            1130, 131, 427, 432,
            629, 290, 298, 201, 131, 91,
            290, 238, 133, 66, 136, 256,
            70, 99, 133, 89, 109, 195, 176,
            158, 465, 242, 276, 106, 97,
            229, 126
        ],
        "Unemployment Rate (%)": [
            6.2, 4.1, 3.8, 7.0, 10.2,
            9.6, 3.5, 4.2, 13.8,
            5.4, 2.8, 14.7, 7.3, 12.0, 7.2,
            2.8, 6.2, 4.1, 3.2, 2.1, 3.2,
            4.8, 3.1, 4.2, 12.1, 5.6, 8.2, 7.6,
            2.8, 3.1, 4.9, 3.6, 3.2, 4.7,
            3.5, 4.8
        ],
        # Health
        "Hospitals per 100k": [
            12.4, 8.2, 3.1, 5.6, 3.2,
            18.1, 4.1, 7.2, 14.3,
            16.2, 9.1, 8.7, 11.2, 6.2, 4.8,
            10.2, 14.1, 2.8, 8.4, 5.2, 9.8,
            5.1, 4.2, 4.8, 3.9, 6.1, 15.6, 10.1,
            5.8, 7.2, 11.4, 9.2, 6.8, 4.2,
            9.6, 9.8
        ],
        "Infant Mortality Rate": [
            20, 31, 35, 38, 51,
            14, 42, 18, 28,
            7, 28, 31, 22, 42, 38,
            26, 6, 33, 18, 44, 22,
            12, 28, 30, 22, 38, 17, 21,
            35, 18, 19, 28, 28, 42,
            35, 22
        ],
        # Education
        "Schools per 100k": [
            142, 182, 128, 198, 168,
            281, 158, 142, 198,
            196, 172, 192, 218, 148, 172,
            188, 214, 110, 195, 162, 174,
            196, 184, 178, 162, 178, 228, 196,
            156, 198, 214, 186, 202, 148,
            204, 198
        ],
        "College Enrollment Rate (%)": [
            28.2, 22.1, 15.4, 18.2, 14.3,
            48.2, 19.1, 24.2, 38.6,
            38.4, 27.2, 31.8, 29.6, 16.2, 16.8,
            31.2, 36.4, 12.4, 22.1, 18.8, 32.6,
            21.4, 20.8, 22.4, 18.2, 21.2, 38.2, 28.6,
            18.8, 24.2, 46.2, 32.4, 22.8, 16.8,
            31.8, 21.6
        ],
        # Agriculture
        "Crop Production (Million Tonnes)": [
            0.01, 22.8, 0.42, 8.2, 18.4,
            0.12, 16.2, 0.08, 0.14,
            0.32, 24.6, 22.8, 2.8, 2.6, 8.4,
            16.2, 8.6, 0.08, 0.01, 38.4, 28.6,
            0.82, 0.96, 0.26, 0.48, 24.8, 0.28, 28.6,
            26.8, 0.28, 19.2, 18.8, 1.48, 58.6,
            3.8, 22.8
        ],
        "Irrigated Land (%)": [
            14.2, 38.6, 8.2, 28.4, 62.8,
            88.6, 32.4, 42.8, 78.6,
            36.2, 48.4, 84.8, 22.6, 38.2, 12.8,
            26.8, 18.6, 4.2, 10.4, 38.6, 18.4,
            22.4, 12.8, 14.6, 18.2, 36.8, 64.2, 98.2,
            34.8, 8.6, 62.4, 46.8, 28.4, 78.6,
            62.8, 62.4
        ]
    }
    return pd.DataFrame(data)

df = load_data()

# ── SVG LOADER ────────────────────────────────────────────────────────────────
@st.cache_data
def load_svg():
    with open("india_clean.svg", "r", encoding="utf-8") as f:
        return f.read()

svg_raw = load_svg()

# ── MANUAL COLOR OVERRIDES ─────────────────────────────────────────────────────
if "manual_colors" not in st.session_state:
    st.session_state.manual_colors = {}   # { "INMH": "#ff0000", ... }
if "color_mode" not in st.session_state:
    st.session_state.color_mode = "By Metric"

# ── METRIC CONFIG ─────────────────────────────────────────────────────────────
CATEGORIES = {
    "📊 Demographics": {
        "Population (Millions)": {"fmt": "{:.1f}M", "color": "#4f83cc"},
        "Area (1000 km²)":       {"fmt": "{:.1f}k km²","color": "#5cb85c"},
        "Literacy Rate (%)":     {"fmt": "{:.1f}%",   "color": "#f0ad4e"},
        "Sex Ratio (F per 1000 M)": {"fmt": "{:.0f}", "color": "#d9534f"},
    },
    "💰 Economy": {
        "GDP (Billion ₹)":            {"fmt": "₹{:.0f}B",  "color": "#5cb85c"},
        "Per Capita Income (₹ Thousands)": {"fmt": "₹{:.0f}k", "color": "#f0ad4e"},
        "Unemployment Rate (%)":      {"fmt": "{:.1f}%",   "color": "#d9534f"},
    },
    "🏥 Health": {
        "Hospitals per 100k":   {"fmt": "{:.1f}",  "color": "#5bc0de"},
        "Infant Mortality Rate":{"fmt": "{:.0f}",  "color": "#d9534f"},
    },
    "🎓 Education": {
        "Schools per 100k":           {"fmt": "{:.0f}",  "color": "#9b59b6"},
        "College Enrollment Rate (%)":{"fmt": "{:.1f}%", "color": "#3498db"},
    },
    "🌾 Agriculture": {
        "Crop Production (Million Tonnes)": {"fmt": "{:.1f}MT", "color": "#27ae60"},
        "Irrigated Land (%)":               {"fmt": "{:.1f}%",  "color": "#16a085"},
    }
}

ALL_METRICS = {m: v for cat in CATEGORIES.values() for m, v in cat.items()}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #0d1117; color: #e6edf3; }

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 1.5rem 1rem; max-width: 100%; }

/* page title */
.page-title {
    font-size: 1.6rem; font-weight: 700; color: #58a6ff;
    margin-bottom: 0; letter-spacing: -.3px;
}
.page-sub { font-size: .82rem; color: #8b949e; margin-bottom: 1rem; }

/* metric cards */
.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.metric-card .label { font-size: .68rem; text-transform: uppercase; letter-spacing: 1px; color: #8b949e; }
.metric-card .value { font-size: 1.5rem; font-weight: 700; color: #f0f6fc; line-height: 1.2; }
.metric-card .delta { font-size: .72rem; color: #3fb950; margin-top: 2px; }

/* info panel */
.info-panel {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 18px;
}
.info-panel h2 {
    font-size: 1.15rem; font-weight: 700;
    color: #58a6ff; margin: 0 0 4px;
}
.info-panel .sub { font-size: .75rem; color: #8b949e; margin-bottom: 14px; }

/* stat rows inside panel */
.stat-row {
    display: flex; justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid #21262d;
    font-size: .82rem;
}
.stat-row:last-child { border-bottom: none; }
.stat-row .sname { color: #8b949e; }
.stat-row .sval  { font-weight: 600; color: #f0f6fc; }

/* rank badge */
.rank-badge {
    display: inline-block;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: .68rem;
    color: #8b949e;
    margin-left: 6px;
}

/* section headers */
.section-hdr {
    font-size: .72rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1px;
    color: #484f58; margin: 14px 0 6px;
}

/* chart container */
.chart-wrap {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 16px;
    margin-top: 10px;
}

/* selectbox and radio styling override */
div[data-baseweb="select"] > div { background: #21262d !important; border-color: #30363d !important; color: #e6edf3 !important; }
div[data-baseweb="radio"] label { color: #e6edf3 !important; }

.stSelectbox label, .stRadio label { color: #8b949e !important; font-size: .78rem !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "selected_state" not in st.session_state:
    st.session_state.selected_state = "Maharashtra"
if "selected_metric" not in st.session_state:
    st.session_state.selected_metric = "Population (Millions)"

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">🗺️ India State Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Hover over states to zoom · Click to explore · Color-coded by your chosen metric</div>', unsafe_allow_html=True)

# ── LAYOUT: metric picker row ─────────────────────────────────────────────────
cat_col, metric_col, _ = st.columns([2, 3, 3])
with cat_col:
    chosen_cat = st.selectbox("Category", list(CATEGORIES.keys()), label_visibility="collapsed")
with metric_col:
    chosen_metric = st.selectbox("Metric", list(CATEGORIES[chosen_cat].keys()), label_visibility="collapsed")

st.session_state.selected_metric = chosen_metric
metric_cfg = ALL_METRICS[chosen_metric]

# ── COLOR SCALE for choropleth ────────────────────────────────────────────────
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def make_color_scale(base_hex, n=10):
    r, g, b = hex_to_rgb(base_hex)
    return [
        f"rgb({int(20 + (r-20)*i/(n-1))},{int(20 + (g-20)*i/(n-1))},{int(20 + (b-20)*i/(n-1))})"
        for i in range(n)
    ]

def value_to_color(val, min_val, max_val, base_hex):
    colors = make_color_scale(base_hex)
    if max_val == min_val:
        return colors[5]
    idx = int((val - min_val) / (max_val - min_val) * (len(colors) - 1))
    return colors[max(0, min(idx, len(colors)-1))]

# ── BUILD INTERACTIVE SVG ─────────────────────────────────────────────────────
def build_svg(svg_src, metric, selected_state_name, color_mode):
    col_data = df.set_index("State")[metric]
    min_v, max_v = col_data.min(), col_data.max()
    base_color = metric_cfg["color"]

    # map state ID -> (color, name, value)
    state_colors = {}
    for _, row in df.iterrows():
        sid = row["ID"]
        if color_mode == "Manual" and sid in st.session_state.manual_colors:
            c = st.session_state.manual_colors[sid]
        elif color_mode == "By Metric":
            c = value_to_color(row[metric], min_v, max_v, base_color)
        else:
            c = st.session_state.manual_colors.get(sid, "#4a8c5c")
        state_colors[sid] = (c, row["State"], row[metric])

    # inject JS data for tooltips
    js_data = {}
    for _, row in df.iterrows():
        js_data[row["ID"]] = {m: float(row[m]) for m in ALL_METRICS}
        js_data[row["ID"]]["__name__"] = row["State"]

    fmt = metric_cfg["fmt"]

    # Patch every <path ...> or <circle ...> tag that has an id="IN.." attribute
    # (attribute order in the source SVG is not fixed, so search the whole tag)
    TAG_RE = re.compile(r'<(path|circle)\b([^>]*?)/?>')

    def patch_tag(m):
        tag, attrs = m.group(1), m.group(2)
        id_match = re.search(r'id="([^"]+)"', attrs)
        if not id_match:
            return m.group(0)
        sid = id_match.group(1)
        if sid not in state_colors:
            return m.group(0)

        color, sname, val = state_colors[sid]
        is_sel = (sname == selected_state_name)
        stroke = '#58a6ff' if is_sel else '#ffffff'
        sw = '2.5' if is_sel else '0.5'

        # strip any pre-existing style/fill attrs to avoid duplicates, keep the rest (e.g. name, d)
        attrs_clean = re.sub(r'\sstyle="[^"]*"', '', attrs)
        attrs_clean = re.sub(r'\sfill="[^"]*"', '', attrs_clean)

        return (f'<{tag} class="state"{attrs_clean} '
                f'style="fill:{color};stroke:{stroke};stroke-width:{sw}" '
                f'onclick="selectState(\'{sid}\',\'{sname}\')">')

    patched = TAG_RE.sub(patch_tag, svg_src)

    html = f"""
<div style="position:relative;width:100%;height:520px;background:#161b22;border-radius:14px;border:1px solid #30363d;overflow:hidden;">
  <div id="map-wrap" style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;padding:16px;">
    {patched}
  </div>

  <!-- Tooltip -->
  <div id="tip" style="position:absolute;display:none;background:#21262dee;color:#f0f6fc;padding:6px 12px;
       border-radius:8px;font-size:.78rem;pointer-events:none;border:1px solid #30363d;
       box-shadow:0 4px 12px #0008;white-space:nowrap;z-index:10;font-family:Inter,sans-serif;">
  </div>

  <!-- Legend -->
  <div style="position:absolute;bottom:14px;left:14px;background:#21262dcc;border:1px solid #30363d;
       border-radius:10px;padding:8px 12px;font-size:.68rem;color:#8b949e;font-family:Inter,sans-serif;">
    <div style="font-weight:600;color:#e6edf3;margin-bottom:5px;">{chosen_metric if color_mode=="By Metric" else "Manual Colors"}</div>
    {"" if color_mode != "By Metric" else f'''<div style="display:flex;align-items:center;gap:6px;">
      <span>{fmt.format(min_v)}</span>
      <div style="width:80px;height:8px;border-radius:4px;
           background:linear-gradient(to right, rgb(20,20,20), {base_color});"></div>
      <span>{fmt.format(max_v)}</span>
    </div>'''}
  </div>
</div>

<style>
  .state {{
    cursor:pointer;
    transition: transform .22s cubic-bezier(.34,1.56,.64,1), filter .22s ease;
    transform-box: fill-box;
    transform-origin: center;
  }}
  .state:hover {{
    transform: scale(1.07);
    filter: brightness(1.4) drop-shadow(0 0 8px rgba(88,166,255,.6));
  }}
</style>

<script>
const STATE_DATA = {json.dumps(js_data)};
const SELECTED_METRIC = "{metric}";

const tip = document.getElementById('tip');
const mapWrap = document.getElementById('map-wrap');

document.querySelectorAll('.state').forEach(el => {{
  el.addEventListener('mouseenter', e => {{
    const sid = el.id;
    const d = STATE_DATA[sid];
    if (!d) return;
    const val = d[SELECTED_METRIC];
    tip.innerHTML = '<b>' + d.__name__ + '</b><br>' + SELECTED_METRIC + ': <b>' + (val !== undefined ? val.toLocaleString() : 'N/A') + '</b>';
    tip.style.display = 'block';
  }});
  el.addEventListener('mousemove', e => {{
    const rect = mapWrap.getBoundingClientRect();
    tip.style.left = (e.clientX - rect.left + 12) + 'px';
    tip.style.top  = (e.clientY - rect.top  - 36) + 'px';
  }});
  el.addEventListener('mouseleave', () => {{ tip.style.display = 'none'; }});
}});

function selectState(sid, name) {{
  document.querySelectorAll('.state').forEach(p => {{
    p.style.stroke = '#ffffff';
    p.style.strokeWidth = '0.5';
  }});
  const el = document.getElementById(sid);
  if (el) {{ el.style.stroke = '#58a6ff'; el.style.strokeWidth = '2.5'; }}
}}
</script>
"""
    return html

# ── MAIN LAYOUT ───────────────────────────────────────────────────────────────
import streamlit.components.v1 as components

left_col, right_col = st.columns([3, 2], gap="medium")

with right_col:
    st.session_state.color_mode = st.radio(
        "Map coloring",
        ["By Metric", "Manual"],
        horizontal=True,
        index=0 if st.session_state.color_mode == "By Metric" else 1
    )

with left_col:
    svg_html = build_svg(svg_raw, chosen_metric, st.session_state.selected_state, st.session_state.color_mode)
    components.html(svg_html, height=540, scrolling=False)



with right_col:
    sel = st.session_state.selected_state
    row = df[df["State"] == sel].iloc[0]

    # ── State selector dropdown
    state_choice = st.selectbox(
        "Select a State / UT",
        df["State"].sort_values().tolist(),
        index=df["State"].sort_values().tolist().index(sel)
    )
    if state_choice != sel:
        st.session_state.selected_state = state_choice
        st.rerun()

    # ── Manual color picker for the selected state
    sel_id = row["ID"]
    pick_col, apply_col, reset_col = st.columns([2, 2, 1])
    with pick_col:
        picked_color = st.color_picker(
            "Pick color",
            value=st.session_state.manual_colors.get(sel_id, "#4a8c5c"),
            label_visibility="collapsed"
        )
    with apply_col:
        if st.button("🎨 Apply to " + sel.split(",")[0][:14], use_container_width=True):
            st.session_state.manual_colors[sel_id] = picked_color
            st.session_state.color_mode = "Manual"
            st.rerun()
    with reset_col:
        if st.button("↺", use_container_width=True, help="Reset this state's color"):
            st.session_state.manual_colors.pop(sel_id, None)
            st.rerun()

    if st.session_state.manual_colors:
        if st.button("Clear all manual colors", use_container_width=True):
            st.session_state.manual_colors = {}
            st.rerun()

    # ── Info panel
    st.markdown(f"""
    <div class="info-panel">
      <h2>{sel}</h2>
      <div class="sub">State ID: {row['ID']}</div>

      <div class="section-hdr">📊 Demographics</div>
      <div class="stat-row"><span class="sname">Population</span><span class="sval">{row['Population (Millions)']:.1f}M</span></div>
      <div class="stat-row"><span class="sname">Area</span><span class="sval">{row['Area (1000 km²)']:.1f}k km²</span></div>
      <div class="stat-row"><span class="sname">Literacy Rate</span><span class="sval">{row['Literacy Rate (%)']:.1f}%</span></div>
      <div class="stat-row"><span class="sname">Sex Ratio</span><span class="sval">{row['Sex Ratio (F per 1000 M)']:.0f} F/1000M</span></div>

      <div class="section-hdr">💰 Economy</div>
      <div class="stat-row"><span class="sname">GDP</span><span class="sval">₹{row['GDP (Billion ₹)']:.0f}B</span></div>
      <div class="stat-row"><span class="sname">Per Capita Income</span><span class="sval">₹{row['Per Capita Income (₹ Thousands)']:.0f}k</span></div>
      <div class="stat-row"><span class="sname">Unemployment</span><span class="sval">{row['Unemployment Rate (%)']:.1f}%</span></div>

      <div class="section-hdr">🏥 Health</div>
      <div class="stat-row"><span class="sname">Hospitals/100k</span><span class="sval">{row['Hospitals per 100k']:.1f}</span></div>
      <div class="stat-row"><span class="sname">Infant Mortality</span><span class="sval">{row['Infant Mortality Rate']:.0f}</span></div>

      <div class="section-hdr">🎓 Education</div>
      <div class="stat-row"><span class="sname">Schools/100k</span><span class="sval">{row['Schools per 100k']:.0f}</span></div>
      <div class="stat-row"><span class="sname">College Enrollment</span><span class="sval">{row['College Enrollment Rate (%)']:.1f}%</span></div>

      <div class="section-hdr">🌾 Agriculture</div>
      <div class="stat-row"><span class="sname">Crop Production</span><span class="sval">{row['Crop Production (Million Tonnes)']:.1f} MT</span></div>
      <div class="stat-row"><span class="sname">Irrigated Land</span><span class="sval">{row['Irrigated Land (%)']:.1f}%</span></div>
    </div>
    """, unsafe_allow_html=True)

# ── CHARTS ROW ────────────────────────────────────────────────────────────────
st.markdown("---")
chart_col1, chart_col2, chart_col3 = st.columns(3)

# Top 10 bar chart
with chart_col1:
    top10 = df.nlargest(10, chosen_metric)[["State", chosen_metric]]
    fig = px.bar(
        top10, x=chosen_metric, y="State", orientation='h',
        title=f"Top 10 States — {chosen_metric}",
        color=chosen_metric,
        color_continuous_scale=[[0, "#21262d"], [1, metric_cfg["color"]]],
    )
    fig.update_layout(
        plot_bgcolor='#161b22', paper_bgcolor='#161b22',
        font_color='#8b949e', title_font_color='#e6edf3',
        coloraxis_showscale=False,
        margin=dict(l=0,r=0,t=36,b=0),
        yaxis=dict(categoryorder='total ascending'),
        height=320
    )
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)

# Radar chart for selected state
with chart_col2:
    radar_metrics = [
        "Literacy Rate (%)", "Hospitals per 100k",
        "College Enrollment Rate (%)", "Irrigated Land (%)",
        "Per Capita Income (₹ Thousands)"
    ]
    # Normalize 0-100
    def normalize(col):
        return (df[col] - df[col].min()) / (df[col].max() - df[col].min()) * 100

    sel_row = df[df["State"] == st.session_state.selected_state].iloc[0]
    vals = [normalize(m)[df["State"] == st.session_state.selected_state].values[0] for m in radar_metrics]
    labels = ["Literacy", "Health", "Education", "Irrigation", "Income"]

    fig2 = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]], theta=labels + [labels[0]],
        fill='toself',
        fillcolor=metric_cfg["color"] + "44",
        line_color=metric_cfg["color"],
        name=st.session_state.selected_state
    ))
    fig2.update_layout(
        polar=dict(
            bgcolor='#21262d',
            radialaxis=dict(visible=True, range=[0,100], gridcolor='#30363d', color='#484f58'),
            angularaxis=dict(gridcolor='#30363d', color='#8b949e')
        ),
        plot_bgcolor='#161b22', paper_bgcolor='#161b22',
        font_color='#8b949e',
        title=dict(text=f"Profile — {st.session_state.selected_state}", font_color='#e6edf3'),
        showlegend=False,
        margin=dict(l=30,r=30,t=40,b=10),
        height=320
    )
    st.plotly_chart(fig2, use_container_width=True)

# Distribution histogram
with chart_col3:
    fig3 = px.histogram(
        df, x=chosen_metric, nbins=12,
        title=f"Distribution — {chosen_metric}",
        color_discrete_sequence=[metric_cfg["color"]]
    )
    # Add vertical line for selected state
    sel_val = df[df["State"] == st.session_state.selected_state][chosen_metric].values[0]
    fig3.add_vline(x=sel_val, line_dash="dash", line_color="#58a6ff",
                   annotation_text=st.session_state.selected_state,
                   annotation_font_color="#58a6ff")
    fig3.update_layout(
        plot_bgcolor='#161b22', paper_bgcolor='#161b22',
        font_color='#8b949e', title_font_color='#e6edf3',
        margin=dict(l=0,r=0,t=36,b=0),
        height=320
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── DATA TABLE ────────────────────────────────────────────────────────────────
with st.expander("📋 View Full Data Table"):
    display_df = df.drop(columns=["ID"]).set_index("State")
    st.dataframe(
        display_df.style.highlight_max(color="#1e3a2f").highlight_min(color="#3a1e1e"),
        use_container_width=True,
        height=400
    )
