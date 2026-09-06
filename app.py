import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

from data import (
    generate_deliveries, supplier_risk_table, delay_trend,
    SUPPLIERS, PLANTS, CARRIERS, MATERIAL_CATEGORIES, RISK_LEVELS,
)

st.set_page_config(
    page_title="Inbound Delivery Visibility Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------- styling ---
PRIMARY_GREEN = "#1E7B34"
DARK_GREEN = "#0B3D24"
RED = "#D8342A"
ORANGE = "#F0A32E"
YELLOW = "#F4C430"
GRAY = "#6B7280"

st.markdown(f"""
<style>
    html, body {{ overflow: hidden; }}
    .stApp {{ background-color: #F5F6F8; }}
    header[data-testid="stHeader"] {{ display: none; }}
    div[data-testid="stToolbar"] {{ display: none; }}
    .block-container {{
        padding-top: 0.15rem !important;
        padding-bottom: 0.05rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-height: 100vh;
    }}
    div[data-testid="stVerticalBlock"] {{ gap: 0.2rem !important; }}
    div[data-testid="stElementContainer"] {{ margin-bottom: 0 !important; }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: white !important;
        border-radius: 8px !important;
        border: 1px solid #E7E9EC !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        height: 100%;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] > div {{ gap: 0.25rem !important; }}
    section[data-testid="stSidebar"] {{
        background-color: {DARK_GREEN};
    }}
    section[data-testid="stSidebar"] * {{ color: #EAF3EC !important; }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 1rem !important; }}
    div[data-testid="stMetric"] {{
        background: white;
        border-radius: 8px;
        padding: 6px 10px 4px 10px;
        border: 1px solid #E7E9EC;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }}
    div[data-testid="stMetricLabel"] {{ font-size: 0.68rem; color: #444; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.15rem; }}
    .card-title {{
        color: {PRIMARY_GREEN};
        font-weight: 700;
        font-size: 0.78rem;
        margin-bottom: 2px;
    }}
    .filter-bar {{
        background: white;
        border: 1px solid #E7E9EC;
        border-radius: 8px;
        padding: 2px 12px;
        margin-bottom: 2px;
    }}
    .filter-bar label p {{ font-size: 0.68rem !important; }}
    .status-badge {{
        padding: 3px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.78rem;
        color: white;
        display: inline-block;
    }}
    .header-title {{
        font-size: 1.25rem;
        font-weight: 800;
        color: #1a1a1a;
        margin-bottom: 0px;
        line-height: 1.1;
    }}
    .header-sub {{
        color: #666;
        font-size: 0.68rem;
    }}
    .html-tbl {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.68rem;
    }}
    .html-tbl thead tr th {{
        background-color: {PRIMARY_GREEN};
        color: white;
        text-align: left;
        padding: 2px 6px;
        font-weight: 600;
        white-space: nowrap;
    }}
    .html-tbl tbody tr td {{
        padding: 1px 6px;
        border-bottom: 1px solid #EEF0F2;
        color: #333;
        white-space: nowrap;
    }}
    .html-tbl tbody tr:last-child td {{ border-bottom: none; }}
    .stMultiSelect [data-baseweb="select"] {{ min-height: 30px; font-size: 0.7rem; }}
    .stDateInput input {{ font-size: 0.7rem; padding: 4px 6px; }}
    .card-scroll {{ font-size: 0.68rem; line-height: 1.25; }}
    .card-scroll li {{ margin-bottom: 1px; }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ data ---
@st.cache_data
def load_data():
    return generate_deliveries()

df_all = load_data()

# --------------------------------------------------------------- sidebar ---
with st.sidebar:
    st.markdown("### 📊 Schneider Electric")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🏠 Overview", "🚚 Deliveries", "👥 Suppliers", "📈 Performance",
         "⚠️ Risks", "🔔 Alerts (4)", "✅ Actions", "📄 Reports", "ℹ️ Info"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption(f"Data refreshed\n\n**{datetime.now().strftime('%b %d, %Y %I:%M %p')}**")

# ------------------------------------------------------------------ header --
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown('<div class="header-title">Inbound Delivery Visibility Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-sub">Logistics &nbsp;|&nbsp; Inbound Delivery Performance Overview</div>', unsafe_allow_html=True)
with h2:
    st.markdown(
        f'<div style="text-align:right; color:#666; font-size:0.85rem;">Data as of<br>'
        f'<b>{datetime.now().strftime("%b %d, %Y %I:%M %p")}</b></div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------ filters --
with st.container():
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    with c1:
        date_range = st.date_input("Date Range", value=(df_all["ETA"].min(), df_all["ETA"].max()))
    with c2:
        f_supplier = st.multiselect("Supplier", SUPPLIERS, placeholder="All")
    with c3:
        f_plant = st.multiselect("Plant", PLANTS, placeholder="All")
    with c4:
        f_carrier = st.multiselect("Carrier", CARRIERS, placeholder="All")
    with c5:
        f_risk = st.multiselect("Risk Level", RISK_LEVELS, placeholder="All")
    with c6:
        f_material = st.multiselect("Material Category", MATERIAL_CATEGORIES, placeholder="All")
    with c7:
        f_bucket = st.multiselect("Delay Bucket", sorted(df_all["Delay Bucket"].unique()), placeholder="All")
    st.markdown('</div>', unsafe_allow_html=True)

# apply filters
df = df_all.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df = df[(df["ETA"] >= start) & (df["ETA"] <= end)]
if f_supplier:
    df = df[df["Supplier"].isin(f_supplier)]
if f_plant:
    df = df[df["Plant"].isin(f_plant)]
if f_carrier:
    df = df[df["Carrier"].isin(f_carrier)]
if f_risk:
    df = df[df["Risk Level"].isin(f_risk)]
if f_material:
    df = df[df["Material Category"].isin(f_material)]
if f_bucket:
    df = df[df["Delay Bucket"].isin(f_bucket)]

if df.empty:
    st.warning("No deliveries match the selected filters.")
    st.stop()

# ------------------------------------------------------------------- KPIs --
total_deliveries = len(df)
delayed = df[df["Status"] == "Delayed"]
on_time_pct = 100 * (total_deliveries - len(delayed)) / total_deliveries
avg_delay = df["Delay (Days)"].mean()
max_delay = df["Delay (Days)"].max()
high_risk_suppliers = df[df["Risk Level"] == "High"]["Supplier"].nunique()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Deliveries", f"{total_deliveries}")
k2.metric("On-Time %", f"{on_time_pct:.0f}%")
k3.metric("Delayed", f"{len(delayed)}")
k4.metric("Avg Delay (d)", f"{avg_delay:.2f}")
k5.metric("Max Delay (d)", f"{max_delay}")
k6.metric("High-Risk Sup.", f"{high_risk_suppliers}")


# --------------------------------------------------------- trend / bar / donut --
col1, col2, col3 = st.columns([1.4, 1, 0.8])

with col1:
    with st.container(border=True):
        st.markdown('<div class="card-title">📈 Inbound Delay Trend (Days)</div>', unsafe_allow_html=True)
        trend = delay_trend(df)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend["Date"], y=trend["Average Delay (Days)"],
            mode="lines+markers+text",
            text=trend["Average Delay (Days)"],
            textposition="top center",
            line=dict(color=PRIMARY_GREEN, width=3),
            marker=dict(size=7),
            name="Average Delay (Days)",
        ))
        fig.update_layout(
            height=100, margin=dict(l=2, r=2, t=2, b=2),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis_title="Delay (Days)", xaxis_title="ETA Date",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    with st.container(border=True):
        st.markdown('<div class="card-title">📊 Average Delay by Supplier (Days)</div>', unsafe_allow_html=True)
        sup_delay = df.groupby("Supplier")["Delay (Days)"].mean().sort_values(ascending=True).reset_index()
        colors = [RED if v >= 4 else ORANGE if v >= 2.5 else YELLOW if v >= 1.5 else PRIMARY_GREEN for v in sup_delay["Delay (Days)"]]
        fig2 = go.Figure(go.Bar(
            x=sup_delay["Delay (Days)"], y=sup_delay["Supplier"],
            orientation="h", marker_color=colors,
            text=sup_delay["Delay (Days)"].round(1), textposition="outside",
        ))
        fig2.update_layout(
            height=100, margin=dict(l=2, r=2, t=2, b=2),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis_title="Delay (Days)",
        )
        st.plotly_chart(fig2, use_container_width=True)

with col3:
    with st.container(border=True):
        st.markdown('<div class="card-title">🟢 Delivery Status</div>', unsafe_allow_html=True)
        n_delayed = len(delayed)
        n_ontime = total_deliveries - n_delayed
        pct_delayed = 100 * n_delayed / total_deliveries
        fig3 = go.Figure(go.Pie(
            values=[n_delayed, n_ontime], labels=["Delayed", "On-Time"],
            hole=0.65, marker_colors=[RED, PRIMARY_GREEN], textinfo="none",
        ))
        fig3.update_layout(
            height=75, margin=dict(l=2, r=2, t=2, b=2), showlegend=False,
            annotations=[dict(text=f"<b>{pct_delayed:.0f}%</b><br>Delayed", x=0.5, y=0.5, font_size=20, showarrow=False)],
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown(
            f'<div style="text-align:center;">'
            f'<span style="color:{RED};">●</span> Delayed ({n_delayed}) &nbsp;&nbsp;'
            f'<span style="color:{PRIMARY_GREEN};">●</span> On-Time ({n_ontime})</div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------- performance / risk / heatmap --
col4, col5, col6 = st.columns([1.4, 1, 1])

def badge(val, color):
    return (f'<span style="background:{color}; color:white; font-weight:600; '
            f'border-radius:4px; padding:1px 7px; display:inline-block; white-space:nowrap; font-size:0.65rem;">{val}</span>')

def status_badge(val):
    return badge(val, RED if val == "Delayed" else PRIMARY_GREEN)

def risk_badge(val):
    return badge(val, {"High": RED, "Medium": ORANGE, "Low": PRIMARY_GREEN}.get(val, GRAY))

def html_table(dframe, badge_cols=None):
    badge_cols = badge_cols or {}
    header = "".join(f"<th>{c}</th>" for c in dframe.columns)
    body = ""
    for _, row in dframe.iterrows():
        cells = ""
        for c in dframe.columns:
            v = row[c]
            cells += f"<td>{badge_cols[c](v) if c in badge_cols else v}</td>"
        body += f"<tr>{cells}</tr>"
    return f'<table class="html-tbl"><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>'

with col4:
    with st.container(border=True):
        st.markdown('<div class="card-title">📋 Inbound Delivery Performance</div>', unsafe_allow_html=True)
        show_cols = ["PO", "Supplier", "ETA", "Actual Arrival", "Delay (Days)", "Delay Bucket", "Status"]
        disp = df[show_cols].copy().head(5)
        disp["ETA"] = disp["ETA"].dt.strftime("%b %d")
        disp["Actual Arrival"] = disp["Actual Arrival"].dt.strftime("%b %d")
        st.markdown(html_table(disp, {"Status": status_badge}), unsafe_allow_html=True)
        tot_delay = df["Delay (Days)"].sum()
        st.caption(f"Total deliveries: **{total_deliveries}** &nbsp;|&nbsp; Total delay days: **{tot_delay}** &nbsp;|&nbsp; Avg delay: **{avg_delay:.2f} days**")

with col5:
    with st.container(border=True):
        st.markdown('<div class="card-title">🎯 Supplier Risk Assessment</div>', unsafe_allow_html=True)
        risk_tbl = supplier_risk_table(df)
        disp_risk = risk_tbl.copy()
        disp_risk["Average Delay (Days)"] = disp_risk["Average Delay (Days)"].map("{:.2f}".format)
        disp_risk["Risk Score"] = disp_risk["Risk Score"].round(0).astype(int)
        st.markdown(html_table(disp_risk, {"Risk Level": risk_badge}), unsafe_allow_html=True)

with col6:
    with st.container(border=True):
        st.markdown('<div class="card-title">🔥 Risk Heat Map</div>', unsafe_allow_html=True)
        # Build heat map: likelihood (rows) x impact (cols)
        likelihood_levels = ["High", "Medium", "Low"]
        impact_levels = ["Low", "Medium", "High"]
        risk_tbl2 = supplier_risk_table(df).set_index("Supplier")
        # crude mapping: likelihood = risk level, impact = based on avg delay magnitude
        cell_map = {lvl: {imp: [] for imp in impact_levels} for lvl in likelihood_levels}
        for sup, row in risk_tbl2.iterrows():
            likelihood = row["Risk Level"]
            delay = row["Average Delay (Days)"]
            impact = "High" if delay >= 4 else "Medium" if delay >= 2 else "Low"
            cell_map[likelihood][impact].append(sup)

        color_grid = {
            ("High", "High"): RED, ("High", "Medium"): ORANGE, ("High", "Low"): "#D9EAD3",
            ("Medium", "High"): ORANGE, ("Medium", "Medium"): YELLOW, ("Medium", "Low"): "#D9EAD3",
            ("Low", "High"): YELLOW, ("Low", "Medium"): "#D9EAD3", ("Low", "Low"): PRIMARY_GREEN,
        }
        rows_html = ""
        header = "".join(f"<th style='padding:6px 10px;'>{imp}</th>" for imp in impact_levels)
        rows_html += f"<tr><th></th>{header}</tr>"
        for lvl in likelihood_levels:
            cells = ""
            for imp in impact_levels:
                names = cell_map[lvl][imp]
                bg = color_grid[(lvl, imp)]
                text_color = "white" if bg in (RED, ORANGE, PRIMARY_GREEN) else "#333"
                content = "<br>".join(names) if names else ""
                cells += f"<td style='background:{bg}; color:{text_color}; text-align:center; padding:10px; border-radius:4px; font-weight:600; font-size:0.82rem;'>{content}</td>"
            rows_html += f"<tr><td style='font-weight:700; color:#333; padding:6px 10px;'>{lvl}</td>{cells}</tr>"

        st.markdown(
            f"""
            <table style="width:100%; border-collapse:separate; border-spacing:6px;">
            {rows_html}
            </table>
            <div style="text-align:center; color:#888; font-size:0.75rem; margin-top:4px;">Impact →</div>
            """,
            unsafe_allow_html=True,
        )


# --------------------------------------------------- insights / summary / actions --
col7, col8, col9 = st.columns(3)

with col7:
    with st.container(border=True):
        st.markdown('<div class="card-title">🤖 Copilot Insights</div>', unsafe_allow_html=True)
        top_supplier = risk_tbl.iloc[0]["Supplier"] if not risk_tbl.empty else "-"
        pct_delayed_overall = 100 * len(delayed) / total_deliveries
        total_delay_days = int(df["Delay (Days)"].sum())
        top_two = risk_tbl.head(2)
        contrib_lines = ""
        for _, r in top_two.iterrows():
            share = 100 * df[df["Supplier"] == r["Supplier"]]["Delay (Days)"].sum() / max(total_delay_days, 1)
            contrib_lines += f"<li>{r['Supplier']} contributes {share:.0f}% of total delay days.</li>"
        st.markdown(f"""
        <ul class="card-scroll" style="margin:0; padding-left:14px;">
            <li>{pct_delayed_overall:.0f}% of deliveries arrived late this period.</li>
            {contrib_lines}
            <li>Governance review recommended for {top_supplier}.</li>
        </ul>
        """, unsafe_allow_html=True)

with col8:
    with st.container(border=True):
        st.markdown('<div class="card-title">📝 Executive Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <p class="card-scroll" style="margin:0 0 4px 0;">
        {len(delayed)}/{total_deliveries} delayed ({on_time_pct:.0f}% on-time). Avg {avg_delay:.2f}d, max {max_delay}d.
        {top_supplier} is highest risk.
        </p>
        """, unsafe_allow_html=True)
        e1, e2, e3, e4 = st.columns(4)
        e1.metric("Delay Days", total_delay_days)
        e2.metric("On-Time %", f"{on_time_pct:.0f}%")
        e3.metric("Avg (d)", f"{avg_delay:.2f}")
        e4.metric("Max (d)", f"{max_delay}")

with col9:
    with st.container(border=True):
        st.markdown('<div class="card-title">✅ Recommended Actions</div>', unsafe_allow_html=True)
        actions = [
            ("Supplier Escalation Review for high-risk suppliers", "SCM"),
            ("Enhance inbound visibility with daily ETA monitoring", "Logistics"),
            ("Monitor critical and high-value materials closely", "Planning"),
            ("Implement supplier performance scorecards", "Quality"),
            ("Strengthen exception management and alerting", "IT"),
        ]
        rows_html = ""
        for i, (act, owner) in enumerate(actions, 1):
            rows_html += (
                f'<div style="display:flex; justify-content:space-between; align-items:center; '
                f'margin-bottom:2px;"><span><b>{i}.</b> {act}</span>'
                f'<span style="background:{PRIMARY_GREEN}1A; color:{PRIMARY_GREEN}; padding:1px 6px; '
                f'border-radius:8px; font-size:0.62rem; font-weight:600; white-space:nowrap; margin-left:6px;">'
                f'{owner}</span></div>'
            )
        st.markdown(f'<div class="card-scroll">{rows_html}</div>', unsafe_allow_html=True)
