import pandas as pd
import streamlit as st

from components import charts, theme
from components.page import no_data, setup
from services import metrics
from services.data_loader import (SITES, TARGET_COVERAGE, aci_table, calibration_table, cqr_seeds,
                                  intervals)

site = setup()
theme.header("Évaluation du modèle",
             "Intervalles brut, gaussien et CQR (axe 4) : couverture, largeur, erreur de couverture et variabilité entre graines.",
             eyebrow="Analyse scientifique")

iv = intervals(site)
seeds = cqr_seeds()
if iv is None:
    no_data(f"Intervalles de « {site} » non disponibles. Relancez axe4_cqr.py pour les exporter.")
    st.stop()

y = iv["observe"].to_numpy()
brut_cov = metrics.coverage(y, iv["brut_bas"].to_numpy(), iv["brut_haut"].to_numpy())
brut_wid = metrics.width(iv["brut_bas"].to_numpy(), iv["brut_haut"].to_numpy())
gauss_cov = metrics.coverage(y, iv["gauss_bas"].to_numpy(), iv["gauss_haut"].to_numpy())
gauss_wid = metrics.width(iv["gauss_bas"].to_numpy(), iv["gauss_haut"].to_numpy())

seed_cols = sorted({c.split("_g")[1] for c in iv.columns if c.startswith("cqr_bas_g")}, key=int)
cqr_cov_seed, cqr_wid_seed = [], []
for s in seed_cols:
    lo, hi = iv[f"cqr_bas_g{s}"].to_numpy(), iv[f"cqr_haut_g{s}"].to_numpy()
    cqr_cov_seed.append(metrics.coverage(y, lo, hi))
    cqr_wid_seed.append(metrics.width(lo, hi))
cqr_cov = pd.Series(cqr_cov_seed)
cqr_wid = pd.Series(cqr_wid_seed)

k1, k2, k3, k4 = st.columns(4)
with k1:
    theme.kpi("Cible de couverture", f"{TARGET_COVERAGE:.0%}", help_text="Intervalle à 80 % (niveau 1 − α, α = 0,2).")
with k2:
    theme.kpi("Couverture brute", f"{brut_cov:.1%}", help_text="Quantiles 0,1 et 0,9 sans calibration.",
              delta=f"{brut_cov - TARGET_COVERAGE:+.1%}", delta_color="normal")
with k3:
    theme.kpi("CQR · moyenne (graines)", f"{cqr_cov.mean():.1%}",
              help_text=f"Moyenne sur {len(seed_cols)} graines ; écart-type {cqr_cov.std(ddof=1):.2%}.",
              delta=f"{cqr_cov.mean() - TARGET_COVERAGE:+.1%}", delta_color="normal")
with k4:
    theme.kpi("Largeur CQR", f"{cqr_wid.mean():.2f} kWh/m²/j",
              help_text=f"Brut : {brut_wid:.2f} kWh/m²/j.")

methods = pd.DataFrame({
    "Méthode": ["Brut (quantiles 0,1 et 0,9)", "Gaussien ridge ±1,28σ", "CQR (moyenne des graines)"],
    "Couverture": [brut_cov, gauss_cov, cqr_cov.mean()],
    "Erreur de couverture": [brut_cov - TARGET_COVERAGE, gauss_cov - TARGET_COVERAGE,
                             cqr_cov.mean() - TARGET_COVERAGE],
    "Largeur (kWh/m²/j)": [brut_wid, gauss_wid, cqr_wid.mean()],
    "Écart-type couverture": [None, None, cqr_cov.std(ddof=1)],
})

left, right = st.columns([1.1, 1], gap="medium")
with left, st.container(border=True):
    st.markdown(f"**Comparaison des méthodes — {site}**")
    st.plotly_chart(charts.bars(methods["Méthode"], {"Couverture": methods["Couverture"].tolist()},
                                height=340, yaxis_title="Couverture", yaxis_format=".0%",
                                colors=["#8B7CFF"]), width="stretch",
                    config={"displaylogo": False}, key="eval_cov")
    st.caption(f"La ligne de référence est la cible de {TARGET_COVERAGE:.0%}. Une barre sous la cible sous-couvre le test.")
with right, st.container(border=True):
    st.markdown(f"**Largeur des intervalles — {site}**")
    st.plotly_chart(charts.bars(methods["Méthode"], {"Largeur": methods["Largeur (kWh/m²/j)"].tolist()},
                                height=340, yaxis_title="kWh/m²/j", colors=["#FFC66D"]),
                    width="stretch", config={"displaylogo": False}, key="eval_wid")

st.dataframe(methods, width="stretch", hide_index=True,
             column_config={"Couverture": st.column_config.NumberColumn(format="%.4f"),
                            "Erreur de couverture": st.column_config.NumberColumn(format="%+.4f"),
                            "Largeur (kWh/m²/j)": st.column_config.NumberColumn(format="%.3f"),
                            "Écart-type couverture": st.column_config.NumberColumn(format="%.4f")})

st.markdown("**Variabilité entre graines (CQR)**")
seed_df = pd.DataFrame({"Graine": [int(s) for s in seed_cols], "Couverture": cqr_cov_seed,
                        "Largeur": cqr_wid_seed})
with st.container(border=True):
    st.plotly_chart(charts.bars(seed_df["Graine"].astype(str), {"Couverture": seed_df["Couverture"].tolist()},
                                height=300, yaxis_title="Couverture", yaxis_format=".0%", colors=["#45D6D0"]),
                    width="stretch", config={"displaylogo": False}, key="eval_seeds")
    st.caption("Chaque graine tire un sous-échantillon d'apprentissage différent (80 %) ; la calibration est fixe.")

st.markdown("**Performance par site (CQR, 5 graines)**")
if seeds is None:
    no_data("axe4_graines.csv non disponible : performance par site indisponible.")
else:
    summary = (seeds.groupby("site").agg(couverture_moyenne=("couverture", "mean"),
                                        ecart_type=("couverture", "std"),
                                        largeur_moyenne=("largeur", "mean"))
               .reindex([s for s in SITES if s in set(seeds["site"])]).reset_index())
    st.dataframe(summary, width="stretch", hide_index=True,
                 column_config={"couverture_moyenne": st.column_config.NumberColumn(format="%.4f"),
                                "ecart_type": st.column_config.NumberColumn(format="%.4f"),
                                "largeur_moyenne": st.column_config.NumberColumn(format="%.3f")})
    st.caption("Tamanrasset : couverture sous la cible. La garantie CQR suppose que calibration (2023) et test sont échangeables ; "
               "ce n'est pas vérifié ici.")

st.markdown("**Expériences complémentaires**")
c1, c2 = st.columns(2, gap="medium")
with c1, st.container(border=True):
    st.markdown("Calibration selon la durée (Monastir)")
    cal = calibration_table()
    if cal is None:
        no_data("Résultats de calibration non exportés (axe4_calibration_monastir.csv manquant).")
    else:
        st.dataframe(cal, width="stretch", hide_index=True)
with c2, st.container(border=True):
    st.markdown("ACI : suivi en ligne (Monastir)")
    aci = aci_table()
    if aci is None:
        no_data("Résultats ACI non exportés (axe4_aci_monastir.csv manquant).")
    else:
        st.dataframe(aci, width="stretch", hide_index=True)
st.caption("Calibration et ACI ne sont exportés que pour Monastir : ces comparaisons ne sont pas disponibles pour les autres sites.")
