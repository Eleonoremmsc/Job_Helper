from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_KEY"])


def create_beautiful_cv(content: str) -> str:
#    sections = content.strip().split("\n\n")
#    html_sections = []
#
#    for section in sections:
#        lines = section.strip().split("\n")
#        if not lines:
#            continue
#
#        title = lines[0].strip()
#        body = lines[1:] if len(lines) > 1 else []
#
#        # Map section title to a styled HTML heading
#        html = f'<h2 style="border-bottom: 2px solid #ccc; padding-bottom: 4px; margin-top: 32px;">{title}</h2>'
#
#        for line in body:
#            if "|" in line:
#                # Probably a job entry
#                html += f'<p style="margin: 0.3em 0;"><strong>{line}</strong></p>'
#            elif "-" in line and any(char.isdigit() for char in line):
#                # Possibly date or job line
#                html += f'<p style="margin: 0.3em 0;">{line}</p>'
#            else:
#                html += f'<p>{line}</p>'
#
#        html_sections.append(html)
#
#    return f"""
#    <html>
#    <head>
#        <style>
#            body {{
#                font-family: 'Georgia', serif;
#                margin: 40px;
#                color: #000;
#                font-size: 14px;
#                line-height: 1.5;
#            }}
#            h2 {{
#                color: #2e6c80;
#                font-size: 18px;
#                margin-bottom: 10px;
#            }}
#            p {{
#                margin: 0 0 10px;
#            }}
#        </style>
#    </head>
#    <body>
#        {''.join(html_sections)}
#    </body>
#    </html>
#    """
#
    prompt = """

    Tu es un assistant bienveillant qui aide à enrichir des profils pour un CV.
    Voici un profil utilisateur :
    -----------------------
    """+content+"""
    -----------------------
    Tu dois remplacer chaque partie entre guillemets et doubles accolades (comme "{{Prénom Nom}}") par la donnée correspondante du profil.

    Si l'information n'est pas présente, tu dois simplement ignorer le bloc concerné.

    Les commentaires HTML indiquent ce que tu dois faire dans chaque section.
    Tu dois retourner **uniquement** le code HTML final, sans intro ni explication.

    J'aimerai que tu me donnes un CV selon le code html suivant : 
    -----------------------

    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {
        font-family: "Georgia", serif;
        margin: 40px;
        color: #000;
        font-size: 14px;
        }

        h1 {
        font-size: 24px;
        margin-bottom: 0;
        }

        h2 {
        font-size: 16px;
        margin-bottom: 2px;
        font-weight: bold;
        }

        .section-title {
        font-size: 16px;
        margin-top: 30px;
        margin-bottom: 5px;
        border-bottom: 1px solid #000;
        font-weight: bold;
        text-transform: uppercase;
        }

        .entry {
        margin-top: 10px;
        margin-bottom: 15px;
        }

        .entry-title {
        font-weight: bold;
        }

        .entry-subtitle {
        font-style: italic;
        font-size: 13px;
        }

        .entry-location {
        float: right;
        font-size: 13px;
        }

        ul {
        margin-top: 5px;
        padding-left: 20px;
        }

        li {
        margin-bottom: 3px;
        }

        .clear {
        clear: both;
        }
    </style>
    </head>
    <body>

    <h1>"{{Prénom Nom}}"</h1>
    <p><em>"{{résumé du personnage}}"</em></p>

    <div class="section-title">Professional Experience</div>
    <!-- copier coller le code de la division suivante pour CHAQUE experience pro que tu trouve dans le content   -->
    <div class="entry">
        <div class="entry-title">"{{nom de l'entreprise de cette experience }}"</div>
        <div class="entry-location">"{{lieu de l'experience si precisé}}"</div>
        <div class="entry-subtitle">"{{poste occupé lors de l'experience}}" | "{{date de debut et de fin de l'experience}}"</div>
        <ul>
        <li>"{{description de l'exp}}"</li>
        <li>"{{description de l'exp}}" </li>
        <li>"{{description de l'exp}}"</li>
        <li>"{{description de l'exp}}"</li>
        </ul>
        <div class="clear"></div>
    </div>


    <div class="section-title">Education</div>
    <!-- copier coller le code de la division suivante pour CHAQUE formation ou diplome que tu trouve dans le content   -->
    <div class="entry">
        <div class="entry-title">"{{Nom de l'organimse de formation (ecole..)}}"</div>
        <div class="entry-location">{{Nom de la ville, Pays}}</div>
        <div class="entry-subtitle">{{Nom de la formation/diplome etc | date de debut et de fain si disponible}}</div>
        <ul>
        <li>"{{description de la formation}}" </li>
        <li>"{{description de la formation}}" </li>
        </ul>
    </div>

    <div class="section-title">Description</div>

    <div class="entry">
        <ul>
        <li>"{{Résumé global de l'utilisateur, a travers son experience tehcnique mais aussi humaine, d'ou il vinet se qu'il a traversé etc}}" </li>
        </ul>
    </div>

    <div class="section-title">Languages</div>
    <p>"{{ici ecrit moi a la suite les languages que l'utilisateur parle avec un niveau associé si possible}}" </p>

    <div class="section-title">Soft Skills</div>
    <p>"{{ici ecrit moi a la suite les skills que l'utilisateur à selon sa description}}"</p>

    <div class="section-title">Extracurricular Activities</div>
    <p>"{{ici ecrit moi a la suite les activité que l'utilisateur a au quotidien, hobbie etc}}"</p>

    </body>
    </html>


    -----------------------

    Merci de :
    - Remplacer chaque élément entre guillemets par les bonnes données extraites du profil.
    - Ne pas laisser de guillemets dans le résultat final.
    - Générer plusieurs blocs `<h3>...` ou `<li>...` si le profil mentionne plusieurs expériences, diplômes, ou compétences.
    - Ne jamais ajouter de texte hors de la structure HTML fournie.

    TU NE RENVOIE QUE LE CODE HTML
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu aides des personnes à rédiger des CV professionnels à partir de données brutes."},
            {"role": "user", "content": prompt}
        ]
    )
            
    return response.choices[0].message.content.strip()