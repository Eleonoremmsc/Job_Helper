import streamlit as st
from openai import OpenAI
from utils.helpers import load_user_from_sheet

client = OpenAI(api_key=st.secrets["OPENAI_KEY"])

st.title("🗣️ Préparation aux Entretiens")
st.markdown("""
Bienvenue dans votre assistant d'entraînement aux entretiens.

👉 Vous pouvez répondre à 5 questions courantes et obtenir un feedback immédiat ✨.

💡 *Astuce : Si vous avez créé une candidature dans la section lettre de motivation, vous pouvez aussi vous entraîner sur des questions spécifiques à l'offre !*
""")

basic_questions = [
    "Pouvez-vous vous présenter en quelques mots ?",
    "Pourquoi postulez-vous à ce poste ?",
    "Quels sont vos points forts et vos axes d'amélioration ?",
    "Parlez-moi d'une difficulté que vous avez rencontrée et comment vous l'avez gérée.",
    "Où vous voyez-vous dans 5 ans ?"
]

st.subheader("🧪 Questions Générales")

for i, q in enumerate(basic_questions):
    answer = st.text_area(f"{i+1}. {q}", key=f"q{i}")
    if st.button(f"💬 Feedback sur ma réponse {i+1}", key=f"f{i}"):
        with st.spinner("Analyse de votre réponse..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es un recruteur bienveillant qui donne un retour constructif et clair à un candidat sur sa réponse à une question d'entretien."},
                    {"role": "user", "content": f"Question : {q}\nRéponse du candidat : {answer}\n\nDonne un feedback structuré avec :\n- Ce qui est bien\n- Ce qui peut être amélioré\n- Un conseil pour améliorer la réponse."}
                ]
            )
            st.markdown(response.choices[0].message.content)

st.divider()
st.subheader("🎯 Questions Spécifiques aux Candidatures")

# Charge les candidatures si disponibles dans session_state ou feuille
email = st.session_state.user_data.get("email") if "user_data" in st.session_state else None
if email:
    user_data = load_user_from_sheet(email)
    applications = user_data.get("applications", [])  # Liste de dicts avec {"title":..., "offer":...}

    if applications:
        for app in applications:
            job_title = app.get("title")
            offer_text = app.get("offer")
            with st.expander(f"📌 {job_title}"):
                if st.button(f"🎙️ Générer des questions pour {job_title}", key=f"q_{job_title}"):
                    with st.spinner("Génération de questions personnalisées..."):
                        prompt = f"Voici une offre d'emploi :\n\n{offer_text}\n\nGénère 5 questions qu'un recruteur pourrait poser lors d'un entretien pour ce poste. Sois direct et précis."
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "user", "content": prompt}
                            ]
                        )
                        st.markdown(response.choices[0].message.content)
    else:
        st.info("Aucune candidature trouvée. Créez une lettre de motivation pour accéder à cette fonctionnalité.")
else:
    st.warning("Veuillez d'abord créer un profil pour accéder à cette fonctionnalité.")
