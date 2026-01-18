import os, requests, base64, datetime
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

# --- FONCTION DE DEPLOIEMENT MULTI-DOSSIERS ---
def deploy_to_web(content, idea_name):
    # Création d'un nom de dossier basé sur la date et l'idée
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    clean_name = idea_name.lower().replace(" ", "-")[:15]
    folder_name = f"{date_str}-{clean_name}"
    filename = f"{folder_name}/index.html"
    
    repo = "olriche/ai-factory-output" 
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    headers = {"Authorization": f"token {token}"}
    
    # On vérifie si le fichier existe (peu probable avec la date)
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None

    payload = {"message": f"Nouveau SaaS: {idea_name}", "content": encoded_content, "branch": "main"}
    if sha: payload["sha"] = sha

    res = requests.put(url, json=payload, headers=headers)
    return res.status_code, folder_name

# --- AGENTS AVEC INSTRUCTIONS DE DESIGN PRO ---
analyste = Agent(
    role='Market Intelligence',
    goal='Trouver un outil web simple qui résout un problème précis.',
    backstory='Tu identifies des outils qui ont un fort potentiel de partage social.',
    llm=llm
)

codeur = Agent(
    role='UX/UI Developer',
    goal='Créer une application web Single-Page magnifique et responsive.',
    backstory='''Tu es un expert en design moderne. 
    Tu utilises systématiquement :
    1. Tailwind CSS pour un design épuré (mode sombre/clair).
    2. Des animations CSS fluides.
    3. Une mise en page "App-like" avec une typographie soignée (Inter ou Sans-serif).
    Ta réponse doit être uniquement le code HTML.''',
    llm=llm
)

# --- TASKS ---
t1 = Task(
    description="Trouve une idée d'outil micro-SaaS utile aujourd'hui.",
    expected_output="Un nom court et une description de l'outil.",
    agent=analyste
)

t2 = Task(
    description="Code cet outil dans un fichier HTML unique. Inclus Tailwind CSS via CDN. L'outil doit être pro, dynamique et prêt à l'emploi.",
    expected_output="Le code HTML complet.",
    agent=codeur
)

# --- EXECUTION ---
crew = Crew(agents=[analyste, codeur], tasks=[t1, t2])
resultat = crew.kickoff()

# Nettoyage et Envoi
code_final = str(resultat).replace('```html', '').replace('```', '').strip()
status, folder = deploy_to_web(code_final, "SaaS-" + datetime.datetime.now().strftime("%H%M"))

if status in [200, 201]:
    print(f"🚀 Business en ligne ! Accès ici : https://olriche.github.io/ai-factory-output/{folder}/")
else:
    print(f"❌ Erreur : {status}")
