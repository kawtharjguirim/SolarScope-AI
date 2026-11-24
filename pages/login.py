import streamlit as st

from auth import authenticate, current_user, login_user, register, valid_email
from components import theme

theme.inject()
theme.brand("WELCOME BACK")
st.write("")

if current_user() is not None:
    st.success("Vous êtes déjà connecté.", icon=":material/check_circle:")
    if st.button("Ouvrir le tableau de bord", icon=":material/dashboard:"):
        st.switch_page("pages/1_Vue_generale.py")
    st.stop()

left, right = st.columns([1, 1], gap="large")

with left, st.container(border=True):
    st.markdown("### Accès à SolarScope AI")
    tab_in, tab_up = st.tabs(["Se connecter", "Créer un compte"])

    with tab_in:
        with st.form("form_login", border=False):
            email = st.text_input("Adresse e-mail", placeholder="nom@exemple.com", key="login_email")
            password = st.text_input("Mot de passe", type="password", key="login_password",
                                     help="Utilisez l'icône œil pour afficher ou masquer le mot de passe.")
            submitted = st.form_submit_button("Se connecter", type="primary",
                                              icon=":material/login:", width="stretch")
        if submitted:
            if not valid_email(email or ""):
                st.error("Saisissez une adresse e-mail valide.", icon=":material/error:")
            elif not password:
                st.error("Saisissez votre mot de passe.", icon=":material/error:")
            else:
                ok, info = authenticate(email, password)
                if ok:
                    login_user(email, info)
                    st.switch_page("pages/home.py")
                else:
                    st.error(info, icon=":material/error:")

    with tab_up:
        with st.form("form_signup", border=False):
            name = st.text_input("Nom affiché", key="signup_name")
            email_up = st.text_input("Adresse e-mail", key="signup_email")
            pw1 = st.text_input("Mot de passe (8 caractères minimum)", type="password", key="signup_pw1")
            pw2 = st.text_input("Confirmer le mot de passe", type="password", key="signup_pw2")
            created = st.form_submit_button("Créer mon compte", type="primary",
                                            icon=":material/person_add:", width="stretch")
        if created:
            if pw1 != pw2:
                st.error("Les mots de passe ne correspondent pas.", icon=":material/error:")
            else:
                ok, msg = register(email_up, name, pw1)
                if ok:
                    st.success("Compte créé. Vous pouvez maintenant vous connecter.",
                               icon=":material/check_circle:")
                else:
                    st.error(msg, icon=":material/error:")

with right, st.container(border=True):
    st.markdown("### Pourquoi un compte ?")
    st.markdown(
        "- Accès aux **prévisions** Q10, Q50 et Q90 par site et par période.\n"
        "- Consultation des **résultats** et des **méthodes** des axes 1 à 4.\n"
        "- Export des données filtrées au format CSV."
    )
    st.info("Authentification locale : les comptes sont stockés dans `users.json` avec mot de passe haché. "
            "Ce mécanisme convient à une démonstration, pas à une mise en production.",
            icon=":material/info:")
    st.caption("Connexion Google non affichée : aucun fournisseur OAuth n'est configuré dans ce projet.")
