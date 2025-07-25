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
<html lang="de">
<head>
<title>Scrum Team Assistant</title>
<style>
body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #f7fafd;
    color: #263238;
    margin: 0;
    padding: 0;
}
.container {
    max-width: 560px;
    margin: 35px auto;
    background: #fff;
    border-radius: 15px;
    box-shadow: 0 6px 28px #76a1ff15;
    padding: 36px 40px 28px 40px;
}
h2 {
    color: #3382f7;
    margin-bottom: 18px;
}
label {
    font-size: 1.11em;
    color: #333;
}
input[type=text], textarea {
    padding: 10px;
    border: 1.5px solid #bcd7ff;
    border-radius: 8px;
    width: 98%%;
    margin-top: 7px;
    margin-bottom: 12px;
    font-size: 1.05em;
    background: #f6fbff;
}
input[type=submit], button {
    background: linear-gradient(90deg, #2560c0 60%%, #3382f7 100%%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 25px;
    font-size: 1.1em;
    font-weight: bold;
    margin-top: 2px;
    cursor: pointer;
    box-shadow: 0 1px 5px #3382f730;
    transition: background .18s;
    opacity: 1;
}
input[type=submit]:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
input[type=submit]:hover:enabled, button:hover {
    background: linear-gradient(90deg, #1560bd 40%%, #44d7b6 100%%);
}
hr {
    margin: 28px 0 22px 0;
    border: none;
    border-top: 1.5px solid #f1f5fb;
}
.info {
    color: #666;
    font-size: 0.99em;
    margin-bottom: 7px;
}
.vdb-preview {
    background: #e6f2ff;
    border-left: 4px solid #3382f7;
    color: #224970;
    padding: 8px 13px;
    margin-bottom: 17px;
    border-radius: 7px;
    font-size: 1.05em;
}
.result-box {
    background: #f6fbff;
    border-left: 4px solid #8fd1ff;
    padding: 10px 17px;
    border-radius: 7px;
    margin-top: 6px;
    font-size: 1.08em;
}
.result-title {
    margin-bottom: 5px;
    color: #3382f7;
}
#team_btn {
    background: linear-gradient(90deg, #1a437c 40%%, #3382f7 100%%);
    color: white;
    font-weight: bold;
    opacity: 1;
}
#team_btn:active, #team_btn:hover {
    background: linear-gradient(90deg, #1560bd 40%%, #44d7b6 100%%);
}
</style>
</head>
<body>
<div class="container">
    <h2>🤖 Scrum GPT Team-Assistant</h2>
    <form method=post>
      <label>Deine Stimmung, Anmerkungen, Verbesserungsvorschläge, Beschwerden an das Team:</label>
      <textarea name="user_prompt" id="user_prompt" rows="3" oninput="updateVdbPreview(); checkSubmitBtn();"></textarea>
      <input type=submit value="Absenden" id="submit_btn" disabled>
    </form>
    <div class="info">
      <i>Was du oben eingibst, siehst du hier als Vorschau (wird später in der Vector DB gespeichert):</i>
    </div>
    <div class="vdb-preview">
      <b id="vdb_preview"></b>
    </div>
    {% if antwort %}
      <div class="result-title">GPT Antwort:</div>
      <div class="result-box">{{ antwort }}</div>
    {% endif %}
    <hr>
    <form method=post>
      <button name="team_check" value="1" id="team_btn" type="submit">🚦 Teamstimmung abfragen</button>
    </form>
    {% if team_antwort %}
      <div class="result-title">GPT Teamstimmung:</div>
      <div class="result-box">{{ team_antwort }}</div>
    {% endif %}
</div>
<script>
function updateVdbPreview() {
    document.getElementById("vdb_preview").innerText =
        document.getElementById("user_prompt").value;
}
function checkSubmitBtn() {
    let txt = document.getElementById("user_prompt").value.trim();
    document.getElementById("submit_btn").disabled = (txt === "");
}
window.onload = function() {
    updateVdbPreview();
    checkSubmitBtn();
}
</script>
</body>
</html>
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
