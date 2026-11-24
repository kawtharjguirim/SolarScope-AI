import streamlit as st

from components import theme
from services.data_loader import QUANTILES, TARGET_COVERAGE, site_meta

theme.inject()
meta = site_meta()

theme.brand()
st.write("")
left, right = st.columns([1.1, 0.9], gap="large", vertical_alignment="center")
with left:
    st.markdown("<span class='ss-eyebrow'>● Probabilistic solar forecasting · Africa</span>",
                unsafe_allow_html=True)
    st.markdown(
        "<div class='ss-title'>SolarScope <span class='ss-grad'>AI</span></div>"
        "<div class='ss-title ss-grad' style='font-size:1.9rem;letter-spacing:-.8px'>"
        "Anticipating solar radiation.<br>Quantifying uncertainty.<br>Empowering energy decisions.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='ss-lead'>An intelligent probabilistic solar forecasting platform designed to analyze "
        "solar radiation and quantify prediction uncertainty across African climatic regions.</p>",
        unsafe_allow_html=True,
    )
    b1, b2 = st.columns(2)
    with b1:
        st.page_link("pages/1_Vue_generale.py", label="Explorer la plateforme",
                     icon=":material/arrow_forward:", width="stretch")
    with b2:
        st.page_link("pages/7_A_propos.py", label="Découvrir le projet", icon=":material/explore:",
                     width="stretch")

st.write("")
c1, c2, c3 = st.columns(3)
with c1, st.container(border=True):
    st.metric("Study sites", f"{len(meta)}", help="Sites présents dans resultats_groupe.csv.")
with c2, st.container(border=True):
    st.metric("Forecasting quantiles", f"{len(QUANTILES)}", help=" · ".join(QUANTILES))
with c3, st.container(border=True):
    st.metric("Target interval coverage", f"{TARGET_COVERAGE:.0%}",
              help="Cible de couverture de l'intervalle [Q10 ; Q90] (cahier des charges).")

st.markdown("## Features")
features = [
    (":material/location_on:", "Multi-site solar forecasting",
     "Three African sites with different climates, compared on the same test period."),
    (":material/timeline:", "Probabilistic prediction",
     "Q10, Q50 and Q90 quantile forecasts, with the observed radiation on the test period."),
    (":material/verified:", "Model evaluation",
     "Interval coverage, width, and a comparison of raw, Gaussian and conformal (CQR) intervals."),
    (":material/show_chart:", "Optimization analysis",
     "Convergence histories for ridge, quantile and constrained optimization, against theoretical bounds."),
    (":material/shield:", "Physical constraints",
     "Quantile crossings, negative values and clear-sky violations, before and after constraints."),
]
cols = st.columns(3)
for i, (icon, title, text) in enumerate(features):
    with cols[i % 3], st.container(border=True):
        st.markdown(f"#### {icon} {title}")
        st.write(text)

st.markdown(
    "<div class='ss-foot'>© 2026 SolarScope AI · Probabilistic Solar Energy Forecasting in Africa · "
    "Sujet C — Optimisation pour le Machine Learning (5e année Data Sciences et IA) · "
    "Prototype académique</div>",
    unsafe_allow_html=True,
)
