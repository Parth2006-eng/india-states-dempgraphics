import streamlit as st
import pandas as pd
import json
import re
import streamlit.components.v1 as components

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── STATE MASTER LIST ─────────────────────────────────────────────────────────
STATES = [
    ("INAN", "Andaman and Nicobar"),
    ("INAP", "Andhra Pradesh"),
    ("INAR", "Arunachal Pradesh"),
    ("INAS", "Assam"),
    ("INBR", "Bihar"),
    ("INCH", "Chandigarh"),
    ("INCT", "Chhattisgarh"),
    ("INDH", "Dādra and Nagar Haveli and Damān and Diu"),
    ("INDL", "Delhi"),
    ("INGA", "Goa"),
    ("INGJ", "Gujarat"),
    ("INHR", "Haryana"),
    ("INHP", "Himachal Pradesh"),
    ("INJK", "Jammu and Kashmir"),
    ("INJH", "Jharkhand"),
    ("INKA", "Karnataka"),
    ("INKL", "Kerala"),
    ("INLA", "Ladakh"),
    ("INLD", "Lakshadweep"),
    ("INMP", "Madhya Pradesh"),
    ("INMH", "Maharashtra"),
    ("INMN", "Manipur"),
    ("INML", "Meghalaya"),
    ("INMZ", "Mizoram"),
    ("INNL", "Nagaland"),
    ("INOR", "Odisha"),
    ("INPY", "Puducherry"),
    ("INPB", "Punjab"),
    ("INRJ", "Rajasthan"),
    ("INSK", "Sikkim"),
    ("INTN", "Tamil Nadu"),
    ("INTG", "Telangana"),
    ("INTR", "Tripura"),
    ("INUP", "Uttar Pradesh"),
    ("INUT", "Uttarakhand"),
    ("INWB", "West Bengal"),
]
ID_TO_NAME = {sid: name for sid, name in STATES}
NAME_TO_ID = {name: sid for sid, name in STATES}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "selected" not in st.session_state:
    st.session_state.selected = None          # currently clicked state ID
if "user_data" not in st.session_state:
    # { "INMH": { "field": "value", ... }, ... }
    st.session_state.user_data = {}
if "last_click" not in st.session_state:
    st.session_state.last_click = None

# ── LOAD SVG ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_svg():
    with open("india_clean.svg", encoding="utf-8") as f:
        return f.read()

svg_raw = load_svg()

# ── STATE COLORS ──────────────────────────────────────────────────────────────
# Nice default palette — distinct colors per region
DEFAULT_COLORS = {
    "INJK": "#7eb8d4", "INLA": "#a8d8ea",                          # North
    "INHP": "#68b0ab", "INPB": "#8fc0a9", "INCH": "#c8d5b9",
    "INHR": "#fad4c0", "INUP": "#f9b5ac", "INUT": "#ee7674",
    "INAR": "#b8bedd", "INAS": "#c9d4e8", "INMN": "#dce8f0",       # NE
    "INML": "#b8d8d8", "INMZ": "#a2c4c9", "INNL": "#889fad",
    "INTR": "#c4a4c4", "INSK": "#d4b8e0",
    "INBR": "#f2c87e", "INJH": "#f4a261", "INWB": "#e76f51",       # East
    "INOR": "#e9c46a",
    "INGJ": "#90be6d", "INRJ": "#57cc99", "INMP": "#38a3a5",       # Central/West
    "INCT": "#22577a",
    "INMH": "#c77dff", "INGA": "#e0aaff",                           # West/Goa
    "INKA": "#ff9f1c", "INKL": "#2ec4b6", "INTN": "#ff6b6b",       # South
    "INTG": "#ffd166", "INAP": "#06d6a0",
    "INDL": "#ef476f", "INPY": "#118ab2",                           # UTs
    "INDH": "#ffd60a", "INLD": "#80b918",
    "INAN": "#c9ada7",
}

# ── BUILD THE SVG HTML ────────────────────────────────────────────────────────
def build_map(svg_src, selected_id, user_data):
    TAG_RE = re.compile(r'<(path|circle)\b([^>]*?)/?>', re.DOTALL)

    def patch(m):
        tag, attrs = m.group(1), m.group(2)
        id_m = re.search(r'id="([^"]+)"', attrs)
        if not id_m:
            return m.group(0)
        sid = id_m.group(1)
        if sid not in ID_TO_NAME:
            return m.group(0)

        name = ID_TO_NAME[sid]
        color = DEFAULT_COLORS.get(sid, "#95b8a0")
        is_sel = (sid == selected_id)
        stroke_col = "#ffffff" if not is_sel else "#1a1a1a"
        stroke_w   = "0.8"    if not is_sel else "2.5"
        bright     = "filter:brightness(1.15);" if is_sel else ""

        return (
            f'<{tag} id="{sid}" class="state" data-name="{name}" '
            f'style="fill:{color};stroke:{stroke_col};stroke-width:{stroke_w};'
            f'cursor:pointer;transition:transform .2s cubic-bezier(.34,1.56,.64,1),'
            f'filter .2s;transform-box:fill-box;transform-origin:center;{bright}" '
            f'onclick="clickState(\'{sid}\',\'{name}\')">'
        )

    patched = TAG_RE.sub(patch, svg_src)

    # build tooltip data for JS
    tip_data = {}
    for sid, name in ID_TO_NAME.items():
        fields = user_data.get(sid, {})
        tip_data[sid] = {"name": name, "fields": fields}

    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#f0f4f8; font-family:'Segoe UI',sans-serif; }}

  #wrap {{
    width:100%; height:580px;
    display:flex; align-items:center; justify-content:center;
    padding:12px;
  }}

  #map-container {{
    width:100%; height:100%;
    max-width:560px;
    filter: drop-shadow(0 4px 24px rgba(0,0,0,0.13));
  }}

  .state:hover {{
    transform: scale(1.06);
    filter: brightness(1.22) drop-shadow(0 2px 8px rgba(0,0,0,0.25)) !important;
  }}

  /* Tooltip */
  #tip {{
    position:fixed;
    background:#1e293b;
    color:#f1f5f9;
    border-radius:10px;
    padding:8px 13px;
    font-size:13px;
    pointer-events:none;
    display:none;
    z-index:999;
    box-shadow:0 4px 16px rgba(0,0,0,0.3);
    max-width:200px;
    line-height:1.6;
  }}
  #tip .tip-name {{
    font-weight:700;
    font-size:14px;
    border-bottom:1px solid #334155;
    margin-bottom:5px;
    padding-bottom:4px;
  }}
  #tip .tip-row {{
    font-size:12px;
    color:#cbd5e1;
  }}
  #tip .tip-row span {{
    color:#f1f5f9;
    font-weight:600;
  }}
  #tip .tip-empty {{
    font-size:11px;
    color:#64748b;
    font-style:italic;
  }}
</style>
</head>
<body>

<div id="wrap">
  <div id="map-container">{patched}</div>
</div>

<div id="tip"></div>

<script>
const TIP_DATA = {json.dumps(tip_data)};
const tip = document.getElementById('tip');

document.querySelectorAll('.state').forEach(el => {{
  el.addEventListener('mouseenter', e => {{
    const d = TIP_DATA[el.id];
    if (!d) return;
    let html = `<div class="tip-name">${{d.name}}</div>`;
    const keys = Object.keys(d.fields);
    if (keys.length === 0) {{
      html += `<div class="tip-empty">No data added yet</div>`;
    }} else {{
      keys.forEach(k => {{
        html += `<div class="tip-row">${{k}}: <span>${{d.fields[k]}}</span></div>`;
      }});
    }}
    tip.innerHTML = html;
    tip.style.display = 'block';
  }});
  el.addEventListener('mousemove', e => {{
    tip.style.left = (e.clientX + 16) + 'px';
    tip.style.top  = (e.clientY - 10) + 'px';
  }});
  el.addEventListener('mouseleave', () => tip.style.display = 'none');
}});

function clickState(sid, name) {{
  window.parent.postMessage({{isStreamlitMessage: true, type:'streamlit:setComponentValue', value: sid}}, '*');
}}
</script>
</body>
</html>
"""
    return html

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu, footer, header { visibility:hidden; }
  .block-container { padding: 1.2rem 1.5rem; max-width:100%; }
  body, .stApp { background:#f0f4f8; }

  h1 { font-size:1.4rem !important; font-weight:700 !important; color:#1e293b !important; }
  .sub  { color:#64748b; font-size:.82rem; margin-top:-6px; margin-bottom:12px; }

  /* data panel */
  .panel {
    background:#fff;
    border-radius:14px;
    padding:20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-bottom:14px;
  }
  .panel h3 { font-size:.95rem; font-weight:700; color:#1e293b; margin-bottom:2px; }
  .panel .sub2 { font-size:.73rem; color:#94a3b8; margin-bottom:14px; }

  /* data rows */
  .data-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:7px 0; border-bottom:1px solid #f1f5f9;
    font-size:.83rem;
  }
  .data-row:last-child { border-bottom:none; }
  .data-key { color:#64748b; }
  .data-val { font-weight:600; color:#1e293b; }

  /* placeholder */
  .placeholder {
    text-align:center; padding:30px 16px;
    color:#94a3b8; font-size:.82rem;
  }
  .placeholder .icon { font-size:2rem; margin-bottom:8px; }

  div[data-testid="stHorizontalBlock"] { gap: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("## 🗺️ India Map Explorer")
st.markdown('<p class="sub">Click any state or union territory to select it · Add your own data · Hover to preview</p>', unsafe_allow_html=True)

# ── LAYOUT ────────────────────────────────────────────────────────────────────
map_col, data_col = st.columns([3, 2], gap="medium")

# ── MAP ───────────────────────────────────────────────────────────────────────
with map_col:
    map_html = build_map(svg_raw, st.session_state.selected, st.session_state.user_data)
    clicked = components.html(map_html, height=590, scrolling=False)

# ── RIGHT PANEL ───────────────────────────────────────────────────────────────
with data_col:
    # State selector (also lets user click from list)
    names = sorted([name for _, name in STATES])
    sel_name = ID_TO_NAME.get(st.session_state.selected) if st.session_state.selected else None

    chosen = st.selectbox(
        "Select a state / UT",
        ["— click map or choose here —"] + names,
        index=0 if not sel_name else names.index(sel_name) + 1
    )
    if chosen != "— click map or choose here —":
        new_id = NAME_TO_ID[chosen]
        if new_id != st.session_state.selected:
            st.session_state.selected = new_id
            st.rerun()

    st.markdown("---")

    if not st.session_state.selected:
        # Nothing selected yet
        st.markdown("""
        <div class="placeholder">
          <div class="icon">👆</div>
          <b>Click any state on the map</b><br>
          or use the dropdown above<br>to select and view data
        </div>
        """, unsafe_allow_html=True)

    else:
        sid   = st.session_state.selected
        sname = ID_TO_NAME[sid]
        sdata = st.session_state.user_data.get(sid, {})

        # ── State header
        color = DEFAULT_COLORS.get(sid, "#95b8a0")
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
          <div style="width:18px;height:18px;border-radius:5px;background:{color};flex-shrink:0;
               box-shadow:0 2px 6px rgba(0,0,0,0.15);"></div>
          <div style="font-size:1.1rem;font-weight:700;color:#1e293b;">{sname}</div>
          <div style="font-size:.7rem;color:#94a3b8;margin-left:auto;background:#f1f5f9;
               padding:2px 8px;border-radius:20px;">{sid}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Existing data display
        if sdata:
            st.markdown('<div style="font-size:.73rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;">Your Data</div>', unsafe_allow_html=True)
            rows_html = ""
            for k, v in sdata.items():
                rows_html += f'<div class="data-row"><span class="data-key">{k}</span><span class="data-val">{v}</span></div>'
            st.markdown(f'<div class="panel" style="padding:14px 16px;">{rows_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="font-size:.78rem;color:#94a3b8;font-style:italic;
                 background:#f8fafc;border-radius:10px;padding:12px 14px;
                 margin-bottom:12px;">
              No data added yet for this state.
            </div>
            """, unsafe_allow_html=True)

        # ── Add / edit data
        st.markdown('<div style="font-size:.73rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;margin-top:4px;">Add Data</div>', unsafe_allow_html=True)

        with st.form(key=f"form_{sid}", clear_on_submit=True):
            field_name  = st.text_input("Field name",  placeholder="e.g. Population, GDP, Notes…")
            field_value = st.text_input("Value",        placeholder="e.g. 112 Million, ₹8.4T…")
            c1, c2 = st.columns(2)
            with c1:
                submitted = st.form_submit_button("➕ Add", use_container_width=True)
            with c2:
                clear = st.form_submit_button("🗑 Clear all", use_container_width=True, type="secondary")

            if submitted and field_name.strip():
                if sid not in st.session_state.user_data:
                    st.session_state.user_data[sid] = {}
                st.session_state.user_data[sid][field_name.strip()] = field_value.strip()
                st.rerun()

            if clear:
                st.session_state.user_data.pop(sid, None)
                st.rerun()

        # ── Delete individual fields
        if sdata:
            st.markdown('<div style="font-size:.73rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;margin-top:12px;">Remove a field</div>', unsafe_allow_html=True)
            field_to_del = st.selectbox("", ["—"] + list(sdata.keys()), label_visibility="collapsed")
            if field_to_del != "—":
                if st.button(f"Remove '{field_to_del}'", use_container_width=True):
                    del st.session_state.user_data[sid][field_to_del]
                    if not st.session_state.user_data[sid]:
                        del st.session_state.user_data[sid]
                    st.rerun()

# ── FOOTER: summary table ─────────────────────────────────────────────────────
all_entries = []
for sid, fields in st.session_state.user_data.items():
    for k, v in fields.items():
        all_entries.append({"State": ID_TO_NAME.get(sid, sid), "Field": k, "Value": v})

if all_entries:
    st.markdown("---")
    st.markdown("#### 📋 All Data You've Added")
    st.dataframe(
        pd.DataFrame(all_entries),
        use_container_width=True,
        hide_index=True
    )
