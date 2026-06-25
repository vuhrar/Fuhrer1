<< 'PYEOF'
"""
Führer """

import streamlit as st
import re, io, os, json, logging, hashlib, base64
from datetime import datetime, timedelta
from typing import Dict, List
import urllib.request, urllib.error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fuehrer")

st.set_page_config(
    page_title="⚖️ Führer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════
# الخلفية والتصميم
# ══════════════════════════════════════════════
def get_bg(path="bg.png"):
    """تحميل الخلفية من ملف محلي أو إرجاع فارغ"""
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

bg_b64 = get_bg("bg.png")
bg_css = f"""
background-image: url("data:image/png;base64,{bg_b64}");
background-size: cover;
background-position: center;
background-attachment: fixed;
background-repeat: no-repeat;
""" if bg_b64 else "background:#0a0a0a;"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');
*{{box-sizing:border-box}}

/* الخلفية الرئيسية */
.stApp{{
    {bg_css}
    color:#f0ead0;
    font-family:'Cairo',sans-serif;
    direction:rtl;
}}
.stApp::before{{
    content:'';
    position:fixed;
    top:0;left:0;right:0;bottom:0;
    background:rgba(0,0,0,0.82);
    z-index:0;
    pointer-events:none;
}}
.stApp > * {{position:relative;z-index:1;}}

/* الشريط الجانبي */
[data-testid="stSidebar"]{{
    background:rgba(8,12,20,0.97)!important;
    border-left:1px solid #1e2a40;
}}
[data-testid="stSidebar"] *{{color:#c8c0b0!important}}

/* العناوين */
h1,h2,h3{{color:#f0c040!important;font-weight:700}}

/* التبويبات */
.stTabs [data-baseweb="tab-list"]{{
    background:rgba(13,19,32,0.95);
    border-bottom:2px solid #1e2a40;
    gap:3px;padding:4px;
    border-radius:8px 8px 0 0;
}}
.stTabs [data-baseweb="tab"]{{
    background:transparent!important;
    color:#8090a0!important;
    border:1px solid transparent!important;
    border-radius:6px!important;
    padding:7px 14px!important;
    font-size:13px;
    font-family:'Cairo',sans-serif;
}}
.stTabs [data-baseweb="tab"][aria-selected="true"]{{
    background:#1a2235!important;
    color:#f0c040!important;
    border-color:#f0c040!important;
    font-weight:700;
}}
.stTabs [data-baseweb="tab-panel"]{{
    background:rgba(10,15,26,0.97);
    border:1px solid #1e2a40;
    border-radius:0 0 8px 8px;
    padding:18px;
}}

/* المدخلات */
.stTextInput>div>div>input,
.stTextArea textarea{{
    background:rgba(13,19,32,0.98)!important;
    color:#e8e0d0!important;
    border:1px solid #2a3a55!important;
    border-radius:6px!important;
    font-family:'Cairo',sans-serif!important;
}}
.stTextInput>div>div>input:focus,
.stTextArea textarea:focus{{
    border-color:#f0c040!important;
    box-shadow:0 0 0 2px rgba(240,192,64,.2)!important;
}}

/* الأزرار */
.stButton>button{{
    background:linear-gradient(135deg,#c8a020,#f0c040)!important;
    color:#0a0f1a!important;
    border:none!important;
    border-radius:6px!important;
    font-weight:700!important;
    font-family:'Cairo',sans-serif!important;
    padding:10px 18px!important;
    transition:all .2s!important;
}}
.stButton>button:hover{{
    transform:translateY(-1px);
    box-shadow:0 4px 16px rgba(240,192,64,.4)!important;
}}

/* المقاييس */
[data-testid="stMetric"]{{
    background:rgba(13,19,32,0.95);
    border:1px solid #1e2a40;
    border-radius:8px;padding:12px 16px;
}}
[data-testid="stMetricLabel"]{{color:#8090a0!important;font-size:12px}}
[data-testid="stMetricValue"]{{color:#f0c040!important;font-weight:700;font-size:22px}}

/* القوائم المنسدلة */
.stSelectbox [data-baseweb="select"]>div{{
    background:rgba(13,19,32,0.98)!important;
    border-color:#2a3a55!important;
    color:#e8e0d0!important;
}}

/* البطاقات المخصصة */
.chat-user{{
    background:rgba(26,34,53,0.95);
    border:1px solid #2a3a55;
    border-radius:12px 12px 2px 12px;
    padding:12px 16px;margin:8px 0;
    max-width:82%;float:right;clear:both;direction:rtl;
}}
.chat-ai{{
    background:rgba(13,26,42,0.97);
    border:1px solid #1e3a50;
    border-radius:12px 12px 12px 2px;
    padding:12px 16px;margin:8px 0;
    max-width:88%;float:left;clear:both;direction:rtl;
    border-left:3px solid #f0c040;
}}
.chat-wrap{{overflow:hidden;min-height:60px}}
.mem-card{{
    background:rgba(13,19,32,0.95);
    border:1px solid #1e2a40;
    border-radius:8px;padding:12px;margin:5px 0;direction:rtl;
}}
.ok-card{{
    background:rgba(40,100,60,.2);
    border:1px solid rgba(64,192,96,.4);
    border-radius:6px;padding:9px 14px;margin:3px 0;direction:rtl;
}}
.bad-card{{
    background:rgba(100,30,30,.2);
    border:1px solid rgba(192,64,64,.4);
    border-radius:6px;padding:9px 14px;margin:3px 0;direction:rtl;
}}
.rule-card{{
    background:rgba(13,26,42,0.95);
    border-right:4px solid #f0c040;
    border-radius:0 6px 6px 0;
    padding:9px 14px;margin:3px 0;direction:rtl;font-size:14px;
}}
.tl-item{{
    border-right:2px solid #2a3a55;
    padding:8px 16px 8px 0;margin:7px 0;
    position:relative;direction:rtl;
}}
.tl-item::before{{
    content:'';width:10px;height:10px;
    background:#f0c040;border-radius:50%;
    position:absolute;right:-6px;top:12px;
}}
.badge{{
    display:inline-block;
    background:#1a2235;border:1px solid #f0c040;
    color:#f0c040;border-radius:4px;
    padding:2px 8px;font-size:11px;font-weight:600;margin:2px;
}}
.hdr{{
    background:rgba(13,19,32,0.9);
    border:1px solid #1e2a40;
    border-bottom:2px solid #f0c040;
    border-radius:8px;padding:18px 24px;
    margin-bottom:16px;direction:rtl;
    backdrop-filter:blur(10px);
}}
hr{{border-color:#1e2a40!important}}
::-webkit-scrollbar{{width:5px}}
::-webkit-scrollbar-track{{background:rgba(8,12,20,.5)}}
::-webkit-scrollbar-thumb{{background:#2a3a55;border-radius:3px}}
::-webkit-scrollbar-thumb:hover{{background:#f0c040}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# مجلدات التخزين
# ══════════════════════════════════════════════
DATA_DIR     = "fuehrer_data"
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
MEMORY_FILE  = os.path.join(DATA_DIR, "memory.json")
SETTINGS_FILE= os.path.join(DATA_DIR, "settings.json")
LAW_FILE     = os.path.join(DATA_DIR, "law_db.json")

for d in [DATA_DIR, SESSIONS_DIR]:
    os.makedirs(d, exist_ok=True)

# ══════════════════════════════════════════════
# دوال التخزين
# ══════════════════════════════════════════════
def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("save %s: %s", path, e)

def list_sessions():
    sessions = []
    try:
        for fname in sorted(os.listdir(SESSIONS_DIR), reverse=True):
            if fname.endswith(".json"):
                data = load_json(os.path.join(SESSIONS_DIR, fname), {})
                sessions.append({
                    "id":      fname.replace(".json",""),
                    "name":    data.get("name","جلسة"),
                    "count":   len(data.get("messages",[])),
                    "updated": data.get("updated",""),
                })
    except Exception:
        pass
    return sessions

def load_session(sid):
    return load_json(os.path.join(SESSIONS_DIR, f"{sid}.json"),
                     {"name":"جلسة جديدة","messages":[],"updated":""})

def save_session(sid, data):
    data["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_json(os.path.join(SESSIONS_DIR, f"{sid}.json"), data)

def delete_session(sid):
    path = os.path.join(SESSIONS_DIR, f"{sid}.json")
    try:
        if os.path.exists(path): os.remove(path)
    except Exception:
        pass

def new_sid():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# ══════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════
def _init():
    saved = load_json(SETTINGS_FILE, {})
    defs = {
        "memory":       load_json(MEMORY_FILE, []),
        "law_db":       load_json(LAW_FILE, []),
        "docs":         [],
        "pending_q":    "",
        "current_sid":  None,
        "current_msgs": [],
        # إعدادات النموذج
        "ai_provider":  saved.get("ai_provider", "Gemini (Google)"),
        "ai_model":     saved.get("ai_model", "gemini-2.0-flash"),
        "ai_endpoint":  saved.get("ai_endpoint", ""),
        "gemini_key":   saved.get("gemini_key", ""),
        "claude_key":   saved.get("claude_key", ""),
        "groq_key":     saved.get("groq_key", ""),
        "custom_key":   saved.get("custom_key", ""),
        "custom_url":   saved.get("custom_url", ""),
        "case_type":    "قضية عمالية",
    }
    for k,v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

def save_settings():
    save_json(SETTINGS_FILE, {
        "ai_provider": st.session_state.ai_provider,
        "ai_model":    st.session_state.ai_model,
        "gemini_key":  st.session_state.gemini_key,
        "claude_key":  st.session_state.claude_key,
        "groq_key":    st.session_state.groq_key,
        "custom_key":  st.session_state.custom_key,
        "custom_url":  st.session_state.custom_url,
    })

# ══════════════════════════════════════════════
# استخراج النصوص — يدعم كل الأنواع
# ══════════════════════════════════════════════
def get_bytes(f):
    if hasattr(f, "getvalue"): return f.getvalue()
    try:
        p = f.tell(); d = f.read(); f.seek(p); return d
    except Exception:
        return f.read()

def extract_text(f) -> str:
    name = getattr(f, "name", "") or ""
    ext  = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    raw  = get_bytes(f)

    # PDF
    if ext == "pdf":
        parts = []
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                for pg in pdf.pages:
                    t = pg.extract_text() or ""
                    if t.strip(): parts.append(t)
        except Exception:
            try:
                import PyPDF2
                for pg in PyPDF2.PdfReader(io.BytesIO(raw)).pages:
                    t = pg.extract_text() or ""
                    if t.strip(): parts.append(t)
            except Exception:
                pass
        return re.sub(r"\s+", " ", "\n".join(parts)).strip()

    # Word
    if ext == "docx":
        try:
            from docx import Document
            doc = Document(io.BytesIO(raw))
            return re.sub(r"\s+", " ", "\n".join(
                p.text for p in doc.paragraphs if p.text)).strip()
        except Exception:
            return ""

    # نص عادي — يشمل txt, md, rst, log, csv وأي امتداد آخر
    if ext in ("txt","md","rst","log","text","") or True:
        for enc in ["utf-8", "utf-16", "cp1256", "latin-1"]:
            try:
                return re.sub(r"\s+", " ", raw.decode(enc, errors="ignore")).strip()
            except Exception:
                continue

    # JSON
    if ext == "json":
        try:
            obj = json.loads(raw.decode("utf-8", errors="ignore"))
            return re.sub(r"\s+", " ",
                json.dumps(obj, ensure_ascii=False, indent=2)).strip()
        except Exception:
            return ""

    # CSV
    if ext == "csv":
        try:
            import csv
            rows = list(csv.reader(io.StringIO(
                raw.decode("utf-8", errors="ignore"))))
            return re.sub(r"\s+", " ",
                "\n".join(" | ".join(r) for r in rows)).strip()
        except Exception:
            return ""

    # محاولة أخيرة
    try:
        return re.sub(r"\s+", " ",
            raw.decode("utf-8", errors="ignore")).strip()
    except Exception:
        return ""

# ══════════════════════════════════════════════
# استخراج قاعدة بيانات القوانين من أي ملف
# ══════════════════════════════════════════════
def extract_law_records(text: str, source_name: str) -> List[Dict]:
    """استخراج المواد القانونية من نص خام"""
    records = []

    # تنظيف
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"صفحة\s+\d+\s+من\s+\d+", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    # تقسيم على المواد
    blocks = re.split(
        r"(?=المادة\s+(?:الأولى|الثانية|الثالثة|الرابعة|الخامسة|"
        r"السادسة|السابعة|الثامنة|التاسعة|العاشرة|الحادية|"
        r"الثانية عشرة?|الثالثة عشرة?|[\u0600-\u06ff]{3,20}|\d+))",
        text)

    current_law = source_name

    for block in blocks:
        block = block.strip()
        if len(block) < 40: continue

        arabic_count = len(re.findall(r"[\u0600-\u06ff]", block))
        if arabic_count < 20: continue

        # استخراج اسم النظام
        law_match = re.search(
            r"نظام\s+[\u0600-\u06ff\s]{4,35}(?=\s{2,}|المادة|\n)", block)
        if law_match:
            current_law = law_match.group(0).strip()

        # استخراج المادة
        art_match = re.match(
            r"(المادة\s+[\u0600-\u06ff\s\d\(\)]{2,30}?)[\s:،]", block)
        article = art_match.group(1).strip() if art_match else ""

        records.append({
            "article":  article,
            "law_name": current_law,
            "text":     block[:800],
            "source":   source_name,
            "added":    datetime.now().strftime("%Y-%m-%d"),
        })

    return records

# ══════════════════════════════════════════════
# محرك القواعد — 45+ قاعدة
# ══════════════════════════════════════════════
RULES = [
    {"c":"days_abandoned>30","o":"⚠️ انقطاع >30 يوم (ترك العمل)","cat":"عمل"},
    {"c":"days_abandoned>15 and days_abandoned<=30","o":"⚠️ انقطاع 15-30 يوم (إنذار)","cat":"عمل"},
    {"c":"days_since_firing>365","o":"⛔ مضى >سنة (سقط حق التقاضي)","cat":"تقادم"},
    {"c":"days_since_firing>180 and days_since_firing<=365","o":"⏳ مضى >6 أشهر (تقادم جزئي)","cat":"تقادم"},
    {"c":"no_investigation","o":"⚖️ فصل بلا تحقيق (بطلان)","cat":"إجراءات"},
    {"c":"arbitrary_dismissal","o":"⚖️ فصل تعسفي (تعويض)","cat":"عمل"},
    {"c":"salary_delay","o":"⚖️ تأخير الراتب (تعويض)","cat":"عمل"},
    {"c":"eosb_not_paid","o":"⚖️ مكافأة نهاية الخدمة لم تُصرف","cat":"عمل"},
    {"c":"unlawful_deduction","o":"⚖️ خصم غير نظامي (يُرد)","cat":"عمل"},
    {"c":"absence_days>30","o":"⚠️ غياب >30 يوم (فصل)","cat":"غياب"},
    {"c":"absence_days>20 and absence_days<=30","o":"⚠️ غياب 20-30 يوم (إنذار ثانٍ)","cat":"غياب"},
    {"c":"absence_days>15 and absence_days<=20","o":"⚠️ غياب 15-20 يوم (إنذار أول)","cat":"غياب"},
    {"c":"service_length<2","o":"📌 خدمة <2 سنة (نصف شهر/سنة)","cat":"مكافأة"},
    {"c":"service_length>=2 and service_length<5","o":"📌 خدمة 2-5 سنوات (شهر/سنة)","cat":"مكافأة"},
    {"c":"service_length>=5","o":"📌 خدمة ≥5 سنوات (شهر ونصف/سنة)","cat":"مكافأة"},
    {"c":"notification_late","o":"⚖️ تبليغ بعد 7 أيام (إخلال)","cat":"إجراءات"},
    {"c":"violation_date_missing","o":"⚖️ تاريخ المخالفة مجهول (لصالحك)","cat":"إجراءات"},
    {"c":"penalty_after_1_year","o":"⛔ سنة على المخالفة بلا عقوبة (سقط)","cat":"تقادم"},
    {"c":"judgment_without_hearing","o":"⚖️ حكم دون سماعك (بطلان)","cat":"إجراءات"},
    {"c":"no_response_90_days","o":"⚖️ 90 يوم بلا رد (موافقة ضمنية)","cat":"إجراءات"},
    {"c":"doc_unsigned","o":"⚖️ مستند غير موقع (لا حجية)","cat":"مستندات"},
    {"c":"forgery_proven","o":"🚨 تزوير مثبت (جريمة)","cat":"مستندات"},
    {"c":"opponent_hides_doc","o":"⚖️ الخصم يخفي مستنداً (يُحكم ضده)","cat":"مستندات"},
    {"c":"settlement_offer is True and risk_score>60","o":"🤝 الصلح أفضل","cat":"صلح"},
    {"c":"settlement_offer is True and risk_score<=40","o":"⚖️ الصلح ممكن والقضية قوية","cat":"صلح"},
    {"c":"settlement_broken","o":"⚖️ نقض الصلح (تعويض)","cat":"صلح"},
    {"c":"reply_delay>30","o":"⏳ تأخير إداري >30 يوم","cat":"تأخير"},
    {"c":"reply_delay>15 and reply_delay<=30","o":"⏳ تأخير إداري 15-30 يوم","cat":"تأخير"},
    {"c":"ambiguous_count>3","o":"🔍 عبارات غامضة (طعن محتمل)","cat":"لغوي"},
    {"c":"contradictions>1","o":"⚡ تناقض في مراسلات الخصم","cat":"تناقضات"},
    {"c":"force_majeure is True","o":"📌 عذر قاهر مثبت","cat":"أعذار"},
    {"c":"proven_illness","o":"📌 مرض مثبت (عذر مقبول)","cat":"أعذار"},
    {"c":"natural_disaster","o":"📌 كارثة طبيعية (قوة قاهرة)","cat":"أعذار"},
    {"c":"disproportionate_fine","o":"⚖️ غرامة غير متناسبة (تُخفَّض)","cat":"غرامات"},
    {"c":"fine_illegal","o":"⚖️ غرامة مخالفة للنظام (تُلغى)","cat":"غرامات"},
    {"c":"supreme_court_ruling","o":"⭐ سابقة من المحكمة العليا","cat":"سوابق"},
    {"c":"expert_request_denied","o":"⚖️ رفض الخبرة (إخلال بحق الدفاع)","cat":"إجراءات"},
    {"c":"non_judicial_acknowledgment","o":"📌 إقرار غير قضائي (حجة على المُقِر)","cat":"مستندات"},
    {"c":"opponent_threatens","o":"⚖️ تهديد متكرر (تعسف)","cat":"سلوك"},
    {"c":"death_of_relative","o":"📌 وفاة قريب (إجازة رسمية)","cat":"أعذار"},
    {"c":"travel_ban","o":"📌 منع السفر (قوة قاهرة)","cat":"أعذار"},
    {"c":"two_vs_one_witness","o":"📌 شاهدان ضد واحد (مقبول)","cat":"شهادات"},
    {"c":"witnesses_conflict","o":"⚖️ تناقض الشهود","cat":"شهادات"},
    {"c":"new_evidence_late","o":"📌 أدلة جديدة بعد الميعاد (مقبولة)","cat":"مستندات"},
    {"c":"offer_rejected_by_opponent","o":"📌 رفض الخصم الصلح (تعويض لك)","cat":"صلح"},
]

def eval_rule(cond, ctx):
    try:
        for part in [p.strip() for p in cond.split(" and ")]:
            if not part: continue
            m = re.match(r"^(\w+)\s+is\s+(True|False)$", part)
            if m:
                if bool(ctx.get(m[1],False)) != (m[2]=="True"): return False
                continue
            m = re.match(r"^(\w+)$", part)
            if m:
                if not bool(ctx.get(m[1],False)): return False
                continue
            m = re.match(r"^(\w+)\s*(>=|<=|>|<)\s*([0-9.]+)$", part)
            if m:
                lhs=float(ctx.get(m[1],0)); rhs=float(m[3])
                if not {">":lhs>rhs,">=":lhs>=rhs,"<":lhs<rhs,"<=":lhs<=rhs}[m[2]]: return False
                continue
            m = re.match(r"^(\w+)=='([^']*)'$", part.replace(" ",""))
            if m:
                if str(ctx.get(m[1],"")) != m[2]: return False
                continue
            return False
        return True
    except Exception:
        return False

def apply_rules(ctx):
    return [{"text":r["o"],"cat":r["cat"]} for r in RULES if eval_rule(r["c"],ctx)]

# ══════════════════════════════════════════════
# الذاكرة
# ══════════════════════════════════════════════
def mem_add(text, tags=None, cat="عام"):
    m = {
        "id":  hashlib.md5(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()[:8],
        "text":text, "tags":tags or [], "category":cat,
        "ts":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    st.session_state.memory.append(m)
    save_json(MEMORY_FILE, st.session_state.memory)
    return m["id"]

def mem_del(mid):
    st.session_state.memory = [m for m in st.session_state.memory if m["id"] != mid]
    save_json(MEMORY_FILE, st.session_state.memory)

def mem_edit(mid, new_text):
    for m in st.session_state.memory:
        if m["id"] == mid:
            m["text"] = new_text
            m["ts"]   = datetime.now().strftime("%Y-%m-%d %H:%M")
            break
    save_json(MEMORY_FILE, st.session_state.memory)

# ══════════════════════════════════════════════
# الذكاء الاصطناعي — أي نموذج
# ══════════════════════════════════════════════
def build_system(doc_ctx=""):
    mem_txt = ""
    if st.session_state.memory:
        mem_txt = "\n\nالذاكرة:\n" + "\n".join(
            f"- {m['text'][:150]}" for m in st.session_state.memory[-20:])

    law_txt = ""
    if st.session_state.law_db:
        q_words = set()
        for msg in st.session_state.current_msgs[-3:]:
            q_words |= set(re.findall(r"[\u0600-\u06ff]{3,}", msg.get("content","")))
        if q_words:
            scored = sorted(
                [(sum(1 for w in q_words if w in r.get("text","")), r)
                 for r in st.session_state.law_db],
                reverse=True)
            top = [r for sc,r in scored if sc>0][:5]
            if top:
                law_txt = "\n\nمواد قانونية ذات صلة:\n" + "\n".join(
                    f"• [{r['law_name']}] {r['article']}: {r['text'][:300]}"
                    for r in top)

    sys = f"""أنت محامٍ ومستشار قانوني سعودي خبير متخصص في:
- نظام العمل السعودي وقرارات هيئة تسوية النزاعات
- نظام المرافعات الشرعية والإجراءات القضائية
- الأنظمة التجارية والمدنية والجزائية

قواعد الإجابة:
• استند للأنظمة السعودية واذكر المواد بالاسم
• كن محدداً وعملياً لا نظرياً
• أجب بالعربية الفصحى الواضحة
• اقترح خطوات قابلة للتنفيذ{mem_txt}{law_txt}"""

    if doc_ctx:
        sys += f"\n\nالمستندات:\n{doc_ctx[:5000]}"
    return sys

def call_ai(prompt: str, doc_ctx: str = "") -> str:
    p       = st.session_state.ai_provider
    msgs    = st.session_state.current_msgs
    system  = build_system(doc_ctx)

    # ── Gemini ──────────────────────────────────
    if "Gemini" in p:
        key   = st.session_state.gemini_key
        model = st.session_state.ai_model or "gemini-2.0-flash"
        if not key: return "❌ أدخل Gemini API Key"
        contents = [{"role":"user","parts":[{"text":system+"\n\nالسؤال: "+prompt}]}]
        for m in msgs[-40:]:
            role = "user" if m["role"]=="user" else "model"
            contents.append({"role":role,"parts":[{"text":m["content"]}]})
        payload = json.dumps({"contents":contents}).encode()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        req = urllib.request.Request(url, data=payload,
              headers={"Content-Type":"application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read().decode())
                return d["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:300]
            if "quota" in err.lower() or "429" in str(e.code):
                return "❌ استُنفد الحصة اليومية — جرّب Groq أو غيّر الـ Key"
            return f"❌ Gemini {e.code}: {err}"
        except Exception as e:
            return f"❌ {e}"

    # ── Groq ────────────────────────────────────
    elif "Groq" in p:
        key   = st.session_state.groq_key
        model = st.session_state.ai_model or "llama-3.3-70b-versatile"
        if not key: return "❌ أدخل Groq API Key"
        messages = [{"role":"system","content":system}]
        for m in msgs[-40:]:
            messages.append({"role":m["role"],"content":m["content"]})
        messages.append({"role":"user","content":prompt})
        payload = json.dumps({"model":model,"messages":messages,"max_tokens":2048}).encode()
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={"Content-Type":"application/json",
                     "Authorization":f"Bearer {key}"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            return f"❌ Groq {e.code}: {e.read().decode()[:200]}"
        except Exception as e:
            return f"❌ {e}"

    # ── Claude ──────────────────────────────────
    elif "Claude" in p:
        key   = st.session_state.claude_key
        model = st.session_state.ai_model or "claude-sonnet-4-6"
        if not key: return "❌ أدخل Claude API Key"
        messages = []
        for m in msgs[-40:]:
            messages.append({"role":m["role"],"content":m["content"]})
        messages.append({"role":"user","content":prompt})
        payload = json.dumps({
            "model":model,"max_tokens":2048,
            "system":system,"messages":messages}).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"Content-Type":"application/json",
                     "x-api-key":key,
                     "anthropic-version":"2023-06-01"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())["content"][0]["text"]
        except urllib.error.HTTPError as e:
            return f"❌ Claude {e.code}: {e.read().decode()[:200]}"
        except Exception as e:
            return f"❌ {e}"

    # ── OpenAI-Compatible (أي نموذج آخر) ────────
    elif "مخصص" in p or "Custom" in p:
        key = st.session_state.custom_key
        url = st.session_state.custom_url
        model = st.session_state.ai_model
        if not key or not url: return "❌ أدخل الـ URL والـ Key في الإعدادات"
        messages = [{"role":"system","content":system}]
        for m in msgs[-40:]:
            messages.append({"role":m["role"],"content":m["content"]})
        messages.append({"role":"user","content":prompt})
        payload = json.dumps({"model":model,"messages":messages,"max_tokens":2048}).encode()
        req = urllib.request.Request(url, data=payload,
            headers={"Content-Type":"application/json",
                     "Authorization":f"Bearer {key}"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read().decode())
                # يدعم OpenAI format و Anthropic format
                if "choices" in d:
                    return d["choices"][0]["message"]["content"]
                elif "content" in d:
                    return d["content"][0]["text"]
                return str(d)
        except Exception as e:
            return f"❌ {e}"

    return "❌ اختر نموذجاً من الإعدادات"

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚖️ Führer v2.0")
    st.markdown("---")

    # اختيار النموذج
    st.markdown("**🤖 النموذج**")
    provider = st.selectbox("النموذج", [
        "Gemini (Google)",
        "Groq (سريع ومجاني)",
        "Claude (Anthropic)",
        "نموذج مخصص (Custom)",
    ], label_visibility="collapsed")

    if provider != st.session_state.ai_provider:
        st.session_state.ai_provider = provider
        save_settings()

    # اسم النموذج
    model_placeholder = {
        "Gemini (Google)":        "gemini-2.0-flash",
        "Groq (سريع ومجاني)":    "llama-3.3-70b-versatile",
        "Claude (Anthropic)":     "claude-sonnet-4-6",
        "نموذج مخصص (Custom)":   "اكتب اسم النموذج",
    }.get(provider, "")

    model_val = st.text_input("اسم النموذج",
        value=st.session_state.ai_model or model_placeholder,
        placeholder=model_placeholder,
        label_visibility="collapsed")
    if model_val != st.session_state.ai_model:
        st.session_state.ai_model = model_val
        save_settings()

    # مفاتيح API
    if "Gemini" in provider:
        k = st.text_input("Gemini Key", value=st.session_state.gemini_key,
            type="password", label_visibility="collapsed", placeholder="AIza...")
        if k != st.session_state.gemini_key:
            st.session_state.gemini_key = k; save_settings()
        st.markdown("[🔑 Key مجاني](https://aistudio.google.com/apikey)")
        if k: st.success("✅ محفوظ")

    elif "Groq" in provider:
        k = st.text_input("Groq Key", value=st.session_state.groq_key,
            type="password", label_visibility="collapsed", placeholder="gsk_...")
        if k != st.session_state.groq_key:
            st.session_state.groq_key = k; save_settings()
        st.markdown("[🔑 Key مجاني](https://console.groq.com)")
        if k: st.success("✅ محفوظ")

    elif "Claude" in provider:
        k = st.text_input("Claude Key", value=st.session_state.claude_key,
            type="password", label_visibility="collapsed", placeholder="sk-ant-...")
        if k != st.session_state.claude_key:
            st.session_state.claude_key = k; save_settings()
        st.markdown("[🔑 Key](https://console.anthropic.com)")
        if k: st.success("✅ محفوظ")

    elif "مخصص" in provider:
        url = st.text_input("Endpoint URL",
            value=st.session_state.custom_url,
            placeholder="https://api.example.com/v1/chat/completions")
        if url != st.session_state.custom_url:
            st.session_state.custom_url = url; save_settings()
        k = st.text_input("API Key", value=st.session_state.custom_key,
            type="password", placeholder="Bearer token...")
        if k != st.session_state.custom_key:
            st.session_state.custom_key = k; save_settings()
        st.info("يدعم أي API متوافق مع OpenAI")

    st.markdown("---")

    # الجلسات
    st.markdown("**💬 الجلسات**")
    if st.button("➕ جلسة جديدة", use_container_width=True):
        sid = new_sid()
        st.session_state.current_sid  = sid
        st.session_state.current_msgs = []
        save_session(sid, {"name":"جلسة جديدة","messages":[]})
        st.rerun()

    sessions = list_sessions()
    for s in sessions[:12]:
        c1,c2 = st.columns([5,1])
        with c1:
            active = s["id"] == st.session_state.current_sid
            label  = f"{'🟢 ' if active else ''}{s['name'][:18]} ({s['count']})"
            if st.button(label, key=f"s_{s['id']}", use_container_width=True):
                data = load_session(s["id"])
                st.session_state.current_sid  = s["id"]
                st.session_state.current_msgs = data.get("messages",[])
                st.rerun()
        with c2:
            if st.button("🗑", key=f"ds_{s['id']}"):
                delete_session(s["id"])
                if st.session_state.current_sid == s["id"]:
                    st.session_state.current_sid  = None
                    st.session_state.current_msgs = []
                st.rerun()

    st.markdown("---")
    st.markdown("**📋 نوع القضية**")
    ct = st.selectbox("النوع", [
        "قضية عمالية","نزاع تجاري","قضية عقارية",
        "نزاع إداري","قضية جنائية","إفلاس وتصفية",
    ], label_visibility="collapsed")
    st.session_state.case_type = ct

    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1: st.metric("الذاكرة", len(st.session_state.memory))
    with c2: st.metric("الجلسات", len(sessions))
    st.metric("مواد قانونية", len(st.session_state.law_db))

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
st.markdown("""
<div class="hdr">
<h1 style="margin:0;font-size:24px">⚖️ Führer 
<p style="color:#8090a0;margin:4px 0 0;font-size:12px">
سري • دائم • أي نموذج ذكاء • قاعدة قانونية شاملة
</p>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tabs = st.tabs([
    "🤖 المستشار",
    "📂 الملفات",
    "🧠 الذاكرة",
    "📚 القانون",
    "📜 القواعد",
    "📄 التقارير",
    "📅 الجدول",
    "⚙️ الإعدادات",
])
t_ai,t_files,t_mem,t_law,t_rules,t_reports,t_tl,t_settings = tabs

# ──────────────────────────────────────────────
# TAB 1 — المستشار الذكي
# ──────────────────────────────────────────────
with t_ai:
    st.subheader(f"🤖 {st.session_state.ai_provider} — {st.session_state.ai_model}")

    if not st.session_state.current_sid:
        st.markdown("""
<div style="text-align:center;padding:40px;color:#8090a0">
<h2>👈 ابدأ بإنشاء جلسة جديدة من الشريط الجانبي</h2>
<p>كل جلسة محفوظة ولا تُحذف إلا باختيارك</p>
</div>""", unsafe_allow_html=True)
    else:
        sess_data = load_session(st.session_state.current_sid)

        # تسمية الجلسة
        nc1,nc2 = st.columns([4,1])
        with nc1:
            new_name = st.text_input("اسم الجلسة",
                value=sess_data.get("name","جلسة"),
                key="sess_name_inp")
        with nc2:
            if st.button("✏️ حفظ الاسم"):
                sess_data["name"] = new_name
                sess_data["messages"] = st.session_state.current_msgs
                save_session(st.session_state.current_sid, sess_data)
                st.success("✅")

        # طلبات سريعة
        qps = ["حلل وضعي القانوني","ما نقاط قوتي؟",
               "ما المواعيد النظامية؟","اقترح استراتيجية",
               "ما حقوقي في الفصل؟","كيف أتظلم؟"]
        qc  = st.columns(3)
        for i,q in enumerate(qps):
            with qc[i%3]:
                if st.button(q, key=f"qp{i}", use_container_width=True):
                    st.session_state.pending_q = q

        st.markdown("---")

        # عرض المحادثة
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        for msg in st.session_state.current_msgs:
            cls     = "chat-user" if msg["role"]=="user" else "chat-ai"
            ico     = "👤" if msg["role"]=="user" else "⚖️"
            content = msg["content"].replace("\n","<br>")
            ts      = msg.get("ts","")
            st.markdown(
                f'<div class="{cls}">{ico} {content}'
                f'<br><small style="color:#445;font-size:10px">⏱ {ts}</small></div>',
                unsafe_allow_html=True)
        st.markdown('</div><br>', unsafe_allow_html=True)

        # خيارات
        oc1,oc2,oc3 = st.columns(3)
        with oc1: use_docs = st.checkbox("📄 استخدم المستندات", value=True)
        with oc2: use_law  = st.checkbox("📚 استخدم القانون", value=True)
        with oc3: auto_mem = st.checkbox("🧠 حفظ في الذاكرة", value=True)

        user_inp = st.text_area(
            "سؤالك",
            value=st.session_state.pending_q,
            height=100,
            placeholder="مثال: فُصلت من العمل بعد 7 سنوات بدون تحقيق — ما حقوقي؟",
            key="chat_inp",
        )

        sc1,sc2,sc3 = st.columns([3,1,1])
        with sc1: send_btn = st.button("📤 إرسال", use_container_width=True)
        with sc2:
            if st.button("🗑️ مسح الجلسة", use_container_width=True):
                st.session_state.current_msgs = []
                sess_data["messages"] = []
                save_session(st.session_state.current_sid, sess_data)
                st.rerun()
        with sc3:
            if st.session_state.current_msgs:
                chat_exp = "\n\n".join(
                    f"{'أنت' if m['role']=='user' else 'المستشار'} [{m.get('ts','')}]:\n{m['content']}"
                    for m in st.session_state.current_msgs)
                st.download_button("⬇️ تحميل",
                    data=chat_exp.encode("utf-8"),
                    file_name=f"محادثة_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True)

        if send_btn and user_inp.strip():
            st.session_state.pending_q = ""
            doc_ctx = ""
            if use_docs and st.session_state.docs:
                doc_ctx = "\n\n".join(st.session_state.docs[:3])[:5000]
            ts = datetime.now().strftime("%H:%M")
            st.session_state.current_msgs.append(
                {"role":"user","content":user_inp,"ts":ts})
            with st.spinner("⚖️ يحلل..."):
                resp = call_ai(user_inp, doc_ctx=doc_ctx)
            st.session_state.current_msgs.append(
                {"role":"assistant","content":resp,"ts":ts})
            sess_data["messages"] = st.session_state.current_msgs
            save_session(st.session_state.current_sid, sess_data)
            if auto_mem and len(resp)>80 and "❌" not in resp:
                mem_add(f"س: {user_inp[:80]} | ج: {resp[:150]}...",
                       tags=["محادثة", st.session_state.case_type],
                       cat="محادثة")
            st.rerun()

# ──────────────────────────────────────────────
# TAB 2 — الملفات (يقبل أي شيء)
# ──────────────────────────────────────────────
with t_files:
    st.subheader("📂 رفع وتحليل المستندات")
    st.markdown("""
<small style='color:#8090a0'>
يقبل: PDF · DOCX · TXT · MD · JSON · CSV · وأي نص آخر
</small>""", unsafe_allow_html=True)

    # رفع بدون قيود على الامتداد
    uploaded = st.file_uploader(
        "اختر الملفات — أي نوع",
        accept_multiple_files=True,
        type=None,
    )

    if uploaded:
        st.info(f"✅ {len(uploaded)} ملف جاهز")
        if st.button("🔍 استخراج وتحليل الكل", use_container_width=True):
            texts = []
            for f in uploaded:
                with st.expander(f"📄 {f.name}"):
                    with st.spinner("..."):
                        txt = extract_text(f)
                    if txt and len(txt) > 30:
                        texts.append(txt)
                        # كيانات
                        dates   = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", txt)
                        arts    = re.findall(r"المادة\s*[\u0600-\u06FF\d]+", txt)
                        amounts = re.findall(r"[\d,]+\s*(?:ريال|درهم|دولار)", txt)

                        st.text(txt[:600]+("..." if len(txt)>600 else ""))

                        if arts:
                            st.markdown("**المواد:** " + " ".join(
                                f'<span class="badge">{a}</span>'
                                for a in arts[:6]),
                                unsafe_allow_html=True)
                        if dates:
                            st.markdown(f"**تواريخ:** {', '.join(dates[:5])}")
                        if amounts:
                            st.markdown(f"**مبالغ:** {', '.join(amounts[:5])}")
                    else:
                        st.warning("⚠️ لم يُستخرج نص كافٍ")

            st.session_state.docs = texts
            st.success(f"✅ {len(texts)} ملف | {sum(len(t) for t in texts):,} حرف")

# ──────────────────────────────────────────────
# TAB 3 — الذاكرة
# ──────────────────────────────────────────────
with t_mem:
    st.subheader("🧠 الذاكرة الدائمة")
    st.markdown("تُحفظ تلقائياً ولا تُمسح إلا باختيارك")

    # إضافة يدوية
    with st.expander("➕ إضافة ذاكرة يدوياً"):
        mt    = st.text_area("النص", height=100,
                             placeholder="مثال: الموكل يعمل منذ 2019 براتب 12,000 ريال")
        mcat  = st.selectbox("الفئة",
                ["قضية","موكل","حكم","ملاحظة","استراتيجية","قانون","عام"])
        mtags = st.text_input("وسوم (افصل بفاصلة)")
        if st.button("💾 حفظ في الذاكرة"):
            if mt.strip():
                tags = [x.strip() for x in mtags.split(",") if x.strip()]
                mid  = mem_add(mt, tags, mcat)
                st.success(f"✅ محفوظ (ID: {mid})")
                st.rerun()

    # إضافة من ملف
    with st.expander("📁 إضافة للذاكرة من ملف"):
        mf_up = st.file_uploader("ارفع ملفاً لإضافته للذاكرة",
                                  accept_multiple_files=True,
                                  key="mem_file_up",
                                  type=None)
        mf_cat = st.selectbox("فئة الملف",
                ["قانون","قضية","وثيقة","مرجع","عام"], key="mf_cat")
        if mf_up and st.button("📥 استخراج وحفظ في الذاكرة"):
            for f in mf_up:
                txt = extract_text(f)
                if txt and len(txt) > 30:
                    # تقسيم لقطع مناسبة
                    chunks = [txt[i:i+500] for i in range(0, min(len(txt),5000), 500)]
                    for i,ch in enumerate(chunks):
                        mem_add(ch, tags=[f.name, mf_cat], cat=mf_cat)
                    st.success(f"✅ {f.name} — {len(chunks)} قطعة محفوظة")
                else:
                    st.warning(f"⚠️ {f.name} — لم يُستخرج نص")
            st.rerun()

    st.markdown("---")

    # بحث وعرض
    mq = st.text_input("🔍 بحث في الذاكرة")
    q  = mq.lower()
    mems = [m for m in st.session_state.memory
            if not mq
            or q in m["text"].lower()
            or any(q in t.lower() for t in m.get("tags",[]))]

    st.markdown(f"**{len(mems)} ذاكرة**")
    for m in reversed(mems):
        ec1,ec2,ec3 = st.columns([8,1,1])
        with ec1:
            badges = "".join(
                f'<span class="badge">{t}</span>'
                for t in m.get("tags",[]))
            st.markdown(
                f'<div class="mem-card">'
                f'<small style="color:#8090a0">'
                f'{m.get("ts","")} · {m.get("category","")}</small>'
                f'<br>{m["text"][:200]}<br>{badges}</div>',
                unsafe_allow_html=True)
        with ec2:
            if st.button("✏️", key=f"e_{m['id']}"):
                st.session_state[f"edit_{m['id']}"] = True
        with ec3:
            if st.button("🗑", key=f"d_{m['id']}"):
                mem_del(m["id"]); st.rerun()
        if st.session_state.get(f"edit_{m['id']}"):
            nt = st.text_area("تعديل", value=m["text"],
                               key=f"et_{m['id']}", height=100)
            if st.button("✅ حفظ", key=f"sv_{m['id']}"):
                mem_edit(m["id"], nt)
                del st.session_state[f"edit_{m['id']}"]
                st.rerun()

    st.markdown("---")
    ex1,ex2 = st.columns(2)
    with ex1:
        if st.button("📤 تصدير الذاكرة"):
            d = json.dumps(st.session_state.memory,
                          ensure_ascii=False, indent=2)
            st.download_button("⬇️ JSON", d.encode("utf-8"),
                "memory.json", "application/json")
    with ex2:
        imp_f = st.file_uploader("📥 استيراد ذاكرة JSON",
                                  type=["json"], key="mem_imp")
        if imp_f:
            try:
                imported = json.loads(imp_f.read())
                existing = {m["id"] for m in st.session_state.memory}
                new_ones = [m for m in imported
                           if m.get("id") not in existing]
                st.session_state.memory.extend(new_ones)
                save_json(MEMORY_FILE, st.session_state.memory)
                st.success(f"✅ {len(new_ones)} ذاكرة مستوردة")
            except Exception as e:
                st.error(f"❌ {e}")

# ──────────────────────────────────────────────
# TAB 4 — قاعدة القانون
# ──────────────────────────────────────────────
with t_law:
    st.subheader("📚 قاعدة الأنظمة السعودية")

    lc1,lc2 = st.columns(2)

    with lc1:
        st.markdown("**📁 تحميل من ملف (أي نوع)**")
        st.markdown("""
<small style='color:#8090a0'>
TXT · PDF · DOCX · MD · JSON · CSV<br>
يستخرج المواد تلقائياً ويفهرسها
</small>""", unsafe_allow_html=True)
        law_files = st.file_uploader(
            "ارفع ملف قانون",
            accept_multiple_files=True,
            key="law_up",
            type=None,
        )
        if law_files and st.button("📥 استخراج وإضافة للقاعدة",
                                    use_container_width=True):
            total_added = 0
            for f in law_files:
                with st.spinner(f"جاري معالجة {f.name}..."):
                    txt = extract_text(f)
                if txt and len(txt) > 50:
                    records = extract_law_records(txt, f.name)
                    st.session_state.law_db.extend(records)
                    total_added += len(records)
                    st.success(f"✅ {f.name} — {len(records)} مادة")
                else:
                    st.warning(f"⚠️ {f.name} — لم يُستخرج نص")
            save_json(LAW_FILE, st.session_state.law_db)
            st.success(f"✅ المجموع: {total_added} مادة جديدة")

    with lc2:
        st.markdown("**➕ إضافة مادة يدوياً**")
        ma_text = st.text_area("نص المادة", height=100, key="ma_t")
        ma_art  = st.text_input("اسم/رقم المادة", key="ma_a",
                                 placeholder="المادة الأولى")
        ma_law  = st.text_input("اسم النظام", key="ma_l",
                                 placeholder="نظام العمل")
        if st.button("➕ إضافة للقاعدة"):
            if ma_text.strip():
                rec = {
                    "text":     ma_text,
                    "article":  ma_art,
                    "law_name": ma_law or "نظام يدوي",
                    "source":   "يدوي",
                    "added":    datetime.now().strftime("%Y-%m-%d"),
                }
                st.session_state.law_db.append(rec)
                save_json(LAW_FILE, st.session_state.law_db)
                st.success("✅ تمت الإضافة")

    st.markdown("---")

    if st.session_state.law_db:
        lm1,lm2,lm3 = st.columns(3)
        with lm1: st.metric("إجمالي المواد", len(st.session_state.law_db))
        with lm2:
            n_laws = len(set(r.get("law_name","") for r in st.session_state.law_db))
            st.metric("الأنظمة", n_laws)
        with lm3:
            n_art = sum(1 for r in st.session_state.law_db if r.get("article"))
            st.metric("مواد محددة", n_art)

        law_q = st.text_input("🔍 ابحث في الأنظمة",
                               placeholder="مثال: مكافأة نهاية الخدمة")
        if law_q:
            q_words = set(re.findall(r"[\u0600-\u06FF]{3,}", law_q))
            scored  = sorted(
                [(sum(1 for w in q_words
                      if w in r.get("text","") or w in r.get("article","")),r)
                 for r in st.session_state.law_db],
                reverse=True)
            results = [(sc,r) for sc,r in scored if sc>0][:10]

            if results:
                st.markdown(f"**{len(results)} نتيجة:**")
                for sc,r in results:
                    with st.expander(
                        f"📜 {r.get('article','مادة')} — "
                        f"{r.get('law_name','')} (تطابق: {sc})"):
                        st.write(r["text"])
                        if st.button("💾 حفظ في الذاكرة",
                                     key=f"ls_{abs(hash(r['text']))%999999}"):
                            mem_add(
                                f"[{r.get('law_name','')}] "
                                f"{r.get('article','')}: {r['text'][:250]}",
                                tags=["قانون", r.get("law_name","")],
                                cat="قانون")
                            st.success("✅")
            else:
                st.info(f"لا نتائج لـ '{law_q}'")

        # تصدير/حذف
        ec1,ec2 = st.columns(2)
        with ec1:
            if st.button("📤 تصدير القاعدة JSON"):
                d = json.dumps(st.session_state.law_db,
                               ensure_ascii=False, indent=2)
                st.download_button("⬇️ تحميل",
                    d.encode("utf-8"), "law_db.json", "application/json")
        with ec2:
            if st.button("🗑️ مسح القاعدة كاملاً"):
                st.session_state.law_db = []
                save_json(LAW_FILE, [])
                st.success("✅ تم المسح")
                st.rerun()
    else:
        st.info("💡 ارفع ملفات الأنظمة أعلاه لبناء قاعدة البيانات")

# ──────────────────────────────────────────────
# TAB 5 — القواعد
# ──────────────────────────────────────────────
with t_rules:
    st.subheader(f"📜 محرك القواعد — {len(RULES)} قاعدة")
    with st.expander("⚙️ بيانات القضية", expanded=True):
        rc1,rc2,rc3 = st.columns(3)
        with rc1:
            d_aban  = st.number_input("أيام الانقطاع",0,3000,0)
            d_fire  = st.number_input("أيام منذ الفصل",0,3000,0)
            d_reply = st.number_input("تأخر رد الخصم",0,365,0)
            d_abs   = st.number_input("أيام الغياب",0,365,0)
        with rc2:
            svc    = st.number_input("سنوات الخدمة",0.0,50.0,0.0,0.5)
            rscore = st.number_input("درجة الخطر (0-100)",0,100,50)
        with rc3:
            no_inv  = st.checkbox("فصل بلا تحقيق")
            arb_dis = st.checkbox("فصل تعسفي")
            fm      = st.checkbox("عذر قاهر")
            settl   = st.checkbox("عرض صلح")
            sal_del = st.checkbox("تأخير الراتب")
            eosb    = st.checkbox("مكافأة لم تُصرف")
            ill     = st.checkbox("مرض مثبت")
            no_resp = st.checkbox("90 يوم بلا رد")
            ded     = st.checkbox("خصم غير نظامي")
            forgery = st.checkbox("تزوير مثبت")

    if st.button("🔍 تطبيق القواعد", use_container_width=True):
        # تلقائي من المستندات
        contras = 0
        ambig   = 0
        for t in st.session_state.docs:
            dates = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", t or "")
            if len(dates)>=2 and dates[0]==dates[1]: contras += 1
            ambig += len([p for p in
                ["يحق للجهة","ما تراه مناسباً","تقدير الجهة"] if p in t])

        ctx = {
            "days_abandoned":d_aban, "days_since_firing":d_fire,
            "reply_delay":d_reply,   "absence_days":d_abs,
            "service_length":svc,    "risk_score":rscore,
            "no_investigation":no_inv, "arbitrary_dismissal":arb_dis,
            "force_majeure":fm,      "settlement_offer":settl,
            "salary_delay":sal_del,  "eosb_not_paid":eosb,
            "proven_illness":ill,    "no_response_90_days":no_resp,
            "unlawful_deduction":ded,"forgery_proven":forgery,
            "contradictions":contras,"ambiguous_count":ambig,
        }
        alerts = apply_rules(ctx)
        if alerts:
            cats = {}
            for a in alerts: cats.setdefault(a["cat"],[]).append(a["text"])
            st.markdown(f"**{len(alerts)} تنبيه:**")
            for cat,items in cats.items():
                st.markdown(f"**{cat}**")
                for item in items:
                    st.markdown(f'<div class="rule-card">{item}</div>',
                               unsafe_allow_html=True)
        else:
            st.success("✅ لا تنبيهات")

# ──────────────────────────────────────────────
# TAB 6 — التقارير
# ──────────────────────────────────────────────
with t_reports:
    st.subheader("📄 التقارير واللوائح")
    rp1,rp2 = st.columns(2)

    with rp1:
        st.markdown("### 📊 تقرير شامل")
        if st.button("🖨️ إنشاء التقرير", use_container_width=True):
            sessions_count = len(list_sessions())
            report = f"""تقرير قانوني — {datetime.now().strftime('%d/%m/%Y %H:%M')}
نوع القضية: {st.session_state.case_type}
النموذج: {st.session_state.ai_provider}
{'='*40}

الجلسات المحفوظة: {sessions_count}
الذاكرة: {len(st.session_state.memory)} سجل
المواد القانونية: {len(st.session_state.law_db)} مادة
المستندات المحللة: {len(st.session_state.docs)} ملف

رسائل الجلسة الحالية: {len(st.session_state.current_msgs)}

ملخص الذاكرة:
""" + "\n".join(f"• [{m['category']}] {m['text'][:100]}"
                for m in st.session_state.memory[-10:])

            st.text_area("التقرير", report, height=300)
            st.download_button("⬇️ تحميل",
                data=report.encode("utf-8"),
                file_name=f"تقرير_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain")

    with rp2:
        st.markdown("### ✍️ مسودة اللائحة")
        tmpl    = st.selectbox("النوع",
                    ["مذكرة دفاع","صحيفة دعوى",
                     "عريضة اعتراض","إنذار رسمي"])
        court_n = st.text_input("المحكمة","محكمة العمل")
        case_n  = st.text_input("رقم القضية","___/___/____")
        client_n= st.text_input("الموكل","")
        oppon_n = st.text_input("الخصم","")
        facts_n = st.text_area("الوقائع","",height=100)
        reqs_n  = st.text_area("الطلبات",
                    "إلغاء القرار والتعويض عن الأضرار",height=100)

        if st.button("✍️ إنشاء المسودة", use_container_width=True):
            date_now = datetime.now().strftime("%d/%m/%Y")
            drafts = {
"مذكرة دفاع":f"""بسم الله الرحمن الرحيم
السيد/ رئيس {court_n} المحترم
الموضوع: مذكرة دفاع — الدعوى رقم ({case_n})
المقدم من: {client_n}  ضد: {oppon_n}

أولاً — الوقائع:
{facts_n}

ثانياً — الطلبات:
{reqs_n}

المقدم: {client_n}   التاريخ: {date_now}""",

"صحيفة دعوى":f"""بسم الله الرحمن الرحيم
السيد/ رئيس {court_n} المحترم
المدعي: {client_n}   المدعى عليه: {oppon_n}
الوقائع: {facts_n}
الطلبات: {reqs_n}
التاريخ: {date_now}""",

"عريضة اعتراض":f"""بسم الله الرحمن الرحيم
المقام الكريم/ رئيس {court_n}
الموضوع: اعتراض على القرار رقم ({case_n})
مقدم من: {client_n}
أسباب الاعتراض: {facts_n}
الطلبات: {reqs_n}
التاريخ: {date_now}""",

"إنذار رسمي":f"""بسم الله الرحمن الرحيم
إلى: {oppon_n}   من: {client_n}   التاريخ: {date_now}
الموضوع: إنذار رسمي
أُنذركم رسمياً بشأن: {facts_n}
في حال عدم الاستجابة خلال 15 يوماً ستُتَّخذ كافة الإجراءات النظامية.
{reqs_n}""",
            }
            draft = drafts.get(tmpl,"")
            st.text_area("المسودة", draft, height=400)
            st.download_button("⬇️ تحميل المسودة",
                data=draft.encode("utf-8"),
                file_name=f"مسودة_{tmpl}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain")

# ──────────────────────────────────────────────
# TAB 7 — الجدول الزمني
# ──────────────────────────────────────────────
with t_tl:
    st.subheader("📅 الجدول الزمني")
    if not st.session_state.docs:
        st.info("⚠️ ارفع الملفات من تبويب 'الملفات' أولاً")
    else:
        evs = []
        for txt in st.session_state.docs:
            for d in re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", txt or ""):
                for fmt in ["%d/%m/%Y","%d/%m/%y"]:
                    try:
                        dt = datetime.strptime(d,fmt)
                        evs.append({"date":dt,"text":txt[:200]})
                        break
                    except ValueError:
                        pass
        evs.sort(key=lambda x: x["date"])

        gaps = []
        for i in range(len(evs)-1):
            diff = (evs[i+1]["date"]-evs[i]["date"]).days
            if diff > 30:
                gaps.append({"from":evs[i]["date"].strftime("%d/%m/%Y"),
                             "to":evs[i+1]["date"].strftime("%d/%m/%Y"),
                             "days":diff})

        m1,m2 = st.columns(2)
        with m1: st.metric("الأحداث",len(evs))
        with m2: st.metric("الفجوات",len(gaps))

        for ev in evs:
            st.markdown(
                f'<div class="tl-item">'
                f'<strong>{ev["date"].strftime("%d/%m/%Y")}</strong>'
                f'<br><span style="color:#a0b0c0;font-size:13px">'
                f'{ev["text"][:120]}...</span></div>',
                unsafe_allow_html=True)

        if gaps:
            st.markdown("### ⚠️ الفجوات")
            for g in gaps:
                st.error(f"⏰ {g['days']} يوم — من {g['from']} إلى {g['to']}")

# ──────────────────────────────────────────────
# TAB 8 — الإعدادات
# ──────────────────────────────────────────────
with t_settings:
    st.subheader("⚙️ الإعدادات")

    st.markdown("### 🎨 الخلفية")
    bg_file = st.file_uploader("ارفع صورة خلفية",
                                type=["png","jpg","jpeg","webp"],
                                key="bg_up")
    if bg_file:
        raw_bg = bg_file.read()
        with open("bg.png","wb") as f: f.write(raw_bg)
        st.success("✅ الخلفية محفوظة — أعد تشغيل التطبيق لتطبيقها")
        b64 = base64.b64encode(raw_bg).decode()
        st.markdown(
            f'<img src="data:image/png;base64,{b64}" '
            f'style="width:100%;border-radius:8px;margin-top:8px">',
            unsafe_allow_html=True)

    if os.path.exists("bg.png"):
        if st.button("🗑️ إزالة الخلفية"):
            os.remove("bg.png")
            st.success("✅ تمت الإزالة — أعد التشغيل")

    st.markdown("---")
    st.markdown("### 📊 إحصائيات التخزين")
    total_size = 0
    for root, dirs, files in os.walk(DATA_DIR):
        for fname in files:
            fp = os.path.join(root, fname)
            total_size += os.path.getsize(fp)

    st.info(f"""
- الجلسات: {len(list_sessions())} جلسة
- الذاكرة: {len(st.session_state.memory)} سجل
- القانون: {len(st.session_state.law_db)} مادة
- حجم البيانات: {total_size/1024:.1f} KB
""")

    st.markdown("---")
    st.markdown("### 🗑️ إدارة البيانات")
    dc1,dc2 = st.columns(2)
    with dc1:
        if st.button("🗑️ مسح كل الجلسات", use_container_width=True):
            for s in list_sessions():
                delete_session(s["id"])
            st.session_state.current_sid  = None
            st.session_state.current_msgs = []
            st.success("✅ تم مسح الجلسات")
            st.rerun()
    with dc2:
        if st.button("🗑️ مسح الذاكرة كاملاً", use_container_width=True):
            st.session_state.memory = []
            save_json(MEMORY_FILE, [])
            st.success("✅ تم مسح الذاكرة")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📤 نسخة احتياطية كاملة")
    if st.button("📦 تصدير كل شيء"):
        backup = {
            "memory":      st.session_state.memory,
            "law_db":      st.session_state.law_db,
            "case_type":   st.session_state.case_type,
            "ai_provider": st.session_state.ai_provider,
            "ai_model":    st.session_state.ai_model,
            "exported_at": datetime.now().isoformat(),
            "version":     "2.0",
        }
        d = json.dumps(backup, ensure_ascii=False, indent=2)
        st.download_button("⬇️ تحميل النسخة الاحتياطية",
            d.encode("utf-8"),
            f"fuehrer_backup_{datetime.now().strftime('%Y%m%d')}.json",
            "application/json")

# Footer
st.markdown(
    '<hr><p style="text-align:center;color:#303848;font-size:11px">'
    'Führer v2.0 | سري • دائم • أي نموذج | '
    'Gemini · Claude · Groq · Custom</p>',
    unsafe_allow_html=True)
PYEOF
echo "Lines: $(wc -l < /mnt/user-data/outputs/fuehrer_v2.py)"
