import streamlit as st

from components import theme
from components.page import setup
from services.data_loader import inventory

setup()
theme.header("À propos du projet", "Probabilistic Solar Energy Forecasting in Africa — Sujet C, "
             "Optimisation pour le Machine Learning (5e année Data Sciences et IA).", eyebrow="Projet")

c1, c2 = st.columns([1.2, 1], gap="medium")
with c1, st.container(border=True):
    st.markdown("### Objectifs de recherche")
    st.write("Prévoir, la veille, le rayonnement solaire journalier (ALLSKY_SFC_SW_DWN, kWh/m²/j) du lendemain "
             "sous forme de trois quantiles (Q10, Q50, Q90), avec une couverture d'intervalle visée de 80 %, "
             "puis vérifier la cohérence physique des prévisions.")
    st.markdown("### Source des données")
    st.write("**NASA POWER** (API journalière, sans compte). Période : 2014-01-01 à 2026-06-30. "
             "Apprentissage : cibles jusqu'au 31/12/2023 ; test : cibles du 01/01/2024 au 30/06/2026.")
    st.markdown("### Sites d'étude")
    st.write("**Monastir** (Tunisie, BSh), **Tamanrasset** (Algérie, BWh), **Dakar** (Sénégal, BSh). "
             "Zones climatiques : carte Köppen-Geiger (kgcpy) et recalcul NASA 1991–2020, identiques ici.")
with c2, st.container(border=True):
    st.markdown("### Méthodologie")
    st.markdown(
        "- **Régression ridge** (axe 1) : descente à pas fixe, pas exact, Armijo, Wolfe, gradient conjugué.\n"
        "- **Régression quantile** (axe 2) : perte pinball, sous-gradient projeté, lissage de Moreau, Newton amorti.\n"
        "- **Contraintes physiques** (axe 3) : non-croisement et bornes de ciel clair, dual et lagrangien augmenté.\n"
        "- **Conformal** (axe 4, piste R3) : CQR et ACI pour garantir la couverture.\n"
    )
    st.caption("Algorithmes écrits à la main en NumPy. scikit-learn, SciPy et cvxpy servent à la vérification.")

st.markdown("### Diagramme de la méthode")
st.graphviz_chart("""
digraph G {
  rankdir=LR; bgcolor="transparent";
  node [shape=box, style="rounded,filled", fontname="Helvetica", fontcolor="#EDF5FF", color="#45D6D0", fillcolor="#10233A"];
  edge [color="#91A6BF", fontcolor="#91A6BF"];
  nasa [label="NASA POWER\\nobservations 2014–2026"];
  feat [label="Variables du jour t\\nmétéo, 3 jours de rayonnement,\\nsaisonnalité"];
  split [label="Découpage sur la date\\nde la cible ALLSKY(t+1)\\napprentissage ≤ 2023 | test 2024–2026"];
  ridge [label="Axe 1 · Ridge\\nλ = 10⁻²"];
  quant [label="Axe 2 · Quantiles Q10 Q50 Q90\\npinball, Moreau, Newton"];
  cons [label="Axe 3 · Contraintes\\nnon-croisement, 0 ≤ q ≤ ciel clair"];
  cqr [label="Axe 4 · CQR / ACI\\ncalibration postérieure"];
  eval [label="Évaluation sur le test\\ncouverture, largeur, pinball"];
  nasa -> feat -> split;
  split -> ridge; split -> quant -> cons; quant -> cqr;
  ridge -> eval; cons -> eval; cqr -> eval;
}
""")

st.markdown("### Fichiers du projet")
inv = inventory()
present = int(inv["présent"].sum())
st.caption(f"{present} fichiers sur {len(inv)} attendus sont présents.")
st.dataframe(inv, width="stretch", hide_index=True,
             column_config={"présent": st.column_config.CheckboxColumn("présent")})
