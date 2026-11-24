"""Écriture des sorties réelles des expériences dans le dossier `exports/` (lu par l'application)."""
import os

import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(BASE, "exports")


def out(name, df):
    os.makedirs(EXPORT_DIR, exist_ok=True)
    path = os.path.join(EXPORT_DIR, name)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"Export : {name} ({len(df)} lignes)")
    return path


def date_str(dates):
    return pd.to_datetime(dates).strftime("%Y-%m-%d")
