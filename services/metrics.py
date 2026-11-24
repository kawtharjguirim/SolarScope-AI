"""Calculs transparents à partir des prédictions réelles (aucune métrique figée)."""
import numpy as np


def pinball(y, q, tau):
    """Perte pinball moyenne du quantile tau."""
    r = y - q
    return float(np.mean(np.maximum(tau * r, (tau - 1) * r)))


def coverage(y, lo, hi):
    """Part des observations dans [lo, hi]."""
    return float(np.mean((y >= lo) & (y <= hi)))


def width(lo, hi):
    return float(np.mean(hi - lo))


def rmse(y, p):
    return float(np.sqrt(np.mean((y - p) ** 2)))


def crossings(q10, q50, q90, tol=1e-9):
    """Nombre de jours où Q10 > Q50 ou Q50 > Q90."""
    return int(np.sum((q10 > q50 + tol) | (q50 > q90 + tol)))


def out_of_bounds(q, lower=0.0, upper=None, tol=1e-9):
    """Nombre de jours où q < lower ou q > upper (upper : rayonnement ciel clair du lendemain)."""
    bad = q < lower - tol
    if upper is not None:
        bad = bad | (q > upper + tol)
    return int(np.sum(bad))


def active_ceiling(q, clr, tol=1e-3):
    """Part des jours où le quantile touche le ciel clair (à tol près)."""
    return float(np.mean(np.abs(q - clr) <= tol))
