import os, requests, base64, datetime
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

# --- CONFIGURATION ---
USER = "olriche"
REPO = "ai-factory-output"
TOKEN = os.getenv("GITHUB_TOKEN")

# --- FUNCTIONS ---
def get_all_tools():
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/"
    headers = {"Authorization": f"token {TOKEN}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return [f['name'] for f in res.json() if f['type'] == 'dir' and f['name'].startswith('20')]
    return []

def push_to_github(content, path, message):
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{path}"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    payload = {"message": message, "content": encoded, "branch": "main"}
    if sha: payload["sha"] = sha
    res = requests.put(url, json=payload, headers=headers)
    return res.status_code

# --- AGENTS (IN ENGLISH) ---
expert_saas = Agent(
    role='Global SaaS Strategist',
    goal='Identify trending micro-tools for a global English-speaking audience.',
    backstory='You are an expert in finding viral tools for Product Hunt and Hacker News.',
    llm=llm
)

designer = Agent(
    role='Senior UI/UX Developer',
    goal='Create stunning, professional web apps in English using Tailwind CSS.',
    backstory='You specialize in clean, Apple-style minimal designs. You only output code.',
    llm=llm
)

# --- WORKFLOW ---

# 1. TOOL GENERATION (ENGLISH ONLY)
print("🚀 Creating today's global tool...")
t1 = Task(
    description="Find a useful micro-tool idea and generate the complete HTML/JS code. ALL TEXT MUST BE IN ENGLISH.",
    expected_output="Full professional HTML/JS code in English.",
    agent=designer
)
crew_tool = Crew(agents=[designer], tasks=[t1])
outil_code = str(crew_tool.kickoff()).replace('```html', '').replace('```', '').strip()

# 2. CATEGORY CLASSIFICATION
print("🏷️ Classifying the tool...")
t2 = Task(
    description=f"Analyze the created tool and give it a one-word category in English (e.g., Marketing, Productivity, AI, Writing).",
    expected_output="The category name in English.",
    agent=expert_saas
)
crew_cat = Crew(agents=[expert_saas], tasks=[t2])
categorie = str(crew_cat.kickoff()).strip()

# Deployment
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
folder_name = f"{date_str}-{categorie.lower()}"
push_to_github(outil_code, f"{folder_name}/index.html", f"New Global Tool: {categorie}")

# 3. UPDATE HUB WITH NEWSLETTER
print("🎨 Updating the Global Hub with Newsletter...")
outils_existants = get_all_tools()
outils_str = ", ".join(outils_existants)

t3 = Task(
    description=f'''Create a modern index.html (Main Dashboard) in English.
    1. Grid: Display these folders as clickable cards: {outils_str}.
    2. Newsletter: Add a professional "Join the Newsletter" section to get notified of new daily tools.
    3. UI: Include category filters and a search bar. Use a dark/light mode toggle if possible.''',
    expected_output="The complete professional index.html code in English.",
    agent=designer
)
crew_dash = Crew(agents=[designer], tasks=[t3])
index_code = str(crew_dash.kickoff()).replace('```html', '').replace('```', '').strip()

push_to_github(index_code, "index.html", "Update Dashboard with Newsletter")

print(f"✅ Success! Portal live: https://{USER}.github.io/{REPO}/")
