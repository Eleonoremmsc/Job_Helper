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


client = get_gspread_client()
sheet = client.open("Job_Assistant_Users").worksheet("Users") 


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
        
    if st.sidebar.button("Créer un compte"):
        create_account()
        st.stop()
        
    # Show sidebar menu
    menu_option = st.sidebar.radio("Menu", ["📄 Mon CV", "📂 Mes candidatures", "🎤 Préparation aux entretiens"])

    if menu_option == "📄 Mon CV":
        run_job_helper_app()

    elif menu_option == "📂 Mes candidatures":
        st.subheader("📂 Mes candidatures")
        st.write("À venir : un espace pour voir, modifier et suivre vos candidatures envoyées.")

    elif menu_option == "🎤 Préparation aux entretiens":
        st.subheader("🎤 Préparation aux entretiens")
        st.write("Fonctionnalité en cours de développement : exemples de questions, enregistrement vocal, et retours personnalisés.")
