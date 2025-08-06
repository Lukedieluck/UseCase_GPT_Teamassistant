import os
from dotenv import load_dotenv
import openai
from flask import Flask, render_template_string, request, session
from vdb_helper import save_entry, get_last_entries
from sentiment_dashboard import get_team_sentiment_dashboard  # Wichtig: import hier

# Umgebungsvariablen laden
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = (
    "Du bist ein Berater eines Scrum-Teams. Bitte maximal nur 40 Wörter ausgeben. "
    "Bevorzuge die Inhalte die dir zugetragen wurde und versuche dein trainiertes Wissen aus dem Internet nur dann einzufügen, "
    "wenn du kein anderes Wissen findest."
)

def chat_with_gpt(system_prompt: str, messages) -> str:
    if isinstance(messages, str):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": messages},
        ]
    else:
        messages = [{"role": "system", "content": system_prompt}] + messages
    response = openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "debug-key")

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
.chat-box {
    margin-top: 20px;
}
.chat-message {
    margin-bottom: 10px;
}
.chat-message span {
    font-weight: bold;
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
    {% if dash_img %}
        <div style="margin-bottom:20px;">
            <img src="data:image/png;base64,{{ dash_img }}" style="width:250px;">
            <br><small>Teamstimmungsbarometer (letzte 5 Einträge)</small>
        </div>
    {% endif %}
    {% if team_antwort %}
        <div class="result-title">GPT Teamstimmung:</div>
        <div class="result-box">{{ team_antwort }}</div>
        <form method="POST">
            <input type="hidden" name="continue_chat" value="1">
            <textarea name="follow_up" placeholder="Frage zu dieser Teamstimmung..." style="width:100%;height:60px;margin-top:10px;"></textarea>
            <input type="submit" value="Absenden">
        </form>
    {% endif %}
    {% if chat_history %}
        <div style="margin-top:15px;">
        {% for msg in chat_history %}
            <div><b>Du:</b> {{ msg["user"] }}</div>
            <div><b>GPT:</b> {{ msg["gpt"] }}</div>
        {% endfor %}
        </div>
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

    chat_history = session.get('chat_history', [])

    if request.method == "POST":
        if request.form.get("user_prompt"):
            user_prompt = request.form["user_prompt"]
            save_entry("Team", user_prompt)
            antwort = "✅ Deine Anmerkungen wurden in der Team-Datenbank erfolgreich aufgenommen. Vielen Dank für deinen Beitrag!"
            session.pop('chat_history', None)  # Verlauf zurücksetzen

        elif request.form.get("team_check"):
            last_entries = get_last_entries(5)
            context = "\n".join(last_entries)
            user_message = "Wie ist die Stimmung im Team?"
            gpt_answer = chat_with_gpt(
                SYSTEM_PROMPT,
                [
                    {"role": "user", "content": f"{user_message} Kontext:\n{context}"}
                ]
            )
            chat_history = [{"user": user_message, "gpt": gpt_answer}]
            session['chat_history'] = chat_history
            team_antwort = gpt_answer

        elif request.form.get("continue_chat"):
            follow_up = request.form.get("follow_up", "")
            messages = []
            for pair in chat_history:
                messages.append({"role": "user", "content": pair["user"]})
                messages.append({"role": "assistant", "content": pair["gpt"]})
            messages.append({"role": "user", "content": follow_up})
            gpt_reply = chat_with_gpt(SYSTEM_PROMPT, messages[1:])
            chat_history.append({"user": follow_up, "gpt": gpt_reply})
            session['chat_history'] = chat_history
            team_antwort = None

    # --- WICHTIG: Nur echte Team-Feedbacks fürs Barometer! ---
    last_entries = get_last_entries(5)
    dash_img, dash_avg = get_team_sentiment_dashboard(last_entries)
    # ---------------------------------------------------------

    if 'chat_history' in session and session['chat_history']:
        if not team_antwort:
            team_antwort = session['chat_history'][-1]['gpt']

    return render_template_string(
        TEMPLATE,
        antwort=antwort,
        team_antwort=team_antwort,
        chat_history=chat_history if chat_history else None,
        dash_img=dash_img
    )

if __name__ == "__main__":
    from vdb_helper import print_all_entries
    print_all_entries()
    app.run(debug=True)
