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

name, authentication_status, username = authenticator.login(location="main", form_name="Connexion")

if authentication_status == False:
    st.error("Mot de passe incorrect")
elif authentication_status == None:
    st.warning("Entrez vos identifiants")
elif authentication_status:
    authenticator.logout("Se déconnecter", "sidebar")
    st.success(f"Bienvenue {name} 👋")
    run_job_helper_app()
