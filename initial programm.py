import os
from dotenv import load_dotenv
import openai

# Umgebungsvariablen laden
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === System Prompt ===
SYSTEM_PROMPT = (
    "Du bist ein Berater eines Scrum Teams und sollst wertvolle Beratungstipps "
    "für Product Owner, Scrum Master und Developer geben. Dabei ist die oberste "
    "Priorität keine Namen in deiner Antwort zu geben. "
    "Gebe nicht mehr als 20 Wörter aus."
)

def chat_with_gpt(system_prompt: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]
    response = openai.chat.completions.create(
        model="gpt-4.1-nano",   # oder das Modell deiner Wahl
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    user_input = input("Was möchtest du das Scrum-GPT fragen? ")
    antwort = chat_with_gpt(SYSTEM_PROMPT, user_input)
    print("GPT:", antwort)
