"""Chargement des données réelles du projet (aucune valeur n'est saisie à la main).

Sources :
- `donnees/<Site>.csv` : observations NASA POWER ;
- `exports/*.csv` : prédictions et historiques écrits par les scripts d'axe ;
- `*_resume.csv`, `resultats_groupe.csv` : tableaux de synthèse.
"""
import os

import numpy as np
import pandas as pd
import streamlit as st

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "donnees")
EXPORT_DIR = os.path.join(BASE, "exports")

SITES = ["Monastir", "Tamanrasset", "Dakar"]
TARGET_COVERAGE = 0.80          # cible de l'intervalle (cahier des charges)
QUANTILES = ("Q10", "Q50", "Q90")  # les trois quantiles du projet


class MissingData(Exception):
    """Un fichier attendu est absent ou ne contient pas les colonnes attendues."""


def _path(folder, name):
    return os.path.join(folder, name)


@st.cache_data(show_spinner=False)
def read_csv(folder, name, required=()):
    """Lit un CSV, vérifie les colonnes requises. Retourne None si le fichier est absent."""
    path = _path(folder, name)
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise MissingData(f"{name} : colonnes absentes {missing}")
    return df


def summary(name):
    return read_csv(BASE, name)


def export(name, required=()):
    return read_csv(EXPORT_DIR, name, required)


# ---------------------------------------------------------------- métadonnées des sites
@st.cache_data(show_spinner=False)
def site_meta():
    """Lat/lon, pays, zone climatique : lus dans resultats_groupe.csv."""
    df = summary("resultats_groupe.csv")
    if df is None:
        return pd.DataFrame(columns=["site", "pays", "lat", "lon", "zone_carte", "zone_nasa"])
    return df[["site", "pays", "lat", "lon", "zone_carte", "zone_nasa"]].drop_duplicates("site")


# ---------------------------------------------------------------- observations
@st.cache_data(show_spinner=False)
def observations(site):
    """Série journalière observée (ALLSKY et CLRSKY) d'un site."""
    path = _path(DATA_DIR, f"{site}.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date")
    cols = ["ALLSKY_SFC_SW_DWN", "CLRSKY_SFC_SW_DWN"]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise MissingData(f"{site}.csv : colonnes absentes {missing}")
    return df[cols].replace(-999.0, np.nan)


# ---------------------------------------------------------------- prédictions (test)
def _predictions(prefix, site, required):
    df = export(f"{prefix}_{site.lower()}.csv", required)
    if df is None:
        return None
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")


@st.cache_data(show_spinner=False)
def quantile_predictions(site):
    """Q10/Q50/Q90 du quantile sans contrainte (axe 2) sur le test."""
    return _predictions("axe2_predictions", site, ["date", "observe", "naif", "q10", "q50", "q90"])


@st.cache_data(show_spinner=False)
def constrained_predictions(site):
    """Quantiles après contraintes (axe 3), avec les versions sans contrainte."""
    return _predictions("axe3_predictions", site,
                        ["date", "observe", "naif", "clr", "q10", "q50", "q90",
                         "q10_sans", "q50_sans", "q90_sans"])


@st.cache_data(show_spinner=False)
def ridge_predictions(site):
    return _predictions("axe1_predictions", site, ["date", "observe", "ridge", "naif"])


@st.cache_data(show_spinner=False)
def intervals(site):
    """Intervalles de l'axe 4 : brut, gaussien, CQR (une colonne par graine)."""
    return _predictions("axe4_intervalles", site, ["date", "observe", "brut_bas", "brut_haut",
                                                    "gauss_bas", "gauss_haut"])


# ---------------------------------------------------------------- historiques d'optimisation
def history_ridge():
    return export("axe1_historique_monastir.csv", ["methode", "iteration", "ecart_f_fstar"])


def history_subgradient():
    return export("axe2_historique_subgradient_monastir.csv", ["iteration", "ecart_F_Fstar"])


def history_dual(kind):
    names = {"projete": "axe3_historique_dual_projete.csv",
             "accelere": "axe3_historique_dual_accelere.csv",
             "al": "axe3_historique_lagrangien_augmente.csv"}
    return export(names[kind], ["iteration", "violation_max"])


def smoothing_table():
    return export("axe2_lissage_monastir.csv")


def quantile_fstar():
    return export("axe2_fstar_monastir.csv", ["tau", "F_star", "ecart_newton"])


def minibatch_table():
    return export("axe2_minibatch_monastir.csv", ["methode", "ecart_F_Fstar"])


def before_after_table():
    return export("axe3_avant_apres_monastir.csv")


# ---------------------------------------------------------------- axe 4 : graines, calibration, ACI
def cqr_seeds():
    return export("axe4_graines.csv", ["site", "graine", "couverture", "largeur"])


def calibration_table():
    return export("axe4_calibration_monastir.csv")


def aci_table():
    return export("axe4_aci_monastir.csv")


# ---------------------------------------------------------------- validation
def inventory():
    """Liste les fichiers attendus et leur statut, pour l'affichage « À propos » et les pages."""
    expected = [
        ("donnees", f"{s}.csv") for s in SITES
    ] + [
        ("", "resultats_groupe.csv"), ("", "axe1_resume.csv"), ("", "axe2_resume.csv"),
        ("", "axe3_resume.csv"), ("", "axe4_resume.csv"),
    ] + [
        ("exports", f"axe2_predictions_{s.lower()}.csv") for s in SITES
    ] + [
        ("exports", f"axe3_predictions_{s.lower()}.csv") for s in SITES
    ] + [
        ("exports", f"axe1_predictions_{s.lower()}.csv") for s in SITES
    ] + [
        ("exports", f"axe4_intervalles_{s.lower()}.csv") for s in SITES
    ] + [
        ("exports", n) for n in [
            "axe1_historique_monastir.csv", "axe2_historique_subgradient_monastir.csv",
            "axe2_lissage_monastir.csv", "axe2_fstar_monastir.csv", "axe2_minibatch_monastir.csv",
            "axe3_historique_dual_projete.csv", "axe3_historique_dual_accelere.csv",
            "axe3_historique_lagrangien_augmente.csv", "axe3_avant_apres_monastir.csv",
            "axe4_graines.csv", "axe4_calibration_monastir.csv", "axe4_aci_monastir.csv",
        ]
    ]
    rows = []
    for folder, name in expected:
        path = _path({"donnees": DATA_DIR, "exports": EXPORT_DIR, "": BASE}[folder], name)
        rows.append({"fichier": name, "dossier": folder or ".", "présent": os.path.exists(path)})
    return pd.DataFrame(rows)
