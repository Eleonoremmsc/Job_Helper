import streamlit as st
import streamlit_authenticator as stauth
from auth_config import load_auth_config
from job_helper_app import run_job_helper_app
import yaml
from yaml.loader import SafeLoader


# Load credentials
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Handle login state
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
            st.session_state.login_success = True
            st.session_state.username = username
            st.session_state.name = user_info["name"]
            st.success(f"Bienvenue {user_info['name']} 👋")
            st.experimental_rerun()
        else:
            st.error("Identifiants incorrects")
else:
    st.sidebar.write(f"👤 Connecté en tant que {st.session_state.name}")
    if st.sidebar.button("Se déconnecter"):
        st.session_state.clear()
        st.experimental_rerun()

    # 👉 Import and run the app
    from job_helper_app import run_job_helper_app
    run_job_helper_app()