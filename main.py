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

# --- UPDATED TASK 3 WITH PREMIUM APPLE DESIGN ---
t3 = Task(
    description=f'''Create a world-class index.html (Main Hub) in English.
    List these tools as interactive cards: {outils_str}.
    
    DESIGN SPECIFICATIONS:
    1. AESTHETIC: Apple-inspired, minimal, futuristic. Use "Inter" font and a neutral palette (White/Charcoal).
    2. GLASSMORPHISM: Cards must have a subtle blur backdrop, thin borders (border-white/20), and soft shadows.
    3. HERO SECTION: Bold headline "The Future of Micro-Tools" with a glassmorphic CTA button.
    4. ANIMATIONS: Use AOS (Animate On Scroll) or simple CSS keyframes for fade-in and slide-up effects.
    5. INTERACTION: Hover effects on cards should include a subtle scale-up and increased glow.
    6. SECTIONS: Include Hero, Tool Grid (with category filters), a "Why Us" section with minimalist icons, and a refined Newsletter footer.
    
    TECHNICAL: Use Tailwind CSS CDN and Lucide Icons. The code must be one single file.''',
    expected_output="The complete premium Apple-style index.html source code.",
    agent=designer
)
crew_dash = Crew(agents=[designer], tasks=[t3])
index_code = str(crew_dash.kickoff()).replace('```html', '').replace('```', '').strip()

push_to_github(index_code, "index.html", "Update Dashboard with Newsletter")

print(f"✅ Success! Portal live: https://{USER}.github.io/{REPO}/")
