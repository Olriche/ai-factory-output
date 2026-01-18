import os
import requests
import base64
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Charger les clés du fichier .env
load_dotenv()

# Configuration de l'IA (Modèle pas cher pour tenir le 1$/jour)
llm = ChatOpenAI(model="gpt-4o-mini")

# --- FONCTION DE DEPLOIEMENT (Les bras) ---
def deploy_to_web(content, filename):
    repo = "VOTRE_PSEUDO_GITHUB/ai-factory-output"
    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    token = os.getenv("GITHUB_TOKEN")
    
    encoded_content = base64.b64encode(content.encode()).decode()
    
    headers = {"Authorization": f"token {token}"}
    # On vérifie si le fichier existe déjà pour le mettre à jour
    data = {
        "message": "Update Micro-SaaS",
        "content": encoded_content
    }
    
    response = requests.put(url, json=data, headers=headers)
    return response.status_code

# --- AGENTS (L'intelligence) ---
analyste = Agent(
    role='Analyste de Marché',
    goal='Trouver une niche Micro-SaaS rentable',
    backstory='Expert en tendances web.',
    llm=llm
)

codeur = Agent(
    role='Développeur Full-Stack',
    goal='Ecrire un fichier index.html complet avec Tailwind CSS',
    backstory='Expert en développement rapide.',
    llm=llm
)

# --- MISSIONS ---
t1 = Task(description="Trouve une idée de micro-outil web utile.", agent=analyste)
t2 = Task(description="Génère le code HTML/JS complet (un seul fichier) pour cet outil.", agent=codeur)

# --- LANCEMENT ---
crew = Crew(agents=[analyste, codeur], tasks=[t1, t2])
resultat_code = crew.start()

# --- DEPLOIEMENT ---
status = deploy_to_web(str(resultat_code), "index.html")

if status in [200, 201]:
    print("✅ Succès ! Votre business est en ligne.")
else:
    print(f"❌ Erreur lors du déploiement : {status}")
