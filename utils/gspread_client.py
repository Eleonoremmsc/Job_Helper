import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scopes=scope
    )

    return gspread.authorize(credentials)