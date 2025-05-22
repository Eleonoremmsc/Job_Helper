import streamlit as st
import bcrypt
import yaml
from yaml.loader import SafeLoader
from create_account import create_account
from utils.gspread_client import get_gspread_client
from job_helper_app import run_job_helper_app
from motivation_letter import run_applications_page
from utils.helpers import load_user_from_sheet, get_all_user_records
from utils.language import language_selector
import interview_prep

T = {
    "login_title": {"fr": "🔐 Connexion", "en": "🔐 Login"},
    "email": {"fr": "Email", "en": "Email"},
    "password": {"fr": "Mot de passe", "en": "Password"},
    "login": {"fr": "Se connecter", "en": "Log in"},
    "create": {"fr": "Créer un compte", "en": "Create an account"},
    "logout": {"fr": "Se déconnecter", "en": "Log out"},
    "connected_as": {"fr": "👤 Connecté en tant que", "en": "👤 Logged in as"},
    "invalid_login": {"fr": "Identifiants incorrects", "en": "Invalid login credentials"},
    "menu_options": [
        {"fr": "📄 Mon CV", "en": "📄 My CV"},
        {"fr": "📂 Mes candidatures", "en": "📂 My Applications"},
        {"fr": "🎤 Préparation aux entretiens", "en": "🎤 Interview Preparation"}
    ]
}

language_selector()
lang = st.session_state.get("lang", "fr")

client = get_gspread_client()
sheet = client.open("Job_Assistant_Users").worksheet("Users") 

# Initialize session state
if "login_success" not in st.session_state:
    st.session_state.login_success = False
    
if st.session_state.get("step") == "create_account":
    create_account()
    st.stop()
    
if not st.session_state.login_success:
    st.title(T["login_title"][lang])
    email = st.text_input(T["email"][lang]).strip()
    password = st.text_input(T["password"][lang], type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(T["login"][lang]):
            sheet_records= get_all_user_records()
            user_info = next((row for row in sheet_records if row.get("Email", "").strip().lower()==email.strip().lower()), None)

            if user_info and bcrypt.checkpw(password.encode(), user_info["Hashed_Password"].encode()):
                st.session_state.login_success = True
                st.session_state.email = user_info["Email"]
                user_data = load_user_from_sheet(email)
                st.session_state.user_data = user_data
                st.session_state.accepted_suggestions = user_data.get("accepted_suggestions", [])
                st.rerun()
            else:
                st.error(T["invalid_login"][lang])

    with col2:
        if st.button(T["create"][lang]):
            st.session_state.step = "create_account"
            st.rerun()

# 🌟 STEP: AFTER LOGIN
else:
    st.session_state.name = f'{st.session_state.user_data.get("first_name", "")} {st.session_state.user_data.get("last_name", "")}'
    st.sidebar.write(f"{T['connected_as'][lang]} {st.session_state.name}")
    if st.sidebar.button(T["logout"][lang]):
        st.session_state.clear()
        st.rerun()

    menu_labels = [opt[lang] for opt in T["menu_options"]]
    menu_option = st.sidebar.radio("Menu", menu_labels)

    if menu_option == menu_labels[0]:
        run_job_helper_app()

    elif menu_option == menu_labels[1]:
        st.subheader(menu_labels[1])
        run_applications_page()

    elif menu_option == menu_labels[2]:
        st.subheader(menu_labels[2])
        interview_prep()  # ✅ NEW