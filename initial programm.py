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
    "Du bist ein erfahrener agiler Coach. Denke bei schwierigen Fragen Schritt für Schritt nach, bevor du deine Antwort gibst."
    "Nutze dabei explizite Zwischenüberlegungen, um deine Antwort zu begründen."
    "Wenn dir Stimmungsdaten gegeben werden, fasse diese präzise und ohne zusätzliche Schlussfolgerungen zusammen."
    "Wenn du Gründe analysierst, denke Schritt für Schritt nach, aber beziehe dich dabei nur allgemein auf die Einträge. "
    "Zitiere keine konkreten Formulierungen. "
    "Verwende abstrahierende Sprache wie „mehrere Teammitglieder berichten …“ oder „es wirkt, als ob …“ "
    "Bitte maximal nur 500 Wörter ausgeben."
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
        temperature=0.3
    )
    return response.choices[0].message.content

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "debug-key")

TEMPLATE = """
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scrum GPT‑Team‑Assistant</title>
<style>
:root{
  --bg: #0b1020;
  --panel: #0f1630;
  --panel-2:#0c132a;
  --text:#e7ecff;
  --muted:#aab4d4;
  --brand:#7aa2ff;
  --brand-2:#9cd6ff;
  --ok:#36d45c;
  --warn:#ffbf00;
  --bad:#ff5959;
  --border:#1b2446;
  --chip:#151c3b;
  --shadow: 0 12px 30px rgba(41,80,255,0.18);
}

*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0;
  background:
   radial-gradient(1200px 800px at -20% -10%, #15214d 0%, transparent 60%),
   radial-gradient(800px 600px at 120% 30%, #1b2b66 0%, transparent 50%),
   linear-gradient(180deg,#0a0f20 0%, #080c1a 100%);
  color:var(--text);
  font: 16px/1.5 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}

.container{
  max-width: 980px;
  margin: 36px auto;
  padding: 0 16px;
}

.header{
  display:flex; gap:16px; align-items:center; justify-content:space-between;
  margin-bottom:18px;
}
.brand{
  display:flex; gap:12px; align-items:center;
}
.logo{
  width:44px; height:44px; display:grid; place-items:center;
  background: conic-gradient(from 210deg, #7aa2ff, #9cd6ff, #7aa2ff);
  border-radius:14px; box-shadow: var(--shadow);
  color:#0a0f20; font-weight:800; letter-spacing:.5px;
}
.hmeta{
  display:flex; gap:10px; align-items:center; color:var(--muted);
  font-size:14px;
}
.switch{
  appearance:none; width:46px; height:26px; border-radius:30px;
  background:#1a2445; position:relative; outline:none; cursor:pointer; border:1px solid var(--border);
}
.switch:after{
  content:""; position:absolute; inset:3px; width:20px; height:20px; border-radius:20px;
  background:#b9c9ff; transition:transform .2s ease;
}
.switch:checked:after{ transform: translateX(20px); }

.grid{
  display:grid; grid-template-columns: 1.2fr .8fr; gap:16px;
}
@media (max-width: 900px){ .grid{ grid-template-columns: 1fr; } }

.card{
  background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
  border:1px solid var(--border); border-radius:16px; padding:16px; box-shadow: var(--shadow);
}

.card h3{ margin:0 0 10px 0; font-size:18px; letter-spacing:.2px }
.help{ color:var(--muted); font-size:13px; margin-top:6px }

label{ display:block; font-weight:600; margin:6px 0 8px 4px }
textarea{
  width:100%; min-height:120px; resize:vertical; border-radius:12px;
  border:1px solid var(--border); background:#0b132c; color:var(--text);
  padding:14px 12px; font-size:15px; outline:none;
  box-shadow: inset 0 0 0 1px #0f1b3f;
}
textarea:focus{ box-shadow: 0 0 0 2px #7aa2ff55, inset 0 0 0 1px #1f356f; }

.controls{ display:flex; gap:10px; align-items:center; justify-content:flex-end; margin-top:10px }
.btn{
  appearance:none; border:none; border-radius:12px; padding:10px 14px;
  background: linear-gradient(180deg,#7aa2ff,#6b93f2);
  color:#07112b; font-weight:700; cursor:pointer; box-shadow: var(--shadow);
}
.btn.secondary{
  background: #141d3b; color:var(--text); border:1px solid var(--border); font-weight:600;
}
.btn[disabled]{ opacity:.6; cursor:not-allowed }

.kpis{ display:flex; gap:10px; flex-wrap:wrap; margin-top:8px }
.kpi{
  background: #0b132c; border:1px solid var(--border); border-radius:12px; padding:8px 10px;
  font-size:13px; color:var(--muted);
}
.kpi b{ color:var(--text) }

.divider{ height:1px; background:linear-gradient(90deg, transparent, #31407a, transparent); margin:14px 0 }

.result{
  background: #0b132c; border:1px solid var(--border); border-radius:12px; padding:12px;
  font-size:15px;
}
.result .title{ color:#9cd6ff; font-weight:700; margin-bottom:6px }

.barometer{
  display:flex; align-items:center; gap:12px;
}
.barometer img{ width:280px; max-width:100% }

.badge{
  display:inline-flex; align-items:center; gap:8px; padding:6px 10px; border-radius:999px;
  background:#111941; border:1px solid var(--border); color:var(--muted); font-size:13px;
}
.dot{ width:8px; height:8px; border-radius:8px; display:inline-block; }
.dot.ok{ background:var(--ok) } .dot.warn{ background:var(--warn) } .dot.bad{ background:var(--bad) }

.chat{
  display:flex; flex-direction:column; gap:10px; margin-top:10px;
}
.msg{ display:flex; gap:10px }
.msg .bubble{
  padding:10px 12px; border-radius:12px; max-width:78%;
  border:1px solid var(--border); background:#0b132c;
}
.msg.you{ justify-content:flex-end }
.msg.you .bubble{ background:#0f1b3f }
.msg .who{ font-size:12px; color:var(--muted); margin-bottom:4px }
.small{ font-size:12px; color:var(--muted) }

.footer{ margin-top:20px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; color:var(--muted); font-size:12px }

.toast{
  position:fixed; right:16px; bottom:16px; background:#0b132c; color:var(--text);
  border:1px solid var(--border); border-radius:12px; padding:10px 12px; box-shadow: var(--shadow); display:none;
}
.loading{ opacity:.8; pointer-events:none }
.counter{ color:var(--muted); font-size:12px; margin-top:4px; text-align:right }
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="brand">
        <div class="logo">GPT</div>
        <div>
          <div style="font-weight:800; letter-spacing:.3px;">Scrum GPT‑Team‑Assistant</div>
          <div class="hmeta">Privacy‑aware • RAG‑gestützt • Coach‑Modus</div>
        </div>
      </div>
      <label title="Reduziert visuelle Effekte" class="badge">
        <span>Low‑Motion</span>
        <input id="motionSwitch" class="switch" type="checkbox" />
      </label>
    </div>

    <div class="grid">
      <!-- Left: Eingabe & Teamabfrage -->
      <div class="card">
        <h3>Dein Beitrag</h3>
        <form method="POST" id="formFeedback">
          <label for="user_prompt">Stimmung / Hinweis an das Team</label>
          <textarea id="user_prompt" name="user_prompt" placeholder="Kurz & sachlich. Keine personenbezogenen Daten, bitte."></textarea>
          <div class="counter"><span id="charCount">0</span> Zeichen</div>
          <div class="controls">
            <button class="btn secondary" type="button" id="clearDraft">Entwurf löschen</button>
            <input class="btn" type="submit" value="Senden" id="submit_btn" disabled>
          </div>
          <div class="help">Wird anonymisiert in der Vektor‑DB gespeichert (Chunking & Embeddings).</div>
        </form>

        <div class="divider"></div>

        <h3>Teamstimmung</h3>
        <form method="POST" id="formTeam">
          <input type="hidden" name="team_check" value="1">
          <div class="controls">
            <button class="btn" id="btnTeam" type="submit">Teamstimmung abfragen</button>
          </div>
        </form>

        {% if dash_img %}
          <div class="barometer" style="margin-top:12px">
            <div class="badge"><span class="dot {% if team_antwort %}ok{% else %}warn{% endif %}"></span> Barometer (letzte 5 Einträge)</div>
            <img src="data:image/png;base64,{{ dash_img }}" alt="Teamstimmungs‑Barometer">
          </div>
        {% endif %}

        {% if antwort %}
          <div style="margin-top:12px" class="result">
            <div class="title">Bestätigung</div>
            <div>{{ antwort }}</div>
          </div>
        {% endif %}

        {% if team_antwort %}
          <div style="margin-top:12px" class="result">
            <div class="title">GPT Einschätzung zur Teamstimmung</div>
            <div>{{ team_antwort }}</div>
          </div>

          <form method="POST" style="margin-top:10px">
            <input type="hidden" name="continue_chat" value="1">
            <label for="follow_up">Rückfrage an den Coach</label>
            <textarea id="follow_up" name="follow_up" placeholder="Kurze Nachfrage, z. B. 'Wie moderieren wir das im Daily?'"></textarea>
            <div class="controls">
              <input class="btn" type="submit" value="Absenden">
            </div>
          </form>
        {% endif %}
      </div>

      <!-- Right: Verlauf -->
      <div class="card">
        <h3>Verlauf</h3>
        {% if chat_history %}
          <div class="chat" id="chatHistory">
            {% for msg in chat_history %}
              <div class="msg you">
                <div class="bubble">
                  <div class="who">Du</div>
                  <div>{{ msg["user"] }}</div>
                </div>
              </div>
              <div class="msg">
                <div class="bubble">
                  <div class="who">GPT</div>
                  <div>{{ msg["gpt"] }}</div>
                </div>
              </div>
            {% endfor %}
          </div>
        {% else %}
          <div class="small">Noch keine Unterhaltung. Starte mit <b>Teamstimmung abfragen</b> oder sende einen Beitrag.</div>
        {% endif %}
      </div>
    </div>

    <div class="footer">
      <span class="badge"><span class="dot ok"></span> Stable API</span>
      <span class="badge"><span class="dot warn"></span> Datenschutz gewahrt</span>
      <span class="badge"><span class="dot bad"></span> Keine Original‑Zitate</span>
      <span class="small">Build {{  now().strftime("%Y-%m-%d") if false else "" }}</span>
    </div>
  </div>

  <div class="toast" id="toast">Gespeichert.</div>

<script>
(function(){
  const ta = document.getElementById('user_prompt');
  const btn = document.getElementById('submit_btn');
  const count = document.getElementById('charCount');
  const toast = document.getElementById('toast');
  const clearBtn = document.getElementById('clearDraft');
  const formFeedback = document.getElementById('formFeedback');
  const formTeam = document.getElementById('formTeam');
  const btnTeam = document.getElementById('btnTeam');

  // Draft aus localStorage
  const KEY='scrum-gpt-draft';
  if(ta && localStorage.getItem(KEY)){
    ta.value = localStorage.getItem(KEY);
  }

  function updateState(){
    if(!ta || !btn) return;
    const v = (ta.value || "").trim();
    btn.disabled = v.length === 0;
    count.textContent = v.length;
  }

  function showToast(msg){
    if(!toast) return;
    toast.textContent = msg || 'Gespeichert.';
    toast.style.display='block';
    setTimeout(()=> toast.style.display='none', 1800);
  }

  if(ta){
    ta.addEventListener('input', ()=>{
      localStorage.setItem(KEY, ta.value);
      updateState();
    });
    updateState();
  }

  if(clearBtn){
    clearBtn.addEventListener('click', ()=>{
      if(ta){ ta.value=''; localStorage.removeItem(KEY); updateState(); }
      showToast('Entwurf gelöscht');
    });
  }

  // Loading States
  function setLoading(el, on){
    if(!el) return;
    if(on){ el.classList.add('loading'); el.setAttribute('data-prev', el.textContent); el.textContent='Bitte warten…'; }
    else{ el.classList.remove('loading'); el.textContent = el.getAttribute('data-prev') || el.textContent; el.removeAttribute('data-prev'); }
  }
  if(formFeedback){
    formFeedback.addEventListener('submit', ()=> setLoading(btn, true));
  }
  if(formTeam){
    formTeam.addEventListener('submit', ()=> setLoading(btnTeam, true));
  }

  // Reduce motion (nur kosmetisch hier)
  const motion = document.getElementById('motionSwitch');
  if(motion){
    const K='scrum-gpt-motion-off';
    motion.checked = localStorage.getItem(K)==='1';
    motion.addEventListener('change', ()=>{
      localStorage.setItem(K, motion.checked?'1':'0');
      showToast(motion.checked ? 'Bewegung reduziert' : 'Bewegung normal');
    });
  }

  // Auto‑scroll zu letztem Chat
  const ch = document.getElementById('chatHistory');
  if(ch){ ch.scrollTop = ch.scrollHeight; }
})();
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
