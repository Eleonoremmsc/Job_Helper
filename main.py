import streamlit as st
import streamlit_authenticator as stauth
from auth_config import load_auth_config
import yaml
from yaml.loader import SafeLoader
import bcrypt
from utils import load_user_data, save_user_data

# Load credentials
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize session state
if "login_success" not in st.session_state:
    st.session_state.login_success = False

if not st.session_state.login_success:
    st.title("🔐 Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    login_button = st.button("Se connecter")

    if login_button:
        user_info = config["credentials"]["usernames"].get(username)
        if user_info and bcrypt.checkpw(password.encode(), user_info["password"].encode()):
            # Save login info to session
            st.session_state.login_success = True
            st.session_state.username = username
            st.session_state.name = user_info["name"]

            # Load saved user data from disk
            all_data = load_user_data()
            st.session_state.user_data = all_data.get(username, {})
            st.rerun()
        else:
            st.error("Identifiants incorrects")

else:
    st.sidebar.write(f"👤 Connecté en tant que {st.session_state.name}")
    if st.sidebar.button("Se déconnecter"):
        st.session_state.clear()
        st.rerun()

    # Run app
    from job_helper_app import run_job_helper_app
    run_job_helper_app()
