import streamlit as st
import streamlit_authenticator as stauth
from auth_config import load_auth_config
from job_helper_app import run_job_helper_app
import yaml
from yaml.loader import SafeLoader
st.write(stauth.__version__)

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    'cookie_name',
    'cookie_key',
    cookie_expiry_days=30
)

name, authentication_status = authenticator.login("main", "Connexion")
username = authenticator.username

if authentication_status:
    username = st.session_state["username"]
    st.success(f"Bienvenue {name} 👋 (utilisateur: {username})")
    authenticator.logout("Se déconnecter", "sidebar")
    run_job_helper_app()
elif authentication_status is False:
    st.error("Mot de passe incorrect")
elif authentication_status is None:
    st.warning("Entrez vos identifiants")
