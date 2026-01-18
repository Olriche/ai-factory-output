import os, requests, base64, datetime, re
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# --- 1. CONFIGURATION ---
llm = ChatOpenAI(model="gpt-4o") # On reste sur le meilleur modèle
USER = "olriche"          # <--- REMETTEZ VOTRE PSEUDO ICI
REPO = "ai-factory-output"
TOKEN = os.getenv("GITHUB_TOKEN")
SUP_URL = os.getenv("SUPABASE_URL")
SUP_KEY = os.getenv("SUPABASE_KEY")

# --- 2. FONCTION DE NETTOYAGE CHIRURGICALE ---
def extract_content(text, type_tag):
    """
    Cette fonction va chercher uniquement ce qu'il y a entre les balises ```
    pour éviter que le blabla de l'IA ne casse le fichier.
    """
    # On cherche les blocs ```html ... ``` ou ```sql ... ```
    pattern = rf"```{type_tag}(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Si pas de balise précise, on cherche juste ``` ... ```
    pattern_generic = r"```(.*?)```"
    match_gen = re.search(pattern_generic, text, re.DOTALL)
    if match_gen:
        return match_gen.group(1).strip()
        
    # Si l'IA n'a pas mis de balises, on rend le texte brut (risque, mais mieux que rien)
    return text.strip()

def push_to_github(content, path, message):
    if not content:
        print(f"⚠️ ATTENTION: Contenu vide pour {path}, annulation de l'envoi.")
        return 400
        
    url = f"[https://api.github.com/repos/](https://api.github.com/repos/){USER}/{REPO}/contents/{path}"
    headers = {"Authorization": f"token {TOKEN}"}
    
    # Vérif si fichier existe (pour update)
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    payload = {"message": message, "content": encoded, "branch": "main"}
    if sha: payload["sha"] = sha
    
    res = requests.put(url, json=payload, headers=headers)
    if res.status_code in [200, 201]:
        print(f"✅ Fichier créé : {path}")
    else:
        print(f"❌ Erreur GitHub ({res.status_code}) sur {path} : {res.text}")
    return res.status_code

# --- 3. AGENTS AVEC INSTRUCTIONS STRICTES ---

architect = Agent(
    role='Database Architect',
    goal='Generate precise SQL queries.',
    backstory='You communicate ONLY in SQL code. No explanation. No "Here is the code". Just SQL.',
    llm=llm
)

web_expert = Agent(
    role='Senior Frontend Developer',
    goal='Code beautiful Apple-style interfaces.',
    backstory='''You are a master of TailwindCSS and GSAP animations.
    CRITICAL INSTRUCTIONS:
    1. Always include these CDNs in the <head>:
       - Tailwind: <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
       - FontAwesome: <link rel="stylesheet" href="[https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css](https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css)">
       - GSAP (Animations): <script src="[https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js](https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js)"></script>
       - Supabase: <script src="[https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2](https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2)"></script>
    2. Start your response with ```html and end with ```.
    3. Do NOT speak. Just code.''',
    llm=llm
)

# --- 4. WORKFLOW ---

# Étape A : Génération de l'ID du projet
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
project_name = f"{date_str}-saas-pro"
print(f"🚀 Démarrage du projet : {project_name}")

# Étape B : SQL pour la base de données
print("🗄️ Génération de la base de données...")
t1 = Task(
    description=f"Generate a valid PostgreSQL/Supabase SQL script to create a table for a 'Task Manager' app. Include Row Level Security (RLS).",
    expected_output="Raw SQL code inside ```sql ``` tags.",
    agent=architect
)
crew_sql = Crew(agents=[architect], tasks=[t1])
raw_sql = str(crew_sql.kickoff())
clean_sql = extract_content(raw_sql, "sql")

# On force la création du fichier SQL
push_to_github(clean_sql, f"{project_name}/setup_database.sql", "Database Setup")


# Étape C : L'Application Web (Le fichier qui était 'moche')
print("🎨 Design de l'application...")
t2 = Task(
    description=f'''Create a single-file `index.html` for a Task Manager.
    1. Use TailwindCSS for styling (Apple ecosystem look: gray-50 bg, rounded-xl cards, backdrop-blur).
    2. Use GSAP for smooth entrance animations (fade-in).
    3. Initialize Supabase client with URL: "{SUP_URL}" and KEY: "{SUP_KEY}".
    4. Handle Login/Signup UI vs Dashboard UI (show Dashboard only if logged in).
    
    IMPORTANT: The output MUST be a valid HTML file starting with <!DOCTYPE html> wrapped in ```html tags.''',
    expected_output="Raw HTML code inside ```html ``` tags.",
    agent=web_expert
)
crew_app = Crew(agents=[web_expert], tasks=[t2])
raw_app = str(crew_app.kickoff())
clean_app = extract_content(raw_app, "html")

push_to_github(clean_app, f"{project_name}/index.html", "SaaS Application")


# Étape D : La Page d'Accueil (Hub)
print("🏠 Mise à jour de la page d'accueil...")
# On récupère la liste des dossiers pour les lier
tools_links = f"<li><a href='/{project_name}/index.html' class='block p-6 bg-white rounded-2xl shadow hover:scale-105 transition'>Latest App: {project_name}</a></li>"

t3 = Task(
    description=f'''Create the main landing page `index.html`.
    Design: Apple.com aesthetic. Big typography, "Inter" font, whitespace.
    Content: A grid showing the available tools.
    Here is the link to insert for the new tool: {tools_links}
    Include Tailwind CDN. make it responsive.''',
    expected_output="Raw HTML code inside ```html ``` tags.",
    agent=web_expert
)
crew_hub = Crew(agents=[web_expert], tasks=[t3])
raw_hub = str(crew_hub.kickoff())
clean_hub = extract_content(raw_hub, "html")

push_to_github(clean_hub, "index.html", "Update Main Hub")

print(f"✅ TERMINÉ ! Vérifiez le dossier '{project_name}' sur GitHub.")
