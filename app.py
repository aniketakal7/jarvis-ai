from flask import Flask, request, jsonify, render_template
import requests, json, datetime, wikipedia, re, os

app = Flask(__name__)

# ========= API KEYS =========
GEMINI_API_KEY = "YOUR_GEMINI_KEY"
OPENROUTER_API_KEY = "YOUR_OPENROUTER_KEY"
GROQ_API_KEY = "YOUR_GROQ_KEY"
COHERE_API_KEY = "YOUR_COHERE_KEY"
TOGETHER_API_KEY = "YOUR_TOGETHER_KEY"
HF_API_KEY = "YOUR_HF_KEY"

# ========= MEMORY =========
MEMORY_FILE = "memory.json"

def load_memory():
    try:
        return json.load(open(MEMORY_FILE))
    except:
        return {}

def save_memory(mem):
    json.dump(mem, open(MEMORY_FILE, "w"), indent=4)

memory = load_memory()
history = []

# ========= TOOLS =========
def web_search(q):
    try:
        url = f"https://api.duckduckgo.com/?q={q}&format=json"
        r = requests.get(url).json()
        return r.get("AbstractText")
    except:
        return None

# ========= APIs =========
def groq(q):
    try:
        headers={"Authorization":f"Bearer {GROQ_API_KEY}"}
        data={"model":"llama3-8b-8192","messages":[{"role":"user","content":q}]}
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers=headers,json=data)
        return r.json()['choices'][0]['message']['content']
    except:
        return None

def gemini(q):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        r = requests.post(url, json={"contents":[{"parts":[{"text":q}]}]})
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return None

def openrouter(q):
    try:
        headers={"Authorization":f"Bearer {OPENROUTER_API_KEY}"}
        data={"model":"openai/gpt-4o-mini","messages":[{"role":"user","content":q}]}
        r=requests.post("https://openrouter.ai/api/v1/chat/completions",headers=headers,json=data)
        return r.json()['choices'][0]['message']['content']
    except:
        return None

# ========= BRAIN =========
def jarvis(q):
    q_lower = q.lower()

    # BASIC
    if re.match(r'^[0-9\s\+\-\*\/\(\)\.]+$', q):
        try: return str(eval(q))
        except: pass

    if "time" in q_lower:
        return datetime.datetime.now().strftime("%H:%M:%S")

    if "date" in q_lower:
        return str(datetime.date.today())

    # CONTEXT
    history.append({"user": q})
    context = " ".join([h["user"] for h in history[-5:]])

    prompt = f"""
You are Jarvis AI.
Be smart, short and helpful.

Context: {context}
User: {q}
"""

    # PRIORITY
    priority = [groq, gemini, openrouter]

    for func in priority:
        try:
            ans = func(prompt)
            if ans and len(ans) > 5:
                return ans.strip()
        except:
            continue

    # WEB
    web = web_search(q)
    if web:
        return web

    try:
        return wikipedia.summary(q, sentences=2)
    except:
        pass

    return "I couldn't find a good answer 🤔"

# ========= ROUTES =========
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    q = request.json.get("q")
    ans = jarvis(q)
    return jsonify({"answer": ans})

# ========= RUN =========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
