"""Étapes communes à toutes les pages du tableau de bord."""
import streamlit as st

from components import theme
from services.data_loader import SITES


def current_site():
    """Site sélectionné dans la barre latérale (défaut : Monastir)."""
    site = st.session_state.get("site", SITES[0])
    return site if site in SITES else SITES[0]


def setup():
    """Charte et site courant. Retourne le site courant."""
    theme.inject()
    return current_site()


def no_data(message):
    theme.empty_state(message)
