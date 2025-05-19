import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import bcrypt
import uuid
import json

# Constants
SPREADSHEET_NAME = "Job_Assistant_Users"
SHEET_NAME = "Users"

def get_worksheet():
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
    st.title("Créer un compte")
    
    if st.button("🔐 J'ai déjà un compte"):
        st.session_state.step = "login"
        st.rerun()
    
    uid = generate_user_id()
    name = st.text_input("Prénom")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    confirm = st.text_input("Confirmez le mot de passe", type="password")
        
    if st.button("Créer mon compte"):
        if not (name and email and password and confirm):
            st.warning("Veuillez remplir tous les champs.")
            return

        if password != confirm:
            st.error("Les mots de passe ne correspondent pas.")
            return

        sheet = get_worksheet()
        existing_emails = sheet.col_values(4) 

        if email in existing_emails:
            st.error("Cet email est déjà utilisé.")
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
        st.success("Compte créé avec succès ! Vous êtes maintenant connecté.")
        st.session_state.step = None
        st.rerun()