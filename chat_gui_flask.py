import os
from dotenv import load_dotenv
import openai
from flask import Flask, render_template, request, session, redirect, url_for

# OpenAI API-Key laden
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Session für Chat-Verlauf

def ask_gpt(messages):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",   # Oder dein Modell
        messages=messages,
        temperature=1.0
    )
    return response.choices[0].message.content

@app.route("/", methods=["GET", "POST"])
def chat():
    if "history" not in session:
        session["history"] = [
            {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Respond concisely and clearly."}
        ]
    history = session["history"]

    if request.method == "POST":
        user_message = request.form["user_input"]
        if user_message.strip():
            history.append({"role": "user", "content": user_message})
            answer = ask_gpt(history)
            history.append({"role": "assistant", "content": answer})
            session["history"] = history
        return redirect(url_for("chat"))  # Verhindert Resubmit

    # Alle Chat-Nachrichten außer System Prompt
    chat_msgs = [msg for msg in history if msg["role"] != "system"]
    return render_template("chat.html", chat_msgs=chat_msgs)

if __name__ == "__main__":
    app.run(debug=True)
