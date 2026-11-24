"""Connexion par e-mail et mot de passe pour SolarScope AI.

Les comptes sont stockés dans `users.json` (à côté de l'application), avec un mot de passe haché
(PBKDF2-SHA256, 200 000 itérations, sel aléatoire). Ce mécanisme convient à un usage local ou de
démonstration ; pour une mise en production, utiliser un fournisseur d'identité (OIDC via st.login).
"""
import hashlib
import hmac
import json
import os
import re
import tempfile

import streamlit as st

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD = 8
ITERATIONS = 200_000


def _load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_users(users):
    folder = os.path.dirname(USERS_FILE)
    fd, tmp = tempfile.mkstemp(dir=folder, suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    os.replace(tmp, USERS_FILE)


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS).hex()


def valid_email(email):
    return bool(EMAIL_RE.match(email.strip()))


def register(email, name, password):
    """Crée un compte. Retourne (ok, message)."""
    email = email.strip().lower()
    if not valid_email(email):
        return False, "Adresse e-mail invalide."
    if len(password) < MIN_PASSWORD:
        return False, f"Le mot de passe doit contenir au moins {MIN_PASSWORD} caractères."
    users = _load_users()
    if email in users:
        return False, "Un compte existe déjà avec cette adresse."
    salt = os.urandom(16)
    users[email] = {"name": name.strip() or email.split("@")[0],
                    "salt": salt.hex(), "hash": _hash(password, salt)}
    _save_users(users)
    return True, "Compte créé."


def authenticate(email, password):
    """Vérifie les identifiants. Retourne (ok, nom ou message d'erreur)."""
    email = email.strip().lower()
    user = _load_users().get(email)
    if user is None:
        return False, "E-mail ou mot de passe incorrect."
    candidate = _hash(password, bytes.fromhex(user["salt"]))
    if not hmac.compare_digest(candidate, user["hash"]):
        return False, "E-mail ou mot de passe incorrect."
    return True, user["name"]


def current_user():
    return st.session_state.get("user")


def login_user(email, name):
    st.session_state["user"] = {"email": email.strip().lower(), "name": name}


def logout_user():
    st.session_state.pop("user", None)


def require_login():
    """Protège une page : arrête l'exécution si l'utilisateur n'est pas connecté."""
    if current_user() is None:
        st.warning("Connectez-vous pour accéder à cette page.", icon=":material/lock:")
        st.page_link("pages/login.py", label="Aller à la connexion", icon=":material/login:")
        st.stop()
