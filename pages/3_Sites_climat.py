import pandas as pd
import streamlit as st

from components import charts, theme
from components.page import no_data, setup
from services import analysis
from services.data_loader import SITES, TARGET_COVERAGE, observations, site_meta

site = setup()
theme.header("Sites & climat", "Localisation, climat et performance des trois sites, à partir des résultats réels.",
             eyebrow="Tableau de bord")

meta = site_meta()
if meta.empty:
    no_data("resultats_groupe.csv est introuvable : métadonnées des sites indisponibles.")
    st.stop()

rows = []
for name in SITES:
    m = meta[meta["site"] == name]
    s = analysis.observation_stats(name)
    q = analysis.test_quality(name)
    r = analysis.ridge_quality(name)
    if m.empty or s is None or q is None or r is None:
        continue
    rows.append({
        "Site": name,
        "Pays": m["pays"].iloc[0],
        "Latitude": float(m["lat"].iloc[0]),
        "Longitude": float(m["lon"].iloc[0]),
        "Zone climatique (carte)": m["zone_carte"].iloc[0],
        "Zone climatique (NASA)": m["zone_nasa"].iloc[0],
        "Observations": s["n_obs"],
        "Rayonnement moyen": round(s["mean"], 3),
        "RMSE ridge": round(r["rmse_ridge"], 4),
        "RMSE naïf": round(r["rmse_naive"], 4),
        "Couverture [Q10 ; Q90]": round(q["coverage"], 4),
        "Largeur": round(q["width"], 3),
    })
table = pd.DataFrame(rows)

left, right = st.columns([1, 1], gap="medium")
with left, st.container(border=True):
    st.markdown("**Carte des sites**")
    st.plotly_chart(charts.map_sites(meta, selected=site), width="stretch",
                    config={"displaylogo": False}, key="map_sites")
with right, st.container(border=True):
    st.markdown("**Performance comparée**")
    if table.empty:
        no_data("Aucune performance disponible.")
    else:
        st.plotly_chart(charts.bars(table["Site"], {
            "RMSE ridge": table["RMSE ridge"].tolist(),
            "RMSE naïf": table["RMSE naïf"].tolist(),
        }, height=380, yaxis_title="RMSE (kWh/m²/j)"), width="stretch",
            config={"displaylogo": False}, key="bars_rmse")

st.markdown("**Fiche comparative**")
if table.empty:
    no_data("Tableau comparatif indisponible.")
else:
    st.dataframe(table, width="stretch", hide_index=True,
                 column_config={"Couverture [Q10 ; Q90]": st.column_config.NumberColumn(format="%.3f")})
    st.caption(f"Cible de couverture : {TARGET_COVERAGE:.0%}. Zones : carte Köppen-Geiger (kgcpy) et recalcul "
               "NASA POWER 1991–2020 (identiques pour ces trois sites).")
    c1, c2 = st.columns(2, gap="medium")
    with c1, st.container(border=True):
        st.markdown("**Couverture de l'intervalle par site**")
        st.plotly_chart(charts.bars(table["Site"], {"Couverture": table["Couverture [Q10 ; Q90]"].tolist()},
                                    height=320, yaxis_title="Couverture", yaxis_format=".0%"),
                        width="stretch", config={"displaylogo": False}, key="bars_cov")
    with c2, st.container(border=True):
        st.markdown(f"**Rayonnement mensuel moyen — {site}**")
        obs = observations(site)
        if obs is None:
            no_data(f"Observations de « {site} » indisponibles.")
        else:
            monthly = obs["ALLSKY_SFC_SW_DWN"].groupby(obs.index.month).mean()
            labels = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
            st.plotly_chart(charts.bars([labels[m - 1] for m in monthly.index],
                                        {"Rayonnement moyen": monthly.round(3).tolist()},
                                        height=320, yaxis_title="kWh/m²/j", colors=["#45D6D0"]),
                            width="stretch", config={"displaylogo": False}, key="bars_monthly")
