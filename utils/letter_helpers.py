import requests
import uuid
import datetime
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

def get_gpt_letter_and_score(user_data, job_link, additional_info, job_title, company, selected_date):
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

Dates d'envoi : 
{selected_date}

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
[Ton texte ici. Une fois que tu rédige réellement la lettre, commence par "### Lettre de Motivation" et puis n'ajoute rien d'autre à part la lettre. L'idée est que je puisse extraire tout le reste de l'output après cette ligne.]

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
    
    # Split at the marker
    split_marker = "### Lettre de Motivation"
    if split_marker in letter:
        _, letter_content = letter.split(split_marker, 1)
        letter_content = letter_content.strip()
    else:
        letter_content = letter  # fallback if marker not found

    return {
        "letter": letter_content,
        "match_score": score,
        "suggestions": suggestions
    }

SPREADSHEET_NAME = "Job_Assistant_Users"
SHEET_NAME = "Users"

# Save user applications to disk
def save_application_for_user(email, job_title, company, date, letter, score, offer_link="", extra_info=""):
    sheet = get_worksheet(SPREADSHEET_NAME, SHEET_NAME)
    sheet.append_row([
        str(uuid.uuid4()),
        email,
        job_title,
        company,
        date,
        letter,
        score,
        offer_link,
        extra_info,
        datetime.now().isoformat()
    ])
