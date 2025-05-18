import streamlit as st
import streamlit_authenticator as stauth
from auth_config import load_auth_config
from job_helper_app import run_job_helper_app
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    'cookie_name',
    'cookie_key',
    cookie_expiry_days=30
)

name, auth_status, username = authenticator.login("main", "Connexion")


if auth_status:
    st.success(f"Bienvenue {name} 👋")
    authenticator.logout("Se déconnecter", "sidebar")
    run_job_helper_app()
elif auth_status is False:
    st.error("Mot de passe incorrect")
elif auth_status is None:
    st.warning("Entrez vos identifiants")
