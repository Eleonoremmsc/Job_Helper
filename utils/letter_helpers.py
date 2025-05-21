import requests
from bs4 import BeautifulSoup
import openai
import streamlit as st
from create_account import get_worksheet


def extract_job_info_from_link(link):
    """
    Scrapes the job posting title and company name from a given URL (basic implementation).
    """
    try:
        response = requests.get(link, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else ""
            # You can customize scraping logic here to extract <h1>, meta tags, etc.
            return title
        else:
            return ""
    except Exception as e:
        print(f"Error extracting info from link: {e}")
        return ""

def get_gpt_letter_and_score(user_data, job_link, additional_info, job_title, company):
    """
    Calls GPT to generate a motivation letter, match score, and suggestions.
    """
    client = openai.OpenAI(api_key=st.secrets["OPENAI_KEY"])

    prompt = f"""
Tu es un assistant RH bienveillant. Tu aides un candidat à rédiger une lettre de motivation pour un poste. 
Tu reçois :
- Les informations du candidat (profil, compétences, etc.)
- Un lien vers l'offre d'emploi
- Des infos complémentaires optionnelles (précisions, motivations)

Ta tâche :
1. Analyse le lien et les infos pour comprendre le poste (nom du poste, missions, employeur).
2. Vérifie si le profil du candidat correspond au poste. Si oui, explique pourquoi. Sinon, trouve des éléments pertinents pour créer une lettre convaincante quand même.
3. Fournis une **lettre de motivation personnalisée** adaptée à l'offre et au profil.
4. Fournis un **score de compatibilité (0-100%)**.
5. Si le score < 50%, suggère **2 autres postes/domaines** mieux adaptés.

Infos candidat :
{user_data}

Offre d'emploi :
{job_link}

Infos complémentaires :
{additional_info}

Nom du poste : {job_title}
Nom de l'entreprise : {company}

Donne ta réponse dans ce format :
=== LETTRE ===\n
[Ton texte ici]

=== SCORE ===\n
XX

=== SUGGESTIONS ===\n
- [Suggestion 1]\n
- [Suggestion 2] (laisse vide si non applicable)
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    letter = content.split("=== SCORE ===")[0].replace("=== LETTRE ===", "").strip()
    score = content.split("=== SCORE ===")[1].split("===")[0].strip()
    suggestions_section = content.split("=== SUGGESTIONS ===")[-1].strip()

    try:
        score_value = int(score)
    except:
        score_value = 0

    suggestions = []
    if score_value < 50:
        suggestions = [line.strip("- ") for line in suggestions_section.split("\n") if line.strip()]

    return {
        "letter": letter,
        "match_score": score,
        "suggestions": suggestions
    }
    
def save_application_for_user(email, application_data):
    """
    Save this application for the user using local storage or Google Sheets (adapt as needed).
    """
    sheet = get_worksheet("Applications")
    sheet.append_row([
        email,
        application_data.get("job_title", ""),
        application_data.get("company", ""),
        application_data.get("date", ""),
        application_data.get("match_score", ""),
        application_data.get("letter", "")
    ])
    
