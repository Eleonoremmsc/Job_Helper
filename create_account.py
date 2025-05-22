import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import bcrypt
import uuid
import json
from utils.language import language_selector

language_selector()

def get_worksheet(SPREADSHEET_NAME, SHEET_NAME):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    return sheet

def generate_user_id():
    return str(uuid.uuid4())

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Create account function
def create_account():

    lang = st.session_state.get("lang", "fr")
    
    st.title("Créer un compte" if lang == "fr" else "Create an account")
    
    if st.button("🔐 J'ai déjà un compte" if lang == "fr" else "🔐 I already have an account"):
        st.session_state.step = "login"
        st.rerun()
    
    uid = generate_user_id()
    name = st.text_input("Prénom" if lang == "fr" else "First Name")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe" if lang == "fr" else "Password", type="password")
    confirm = st.text_input("Confirmez le mot de passe" if lang == "fr" else "Confirm password", type="password")
        
    if st.button("Créer mon compte" if lang == "fr" else "Create my account"):
        if not (name and email and password and confirm):
            st.warning("Veuillez remplir tous les champs." if lang == "fr" else "Please fill out all fields.")
            return

        if password != confirm:
            st.error("Les mots de passe ne correspondent pas." if lang == "fr" else "Passwords do not match.")
            return
        SPREADSHEET_NAME = "Job_Assistant_Users"
        SHEET_NAME = "Users"
        sheet = get_worksheet(SPREADSHEET_NAME, SHEET_NAME)
        existing_emails = sheet.col_values(4) 

        if email in existing_emails:
            st.error("Cet email est déjà utilisé." if lang == "fr" else "This email is already used.")
            return

        hashed_pw = hash_password(password)

        new_row = [
            uid,
            name,
            email,
            hashed_pw,
            datetime.now().isoformat(),
            "", "", "", "", "", "", "", "", ""
        ]  # Fill with empty profile fields

        sheet.append_row(new_row)
        st.success("Compte créé avec succès ! Vous êtes maintenant connecté." if lang == "fr" else "Account created successfully! You are now logged in.")
        st.session_state.step = None
        st.rerun()