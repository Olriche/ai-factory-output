import os, requests, base64, datetime, json
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION (MODÈLE GPT-4o POUR L'INTELLIGENCE MAXIMALE) ---
llm = ChatOpenAI(model="gpt-4o")

# REMPLACEZ VOTRE_PSEUDO ICI
USER = "VOTRE_PSEUDO"
REPO = "ai-factory-output"

# SECRETS (Doivent être dans GitHub Settings)
TOKEN = os.getenv("GITHUB_TOKEN")
SUP_URL = os.getenv("SUPABASE_URL")
SUP_KEY = os.getenv("SUPABASE_KEY")

# --- FONCTIONS SYSTÈME ---
def get_existing_tools():
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/"
    headers = {"Authorization": f"token {TOKEN}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return [f['name'] for f in res.json() if f['type'] == 'dir' and f['name'][0].isdigit()]
    return []

def push_to_github(content, path, message):
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{path}"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    
    # Nettoyage ultime du code si l'IA laisse des balises markdown
    clean_content = str(content).replace('```html', '').replace('```sql', '').replace('```', '').strip()
    
    encoded = base64.b64encode(clean_content.encode('utf-8')).decode('utf-8')
    payload = {"message": message, "content": encoded, "branch": "main"}
    if sha: payload["sha"] = sha
    res = requests.put(url, json=payload, headers=headers)
    return res.status_code

# --- L'ÉQUIPE D'ÉLITE (AGENTS) ---

architect = Agent(
    role='SaaS Architect & Database Engineer',
    goal='Design secure, scalable database schemas and authentication flows.',
    backstory='You are an expert in Supabase, SQL, and Row Level Security (RLS). You structure apps where users own their data.',
    llm=llm
)

product_manager = Agent(
    role='Product Visionary',
    goal='Identify high-value SaaS ideas (B2B or B2C) that require user login.',
    backstory='You find gaps in the market for tools like "Personal CRM", "Habit Gamification", or "AI Prompts Manager".',
    llm=llm
)

apple_dev = Agent(
    role='Lead Frontend Engineer (Apple Style)',
    goal='Code the interface using Tailwind CSS, Supabase JS Client, and Auth logic.',
    backstory='''You build interfaces that look like iOS 18. 
    You manage the Logic: Login, Sign Up, Logout, and CRUD operations.
    You manage the Design: Glassmorphism, San Francisco fonts, Smooth animations.''',
    llm=llm
)

growth_hacker = Agent(
    role='CMO & SEO Strategist',
    goal='Write viral launch content and optimize SEO.',
    backstory='You write hooks that make people click immediately.',
    llm=llm
)

# --- LE WORKFLOW DE L'USINE ---

# 1. IDÉE & STRUCTURE DE DONNÉES
print("🧠 Conception du SaaS et de la Base de Données...")
t1 = Task(
    description=f'''Imagine a new useful SaaS tool that NEEDS a login (e.g., to save user preferences, lists, or projects).
    1. Define the concept (Title, one-line pitch).
    2. Write the SQL code to create the table in Supabase. Include RLS policies so users only see THEIR data.
    Format: The output must be the SQL code only.''',
    expected_output="SQL query to set up the database.",
    agent=architect
)
crew_arch = Crew(agents=[architect, product_manager], tasks=[t1])
sql_schema = str(crew_arch.kickoff())

# 2. DÉVELOPPEMENT DE L'APPLICATION (AVEC LOGIN)
print("💻 Développement de l'interface Apple-Style avec Login...")
t2 = Task(
    description=f'''Create the full `index.html` file for this SaaS.
    
    TECH STACK:
    - Tailwind CSS (via CDN)
    - Supabase JS Client (via CDN: [https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2](https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2))
    - FontAwesome or Lucide Icons
    
    REQUIREMENTS:
    1. **Config**: Initialize Supabase with PROJECT_URL: "{SUP_URL}" and ANON_KEY: "{SUP_KEY}".
    2. **Auth UI**: Create a beautiful sleek Login/Sign-up form. Hide the app content until logged in.
    3. **Logic**: When logged in, fetch and display user's data from the database. Allow adding/deleting items.
    4. **Design**: iOS 18 Aesthetic. Large blurry headers, rounded cards, subtle shadows, smooth transitions.
    5. **Language**: English (Global Market).
    
    Output: ONLY the raw HTML code.''',
    expected_output="Complete functional HTML/JS code.",
    agent=apple_dev
)
crew_dev = Crew(agents=[apple_dev], tasks=[t2])
app_code = str(crew_dev.kickoff())

# 3. MARKETING & SEO
print("🚀 Génération du Marketing Kit...")
t3 = Task(
    description="Write a 'Launch Kit' containing: 1. SEO Meta Title & Description. 2. A Viral Twitter Thread (3 tweets). 3. A LinkedIn Post focusing on the problem/solution.",
    expected_output="Text content for marketing.",
    agent=growth_hacker
)
crew_growth = Crew(agents=[growth_hacker], tasks=[t3])
marketing_content = str(crew_growth.kickoff())

# 4. DÉPLOIEMENT DU NOUVEL OUTIL
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
# On extrait le nom du projet depuis le code ou on génère un nom générique
tool_name = f"{date_str}-saas-app"
folder_path = f"{tool_name}"

print(f"📦 Déploiement dans le dossier : {folder_path}")
push_to_github(sql_schema, f"{folder_path}/setup_database.sql", "SQL Schema for Supabase")
push_to_github(app_code, f"{folder_path}/index.html", "New AI SaaS App")
push_to_github(marketing_content, f"{folder_path}/marketing_kit.txt", "Marketing Content")

# 5. MISE À JOUR DU HUB CENTRAL (DASHBOARD)
print("💎 Mise à jour du Hub Principal...")
tools_list = get_existing_tools()
tools_str = ", ".join(tools_list)

t4 = Task(
    description=f'''Update the main `index.html` of the repository.
    Create a "SaaS App Store" looking landing page.
    1. Hero Section: "AI Software Suite".
    2. Grid: Display these folders as Apps: {tools_str}.
    3. Add a "New" badge on the latest tool ({tool_name}).
    4. Design: Apple.com homepage style (Black/White/Gray, huge typography, parallax).
    ''',
    expected_output="HTML code for the main hub.",
    agent=apple_dev
)
crew_hub = Crew(agents=[apple_dev], tasks=[t4])
hub_code = str(crew_hub.kickoff())

push_to_github(hub_code, "index.html", "Update Main Hub")

print(f"✅ SUCCÈS TOTAL ! Votre nouvel empire est à jour : https://{USER}.github.io/{REPO}/")
print(f"⚠️ IMPORTANT : Allez dans le dossier '{folder_path}' sur GitHub, ouvrez 'setup_database.sql' et exécutez le code dans l'éditeur SQL de Supabase pour faire fonctionner le nouvel outil.")
