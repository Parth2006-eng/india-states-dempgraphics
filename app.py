import streamlit as st
import pandas as pd
import json, re
import streamlit.components.v1 as components

st.set_page_config(page_title="India Map", page_icon="🗺️", layout="wide", initial_sidebar_state="collapsed")

STATES = [
    ("INAN","Andaman and Nicobar"),("INAP","Andhra Pradesh"),("INAR","Arunachal Pradesh"),
    ("INAS","Assam"),("INBR","Bihar"),("INCH","Chandigarh"),("INCT","Chhattisgarh"),
    ("INDH","Dādra and Nagar Haveli and Damān and Diu"),("INDL","Delhi"),("INGA","Goa"),
    ("INGJ","Gujarat"),("INHR","Haryana"),("INHP","Himachal Pradesh"),
    ("INJK","Jammu and Kashmir"),("INJH","Jharkhand"),("INKA","Karnataka"),
    ("INKL","Kerala"),("INLA","Ladakh"),("INLD","Lakshadweep"),("INMP","Madhya Pradesh"),
    ("INMH","Maharashtra"),("INMN","Manipur"),("INML","Meghalaya"),("INMZ","Mizoram"),
    ("INNL","Nagaland"),("INOR","Odisha"),("INPY","Puducherry"),("INPB","Punjab"),
    ("INRJ","Rajasthan"),("INSK","Sikkim"),("INTN","Tamil Nadu"),("INTG","Telangana"),
    ("INTR","Tripura"),("INUP","Uttar Pradesh"),("INUT","Uttarakhand"),("INWB","West Bengal"),
]
ID_TO_NAME = {s:n for s,n in STATES}
NAME_TO_ID = {n:s for s,n in STATES}
UTS = {'INDL','INCH','INPY','INDH','INLD','INAN','INLA','INJK'}

DEFAULT_COLORS = {
    "INJK":"#7eb8d4","INLA":"#a8d8ea","INHP":"#68b0ab","INPB":"#8fc0a9",
    "INCH":"#fad4c0","INHR":"#f9b5ac","INUP":"#ee7674","INUT":"#ef9a9a",
    "INAR":"#b8bedd","INAS":"#c9d4e8","INMN":"#dce8f0","INML":"#b8d8d8",
    "INMZ":"#a2c4c9","INNL":"#889fad","INTR":"#c4a4c4","INSK":"#d4b8e0",
    "INBR":"#f2c87e","INJH":"#f4a261","INWB":"#e76f51","INOR":"#e9c46a",
    "INGJ":"#90be6d","INRJ":"#57cc99","INMP":"#38a3a5","INCT":"#22577a",
    "INMH":"#c77dff","INGA":"#e0aaff","INKA":"#ff9f1c","INKL":"#2ec4b6",
    "INTN":"#ff6b6b","INTG":"#ffd166","INAP":"#06d6a0","INDL":"#ef476f",
    "INPY":"#118ab2","INDH":"#ffd60a","INLD":"#80b918","INAN":"#c9ada7",
}

BUILTIN_DATA = {
    "INAN":{"Population":"0.38 M","Capital":"Port Blair","Area":"8,249 km²","Literacy":"86.3%","Language":"Hindi, Bengali, Tamil"},
    "INAP":{"Population":"49.4 M","Capital":"Amaravati","Area":"1,62,975 km²","GDP":"₹10.3 T","Literacy":"67.4%","Language":"Telugu"},
    "INAR":{"Population":"1.38 M","Capital":"Itanagar","Area":"83,743 km²","Literacy":"66.9%","Language":"English, Nyishi, Bengali"},
    "INAS":{"Population":"31.2 M","Capital":"Dispur","Area":"78,438 km²","GDP":"₹4.5 T","Literacy":"73.2%","Language":"Assamese"},
    "INBR":{"Population":"104.1 M","Capital":"Patna","Area":"94,163 km²","GDP":"₹8.5 T","Literacy":"63.8%","Language":"Hindi, Maithili"},
    "INCH":{"Population":"1.06 M","Capital":"Chandigarh","Area":"114 km²","Literacy":"86.4%","Language":"Hindi, Punjabi"},
    "INCT":{"Population":"25.5 M","Capital":"Raipur","Area":"1,35,192 km²","GDP":"₹4.0 T","Literacy":"71.0%","Language":"Hindi, Chhattisgarhi"},
    "INDH":{"Population":"0.59 M","Capital":"Daman","Area":"603 km²","Literacy":"77.7%","Language":"Gujarati, Hindi"},
    "INDL":{"Population":"16.8 M","Capital":"New Delhi","Area":"1,484 km²","GDP":"₹9.8 T","Literacy":"86.3%","Language":"Hindi, English, Punjabi"},
    "INGA":{"Population":"1.46 M","Capital":"Panaji","Area":"3,702 km²","GDP":"₹920 B","Literacy":"88.7%","Language":"Konkani, English"},
    "INGJ":{"Population":"60.4 M","Capital":"Gandhinagar","Area":"1,96,024 km²","GDP":"₹21.8 T","Literacy":"79.3%","Language":"Gujarati"},
    "INHR":{"Population":"25.4 M","Capital":"Chandigarh","Area":"44,212 km²","GDP":"₹10.1 T","Literacy":"76.6%","Language":"Hindi, Haryanvi"},
    "INHP":{"Population":"6.86 M","Capital":"Shimla","Area":"55,673 km²","Literacy":"83.8%","Language":"Hindi, Pahari"},
    "INJK":{"Population":"12.5 M","Capital":"Srinagar / Jammu","Area":"42,241 km²","Literacy":"68.7%","Language":"Kashmiri, Dogri, Urdu"},
    "INJH":{"Population":"33.0 M","Capital":"Ranchi","Area":"79,716 km²","GDP":"₹4.4 T","Literacy":"67.6%","Language":"Hindi, Santali"},
    "INKA":{"Population":"61.1 M","Capital":"Bengaluru","Area":"1,91,791 km²","GDP":"₹23.6 T","Literacy":"75.6%","Language":"Kannada"},
    "INKL":{"Population":"33.4 M","Capital":"Thiruvananthapuram","Area":"38,852 km²","GDP":"₹11.2 T","Literacy":"94.0%","Language":"Malayalam"},
    "INLA":{"Population":"0.27 M","Capital":"Leh","Area":"59,146 km²","Literacy":"77.7%","Language":"Ladakhi, Hindi, Urdu"},
    "INLD":{"Population":"0.07 M","Capital":"Kavaratti","Area":"32 km²","Literacy":"92.3%","Language":"Malayalam"},
    "INMP":{"Population":"72.6 M","Capital":"Bhopal","Area":"3,08,252 km²","GDP":"₹13.9 T","Literacy":"70.6%","Language":"Hindi"},
    "INMH":{"Population":"112.4 M","Capital":"Mumbai","Area":"3,07,713 km²","GDP":"₹39.5 T","Literacy":"82.9%","Language":"Marathi"},
    "INMN":{"Population":"2.86 M","Capital":"Imphal","Area":"22,327 km²","Literacy":"79.9%","Language":"Meitei, English"},
    "INML":{"Population":"2.97 M","Capital":"Shillong","Area":"22,429 km²","Literacy":"75.5%","Language":"Khasi, Garo, English"},
    "INMZ":{"Population":"1.09 M","Capital":"Aizawl","Area":"21,081 km²","Literacy":"91.6%","Language":"Mizo, English"},
    "INNL":{"Population":"1.98 M","Capital":"Kohima","Area":"16,579 km²","Literacy":"80.1%","Language":"English, Nagamese"},
    "INOR":{"Population":"41.97 M","Capital":"Bhubaneswar","Area":"1,55,707 km²","GDP":"₹8.1 T","Literacy":"73.5%","Language":"Odia"},
    "INPY":{"Population":"1.24 M","Capital":"Puducherry","Area":"479 km²","Literacy":"86.6%","Language":"Tamil, French, Telugu"},
    "INPB":{"Population":"27.7 M","Capital":"Chandigarh","Area":"50,362 km²","GDP":"₹7.1 T","Literacy":"76.7%","Language":"Punjabi"},
    "INRJ":{"Population":"68.5 M","Capital":"Jaipur","Area":"3,42,239 km²","GDP":"₹15.6 T","Literacy":"67.1%","Language":"Hindi, Rajasthani"},
    "INSK":{"Population":"0.61 M","Capital":"Gangtok","Area":"7,096 km²","Literacy":"82.2%","Language":"Nepali, Sikkimese"},
    "INTN":{"Population":"72.1 M","Capital":"Chennai","Area":"1,30,058 km²","GDP":"₹23.5 T","Literacy":"80.3%","Language":"Tamil"},
    "INTG":{"Population":"35.0 M","Capital":"Hyderabad","Area":"1,12,077 km²","GDP":"₹13.8 T","Literacy":"66.4%","Language":"Telugu, Urdu"},
    "INTR":{"Population":"3.67 M","Capital":"Agartala","Area":"10,486 km²","Literacy":"87.8%","Language":"Bengali, Kokborok"},
    "INUP":{"Population":"199.8 M","Capital":"Lucknow","Area":"2,40,928 km²","GDP":"₹25.6 T","Literacy":"67.7%","Language":"Hindi, Urdu"},
    "INUT":{"Population":"10.1 M","Capital":"Dehradun","Area":"53,483 km²","GDP":"₹3.4 T","Literacy":"79.6%","Language":"Hindi, Garhwali"},
    "INWB":{"Population":"91.3 M","Capital":"Kolkata","Area":"88,752 km²","GDP":"₹17.1 T","Literacy":"77.1%","Language":"Bengali"},
}

# session state
for k,v in [("selected",None),("user_data",{}),("custom_colors",{})]:
    if k not in st.session_state: st.session_state[k] = v

@st.cache_data
def load_svg():
    with open("india_clean.svg", encoding="utf-8") as f: return f.read()

def build_map(selected_id, custom_colors, user_data):
    svg = load_svg()
    for sid in ID_TO_NAME:
        color  = custom_colors.get(sid, DEFAULT_COLORS.get(sid, "#95b8a0"))
        is_sel = sid == selected_id
        stroke = "#111" if is_sel else "#fff"
        sw     = "3"    if is_sel else "0.8"
        bright = "filter:brightness(1.12);" if is_sel else ""
        inject = (f' style="fill:{color};stroke:{stroke};stroke-width:{sw};{bright}'
                  f'cursor:pointer;transition:transform .18s cubic-bezier(.34,1.56,.64,1),filter .18s;'
                  f'transform-box:fill-box;transform-origin:center;"'
                  f' class="state" onclick="clickState(\'{sid}\')"')
        svg = re.sub(rf'(id="{re.escape(sid)}"[^>]*)(>)', rf'\1{inject}\2', svg)

    tip_js = {sid: {"name": name, "fields": {**BUILTIN_DATA.get(sid,{}), **user_data.get(sid,{})}}
              for sid, name in ID_TO_NAME.items()}

    return f"""<!DOCTYPE html><html><head>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#f0f4f8;overflow:hidden;}}
#wrap{{width:100%;height:575px;display:flex;align-items:center;justify-content:center;padding:8px;}}
#mc{{width:100%;height:100%;max-width:540px;}}
#mc svg{{filter:drop-shadow(0 4px 22px rgba(0,0,0,.15));}}
.state:hover{{transform:scale(1.06)!important;filter:brightness(1.22) drop-shadow(0 2px 10px rgba(0,0,0,.28))!important;}}
#tip{{position:fixed;display:none;background:#1e293b;color:#f1f5f9;border-radius:10px;
      padding:9px 14px;font:13px/1.6 'Segoe UI',sans-serif;pointer-events:none;
      z-index:999;box-shadow:0 4px 20px rgba(0,0,0,.35);max-width:220px;}}
.tn{{font-weight:700;font-size:14px;border-bottom:1px solid #334155;margin-bottom:5px;padding-bottom:4px;}}
.tr{{font-size:12px;color:#cbd5e1;}}.tr b{{color:#f1f5f9;}}
</style></head><body>
<div id="wrap"><div id="mc">{svg}</div></div>
<div id="tip"></div>
<script>
const DATA={json.dumps(tip_js)};
const tip=document.getElementById('tip');
document.querySelectorAll('.state').forEach(el=>{{
  el.addEventListener('mouseenter',e=>{{
    const d=DATA[el.id];if(!d)return;
    let h=`<div class="tn">${{d.name}}</div>`;
    Object.entries(d.fields).slice(0,6).forEach(([k,v])=>h+=`<div class="tr">${{k}}: <b>${{v}}</b></div>`);
    tip.innerHTML=h;tip.style.display='block';
  }});
  el.addEventListener('mousemove',e=>{{tip.style.left=(e.clientX+16)+'px';tip.style.top=(e.clientY-10)+'px';}});
  el.addEventListener('mouseleave',()=>tip.style.display='none');
}});
function clickState(sid){{
  // Navigate parent to same page with ?sid=XX — Streamlit picks it up via query_params
  const url=new URL(window.parent.location.href);
  url.searchParams.set('sid',sid);
  window.parent.history.pushState({{}},'',url);
  window.parent.dispatchEvent(new PopStateEvent('popstate'));
  // Also try postMessage as fallback
  window.parent.postMessage({{isStreamlitMessage:true,type:'streamlit:setComponentValue',value:sid}},'*');
}}
</script></body></html>"""

# ── STYLES ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1rem 1.5rem;max-width:100%;}
.stApp{background:#f0f4f8;}
[data-testid="stForm"]{border:none!important;padding:0!important;}
.card{background:#fff;border-radius:14px;padding:14px 16px;
      box-shadow:0 2px 10px rgba(0,0,0,.07);margin-bottom:10px;}
.drow{display:flex;justify-content:space-between;align-items:center;
      padding:6px 0;border-bottom:1px solid #f1f5f9;font-size:.82rem;}
.drow:last-child{border-bottom:none;}
.dk{color:#64748b;}.dv{font-weight:600;color:#1e293b;}
</style>
""", unsafe_allow_html=True)

# ── READ CLICK from query param ───────────────────────────────────────────────
qp = st.query_params
if "sid" in qp and qp["sid"] in ID_TO_NAME:
    if qp["sid"] != st.session_state.selected:
        st.session_state.selected = qp["sid"]
        st.query_params.clear()
        st.rerun()

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("## 🗺️ India Map Explorer")
st.markdown('<p style="color:#64748b;font-size:.82rem;margin-top:-8px;margin-bottom:10px;">Hover over any state to preview · Click to select · Add custom data · Pick colors</p>', unsafe_allow_html=True)

map_col, panel_col = st.columns([55,45], gap="medium")

with map_col:
    components.html(build_map(st.session_state.selected,
                              st.session_state.custom_colors,
                              st.session_state.user_data), height=585, scrolling=False)
    st.caption("👆 Click a state on the map — or use the selector on the right")

with panel_col:
    names_sorted = sorted(n for _,n in STATES)
    sel_name = ID_TO_NAME.get(st.session_state.selected,"")
    idx = names_sorted.index(sel_name)+1 if sel_name in names_sorted else 0

    chosen = st.selectbox("🔍 Select State / Union Territory",
                          ["— choose a state —"]+names_sorted, index=idx)
    if chosen != "— choose a state —":
        nid = NAME_TO_ID[chosen]
        if nid != st.session_state.selected:
            st.session_state.selected = nid
            st.rerun()

    st.markdown("---")

    if not st.session_state.selected:
        st.markdown('<div class="card" style="text-align:center;padding:30px;color:#94a3b8;">'
                    '<div style="font-size:2rem;margin-bottom:8px;">👆</div>'
                    '<b style="color:#64748b;">Click any state on the map</b><br>'
                    '<span style="font-size:.78rem;">or use the dropdown above</span></div>',
                    unsafe_allow_html=True)
    else:
        sid   = st.session_state.selected
        sname = ID_TO_NAME[sid]
        color = st.session_state.custom_colors.get(sid, DEFAULT_COLORS.get(sid,"#95b8a0"))

        # header
        st.markdown(f"""<div class="card" style="display:flex;align-items:center;gap:12px;">
          <div style="width:22px;height:22px;border-radius:6px;background:{color};
               box-shadow:0 2px 8px rgba(0,0,0,.2);flex-shrink:0;"></div>
          <div><div style="font-size:1.05rem;font-weight:700;color:#1e293b;">{sname}</div>
               <div style="font-size:.7rem;color:#94a3b8;">{'Union Territory' if sid in UTS else 'State'} · {sid}</div></div>
        </div>""", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📊 Data", "✏️ Add Data", "🎨 Color"])

        with tab1:
            builtin    = BUILTIN_DATA.get(sid, {})
            user_extra = st.session_state.user_data.get(sid, {})
            if builtin:
                st.markdown('<div style="font-size:.68rem;font-weight:600;color:#94a3b8;'
                            'text-transform:uppercase;letter-spacing:.8px;margin-bottom:5px;">General Info</div>',
                            unsafe_allow_html=True)
                rows = "".join(f'<div class="drow"><span class="dk">{k}</span>'
                               f'<span class="dv">{v}</span></div>' for k,v in builtin.items())
                st.markdown(f'<div class="card">{rows}</div>', unsafe_allow_html=True)
            if user_extra:
                st.markdown('<div style="font-size:.68rem;font-weight:600;color:#94a3b8;'
                            'text-transform:uppercase;letter-spacing:.8px;margin-bottom:5px;">Your Data</div>',
                            unsafe_allow_html=True)
                rows2 = "".join(f'<div class="drow"><span class="dk">{k}</span>'
                                f'<span class="dv">{v}</span></div>' for k,v in user_extra.items())
                st.markdown(f'<div class="card">{rows2}</div>', unsafe_allow_html=True)

        with tab2:
            with st.form(key=f"add_{sid}", clear_on_submit=True):
                c1,c2 = st.columns(2)
                fname = c1.text_input("Field", placeholder="e.g. Tourists/year")
                fval  = c2.text_input("Value", placeholder="e.g. 4.2 Million")
                if st.form_submit_button("➕ Add", use_container_width=True, type="primary"):
                    if fname.strip():
                        st.session_state.user_data.setdefault(sid,{})[fname.strip()] = fval.strip()
                        st.rerun()
            ue = st.session_state.user_data.get(sid,{})
            if ue:
                to_del = st.selectbox("Remove field", ["—"]+list(ue.keys()))
                c1,c2 = st.columns(2)
                if to_del!="—" and c1.button("🗑 Remove", use_container_width=True):
                    del st.session_state.user_data[sid][to_del]
                    if not st.session_state.user_data[sid]: del st.session_state.user_data[sid]
                    st.rerun()
                if c2.button("Clear All", use_container_width=True):
                    st.session_state.user_data.pop(sid,None); st.rerun()
            else:
                st.caption("No custom fields yet.")

        with tab3:
            new_color = st.color_picker("Pick color for " + sname, value=color)
            p1,p2 = st.columns(2)
            if p1.button("✅ Apply", use_container_width=True, type="primary"):
                st.session_state.custom_colors[sid] = new_color; st.rerun()
            if p2.button("↺ Reset", use_container_width=True):
                st.session_state.custom_colors.pop(sid,None); st.rerun()

            st.markdown("**Quick presets**")
            PRESETS = ["#ef476f","#ffd166","#06d6a0","#118ab2","#c77dff",
                       "#ff9f1c","#e76f51","#57cc99","#4cc9f0","#f72585","#3a86ff","#2d6a4f"]
            cols = st.columns(6)
            for i,pc in enumerate(PRESETS):
                with cols[i%6]:
                    st.markdown(f'<div style="width:26px;height:26px;border-radius:50%;'
                                f'background:{pc};margin:0 auto 2px;border:2px solid #fff;'
                                f'box-shadow:0 1px 4px rgba(0,0,0,.2);"></div>', unsafe_allow_html=True)
                    if st.button("·", key=f"p_{sid}_{i}", help=f"Apply {pc}", use_container_width=True):
                        st.session_state.custom_colors[sid] = pc; st.rerun()

# summary
rows = [{"State":ID_TO_NAME.get(s,s),"Field":k,"Value":v}
        for s,flds in st.session_state.user_data.items() for k,v in flds.items()]
if rows:
    st.markdown("---")
    st.markdown("#### 📋 All Custom Data")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
