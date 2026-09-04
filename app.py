from __future__ import annotations

import base64
import calendar
import json
import re
import uuid
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image, ImageOps

# ============================================================
# S & J — NUESTRA HISTORIA
# Versión móvil, pensada primero para celular.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
MOMENTS_DIR = ASSETS_DIR / "moments"
BB_UPLOADS_DIR = ASSETS_DIR / "bb_uploads"
DATA_DIR = BASE_DIR / "data"
BB_MEMORY_DB = DATA_DIR / "bb_memories.json"
ANSWERS_DB = DATA_DIR / "respuestas_bb.json"

BB_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

INITIALS = "S & J"
BB = "bb"
RELATIONSHIP_START = date(2026, 3, 13)
SIX_MONTH_DATE = date(2026, 9, 13)
ACCESS_CODE = "13032026"

MOMENTS = [
    {
        "slug": "01_long_lake",
        "title": "Long Lake, Colorado",
        "short": "Long Lake",
        "category": "Aventura",
        "phrase": "Entre montañas y agua, cualquier camino se disfruta más contigo.",
        "coords": (40.078, -105.584),
    },
    {
        "slug": "02_silver_plume",
        "title": "Silver Plume, Colorado",
        "short": "Silver Plume",
        "category": "Aventura",
        "phrase": "Una parada pequeña que terminó convirtiéndose en un recuerdo enorme.",
        "coords": (39.6961, -105.7253),
    },
    {
        "slug": "03_nederland",
        "title": "Nederland, Colorado",
        "short": "Nederland",
        "category": "Aventura",
        "phrase": "Nuevos lugares, nuevas historias… siempre tú y yo.",
        "coords": (39.9614, -105.5108),
    },
    {
        "slug": "04_topgolf",
        "title": "TopGolf, Colorado",
        "short": "TopGolf",
        "category": "Salida",
        "phrase": "Competencia, risas y otro plan que terminó siendo de mis favoritos contigo.",
        "coords": None,
    },
    {
        "slug": "05_primera_salida",
        "title": "Nuestra primera salida como novios",
        "short": "Primera salida",
        "category": "Nosotros",
        "phrase": "La primera salida con un nombre nuevo para lo nuestro: novios. ♡",
        "coords": None,
    },
    {
        "slug": "06_estes_park",
        "title": "Estes Park, Colorado",
        "short": "Estes Park",
        "category": "Escapada",
        "phrase": "Noches que se quedan en el alma, bb.",
        "coords": (40.3772, -105.5217),
    },
    {
        "slug": "07_black_hawk",
        "title": "Black Hawk, Colorado",
        "short": "Black Hawk",
        "category": "Noche",
        "phrase": "Entre luces, apuestas y risas, mi mejor suerte siempre eres tú.",
        "coords": (39.8017, -105.4939),
    },
    {
        "slug": "08_comida_depa",
        "title": "Comida en tu depa",
        "short": "En casa",
        "category": "Momentos simples",
        "phrase": "También amo esto: comer contigo, platicar y hacer especial un momento sencillo.",
        "coords": None,
    },
    {
        "slug": "09_vegas",
        "title": "Las Vegas, Nevada",
        "short": "Las Vegas",
        "category": "Viaje",
        "phrase": "Una de nuestras aventuras más grandes hasta ahora. Y todavía faltan muchas, bb.",
        "coords": (36.1699, -115.1398),
    },
    {
        "slug": "10_golden",
        "title": "Golden, Colorado",
        "short": "Golden",
        "category": "Aventura",
        "phrase": "Cada aventura contigo me confirma que mi lugar favorito no es un lugar: es juntos.",
        "coords": (39.7555, -105.2211),
    },
]

QUESTIONS = [
    "¿Qué fue lo que más te gustó de mí antes de que fuéramos novios?",
    "¿Qué es lo que más te ha gustado que he hecho por ti desde que somos novios?",
    "Dime 3 cosas de mí que te gusten — pueden ser de mi forma de ser, físicas o de cómo te trato.",
    "¿Cuál de nuestras salidas o viajes repetirías mañana sin pensarlo y por qué?",
    "¿Qué es algo que te gustaría que viviéramos juntos en nuestros próximos 6 meses?",
]

REASONS = [
    "Porque contigo puedo ser yo, sin filtros y sin sentir que tengo que fingir nada.",
    "Porque tu sonrisa tiene una forma muy tuya de cambiarme el día.",
    "Porque incluso un plan sencillo termina sintiéndose especial si estoy contigo.",
    "Porque amo nuestra complicidad y esas cosas que solo tú y yo entendemos.",
    "Porque contigo siempre quiero sumar otra salida, otro viaje y otra aventura.",
    "Porque admiro todo eso que te hace ser tú, bb.",
    "Porque verte feliz también se ha convertido en una de mis cosas favoritas.",
    "Porque contigo he aprendido a disfrutar más el presente y los pequeños momentos.",
    "Porque nuestras risas, conversaciones y locuras ya forman parte de mis recuerdos favoritos.",
    "Porque entre todas las posibilidades, bb, me sigue encantando elegirte a ti.",
]

# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="S & J · Nuestra historia",
    page_icon="♡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CSS = r"""
<style>
:root{
  --paper:#fbf6ef;
  --paper2:#f3e8dc;
  --ink:#3a302c;
  --muted:#81736d;
  --rose:#ca8588;
  --rose-soft:#efd7d4;
  --rose-pale:#f7e9e6;
  --gold:#b8925b;
  --line:rgba(83,61,47,.11);
}

html, body, [data-testid="stAppViewContainer"]{
  background:
    radial-gradient(circle at 12% 7%, rgba(207,137,141,.08), transparent 25%),
    radial-gradient(circle at 91% 14%, rgba(184,146,91,.07), transparent 22%),
    linear-gradient(180deg,#fdf9f4 0%,#f7eee5 100%);
  color:var(--ink);
}
[data-testid="stHeader"]{background:transparent;height:0;}
[data-testid="stToolbar"]{display:none;}
[data-testid="stDecoration"]{display:none;}
[data-testid="stSidebar"]{display:none;}

.block-container{
  max-width:440px !important;
  padding:12px 14px 112px !important;
  margin:0 auto;
}

h1,h2,h3{
  font-family:"Iowan Old Style","Baskerville","Palatino Linotype",Georgia,serif !important;
}
p,div,label,button,input,textarea{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}

/* ---------- tipografía / encabezados ---------- */
.brand-row{display:flex;align-items:center;justify-content:space-between;padding:8px 4px 10px;}
.brand-script{
  font-family:"Snell Roundhand","Apple Chancery","Segoe Script","Brush Script MT",cursive;
  font-size:2.15rem;color:#463936;line-height:1;
}
.brand-heart{font-size:1.4rem;color:var(--rose);}
.eyebrow{font-size:.69rem;letter-spacing:.19em;text-transform:uppercase;color:#a07f6d;margin-bottom:5px;}
.page-title{font-family:"Iowan Old Style","Baskerville",Georgia,serif;font-size:2rem;line-height:1.05;color:#40332f;margin-bottom:5px;}
.page-sub{font-size:.89rem;line-height:1.55;color:var(--muted);margin-bottom:17px;}
.script-title{
  font-family:"Snell Roundhand","Apple Chancery","Segoe Script","Brush Script MT",cursive;
  font-size:2rem;line-height:1.05;color:#5d4542;margin-bottom:5px;
}

/* ---------- portada home ---------- */
.home-cover{position:relative;height:218px;border-radius:24px;overflow:hidden;background:#171310;box-shadow:0 13px 34px rgba(74,49,36,.12);margin-bottom:14px;}
.home-cover img{width:100%;height:100%;object-fit:cover;object-position:center 43%;filter:brightness(.60) saturate(.78);transform:scale(1.01);}
.home-cover:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.05),rgba(0,0,0,.08) 38%,rgba(0,0,0,.57) 100%);}
.home-cover-copy{position:absolute;z-index:2;left:20px;right:20px;bottom:16px;color:#fff8ef;}
.home-date{font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;opacity:.82;margin-bottom:3px;}
.home-cover-title{font-family:"Snell Roundhand","Apple Chancery","Segoe Script",cursive;font-size:2rem;line-height:1.05;}
.home-cover-sub{font-family:Georgia,serif;font-size:.85rem;opacity:.88;margin-top:4px;}

/* ---------- contador ---------- */
.counter-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 0 18px;}
.counter-card{background:rgba(255,252,247,.88);border:1px solid var(--line);border-radius:17px;padding:13px 6px 11px;text-align:center;box-shadow:0 7px 22px rgba(79,55,40,.05);}
.counter-num{font-family:"Iowan Old Style",Georgia,serif;color:#9e6565;font-size:1.8rem;line-height:1;}
.counter-label{color:#817069;font-size:.66rem;margin-top:5px;line-height:1.25;}
.counter-small{color:#b27d7a;font-size:.62rem;margin-top:4px;line-height:1.2;}

/* ---------- paper cards ---------- */
.paper-card{background:rgba(255,252,248,.90);border:1px solid var(--line);border-radius:20px;padding:17px;box-shadow:0 8px 24px rgba(76,54,41,.05);margin:10px 0;}
.soft-note{background:#f3dedb;border-radius:15px;padding:17px;color:#584541;margin:10px 0;}
.soft-note-title{font-family:"Snell Roundhand","Segoe Script",cursive;font-size:1.55rem;margin-bottom:5px;}
.small-muted{font-size:.78rem;color:var(--muted);line-height:1.5;}
.quote{font-family:Georgia,serif;font-style:italic;color:#765d57;font-size:.96rem;line-height:1.6;}

/* ---------- film roll ---------- */
.film-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding:7px 0 13px;}
.film-scroll::-webkit-scrollbar{display:none;}
.film-roll{display:flex;gap:0;background:#171513;border-radius:13px;padding:10px 8px;width:max-content;box-shadow:0 9px 23px rgba(0,0,0,.12);}
.film-frame{width:126px;margin:0 5px;flex:0 0 auto;}
.film-holes{height:6px;background:repeating-linear-gradient(90deg,#c79e5e 0 6px,transparent 6px 12px);opacity:.66;margin-bottom:6px;}
.film-frame img{width:126px;height:154px;object-fit:cover;display:block;border:4px solid #27231f;border-radius:2px;}
.film-caption{color:#ead9bd;text-align:center;font-family:Georgia,serif;font-size:.69rem;padding:6px 3px 1px;}

/* ---------- polaroids ---------- */
.polaroid{background:#fffdf8;border:1px solid rgba(0,0,0,.05);padding:8px 8px 19px;border-radius:5px;box-shadow:0 9px 24px rgba(66,47,35,.12);margin:8px 0 15px;}
.polaroid img{width:100%;height:235px;object-fit:cover;display:block;border-radius:2px;}
.polaroid-caption{text-align:center;padding:9px 4px 0;font-family:"Snell Roundhand","Segoe Script",cursive;font-size:1.05rem;color:#604a44;}

/* ---------- album / cards ---------- */
.memory-head{background:linear-gradient(145deg,#fffaf5,#f4e7dc);border:1px solid var(--line);border-radius:18px;padding:14px;margin-bottom:12px;}
.memory-category{display:inline-block;padding:4px 9px;border-radius:999px;background:#f0d8d5;color:#9b6666;font-size:.65rem;margin:4px 0 7px;}
.memory-title{font-family:"Iowan Old Style",Georgia,serif;font-size:1.2rem;color:#493a35;}
.memory-phrase{font-family:Georgia,serif;font-style:italic;font-size:.86rem;line-height:1.5;color:#71615b;margin-top:3px;}

/* ---------- reasons ---------- */
.reason-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:7px;margin:12px 0 17px;}
.reason-pill{aspect-ratio:1;border-radius:50%;background:#f2d9d6;border:1px solid rgba(174,110,112,.18);display:flex;align-items:center;justify-content:center;color:#a56d6d;font-family:Georgia,serif;font-size:.85rem;}
.reason-card{background:#fffaf5;border:1px solid rgba(185,146,91,.18);border-radius:18px;padding:16px;margin:9px 0;}
.reason-number{font-family:Georgia,serif;color:#b57676;font-size:1.22rem;margin-bottom:4px;}
.reason-text{font-size:.87rem;line-height:1.55;color:#584a45;}

/* ---------- questions ---------- */
.q-number{width:34px;height:34px;border-radius:50%;background:#ecd1cf;display:flex;align-items:center;justify-content:center;color:#9e6666;font-family:Georgia,serif;margin-bottom:7px;}
.q-title{font-family:Georgia,serif;font-size:1rem;line-height:1.45;color:#493d38;margin-bottom:7px;}

/* ---------- login ---------- */
.login-card{background:#171412;border-radius:27px;overflow:hidden;box-shadow:0 18px 45px rgba(59,39,29,.18);border:1px solid rgba(255,255,255,.08);margin:14px auto 0;}
.login-photo{height:235px;position:relative;overflow:hidden;}
.login-photo img{width:100%;height:100%;object-fit:cover;object-position:center 48%;filter:brightness(.38) saturate(.68);}
.login-photo:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.10),rgba(0,0,0,.18) 48%,rgba(19,16,14,.82) 100%);}
.login-brand{position:absolute;z-index:2;left:0;right:0;top:32px;text-align:center;color:#f5eadc;}
.login-initials{font-family:"Snell Roundhand","Apple Chancery","Segoe Script",cursive;font-size:4.2rem;line-height:.95;}
.login-story{font-family:Georgia,serif;font-size:.96rem;margin-top:6px;opacity:.92;}
.login-form{padding:9px 20px 23px;color:#f5eadc;}
.login-label{text-align:center;font-family:Georgia,serif;font-size:.92rem;margin-bottom:8px;color:#ebdfd1;}
.login-foot{text-align:center;font-family:"Snell Roundhand","Segoe Script",cursive;font-size:1.2rem;color:#e9d8c5;margin-top:15px;}

/* ---------- widgets ---------- */
.stButton > button{border-radius:13px !important;border:0 !important;background:#c98789 !important;color:white !important;font-weight:600 !important;min-height:43px;box-shadow:none !important;}
.stButton > button:hover{background:#bc777a !important;color:white !important;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{border-radius:13px !important;border-color:rgba(94,71,56,.15) !important;background:rgba(255,253,250,.92) !important;}
[data-testid="stFileUploader"]{background:rgba(255,252,248,.7);border-radius:16px;padding:4px;}
[data-testid="stExpander"]{background:rgba(255,252,248,.72);border:1px solid var(--line);border-radius:16px;margin-bottom:9px;overflow:hidden;}

/* ---------- fixed bottom navigation (native Streamlit buttons) ---------- */
.st-key-mobile_nav{
  position:fixed !important;
  left:50% !important;
  bottom:0 !important;
  transform:translateX(-50%) !important;
  z-index:9999 !important;
  width:min(100%,440px) !important;
  min-height:76px !important;
  padding:7px 7px 9px !important;
  background:rgba(251,247,241,.97) !important;
  border-top:1px solid rgba(84,62,50,.10) !important;
  box-shadow:0 -7px 25px rgba(69,47,34,.08) !important;
  backdrop-filter:blur(12px) !important;
}
.st-key-mobile_nav [data-testid="stHorizontalBlock"]{gap:2px !important;}
.st-key-mobile_nav [data-testid="column"]{min-width:0 !important;}
.st-key-mobile_nav .stButton{margin:0 !important;}
.st-key-mobile_nav .stButton > button{
  width:100% !important;
  height:58px !important;
  min-height:58px !important;
  padding:4px 1px !important;
  border-radius:12px !important;
  display:flex !important;
  flex-direction:column !important;
  align-items:center !important;
  justify-content:center !important;
  gap:1px !important;
  box-shadow:none !important;
  font-size:.58rem !important;
  font-weight:500 !important;
  line-height:1 !important;
}
.st-key-mobile_nav .stButton > button[kind="secondary"]{
  background:transparent !important;
  color:#8e827b !important;
  border:0 !important;
}
.st-key-mobile_nav .stButton > button[kind="primary"]{
  background:#f6e5e2 !important;
  color:#bf7378 !important;
  border:0 !important;
}
.st-key-mobile_nav .stButton > button svg{
  width:20px !important;
  height:20px !important;
  margin:0 !important;
}
.st-key-mobile_nav .stButton > button p{
  font-size:.58rem !important;
  line-height:1 !important;
  margin:0 !important;
  white-space:nowrap !important;
}

@media(max-width:480px){
  .block-container{padding-left:11px !important;padding-right:11px !important;}
  .home-cover{height:205px;border-radius:21px;}
  .counter-num{font-size:1.65rem;}
  .st-key-mobile_nav{min-height:72px !important;}
  .st-key-mobile_nav .stButton > button{height:55px !important;min-height:55px !important;}
  .st-key-mobile_nav .stButton > button svg{width:19px !important;height:19px !important;}
  .polaroid img{height:220px;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================

IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_TYPES = {".mp4", ".mov", ".m4v"}


def digits_only(value: str) -> str:
    return "".join(c for c in value if c.isdigit())


def read_json(path: Path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback


def write_json(path: Path, payload) -> bool:
    try:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def image_uri(path: Path, max_side: int = 1100) -> str | None:
    try:
        im = Image.open(path)
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((max_side, max_side))
        buf = BytesIO()
        im.save(buf, format="JPEG", quality=86)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return None


def media_for_moment(moment: dict):
    folder = MOMENTS_DIR / moment["slug"]
    if not folder.exists():
        return [], []
    photos = sorted([p for p in folder.iterdir() if p.suffix.lower() in IMAGE_TYPES and p.name != "cover.jpg"])
    videos = sorted([p for p in folder.iterdir() if p.suffix.lower() in VIDEO_TYPES])
    return photos, videos


def cover_for(moment: dict) -> Path | None:
    p = MOMENTS_DIR / moment["slug"] / "cover.jpg"
    return p if p.exists() else None


def safe_filename(name: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return stem or "foto.jpg"


def save_bb_uploads(album: str, title: str, message: str, files) -> tuple[bool, int]:
    db = read_json(BB_MEMORY_DB, [])
    saved = 0
    try:
        for uploaded in files:
            ext = Path(uploaded.name).suffix.lower()
            if ext not in IMAGE_TYPES:
                continue
            new_name = f"{uuid.uuid4().hex[:10]}_{safe_filename(uploaded.name)}"
            target = BB_UPLOADS_DIR / new_name
            target.write_bytes(uploaded.getvalue())
            db.append({
                "id": uuid.uuid4().hex,
                "album": album,
                "title": title.strip() or "Un recuerdo de bb",
                "message": message.strip(),
                "file": str(target.relative_to(BASE_DIR)).replace("\\", "/"),
                "created_at": datetime.now().isoformat(timespec="seconds"),
            })
            saved += 1
        return write_json(BB_MEMORY_DB, db), saved
    except Exception:
        return False, saved


def bb_uploads(album: str | None = None):
    records = read_json(BB_MEMORY_DB, [])
    if album is None:
        return records
    return [r for r in records if r.get("album") == album]


def polaroid(path: Path, caption: str):
    uri = image_uri(path)
    if uri:
        st.markdown(
            f'<div class="polaroid"><img src="{uri}"><div class="polaroid-caption">{caption}</div></div>',
            unsafe_allow_html=True,
        )


def polaroid_record(record: dict):
    p = BASE_DIR / record.get("file", "")
    if not p.exists():
        return
    caption = record.get("title") or "Un recuerdo de bb"
    if record.get("message"):
        caption += f" · {record['message']}"
    polaroid(p, caption)


def full_months_days(start: date, end: date) -> tuple[int, int]:
    if end < start:
        return 0, 0
    months = (end.year - start.year) * 12 + (end.month - start.month)
    y = start.year + (start.month - 1 + months) // 12
    m = (start.month - 1 + months) % 12 + 1
    d = min(start.day, calendar.monthrange(y, m)[1])
    anchor = date(y, m, d)
    if anchor > end:
        months -= 1
        y = start.year + (start.month - 1 + months) // 12
        m = (start.month - 1 + months) % 12 + 1
        d = min(start.day, calendar.monthrange(y, m)[1])
        anchor = date(y, m, d)
    return months, (end - anchor).days


def render_film_roll():
    frames = []
    for moment in MOMENTS:
        cover = cover_for(moment)
        if not cover:
            continue
        uri = image_uri(cover, 520)
        if uri:
            frames.append(
                f'''<div class="film-frame">
                    <div class="film-holes"></div>
                    <img src="{uri}" alt="{moment['short']}">
                    <div class="film-caption">{moment['short']}</div>
                </div>'''
            )
    st.markdown(
        '<div class="film-scroll"><div class="film-roll">' + "".join(frames) + "</div></div>",
        unsafe_allow_html=True,
    )


def go_to(section: str):
    """Cambia de sección sin recargar el navegador ni perder la sesión."""
    st.session_state.section = section


def render_bottom_nav(active: str):
    # Usamos botones nativos de Streamlit para mantener la misma sesión.
    # Los enlaces HTML anteriores recargaban la página y volvían a mostrar el login.
    items = [
        ("inicio", "Inicio", ":material/home:"),
        ("momentos", "Momentos", ":material/photo_library:"),
        ("mapa", "Mapa", ":material/location_on:"),
        ("preguntas", "Preguntas", ":material/help:"),
        ("razones", "Razones", ":material/favorite:"),
        ("carta", "Carta", ":material/mail:"),
    ]

    with st.container(key="mobile_nav"):
        cols = st.columns(6, gap="small")
        for col, (key, label, icon) in zip(cols, items):
            with col:
                st.button(
                    label,
                    icon=icon,
                    key=f"nav_{key}",
                    type="primary" if key == active else "secondary",
                    use_container_width=True,
                    on_click=go_to,
                    args=(key,),
                )

def save_answers(answers: list[str]) -> bool:
    payload = {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "answers": [{"question": q, "answer": a} for q, a in zip(QUESTIONS, answers)],
    }
    return write_json(ANSWERS_DB, payload)

# ============================================================
# SESSION / LOGIN
# ============================================================

if "unlocked" not in st.session_state:
    st.session_state.unlocked = False
if "reason_selected" not in st.session_state:
    st.session_state.reason_selected = None
if "section" not in st.session_state:
    st.session_state.section = "inicio"

if not st.session_state.unlocked:
    login_img = image_uri(ASSETS_DIR / "login_cover.jpg", 1300)

    st.markdown('<div class="brand-row"><div class="brand-script">S & J</div><div class="brand-heart">♡</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    if login_img:
        st.markdown(
            f'''<div class="login-photo">
                    <img src="{login_img}" alt="S y J">
                    <div class="login-brand">
                      <div class="login-initials">S & J</div>
                      <div class="login-story">Nuestra historia ♡</div>
                    </div>
                </div>''',
            unsafe_allow_html=True,
        )
    st.markdown('<div class="login-form"><div class="login-label">Ingresa nuestra fecha</div></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1.35])
    with c1:
        day = st.text_input("Día", placeholder="13", max_chars=2, label_visibility="collapsed", key="login_day")
    with c2:
        month = st.text_input("Mes", placeholder="03", max_chars=2, label_visibility="collapsed", key="login_month")
    with c3:
        year = st.text_input("Año", placeholder="2026", max_chars=4, label_visibility="collapsed", key="login_year")

    if st.button("ENTRAR", use_container_width=True, key="login_enter"):
        if digits_only(f"{day}{month}{year}") == ACCESS_CODE:
            st.session_state.unlocked = True
            st.session_state.section = "inicio"
            st.rerun()
        else:
            st.error("Mmm bb… esa no es nuestra fecha 👀♡")

    st.markdown('<div class="login-foot">Cada aventura nos trajo hasta aquí ♡</div></div>', unsafe_allow_html=True)
    st.stop()

# ============================================================
# ROUTING
# ============================================================

allowed_sections = {"inicio", "momentos", "mapa", "preguntas", "razones", "carta"}
section = st.session_state.get("section", "inicio")
if section not in allowed_sections:
    section = "inicio"
    st.session_state.section = "inicio"

# Header compacto tipo app
st.markdown(
    '<div class="brand-row"><div class="brand-script">S & J</div><div class="brand-heart">♡</div></div>',
    unsafe_allow_html=True,
)

# ============================================================
# INICIO
# ============================================================

if section == "inicio":
    home_img = image_uri(ASSETS_DIR / "home_cover.jpg", 1200)
    if home_img:
        st.markdown(
            f'''<div class="home-cover">
                  <img src="{home_img}" alt="Nosotros">
                  <div class="home-cover-copy">
                    <div class="home-date">13 · 03 · 2026</div>
                    <div class="home-cover-title">Nuestro lugar favorito: juntos ♡</div>
                    <div class="home-cover-sub">Cada momento contigo se vuelve parte de nuestra historia.</div>
                  </div>
                </div>''',
            unsafe_allow_html=True,
        )

    today = date.today()
    total_days = max((today - RELATIONSHIP_START).days, 0)
    months, extra_days = full_months_days(RELATIONSHIP_START, today)
    days_left = max((SIX_MONTH_DATE - today).days, 0)

    st.markdown('<div class="eyebrow">Nuestro tiempo</div><div class="page-title">Lo que llevamos siendo nosotros</div>', unsafe_allow_html=True)
    st.markdown(
        f'''<div class="counter-grid">
              <div class="counter-card"><div class="counter-num">{total_days}</div><div class="counter-label">días juntos</div></div>
              <div class="counter-card"><div class="counter-num">{months}</div><div class="counter-label">meses</div><div class="counter-small">+ {extra_days} días</div></div>
              <div class="counter-card"><div class="counter-num">{days_left}</div><div class="counter-label">días para 6 meses</div></div>
            </div>''',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'''<div class="soft-note">
              <div class="soft-note-title">Para nosotros, cada momento cuenta ♡</div>
              <div class="small-muted">No quise hacerte solo una tarjeta, {BB}. Quise hacer un lugar para volver a nuestras fotos, salidas y aventuras… y seguir agregando nuevas.</div>
            </div>''',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="script-title">Nuestro rollo fotográfico</div><div class="page-sub">Deslízalo hacia los lados. Cada cuadro pertenece a un momento de nosotros.</div>', unsafe_allow_html=True)
    render_film_roll()

    st.markdown('<div class="paper-card"><div class="quote">“No es la cantidad de tiempo, es todo lo que hemos vivido juntos.” ♡</div></div>', unsafe_allow_html=True)

# ============================================================
# MOMENTOS / ALBUM
# ============================================================

elif section == "momentos":
    st.markdown('<div class="eyebrow">Nuestro álbum</div><div class="page-title">Momentos que quiero guardar ♡</div><div class="page-sub">Cada salida tiene su propia pequeña historia. Abre una para ver las fotos y videos.</div>', unsafe_allow_html=True)

    names = [m["title"] for m in MOMENTS]
    selected = st.selectbox("Ir a un recuerdo", ["Ver todos"] + names, label_visibility="collapsed")
    filtered = MOMENTS if selected == "Ver todos" else [m for m in MOMENTS if m["title"] == selected]

    for i, moment in enumerate(filtered):
        photos, videos = media_for_moment(moment)
        user_records = bb_uploads(moment["slug"])
        expanded = selected != "Ver todos" or i == 0
        with st.expander(f"{moment['short']}  ♡", expanded=expanded):
            st.markdown(
                f'''<div class="memory-head">
                      <div class="memory-title">{moment['title']}</div>
                      <div class="memory-category">{moment['category']}</div>
                      <div class="memory-phrase">“{moment['phrase']}”</div>
                    </div>''',
                unsafe_allow_html=True,
            )

            cover = cover_for(moment)
            if cover:
                polaroid(cover, moment["short"])
            for p in photos:
                polaroid(p, "Otro pedacito de este día ♡")
            for v in videos:
                st.video(str(v))
            for rec in user_records:
                polaroid_record(rec)

    st.markdown('<div class="script-title">Agrega tus favoritas, bb ♡</div><div class="page-sub">Si tienes una foto que yo no puse, también puede vivir aquí.</div>', unsafe_allow_html=True)
    with st.form("upload_form", clear_on_submit=True):
        album_label = st.selectbox("¿A qué recuerdo pertenece?", ["Álbum general"] + names)
        title = st.text_input("Nombre del recuerdo", placeholder="Ej. Esta me encanta")
        message = st.text_area("¿Quieres escribir algo?", placeholder="Ej. Me encanta este día porque…", height=80)
        uploads = st.file_uploader("Sube una o varias fotos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
        sent = st.form_submit_button("Guardar en nuestro álbum ♡", use_container_width=True)

    if sent:
        if not uploads:
            st.warning("Elige por lo menos una foto, bb ♡")
        else:
            slug_map = {m["title"]: m["slug"] for m in MOMENTS}
            album = "general" if album_label == "Álbum general" else slug_map[album_label]
            ok, saved = save_bb_uploads(album, title, message, uploads)
            if ok and saved:
                st.success(f"Listo ♡ Guardé {saved} foto(s).")
                st.rerun()
            else:
                st.error("No pude guardarlas en esta versión local. En la versión final lo conectaremos a Supabase.")

    general_records = bb_uploads("general")
    if general_records:
        st.markdown('<div class="script-title">Las favoritas que bb agregó</div>', unsafe_allow_html=True)
        for rec in general_records:
            polaroid_record(rec)

# ============================================================
# MAPA
# ============================================================

elif section == "mapa":
    st.markdown('<div class="eyebrow">Nuestros lugares</div><div class="page-title">El mapa de nosotros ♡</div><div class="page-sub">Cada punto guarda una historia. Los lugares privados no aparecen en el mapa.</div>', unsafe_allow_html=True)

    rows = []
    for m in MOMENTS:
        if m.get("coords"):
            rows.append({"latitude": m["coords"][0], "longitude": m["coords"][1], "lugar": m["short"]})
    if rows:
        st.map(pd.DataFrame(rows), latitude="latitude", longitude="longitude", zoom=5, use_container_width=True)

    for m in MOMENTS:
        cover = cover_for(m)
        st.markdown(f'<div class="memory-head"><div class="memory-title">{m["short"]}</div><div class="memory-category">{m["category"]}</div><div class="memory-phrase">{m["phrase"]}</div></div>', unsafe_allow_html=True)
        if cover:
            uri = image_uri(cover, 600)
            if uri:
                st.markdown(f'<div style="margin:-4px 0 13px"><img src="{uri}" style="width:100%;height:145px;object-fit:cover;border-radius:15px;filter:saturate(.82)"></div>', unsafe_allow_html=True)

# ============================================================
# 5 PREGUNTAS
# ============================================================

elif section == "preguntas":
    st.markdown('<div class="eyebrow">Para ti, bb</div><div class="page-title">5 preguntas de nosotros ♡</div><div class="page-sub">No es un examen. Solo quiero conocer nuestra historia desde tus ojos.</div>', unsafe_allow_html=True)

    answers = []
    for i, q in enumerate(QUESTIONS, 1):
        st.markdown(f'<div class="paper-card"><div class="q-number">{i}</div><div class="q-title">{q}</div></div>', unsafe_allow_html=True)
        a = st.text_area(f"Respuesta {i}", key=f"answer_{i}", placeholder="Escribe aquí…", label_visibility="collapsed", height=95)
        answers.append(a)

    if st.button("Guardar mis respuestas ♡", use_container_width=True):
        if any(not a.strip() for a in answers):
            st.warning("Todavía falta por responder alguna, bb ♡")
        elif save_answers(answers):
            st.success("Guardadas ♡ Me va a encantar leerlas.")
        else:
            st.error("No pude guardar las respuestas en esta versión local.")

# ============================================================
# 10 RAZONES
# ============================================================

elif section == "razones":
    st.markdown('<div class="eyebrow">Una por una</div><div class="page-title">10 razones por las que amo estar contigo ♡</div><div class="page-sub">Toca un número y descubre una razón.</div>', unsafe_allow_html=True)

    cols = st.columns(5)
    for i in range(10):
        with cols[i % 5]:
            if st.button(f"♡ {i+1}", key=f"reason_{i}", use_container_width=True):
                st.session_state.reason_selected = i

    if st.session_state.reason_selected is None:
        st.markdown('<div class="soft-note"><div class="soft-note-title">Elige un corazón ♡</div><div class="small-muted">Hay diez pequeñas razones esperando aquí.</div></div>', unsafe_allow_html=True)
    else:
        idx = st.session_state.reason_selected
        st.markdown(
            f'<div class="reason-card"><div class="reason-number">Razón #{idx+1}</div><div class="reason-text">{REASONS[idx]}</div></div>',
            unsafe_allow_html=True,
        )
        moment = MOMENTS[idx % len(MOMENTS)]
        cover = cover_for(moment)
        if cover:
            polaroid(cover, "Un recuerdo para acompañar esta razón ♡")

# ============================================================
# CARTA
# ============================================================

elif section == "carta":
    st.markdown('<div class="eyebrow">Solo para ti</div><div class="page-title">Para mi bb ♡</div><div class="page-sub">Una carta pequeña para cerrar este primer capítulo.</div>', unsafe_allow_html=True)

    st.markdown(
        f'''<div class="soft-note">
              <div class="soft-note-title">Para ti, amor ♡</div>
              <div class="quote" style="font-style:normal">
                Quise hacerte esto porque nuestros meses juntos son mucho más que un número. Son salidas, viajes, conversaciones, risas, noches especiales y momentos normales que contigo dejaron de sentirse normales.<br><br>
                Gracias por cada aventura, por los recuerdos que ya tenemos y por todo lo que todavía nos falta vivir. Me gusta pensar que esta app no termina aquí: va a ir creciendo igual que nuestra historia.<br><br>
                Te elijo hoy, mañana y en cada capítulo que venga, {BB}. ♡
              </div>
            </div>''',
        unsafe_allow_html=True,
    )

    today = date.today()
    left = max((SIX_MONTH_DATE - today).days, 0)
    if today < SIX_MONTH_DATE:
        st.markdown(f'<div class="paper-card" style="text-align:center"><div class="counter-num">{left}</div><div class="counter-label">días para nuestros 6 meses</div><div class="small-muted" style="margin-top:8px">13 de septiembre de 2026 ♡</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="paper-card" style="text-align:center"><div class="script-title">Feliz 6 meses, bb ♡</div><div class="small-muted">Y esto apenas comienza.</div></div>', unsafe_allow_html=True)

# Navegación inferior siempre visible
render_bottom_nav(section)
