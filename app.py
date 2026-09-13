import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

# Historique global (simple pour l'instant, une seule conversation)
if os.path.exists("conversation.json"):
    with open("conversation.json", "r") as f:
        historique = json.load(f)
else:
    historique = [
        {"role": "system", "content": "Tu t'appelles Duprie. Tu es enthousiaste et tu utilises parfois des emojis. Si on te demande si tu es ChatGPT ou un autre assistant, réponds que non, tu es Duprie. Réponds toujours en texte simple, sans Markdown (pas de #, pas de **, pas de tableaux, pas de listes à puces avec des tirets). Reste concis : 2-4 phrases maximum sauf si on te demande explicitement plus de détails."}
         ]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    historique.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=historique
        )
        bot_reply = response.choices[0].message.content
        historique.append({"role": "assistant", "content": bot_reply})

        with open("conversation.json", "w") as f:
            json.dump(historique, f, indent=2, ensure_ascii=False)

        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"reply": f"Erreur : {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
