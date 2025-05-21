import streamlit as st
from openai import OpenAI
import json
import os
from datetime import date
from utils.letter_helpers import extract_job_info_from_link, get_gpt_letter_and_score, save_application_for_user

# Constants
APPLICATIONS_FILE = "user_applications.json"
client = OpenAI(api_key=st.secrets["OPENAI_KEY"])

# Load user applications from disk
def load_applications():
    if os.path.exists(APPLICATIONS_FILE):
        with open(APPLICATIONS_FILE, "r") as f:
            return json.load(f)
    return {}

# Save user applications to disk
def save_applications(data):
    with open(APPLICATIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Generate letter of motivation using GPT
def generate_letter(user_data, offer_link, extra_info):
    profile = f"""
    Nom: {user_data.get('first_name', '')} {user_data.get('last_name', '')}
    Ville: {user_data.get('location', '')}
    Âge: {user_data.get('age', '')}
    Téléphone: {user_data.get('phone', '')}
    Email: {user_data.get('email', '')}
    Description: {user_data.get('description', '')}
    Éducation: {user_data.get('education', '')}
    Compétences: {user_data.get('skills', '')}
    Expérience: {user_data.get('experience', '')}
    """

    prompt = f"""
    Tu es un assistant RH qui aide à rédiger des lettres de motivation professionnelles et personnalisées.
    Voici le profil du candidat :
    {profile}

    Voici le lien de l'offre : {offer_link}
    Voici des informations complémentaires : {extra_info}

    Rédige une lettre de motivation convaincante, claire et adaptée à l'offre.
    Utilise un ton professionnel, et fais au maximum une page.
    Ne copie pas le texte de l'offre, mais montre que la candidate a compris le poste.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# Main Application Page
def run_applications_page():
    user_data = st.session_state.get("user_data", {})
    if not user_data:
        st.warning("Aucun profil trouvé. Veuillez d'abord remplir votre CV dans la section '📄 Mon CV'.")
        st.stop()

    st.title("📂 Mes candidatures")
    user_data = st.session_state.get("user_data", {})
    username = st.session_state.get("email")

    if not username:
        st.warning("Vous devez être connecté pour accéder à cette page.")
        return

    all_apps = load_applications()
    user_apps = all_apps.get(username, [])

    # Sidebar to add new application
    with st.expander("➕ Créer une nouvelle candidature"):
        st.subheader("Nouvelle candidature")
        
        offer_link = st.text_input("🔗 Lien de l'offre")
        job_title = st.text_input("Nom du poste")
        company = st.text_input("Nom de l'entreprise")
        selected_date = st.date_input("Date", value=date.today())
        formatted_date = selected_date.strftime("%d/%m/%Y")
        extra_info = st.text_area("Informations complémentaires (facultatif)")
        
        if st.button("✍️ Générer ma lettre de motivation"):
            if not offer_link:
                st.warning("Merci d'ajouter un lien vers l'offre.")
            else:
                with st.spinner("Rédaction en cours..."):
                    job_data = extract_job_info_from_link(offer_link)
                    gpt_result = get_gpt_letter_and_score(user_data, offer_link, extra_info, job_title, company)
                    st.session_state.generated_letter = gpt_result["letter"]
                    st.session_state.match_score = gpt_result["match_score"]
                    st.session_state.suggestions = gpt_result.get("suggestions", [])
                    st.session_state.application_meta = {
                        "job_title": job_title,
                        "company": company,
                        "date": formatted_date                       
                    }
                    st.rerun()
        elif "generated_letter" in st.session_state:
            st.subheader("📄 Lettre de motivation générée avec succès !")
            
        # Only show this block if match_score exists (i.e., a letter was generated)
    if "match_score" in st.session_state and "generated_letter" in st.session_state:
        match_score = st.session_state.match_score
        st.markdown(f"**Score de compatibilité : {match_score}%**")
        st.progress(int(match_score)/100)

        # If match is <50% : Suggestions
        if (match_score) < 50 and st.session_state.get("suggestions"):
            st.warning("⚠️ Le profil semble peu adapté à cette offre. Suggestions :")
            for sugg in st.session_state.suggestions:
                st.markdown(f"- {sugg}")

        # Editable letter
        letter_text = st.text_area("✏️ Modifiez votre lettre ci-dessous :",
                                    value=st.session_state.generated_letter,
                                    height=500)

        if st.button("💾 Sauvegarder cette candidature"):
            save_application_for_user(
                email=user_data.get("email"),
                job_title=st.session_state.application_meta["job_title"],
                company=st.session_state.application_meta["company"],
                date=st.session_state.application_meta["date"],
                letter=letter_text,
                score=match_score
            )
            st.success("✅ Candidature sauvegardée avec succès.")
            st.session_state.pop("generated_letter")
            st.session_state.pop("match_score")
            st.session_state.pop("application_meta")
            st.rerun()


    st.markdown("---")
    st.subheader("📁 Mes lettres de motivation sauvegardées")
    if user_apps:
        for i, app in enumerate(user_apps[::-1]):
            with st.expander(f"📄 Candidature du {app['date'][:10]}"):
                st.markdown(f"**Lien de l'offre :** [{app['offer_link']}]({app['offer_link']})")
                st.markdown(f"**Informations complémentaires :** {app['extra_info'] or 'Aucune'}")
                st.markdown("---")
                st.text_area("Lettre de motivation :", value=app['letter'], height=300, key=f"letter_{i}")


    else:
        st.info("Aucune candidature enregistrée pour l'instant.")
