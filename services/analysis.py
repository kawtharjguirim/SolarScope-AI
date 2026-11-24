"""Indicateurs calculés à partir des données réelles (affichés avec leur libellé « calculé »)."""
import numpy as np
import streamlit as st

from services import metrics
from services.data_loader import observations, quantile_predictions, ridge_predictions


@st.cache_data(show_spinner=False)
def observation_stats(site):
    """Statistiques sur l'ensemble des jours observés du site (ALLSKY)."""
    obs = observations(site)
    if obs is None:
        return None
    s = obs["ALLSKY_SFC_SW_DWN"].dropna()
    return {
        "n_obs": int(s.size),
        "first": s.index.min().date(),
        "last": s.index.max().date(),
        "median": float(s.median()),
        "mean": float(s.mean()),
        "std": float(s.std()),
        "min": float(s.min()),
        "max": float(s.max()),
    }


@st.cache_data(show_spinner=False)
def test_quality(site):
    """Qualité du quantile sans contrainte (axe 2) sur le test, recalculée depuis les prédictions."""
    p = quantile_predictions(site)
    if p is None:
        return None
    y, q10, q50, q90 = p["observe"].to_numpy(), p["q10"].to_numpy(), p["q50"].to_numpy(), p["q90"].to_numpy()
    return {
        "n_test": int(len(p)),
        "coverage": metrics.coverage(y, q10, q90),
        "width": metrics.width(q10, q90),
        "crossings": metrics.crossings(q10, q50, q90),
        "pinball_q10": metrics.pinball(y, q10, 0.1),
        "pinball_q50": metrics.pinball(y, q50, 0.5),
        "pinball_q90": metrics.pinball(y, q90, 0.9),
        "couv_q10": float(np.mean(y <= q10)),
        "couv_q90": float(np.mean(y <= q90)),
        "rmse_q50": metrics.rmse(y, q50),
        "rmse_naive": metrics.rmse(y, p["naif"].to_numpy()),
    }


@st.cache_data(show_spinner=False)
def ridge_quality(site):
    p = ridge_predictions(site)
    if p is None:
        return None
    y = p["observe"].to_numpy()
    return {"rmse_ridge": metrics.rmse(y, p["ridge"].to_numpy()),
            "rmse_naive": metrics.rmse(y, p["naif"].to_numpy())}
