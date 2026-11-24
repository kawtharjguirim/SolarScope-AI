"""SolarScope AI — point d'entrée de l'application.

Lancement (dans le dossier du projet, avec le Python du .venv) :
    python -m streamlit run app.py
"""
import streamlit as st

from components import theme
from services.data_loader import SITES

st.set_page_config(
    page_title="SolarScope AI",
    page_icon=":material/wb_sunny:",
    layout="wide",
    initial_sidebar_state="expanded",
)

home = st.Page("pages/home.py", title="Accueil", icon=":material/home:", default=True)
overview = st.Page("pages/1_Vue_generale.py", title="Vue générale", icon=":material/dashboard:")
forecast = st.Page("pages/2_Prevision.py", title="Prévision solaire", icon=":material/timeline:")
sites = st.Page("pages/3_Sites_climat.py", title="Sites & climat", icon=":material/public:")
evaluation = st.Page("pages/4_Evaluation.py", title="Évaluation du modèle", icon=":material/verified:")
optimization = st.Page("pages/5_Optimisation.py", title="Analyse d'optimisation", icon=":material/show_chart:")
constraints = st.Page("pages/6_Contraintes.py", title="Contraintes physiques", icon=":material/shield:")
about = st.Page("pages/7_A_propos.py", title="À propos du projet", icon=":material/info:")

nav = st.navigation(
    {
        "Espace": [home],
        "Tableau de bord": [overview, forecast, sites],
        "Analyse scientifique": [evaluation, optimization, constraints],
        "Projet": [about],
    },
    position="sidebar",
)

with st.sidebar:
    theme.brand()
    st.write("")
    st.selectbox("Site", SITES, key="site", help="Met à jour toutes les visualisations.")

nav.run()
