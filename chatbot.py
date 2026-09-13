import os
from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("Chatbot d'Endie prêt ! Tape 'quit' pour arrêter.\n")

if os.path.exists("conversation.json"):
    with open("conversation.json", "r") as f:
        historique = json.load(f)
    print("Ancienne conversation rechargée !\n")
else:
    historique = [
        {"role": "system", "content": "Tu t'appelles Duprie. Tu es enthousiaste et tu utilises parfois des emojis. Si on te demande si tu es ChatGPT ou un autre assistant, réponds que non, tu es Duprie."}
    ]

while True:
    user_input = input("Toi : ")

    if user_input.lower() == "quit":
        print("À Plus !")
        with open("conversation.json", "w") as f:
            json.dump(historique, f, indent=2, ensure_ascii=False)
        break

    historique.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=historique
        )
        bot_reply = response.choices[0].message.content
        print(f"Bot : {bot_reply}\n")
        historique.append({"role": "assistant", "content": bot_reply})
    except Exception as e:
        print(f"Erreur : impossible de contacter l'IA ({e}). Réessaie.\n")