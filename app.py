import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

def get_heure_actuelle():
    maintenant = datetime.now()
    return maintenant.strftime("%H:%M:%S le %d/%m/%Y")

def calculer(operation, a, b):
    if operation == "addition":
        return a + b
    elif operation == "soustraction":
        return a - b
    elif operation == "multiplication":
        return a * b
    elif operation == "division":
        if b == 0:
            raise ValueError("Le dénominateur ne peut pas être zéro.")
        return a / b
    else:
        raise ValueError("Opération non supportée.")


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_heure_actuelle",
            "description": "Retourne l'heure et la date actuelles",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

if os.path.exists("conversation.json"):
    with open("conversation.json", "r") as f:
        historique = json.load(f)
else:
    historique = [
        {"role": "system", "content": "Tu t'appelles Mr Duprie. Tu es enthousiaste et tu utilises parfois des emojis. Si on te demande si tu es ChatGPT ou un autre assistant, reponds que non, tu es Duprie. Reponds toujours en texte simple, sans Markdown. Reste concis : 2-4 phrases maximum sauf si on te demande explicitement plus de details."}
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
            model="openai/gpt-oss-120b",
            messages=historique,
            tools=tools,
            reasoning_format="hidden"
        )
        message = response.choices[0].message

        if message.tool_calls:
            historique.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in message.tool_calls
                ]
            })

            for tool_call in message.tool_calls:
                if tool_call.function.name == "get_heure_actuelle":
                    resultat = get_heure_actuelle()

                historique.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": resultat
                })

            response2 = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=historique,
                reasoning_format="hidden"
            )
            bot_reply = response2.choices[0].message.content
        else:
            bot_reply = message.content

        historique.append({"role": "assistant", "content": bot_reply})

        with open("conversation.json", "w") as f:
            json.dump(historique, f, indent=2, ensure_ascii=False)

        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"reply": f"Erreur : {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)


