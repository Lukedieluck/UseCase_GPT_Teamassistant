import os
from dotenv import load_dotenv
import openai
from flask import Flask, render_template_string, request

# Umgebungsvariablen laden
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
        model="gpt-4.1-nano",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<title>Scrum Team Assistant</title>
<h2>Scrum GPT Team-Assistant</h2>
<form method=post>
  <label>Deine Stimmung oder Frage an das Team:</label><br>
  <input type=text name=user_prompt style="width:60%%" autofocus>
  <input type=submit value="Absenden">
</form>
{% if antwort %}
  <h4>GPT Antwort:</h4>
  <div style="border:1px solid #ddd; padding:10px;">{{ antwort }}</div>
{% endif %}
<hr>
<form method=post>
  <button name="team_check" value="1">Teamstimmung abfragen</button>
</form>
{% if team_antwort %}
  <h4>GPT Teamstimmung:</h4>
  <div style="border:1px solid #eec; padding:10px;">{{ team_antwort }}</div>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def index():
    antwort = None
    team_antwort = None

    if request.method == "POST":
        if request.form.get("user_prompt"):
            user_prompt = request.form["user_prompt"]
            antwort = chat_with_gpt(SYSTEM_PROMPT, user_prompt)
        elif request.form.get("team_check"):
            # Platzhalter für spätere VDB-Anbindung
            fake_summary = "Das Team ist aktuell motiviert, aber leicht gestresst."
            team_antwort = chat_with_gpt(SYSTEM_PROMPT, f"Wie ist die Stimmung im Team? Aktuell: {fake_summary}")

    return render_template_string(TEMPLATE, antwort=antwort, team_antwort=team_antwort)

if __name__ == "__main__":
    app.run(debug=True)
