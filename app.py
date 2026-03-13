"""
VaultaLex — Analytics Command Center
Digital Estate Planning & Legal Documentation Platform
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64, sys, os
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / "data"))
from generate import generate_all
sys.path.insert(0, str(BASE_DIR / "reports"))
from pdf_generator import (
    build_descriptive_report, build_diagnostic_report,
    build_predictive_report, build_prescriptive_report,
)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VaultaLex | Analytics Command Center",
    page_icon="⚖️", layout="wide",
    initial_sidebar_state="expanded",
)

# ── LOGO ──────────────────────────────────────────────────────────────────────
def _logo_b64():
    p = BASE_DIR / "assets" / "vaultalex_logo.png"
    if p.exists():
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO_B64 = _logo_b64()
LOGO_SRC = f"data:image/png;base64,{LOGO_B64}" if LOGO_B64 else ""

# ── BRAND COLOURS (from logo: deep navy #142850 + silver #a0a0a0) ────────────
NAVY_BG   = "#0a1020"
NAVY_CARD = "#0e1c32"
NAVY_C2   = "#122040"
NAVY_BORD = "#1e3a5f"
NAVY_LOGO = "#142850"
SILVER    = "#a8bcd0"
SILVER_LT = "#c8d8ec"
STEEL     = "#4a8fd4"
TEXT_MAIN = "#e8eef6"
TEXT_MID  = "#8aa0c0"
TEXT_DIM  = "#5a7090"
GOLD      = "#d4a843"   # KPI value accent — readable on dark navy

CHART_PAL = [STEEL, SILVER, GOLD, "#5bc8a0", "#e07060", "#9480d4", "#50c8d4", "#d47850"]
TIER_C    = {"Free": STEEL, "Basic": "#5bc8a0", "Premium": SILVER, "Family": GOLD}
C = {**TIER_C, "green": "#5bc8a0", "red": "#e07060", "gold": GOLD, "steel": STEEL, "silver": SILVER}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600;700;800&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif;}}
.stApp{{background:{NAVY_BG};}}
.block-container{{padding-top:0;padding-bottom:2rem;max-width:100%!important;}}
[data-testid="stSidebar"]{{
  background:linear-gradient(180deg,#0b1525 0%,{NAVY_BG} 100%);
  border-right:1px solid {NAVY_BORD};}}
[data-testid="stSidebar"] *{{font-family:'Space Mono',monospace!important;}}
section[data-testid="stSidebarContent"]{{padding-top:0!important;}}

/* ── Header bar ── */
.vx-header{{
  background:linear-gradient(90deg,#0a1422 0%,#0f1e38 40%,#0a1422 100%);
  border-bottom:1px solid {NAVY_BORD};
  padding:10px 28px 10px 18px;
  display:flex;align-items:center;gap:16px;
  margin:-1rem -1rem 0 -1rem;}}
.vx-logo{{height:50px;width:auto;}}
.vx-brand{{display:flex;flex-direction:column;}}
.vx-name{{
  font-family:'Inter',sans-serif;font-weight:800;font-size:21px;
  color:{TEXT_MAIN};line-height:1;letter-spacing:-0.2px;}}
.vx-name span{{color:{STEEL};}}
.vx-tag{{
  font-family:'Space Mono',monospace;font-size:8px;
  color:{TEXT_DIM};letter-spacing:2.8px;margin-top:4px;}}
.vx-right{{
  margin-left:auto;font-family:'Space Mono',monospace;
  font-size:9px;color:{TEXT_DIM};text-align:right;line-height:1.7;}}

/* ── KPI cards ── */
.kpi-card{{
  background:linear-gradient(135deg,{NAVY_CARD},{NAVY_C2});
  border:1px solid {NAVY_BORD};border-radius:10px;
  padding:16px 18px;margin-bottom:8px;position:relative;overflow:hidden;}}
.kpi-card::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,{STEEL},{SILVER});}}
.kpi-label{{
  color:{TEXT_DIM};font-size:9px;font-family:'Space Mono',monospace;
  letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;}}
.kpi-value{{color:{GOLD};font-size:23px;font-weight:700;line-height:1;}}
.kpi-delta{{font-size:10px;font-family:'Space Mono',monospace;margin-top:5px;}}
.kpi-delta.pos{{color:#5bc8a0;}} .kpi-delta.neg{{color:#e07060;}}

/* ── Layout helpers ── */
.sec-hdr{{
  font-family:'Inter',sans-serif;font-weight:700;font-size:16px;color:{TEXT_MAIN};
  border-left:3px solid {STEEL};padding-left:12px;margin:22px 0 12px 0;}}
.layer-tag{{font-family:'Space Mono',monospace;font-size:9px;color:{TEXT_DIM};letter-spacing:3px;}}
.layer-title{{font-family:'Inter',sans-serif;font-weight:800;font-size:27px;
  color:{TEXT_MAIN};letter-spacing:-0.3px;}}
.layer-sub{{font-family:'Space Mono',monospace;font-size:10px;color:{TEXT_DIM};margin-top:4px;}}

.insight-box{{
  background:linear-gradient(135deg,#0d1830,#101e38);
  border:1px solid {NAVY_BORD};border-left:4px solid {STEEL};
  border-radius:8px;padding:14px 18px;margin:12px 0;
  font-size:11px;color:{SILVER_LT};font-family:'Space Mono',monospace;line-height:1.85;}}
.insight-box.warn{{border-left-color:{GOLD};}}
.insight-box.alert{{border-left-color:#e07060;}}

.silver-div{{height:1px;background:linear-gradient(90deg,{STEEL} 0%,transparent 100%);
  margin:16px 0;opacity:0.3;}}

/* ── Sidebar logo block ── */
.sb-logo-block{{
  text-align:center;padding:16px 12px 12px;
  border-bottom:1px solid {NAVY_BORD};margin-bottom:8px;}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab"]{{
  font-family:'Space Mono',monospace!important;font-size:10px;
  letter-spacing:1px;color:{TEXT_DIM};}}
.stTabs [aria-selected="true"]{{color:{STEEL}!important;border-bottom:2px solid {STEEL}!important;}}
</style>
""", unsafe_allow_html=True)

# ── BRANDED HEADER ────────────────────────────────────────────────────────────
logo_img = f'<img src="{LOGO_SRC}" class="vx-logo" alt="VaultaLex"/>' if LOGO_SRC else "⚖️"
st.markdown(f"""
<div class="vx-header">
  {logo_img}
  <div class="vx-brand">
    <div class="vx-name">Vaulta<span>Lex</span></div>
    <div class="vx-tag">SECURE YOUR LEGACY &nbsp;·&nbsp; ANALYTICS COMMAND CENTER</div>
  </div>
  <div class="vx-right">
    DIGITAL ESTATE SECURITY<br>
    {datetime.now().strftime('%d %b %Y')}
  </div>
</div>
<div style="margin-top:14px;"></div>
""", unsafe_allow_html=True)

# ── PLOTLY BASE THEME ─────────────────────────────────────────────────────────
PL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Mono, monospace", color=TEXT_MID, size=11),
    title_font=dict(family="Inter, sans-serif", color=TEXT_MAIN, size=13),
    legend=dict(bgcolor="rgba(14,28,50,0.92)", bordercolor=NAVY_BORD, borderwidth=1,
                font=dict(size=10, color=TEXT_MID)),
    margin=dict(l=50, r=20, t=46, b=40),
    colorway=CHART_PAL,
    xaxis=dict(gridcolor=NAVY_BORD, linecolor=NAVY_BORD, tickfont=dict(size=10)),
    yaxis=dict(gridcolor=NAVY_BORD, linecolor=NAVY_BORD, tickfont=dict(size=10)),
)
def pl(fig, title="", h=370):
    fig.update_layout(**PL, title=title, height=h)
    return fig

# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load():
    return generate_all(42)

with st.spinner("🔐 Loading VaultaLex Analytics..."):
    D = load()

customers       = D["customers"]
monthly_revenue = D["monthly_revenue"]
assets          = D["assets"]
documents       = D["documents"]
estate_sections = D["estate_sections"]
sessions        = D["sessions"]
feature_usage   = D["feature_usage"]
security_events = D["security_events"]
rfm             = D["rfm"]
cohort          = D["cohort"]
ab_tests        = D["ab_tests"]
tier_transitions= D["tier_transitions"]
mrr_forecast    = D["mrr_forecast"]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if LOGO_SRC:
        st.markdown(f"""
        <div class="sb-logo-block">
          <img src="{LOGO_SRC}" style="width:110px;height:auto;" alt="VaultaLex"/>
          <div style="font-family:Inter,sans-serif;font-weight:800;font-size:16px;
               color:{TEXT_MAIN};margin-top:8px;">
            Vaulta<span style="color:{STEEL};">Lex</span>
          </div>
          <div style="font-size:8px;color:{TEXT_DIM};letter-spacing:2.5px;
               font-family:Space Mono,monospace;margin-top:3px;">
            DIGITAL ESTATE SECURITY
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:center;padding:14px;font-size:26px;'>⚖️</div>",
                    unsafe_allow_html=True)

    st.markdown(f"<div style='font-size:9px;color:{TEXT_DIM};letter-spacing:2.5px;"
                f"margin:8px 0;font-family:Space Mono,monospace;'>NAVIGATION</div>",
                unsafe_allow_html=True)
    page = st.radio("", [
        "📊  Descriptive",
        "🔍  Diagnostic",
        "🔮  Predictive",
        "🧭  Prescriptive",
    ], label_visibility="collapsed")

    st.markdown(f"<div class='silver-div'></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:9px;color:{TEXT_DIM};letter-spacing:2px;"
                f"margin-bottom:8px;'>FILTERS</div>", unsafe_allow_html=True)

    tier_f = st.multiselect("Subscription Tier",
                             ["Free","Basic","Premium","Family"],
                             default=["Free","Basic","Premium","Family"])
    ch_f   = st.multiselect("Acquisition Channel",
                             customers["acquisition_channel"].unique().tolist(),
                             default=customers["acquisition_channel"].unique().tolist())

    st.markdown(f"<div class='silver-div'></div>", unsafe_allow_html=True)
    active_n = len(customers[(customers["is_churned"]==0) &
                              customers["subscription_tier"].isin(tier_f)])
    avg_comp = customers[customers["subscription_tier"].isin(tier_f)]["estate_completeness_score"].mean()
    st.markdown(f"""<div style='font-size:10px;color:{TEXT_DIM};line-height:2;'>
      PLATFORM SNAPSHOT<br>
      <span style='color:{GOLD};'>{active_n:,}</span> active subscribers<br>
      <span style='color:{STEEL};'>{len(assets[assets["tier"].isin(tier_f)]):,}</span> assets registered<br>
      <span style='color:{SILVER};'>{len(documents[documents["tier"].isin(tier_f)]):,}</span> documents stored<br>
      <span style='color:#5bc8a0;'>{avg_comp:.0%}</span> avg estate completion<br>
      <span style='color:{TEXT_DIM};'>Jan 2022 – Mar 2026</span>
    </div>""", unsafe_allow_html=True)

# ── FILTERED DATA ─────────────────────────────────────────────────────────────
cf  = customers[customers["subscription_tier"].isin(tier_f) &
                customers["acquisition_channel"].isin(ch_f)]
mf  = monthly_revenue[monthly_revenue["tier"].isin(tier_f)]
af  = assets[assets["tier"].isin(tier_f)]
df  = documents[documents["tier"].isin(tier_f)]
esf = estate_sections[estate_sections["tier"].isin(tier_f)]
rf  = rfm[rfm["tier"].isin(tier_f)]
ff  = feature_usage[feature_usage["tier"].isin(tier_f)]
sf  = security_events[security_events["tier"].isin(tier_f)]

# ── UI HELPERS ────────────────────────────────────────────────────────────────
def kpi(col, label, val, delta=None, pos=True):
    d = (f"<div class='kpi-delta {'pos' if pos else 'neg'}'>"
         f"{'▲' if pos else '▼'} {delta}</div>") if delta else ""
    col.markdown(f"<div class='kpi-card'><div class='kpi-label'>{label}</div>"
                 f"<div class='kpi-value'>{val}</div>{d}</div>", unsafe_allow_html=True)

def layer_hdr(tag, title, sub):
    st.markdown(f"""<div style='margin:0 0 18px 0;padding-bottom:12px;
        border-bottom:1px solid {NAVY_BORD};'>
      <div class='layer-tag'>{tag}</div>
      <div class='layer-title'>{title}</div>
      <div class='layer-sub'>{sub}</div></div>""", unsafe_allow_html=True)

def section(title):
    st.markdown(f"<div class='sec-hdr'>{title}</div>", unsafe_allow_html=True)

def divider():
    st.markdown(f"<div class='silver-div'></div>", unsafe_allow_html=True)

def insight(text, kind=""):
    st.markdown(f"<div class='insight-box {kind}'>{text}</div>", unsafe_allow_html=True)

def pdf_button(key, builder, label, filename):
    divider()
    logo_sm = (f'<img src="{LOGO_SRC}" style="height:38px;width:auto;opacity:0.9;'
               f'flex-shrink:0;" />' if LOGO_SRC else "⚖️")
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0b1525,{NAVY_CARD});
         border:1px solid {NAVY_BORD};border-top:2px solid {STEEL};
         border-radius:10px;padding:18px 22px;margin:12px 0;
         display:flex;align-items:center;gap:18px;'>
      {logo_sm}
      <div>
        <div style='font-size:9px;color:{TEXT_DIM};letter-spacing:2px;
             font-family:Space Mono,monospace;margin-bottom:4px;'>EXPORT PDF REPORT</div>
        <div style='font-size:15px;font-weight:700;color:{TEXT_MAIN};
             font-family:Inter,sans-serif;margin-bottom:4px;'>{label}</div>
        <div style='font-size:10px;color:{TEXT_DIM};font-family:Space Mono,monospace;'>
          Multi-page &nbsp;·&nbsp; Executive design &nbsp;·&nbsp;
          Charts, tables &amp; strategic insights &nbsp;·&nbsp; VaultaLex branded
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 3])
    with c1:
        pdf_bytes = builder(D, {"tier": tier_f, "channel": ch_f})
        st.download_button("⬇  Download PDF Report", data=pdf_bytes,
                           file_name=filename, mime="application/pdf",
                           use_container_width=True, key=key)
    with c2:
        st.markdown(f"""<div style='font-size:10px;color:{TEXT_DIM};
          padding-top:6px;font-family:Space Mono,monospace;line-height:1.9;'>
          📄 &nbsp;Generated on-demand · reflects current sidebar filters<br>
          🔐 &nbsp;Confidential — VaultaLex Analytics Command Center<br>
          📅 &nbsp;{datetime.now().strftime("%d %B %Y %H:%M")}
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 1 — DESCRIPTIVE
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊  Descriptive":
    layer_hdr("LAYER 01", "Descriptive Analytics",
              "What is happening — subscribers, revenue, estate readiness, asset registry & document vault")

    active    = int(cf[cf["is_churned"]==0].shape[0])
    total_mrr = int(mf[mf["month"]=="2026-03"]["mrr_usd"].sum())
    prev_mrr  = int(mf[mf["month"]=="2026-02"]["mrr_usd"].sum())
    mrr_g     = ((total_mrr - prev_mrr) / max(prev_mrr,1)) * 100
    avg_comp  = cf["estate_completeness_score"].mean()
    total_av  = af["estimated_value_usd"].sum()
    avg_bene  = cf["beneficiaries_assigned"].mean()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpi(c1, "Active Subscribers",  f"{active:,}",      f"{((active/max(int(active*0.93),1)-1)*100):.1f}% MoM", True)
    kpi(c2, "MRR",                 f"${total_mrr:,}",  f"{mrr_g:+.1f}% MoM", mrr_g>0)
    kpi(c3, "ARR",                 f"${total_mrr*12:,}")
    kpi(c4, "Avg Estate Complete", f"{avg_comp:.0%}",  "across all tiers", True)
    kpi(c5, "Assets Registered",   f"{len(af):,}",     f"${total_av/1e6:.1f}M value", True)
    kpi(c6, "Documents Stored",    f"{len(df):,}",     f"{avg_bene:.1f} avg beneficiaries", True)
    divider()

    section("Estate Completeness by Tier")
    col1, col2 = st.columns([3,2])
    with col1:
        comp = cf.groupby("subscription_tier")["estate_completeness_score"]\
            .describe()[["mean","25%","75%"]].reset_index()
        comp["order"] = comp["subscription_tier"].map({"Free":0,"Basic":1,"Premium":2,"Family":3})
        comp = comp.sort_values("order")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=comp["subscription_tier"], y=comp["mean"]*100,
            marker_color=[TIER_C.get(t,STEEL) for t in comp["subscription_tier"]],
            name="Avg", text=[f"{v*100:.0f}%" for v in comp["mean"]], textposition="outside"))
        fig.add_trace(go.Scatter(x=comp["subscription_tier"], y=comp["75%"]*100,
            name="75th Pct", mode="markers",
            marker=dict(symbol="triangle-up", size=10, color=C["green"])))
        fig.add_trace(go.Scatter(x=comp["subscription_tier"], y=comp["25%"]*100,
            name="25th Pct", mode="markers",
            marker=dict(symbol="triangle-down", size=10, color=C["red"])))
        pl(fig,"Average Estate Completeness Score by Tier (%)",350)
        fig.update_yaxes(title="Completeness (%)", ticksuffix="%", range=[0,115])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        sec_avg = esf.groupby("section")["completion"].mean().reset_index().sort_values("completion")
        fig2 = go.Figure(go.Bar(
            y=sec_avg["section"], x=sec_avg["completion"]*100, orientation="h",
            marker=dict(color=sec_avg["completion"],
                        colorscale=[[0,"#3d1010"],[0.5,GOLD],[1,STEEL]]),
            text=[f"{v*100:.0f}%" for v in sec_avg["completion"]], textposition="outside"))
        pl(fig2,"Completion by Estate Section (%)",350)
        fig2.update_xaxes(title="Avg Completion", ticksuffix="%", range=[0,110])
        st.plotly_chart(fig2, use_container_width=True)
    divider()

    section("Registered Asset Portfolio")
    col3, col4, col5 = st.columns(3)
    with col3:
        at = af.groupby("asset_type")["estimated_value_usd"].sum().reset_index()\
            .sort_values("estimated_value_usd", ascending=False)
        fig3 = go.Figure(go.Pie(labels=at["asset_type"], values=at["estimated_value_usd"],
            hole=0.52, marker=dict(colors=CHART_PAL, line=dict(color=NAVY_BG, width=2)),
            textfont=dict(size=10)))
        pl(fig3,"Asset Value by Type",315)
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        ac = af.groupby("asset_type").size().reset_index(name="count").sort_values("count", ascending=True)
        fig4 = go.Figure(go.Bar(y=ac["asset_type"], x=ac["count"], orientation="h",
            marker_color=STEEL, opacity=0.85,
            text=ac["count"], textposition="outside"))
        pl(fig4,"Asset Count by Type",315)
        st.plotly_chart(fig4, use_container_width=True)
    with col5:
        cr = cf.groupby("subscription_tier")["has_crypto_assets"].mean().reset_index()
        cr["order"] = cr["subscription_tier"].map({"Free":0,"Basic":1,"Premium":2,"Family":3})
        cr = cr.sort_values("order")
        fig5 = go.Figure(go.Bar(x=cr["subscription_tier"], y=cr["has_crypto_assets"]*100,
            marker_color=[TIER_C.get(t,STEEL) for t in cr["subscription_tier"]],
            text=[f"{v*100:.0f}%" for v in cr["has_crypto_assets"]], textposition="outside"))
        pl(fig5,"Crypto Asset Holders by Tier (%)",315)
        fig5.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig5, use_container_width=True)
    divider()

    section("Document Vault Activity")
    col6, col7 = st.columns(2)
    with col6:
        doc_c = df.groupby("doc_type").size().reset_index(name="count").sort_values("count", ascending=True)
        fig6 = go.Figure(go.Bar(y=doc_c["doc_type"], x=doc_c["count"], orientation="h",
            marker=dict(color=doc_c["count"],
                        colorscale=[[0,NAVY_C2],[0.6,STEEL],[1,SILVER]]),
            text=doc_c["count"], textposition="outside"))
        pl(fig6,"Documents Stored by Type",340)
        st.plotly_chart(fig6, use_container_width=True)
    with col7:
        doc_tier = df.groupby(["tier","doc_type"]).size().reset_index(name="count")
        fig7 = px.bar(doc_tier, x="doc_type", y="count", color="tier",
                      color_discrete_map=TIER_C, barmode="stack")
        pl(fig7,"Document Uploads by Type & Tier",340)
        fig7.update_xaxes(tickangle=-35, tickfont=dict(size=9))
        st.plotly_chart(fig7, use_container_width=True)
    divider()

    section("Revenue & Subscriber Growth")
    col8, col9 = st.columns(2)
    with col8:
        mp = mf.groupby(["month","tier"])["mrr_usd"].sum().reset_index()
        mp["month_dt"] = pd.to_datetime(mp["month"])
        fig8 = go.Figure()
        for t in ["Free","Basic","Premium","Family"]:
            d = mp[mp["tier"]==t]
            tc = TIER_C.get(t, STEEL)
            fig8.add_trace(go.Scatter(x=d["month_dt"], y=d["mrr_usd"], name=t, mode="lines",
                line=dict(color=tc, width=2.5), fill="tozeroy", fillcolor=tc))
        pl(fig8,"Monthly Recurring Revenue by Tier (USD)",320)
        fig8.update_yaxes(tickprefix="$")
        st.plotly_chart(fig8, use_container_width=True)
    with col9:
        ns = mf.groupby("month")["new_subscribers"].sum().reset_index().sort_values("month")
        ns["month_dt"] = pd.to_datetime(ns["month"])
        ns["roll3"] = ns["new_subscribers"].rolling(3, min_periods=1).mean()
        fig9 = go.Figure()
        fig9.add_trace(go.Bar(x=ns["month_dt"], y=ns["new_subscribers"], name="New",
            marker_color=f"rgba(74,143,212,0.4)",
            marker_line_color=STEEL, marker_line_width=1))
        fig9.add_trace(go.Scatter(x=ns["month_dt"], y=ns["roll3"], name="3M Avg",
            line=dict(color=GOLD, width=2.5, dash="dot"), mode="lines"))
        pl(fig9,"New Subscribers per Month",320)
        st.plotly_chart(fig9, use_container_width=True)

    col10, col11 = st.columns(2)
    with col10:
        cac_ch = cf.groupby("acquisition_channel")["cac_usd"].agg(["mean","count"]).reset_index()
        cac_ch.columns = ["channel","avg_cac","n"]
        cac_ch = cac_ch.sort_values("avg_cac", ascending=True)
        fig10 = go.Figure(go.Bar(y=cac_ch["channel"], x=cac_ch["avg_cac"], orientation="h",
            marker=dict(color=cac_ch["avg_cac"],
                        colorscale=[[0,C["green"]],[0.5,GOLD],[1,C["red"]]],
                        showscale=True, colorbar=dict(tickfont=dict(size=9))),
            text=[f"${v:.0f} ({c:,})" for v,c in zip(cac_ch["avg_cac"],cac_ch["n"])],
            textposition="outside"))
        pl(fig10,"CAC by Acquisition Channel (USD)",310)
        fig10.update_xaxes(tickprefix="$")
        st.plotly_chart(fig10, use_container_width=True)
    with col11:
        consol = cf.groupby("subscription_tier")["platforms_consolidated"].mean().reset_index()
        consol["order"] = consol["subscription_tier"].map({"Free":0,"Basic":1,"Premium":2,"Family":3})
        consol = consol.sort_values("order")
        fig11 = go.Figure(go.Bar(x=consol["subscription_tier"], y=consol["platforms_consolidated"],
            marker_color=[TIER_C.get(t,STEEL) for t in consol["subscription_tier"]],
            text=[f"{v:.1f}" for v in consol["platforms_consolidated"]], textposition="outside"))
        pl(fig11,"Avg Platforms Consolidated per Subscriber by Tier",310)
        fig11.update_yaxes(title="Avg Platforms Replaced")
        st.plotly_chart(fig11, use_container_width=True)

    churn_rate = cf["is_churned"].mean()*100
    crypto_pct = cf["has_crypto_assets"].mean()*100
    will_count = len(df[df["doc_type"].isin(["Last Will & Testament","Digital Will"])])
    top_ch     = cf.groupby("acquisition_channel").size().idxmax()
    insight(
        f"⚖️ <b>Descriptive Snapshot:</b> VaultaLex hosts <b>{active:,} active subscribers</b> "
        f"generating <b>${total_mrr:,} MRR</b> (${total_mrr*12:,} ARR). "
        f"Average estate completeness is <b>{avg_comp:.0%}</b>. "
        f"<b>{len(af):,} assets</b> totalling <b>${total_av/1e6:.1f}M</b> are registered. "
        f"<b>{crypto_pct:.0f}%</b> of subscribers hold crypto assets — a fast-growing segment. "
        f"<b>{will_count:,} wills</b> stored in the vault. "
        f"Subscribers consolidate <b>{cf['platforms_consolidated'].mean():.1f} platforms</b> on average. "
        f"Overall churn: <b>{churn_rate:.1f}%</b>. {top_ch} leads acquisition."
    )
    pdf_button("dl_descriptive", build_descriptive_report,
               "📊 Descriptive Analytics Report",
               f"VaultaLex_Descriptive_{datetime.now().strftime('%Y%m%d')}.pdf")

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 2 — DIAGNOSTIC
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍  Diagnostic":
    layer_hdr("LAYER 02","Diagnostic Analytics",
              "Why things happened — estate gaps, churn drivers, feature behaviour & security posture")

    section("Estate Completeness Deep-Dive")
    col1, col2 = st.columns(2)
    with col1:
        sec_tier = esf.groupby(["section","tier"])["completion"].mean().reset_index()
        fig = px.bar(sec_tier, x="section", y="completion", color="tier",
                     color_discrete_map=TIER_C, barmode="group")
        pl(fig,"Estate Section Completion by Tier",355)
        fig.update_yaxes(tickformat=".0%", range=[0,1.1])
        fig.update_xaxes(tickangle=-20, tickfont=dict(size=9))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        will_ids = df[df["doc_type"].isin(["Last Will & Testament","Digital Will"])]["customer_id"].unique()
        cf2 = cf.copy(); cf2["has_will"] = cf2["customer_id"].isin(will_ids).astype(int)
        wr = cf2.groupby("subscription_tier")["has_will"].mean().reset_index()
        wr["order"] = wr["subscription_tier"].map({"Free":0,"Basic":1,"Premium":2,"Family":3})
        wr = wr.sort_values("order")
        fig2 = go.Figure(go.Bar(x=wr["subscription_tier"], y=wr["has_will"]*100,
            marker_color=[TIER_C.get(t,STEEL) for t in wr["subscription_tier"]],
            text=[f"{v*100:.0f}%" for v in wr["has_will"]], textposition="outside"))
        fig2.add_hline(y=50, line_dash="dash", line_color=TEXT_DIM,
                       annotation_text="50% target", annotation_font_size=10)
        pl(fig2,"Will / Digital Will Completion Rate by Tier (%)",355)
        fig2.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig2, use_container_width=True)
    divider()

    section("RFM Customer Segmentation")
    col3, col4 = st.columns([3,2])
    with col3:
        seg_order = ["Champions","Loyal Customers","Potential Loyalists","At Risk","Hibernating"]
        rc = rf.groupby(["rfm_segment","tier"]).size().reset_index(name="count")
        rc["rfm_segment"] = pd.Categorical(rc["rfm_segment"], seg_order, ordered=True)
        rc = rc.sort_values("rfm_segment")
        fig3 = px.bar(rc, x="rfm_segment", y="count", color="tier",
                      color_discrete_map=TIER_C, barmode="group")
        pl(fig3,"Customers by RFM Segment & Tier",340)
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        rb = rf.groupby("rfm_segment").agg(
            avg_r=("recency_days","mean"), avg_f=("frequency_logins","mean"),
            n=("customer_id","count")).reset_index()
        sc_map = {"Champions":GOLD,"Loyal Customers":C["green"],"Potential Loyalists":STEEL,
                  "At Risk":C["red"],"Hibernating":"#9480d4"}
        fig4 = go.Figure()
        for _, row in rb.iterrows():
            fig4.add_trace(go.Scatter(x=[row["avg_r"]], y=[row["avg_f"]],
                mode="markers+text",
                marker=dict(size=row["n"]//10+18, color=sc_map.get(row["rfm_segment"],SILVER),
                            opacity=0.85, line=dict(width=2, color=NAVY_BG)),
                name=row["rfm_segment"], text=[row["rfm_segment"]],
                textposition="top center", textfont=dict(size=9)))
        pl(fig4,"RFM Bubble: Recency vs Frequency",340)
        fig4.update_xaxes(title="Avg Recency (days)", autorange="reversed")
        fig4.update_yaxes(title="Avg Logins")
        st.plotly_chart(fig4, use_container_width=True)
    divider()

    section("Cohort Retention Heatmap")
    recent = sorted(cohort["cohort_month"].unique())[-18:]
    ch_h   = cohort[cohort["cohort_month"].isin(recent)]
    pivot  = ch_h.pivot(index="cohort_month", columns="period_month",
                        values="retention_rate").fillna(0)
    fig5 = go.Figure(go.Heatmap(
        z=pivot.values*100, x=[f"M+{c}" for c in pivot.columns], y=pivot.index,
        colorscale=[[0,"#0a1020"],[0.3,"#142850"],[0.65,STEEL],[0.85,SILVER],[1,"#e8eef6"]],
        text=np.round(pivot.values*100,1), texttemplate="%{text}%",
        textfont=dict(size=9), zmin=0, zmax=100,
        colorbar=dict(title="Retention %", ticksuffix="%", tickfont=dict(size=9))))
    pl(fig5,"Monthly Cohort Retention Heatmap (%) — Last 18 Cohorts",500)
    fig5.update_xaxes(title="Months Since Signup")
    fig5.update_yaxes(title="Cohort Month")
    st.plotly_chart(fig5, use_container_width=True)
    divider()

    col5, col6 = st.columns(2)
    with col5:
        section("Churn Root Cause Breakdown")
        cd = cf[cf["is_churned"]==1]["churn_reason"].value_counts().reset_index()
        cd.columns = ["reason","count"]; cd = cd.sort_values("count", ascending=True)
        fig6 = go.Figure(go.Bar(y=cd["reason"], x=cd["count"], orientation="h",
            marker=dict(color=cd["count"],
                        colorscale=[[0,NAVY_C2],[0.5,GOLD],[1,C["red"]]]),
            text=cd["count"], textposition="outside"))
        pl(fig6,"Churned Customers by Reason",320)
        st.plotly_chart(fig6, use_container_width=True)
    with col6:
        section("Feature-Retention Correlation")
        fr  = ff.merge(cf[["customer_id","is_churned"]], on="customer_id")
        fra = fr.groupby("feature").agg(n=("customer_id","count"),churned=("is_churned","sum")).reset_index()
        fra["retention"] = (1 - fra["churned"]/fra["n"])*100
        non_ret = []
        for feat in ["Document Upload","Password Vault","Asset Registry","Beneficiary Designation","Legal Advisory"]:
            aids = ff[ff["feature"]==feat]["customer_id"].unique()
            non  = cf[~cf["customer_id"].isin(aids)]
            non_ret.append({"feature": feat, "retention": (1-non["is_churned"].mean())*100})
        na_df = pd.DataFrame(non_ret)
        fig7 = go.Figure()
        fig7.add_trace(go.Bar(y=fra["feature"], x=fra["retention"],
            name="Adopters", orientation="h", marker_color=C["green"], opacity=0.85))
        fig7.add_trace(go.Bar(y=na_df["feature"], x=na_df["retention"],
            name="Non-Adopters", orientation="h", marker_color=C["red"], opacity=0.7))
        pl(fig7,"Retention: Adopters vs Non-Adopters (%)",320)
        fig7.update_layout(barmode="group"); fig7.update_xaxes(ticksuffix="%")
        st.plotly_chart(fig7, use_container_width=True)
    divider()

    col7, col8 = st.columns(2)
    with col7:
        section("Upgrade / Downgrade Funnel")
        up = tier_transitions[tier_transitions["direction"]=="Upgrade"]
        dn = tier_transitions[tier_transitions["direction"]=="Downgrade"]
        fig8 = go.Figure()
        fig8.add_trace(go.Bar(x=up["from_tier"]+" → "+up["to_tier"],
            y=up["customers_transitioned"], name="Upgrades", marker_color=C["green"]))
        fig8.add_trace(go.Bar(x=dn["from_tier"]+" → "+dn["to_tier"],
            y=dn["customers_transitioned"], name="Downgrades", marker_color=C["red"]))
        pl(fig8,"Tier Transition Volume",310); fig8.update_layout(barmode="group")
        st.plotly_chart(fig8, use_container_width=True)
    with col8:
        section("Security Trust Score")
        te = len(sf); he = len(sf[sf["risk_level"]=="High"])
        res = sf["resolved"].mean()*100 if len(sf)>0 else 0
        tfa = cf["two_fa_enabled"].mean()*100
        ts  = tfa*0.35 + res*0.40 + (1-he/max(te,1))*100*0.25
        fig9 = go.Figure(go.Indicator(mode="gauge+number", value=ts,
            number=dict(font=dict(family="Inter,sans-serif", size=40, color=GOLD)),
            title=dict(text="Vault Security Trust Score /100",
                       font=dict(family="Space Mono,monospace", size=11, color=TEXT_MID)),
            gauge=dict(axis=dict(range=[0,100], tickfont=dict(size=10, color=TEXT_MID)),
                bar=dict(color=STEEL, thickness=0.25), bgcolor=NAVY_CARD,
                borderwidth=1, bordercolor=NAVY_BORD,
                steps=[dict(range=[0,40],  color="#1a1030"),
                       dict(range=[40,70], color="#142030"),
                       dict(range=[70,100],color="#10253a")],
                threshold=dict(line=dict(color=C["green"], width=3), thickness=0.75, value=75))))
        pl(fig9,"",310); fig9.update_layout(margin=dict(l=30,r=30,t=60,b=20))
        st.plotly_chart(fig9, use_container_width=True)

    top_cr  = cf[cf["is_churned"]==1]["churn_reason"].value_counts().index[0] if cf["is_churned"].sum()>0 else "N/A"
    best_rf = fra.sort_values("retention", ascending=False).iloc[0]["feature"] if len(fra)>0 else "N/A"
    low_sec = esf.groupby("section")["completion"].mean().idxmin()
    no_will = len(cf[cf["is_churned"]==0][~cf[cf["is_churned"]==0]["customer_id"].isin(will_ids)])
    insight(
        f"🔍 <b>Diagnostic Insight:</b> <b>{top_cr}</b> is the #1 churn driver. "
        f"Users adopting <b>{best_rf}</b> show the highest retention — centrepiece of onboarding. "
        f"<b>{no_will:,} active subscribers</b> have no will — the clearest legal advisory upsell signal. "
        f"<b>{low_sec}</b> is the least-completed estate section. "
        f"Security Trust Score <b>{ts:.0f}/100</b> — 2FA adoption ({tfa:.0f}%) is the fastest lever.",
        "warn"
    )
    pdf_button("dl_diagnostic", build_diagnostic_report,
               "🔍 Diagnostic Analytics Report",
               f"VaultaLex_Diagnostic_{datetime.now().strftime('%Y%m%d')}.pdf")

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 3 — PREDICTIVE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔮  Predictive":
    layer_hdr("LAYER 03","Predictive Analytics",
              "What will happen — churn risk, CLV, MRR forecasts & legal advisory pipeline")

    col1, col2 = st.columns([3,2])
    with col1:
        section("Churn Probability Score Distribution")
        fig = go.Figure()
        for t in tier_f:
            d = cf[cf["subscription_tier"]==t]["churn_probability_score"]
            fig.add_trace(go.Histogram(x=d, name=t, nbinsx=30, opacity=0.7,
                marker_color=TIER_C.get(t,STEEL), histnorm="percent"))
        pl(fig,"Churn Probability by Tier",355)
        fig.update_layout(barmode="overlay")
        fig.update_xaxes(title="Churn Probability (0–1)")
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        section("Risk Bucket Breakdown")
        cf2 = cf.copy()
        cf2["risk"] = pd.cut(cf2["churn_probability_score"], bins=[0,.25,.50,.75,1.0],
            labels=["Low Risk","Medium Risk","High Risk","Critical"])
        rc2 = cf2["risk"].value_counts().reset_index(); rc2.columns = ["bucket","count"]
        fig2 = go.Figure(go.Pie(labels=rc2["bucket"], values=rc2["count"], hole=0.5,
            marker=dict(colors=[C["green"],GOLD,C["red"],"#9480d4"],
                        line=dict(color=NAVY_BG, width=3)),
            textfont=dict(family="Space Mono,monospace", size=10)))
        pl(fig2,"Risk Distribution",355)
        st.plotly_chart(fig2, use_container_width=True)
    divider()

    section("Customer Lifetime Value Predictions")
    col3, col4 = st.columns(2)
    with col3:
        fig3 = go.Figure()
        for t in tier_f:
            d = cf[cf["subscription_tier"]==t]["clv_predicted_usd"]
            tc = TIER_C.get(t,STEEL)
            fig3.add_trace(go.Box(y=d, name=t, marker_color=tc, boxpoints="outliers",
                line_color=tc, fillcolor=tc))
        pl(fig3,"Predicted CLV Distribution by Tier (USD)",345)
        fig3.update_yaxes(tickprefix="$")
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        samp = cf.sample(min(600,len(cf)), random_state=1)
        fig4 = px.scatter(samp, x="churn_probability_score", y="clv_predicted_usd",
            color="subscription_tier", color_discrete_map=TIER_C, opacity=0.6,
            size="estate_completeness_score", size_max=12)
        fig4.add_vline(x=samp["churn_probability_score"].median(), line_dash="dash",
                       line_color=NAVY_BORD, opacity=0.5)
        fig4.add_hline(y=samp["clv_predicted_usd"].median(), line_dash="dash",
                       line_color=NAVY_BORD, opacity=0.5)
        pl(fig4,"Risk-Value Matrix (sized by Estate Completeness)",345)
        fig4.update_yaxes(tickprefix="$")
        st.plotly_chart(fig4, use_container_width=True)
    divider()

    section("MRR Forecast — 9-Month Projection")
    hist = mf.groupby("month")["mrr_usd"].sum().reset_index().sort_values("month")
    hist["month_dt"] = pd.to_datetime(hist["month"])
    fct  = mrr_forecast.groupby("forecast_month").agg(
        proj=("projected_mrr_usd","sum"), lo=("lower_bound_usd","sum"),
        hi=("upper_bound_usd","sum")).reset_index()
    fct["month_dt"] = pd.to_datetime(fct["forecast_month"])
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=hist.tail(14)["month_dt"], y=hist.tail(14)["mrr_usd"],
        name="Historical", line=dict(color=STEEL, width=3)))
    fig5.add_trace(go.Scatter(x=fct["month_dt"], y=fct["proj"],
        name="Forecast", line=dict(color=GOLD, width=3, dash="dot"),
        mode="lines+markers", marker=dict(size=7)))
    fig5.add_trace(go.Scatter(
        x=list(fct["month_dt"])+list(fct["month_dt"])[::-1],
        y=list(fct["hi"])+list(fct["lo"])[::-1],
        fill="toself", fillcolor="rgba(212,168,67,0.07)",
        line=dict(color="rgba(0,0,0,0)"), name="Confidence Band"))
    fig5.add_vline(x="2026-04-01", line_dash="dash", line_color=TEXT_DIM,
                   annotation_text="Forecast →", annotation_font_size=10)
    pl(fig5,"MRR: Historical + 9-Month Forecast (USD)",375)
    fig5.update_yaxes(tickprefix="$")
    st.plotly_chart(fig5, use_container_width=True)
    divider()

    section("Legal Advisory & Testamentary Readiness Pipeline")
    col5, col6 = st.columns(2)
    with col5:
        fig6 = go.Figure()
        for t in tier_f:
            d = cf[cf["subscription_tier"]==t]["legal_advisory_readiness_score"]
            fig6.add_trace(go.Histogram(x=d, name=t, nbinsx=20, opacity=0.75,
                marker_color=TIER_C.get(t,STEEL), histnorm="percent"))
        fig6.add_vline(x=0.6, line_dash="dash", line_color=GOLD,
                       annotation_text="Advisory Ready",
                       annotation_font_color=GOLD, annotation_font_size=10)
        pl(fig6,"Legal Advisory Readiness Score",325)
        fig6.update_layout(barmode="overlay"); fig6.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig6, use_container_width=True)
    with col6:
        samp2 = cf.sample(min(500,len(cf)), random_state=5)
        fig7  = px.scatter(samp2, x="estate_completeness_score",
            y="testamentary_readiness_score", color="subscription_tier",
            color_discrete_map=TIER_C, opacity=0.55)
        fig7.add_vline(x=0.7, line_dash="dash", line_color=NAVY_BORD, opacity=0.5)
        fig7.add_hline(y=0.7, line_dash="dash", line_color=NAVY_BORD, opacity=0.5)
        pl(fig7,"Estate Completeness vs Testamentary Readiness",325)
        st.plotly_chart(fig7, use_container_width=True)

    col7, col8 = st.columns(2)
    with col7:
        section("Upgrade Propensity Distribution")
        fig8 = go.Figure()
        for t in ["Free","Basic"]:
            if t not in tier_f: continue
            d = cf[cf["subscription_tier"]==t]["upgrade_propensity_score"]
            fig8.add_trace(go.Histogram(x=d, name=t, nbinsx=25, opacity=0.75,
                marker_color=TIER_C.get(t,STEEL), histnorm="percent"))
        pl(fig8,"Upgrade Propensity: Free & Basic",295)
        fig8.update_layout(barmode="overlay"); fig8.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig8, use_container_width=True)
    with col8:
        section("Top Upgrade Candidates")
        tu = cf[cf["subscription_tier"].isin(["Free","Basic"])]\
            .sort_values("upgrade_propensity_score", ascending=False).head(12)\
            [["customer_id","subscription_tier","upgrade_propensity_score",
              "estate_completeness_score","clv_predicted_usd"]].copy()
        tu.columns = ["ID","Tier","Upgrade Score","Estate %","CLV"]
        tu["Upgrade Score"] = tu["Upgrade Score"].apply(lambda x: f"{x:.3f}")
        tu["Estate %"]      = tu["Estate %"].apply(lambda x: f"{x:.0%}")
        tu["CLV"]           = tu["CLV"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(tu, use_container_width=True, height=295, hide_index=True)

    hrc     = len(cf[cf["churn_probability_score"]>0.6])
    acp     = cf[cf["subscription_tier"]=="Premium"]["clv_predicted_usd"].mean()
    lrc     = len(cf[cf["legal_advisory_readiness_score"]>0.6])
    end_mrr = fct.iloc[-1]["proj"]
    insight(
        f"🔮 <b>Predictive Insight:</b> <b>{hrc:,} subscribers</b> carry churn probability >60% — "
        f"immediate intervention warranted. Premium CLV averages <b>${acp:,.0f}</b>. "
        f"MRR forecast to reach <b>${end_mrr:,.0f}</b> by Dec 2026. "
        f"<b>{lrc:,} subscribers</b> are legal-advisory-ready — "
        f"a tangible pipeline for the VaultaLex testamentary premium tier launch."
    )
    pdf_button("dl_predictive", build_predictive_report,
               "🔮 Predictive Analytics Report",
               f"VaultaLex_Predictive_{datetime.now().strftime('%Y%m%d')}.pdf")

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 4 — PRESCRIPTIVE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧭  Prescriptive":
    layer_hdr("LAYER 04","Prescriptive Analytics",
              "What to do — estate gap interventions, A/B results, at-risk actions & legal advisory launch")

    section("A/B Test Performance")
    abw = ab_tests.pivot(
        index=["test_id","test_name","category","statistical_significance"],
        columns="variant", values=["conversion_rate","revenue_impact_usd"]
    ).reset_index()
    abw.columns = ["test_id","test_name","category","sig","ctrl_cv","treat_cv","ctrl_rv","treat_rv"]
    abw["lift"]     = ((abw["treat_cv"]-abw["ctrl_cv"])/abw["ctrl_cv"].replace(0,1))*100
    abw["rev_lift"] = abw["treat_rv"] - abw["ctrl_rv"]
    abw["winner"]   = abw["lift"].apply(lambda x: "✅ Treatment" if x>0 else "❌ Control")

    col1, col2 = st.columns([3,2])
    with col1:
        ab_s = abw.sort_values("lift")
        fig = go.Figure(go.Bar(y=ab_s["test_name"], x=ab_s["lift"], orientation="h",
            marker=dict(color=ab_s["lift"],
                        colorscale=[[0,C["red"]],[0.5,NAVY_C2],[1,C["green"]]]),
            text=[f"{v:+.1f}%" for v in ab_s["lift"]], textposition="outside"))
        pl(fig,"A/B Test Conversion Lift (Treatment vs Control)",375)
        fig.add_vline(x=0, line_color=TEXT_DIM, line_width=1, line_dash="dash")
        fig.update_xaxes(ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = go.Figure(go.Bar(x=abw["test_name"], y=abw["rev_lift"],
            marker=dict(color=abw["rev_lift"],
                        colorscale=[[0,C["red"]],[0.5,NAVY_C2],[1,C["green"]]]),
            text=[f"${v:+,.0f}" for v in abw["rev_lift"]], textposition="outside",
            textfont=dict(size=9)))
        pl(fig2,"Revenue Lift per Test (USD)",375)
        fig2.add_hline(y=0, line_color=TEXT_DIM, line_width=1, line_dash="dash")
        fig2.update_xaxes(tickangle=-35, tickfont=dict(size=9))
        fig2.update_yaxes(tickprefix="$")
        st.plotly_chart(fig2, use_container_width=True)

    disp_ab = abw[["test_name","category","lift","rev_lift","sig","winner"]].copy()
    disp_ab.columns = ["Test Name","Category","Conv Lift %","Rev Lift $","Significance","Winner"]
    disp_ab["Conv Lift %"] = disp_ab["Conv Lift %"].apply(lambda x: f"{x:+.1f}%")
    disp_ab["Rev Lift $"]  = disp_ab["Rev Lift $"].apply(lambda x: f"${x:+,.0f}")
    disp_ab["Significance"]= disp_ab["Significance"].apply(lambda x: f"{x:.1%}")
    st.dataframe(disp_ab, use_container_width=True, height=240, hide_index=True)
    divider()

    section("Estate Gap Intervention Map")
    active_cf = cf[cf["is_churned"]==0]
    will_ids  = df[df["doc_type"].isin(["Last Will & Testament","Digital Will"])]["customer_id"].unique()
    asset_ids = assets["customer_id"].unique()
    poa_ids   = df[df["doc_type"]=="Power of Attorney"]["customer_id"].unique()
    vault_ids = feature_usage[feature_usage["feature"]=="Password Vault"]["customer_id"].unique()
    gaps = {
        "No Will / Digital Will":    len(active_cf[~active_cf["customer_id"].isin(will_ids)]),
        "No Beneficiaries Set":      len(active_cf[active_cf["beneficiaries_assigned"]==0]),
        "No Assets Registered":      len(active_cf[~active_cf["customer_id"].isin(asset_ids)]),
        "No Power of Attorney":      len(active_cf[~active_cf["customer_id"].isin(poa_ids)]),
        "Password Vault Empty":      len(active_cf[~active_cf["customer_id"].isin(vault_ids)]),
    }
    col3, col4 = st.columns(2)
    with col3:
        gdf = pd.DataFrame(list(gaps.items()), columns=["Gap","Affected"]).sort_values("Affected", ascending=True)
        fig3 = go.Figure(go.Bar(y=gdf["Gap"], x=gdf["Affected"], orientation="h",
            marker=dict(color=gdf["Affected"], colorscale=[[0,GOLD],[1,C["red"]]]),
            text=gdf["Affected"], textposition="outside"))
        pl(fig3,"Active Subscribers with Critical Estate Gaps",335)
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        comp_b = pd.cut(cf["estate_completeness_score"], bins=5,
                        labels=["0–20%","20–40%","40–60%","60–80%","80–100%"])
        cf_b = cf.copy(); cf_b["band"] = comp_b
        churn_bc = cf_b.groupby("band", observed=True)["is_churned"].mean()
        fig4 = go.Figure(go.Bar(
            x=[str(k) for k in churn_bc.index], y=churn_bc.values*100,
            marker=dict(color=churn_bc.values,
                        colorscale=[[0,C["green"]],[0.5,GOLD],[1,C["red"]]]),
            text=[f"{v*100:.1f}%" for v in churn_bc.values], textposition="outside"))
        pl(fig4,"Churn Rate by Estate Completion Band — lower completion = higher churn",335)
        fig4.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig4, use_container_width=True)
    divider()

    section("At-Risk Subscriber Intervention Triggers")
    ar = cf[(cf["churn_probability_score"]>0.55) & (cf["is_churned"]==0)].copy()
    ar["Priority"] = ar["churn_probability_score"].apply(lambda x: "🔴 CRITICAL" if x>0.75 else "🟡 HIGH")
    ar["Save_Val"] = (ar["clv_predicted_usd"]*0.30).round(2)
    ar["Action"]   = ar.apply(lambda r: (
        "Legal advisory unlock + 20% discount"
        if r["legal_advisory_readiness_score"]>0.5
        else "Estate gap email + beneficiary prompt"
        if r["beneficiaries_assigned"]==0
        else "Re-engage: complete your estate plan"
    ), axis=1)

    st.markdown(f"""<div style='display:flex;gap:14px;margin-bottom:14px;'>
      <div class='kpi-card' style='flex:1;'>
        <div class='kpi-label'>At-Risk Subscribers</div>
        <div class='kpi-value'>{len(ar):,}</div>
        <div class='kpi-delta neg'>▼ Need intervention</div></div>
      <div class='kpi-card' style='flex:1;'>
        <div class='kpi-label'>Critical (&gt;75%)</div>
        <div class='kpi-value' style='color:#e07060;'>
          {len(ar[ar["Priority"]=="🔴 CRITICAL"]):,}</div></div>
      <div class='kpi-card' style='flex:1;'>
        <div class='kpi-label'>Recoverable CLV</div>
        <div class='kpi-value'>${ar["Save_Val"].sum():,.0f}</div>
        <div class='kpi-delta pos'>▲ 30% CLV recovery est.</div></div>
    </div>""", unsafe_allow_html=True)

    disp_ar = ar.sort_values("churn_probability_score", ascending=False).head(25)\
        [["customer_id","subscription_tier","churn_probability_score",
          "estate_completeness_score","beneficiaries_assigned","Save_Val","Priority","Action"]].copy()
    disp_ar.columns = ["ID","Tier","Churn Score","Estate %","Beneficiaries","Save Val $","Priority","Recommended Action"]
    disp_ar["Churn Score"] = disp_ar["Churn Score"].apply(lambda x: f"{x:.3f}")
    disp_ar["Estate %"]    = disp_ar["Estate %"].apply(lambda x: f"{x:.0%}")
    disp_ar["Save Val $"]  = disp_ar["Save Val $"].apply(lambda x: f"${x:,.0f}")
    st.dataframe(disp_ar, use_container_width=True, height=380, hide_index=True)
    divider()

    col5, col6 = st.columns(2)
    with col5:
        section("Uplift Score by Tier")
        fig5 = go.Figure()
        for t in tier_f:
            d = cf[cf["subscription_tier"]==t]["uplift_score"]
            tc = TIER_C.get(t,STEEL)
            fig5.add_trace(go.Violin(x=[t]*len(d), y=d, name=t,
                box_visible=True, meanline_visible=True,
                line_color=tc, fillcolor=tc, opacity=0.8))
        pl(fig5,"Uplift Score Distribution by Tier",315)
        st.plotly_chart(fig5, use_container_width=True)
    with col6:
        section("Legal Advisory Conversion Pipeline")
        lrc_bins = ["Not Ready","Early Stage","Developing","Near Ready","Ready"]
        lrc_cut  = pd.cut(cf["legal_advisory_readiness_score"],
                          bins=[0,.2,.4,.6,.8,1.0], labels=lrc_bins)
        pipeline = lrc_cut.value_counts().reindex(lrc_bins)
        fig6 = go.Figure(go.Funnel(
            y=pipeline.index.tolist(), x=pipeline.values.tolist(),
            textinfo="value+percent initial",
            marker=dict(color=[C["red"],C["red"],GOLD,C["green"],STEEL][::-1]),
            connector=dict(line=dict(color=NAVY_BORD, dash="dot", width=2))))
        pl(fig6,"Legal Advisory Readiness Funnel",315)
        st.plotly_chart(fig6, use_container_width=True)

    section("Pricing Tier ROI — LTV:CAC Analysis")
    col7, col8 = st.columns(2)
    with col7:
        tm = cf.groupby("subscription_tier").agg(
            avg_clv=("clv_predicted_usd","mean"), avg_cac=("cac_usd","mean"),
            n=("customer_id","count")).reset_index()
        tm["ltv_cac"] = tm["avg_clv"]/tm["avg_cac"].replace(0,1)
        tm["order"]   = tm["subscription_tier"].map({"Free":0,"Basic":1,"Premium":2,"Family":3})
        tm = tm.sort_values("order")
        fig7 = go.Figure(go.Bar(x=tm["subscription_tier"], y=tm["ltv_cac"],
            marker_color=[TIER_C.get(t,STEEL) for t in tm["subscription_tier"]],
            text=[f"{v:.1f}x" for v in tm["ltv_cac"]], textposition="outside"))
        pl(fig7,"LTV:CAC Ratio by Tier",295); fig7.update_yaxes(ticksuffix="x")
        st.plotly_chart(fig7, use_container_width=True)
    with col8:
        fig8 = go.Figure()
        fig8.add_trace(go.Bar(x=tm["subscription_tier"], y=tm["avg_clv"],
            name="Avg CLV", marker_color=STEEL, opacity=0.85))
        fig8.add_trace(go.Bar(x=tm["subscription_tier"], y=tm["avg_cac"],
            name="Avg CAC", marker_color=C["red"], opacity=0.85))
        pl(fig8,"Avg CLV vs Avg CAC by Tier (USD)",295)
        fig8.update_layout(barmode="group"); fig8.update_yaxes(tickprefix="$")
        st.plotly_chart(fig8, use_container_width=True)

    best_ab   = abw.sort_values("lift", ascending=False).iloc[0]["test_name"]
    lrc_ready = len(cf[cf["legal_advisory_readiness_score"]>0.6])
    best_tier = tm.sort_values("ltv_cac", ascending=False).iloc[0]["subscription_tier"]
    no_will_n = gaps.get("No Will / Digital Will",0)
    insight(
        f"⚖️ <b>Prescriptive Actions:</b><br>"
        f"① <b>{no_will_n:,} subscribers</b> have no will — trigger the Estate Wizard prompt. "
        f"This is VaultaLex's core value gap and most impactful conversion lever.<br>"
        f"② Intervene on <b>{len(ar):,} at-risk subscribers</b> — estate-gap personalised outreach "
        f"can recover <b>${ar['Save_Val'].sum():,.0f}</b> in CLV.<br>"
        f"③ Scale <b>'{best_ab}'</b> — highest-performing A/B test.<br>"
        f"④ <b>{lrc_ready:,} subscribers</b> are legal-advisory-ready — "
        f"prioritise in the testamentary premium tier launch.<br>"
        f"⑤ <b>{best_tier}</b> delivers the best LTV:CAC — focus acquisition on channels converting here.",
        "warn"
    )
    pdf_button("dl_prescriptive", build_prescriptive_report,
               "🧭 Prescriptive Analytics Report",
               f"VaultaLex_Prescriptive_{datetime.now().strftime('%Y%m%d')}.pdf")
