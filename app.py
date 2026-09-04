from __future__ import annotations

import base64
import calendar
import json
import re
import uuid
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps

# ============================================================
# S & J — App de 6 meses
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

# Las carpetas están ordenadas como las compartiste.
# Las coordenadas son solo para lugares públicos que sí podemos ubicar con seguridad.
# Los lugares privados se dejan fuera del mapa.
MOMENTS = [
    {
        "slug": "01_long_lake",
        "title": "Long Lake, Colorado",
        "short": "Long Lake",
        "category": "Aventura",
        "phrase": "Entre montañas y agua, cualquier camino se disfruta más contigo.",
        "coords": (40.078, -105.584),
        "map_note": "Ubicación aproximada del área de Long Lake.",
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
        "map_note": "Dime después cuál TopGolf fue y lo ponemos exacto en el mapa.",
    },
    {
        "slug": "05_primera_salida",
        "title": "Nuestra primera salida como novios",
        "short": "Primera salida",
        "category": "Nosotros",
        "phrase": "La primera salida con un nombre nuevo para lo nuestro: novios. ♡",
        "coords": None,
        "map_note": "Cuando me digas el lugar, lo agregamos al mapa.",
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
        "phrase": "También amo esto: comer contigo, platicar y sentir que cualquier momento sencillo puede volverse especial.",
        "coords": None,
        "map_note": "Este recuerdo se queda privado, sin ubicación en el mapa. ♡",
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
# PAGE + CSS
# ============================================================

st.set_page_config(
    page_title="S & J · Nuestros 6 meses",
    page_icon="♡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root {
    --paper:#fbf5ed;
    --paper2:#f2e5d8;
    --ink:#322925;
    --muted:#7c7068;
    --rose:#d89296;
    --rose2:#efd1cf;
    --gold:#bd9454;
    --black:#10100f;
}
html, body, [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 12% 6%, rgba(217,146,150,.11), transparent 26%),
      radial-gradient(circle at 90% 10%, rgba(189,148,84,.08), transparent 24%),
      linear-gradient(180deg,#fcf8f3 0%,#f5eadf 100%);
    color:var(--ink);
}
[data-testid="stHeader"] {background:transparent;}
.block-container {max-width:1180px;padding-top:1rem;padding-bottom:4rem;}
h1,h2,h3 {font-family:Georgia,'Times New Roman',serif!important;}

.hero {
  position:relative; overflow:hidden; border-radius:30px; padding:46px 32px 40px;
  background:linear-gradient(145deg,#0c0c0b,#1a1714 70%,#201a15);
  color:#f8eee1; border:1px solid rgba(189,148,84,.34);
  box-shadow:0 24px 60px rgba(63,42,30,.18);
}
.hero:after {content:"";position:absolute;width:480px;height:480px;border-radius:50%;right:-180px;top:-280px;background:radial-gradient(circle,rgba(189,148,84,.22),transparent 66%);}
.hero-kicker {position:relative;text-align:center;color:#d3ad72;letter-spacing:.28em;text-transform:uppercase;font-size:.76rem;z-index:1;}
.hero-title {position:relative;text-align:center;font:500 clamp(3.4rem,8vw,7rem)/1 Georgia,serif;z-index:1;margin:.4rem 0 .6rem;}
.hero-sub {position:relative;text-align:center;color:#d6c8bb;max-width:690px;margin:auto;z-index:1;line-height:1.7;}
.hero-heart {position:relative;z-index:1;text-align:center;color:#d3ad72;font-size:1.8rem;margin-top:14px;}

.paper-card {background:rgba(255,252,248,.93);border:1px solid rgba(102,75,57,.11);border-radius:22px;padding:22px;box-shadow:0 10px 30px rgba(76,54,39,.07);}
.scrap-note {background:#f1d6d2;border-radius:7px;padding:20px;box-shadow:0 8px 18px rgba(75,49,40,.09);transform:rotate(-.35deg);}
.scrap-note h3 {margin-top:0;text-align:center;}
.section-title {font:500 2.15rem Georgia,serif;margin:.5rem 0 .15rem;}
.section-sub {color:var(--muted);margin-bottom:1.3rem;}

.metric-shell {display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0 8px;}
.metric-card {background:linear-gradient(180deg,#fffaf5,#f1e2d7);border:1px solid rgba(216,146,150,.22);border-radius:22px;padding:22px 16px;text-align:center;min-height:145px;}
.metric-big {font:500 clamp(2.2rem,5vw,4rem)/1 Georgia,serif;color:#8c5f58;}
.metric-label {margin-top:.5rem;color:#756861;font-size:.92rem;}
.metric-mini {margin-top:.5rem;color:#aa7973;font-size:.82rem;}

.film-wrap {overflow-x:auto;padding:12px 4px 20px;scroll-snap-type:x mandatory;}
.film-roll {display:flex;gap:0;background:#111;padding:16px 10px;border-radius:16px;width:max-content;min-width:100%;box-shadow:0 12px 32px rgba(0,0,0,.17);}
.film-frame {width:190px;margin:0 8px;scroll-snap-align:start;}
.film-holes {height:9px;background:repeating-linear-gradient(90deg,#c59a55 0 9px,transparent 9px 18px);opacity:.7;margin:0 0 8px;}
.film-frame img {width:190px;height:225px;object-fit:cover;border:5px solid #1d1d1d;display:block;}
.film-caption {color:#e9d4b2;text-align:center;font-size:.78rem;padding:8px 4px 2px;white-space:normal;}

.polaroid {background:#fffdf9;border:1px solid rgba(0,0,0,.06);padding:10px 10px 23px;border-radius:5px;box-shadow:0 10px 28px rgba(56,39,28,.14);margin:8px 0 16px;}
.polaroid img {width:100%;height:300px;object-fit:cover;display:block;border-radius:2px;}
.polaroid-caption {padding:11px 5px 0;text-align:center;font:500 .98rem Georgia,serif;color:#574943;}

.location-card {background:#fffaf6;border:1px solid rgba(189,148,84,.18);border-radius:20px;padding:18px;margin-bottom:12px;}
.location-title {font:500 1.3rem Georgia,serif;}
.location-category {display:inline-block;color:#a56f6f;background:#f3dcd9;border-radius:999px;padding:4px 10px;font-size:.73rem;margin:.4rem 0;}
.location-phrase {color:#6d6059;font-style:italic;line-height:1.6;}

.question-num {width:38px;height:38px;border-radius:50%;background:#ecd2cf;color:#8f5f5d;display:flex;align-items:center;justify-content:center;font:500 1.1rem Georgia,serif;margin-bottom:8px;}
.reason-card {background:#fffaf6;border:1px solid rgba(189,148,84,.2);border-radius:19px;padding:18px;margin:8px 0;}
.reason-num {font:500 1.45rem Georgia,serif;color:#b17875;}
.reason-text {color:#50433f;line-height:1.6;margin-top:5px;}
.quote-strip {text-align:center;padding:24px 12px;font:italic 1.2rem Georgia,serif;color:#755b55;}

.stButton>button {border-radius:999px!important;border:1px solid rgba(158,108,91,.18)!important;background:linear-gradient(180deg,#da9b9b,#c97f83)!important;color:white!important;font-weight:650!important;min-height:42px;}
.stButton>button:hover {box-shadow:0 7px 20px rgba(168,101,103,.17);border-color:#b17072!important;}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {border-radius:14px!important;}
[data-baseweb="tab-list"] {gap:6px;background:rgba(255,251,247,.72);padding:6px;border-radius:18px;overflow-x:auto;}
[data-baseweb="tab"] {border-radius:13px;padding:9px 12px;white-space:nowrap;}
.small {font-size:.82rem;color:#81736b;}
.center {text-align:center;}



.login-shell{max-width:470px;margin:0 auto 1.2rem;}
.login-card{position:relative;overflow:hidden;border-radius:30px;background:linear-gradient(180deg,#fffdf9 0%,#f7ede3 100%);border:1px solid rgba(144,107,91,.12);box-shadow:0 18px 48px rgba(70,46,35,.12);padding:22px 18px 22px;}
.login-date-top{text-align:center;color:#ab7a75;letter-spacing:.28em;text-transform:uppercase;font-size:.74rem;margin-top:2px;}
.login-title{font-family:"Snell Roundhand","Apple Chancery","Brush Script MT","Segoe Script",cursive!important;text-align:center;font-size:clamp(3.6rem,10vw,5.4rem);line-height:.92;color:#40302c;margin:.35rem 0 0;}
.login-heart{text-align:center;color:#d68f99;font-size:1.08rem;line-height:1;margin:.25rem 0;}
.login-subtitle{text-align:center;font-family:Georgia,'Times New Roman',serif;color:#66534d;font-size:1.12rem;margin-bottom:1rem;}
.login-photo-panel{position:relative;height:250px;border-radius:24px;overflow:hidden;margin:0 auto 1rem;background:#e8ddd2;border:1px solid rgba(120,88,72,.08);}
.login-photo-panel img{width:100%;height:100%;object-fit:cover;object-position:center 30%;display:block;filter:saturate(.82) brightness(.60) blur(.2px);transform:scale(1.02);}
.login-photo-panel:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,250,245,.10) 0%,rgba(20,13,12,.18) 38%,rgba(14,10,10,.58) 100%);}
.login-photo-caption{position:absolute;left:18px;right:18px;bottom:14px;z-index:2;color:#fff6ee;text-shadow:0 2px 10px rgba(0,0,0,.25);}
.login-photo-caption .mini{font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:#f2d8cd;display:block;margin-bottom:.25rem;}
.login-photo-caption .main{font-family:Georgia,'Times New Roman',serif;font-size:1.2rem;line-height:1.25;}
.login-metrics{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:0 0 1rem;}
.login-metric{background:rgba(255,250,246,.86);border:1px solid rgba(214,143,153,.18);border-radius:18px;padding:15px 12px;text-align:center;}
.login-metric-big{font:500 1.55rem/1 Georgia,serif;color:#8a605f;}
.login-metric-label{color:#7d6d67;font-size:.83rem;margin-top:.25rem;line-height:1.25;}
.login-instruction{text-align:center;color:#5d4d47;font-family:Georgia,'Times New Roman',serif;font-size:1rem;margin:.35rem 0 .18rem;}
.login-instruction-sub{text-align:center;color:#9a847a;font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.35rem;}
.login-separator{text-align:center;color:#c79397;padding-top:.6rem;font:500 1.1rem Georgia,serif;}
.login-shell [data-testid="stTextInput"] input{text-align:center!important;border-radius:14px!important;min-height:50px!important;background:rgba(255,252,248,.95)!important;color:#4a3a35!important;border:1px solid rgba(171,122,117,.16)!important;font:500 1.02rem Georgia,serif!important;}
.login-shell [data-testid="stTextInput"] input::placeholder{color:#baa49a!important;}
.login-shell .stButton>button{border-radius:16px!important;min-height:49px!important;background:linear-gradient(180deg,#dca2a7,#cd858d)!important;border:1px solid rgba(173,113,118,.22)!important;box-shadow:0 8px 20px rgba(181,111,118,.14);}
.login-bottom-text{text-align:center;color:#78635d;font-family:Georgia,'Times New Roman',serif;font-style:italic;line-height:1.55;font-size:1rem;padding:.65rem .7rem 0;}
.login-bottom-text b{display:block;color:#5b4c46;font-style:normal;font-weight:500;margin-top:.25rem;}



/* ============================================================
   LOGIN SIMPLE V9 — solo pantalla de inicio refinada
   ============================================================ */
.simple-login-shell{max-width:430px;margin:0 auto 1.15rem;}
.simple-login-card{background:linear-gradient(180deg,#fffdfa 0%,#f8f1e9 100%);border:1px solid rgba(199,174,143,.20);border-radius:34px;box-shadow:0 22px 55px rgba(86,61,48,.10);overflow:hidden;padding:14px 14px 20px;}
.simple-login-photo{position:relative;height:346px;border-radius:26px;overflow:hidden;background:#e9ddd2;margin-bottom:1.05rem;}
.simple-login-photo img{width:100%;height:100%;object-fit:cover;object-position:center 28%;display:block;filter:saturate(.83) brightness(.64);transform:scale(1.04);}
.simple-login-photo:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,12,11,.22) 0%,rgba(18,12,11,.06) 28%,rgba(255,250,246,.00) 48%,rgba(255,250,246,.52) 74%,rgba(255,250,246,.90) 100%);}
.simple-login-toprow{position:absolute;left:16px;right:16px;top:14px;display:flex;justify-content:space-between;align-items:center;z-index:2;color:#f8ede2;}
.simple-login-menu,.simple-login-miniheart{font-size:1.15rem;line-height:1;opacity:.94;}
.simple-login-overlay{position:absolute;left:0;right:0;bottom:18px;z-index:2;text-align:center;padding:0 22px;}
.simple-login-monogram{display:inline-block;padding:0 .7rem;}
.simple-login-initials{font-family:"Didot","Bodoni MT","Times New Roman",serif!important;font-size:clamp(3rem,8vw,4rem);line-height:.92;color:#fff7f1;letter-spacing:.08em;text-shadow:0 5px 18px rgba(0,0,0,.18);margin:0;font-weight:400;}
.simple-login-divider{display:flex;align-items:center;justify-content:center;gap:10px;margin:.42rem 0 .3rem;}
.simple-login-divider:before,.simple-login-divider:after{content:"";display:block;width:38px;height:1px;background:rgba(255,241,228,.60);} 
.simple-login-divider span{color:#f3dac7;font-size:.95rem;line-height:1;}
.simple-login-story{font:500 1.06rem/1.1 Georgia,'Times New Roman',serif;color:#f7ebdf;letter-spacing:.02em;}
.simple-login-tagline{font-size:.95rem;line-height:1.38;color:#f1dfd3;margin-top:.4rem;}
.simple-login-heart{text-align:center;color:#c9a366;font-size:1.55rem;line-height:1;margin:.18rem 0 .3rem;}
.simple-login-title{text-align:center;font:500 2.18rem/1.06 Georgia,'Times New Roman',serif;color:#7b613b;margin:.14rem 0 .16rem;}
.simple-login-sub{text-align:center;color:#897b71;font-size:.95rem;margin-bottom:.75rem;}
.simple-login-together{display:flex;justify-content:center;margin:.15rem 0 .9rem;}
.simple-login-together-chip{display:inline-flex;align-items:center;gap:9px;background:#fffaf6;border:1px solid rgba(202,171,143,.36);border-radius:999px;padding:10px 16px;color:#7f675e;box-shadow:0 8px 18px rgba(146,110,95,.06);}
.simple-login-together-chip strong{font:500 1rem Georgia,serif;color:#6e5548;}
.simple-login-together-chip span{font-size:.9rem;}
.simple-login-inputs{margin:0 auto;max-width:310px;}
.simple-login-labels{display:grid;grid-template-columns:1fr 1fr 1.15fr;gap:10px;text-align:center;color:#baa69a;font-size:.67rem;letter-spacing:.17em;text-transform:uppercase;margin-top:.35rem;margin-bottom:.2rem;}
.simple-login-shell [data-testid="stTextInput"] input{text-align:center!important;border-radius:12px!important;min-height:52px!important;background:#fffaf5!important;color:#4c3c35!important;border:1px solid rgba(194,174,156,.45)!important;font:500 1.18rem Georgia,serif!important;box-shadow:none!important;}
.simple-login-shell [data-testid="stTextInput"] input::placeholder{color:transparent!important;}
.simple-login-shell .stButton>button{border-radius:18px!important;min-height:50px!important;background:linear-gradient(180deg,#e9b7b0,#d89599)!important;border:1px solid rgba(187,131,135,.22)!important;box-shadow:0 10px 24px rgba(181,111,118,.14);font-family:Georgia,'Times New Roman',serif!important;font-weight:600!important;letter-spacing:.03em;}
.simple-login-bottom{text-align:center;color:#8a776e;font-size:.92rem;line-height:1.55;padding:.9rem .55rem 0;}
.simple-login-bottom b{color:#6a5850;font-weight:500;}


/* ============================================================
   NAVEGACIÓN INFERIOR MÓVIL V12
   Iconos lineales elegantes y compatibles con móvil.
   ============================================================ */
.st-key-bottom_nav{
  position:fixed;
  left:50%;
  bottom:0;
  transform:translateX(-50%);
  width:min(100%,520px);
  z-index:9999;
  background:rgba(255,251,247,.96);
  border-top:1px solid rgba(154,124,103,.15);
  box-shadow:0 -10px 30px rgba(67,45,34,.08);
  backdrop-filter:blur(18px);
  -webkit-backdrop-filter:blur(18px);
  padding:.46rem .52rem calc(.46rem + env(safe-area-inset-bottom));
}
.st-key-bottom_nav [data-testid="stHorizontalBlock"]{gap:.18rem!important;align-items:flex-start!important;}
.st-key-bottom_nav [data-testid="column"]{min-width:0!important;}
.st-key-bottom_nav .stButton{margin:0!important;}
.st-key-bottom_nav .stButton>button{
  min-height:44px!important;
  width:100%!important;
  padding:.18rem!important;
  border:none!important;
  border-radius:16px!important;
  background:transparent!important;
  box-shadow:none!important;
  color:#8d7e75!important;
  font-size:0!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
}
.st-key-bottom_nav .stButton>button::before{
  content:"";
  display:block;
  width:23px;
  height:23px;
  background-color:currentColor;
  -webkit-mask-repeat:no-repeat;
  mask-repeat:no-repeat;
  -webkit-mask-position:center;
  mask-position:center;
  -webkit-mask-size:23px 23px;
  mask-size:23px 23px;
  transition:transform .15s ease, opacity .15s ease;
  opacity:.92;
}
.st-key-bottom_nav .stButton>button:hover{
  background:rgba(221,161,166,.10)!important;
  color:#c47f86!important;
  box-shadow:none!important;
}
.st-key-bottom_nav .stButton>button:hover::before{transform:translateY(-1px);opacity:1;}
.nav-caption{
  text-align:center;
  font-size:.58rem;
  line-height:1.08;
  color:#9a8a81;
  margin-top:-.06rem;
  white-space:nowrap;
}
.nav-caption.active{color:#c47f86;font-weight:700;}
.block-container{padding-bottom:7rem!important;}

.st-key-nav_inicio .stButton>button::before{
  -webkit-mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27M3.5%2010.5%2012%203.5l8.5%207M5.5%209.2V20h13V9.2M9.3%2020v-5.8h5.4V20%27%2F%3E%3C%2Fsvg%3E");
  mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27M3.5%2010.5%2012%203.5l8.5%207M5.5%209.2V20h13V9.2M9.3%2020v-5.8h5.4V20%27%2F%3E%3C%2Fsvg%3E");
}
.st-key-nav_album .stButton>button::before{
  -webkit-mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Crect%20x%3D%273.5%27%20y%3D%274.5%27%20width%3D%2717%27%20height%3D%2715%27%20rx%3D%273%27%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%2F%3E%3Ccircle%20cx%3D%279%27%20cy%3D%279%27%20r%3D%271.4%27%20fill%3D%27black%27%2F%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27m5.8%2016%204.1-4.1%203%203%202.6-2.6%202.8%202.8%27%2F%3E%3C%2Fsvg%3E");
  mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Crect%20x%3D%273.5%27%20y%3D%274.5%27%20width%3D%2717%27%20height%3D%2715%27%20rx%3D%273%27%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%2F%3E%3Ccircle%20cx%3D%279%27%20cy%3D%279%27%20r%3D%271.4%27%20fill%3D%27black%27%2F%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27m5.8%2016%204.1-4.1%203%203%202.6-2.6%202.8%202.8%27%2F%3E%3C%2Fsvg%3E");
}
.st-key-nav_mapa .stButton>button::before{
  -webkit-mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27M12%2021s6.2-5.9%206.2-11.2a6.2%206.2%200%201%200-12.4%200C5.8%2015.1%2012%2021%2012%2021Z%27%2F%3E%3Ccircle%20cx%3D%2712%27%20cy%3D%279.8%27%20r%3D%272.2%27%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%2F%3E%3C%2Fsvg%3E");
  mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27M12%2021s6.2-5.9%206.2-11.2a6.2%206.2%200%201%200-12.4%200C5.8%2015.1%2012%2021%2012%2021Z%27%2F%3E%3Ccircle%20cx%3D%2712%27%20cy%3D%279.8%27%20r%3D%272.2%27%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%2F%3E%3C%2Fsvg%3E");
}
.st-key-nav_preguntas .stButton>button::before{
  -webkit-mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27M7%2017.2%204.2%2020l.8-4.1A8.3%208.3%200%201%201%2020.3%2012%208.3%208.3%200%200%201%207%2017.2Z%27%2F%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20d%3D%27M9.7%209.2a2.5%202.5%200%201%201%204%202c-1%20.7-1.5%201.3-1.5%202.5%27%2F%3E%3Ccircle%20cx%3D%2712.2%27%20cy%3D%2716.2%27%20r%3D%270.8%27%20fill%3D%27black%27%2F%3E%3C%2Fsvg%3E");
  mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27M7%2017.2%204.2%2020l.8-4.1A8.3%208.3%200%201%201%2020.3%2012%208.3%208.3%200%200%201%207%2017.2Z%27%2F%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20d%3D%27M9.7%209.2a2.5%202.5%200%201%201%204%202c-1%20.7-1.5%201.3-1.5%202.5%27%2F%3E%3Ccircle%20cx%3D%2712.2%27%20cy%3D%2716.2%27%20r%3D%270.8%27%20fill%3D%27black%27%2F%3E%3C%2Fsvg%3E");
}
.st-key-nav_razones .stButton>button::before{
  -webkit-mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27M20.8%208.5c0%205.3-8.8%2011-8.8%2011s-8.8-5.7-8.8-11A4.7%204.7%200%200%201%2012%206a4.7%204.7%200%200%201%208.8%202.5Z%27%2F%3E%3C%2Fsvg%3E");
  mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27M20.8%208.5c0%205.3-8.8%2011-8.8%2011s-8.8-5.7-8.8-11A4.7%204.7%200%200%201%2012%206a4.7%204.7%200%200%201%208.8%202.5Z%27%2F%3E%3C%2Fsvg%3E");
}
.st-key-nav_carta .stButton>button::before{
  -webkit-mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Crect%20x%3D%273.5%27%20y%3D%275.8%27%20width%3D%2717%27%20height%3D%2712.4%27%20rx%3D%272.6%27%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%2F%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27m5.5%208.2%206.5%205%206.5-5%27%2F%3E%3C%2Fsvg%3E");
  mask-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%3E%3Crect%20x%3D%273.5%27%20y%3D%275.8%27%20width%3D%2717%27%20height%3D%2712.4%27%20rx%3D%272.6%27%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%2F%3E%3Cpath%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.8%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%20d%3D%27m5.5%208.2%206.5%205%206.5-5%27%2F%3E%3C%2Fsvg%3E");
}
@media(max-width:760px){
 .st-key-bottom_nav{width:100%;border-radius:0;padding-left:.3rem;padding-right:.3rem}.nav-caption{font-size:.56rem}.st-key-bottom_nav .stButton>button{font-size:1.23rem!important;min-height:35px!important}
 .simple-login-shell{max-width:100%}.simple-login-card{border-radius:28px;padding:12px 12px 18px}.simple-login-photo{height:328px;border-radius:24px}.simple-login-title{font-size:2.05rem}.simple-login-story{font-size:1rem}.simple-login-initials{font-size:3.45rem}.simple-login-together-chip{padding:9px 14px}.simple-login-bottom{font-size:.89rem}.login-shell{max-width:100%}.login-card{border-radius:24px;padding:18px 14px 20px}.login-title{font-size:4.1rem}.login-photo-panel{height:230px;border-radius:22px}.login-metrics{grid-template-columns:1fr 1fr;gap:8px}.login-metric{padding:12px 9px}.login-metric-big{font-size:1.35rem}.block-container{padding-left:.85rem;padding-right:.85rem}.hero{padding:34px 18px 30px;border-radius:22px}
 .metric-shell{grid-template-columns:1fr}.polaroid img{height:260px}.film-frame,.film-frame img{width:160px}.film-frame img{height:200px}
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================

IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_TYPES = {".mp4", ".mov", ".m4v"}


def digits_only(value: str) -> str:
    return "".join(c for c in value if c.isdigit())


def add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def relationship_snapshot(today: date | None = None) -> dict:
    today = today or date.today()
    if today < RELATIONSHIP_START:
        return {
            "total_days": 0,
            "months": 0,
            "days": 0,
            "days_to_six_months": max(0, (SIX_MONTH_DATE - today).days),
        }

    total_days = (today - RELATIONSHIP_START).days
    months = (today.year - RELATIONSHIP_START.year) * 12 + (today.month - RELATIONSHIP_START.month)
    anchor = add_months(RELATIONSHIP_START, months)
    if anchor > today:
        months -= 1
        anchor = add_months(RELATIONSHIP_START, months)
    days = (today - anchor).days
    return {
        "total_days": total_days,
        "months": months,
        "days": days,
        "days_to_six_months": max(0, (SIX_MONTH_DATE - today).days),
    }


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


def image_uri(path: Path, max_side: int = 900) -> str | None:
    try:
        im = Image.open(path)
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((max_side, max_side))
        from io import BytesIO
        buf = BytesIO()
        im.save(buf, format="JPEG", quality=84)
        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"
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
        ok = write_json(BB_MEMORY_DB, db)
        return ok, saved
    except Exception:
        return False, saved


def bb_uploads(album: str | None = None):
    records = read_json(BB_MEMORY_DB, [])
    if album is None:
        return records
    return [r for r in records if r.get("album") == album]


def polaroid(path: Path, caption: str):
    uri = image_uri(path)
    if not uri:
        return
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


def render_film_roll():
    frames = []
    for moment in MOMENTS:
        cover = cover_for(moment)
        if not cover:
            continue
        uri = image_uri(cover, 520)
        if not uri:
            continue
        frames.append(
            f'<div class="film-frame"><div class="film-holes"></div><img src="{uri}"><div class="film-caption">{moment["short"]}</div><div class="film-holes" style="margin:8px 0 0"></div></div>'
        )
    st.markdown(
        '<div class="film-wrap"><div class="film-roll">' + "".join(frames) + "</div></div>",
        unsafe_allow_html=True,
    )


def live_counter_component():
    components.html(
        """
        <div id="metrics" class="metric-shell"></div>
        <style>
          body{margin:0;background:transparent;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#322925}
          .metric-shell{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
          .metric-card{box-sizing:border-box;background:linear-gradient(180deg,#fffaf5,#f1e2d7);border:1px solid rgba(216,146,150,.24);border-radius:22px;padding:22px 16px;text-align:center;min-height:145px}
          .metric-big{font:500 clamp(2.1rem,5vw,3.7rem)/1 Georgia,serif;color:#8c5f58}.metric-label{margin-top:.5rem;color:#756861;font-size:.92rem}.metric-mini{margin-top:.55rem;color:#aa7973;font-size:.82rem}
          @media(max-width:650px){.metric-shell{grid-template-columns:1fr}.metric-card{min-height:125px}}
        </style>
        <script>
        const start = new Date(2026, 2, 13, 0, 0, 0);
        const target = new Date(2026, 8, 13, 0, 0, 0);
        const dayMs = 86400000;

        function calendarParts(now){
          if(now < start) return {months:0, days:0};
          let months=(now.getFullYear()-start.getFullYear())*12+(now.getMonth()-start.getMonth());
          let anchor=new Date(start.getFullYear(), start.getMonth()+months, start.getDate());
          if(anchor>now){months--; anchor=new Date(start.getFullYear(), start.getMonth()+months, start.getDate());}
          const days=Math.floor((new Date(now.getFullYear(),now.getMonth(),now.getDate())-new Date(anchor.getFullYear(),anchor.getMonth(),anchor.getDate()))/dayMs);
          return {months,days};
        }
        function render(){
          const now=new Date();
          const daysTogether=Math.max(0,Math.floor((new Date(now.getFullYear(),now.getMonth(),now.getDate())-start)/dayMs));
          const parts=calendarParts(now);
          let diff=target-now;
          let countdown='';
          if(diff>0){
            const d=Math.floor(diff/dayMs); diff-=d*dayMs;
            const h=Math.floor(diff/3600000); diff-=h*3600000;
            const m=Math.floor(diff/60000); diff-=m*60000;
            const s=Math.floor(diff/1000);
            countdown=`<div class="metric-big">${d}</div><div class="metric-label">días para nuestros 6 meses</div><div class="metric-mini">${String(h).padStart(2,'0')} h · ${String(m).padStart(2,'0')} min · ${String(s).padStart(2,'0')} seg</div>`;
          } else {
            countdown=`<div class="metric-big">♡</div><div class="metric-label">Ya cumplimos 6 meses</div><div class="metric-mini">Y lo mejor apenas comienza.</div>`;
          }
          document.getElementById('metrics').innerHTML=`
            <div class="metric-card"><div class="metric-big">${daysTogether}</div><div class="metric-label">días juntos</div><div class="metric-mini">${parts.months} meses y ${parts.days} días siendo novios</div></div>
            <div class="metric-card"><div class="metric-big">6</div><div class="metric-label">meses</div><div class="metric-mini">13 de septiembre de 2026 ♡</div></div>
            <div class="metric-card">${countdown}</div>`;
        }
        render(); setInterval(render,1000);
        </script>
        """,
        height=178,
        scrolling=False,
    )


# ============================================================
# SESSION / LOGIN
# ============================================================

if "unlocked" not in st.session_state:
    st.session_state.unlocked = False
if "reason_selected" not in st.session_state:
    st.session_state.reason_selected = None

if not st.session_state.unlocked:
    snapshot = relationship_snapshot()
    login_photo = ASSETS_DIR / "login_red_jacket_cover.jpg"
    login_uri = image_uri(login_photo, 1400) if login_photo.exists() else None

    left, center, right = st.columns([1, 1.05, 1])
    with center:
        st.markdown('<div class="simple-login-shell">', unsafe_allow_html=True)
        st.markdown('<div class="simple-login-card">', unsafe_allow_html=True)

        if login_uri:
            st.markdown(
                f"""
                <div class="simple-login-photo">
                  <img src="{login_uri}" alt="S y J">
                  <div class="simple-login-toprow">
                    <div class="simple-login-menu">≡</div>
                    <div class="simple-login-miniheart">♡</div>
                  </div>
                  <div class="simple-login-overlay">
                    <div class="simple-login-monogram">
                      <div class="simple-login-initials">{INITIALS}</div>
                      <div class="simple-login-divider"><span>♡</span></div>
                    </div>
                    <div class="simple-login-story">Nuestra historia</div>
                    <div class="simple-login-tagline">La noche en que comenzó lo nuestro, bb ♡</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="simple-login-heart">♡</div>', unsafe_allow_html=True)
        st.markdown('<div class="simple-login-title">Ingresa nuestra<br>fecha</div>', unsafe_allow_html=True)
        st.markdown('<div class="simple-login-sub">Ese día cambió todo.</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="simple-login-together"><div class="simple-login-together-chip"><strong>{snapshot["months"]} meses · {snapshot["days"]} días</strong><span>siendo novios</span></div></div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="simple-login-inputs">', unsafe_allow_html=True)
        dcol, mcol, ycol = st.columns([1, 1, 1.15], gap="small")
        with dcol:
            code_day = st.text_input("Día", value="", placeholder="", max_chars=2, label_visibility="collapsed", key="login_day")
        with mcol:
            code_month = st.text_input("Mes", value="", placeholder="", max_chars=2, label_visibility="collapsed", key="login_month")
        with ycol:
            code_year = st.text_input("Año", value="", placeholder="", max_chars=4, label_visibility="collapsed", key="login_year")

        st.markdown('<div class="simple-login-labels"><div>Día</div><div>Mes</div><div>Año</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Comenzar", use_container_width=True):
            code = f"{code_day}{code_month}{code_year}"
            if digits_only(code) == ACCESS_CODE:
                st.session_state.unlocked = True
                st.rerun()
            else:
                st.error("Mmm bb… esa no es nuestra fecha 👀♡")

        st.markdown(
            '<div class="simple-login-bottom">No es solo una fecha. <b>Es el inicio de nuestra historia favorita.</b></div>',
            unsafe_allow_html=True,
        )

        st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# ============================================================
# MAIN APP
# ============================================================

st.markdown(
    f"""
    <div class="hero">
      <div class="hero-kicker">Nuestro lugar favorito: juntos</div>
      <div class="hero-title">{INITIALS}</div>
      <div class="hero-sub">
        Hola {BB} ♡ Este es nuestro álbum, nuestro mapa y un pedacito de todo lo que hemos vivido desde el 13 de marzo.
      </div>
      <div class="hero-heart">♡</div>
    </div>
    """,
    unsafe_allow_html=True,
)

live_counter_component()

st.markdown('<div class="quote-strip">“No es la cantidad de tiempo, es todo lo que hemos vivido juntos.” ♡</div>', unsafe_allow_html=True)

if "nav_section" not in st.session_state:
    st.session_state.nav_section = "Inicio"

def _go_to_section(section_name: str):
    st.session_state.nav_section = section_name

NAV_ITEMS = [
    ("Inicio", " ", "nav_inicio"),
    ("Álbum", " ", "nav_album"),
    ("Mapa", " ", "nav_mapa"),
    ("Preguntas", " ", "nav_preguntas"),
    ("Razones", " ", "nav_razones"),
    ("Carta", " ", "nav_carta"),
]

with st.container(key="bottom_nav"):
    nav_cols = st.columns(6, gap="small")
    for col, (section_name, icon, button_key) in zip(nav_cols, NAV_ITEMS):
        with col:
            st.button(
                icon,
                key=button_key,
                use_container_width=True,
                on_click=_go_to_section,
                args=(section_name,),
                help=section_name,
            )
            active_class = " active" if st.session_state.nav_section == section_name else ""
            st.markdown(
                f'<div class="nav-caption{active_class}">{section_name}</div>',
                unsafe_allow_html=True,
            )

_active_key = next(item[2] for item in NAV_ITEMS if item[0] == st.session_state.nav_section)
st.markdown(
    "<style>.st-key-" + _active_key + " .stButton>button{color:#c47f86!important;background:rgba(221,161,166,.11)!important;}"
    + ".st-key-" + _active_key + " .stButton>button::before{opacity:1;transform:translateY(-1px);}</style>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# INICIO
# ------------------------------------------------------------
if st.session_state.nav_section == "Inicio":
    st.markdown('<div class="section-title">Nuestro rollo fotográfico</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Deslízalo: cada cuadro es una salida, un viaje o un momento que ya forma parte de nosotros.</div>', unsafe_allow_html=True)
    render_film_roll()

    left, right = st.columns([1.05, .95])
    with left:
        st.markdown(
            f"""
            <div class="scrap-note">
              <h3>Para nosotros, cada momento cuenta ♡</h3>
              <p>No quise hacerte solamente una tarjeta, {BB}. Quise hacer un lugar al que puedas volver, mirar nuestras fotos y recordar todo lo que hemos ido construyendo.</p>
              <p>Hay salidas grandes, viajes, noches especiales y también momentos simples. Para mí todos cuentan porque los viví contigo.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="paper-card">
              <h3 style="margin-top:0">Lo que ya vive aquí</h3>
              <p>♡ 10 recuerdos organizados por lugar o salida.</p>
              <p>♡ Fotos estilo Polaroid y videos de nuestras aventuras.</p>
              <p>♡ Un mapa de los lugares públicos que hemos visitado.</p>
              <p>♡ 5 preguntas para ver nuestra historia desde tus ojos.</p>
              <p>♡ 10 razones escondidas para descubrir una por una.</p>
              <p>♡ Y un espacio para que tú también agregues tus fotos favoritas.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ------------------------------------------------------------
# ALBUM
# ------------------------------------------------------------
if st.session_state.nav_section == "Álbum":
    st.markdown('<div class="section-title">Nuestro álbum ♡</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Cada lugar tiene su propia pequeña historia. Abre los recuerdos y recórrelos a tu ritmo.</div>', unsafe_allow_html=True)

    # Mini navegación por recuerdo
    moment_names = [m["title"] for m in MOMENTS]
    selected_name = st.selectbox("Ir directamente a un recuerdo", ["Ver todos"] + moment_names)
    filtered = MOMENTS if selected_name == "Ver todos" else [m for m in MOMENTS if m["title"] == selected_name]

    for n, moment in enumerate(filtered, 1):
        photos, videos = media_for_moment(moment)
        user_records = bb_uploads(moment["slug"])
        with st.expander(f"{moment['short']} · {moment['category']} ♡", expanded=(selected_name != "Ver todos" or n == 1)):
            st.markdown(
                f"""
                <div class="location-card">
                  <div class="location-title">{moment['title']}</div>
                  <div class="location-category">{moment['category']}</div>
                  <div class="location-phrase">“{moment['phrase']}”</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            all_photo_items = [(p, moment["short"]) for p in photos]
            cols = st.columns(2 if len(all_photo_items) > 1 else 1)
            for i, (photo, caption) in enumerate(all_photo_items):
                with cols[i % len(cols)]:
                    polaroid(photo, caption)

            if videos:
                st.markdown("**Un pedacito en movimiento 🎥**")
                for video in videos:
                    st.video(str(video))

            if user_records:
                st.markdown(f"**Fotos que {BB} agregó a este recuerdo ♡**")
                ucols = st.columns(2)
                for i, record in enumerate(user_records):
                    with ucols[i % 2]:
                        polaroid_record(record)

    # Fotos nuevas de ella
    st.write("")
    st.markdown('<div class="section-title">Agrega tus favoritas, bb ♡</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Puedes sumar fotos tuyas que quieras guardar dentro de nuestro álbum.</div>', unsafe_allow_html=True)

    with st.form("bb_upload_form", clear_on_submit=True):
        album_label = st.selectbox(
            "¿A qué recuerdo pertenece?",
            ["Álbum general"] + [m["title"] for m in MOMENTS],
        )
        title = st.text_input("Ponle un nombre", placeholder="Ej. Una de mis fotos favoritas")
        message = st.text_area("¿Quieres escribir algo?", placeholder="Ej. Me encanta este día porque…", height=85)
        files = st.file_uploader("Sube una o varias fotos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
        submitted = st.form_submit_button("Guardar en nuestro álbum ♡", use_container_width=True)

    if submitted:
        if not files:
            st.warning("Primero elige al menos una foto, bb ♡")
        else:
            slug_by_title = {m["title"]: m["slug"] for m in MOMENTS}
            album = "general" if album_label == "Álbum general" else slug_by_title[album_label]
            ok, saved = save_bb_uploads(album, title, message, files)
            if ok and saved:
                st.success(f"Listo bb ♡ Guardé {saved} foto(s) en nuestro álbum.")
                st.rerun()
            else:
                st.error("No pude guardar las fotos en el disco de esta versión. Más adelante podemos conectarlo a Supabase para que queden guardadas en la nube.")

    general_records = bb_uploads("general")
    if general_records:
        st.markdown("### Las favoritas que bb agregó ♡")
        gcols = st.columns(3)
        for i, record in enumerate(general_records):
            with gcols[i % 3]:
                polaroid_record(record)

# ------------------------------------------------------------
# MAPA
# ------------------------------------------------------------
if st.session_state.nav_section == "Mapa":
    st.markdown('<div class="section-title">Nuestro mapa de recuerdos 📍</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Cada punto es una historia que ya podemos volver a visitar. Los lugares privados no aparecen por ubicación.</div>', unsafe_allow_html=True)

    mapped = [m for m in MOMENTS if m.get("coords")]
    df = pd.DataFrame([
        {"lat": m["coords"][0], "lon": m["coords"][1], "Lugar": m["title"]}
        for m in mapped
    ])
    st.map(df, latitude="lat", longitude="lon", size=90, zoom=5)

    place = st.selectbox("Explora un punto del mapa", [m["title"] for m in mapped], key="map_place")
    chosen = next(m for m in mapped if m["title"] == place)
    cover = cover_for(chosen)
    c1, c2 = st.columns([.8, 1.2])
    with c1:
        if cover:
            polaroid(cover, chosen["short"])
    with c2:
        st.markdown(
            f"""
            <div class="paper-card">
              <h3 style="margin-top:0">{chosen['title']}</h3>
              <p style="font-family:Georgia,serif;font-style:italic">“{chosen['phrase']}”</p>
              <p class="small">Cada lugar, un recuerdo. Cada recuerdo, tú y yo. ♡</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info("TopGolf y nuestra primera salida todavía no tienen ubicación exacta en el mapa. En cuanto me digas dónde fueron, los agregamos. La comida en el depa se mantiene privada a propósito.")

# ------------------------------------------------------------
# 5 PREGUNTAS
# ------------------------------------------------------------
if st.session_state.nav_section == "Preguntas":
    st.markdown(f'<div class="section-title">5 preguntas para ti, {BB} ♡</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">No es un examen. Solo quiero saber cómo se ve nuestra historia desde tus ojos.</div>', unsafe_allow_html=True)

    saved_answers = read_json(ANSWERS_DB, {})
    with st.form("questions_form"):
        responses = {}
        for i, q in enumerate(QUESTIONS, 1):
            st.markdown(f'<div class="question-num">{i}</div><b>{q}</b>', unsafe_allow_html=True)
            responses[str(i)] = st.text_area(
                f"Respuesta {i}",
                value=saved_answers.get(str(i), ""),
                placeholder="Escribe aquí lo que piensas…",
                height=95,
                label_visibility="collapsed",
                key=f"question_{i}",
            )
            st.write("")
        save_answers = st.form_submit_button("Guardar mis respuestas ♡", use_container_width=True)

    if save_answers:
        if write_json(ANSWERS_DB, responses):
            st.success("Ya quedaron guardadas, bb ♡ Estas respuestas también son parte de nuestra historia.")
        else:
            st.error("No pude guardar las respuestas en el disco de esta versión.")

# ------------------------------------------------------------
# 10 RAZONES
# ------------------------------------------------------------
if st.session_state.nav_section == "Razones":
    st.markdown('<div class="section-title">10 razones por las que amo estar contigo ♡</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Toca un corazón, {BB}. No quiero que las leas todas de golpe.</div>', unsafe_allow_html=True)

    cols = st.columns(5)
    for i in range(10):
        with cols[i % 5]:
            if st.button(f"♡ {i+1}", key=f"reason_{i}", use_container_width=True):
                st.session_state.reason_selected = i

    if st.session_state.reason_selected is None:
        st.markdown('<div class="scrap-note"><h3>Hay 10 pequeños mensajes escondidos aquí ♡</h3><p class="center">Elige el corazón que quieras abrir primero.</p></div>', unsafe_allow_html=True)
    else:
        i = st.session_state.reason_selected
        st.markdown(
            f"""
            <div class="reason-card">
              <div class="reason-num">Razón #{i+1}</div>
              <div class="reason-text">{REASONS[i]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ------------------------------------------------------------
# CARTA
# ------------------------------------------------------------
if st.session_state.nav_section == "Carta":
    st.markdown(f'<div class="section-title">Para ti, {BB} ♡</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Una última página antes de seguir escribiendo las siguientes.</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="scrap-note">
          <h3>Mi bb,</h3>
          <p>Quise hacer esto porque seis meses pueden parecer solo una fecha, pero cuando pienso en todo lo que hemos vivido dentro de ese tiempo, para mí significa muchísimo más.</p>
          <p>Me gustan nuestros viajes y nuestras salidas, pero también me gustan los momentos normales: comer juntos, platicar, reírnos, estar cansados y aun así querer compartir el rato.</p>
          <p>No somos perfectos, pero nuestra historia es mi favorita. Gracias por cada aventura, por cada foto y por todo lo que todavía nos falta conocer juntos.</p>
          <p>Porque lo mejor apenas comienza… ♡</p>
          <p style="text-align:right;font-family:Georgia,serif;font-size:1.08rem">— J</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown(
        """
        <div class="paper-card center">
          <h3>Nuestro próximo capítulo</h3>
          <p>13 de septiembre de 2026 · 6 meses juntos ♡</p>
          <p class="small">Y después… otro mes, otro viaje, otra foto, otra historia.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="quote-strip">“Cada salida nos trajo hasta aquí.” · S & J ♡</div>', unsafe_allow_html=True)
