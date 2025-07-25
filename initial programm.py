import os
from dotenv import load_dotenv
import openai

# Umgebungsvariablen laden
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === System Prompt & User Prompt aus dem ehemaligen prompting.py ===
SYSTEM_PROMPT = (
    "Du bist ein Berater eines Scrum Teams und sollst wertvolle Beratungstipps "
    "für Product Owner, Scrum Master und Developer geben. Dabei ist die oberste "
    "Priorität keine Namen in deiner Antwort zu geben"
)
USER_PROMPT = "wie würdest du mit jemandem reden nach den vorgaben des system promptes?"

def chat_with_gpt_scrum(system_prompt: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]
    response = openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

def chat_with_gpt(messages):
    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    # Test: Nutze beide Funktionen
    print("=== Test: Scrum-System-Prompt ===")
    print("GPT (Scrum):", chat_with_gpt_scrum(SYSTEM_PROMPT, USER_PROMPT))

    print("\n=== Test: Einfacher Chat ===")
    user_message = {"role": "user", "content": "Mir gehts gut?"}
    print("GPT (Chat):", chat_with_gpt([user_message]))
