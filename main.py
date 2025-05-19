import streamlit as st
import streamlit_authenticator as stauth
from auth_config import load_auth_config
import yaml
from yaml.loader import SafeLoader
import bcrypt
from utils.helpers import load_user_data, save_user_data
from create_account import create_account
from utils.gspread_client import get_gspread_client
from job_helper_app import run_job_helper_app
from create_account import create_account


client = get_gspread_client()
sheet = client.open("Job_Assistant_Users").worksheet("Users") 


# Load credentials
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize session state
if "login_success" not in st.session_state:
    st.session_state.login_success = False
    
if st.session_state.get("step") == "create_account":
    create_account()
    st.stop()
    
if not st.session_state.login_success:
    st.title("🔐 Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Se connecter"):
            user_info = config["credentials"]["usernames"].get(username)
            if user_info and bcrypt.checkpw(password.encode(), user_info["password"].encode()):
                st.session_state.login_success = True
                st.session_state.username = username
                st.session_state.name = user_info["name"]

                # Load user data from saved JSON or Google Sheets
                all_data = load_user_data()
                st.session_state.user_data = all_data.get(username, {})
                st.rerun()
            else:
                st.error("Identifiants incorrects")
    with col2:
        if st.button("Créer un compte"):
            st.session_state.step = "create_account"
            st.rerun()

# 🌟 STEP: AFTER LOGIN
else:
    st.sidebar.write(f"👤 Connecté en tant que {st.session_state.name}")
    if st.sidebar.button("Se déconnecter"):
        st.session_state.clear()
        st.rerun()

    menu_option = st.sidebar.radio("Menu", ["📄 Mon CV", "📂 Mes candidatures", "🎤 Préparation aux entretiens"])

    if menu_option == "📄 Mon CV":
        run_job_helper_app()

    elif menu_option == "📂 Mes candidatures":
        st.subheader("📂 Mes candidatures")
        st.write("À venir : un espace pour voir, modifier et suivre vos candidatures envoyées.")

    elif menu_option == "🎤 Préparation aux entretiens":
        st.subheader("🎤 Préparation aux entretiens")
        st.write("Fonctionnalité en cours de développement : exemples de questions, enregistrement vocal, et retours personnalisés.")
