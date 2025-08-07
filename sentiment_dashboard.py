import matplotlib.pyplot as plt
import io
import base64
import openai
import os
import re
import hashlib

from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# In-Memory Cache: gleicher Text => gleicher Wert (pro Prozess)
SENTIMENT_CACHE = {}

def _cache_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _parse_score(s: str) -> float:
    # erste Zahl in -2..+2 extrahieren
    m = re.search(r"-?\d+(?:\.\d+)?", s or "")
    if not m:
        return 0.0
    try:
        val = float(m.group(0))
    except:
        return 0.0
    return max(-2.0, min(2.0, val))

def gpt_sentiment(text):
    """
    Liefert Sentiment in [-2, +2] für einen Text.
    Cache + temperature=0.0 sorgen für Stabilität bei wiederholten Rendern.
    """
    key = _cache_key(text)
    if key in SENTIMENT_CACHE:
        return SENTIMENT_CACHE[key]

    prompt = (
        f'Bewerte die Teamstimmung im folgenden Satz auf einer Skala von -2 (sehr negativ) bis +2 (sehr positiv): "{text}". '
        'Antworte nur mit einer Zahl zwischen -2 und 2.'
    )
    resp = openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "Du bewertest streng und antwortest ausschließlich mit einer Zahl."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0  # deterministischer
    )
    score = _parse_score(resp.choices[0].message.content.strip())
    SENTIMENT_CACHE[key] = score
    return score

def get_team_sentiment_dashboard(entries):
    """
    Erstellt ein Barometer aus den Sentiments der übergebenen Einträge.
    Keine DB-Abfrage. Keine erneuten LLM-Calls für bereits bewertete Texte.
    """
    scores = [gpt_sentiment(e) for e in entries]
    avg = (sum(scores) / len(scores)) if scores else 0.0

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.barh(0, 1, left=-2, color='#e33535', height=0.5)   # rot
    ax.barh(0, 1, left=-1, color="#ff7e0e", height=0.5)   # orange
    ax.barh(0, 1, left=0,  color='#ffe700', height=0.5)   # gelb
    ax.barh(0, 2, left=1,  color='#36d45c', height=0.5)   # grün
    ax.plot([avg, avg], [-0.25, 0.25], lw=8, color='k')   # Nadel
    ax.set_xlim(-2, 3)
    ax.axis('off')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64, avg
