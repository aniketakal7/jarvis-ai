from flask import Flask, request, jsonify, render_template
import requests, json, datetime, wikipedia, re, os

app = Flask(__name__, template_folder="templates", static_folder="static")

# ================= API KEYS =================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

# ================= MEMORY =================
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

# ================= APIs =================
def gemini(q):
    if not GEMINI_API_KEY:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        r = requests.post(url, json={"contents":[{"parts":[{"text":q}]}]})
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return None

def openrouter(q):
    if not OPENROUTER_API_KEY:
        return None
    try:
        headers={"Authorization":f"Bearer {OPENROUTER_API_KEY}"}
        data={"model":"openai/gpt-4o-mini","messages":[{"role":"user","content":q}]}
        r=requests.post("https://openrouter.ai/api/v1/chat/completions",headers=headers,json=data)
        return r.json()['choices'][0]['message']['content']
    except:
        return None

def groq(q):
    if not GROQ_API_KEY:
        return None
    try:
        headers={"Authorization":f"Bearer {GROQ_API_KEY}"}
        data={"model":"llama3-8b-8192","messages":[{"role":"user","content":q}]}
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers=headers,json=data)
        return r.json()['choices'][0]['message']['content']
    except:
        return None

def cohere(q):
    if not COHERE_API_KEY:
        return None
    try:
        headers={"Authorization":f"Bearer {COHERE_API_KEY}"}
        r=requests.post("https://api.cohere.ai/v1/generate",headers=headers,json={"prompt":q,"max_tokens":200})
        return r.json()['generations'][0]['text']
    except:
        return None

def together(q):
    if not TOGETHER_API_KEY:
        return None
    try:
        headers={"Authorization":f"Bearer {TOGETHER_API_KEY}"}
        r=requests.post("https://api.together.xyz/v1/completions",headers=headers,json={"model":"mistralai/Mistral-7B-Instruct","prompt":q})
        return r.json()['choices'][0]['text']
    except:
        return None

def huggingface(q):
    if not HF_API_KEY:
        return None
    try:
        headers={"Authorization":f"Bearer {HF_API_KEY}"}
        r=requests.post("https://api-inference.huggingface.co/models/google/flan-t5-base",headers=headers,json={"inputs":q})
        return r.json()[0]['generated_text']
    except:
        return None

# ================= BRAIN =================
def jarvis(q):

    q_lower = q.lower()

    # Math
    if re.match(r'^[0-9\s\+\-\*\/\(\)\.]+$', q):
        try:
            return str(eval(q))
        except:
            pass

    # Time & Date
    if "time" in q_lower:
        return datetime.datetime.now().strftime("%H:%M:%S")

    if "date" in q_lower:
        return str(datetime.date.today())

    # Context
    history.append({"user": q})
    context = " ".join([h["user"] for h in history[-5:]])
    prompt = f"Context: {context}\nUser: {q}"

    # AI priority
    priority = [gemini, openrouter, groq, cohere, together, huggingface]

    for func in priority:
        try:
            ans = func(prompt)
            if ans and len(ans) > 5:
                history.append({"bot": ans})
                return ans.strip()
        except:
            continue

    # Wikipedia fallback
    try:
        return wikipedia.summary(q, sentences=2)
    except:
        pass

    # Memory fallback
    if q in memory:
        return memory[q]

    return "I don't know 🤔 (Teach me)"

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    q = request.json.get("q")
    ans = jarvis(q)
    return jsonify({"answer": ans})

@app.route("/train", methods=["POST"])
def train():
    data = request.json
    memory[data['q']] = data['a']
    save_memory(memory)
    return jsonify({"status":"Learned"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
