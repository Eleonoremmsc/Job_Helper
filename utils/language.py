import streamlit as st

def language_selector():
    prev_lang = st.session_state.get("lang", "fr")
    lang = st.radio("Choisissez votre langue / Choose your language", ["fr", "en"], horizontal=True)
    if lang != prev_lang:
        st.session_state.lang = lang
        st.rerun()
