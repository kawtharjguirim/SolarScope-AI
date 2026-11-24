import numpy as np
import pandas as pd
import streamlit as st

from components import charts, theme
from components.page import no_data, setup
from services.data_loader import (before_after_table, history_dual, history_ridge, history_subgradient,
                                  minibatch_table, quantile_fstar, smoothing_table, summary)

site = setup()
theme.header("Analyse d'optimisation",
             "Historiques réels des algorithmes des axes 1 à 3. Les bornes théoriques sont calculées dans l'application.",
             eyebrow="Analyse scientifique")

tab1, tab2, tab3 = st.tabs(["Axe 1 · Ridge", "Axe 2 · Régression quantile", "Axe 3 · Contraintes"])

# ---------------------------------------------------------------- axe 1
with tab1:
    hist = history_ridge()
    res1 = summary("axe1_resume.csv")
    if hist is None or res1 is None:
        no_data("Historique de la descente ridge non exporté (axe1_historique_monastir.csv).")
    else:
        row = res1[res1["site"] == "Monastir"]
        kappa = float(row["kappa"].iloc[0]) if not row.empty else None
        methods = list(dict.fromkeys(hist["methode"]))
        curves = {}
        thresholds = {}
        for m in methods:
            h = hist[hist["methode"] == m].sort_values("iteration")
            vals = h["ecart_f_fstar"].to_numpy()
            x = h["iteration"].to_numpy()
            keep = slice(0, min(len(x), 3000))
            curves[m] = (x[keep], vals[keep])
            target = 1e-6 * vals[0]
            idx = np.nonzero(vals <= target)[0]
            thresholds[m] = int(idx[0]) if len(idx) else None
        bound = None
        if kappa:
            k = np.arange(0, 3000)
            bound = (k, (1 - 1 / kappa) ** (2 * k) * hist[hist["methode"] == methods[0]]["ecart_f_fstar"].iloc[0])

        left, right = st.columns([1.5, 1], gap="medium")
        with left, st.container(border=True):
            st.markdown("**Écart à l'optimum f(w_k) − f\\* (Monastir, λ = 10⁻²)**")
            st.plotly_chart(charts.convergence(curves, height=460, bound=bound,
                                               xlabel="itération", ylabel="f(w_k) − f*"),
                            width="stretch", config={"displaylogo": False}, key="conv_ridge")
            st.caption("Courbe pointillée : borne théorique du pas 1/L, (1 − 1/κ)^(2k) × écart initial, "
                       f"avec κ = {kappa:.1f} (axe1_resume.csv). Échelle logarithmique.")
        with right, st.container(border=True):
            st.markdown("**Itérations pour diviser l'écart par 10⁶**")
            tbl = pd.DataFrame({"Méthode": methods,
                                "Itérations observées": [thresholds[m] if thresholds[m] is not None else "non atteint"
                                                         for m in methods]})
            st.dataframe(tbl, width="stretch", hide_index=True)
            st.caption("Lecture sur l'historique exporté (plafond de 20 000 itérations).")
            st.metric("Itérations prédites (pas 1/L)", f"{int(row['iter_pred'].iloc[0])}" if not row.empty else "—",
                      help="Borne théorique au pire cas, exportée par axe1_ridge.py.")

    st.markdown("**Analyse de régularisation (λ ∈ {0 ; 10⁻³ ; 10⁻² ; 10⁻¹})**")
    no_data("Résultats de l'analyse de régularisation non exportés : seul λ = 10⁻² est sauvegardé.")

# ---------------------------------------------------------------- axe 2
with tab2:
    sub = history_subgradient()
    if sub is None:
        no_data("Historique du sous-gradient projeté non exporté (axe2_historique_subgradient_monastir.csv).")
    else:
        st.markdown("**Sous-gradient projeté (τ = 0,5, Monastir) : écart à F\\***")
        st.plotly_chart(charts.convergence({"F(w̄_t) − F*": (sub["iteration"], sub["ecart_F_Fstar"])},
                                           height=380, xlabel="itération t", ylabel="F(w̄_t) − F*"),
                        width="stretch", config={"displaylogo": False}, key="conv_sub")
        st.caption("Une seule courbe est exportée : le sous-gradient n'a été lancé que pour τ = 0,5.")

    c1, c2 = st.columns(2, gap="medium")
    with c1, st.container(border=True):
        st.markdown("**Valeur optimale F\\* et précision de Newton**")
        fs = quantile_fstar()
        if fs is None:
            no_data("Valeurs F* non exportées.")
        else:
            st.dataframe(fs, width="stretch", hide_index=True,
                         column_config={"F_star": st.column_config.NumberColumn("F*", format="%.6f"),
                                        "ecart_newton": st.column_config.NumberColumn("Écart Newton",
                                                                                      format="%.1e")})
    with c2, st.container(border=True):
        st.markdown("**Mini-lots et déterministe, à budget égal**")
        mb = minibatch_table()
        if mb is None:
            no_data("Comparaison des mini-lots non exportée.")
        else:
            st.plotly_chart(charts.bars(mb["methode"], {"Écart à F*": mb["ecart_F_Fstar"].tolist()},
                                        height=280, yaxis_title="F(w̄) − F*", colors=["#FFC66D"]),
                            width="stretch", config={"displaylogo": False}, key="bars_mb")

    st.markdown("**Lissage de Moreau : compromis ε / conditionnement**")
    sm = smoothing_table()
    if sm is None:
        no_data("Tableau de lissage non exporté.")
    else:
        st.dataframe(sm, width="stretch", hide_index=True)
        st.caption("Plus ε diminue, plus κ_ε augmente. Newton amorti reste sous une soixantaine d'itérations.")
    st.markdown("**Évolution de la perte pinball et optimisation de Q10 et Q90**")
    no_data("Historiques d'optimisation pour Q10 et Q90 non exportés.")

# ---------------------------------------------------------------- axe 3
with tab3:
    dual_p = history_dual("projete")
    dual_a = history_dual("accelere")
    al = history_dual("al")
    if dual_p is None or dual_a is None or al is None:
        no_data("Historiques de faisabilité non exportés (axe3_historique_*.csv).")
    else:
        st.markdown("**Faisabilité : violation maximale de CW − b**")
        curves = {
            "Dual projeté (pas 1/L_d)": (dual_p["iteration"], dual_p["violation_max"].clip(lower=1e-16)),
            "Dual accéléré (Nesterov)": (dual_a["iteration"], dual_a["violation_max"].clip(lower=1e-16)),
            "Lagrangien augmenté": (al["iteration"], al["violation_max"].clip(lower=1e-16)),
        }
        st.plotly_chart(charts.convergence(curves, height=400, xlabel="itération",
                                           ylabel="violation maximale"),
                        width="stretch", config={"displaylogo": False}, key="conv_constraints")
        st.caption(f"Lagrangien augmenté : {len(al)} itérations externes. Dual : plafond de {len(dual_p):,} itérations.".replace(",", " "))

    st.markdown("**Avant et après contraintes (test, Monastir)**")
    ba = before_after_table()
    if ba is None:
        no_data("Comparaison avant/après non exportée (axe3_avant_apres_monastir.csv).")
    else:
        st.dataframe(ba, width="stretch", hide_index=True)
    st.markdown("**Évolution de l'objectif pendant l'optimisation**")
    no_data("Historique de l'objectif Φ(W) non exporté pour le lagrangien augmenté.")
