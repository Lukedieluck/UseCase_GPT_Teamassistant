import os
from dotenv import load_dotenv
import openai

# Umgebungsvariablen laden
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_with_gpt(messages):
    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    user_message = {"role": "user", "content": "Hallo, wie geht's?"}
    reply = chat_with_gpt([user_message])
    print("GPT:", reply)

