import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import bcrypt

# Constants
SHEET_NAME = "users"  # Name of your sheet tab

# Setup Google Sheets connection
def get_worksheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("JobHelperDB").worksheet(SHEET_NAME)
    return sheet

# Create account function
def create_account():
    st.title("Créer un compte")

    username = st.text_input("Nom d'utilisateur")
    name = st.text_input("Prénom ou nom complet")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    confirm = st.text_input("Confirmez le mot de passe", type="password")
    
    if st.button("Créer mon compte"):
        if not (username and name and email and password and confirm):
            st.warning("Veuillez remplir tous les champs.")
            return

        if password != confirm:
            st.error("Les mots de passe ne correspondent pas.")
            return

        sheet = get_worksheet()
        existing_usernames = sheet.col_values(1)  # Assuming username is in col 1

        if username in existing_usernames:
            st.error("Ce nom d'utilisateur existe déjà.")
            return

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        new_row = [
            username,
            name,
            email,
            hashed_pw,
            datetime.now().isoformat(),
            "", "", "", "", "", "", "", "", ""
        ]  # Fill with empty profile fields

        sheet.append_row(new_row)
        st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
