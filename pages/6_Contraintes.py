import numpy as np
import pandas as pd
import streamlit as st

from components import charts, theme
from components.page import no_data, setup
from services import metrics
from services.data_loader import SITES, constrained_predictions

site = setup()
theme.header("Contraintes physiques",
             "Cohérence des prévisions : valeurs négatives, dépassement du ciel clair, croisements de quantiles. "
             "Avant et après contraintes (axe 3).",
             eyebrow="Analyse scientifique")


def violations(p, prefix=""):
    """Comptages de violations pour un jeu de quantiles (prefix : '' après contraintes, '_sans' avant)."""
    q10 = p[f"q10{prefix}"].to_numpy()
    q50 = p[f"q50{prefix}"].to_numpy()
    q90 = p[f"q90{prefix}"].to_numpy()
    clr = p["clr"].to_numpy()
    n = len(p)
    neg = int(np.sum((q10 < 0) | (q50 < 0) | (q90 < 0)))
    above = int(np.sum(q90 > clr + 1e-9))
    c1 = int(np.sum(q10 > q50 + 1e-9))
    c2 = int(np.sum(q50 > q90 + 1e-9))
    any_ = metrics.crossings(q10, q50, q90)
    return {
        "Jours": n,
        "Prévisions négatives": neg,
        "Q90 au-dessus du ciel clair": above,
        "Q10 > Q50": c1,
        "Q50 > Q90": c2,
        "Au moins un croisement": any_,
        "Part de jours en violation": (neg + above + any_) / n,
        "Part de jours où Q90 touche le ciel clair": metrics.active_ceiling(q90, clr),
    }


pred = constrained_predictions(site)
if pred is None:
    no_data(f"Prédictions contraintes de « {site} » non disponibles (axe3_predictions_{site.lower()}.csv).")
    st.stop()

before = violations(pred, "_sans")
after = violations(pred, "")

k1, k2, k3, k4 = st.columns(4)
with k1:
    theme.kpi("Croisements avant", f"{before['Au moins un croisement']}",
              help_text="Jours où Q10 > Q50 ou Q50 > Q90, quantiles séparés.")
with k2:
    theme.kpi("Croisements après", f"{after['Au moins un croisement']}",
              help_text="Mêmes jours, après contraintes de non-croisement.")
with k3:
    theme.kpi("Q90 > ciel clair avant", f"{before['Q90 au-dessus du ciel clair']}",
              help_text=f"Sur {before['Jours']} jours de test ({before['Q90 au-dessus du ciel clair'] / before['Jours']:.1%}).")
with k4:
    theme.kpi("Q90 > ciel clair après", f"{after['Q90 au-dessus du ciel clair']}",
              help_text="Après contraintes sur l'apprentissage ; le test peut encore les violer.")

rows = [(k, before[k], after[k]) for k in before if k != "Jours"]
cmp_df = pd.DataFrame(rows, columns=["Indicateur", "Avant contraintes", "Après contraintes"])
left, right = st.columns([1.1, 1], gap="medium")
with left, st.container(border=True):
    st.markdown(f"**Comptages de violations — {site} (test)**")
    counts = cmp_df[cmp_df["Indicateur"].isin(["Prévisions négatives", "Q90 au-dessus du ciel clair",
                                              "Q10 > Q50", "Q50 > Q90"])]
    st.plotly_chart(charts.bars(counts["Indicateur"], {
        "Avant": counts["Avant contraintes"].tolist(),
        "Après": counts["Après contraintes"].tolist(),
    }, height=340, yaxis_title="jours", colors=["#8B7CFF", "#45D6D0"]),
        width="stretch", config={"displaylogo": False}, key="viol_bars")
with right, st.container(border=True):
    st.markdown("**Pourcentages de jours en violation**")
    pct = pd.DataFrame({
        "Indicateur": ["Jours en violation (au moins une)", "Q90 touche le ciel clair"],
        "Avant": [before["Part de jours en violation"], before["Part de jours où Q90 touche le ciel clair"]],
        "Après": [after["Part de jours en violation"], after["Part de jours où Q90 touche le ciel clair"]],
    })
    st.dataframe(pct, width="stretch", hide_index=True,
                 column_config={"Avant": st.column_config.NumberColumn(format="%.2f%%"),
                                "Après": st.column_config.NumberColumn(format="%.2f%%")})
    st.caption("« Touche » : |Q90 − ciel clair| ≤ 10⁻³ kWh/m²/j. Calculé sur le test, à partir des prédictions exportées.")

st.markdown("**Comparaison par site (test)**")
site_rows = []
for name in SITES:
    p = constrained_predictions(name)
    if p is None:
        continue
    b = violations(p, "_sans")
    a = violations(p, "")
    site_rows.append({
        "Site": name,
        "Croisements avant": b["Au moins un croisement"],
        "Croisements après": a["Au moins un croisement"],
        "Q90 > ciel clair avant": b["Q90 au-dessus du ciel clair"],
        "Q90 > ciel clair après": a["Q90 au-dessus du ciel clair"],
        "Prévisions négatives après": a["Prévisions négatives"],
        "Part de jours où Q90 touche le ciel clair (après)": round(a["Part de jours où Q90 touche le ciel clair"], 4),
    })
if not site_rows:
    no_data("Aucune prédiction contrainte disponible pour les sites.")
else:
    st.dataframe(pd.DataFrame(site_rows), width="stretch", hide_index=True)
    st.caption("Limite : après contraintes sur la valeur brute, la prévision se resserre autour de la médiane "
               "(voir la page Analyse d'optimisation). Les conditions KKT sont vérifiées.")
