import numpy as np
import pandas as pd
import streamlit as st

from components import charts, theme
from components.page import no_data, setup
from services import analysis, metrics
from services.data_loader import quantile_predictions

site = setup()
theme.header("Prévision solaire",
             "Quantiles Q10, Q50 et Q90 comparés au rayonnement observé, sur la période de test (2024 à juin 2026).",
             eyebrow="Tableau de bord")

pred = quantile_predictions(site)
if pred is None or pred.empty:
    no_data(f"Prédictions Q10/Q50/Q90 de « {site} » non disponibles. Relancez axe2_quantile.py pour les exporter.")
    st.stop()

d_min, d_max = pred.index.min().date(), pred.index.max().date()
c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
with c1:
    start, end = st.slider("Période d'affichage", min_value=d_min, max_value=d_max, value=(d_min, d_max),
                           format="DD MMM YYYY", key=f"period_{site}")
with c2:
    mode = st.segmented_control("Affichage", ["Intervalle", "Observé seul"], default="Intervalle",
                                key="fc_mode", width="stretch")

sub = pred.loc[pd.Timestamp(start):pd.Timestamp(end)]
if sub.empty:
    no_data("Aucune prévision dans la période choisie.")
    st.stop()

y, q10, q50, q90 = sub["observe"].to_numpy(), sub["q10"].to_numpy(), sub["q50"].to_numpy(), sub["q90"].to_numpy()
cov = metrics.coverage(y, q10, q90)
wid = metrics.width(q10, q90)
rmse_q50 = metrics.rmse(y, q50)
rmse_nv = metrics.rmse(y, sub["naif"].to_numpy())
pin = np.mean([metrics.pinball(y, q10, 0.1), metrics.pinball(y, q50, 0.5), metrics.pinball(y, q90, 0.9)])

k1, k2, k3, k4 = st.columns(4)
with k1:
    theme.kpi("Couverture [Q10 ; Q90]", f"{cov:.1%}", help_text="Calculée sur la période affichée. Cible : 80 %.",
              delta=f"{cov - 0.8:+.1%} vs 80 %", delta_color="normal")
with k2:
    theme.kpi("Largeur moyenne", f"{wid:.2f} kWh/m²/j", help_text="Moyenne de Q90 − Q10.")
with k3:
    theme.kpi("RMSE médiane", f"{rmse_q50:.2f}", help_text="RMSE de Q50 par rapport à l'observé.",
              delta=f"{rmse_q50 - rmse_nv:+.2f} vs naïf", delta_color="inverse")
with k4:
    theme.kpi("Perte pinball moyenne", f"{pin:.3f}", help_text="Moyenne des pertes pinball Q10, Q50 et Q90.")

fig_data = sub.copy()
with st.container(border=True):
    st.markdown(f"**Prévision probabiliste — {site}**")
    if mode == "Observé seul":
        import plotly.graph_objects as go
        fig = go.Figure(go.Scatter(x=sub.index, y=y, name="Observé", line=dict(color="#EDF5FF", width=1.6)))
        fig = charts._layout(fig, 420)
        fig.update_xaxes(rangeslider=dict(visible=False))
    else:
        fig = charts.forecast(sub.index, y, q10, q50, q90, height=460)
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "scrollZoom": True}, key="forecast_fig")
    st.caption("Zoom : glisser sur le graphique ; double-clic pour réinitialiser. "
               "Légende : cliquer sur un élément pour l'afficher ou le masquer.")

    moy = st.columns(3)
    moy[0].metric("Q10 moyen", f"{q10.mean():.2f} kWh/m²/j")
    moy[1].metric("Q50 moyen", f"{q50.mean():.2f} kWh/m²/j")
    moy[2].metric("Q90 moyen", f"{q90.mean():.2f} kWh/m²/j")

col_a, col_b = st.columns([1, 1], gap="medium")
with col_a, st.container(border=True):
    st.markdown("**Comment lire une prévision probabiliste ?**")
    with st.expander("Q10, Q50, Q90 : que signifient-ils ?", expanded=True):
        st.write("- **Q10** : 10 % des jours réels sont en dessous de cette valeur prévue.\n"
                 "- **Q50** : la médiane, une prévision centrale qui sépare les jours en deux moitiés égales.\n"
                 "- **Q90** : 90 % des jours réels sont en dessous de cette valeur prévue.")
    with st.expander("Pourquoi un intervalle plutôt qu'un seul chiffre ?"):
        st.write("Une valeur unique ne dit pas à quel point la prévision est incertaine. L'intervalle "
                 "[Q10 ; Q90] vise 80 % des observations : sa largeur mesure l'incertitude du jour.")
    with st.expander("Lecture de la couverture"):
        st.write(f"Couverture actuelle : **{cov:.1%}** sur la période affichée. Une valeur inférieure à 80 % "
                 "signifie que l'intervalle est trop étroit ; supérieure, qu'il est trop large.")
with col_b, st.container(border=True):
    st.markdown("**Détail par saison**")
    seasons = {12: "DJF", 1: "DJF", 2: "DJF", 3: "MAM", 4: "MAM", 5: "MAM",
               6: "JJA", 7: "JJA", 8: "JJA", 9: "SON", 10: "SON", 11: "SON"}
    table = pd.DataFrame({
        "Saison": [seasons[d.month] for d in sub.index],
        "Couverture": (y >= q10) & (y <= q90),
        "Largeur": q90 - q10,
    }).groupby("Saison").agg(Couverture=("Couverture", "mean"), Largeur=("Largeur", "mean")).reset_index()
    st.dataframe(table, width="stretch", hide_index=True,
                 column_config={"Couverture": st.column_config.NumberColumn(format="%.3f"),
                                "Largeur": st.column_config.NumberColumn(format="%.2f")})

with st.container(border=True):
    st.markdown("**Export des données filtrées**")
    export = fig_data.reset_index().rename(columns={
        "date": "date", "observe": "observé", "naif": "naïf", "q10": "Q10", "q50": "Q50", "q90": "Q90"})
    export["date"] = export["date"].dt.strftime("%Y-%m-%d")
    st.download_button("Télécharger le CSV de la période", data=export.to_csv(index=False).encode("utf-8"),
                       file_name=f"previsions_{site.lower()}_{start}_{end}.csv", mime="text/csv",
                       icon=":material/download:")
    st.caption("Source : exports/axe2_predictions_" + site.lower() + ".csv (prédictions réelles de l'axe 2).")
