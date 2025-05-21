import streamlit as st
import bcrypt
import yaml
from yaml.loader import SafeLoader
from create_account import create_account
from utils.gspread_client import get_gspread_client
from job_helper_app import run_job_helper_app
from create_account import create_account
from motivation_letter import run_applications_page
from utils.helpers import load_user_from_sheet

client = get_gspread_client()
sheet = client.open("Job_Assistant_Users").worksheet("Users") 

# Initialize session state
if "login_success" not in st.session_state:
    st.session_state.login_success = False
    
if st.session_state.get("step") == "create_account":
    create_account()
    st.stop()
    
if not st.session_state.login_success:
    st.title("🔐 Connexion")
    email = st.text_input("Email").strip()
    password = st.text_input("Mot de passe", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Se connecter"):
            sheet_records = sheet.get_all_records()
            user_info = next((row for row in sheet_records if row["Email"].lower().strip() == email.lower().strip()), None)

            if user_info and bcrypt.checkpw(password.encode(), user_info["Hashed_Password"].encode()):
                st.session_state.login_success = True
                st.session_state.email = user_info["Email"]
                st.session_state.user_data = load_user_from_sheet(email)
                st.rerun()
            else:
                st.error("Identifiants incorrects")

    with col2:
        if st.button("Créer un compte"):
            st.session_state.step = "create_account"
            st.rerun()

# 🌟 STEP: AFTER LOGIN
else:
    st.session_state.name = f'{st.session_state.user_data.get("first_name", "")} {st.session_state.user_data.get("last_name", "")}'
    st.sidebar.write(f"👤 Connecté en tant que {st.session_state.name}")
    if st.sidebar.button("Se déconnecter"):
        st.session_state.clear()
        st.rerun()

    menu_option = st.sidebar.radio("Menu", ["📄 Mon CV", "📂 Mes candidatures", "🎤 Préparation aux entretiens"])

    if menu_option == "📄 Mon CV":
        run_job_helper_app()

    elif menu_option == "📂 Mes candidatures":
        st.subheader("📂 Mes candidatures")
        run_applications_page()

    elif menu_option == "🎤 Préparation aux entretiens":
        st.subheader("🎤 Préparation aux entretiens")
        st.write("Fonctionnalité en cours de développement : exemples de questions, enregistrement vocal, et retours personnalisés.")
