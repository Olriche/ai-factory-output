import os
import requests
import base64
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import datetime


# Configuration de l'IA
llm = ChatOpenAI(model="gpt-4o-mini")

# --- FONCTION DE DEPLOIEMENT ROBUSTE ---
def deploy_to_web(content, filename):
    # FORCEZ LE NOM ICI POUR LE TEST
    repo = "VOTRE_PSEUDO_GITHUB/ai-factory-output" 
    token = os.getenv("GITHUB_TOKEN")
    
    # On s'assure que le contenu est bien du texte pur
    if hasattr(content, 'raw'):
        clean_content = content.raw
    else:
        clean_content = str(content)

    # Nettoyage des balises markdown si l'IA en a mis
    if "```html" in clean_content:
        clean_content = clean_content.split("```html")[1].split("```")[0]
    elif "```" in clean_content:
        clean_content = clean_content.split("```")[1].split("```")[0]

    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    
    # 1. Vérifier si le fichier existe pour récupérer son SHA
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    get_res = requests.get(url, headers=headers)
    
    sha = None
    if get_res.status_code == 200:
        sha = get_res.json().get('sha')

    # 2. Préparer l'envoi
    encoded_content = base64.b64encode(clean_content.encode('utf-8')).decode('utf-8')
    
    payload = {
        "message": "Update index.html via AI Factory",
        "content": encoded_content,
        "branch": "main" # On force la branche main
    }
    if sha:
        payload["sha"] = sha

    # 3. Envoyer
    put_res = requests.put(url, json=payload, headers=headers)
    
    print(f"DEBUG: Status Code GitHub = {put_res.status_code}")
    print(f"DEBUG: Response = {put_res.text}")
    
    return put_res.status_code

# --- AGENTS ---
analyste = Agent(
    role='Analyste de Marché',
    goal='Trouver une idée de Micro-SaaS simple et virale',
    backstory='Expert en détection de tendances Reddit et Product Hunt.',
    llm=llm,
    allow_delegation=False
)

codeur = Agent(
    role='Développeur Web',
    goal='Créer un site web interactif dans un seul fichier HTML',
    backstory='Expert en HTML5, Tailwind CSS et JavaScript moderne.',
    llm=llm,
    allow_delegation=False
)

# --- MISSIONS (Corrigées avec expected_output) ---
t1 = Task(
    description="Analyse les tendances actuelles et propose une idée d'outil web simple (ex: calculateur, convertisseur, générateur).",
    expected_output="Une description courte et un titre pour le projet.",
    agent=analyste
)

t2 = Task(
    description="Génère le code source complet d'un fichier index.html intégrant le design Tailwind CSS et la logique JavaScript pour l'idée proposée.",
    expected_output="Le code HTML complet et fonctionnel uniquement.",
    agent=codeur
)

# --- LANCEMENT ---
crew = Crew(agents=[analyste, codeur], tasks=[t1, t2])
resultat_brut = crew.kickoff() # Utilisation de kickoff() au lieu de start()

# Conversion du résultat en texte pur
code_final = str(resultat_brut)

# Nettoyage si l'IA ajoute des balises ```html
if "```html" in code_final:
    code_final = code_final.split("```html")[1].split("```")[0]

# --- DEPLOIEMENT ---
status = deploy_to_web(code_final, "index.html")

if status in [200, 201]:
    print("✅ Succès ! Votre business est en ligne.")
else:
    print(f"❌ Erreur lors du déploiement. Code : {status}")
