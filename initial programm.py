import os
from dotenv import load_dotenv
import openai
from flask import Flask, render_template_string, request
from vdb_helper import save_entry, get_last_entries

# Umgebungsvariablen laden
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = (
    "Du bist ein Berater eines Scrum-Teams. Bitte maximal nur 40 Wörter ausgeben. "
    "Bevorzuge die Inhalte die dir zugetragen wurde und versuche dein trainiertes Wissen aus dem Internet nur dann einzufügen "
    ",wenn du kein anderes Wissen findest."
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
<title>Scrum GPT-Team-Assistant</title>
<style>
body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #f7fafd;
    color: #263238;
    margin: 0;
    padding: 0;
}
.container {
    max-width: 650px;
    margin: 35px auto;
    background: #fff;
    border-radius: 15px;
    box-shadow: 0 6px 28px #76a1ff15;
    padding: 36px 40px 28px 40px;
}
h2 {
    color: #000;
    margin-bottom: 18px;
}
label {
    font-size: 1.1em;
    color: #333;
    display: block;
    margin-bottom: 10px;
}
textarea {
    padding: 16px;
    border: 2px solid #a0c4ff;
    border-radius: 15px;
    width: 100%;
    height: 120px;
    font-size: 1.1em;
    background: #e3f2fd;
    font-style: italic;
    color: #555;
    resize: vertical;
    box-sizing: border-box;
}
textarea:focus {
    font-style: normal;
    color: #000;
}
input[type=submit], button {
    background: #e3f2fd;
    color: #000;
    border: 2px solid #000;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 1.1em;
    font-weight: bold;
    cursor: pointer;
    margin-left: 10px;
}
hr {
    margin: 30px 0;
    border: none;
    border-top: 2px solid #ccc;
}
.result-box {
    background: #f6fbff;
    border-left: 4px solid #8fd1ff;
    padding: 10px 17px;
    border-radius: 7px;
    margin-top: 10px;
    font-size: 1.08em;
}
.result-title {
    margin-bottom: 5px;
    color: #3382f7;
    font-weight: bold;
}
.info {
    margin-top: 15px;
    font-size: 0.95em;
    color: #666;
    font-style: italic;
}
</style>
</head>
<body>
<div class="container">
    <h2>🤖 <b>Scrum GPT-Team-Assistant</b></h2>
    <form method="POST">
        <label>Wie ist deine Stimmung heute oder was möchtest du heute an dein Team loswerden?:</label>
        <textarea name="user_prompt" id="user_prompt" placeholder="Was du hier eingibst, wird gespeichert und hilft deinem Team sich zu verbessern und auf deine Anmerkungen besser eingehen zu können." oninput="checkSubmitBtn();"></textarea>
        <input type="submit" value="Senden" id="submit_btn" disabled>
    </form>
    {% if antwort %}
        <div class="result-title">GPT Antwort:</div>
        <div class="result-box">{{ antwort }}</div>
    {% endif %}
    <hr>
    <p><i>Teamstimmung abfragen und mit GPT-Team-Assistant darüber austauschen:</i></p>
    <form method="POST">
        <button name="team_check" value="1">Teamstimmung abfragen</button>
    </form>
    {% if team_antwort %}
        <div class="result-title">GPT Teamstimmung:</div>
        <div class="result-box">{{ team_antwort }}</div>
    {% endif %}
</div>
<script>
function checkSubmitBtn() {
    let txt = document.getElementById("user_prompt").value.trim();
    document.getElementById("submit_btn").disabled = (txt === "");
}
window.onload = function() {
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
            # Speichere anonymisiert in der VDB
            save_entry("Team", user_prompt)
            antwort = "✅ Deine Anmerkungen wurden in der Team-Datenbank erfolgreich aufgenommen. Vielen Dank für deinen Beitrag!"
        elif request.form.get("team_check"):
            # Hole die letzten 5 Team-Feedbacks
            last_entries = get_last_entries(5)
            context = "\n".join(last_entries)
            team_antwort = chat_with_gpt(SYSTEM_PROMPT, f"Wie ist die Stimmung im Team? Stehe dem Team als Berater zur Seite. Kontext:\n{context}")

    return render_template_string(TEMPLATE, antwort=antwort, team_antwort=team_antwort)

from vdb_helper import print_all_entries
if __name__ == "__main__":
    print_all_entries()
    app.run(debug=True)
