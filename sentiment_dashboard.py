# sentiment_dashboard.py
import matplotlib.pyplot as plt
import io, base64, hashlib, re, os
import openai
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# In‑Process Cache
_SENTIMENT_CACHE = {}
def _ck(text:str) -> str: return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _parse_score(s: str) -> float:
    m = re.search(r"-?\d+(?:\.\d+)?", s or "")
    if not m: return 0.0
    try: v = float(m.group(0))
    except: return 0.0
    return max(-2.0, min(2.0, v))

def gpt_sentiment(text: str) -> float:
    key = _ck(text)
    if key in _SENTIMENT_CACHE: return _SENTIMENT_CACHE[key]
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
        temperature=0.0
    )
    score = _parse_score(resp.choices[0].message.content.strip())
    _SENTIMENT_CACHE[key] = score
    return score

def _label_for(avg: float) -> str:
    if avg >= 1.0: return "eher positiv"
    if avg >= 0.2: return "leicht positiv"
    if avg > -0.2: return "neutral"
    if avg > -1.0: return "leicht negativ"
    return "eher negativ"

def get_team_sentiment_dashboard(entries):
    """
    Baut ein horizontales Segment-Barometer:
    -2..-1 (rot), -1..0 (orange), 0..1 (gelb), 1..2 (grün), plus Nadel bei Ø.
    Rückgabe: (base64_png, avg) — Signatur bleibt identisch.
    """
    if not entries:
        # Leer-Bild mit neutraler Anzeige
        fig, ax = plt.subplots(figsize=(4.2, 2.0), dpi=150)
        ax.text(0.5, 0.5, "Keine Einträge", ha="center", va="center", fontsize=10)
        ax.axis("off")
        buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight", transparent=True); plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8"), 0.0

    scores = [gpt_sentiment(e) for e in entries]
    avg = sum(scores)/len(scores) if scores else 0.0

    # Zeichnen
    fig, ax = plt.subplots(figsize=(4.6, 2.0), dpi=180)

    # Segmente
    ax.barh(0, 1, left=-2, color="#ff6b6b", height=0.5)   # rot
    ax.barh(0, 1, left=-1, color="#ffa24c", height=0.5)   # orange
    ax.barh(0, 1, left= 0, color="#ffe766", height=0.5)   # gelb
    ax.barh(0, 1, left= 1, color="#52e07a", height=0.5)   # grün

    # Ticks / Labels
    for x in (-2,-1,0,1,2):
        ax.plot([x,x], [-0.35, 0.35], lw=1, color="#1d274d")
        ax.text(x, 0.48, f"{x}", ha="center", va="bottom", fontsize=7, color="#8aa0d1")

    # Nadel
    ax.plot([avg, avg], [-0.30, 0.30], lw=6, color="#0b0b0b")
    ax.plot([avg, avg], [-0.30, 0.30], lw=3, color="#e9f0ff")

    # Meta
    desc = _label_for(avg)
    ax.text(2.55, 0.02, f"Ø {avg:.2f}\n{desc}", ha="left", va="center", fontsize=8, color="#e9f0ff", bbox=dict(
        boxstyle="round,pad=0.25", fc="#0f1630", ec="#1b2446", lw=1, alpha=0.95
    ))

    ax.set_xlim(-2.2, 3.0)
    ax.set_ylim(-0.7, 0.7)
    ax.axis("off")
    plt.tight_layout(pad=0.4)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8"), float(avg)
