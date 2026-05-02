import streamlit as st
from groq import Groq
from deep_translator import GoogleTranslator
from duckduckgo_search import DDGS
import warnings
import json
warnings.filterwarnings("ignore")

# ============================================================
import os
API_KEY = os.environ.get("GROQ_API_KEY", "")   # <-- paste your Groq key
# ============================================================

st.set_page_config(page_title="AURA - AI Student Mentor", page_icon="🧠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&display=swap');
* { font-family: 'Sora', sans-serif !important; }
.stApp { background: radial-gradient(ellipse at top, #0d0d2b 0%, #050510 100%); min-height: 100vh; }
.main-title {
    text-align: center; font-size: 3.5rem; font-weight: 800;
    background: linear-gradient(90deg, #00f5ff, #bf00ff, #ff6b6b, #00f5ff);
    background-size: 300% auto; -webkit-background-clip: text;
    -webkit-text-fill-color: transparent; animation: shimmer 3s linear infinite;
}
@keyframes shimmer { to { background-position: 300% center; } }
.subtitle { text-align: center; color: #7f8c8d; font-size: 1rem; margin-bottom: 1rem; }
.agent-badge {
    display: inline-block; padding: 4px 14px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600; margin-bottom: 8px;
}
.tutor-badge     { background: rgba(0,245,255,0.15); color: #00f5ff; border: 1px solid #00f5ff; }
.motivator-badge { background: rgba(255,107,107,0.15); color: #ff6b6b; border: 1px solid #ff6b6b; }
.planner-badge   { background: rgba(191,0,255,0.15); color: #bf00ff; border: 1px solid #bf00ff; }
.search-badge    { background: rgba(255,200,0,0.15); color: #ffc800; border: 1px solid #ffc800; }
.emotion-bar {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 12px; margin: 8px 0; font-size: 0.85rem; color: #ccd6f6;
}
.search-result {
    background: rgba(255,200,0,0.05); border: 1px solid rgba(255,200,0,0.2);
    border-radius: 10px; padding: 10px; margin: 6px 0; font-size: 0.82rem; color: #ccd6f6;
}
.stat-box {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 12px; text-align: center; color: #ccd6f6;
}
div[data-testid="stChatMessageContent"] p { color: #ccd6f6; line-height: 1.8; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── ANIMATED ROBOT FACE ────────────────────────────────────────────────────────
def render_robot_face(emotion="neutral", agent="tutor"):
    agent_colors = {
        "tutor":     {"body": "#1a3a8f", "light": "#3a6fd8", "glow": "#00f5ff", "screen": "#0a1a4a"},
        "motivator": {"body": "#8f1a1a", "light": "#d83a3a", "glow": "#ff6b6b", "screen": "#4a0a0a"},
        "planner":   {"body": "#4a1a8f", "light": "#7a3ad8", "glow": "#bf00ff", "screen": "#2a0a4a"},
        "search":    {"body": "#8f6a1a", "light": "#d8a83a", "glow": "#ffc800", "screen": "#4a3a0a"},
    }
    c = agent_colors.get(agent, agent_colors["tutor"])

    # Eye shapes per emotion
    eyes = {
        "neutral":  {"left": "M30,18 Q38,14 46,18 Q38,22 30,18Z", "right": "M74,18 Q82,14 90,18 Q82,22 74,18Z", "blink": "1"},
        "happy":    {"left": "M30,20 Q38,12 46,20", "right": "M74,20 Q82,12 90,20", "blink": "0"},
        "sad":      {"left": "M30,16 Q38,24 46,16", "right": "M74,16 Q82,24 90,16", "blink": "0"},
        "excited":  {"left": "M28,14 Q38,8  48,14 Q38,20 28,14Z", "right": "M72,14 Q82,8  92,14 Q82,20 72,14Z", "blink": "1"},
        "stressed": {"left": "M30,14 Q38,20 46,14", "right": "M74,14 Q82,20 90,14", "blink": "0"},
        "confused": {"left": "M30,18 Q38,14 46,18 Q38,22 30,18Z", "right": "M74,14 Q82,20 90,14", "blink": "0"},
    }

    # Mouth shapes per emotion
    mouths = {
        "neutral":  "M35,44 Q60,48 85,44",
        "happy":    "M30,40 Q60,58 90,40",
        "sad":      "M30,52 Q60,38 90,52",
        "excited":  "M28,38 Q60,62 92,38",
        "stressed": "M35,50 Q50,42 65,50 Q75,44 85,50",
        "confused": "M35,46 Q50,50 65,44 Q75,50 85,46",
    }

    eye_data = eyes.get(emotion, eyes["neutral"])
    mouth_d  = mouths.get(emotion, mouths["neutral"])

    # Extra elements for emotions
    extras = ""
    if emotion == "happy":
        extras = f'<circle cx="28" cy="38" r="8" fill="{c["glow"]}" opacity="0.15"/><circle cx="92" cy="38" r="8" fill="{c["glow"]}" opacity="0.15"/>'
    elif emotion == "stressed":
        extras = f'<line x1="32" y1="10" x2="28" y2="4" stroke="{c["glow"]}" stroke-width="2" stroke-linecap="round" opacity="0.6"/><line x1="44" y1="8" x2="44" y2="2" stroke="{c["glow"]}" stroke-width="2" stroke-linecap="round" opacity="0.6"/><line x1="76" y1="8" x2="76" y2="2" stroke="{c["glow"]}" stroke-width="2" stroke-linecap="round" opacity="0.6"/><line x1="88" y1="10" x2="92" y2="4" stroke="{c["glow"]}" stroke-width="2" stroke-linecap="round" opacity="0.6"/>'
    elif emotion == "confused":
        extras = f'<text x="95" y="18" fill="{c["glow"]}" font-size="14" opacity="0.8">?</text>'
    elif emotion == "excited":
        extras = f'<circle cx="60" cy="60" r="55" fill="none" stroke="{c["glow"]}" stroke-width="1" opacity="0.2"><animate attributeName="r" values="50;58;50" dur="1s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.2;0.05;0.2" dur="1s" repeatCount="indefinite"/></circle>'

    html = f"""
    <div style="display:flex;flex-direction:column;align-items:center;padding:10px 0;">
    <svg width="180" height="220" viewBox="0 0 120 220" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="bodyG" cx="40%" cy="30%" r="65%">
          <stop offset="0%" stop-color="{c['light']}"/>
          <stop offset="100%" stop-color="{c['body']}"/>
        </radialGradient>
        <radialGradient id="glowG" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="{c['glow']}" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="{c['glow']}" stop-opacity="0"/>
        </radialGradient>
        <filter id="gf"><feGaussianBlur stdDeviation="2.5"/></filter>
        <filter id="gf2"><feGaussianBlur stdDeviation="1.5"/></filter>
      </defs>

      <!-- Glow behind head -->
      <ellipse cx="60" cy="85" rx="52" ry="52" fill="url(#glowG)" filter="url(#gf)"/>

      <!-- Antenna -->
      <rect x="56" y="2" width="8" height="22" rx="4" fill="{c['light']}"/>
      <circle cx="60" cy="2" r="7" fill="{c['glow']}">
        <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/>
        <animate attributeName="r" values="6;8;6" dur="1.5s" repeatCount="indefinite"/>
      </circle>
      <!-- Antenna glow -->
      <circle cx="60" cy="2" r="12" fill="{c['glow']}" opacity="0.2" filter="url(#gf2)">
        <animate attributeName="opacity" values="0.2;0.05;0.2" dur="1.5s" repeatCount="indefinite"/>
      </circle>

      <!-- Ears -->
      <rect x="2" y="42" width="12" height="28" rx="6" fill="url(#bodyG)" stroke="{c['glow']}" stroke-width="0.5"/>
      <rect x="106" y="42" width="12" height="28" rx="6" fill="url(#bodyG)" stroke="{c['glow']}" stroke-width="0.5"/>
      <!-- Ear lights -->
      <circle cx="8" cy="56" r="3" fill="{c['glow']}" opacity="0.8">
        <animate attributeName="opacity" values="0.8;0.2;0.8" dur="2s" repeatCount="indefinite"/>
      </circle>
      <circle cx="112" cy="56" r="3" fill="{c['glow']}" opacity="0.8">
        <animate attributeName="opacity" values="0.2;0.8;0.2" dur="2s" repeatCount="indefinite"/>
      </circle>

      <!-- Head body -->
      <rect x="14" y="24" width="92" height="110" rx="18" fill="url(#bodyG)" stroke="{c['glow']}" stroke-width="1.5"/>

      <!-- Screen / face panel -->
      <rect x="22" y="32" width="76" height="80" rx="12" fill="{c['screen']}" stroke="{c['glow']}" stroke-width="1"/>

      <!-- Screen inner glow -->
      <rect x="24" y="34" width="72" height="76" rx="10" fill="{c['glow']}" opacity="0.04"/>

      <!-- EYES -->
      {"<!-- happy/sad arc eyes -->" if eye_data["blink"] == "0" else ""}
      {"" if eye_data["blink"] == "0" else f'<!-- filled eyes --><ellipse cx="38" cy="52" rx="9" ry="7" fill="{c["glow"]}" opacity="0.9"/><ellipse cx="82" cy="52" rx="9" ry="7" fill="{c["glow"]}" opacity="0.9"/><ellipse cx="38" cy="52" rx="4" ry="3" fill="{c["screen"]}"/><ellipse cx="82" cy="52" rx="4" ry="3" fill="{c["screen"]}"/>'}
      {"" if eye_data["blink"] == "1" else f'<path d="{eye_data["left"]}" stroke="{c["glow"]}" stroke-width="3" fill="none" stroke-linecap="round"/><path d="{eye_data["right"]}" stroke="{c["glow"]}" stroke-width="3" fill="none" stroke-linecap="round"/>'}

      <!-- Eye glow -->
      {"" if eye_data["blink"] == "0" else f'<ellipse cx="38" cy="52" rx="11" ry="9" fill="{c["glow"]}" opacity="0.12" filter="url(#gf2)"/><ellipse cx="82" cy="52" rx="11" ry="9" fill="{c["glow"]}" opacity="0.12" filter="url(#gf2)"/>'}

      <!-- EXTRAS (blush, sweat, etc) -->
      {extras}

      <!-- MOUTH -->
      <path d="{mouth_d}" stroke="{c['glow']}" stroke-width="2.5" fill="none" stroke-linecap="round"/>

      <!-- Neck -->
      <rect x="44" y="134" width="32" height="18" rx="6" fill="{c['body']}" stroke="{c['glow']}" stroke-width="0.8"/>

      <!-- Body/chest -->
      <rect x="20" y="150" width="80" height="55" rx="14" fill="url(#bodyG)" stroke="{c['glow']}" stroke-width="1.2"/>

      <!-- Chest panel -->
      <rect x="32" y="160" width="56" height="34" rx="8" fill="{c['screen']}" stroke="{c['glow']}" stroke-width="0.8"/>

      <!-- Chest lights -->
      <circle cx="45" cy="172" r="5" fill="{c['glow']}" opacity="0.9">
        <animate attributeName="opacity" values="0.9;0.2;0.9" dur="1.2s" repeatCount="indefinite"/>
      </circle>
      <circle cx="60" cy="172" r="5" fill="{c['glow']}" opacity="0.5">
        <animate attributeName="opacity" values="0.5;0.9;0.5" dur="1.2s" repeatCount="indefinite"/>
      </circle>
      <circle cx="75" cy="172" r="5" fill="{c['glow']}" opacity="0.2">
        <animate attributeName="opacity" values="0.2;0.9;0.2" dur="1.2s" repeatCount="indefinite"/>
      </circle>

      <!-- Chest bar -->
      <rect x="38" y="183" width="44" height="5" rx="2.5" fill="{c['glow']}" opacity="0.3">
        <animate attributeName="width" values="44;20;44" dur="2s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.3;0.7;0.3" dur="2s" repeatCount="indefinite"/>
      </rect>

      <!-- Floating scan line animation -->
      <rect x="22" y="34" width="76" height="2" rx="1" fill="{c['glow']}" opacity="0.15">
        <animate attributeName="y" values="34;108;34" dur="3s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.15;0.05;0.15" dur="3s" repeatCount="indefinite"/>
      </rect>
    </svg>

    <div style="color:{c['glow']};font-size:0.75rem;font-family:monospace;margin-top:-8px;letter-spacing:2px;opacity:0.8;">
      AURA v2.0
    </div>
    </div>
    """
    return html

# ── Voice OUTPUT ───────────────────────────────────────────────────────────────
def speak(text):
    safe_text = json.dumps(text[:400])
    st.components.v1.html(f"""
    <script>
        (function() {{
            try {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance({safe_text});
                msg.rate = 0.92; msg.pitch = 1.1; msg.volume = 1; msg.lang = 'en-IN';
                window.speechSynthesis.speak(msg);
            }} catch(e) {{ console.log('Voice error:', e); }}
        }})();
    </script>
    """, height=0)

# ── Voice INPUT mic button ─────────────────────────────────────────────────────
def render_mic_button():
    st.components.v1.html("""
    <style>
        .mic-wrap { display:flex; justify-content:center; padding:8px 0; }
        .mic-btn {
            width:60px; height:60px; border-radius:50%;
            background: linear-gradient(135deg,#00f5ff22,#bf00ff22);
            border:2px solid #00f5ff; cursor:pointer; font-size:26px;
            display:flex; align-items:center; justify-content:center; transition:all 0.3s;
        }
        .mic-btn:hover { transform:scale(1.1); background:linear-gradient(135deg,#00f5ff44,#bf00ff44); }
        .mic-btn.listening { border-color:#ff6b6b; animation:pulse-mic 1s infinite; }
        @keyframes pulse-mic {
            0%,100% { box-shadow:0 0 0 0 rgba(255,107,107,0.4); }
            50% { box-shadow:0 0 0 12px rgba(255,107,107,0); }
        }
        .popup-overlay {
            display:none; position:fixed; top:0; left:0;
            width:100%; height:100%; background:rgba(0,0,0,0.8);
            z-index:9999; align-items:center; justify-content:center;
        }
        .popup-overlay.show { display:flex; }
        .popup-box {
            background:#1a1a2e; border:1px solid #00f5ff;
            border-radius:16px; padding:28px; text-align:center; max-width:280px; width:90%;
        }
        .popup-box p { color:#ccd6f6; font-size:15px; margin-bottom:20px; font-family:sans-serif; }
        .popup-icon { font-size:44px; margin-bottom:12px; }
        .popup-btns { display:flex; gap:10px; justify-content:center; }
        .popup-btn { padding:10px 24px; border-radius:25px; font-size:14px; cursor:pointer; font-weight:600; border:none; transition:all 0.2s; }
        .btn-yes { background:linear-gradient(90deg,#00f5ff,#bf00ff); color:white; }
        .btn-yes:hover { transform:scale(1.05); }
        .btn-no { background:rgba(255,255,255,0.1); color:#ccd6f6; border:1px solid #444; }
        .status-text { text-align:center; color:#00f5ff; font-size:12px; margin-top:6px; font-family:sans-serif; min-height:18px; }
    </style>
    <div class="mic-wrap">
        <button class="mic-btn" id="micBtn" onclick="showPopup()" title="Speak your question">🎙️</button>
    </div>
    <div class="status-text" id="statusText"></div>
    <div class="popup-overlay" id="popupOverlay">
        <div class="popup-box">
            <div class="popup-icon">🎙️</div>
            <p><b>Speak your question to AURA?</b></p>
            <div class="popup-btns">
                <button class="popup-btn btn-yes" onclick="startListening()">✅ Yes, Listen</button>
                <button class="popup-btn btn-no" onclick="closePopup()">❌ No</button>
            </div>
        </div>
    </div>
    <script>
    function showPopup() { document.getElementById('popupOverlay').classList.add('show'); }
    function closePopup() { document.getElementById('popupOverlay').classList.remove('show'); }
    function startListening() {
        closePopup();
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            document.getElementById('statusText').innerHTML = '⚠️ Use Chrome browser!';
            return;
        }
        var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        var recognition = new SR();
        recognition.lang = 'en-IN';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        var btn = document.getElementById('micBtn');
        var status = document.getElementById('statusText');
        btn.classList.add('listening'); btn.innerHTML = '🔴';
        status.innerHTML = '🎙️ Listening... speak now!';
        recognition.start();
        recognition.onresult = function(e) {
            var transcript = e.results[0][0].transcript;
            status.innerHTML = '✅ "' + transcript + '"';
            btn.classList.remove('listening'); btn.innerHTML = '🎙️';
            var box = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (box) {
                var setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
                setter.call(box, transcript);
                box.dispatchEvent(new Event('input',{bubbles:true}));
                setTimeout(function() {
                    var send = window.parent.document.querySelector('[data-testid="stChatInputSubmitButton"]');
                    if (send) send.click();
                    status.innerHTML = '';
                }, 400);
            }
        };
        recognition.onerror = function() {
            btn.classList.remove('listening'); btn.innerHTML = '🎙️';
            status.innerHTML = '⚠️ Could not hear. Try again!';
        };
        recognition.onend = function() { btn.classList.remove('listening'); btn.innerHTML = '🎙️'; };
    }
    </script>
    """, height=140)

# ── Agent config ───────────────────────────────────────────────────────────────
AGENT_PROMPTS = {
    "tutor": """You are AURA's Tutor Agent — expert Indian student mentor.
Explain concepts clearly with examples. Use Hinglish naturally. For JEE/NEET give precise answers. Generate quizzes when asked.""",
    "motivator": """You are AURA's Motivator Agent — energetic Indian life coach.
Uplift students in Hinglish. Give powerful pep talks. Be like a caring dost who believes in them.""",
    "planner": """You are AURA's Planner Agent — study schedule expert.
Create detailed timetables. Break goals into daily tasks. Format plans clearly with timings.""",
    "search": """You are AURA's Search Agent with live web results.
Summarize search results clearly. Mention info is from live web search. Keep answers concise."""
}

AGENT_LABELS = {
    "tutor":     ("📚 Tutor Agent",     "tutor-badge"),
    "motivator": ("🔥 Motivator Agent", "motivator-badge"),
    "planner":   ("🗓️ Planner Agent",   "planner-badge"),
    "search":    ("🔍 Search Agent",    "search-badge"),
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def detect_emotion(text):
    t = text.lower()
    if any(w in t for w in ["stressed","tension","exam","scared","nervous","dar","pressure"]): return "stressed"
    elif any(w in t for w in ["sad","upset","cry","rona","dukhi","depressed","fail"]): return "sad"
    elif any(w in t for w in ["happy","great","amazing","khush","mast","excellent","wow"]): return "happy"
    elif any(w in t for w in ["excited","ready","pumped","let's go"]): return "excited"
    elif any(w in t for w in ["confused","don't understand","samajh","kyun","what","how"]): return "confused"
    return "neutral"

def detect_agent(text):
    t = text.lower()
    if any(w in t for w in ["search","latest","news","current","2026","cutoff","result","today","find"]): return "search"
    elif any(w in t for w in ["motivate","sad","stressed","give up","hopeless","tired","thak","haar"]): return "motivator"
    elif any(w in t for w in ["plan","schedule","timetable","routine","strategy","time table"]): return "planner"
    return "tutor"

def is_hindi(text):
    return any('\u0900' <= c <= '\u097f' for c in text)

def translate_to_english(text):
    try: return GoogleTranslator(source='auto', target='en').translate(text)
    except: return text

def translate_to_hindi(text):
    try: return GoogleTranslator(source='en', target='hi').translate(text)
    except: return text

def google_search(query, max_results=3):
    try:
        with DDGS() as ddgs: return list(ddgs.text(query, max_results=max_results))
    except: return []

def ask_aura(messages, agent, search_context=""):
    client = Groq(api_key=API_KEY)
    system = AGENT_PROMPTS[agent]
    if search_context: system += f"\n\nLIVE SEARCH RESULTS:\n{search_context}"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"system","content":system}] + messages,
        max_tokens=1024
    )
    return response.choices[0].message.content

# ── Session state ──────────────────────────────────────────────────────────────
for key, val in [("messages",[]),("emotion","neutral"),("agent","tutor"),
                  ("msg_count",0),("lang","English"),("voice_on",True)]:
    if key not in st.session_state: st.session_state[key] = val

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">⚡ AURA</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI Student Mentor · 🤖 Emotion Robot · 🎙️ Voice Input · 🔊 Voice Output · Google Search · Translate</div>', unsafe_allow_html=True)

# Emotion labels for display
emotion_labels = {"neutral":"😐 Neutral","happy":"😊 Happy","sad":"😢 Sad","excited":"🤩 Excited","stressed":"😰 Stressed","confused":"🤔 Confused"}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # 🤖 ANIMATED ROBOT FACE
    st.markdown(
        render_robot_face(st.session_state.emotion, st.session_state.agent),
        unsafe_allow_html=True
    )

    label, badge = AGENT_LABELS[st.session_state.agent]
    st.markdown(f'<div style="text-align:center"><span class="agent-badge {badge}">{label}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="emotion-bar">🧠 Mood: <b>{emotion_labels.get(st.session_state.emotion,"😐 Neutral")}</b></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎙️ Voice Input")
    st.markdown('<p style="color:#8892b0;font-size:0.78rem;margin:0">Click mic → Yes → speak your question!</p>', unsafe_allow_html=True)
    render_mic_button()

    st.markdown("---")
    st.session_state.voice_on = st.toggle("🔊 Voice Reply", value=st.session_state.voice_on)

    st.markdown("### 🌐 Translate")
    st.session_state.lang = st.radio("Language:", ["English","Hindi (हिंदी)","Auto"], index=0)

    st.markdown("### ⚡ Quick Actions")
    if st.button("📝 Quiz me!", use_container_width=True):
        st.session_state.messages.append({"role":"user","content":"Give me a 3-question JEE quiz."})
        st.rerun()
    if st.button("📅 Study Plan", use_container_width=True):
        st.session_state.messages.append({"role":"user","content":"Create a weekly JEE study plan."})
        st.rerun()
    if st.button("💪 Motivate me!", use_container_width=True):
        st.session_state.messages.append({"role":"user","content":"I'm stressed and losing hope. Motivate me."})
        st.rerun()
    if st.button("🔍 Latest JEE news", use_container_width=True):
        st.session_state.messages.append({"role":"user","content":"Search latest JEE 2026 news."})
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Stats")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-box">💬<br><b style="color:#00f5ff">{st.session_state.msg_count}</b><br><small>Messages</small></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box">🧠<br><b style="color:#bf00ff">{st.session_state.agent.title()}</b><br><small>Agent</small></div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []; st.session_state.msg_count = 0; st.rerun()

# ── Chat ───────────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("""👋 **Namaste! Main hoon AURA** — tera personal AI Student Mentor! 🤖✨

Sidebar mein mera **robot face** dekho — mood ke saath expression change hota hai!

- 📚 **Koi bhi concept** pooch
- 🔍 **Latest news** search karo
- 💪 **Motivation** lo
- 📅 **Study plan** banao
- 🎙️ **Mic** se bolo ya type karo!

Bol, kya help chahiye? 🚀""")

for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg["role"] == "assistant" and "agent" in msg:
            lbl, bdg = AGENT_LABELS[msg["agent"]]
            st.markdown(f'<span class="agent-badge {bdg}">{lbl}</span>', unsafe_allow_html=True)
        st.markdown(msg["content"])

if user_input := st.chat_input("Type here or use 🎙️ mic in sidebar..."):
    original_input = user_input
    user_input_en = translate_to_english(user_input) if is_hindi(user_input) else user_input

    st.session_state.emotion   = detect_emotion(user_input_en)
    st.session_state.agent     = detect_agent(user_input_en)
    st.session_state.msg_count += 1

    st.session_state.messages.append({"role":"user","content":original_input})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(original_input)

    with st.chat_message("assistant", avatar="🤖"):
        agent = st.session_state.agent
        lbl, bdg = AGENT_LABELS[agent]
        st.markdown(f'<span class="agent-badge {bdg}">{lbl}</span>', unsafe_allow_html=True)

        search_context = ""
        search_results = []

        with st.spinner("AURA soch raha hai... 🤖"):
            try:
                if agent == "search":
                    search_results = google_search(user_input_en)
                    if search_results:
                        search_context = "\n\n".join([
                            f"Title: {r.get('title','')}\nSummary: {r.get('body','')}"
                            for r in search_results])
                messages_for_ai = [{"role":m["role"],"content":m["content"]}
                                   for m in st.session_state.messages[-10:]]
                messages_for_ai[-1]["content"] = user_input_en
                reply = ask_aura(messages_for_ai, agent, search_context)

                if st.session_state.lang == "Hindi (हिंदी)":
                    reply = translate_to_hindi(reply)
                elif st.session_state.lang == "Auto" and is_hindi(original_input):
                    reply = translate_to_hindi(reply)

            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"

        if search_results:
            st.markdown("**🔍 Web Sources:**")
            for r in search_results:
                st.markdown(f'<div class="search-result">🌐 <b>{r.get("title","")}</b><br>{r.get("body","")[:120]}...</div>', unsafe_allow_html=True)

        st.markdown(reply)
        if st.session_state.voice_on:
            speak(reply)

    st.session_state.messages.append({"role":"assistant","content":reply,"agent":agent})
    st.rerun()