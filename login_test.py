import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    'cookie_name', 'signature_key', cookie_expiry_days=30
)

name, auth_status, username = authenticator.login(location='main', form_name='Connexion')

if auth_status:
    st.success(f"Bienvenue {name} !")
    authenticator.logout("Se déconnecter", "sidebar")
elif auth_status is False:
    st.error("Mot de passe incorrect")
elif auth_status is None:
    st.warning("Veuillez vous connecter")
