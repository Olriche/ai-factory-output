import os
import requests
import base64
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement (GitHub Actions les injecte automatiquement)
load_dotenv()

# Configuration de l'IA
llm = ChatOpenAI(model="gpt-4o-mini")

# --- FONCTION DE DEPLOIEMENT ---
def deploy_to_web(content, filename):
    # Remplacez bien par votre pseudo GitHub réel
    repo = "VOTRE_PSEUDO_GITHUB/ai-factory-output" 
    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    token = os.getenv("GITHUB_TOKEN")
    
    # Récupérer le SHA du fichier s'il existe déjà (nécessaire pour la mise à jour)
    get_res = requests.get(url, headers={"Authorization": f"token {token}"})
    sha = get_res.json().get('sha') if get_res.status_code == 200 else None

    encoded_content = base64.b64encode(content.encode()).decode()
    
    data = {
        "message": "Mise à jour automatique du Micro-SaaS",
        "content": encoded_content
    }
    if sha:
        data["sha"] = sha # Indique à GitHub qu'on écrase l'ancien fichier
    
    headers = {"Authorization": f"token {token}"}
    response = requests.put(url, json=data, headers=headers)
    return response.status_code

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
