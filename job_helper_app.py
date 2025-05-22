import streamlit as st
from openai import OpenAI
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from utils.helpers import load_user_from_sheet, save_user_to_sheet, sync_to_sheet
from datetime import datetime
from PIL import Image
from beautiful_cv import create_beautiful_cv
from xhtml2pdf import pisa
import base64

T = {
    "title": {
        "fr": "Aide à la candidature",
        "en": "Job Application Assistant"
    },
    "no_profile": {
        "fr": "Aucun profil sauvegardé trouvé. Veuillez remplir vos informations.",
        "en": "No saved profile found. Please fill in your information first."
    },
    "loaded": {
        "fr": "✅ Profil chargé automatiquement à partir de vos informations enregistrées.",
        "en": "✅ Profile automatically loaded from saved data."
    },
    "last_update": {
        "fr": "Dernière mise à jour ",
        "en": "Last updated"
    },
    "restart": {
        "fr": "🔄 Recommencer",
        "en": "🔄 Restart"
    },
    "generate_cv": {
        "fr": "➡️ Continuer vers la génération du CV",
        "en": "➡️ Continue to CV generation"
    },
    "download_cv": {
        "fr": "📥 Télécharger mon CV (.pdf)",
        "en": "📥 Download my CV (.pdf)"
    },
    "saved_profile": {
        "fr": "👀 Aperçu de votre profil sauvegardé",
        "en": "👀 Your saved profile",
    },
    "modify": {
        "fr": "✏️ Modifier mes informations",
        "en": "✏️ Modify my saved information"
    },
    "save": {
        "fr": "💾 Enregistrer",
        "en": "💾 Save"      
    },
    "cancel": {
        "fr": "❌ Annuler",
        "en": "❌ Cancel"
    },
    "info_updated": {
        "fr": "✅ Informations mises à jour.",
        "en": "✅ You Information has been updated."
    },
    "error_warning": {
        "fr": "Erreur : adresse email non trouvée en session.",
        "en": "Error: email address not found."
    },
    "profile_analysis": {
        "fr": "Analyse de votre profil pour suggestions...",
        "en": "Analyzing profile for suggestions..."
    },
    "accept": {
        "fr": "✅ Accepter",
        "en": "✅ Accept"
    },
    "modify": {
        "fr": "✏️ Modifier",
        "en": "✏️ Modify"
    },
    "reject": {
        "fr": "❌ Rejeter",
        "en": "❌ Reject"
    },
    "propose_modify": {
        "fr": "Modifier la suggestion :",
        "en": "Modify the suggestion:"
    },
    "generate_pdf": {
        "fr": "➡️ Continuer vers la génération du DOCX",
        "en": "➡️ Continue to DOCX generation"
    },
    "final_result": {
        "fr": "📝 Résultat final",
        "en": "📝 Final Result"
    },
    "modify_cv": {
        "fr": "✏️ Modifiez votre CV (HTML)",
        "en": "✏️ Modify your CV (HTML)"
    },
    "analyse_me": {
        "fr": "Analyser mon profil",
        "en": "Analyse my profile"
    },
    "generate_recs": {
        "fr": "💡 Générer des recommendations",
        "en": "💡 Generate Recommendations"
    },
    "phone": {"fr": "Téléphone", "en": "Phone"},
    "email": {"fr": "Email", "en": "Email"},
    "first_name": {"fr": "Prénom", "en": "First Name"},
    "last_name": {"fr": "Nom", "en": "Last Name"},
    "age": {"fr": "Âge", "en": "Age"},
    "city": {"fr": "Ville", "en": "City"},
    "desc": {"fr": "Décrivez-vous", "en": "Describe yourself"},
    "education": {"fr": "Votre parcours scolaire", "en": "Education"},
    "skills": {"fr": "Vos compétences", "en": "Skills"},
    "experience": {"fr": "Vos expériences professionnelles", "en": "Professional experience"},
    "hobbies": {"fr": "Vos hobbies", "en": "Hobbies"},
    "languages": {"fr": "Quelles langues maîtrisez vous ?", "en": "Languages"},
    "missing_email": {
        "fr": "❗ Email manquant.",
        "en": "❗ Missing email."
    }
}


def run_job_helper_app():
    lang = st.session_state.get("lang", "fr")

    # DEBUG_MODE = True si tu veux modifier l'appli sans utiliser ChatGPT à chaque fois (Tokens)
    DEBUG_MODE = False
    FONT_PATH = "DejaVuSans.ttf"

    # Setup OpenAI
    client = OpenAI(api_key=st.secrets["OPENAI_KEY"])

    # Configuration App Streamlit

    col1, col2 = st.columns([1, 10])
    with col1:
        st.image("assets/red_cross.png", width=40)
    with col2:
        st.title(T["title"][lang])    
            
    user_data = st.session_state.user_data
    if user_data:
        st.success(T["loaded"][lang])
        if "last_updated" in user_data:
            st.caption(f"{T["title"][lang]}: {user_data['last_updated'][:16].replace('T', ' à ')}")
    else:
        st.info(T["no_profile"][lang])

    #if st.button(T["restart"][lang]):
    #    st.session_state.clear()
    #    st.rerun()
        
        

    # Contrôle la progression de l'appli et garde les inputs de l'utilisateur
    if "step" not in st.session_state:
        st.session_state.step = "input_mode"
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    if "recommendations" not in st.session_state:
        st.session_state.recommendations = []
    if "accepted_suggestions" not in st.session_state:
        st.session_state.accepted_suggestions = []


    # Step 1: Choice of input mode
    # Choix pour le user: insérer un texte qui le décrit en total, ou répondre à chaque bloc pour être guidé
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    if st.session_state.step == "input_mode":
        user_data = st.session_state.get("user_data", {})

        # CASE 1 — User has data and is NOT editing
        if user_data and not st.session_state.edit_mode:
            with st.expander(T["saved_profile"][lang]):
                if lang=="en":
                    st.markdown(f"""
                **Name :** {user_data.get("First_Name", "")} {user_data.get("Last_Name", "")}  
                **Phone :** {user_data.get("phone", "")}  
                **Email :** {user_data.get("Email", "")}  
                **City :** {user_data.get("location", "")}  
                **Age :** {user_data.get("age", "")}  
                **Description :** {user_data.get("description", "")[:100]}...
                """)
                else:
                    st.markdown(f"""
                    **Nom :** {user_data.get("First_Name", "")} {user_data.get("Last_Name", "")}  
                    **Téléphone :** {user_data.get("phone", "")}  
                    **Email :** {user_data.get("Email", "")}  
                    **Ville :** {user_data.get("location", "")}  
                    **Âge :** {user_data.get("age", "")}  
                    **Description :** {user_data.get("description", "")[:100]}...
                    """)
                if st.button(T["modify"][lang]):
                    st.session_state.edit_mode = True
                    st.rerun()

        # CASE 2 — User is editing
        elif st.session_state.edit_mode:
            if lang=="en":
                editable_block = st.text_area("Modify your written information :", 
                                          value=
                                          f"""Name: {user_data.get("first_name", "")} {user_data.get("last_name", "")}
                                                Phone: {user_data.get("phone", "")}
                                                Email: {user_data.get("email", "")}
                                                Age: {user_data.get("age", "")}
                                                City: {user_data.get("location", "")}
                                                Description: {user_data.get("description", "")}
                                                Education: {user_data.get("education", "")}
                                                Skills: {user_data.get("skills", "")}
                                                Professional Experience: {user_data.get("experience", "")},
                                                Hobbies: {user_data.get("hobbies", "")},
                                                Languages: {user_data.get("languages", "")}
                                                """, 
                                           height=300)
            else:
                editable_block = st.text_area("Modifiez vos informations textuelles :", 
                                              value=
                                              f"""Nom: {user_data.get("first_name", "")} {user_data.get("last_name", "")}
                                                    Téléphone: {user_data.get("phone", "")}
                                                    Email: {user_data.get("email", "")}
                                                    Âge: {user_data.get("age", "")}
                                                    Ville: {user_data.get("location", "")}
                                                    Description: {user_data.get("description", "")}
                                                    Éducation: {user_data.get("education", "")}
                                                    Compétences: {user_data.get("skills", "")}
                                                    Expérience: {user_data.get("experience", "")},
                                                    Hobbies: {user_data.get("hobbies", "")},
                                                    Langues: {user_data.get("languages", "")}
                                                    """, 
                                               height=300)

            col1, col2 = st.columns(2)
            with col1:
                if st.button(T["save"][lang]):
                    for line in editable_block.strip().split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            key = key.strip().lower()
                            value = value.strip()
                            if "nom" in key:
                                parts = value.split()
                                st.session_state.user_data["first_name"] = parts[0] if parts else ""
                                st.session_state.user_data["last_name"] = " ".join(parts[1:]) if len(parts) > 1 else ""
                            elif "téléphone" in key or "Phone" in key:
                                st.session_state.user_data["phone"] = value
                            elif "email" in key:
                                st.session_state.user_data["email"] = value
                            elif "âge" in key:
                                st.session_state.user_data["age"] = value
                            elif "ville" in key:
                                st.session_state.user_data["location"] = value
                            elif "description" in key:
                                st.session_state.user_data["description"] = value
                            elif "éducation" in key:
                                st.session_state.user_data["education"] = value
                            elif "compétences" in key:
                                st.session_state.user_data["skills"] = value
                            elif "expérience" in key:
                                st.session_state.user_data["experience"] = value
                            elif "hobbies" in key:
                                st.session_state.user_data["hobbies"] = value
                            elif "langues" in key:
                                st.session_state.user_data["languages"] = value

                    st.session_state.user_data["last_updated"] = datetime.now().isoformat()
                    user_email = st.session_state.user_data.get("email")
                    
                    if user_email:
                        save_user_to_sheet(st.session_state.user_data)
                        sync_to_sheet(st.session_state.user_data)
                        st.success(T["info_updated"][lang])
                    else:
                        st.warning(T["missing_email"][lang])
                        st.session_state.edit_mode = False
                        st.rerun()

            with col2:
                if st.button(T["cancel"][lang]):
                    st.session_state.edit_mode = False
                    st.rerun()

        # CASE 3 — Ask input method
        #elif st.session_state.step == "input_mode" and not st.session_state.edit_mode and not st.session_state.user_data.get("summary") and not st.session_state.user_data.get("first_name"):
        else:
            prompt = {
                "fr": "Souhaitez-vous entrer un résumé ou remplir les informations une par une ?",
                "en": "Would you like to enter a summary or fill in your information step by step?"
            }
            mode_options = {
                "fr": ["Résumé global", "Questions une par une"],
                "en": ["Résumé global", "Questions une par une"]  # You can translate if you prefer
            }

            mode = st.radio(prompt[lang], mode_options[lang], key="input_mode_radio")
            st.session_state.input_mode = mode

            if st.button(T["generate_cv"][lang]):
                st.session_state.step = "summary_input" if mode == "Résumé global" else "form_input"

        if st.button(T["generate_recs"][lang]):
            st.session_state.step = "recommend"
            st.rerun()
        if st.button(T["generate_cv"][lang]):
            st.session_state.step = "generate"
            st.rerun()

        # Step 2A: Il soumets un Résumé global
    if st.session_state.step == "summary_input":
        default_summary = ("Je suis motivée, ponctuelle et organisée. J’ai obtenu un CAP Cuisine "
                           "et j’ai travaillé deux ans comme serveuse dans un restaurant local. "
                           "Je suis à l’aise avec le contact client et je sais gérer la caisse. "
                           "J’aimerais trouver un emploi stable dans la restauration ou l’accueil.")
        summary = st.text_area("Écrivez votre résumé ici (en français)", height=250, value=default_summary if DEBUG_MODE else "")
        if st.button(T["analyse_me"][lang]):
            st.session_state.user_data = {"summary": summary.strip()}
            st.session_state.step = "recommend"

    # Step 2B: Il utilise les Champs classiques
    if st.session_state.step == "form_input":
        with st.form("profile_form"):
            phone = st.text_input(T["phone"][lang])
            email = st.text_input(T["email"][lang])
            first_name = st.text_input(T["first_name"][lang])
            last_name = st.text_input(T["last_name"][lang])
            age = st.number_input(T["age"][lang], min_value=0, max_value=120, value=32 if DEBUG_MODE else 0)
            location = st.text_input(T["city"][lang])
            description = st.text_area(T["desc"][lang])
            education = st.text_area(T["education"][lang])
            skills = st.text_area(T["skills"][lang])
            experience = st.text_area(T["experience"][lang])
            hobbies = st.text_area(T["hobbies"][lang])
            languages = st.text_area(T["languages"][lang])
            submitted = st.form_submit_button(T["analyze"][lang])


        if submitted:
            st.session_state.user_data = {
                "phone": phone.strip(),
                "email": email.strip(),
                "first_name": first_name.strip(),
                "last_name": last_name.strip(),
                "age": age,
                "location": location.strip(),
                "description": description.strip(),
                "education": education.strip(),
                "skills": skills.strip(),
                "experience": experience.strip(),
                "hobbies":hobbies.strip(),
                "languages":languages.strip(),
                "last_updated": datetime.now().isoformat()

            }
            # Save to persistent storage
            email = st.session_state.user_data.get("email")
            if email:
                save_user_to_sheet(st.session_state.user_data)
                sync_to_sheet(st.session_state.user_data)

            else:
                st.warning(T["error_warning"][lang])


            st.session_state.step = "recommend"

    # Step 3: Basé sur l'input de l'utilisateur, GPT génère 5 simples recommandations de contenu qui match avec le profil
    # Les recommendations acceptées sont ajoutées au profil, les autres sont oubliées
    if st.session_state.step == "recommend":
        user = st.session_state.user_data

        content = user.get("summary", "") or f"""
        Nom: {user.get('first_name', '')} {user.get('last_name', '')}
        Téléphone: {user.get('phone', '')}
        Email: {user.get('email', '')}
        Âge: {user.get('age', '')}
        Lieu: {user.get('location', '')}
        Description: {user.get('description', '')}
        Éducation: {user.get('education', '')}
        Compétences: {user.get('skills', '')}
        Expérience: {user.get('experience', '')}
        Hobbies: {user_data.get("hobbies", "")}
        Langues: {user_data.get("languages", "")}
        """ if lang == "fr" else f"""
        Name: {user.get("first_name", "")} {user.get("last_name", "")}
        Phone: {user.get("phone", "")}
        Email: {user.get("email", "")}
        Age: {user.get("age", "")}
        City: {user.get("location", "")}
        Description: {user.get("description", "")}
        Education: {user.get("education", "")}
        Skills: {user.get("skills", "")}
        Professional Experience: {user.get("experience", "")}
        Hobbies: {user_data.get("hobbies", "")},
        Languages: {user_data.get("languages", "")}
        """
        existing = set(st.session_state.accepted_suggestions)
        if not st.session_state.recommendations and not DEBUG_MODE:
            with st.spinner(T["profile_analysis"][lang]):
                prompt = f"""
            Tu es un assistant bienveillant qui aide à enrichir des profils pour un CV.
            Voici un profil utilisateur :

            {content}

            Propose 5 éléments précis que je pourrais ajouter à ce profil sous forme de questions simples.
            Chaque question doit être :
            - très claire,
            - sur un point unique et précis (ex : "Puis-je ajouter que vous parlez espagnol ?"),
            - directement ajoutable à un CV si la réponse est oui.

            N’utilise pas de formulations vagues comme “des langues étrangères” ou “des langages de programmation”.
            Choisis un seul exemple concret par question et évite les suggestions déjà acceptées : [{existing}].

            Exemples :
            - Puis-je ajouter que vous avez le permis B ?
            - Puis-je ajouter que vous parlez espagnol ?
            - Puis-je ajouter que vous savez utiliser Excel ?
            - Puis-je ajouter que vous avez déjà travaillé avec des enfants ?
            
            Réponds entièrement en français ou anglais selon cette clé: {lang}
            """
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.session_state.recommendations = [
                    s.strip("-• ").strip() for s in response.choices[0].message.content.strip().split("\n") if s.strip()
                ]
        elif DEBUG_MODE:
            st.session_state.recommendations = [
                "Puis-je ajouter que vous parlez anglais ?",
                "Puis-je ajouter que vous avez le permis B ?",
                "Puis-je ajouter que vous savez utiliser Word et Excel ?",
                "Puis-je ajouter que vous êtes à l’aise en équipe ?",
                "Puis-je ajouter que vous avez travaillé avec des enfants ?"
            ]

        for i, rec in enumerate(st.session_state.recommendations):
            if rec:
                with st.container():
                    rec = rec.lstrip("0123456789. ").strip()
                    st.markdown(f"**👉 {i+1}. {rec}**")
                    col1, col2, col3 = st.columns([1, 1, 2])

                    with col1:
                        if st.button(T["accept"][lang], key=f"accept_{i}"):
                            st.session_state.accepted_suggestions.append(rec)
                            st.session_state.recommendations[i] = None
                            st.session_state.user_data["accepted_suggestions"] = st.session_state.accepted_suggestions
                            sync_to_sheet(st.session_state.user_data)
                            st.rerun()

                    with col2:
                        if st.button(T["modify"][lang], key=f"mod_button_{i}"):
                            st.session_state[f"modifying{i}"] = True
                        if st.session_state.get(f"modifying_{i}", False):
                                    new_val = st.text_input(
                                        T["propose_modify"][lang],
                                        key=f"mod_text_{i}",
                                        value=rec  # original suggestion text
                                    )

                                    if st.button(T["save"][lang], key=f"save_mod_{i}"):
                                        st.session_state.accepted_suggestions.append(new_val.strip())
                                        st.session_state.recommendations[i] = None
                                        st.session_state.user_data["accepted_suggestions"] = st.session_state.accepted_suggestions
                                        sync_to_sheet(st.session_state.user_data)
                                        st.session_state[f"modifying_{i}"] = False
                                        st.rerun()

                    with col3:
                        if st.button(T["reject"][lang], key=f"reject_{i}"):
                            st.session_state.recommendations[i] = None
                            st.rerun()

                    if st.session_state.get(f"modifying_{i}", False):
                        st.text_input(T["propose_modify"][lang], key=f"mod_text_{i}", value=rec)
                        if st.button(T["save"][lang], key=f"save_mod_{i}"):
                            modified = st.session_state[f"mod_text_{i}"]
                            st.session_state.accepted_suggestions.append(modified)
                            st.session_state.recommendations[i] = None
                            st.session_state[f"modifying_{i}"] = False
                            st.session_state.user_data["accepted_suggestions"] = st.session_state.accepted_suggestions
                            sync_to_sheet(st.session_state.user_data)
                            st.rerun()

        if all(r is None for r in st.session_state.recommendations):
            st.session_state.user_data["accepted_suggestions"] = st.session_state.accepted_suggestions
            sync_to_sheet(st.session_state.user_data)
                
        if st.button(T["generate_cv"][lang]):
            st.session_state.step = "generate"
            st.rerun()

    # Step 4: DOCX generation
    if st.session_state.step == "generate":
        email = st.session_state.user_data.get("email")
        user = load_user_from_sheet(email)
        st.session_state.user_data = user
        st.session_state.accepted_suggestions = user.get("accepted_suggestions", [])

        
        st.subheader(T["final_result"][lang])

        sections = []
        if user.get("description"): sections.append(f"🧍 Description :\n{user['description']}")
        if user.get("education"): sections.append(f"🎓 Éducation :\n{user['education']}")
        if user.get("skills"): sections.append(f"🛠️ Compétences :\n{user['skills']}")
        if user.get("experience"): sections.append(f"💼 Expérience :\n{user['experience']}")
        if st.session_state.accepted_suggestions:
            sections.append("➕ Informations ajoutées :\n- " + "\n- ".join(st.session_state.accepted_suggestions))

        all_skills = user.get('skills', '')
        if st.session_state.accepted_suggestions:
            all_skills += "\n" + "\n".join(st.session_state.accepted_suggestions)

        profile_input = f"""
        Prénom: {user.get('first_name', '')}
        Nom: {user.get('last_name', '')}
        Âge: {user.get('age', '')}
        Ville: {user.get('location', '')}
        Description: {user.get('description', '')}
        Éducation: {user.get('education', '')}
        Compétences: {user.get('skills', '')}
        Expérience professionnelle: {user.get('experience', '')}
        Hobbies: {user_data.get("hobbies", "")}
        Languages: {user_data.get("languages", "")}
        Suggestions acceptées:
        {chr(10).join(user.get("accepted_suggestions", []))}
        """


        reformulate_prompt = f"""
Tu es un assistant RH bienveillant. À partir des informations suivantes, rédige un contenu clair, professionnel et valorisant, structuré comme un CV.

📌 Utilise uniquement les données fournies. N'invente jamais de noms d'écoles, de villes, ou d'entreprises.
📌 Si une section est vide, omets-la (ne la remplis pas avec des informations fictives).
📌 Si certaines suggestions acceptées sont pertinentes, intègre-les dans les bonnes sections.

Organise la sortie finale en 4 sections bien rédigées :
- Une **Description** (2-4 phrases max)
- Une section **Éducation**
- Une section **Compétences** (liste à puces)
- Une section **Expérience professionnelle** (2-3 lignes max par poste)

Voici les données du profil :

{profile_input}

Réponds entièrement en {lang}.
Commence directement par :
Description :
Éducation :
...
"""



        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu aides des personnes à rédiger des CV professionnels à partir de données brutes."},
                {"role": "user", "content": reformulate_prompt}
            ]
        )

        cv_content = response.choices[0].message.content.strip()
        edited_html = st.text_area(T["modify_cv"][lang], value=cv_content, height=600)
        html_cv = create_beautiful_cv(cv_content)  # This is GPT's output
        st.components.v1.html(html_cv, height=1000, scrolling=True)

        edited_html = st.text_area(T["modify_cv"][lang], value=html_cv, height=600)

        def convert_html_to_pdf(source_html, output_filename):
            with open(output_filename, "w+b") as result_file:
                pisa_status = pisa.CreatePDF(source_html, dest=result_file)
            return pisa_status.err

        if st.button(T["download_cv"][lang]):
            filename = "mon_cv.pdf"
            error = convert_html_to_pdf(edited_html, filename)
            if not error:
                with open(filename, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📄 Cliquez ici pour télécharger le CV (.pdf)</a>'
                    st.markdown(href, unsafe_allow_html=True)
            else:
                st.error("Erreur lors de la génération du PDF.")