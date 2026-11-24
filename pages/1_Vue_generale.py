import pandas as pd
import streamlit as st

from components import charts, theme
from components.page import no_data, setup
from services import analysis
from services.data_loader import observations, quantile_predictions, site_meta, SITES, TARGET_COVERAGE

site = setup()
theme.header("Vue générale", "Synthèse du projet et du site sélectionné, calculée à partir des données réelles.",
             eyebrow="Tableau de bord")

stats = analysis.observation_stats(site)
quality = analysis.test_quality(site)
meta = site_meta()

if stats is None or quality is None:
    no_data(f"Données du site « {site} » indisponibles (fichier observé ou prédictions absent).")
    st.stop()

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    theme.kpi("Site sélectionné", site, help_text="Sélectionnez un autre site dans la barre latérale.")
with k2:
    theme.kpi("Observations", f"{stats['n_obs']:,}".replace(",", " "),
              help_text=f"Jours avec rayonnement mesuré, du {stats['first']} au {stats['last']}.")
with k3:
    theme.kpi("Rayonnement médian", f"{stats['median']:.2f}", help_text="kWh/m²/j, calculé sur tous les jours observés.")
with k4:
    theme.kpi("Couverture [Q10 ; Q90]", f"{quality['coverage']:.1%}",
              help_text=f"Test ({quality['n_test']} jours). Cible : {TARGET_COVERAGE:.0%}.",
              delta=f"{quality['coverage'] - TARGET_COVERAGE:+.1%} vs cible", delta_color="normal")
with k5:
    theme.kpi("Largeur moyenne", f"{quality['width']:.2f}", help_text="kWh/m²/j, moyenne de Q90 − Q10 sur le test.")
with k6:
    theme.kpi("Quantiles", "3", help_text="Q10 (bas), Q50 (médian), Q90 (haut).")

left, right = st.columns([1.2, 1], gap="medium")
with left, st.container(border=True):
    st.markdown("**Sites d'étude**")
    st.plotly_chart(charts.map_sites(meta, selected=site), width="stretch",
                    config={"displaylogo": False}, key="map_overview")
    st.caption("Coordonnées issues de resultats_groupe.csv ; site sélectionné en cyan.")
with right, st.container(border=True):
    st.markdown(f"**Distribution du rayonnement observé — {site}**")
    obs = observations(site)["ALLSKY_SFC_SW_DWN"].dropna()
    st.plotly_chart(charts.histogram(obs.values, height=330), width="stretch",
                    config={"displaylogo": False}, key="hist_overview")
    s1, s2, s3 = st.columns(3)
    s1.metric("Moyenne", f"{stats['mean']:.2f}")
    s2.metric("Écart-type", f"{stats['std']:.2f}")
    s3.metric("Min – Max", f"{stats['min']:.2f} – {stats['max']:.2f}")

st.markdown("**Comparaison des sites**")
rows = []
for name in SITES:
    st_ = analysis.observation_stats(name)
    q_ = analysis.test_quality(name)
    m_ = meta[meta["site"] == name]
    if st_ is None or q_ is None or m_.empty:
        continue
    rows.append({
        "Site": name,
        "Pays": m_["pays"].iloc[0],
        "Zone climatique": m_["zone_carte"].iloc[0],
        "Observations": st_["n_obs"],
        "Rayonnement médian": round(st_["median"], 2),
        "Couverture [Q10 ; Q90]": round(q_["coverage"], 4),
        "Largeur moyenne": round(q_["width"], 3),
        "RMSE médiane": round(q_["rmse_q50"], 3),
    })
table = pd.DataFrame(rows)
if table.empty:
    no_data("Aucune donnée de comparaison disponible.")
else:
    st.dataframe(table, width="stretch", hide_index=True,
                 column_config={"Couverture [Q10 ; Q90]": st.column_config.ProgressColumn(
                     "Couverture [Q10 ; Q90]", format="%.1f", min_value=0, max_value=1)})
    st.caption("Couverture et largeur recalculées sur le test à partir des prédictions de l'axe 2 ; "
               "cible de couverture : 80 %.")
