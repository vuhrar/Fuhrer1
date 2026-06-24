cat > /mnt/user-data/outputs/fuehrer_v2.py << 'PYEOF'
"""
Führer 
"""

import streamlit as st
import re, io, os, json, logging, hashlib, struct
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import urllib.request, urllib.error

logger = logging.getLogger("fuehrer_v2")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="⚖️ Führer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
*{box-sizing:border-box}
.stApp{background:#080c14;color:#e8e0d0;font-family:'Cairo',sans-serif;direction:rtl}
[data-testid="stSidebar"]{background:#0d1320!important;border-left:1px solid #1e2a40}
[data-testid="stSidebar"] *{color:#c8c0b0!important}
h1,h2,h3{color:#f0c040!important;font-weight:700}
.stTabs [data-baseweb="tab-list"]{background:#0d1320;border-bottom:2px solid #1e2a40;gap:3px;padding:4px;border-radius:8px 8px 0 0}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#8090a0!important;border:1px solid transparent!important;border-radius:6px!important;padding:7px 14px!important;font-size:13px;font-family:'Cairo',sans-serif}
.stTabs [data-baseweb="tab"][aria-selected="true"]{background:#1a2235!important;color:#f0c040!important;border-color:#f0c040!important;font-weight:700}
.stTabs [data-baseweb="tab-panel"]{background:#0a0f1a;border:1px solid #1e2a40;border-radius:0 0 8px 8px;padding:18px}
.stTextInput>div>div>input,.stTextArea textarea{background:#0d1320!important;color:#e8e0d0!important;border:1px solid #2a3a55!important;border-radius:6px!important;font-family:'Cairo',sans-serif!important}
.stButton>button{background:linear-gradient(135deg,#c8a020,#f0c040)!important;color:#0a0f1a!important;border:none!important;border-radius:6px!important;font-weight:700!important;font-family:'Cairo',sans-serif!important;padding:10px 18px!important}
[data-testid="stMetric"]{background:#0d1320;border:1px solid #1e2a40;border-radius:8px;padding:12px 16px}
[data-testid="stMetricLabel"]{color:#8090a0!important;font-size:12px}
[data-testid="stMetricValue"]{color:#f0c040!important;font-weight:700;font-size:22px}
.stSelectbox [data-baseweb="select"]>div{background:#0d1320!important;border-color:#2a3a55!important;color:#e8e0d0!important}
.chat-user{background:#1a2235;border:1px solid #2a3a55;border-radius:12px 12px 2px 12px;padding:12px 16px;margin:8px 0;max-width:82%;float:right;clear:both;direction:rtl}
.chat-ai{background:#0d1a2a;border:1px solid #1e3a50;border-radius:12px 12px 12px 2px;padding:12px 16px;margin:8px 0;max-width:88%;float:left;clear:both;direction:rtl;border-left:3px solid #f0c040}
.chat-wrap{overflow:hidden;min-height:60px}
.mem-card{background:#0d1320;border:1px solid #1e2a40;border-radius:8px;padding:12px;margin:5px 0;direction:rtl}
.ok-card{background:rgba(40,100,60,.15);border:1px solid rgba(64,192,96,.3);border-radius:6px;padding:9px 14px;margin:3px 0;direction:rtl}
.bad-card{background:rgba(100,30,30,.15);border:1px solid rgba(192,64,64,.3);border-radius:6px;padding:9px 14px;margin:3px 0;direction:rtl}
.rule-card{background:#0d1a2a;border-right:4px solid #f0c040;border-radius:0 6px 6px 0;padding:9px 14px;margin:3px 0;direction:rtl;font-size:14px}
.tl-item{border-right:2px solid #2a3a55;padding:8px 16px 8px 0;margin:7px 0;position:relative;direction:rtl}
.tl-item::before{content:'';width:10px;height:10px;background:#f0c040;border-radius:50%;position:absolute;right:-6px;top:12px}
.tl-gap{border-right-color:#c04040;background:rgba(192,64,64,.05)}
.badge{display:inline-block;background:#1a2235;border:1px solid #f0c040;color:#f0c040;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600;margin:2px}
.hdr{background:linear-gradient(135deg,#0d1320,#1a2235);border:1px solid #1e2a40;border-bottom:2px solid #f0c040;border-radius:8px;padding:18px 24px;margin-bottom:16px;direction:rtl}
hr{border-color:#1e2a40!important}
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:#080c14}
::-webkit-scrollbar-thumb{background:#2a3a55;border-radius:3px}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════
def _init():
    defs = {
        "memory": [],
        "chat": [],
        "docs": [],
        "law_db": [],
        "api_key": "",
        "ai_provider": "Claude (Anthropic)",
        "gemini_key": "",
        "groq_key": "",
        "embedder": None,
        "collection": None,
        "case_ctx": {"type": "قضية عمالية"},
        "pending_q": "",
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

MEMORY_FILE = "fuehrer_memory.json"

def _load_mem():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def _save_mem():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("mem save: %s", e)

if not st.session_state.memory:
    st.session_state.memory = _load_mem()

# ══════════════════════════════════════════════
# PARQUET DECODER — pure Python
# ══════════════════════════════════════════════
def decode_parquet_arabic(raw: bytes) -> List[Dict]:
    results = []
    i = 0
    buf = bytearray()
    while i < len(raw):
        b = raw[i]
        if b in (0xD8, 0xD9, 0xDA, 0xDB) and i + 1 < len(raw):
            b2 = raw[i + 1]
            if 0x80 <= b2 <= 0xBF:
                buf.extend([b, b2])
                i += 2
                continue
        elif buf and b in (0x20, 0x0A, 0x2C, 0x2E, 0x3A, 0x2D, 0x28, 0x29) or (buf and 0x30 <= b <= 0x39):
            buf.append(b)
            i += 1
            continue
        if len(buf) >= 14:
            try:
                text = buf.decode("utf-8", errors="ignore").strip()
                if sum(1 for c in text if "\u0600" <= c <= "\u06FF") >= 8:
                    results.append(text)
            except Exception:
                pass
        buf = bytearray()
        i += 1

    records = []
    for i, s in enumerate(results):
        article = re.search(r"المادة[^\n:]{3,40}", s)
        law = re.search(r"نظام[^\n]{4,50}", s)
        records.append({
            "text": s,
            "article": article.group(0).strip() if article else "",
            "law_name": law.group(0).strip() if law else "الأنظمة السعودية",
            "source": "parquet",
        })
    return records

# ══════════════════════════════════════════════
# DOCUMENT INTELLIGENCE
# ══════════════════════════════════════════════
def _norm(t):
    return re.sub(r"\s+", " ", t or "").strip()

def _bytes(f):
    if hasattr(f, "getvalue"):
        return f.getvalue()
    try:
        p = f.tell(); d = f.read(); f.seek(p); return d
    except Exception:
        return f.read()

class DocIntel:
    def extract(self, f) -> str:
        ext = (getattr(f, "name", "") or "").rsplit(".", 1)[-1].lower()
        raw = _bytes(f)
        try:
            if ext == "pdf":        return self._pdf(raw)
            if ext == "docx":       return self._docx(raw)
            if ext in ("txt","md"): return _norm(raw.decode("utf-8", errors="ignore"))
            if ext == "parquet":    return self._parquet(raw)
            if ext == "json":
                return _norm(json.dumps(json.loads(raw.decode("utf-8", errors="ignore")), ensure_ascii=False))
            if ext == "csv":
                import csv
                rows = list(csv.reader(io.StringIO(raw.decode("utf-8", errors="ignore"))))
                return _norm("\n".join(" | ".join(r) for r in rows))
            return _norm(raw.decode("utf-8", errors="ignore"))
        except Exception as e:
            return ""

    def _pdf(self, raw):
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
        return _norm("\n".join(parts))

    def _docx(self, raw):
        try:
            from docx import Document
            doc = Document(io.BytesIO(raw))
            return _norm("\n".join(p.text for p in doc.paragraphs if p.text))
        except Exception:
            return ""

    def _parquet(self, raw):
        records = decode_parquet_arabic(raw)
        if not records: return ""
        return _norm("\n\n".join(f"[{r['law_name']}] {r['article']}: {r['text']}" for r in records))

    def dates(self, t):
        out = []
        for p in [r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})"]:
            for m in re.findall(p, t or ""):
                out.append(f"{m[0]}/{m[1]}/{m[2]}")
        return out

    def articles(self, t):
        return re.findall(r"المادة\s*[\u0600-\u06FF\d]+", t or "")

    def ambiguous(self, t):
        return [p for p in ["يحق للجهة","ما تراه مناسباً","تقدير الجهة","سيتم الرد لاحقاً"] if p in (t or "")]

    def claims(self, t):
        return [p for p in [r"ثبت لدينا",r"نستدل من",r"بناءً على ما ورد"] if re.search(p, t or "")]

    def entities(self, t):
        return {
            "parties": list(set(re.findall(r"(?:المدعي|المدعى عليه|الشركة|المؤسسة|الموظف|الهيئة)", t or ""))),
            "amounts": re.findall(r"[\d,]+\s*(?:ريال|درهم|دولار)", t or ""),
            "articles": self.articles(t),
            "dates": self.dates(t),
        }

# ══════════════════════════════════════════════
# TIMELINE
# ══════════════════════════════════════════════
class Timeline:
    def build(self, texts):
        evs, di = [], DocIntel()
        for idx, txt in enumerate(texts):
            for d in di.dates(txt):
                for fmt in ["%d/%m/%Y","%d/%m/%y","%Y/%m/%d"]:
                    try:
                        dt = datetime.strptime(d, fmt)
                        evs.append({"date":dt,"text":(txt or "")[:200],"fi":idx})
                        break
                    except ValueError:
                        pass
        evs.sort(key=lambda x: x["date"])
        return evs

    def gaps(self, evs):
        out = []
        for i in range(len(evs)-1):
            diff = (evs[i+1]["date"]-evs[i]["date"]).days
            if diff > 30:
                out.append({"from":evs[i]["date"].strftime("%d/%m/%Y"),
                            "to":evs[i+1]["date"].strftime("%d/%m/%Y"),
                            "days":diff,
                            "sev":"high" if diff>90 else "med" if diff>60 else "low"})
        return out

    def deadlines(self, evs):
        out = []
        for ev in evs:
            t, dt = ev.get("text",""), ev.get("date")
            if not isinstance(dt, datetime): continue
            if any(k in t for k in ["فصل","إنهاء","إيقاف"]):
                out.append({"ev":t[:50],"dl":(dt+timedelta(365)).strftime("%d/%m/%Y"),"type":"تقادم"})
            if "اعتراض" in t:
                out.append({"ev":t[:50],"dl":(dt+timedelta(30)).strftime("%d/%m/%Y"),"type":"اعتراض"})
            if "استئناف" in t:
                out.append({"ev":t[:50],"dl":(dt+timedelta(60)).strftime("%d/%m/%Y"),"type":"استئناف"})
        return out

# ══════════════════════════════════════════════
# RULE ENGINE — 90+ قاعدة
# ══════════════════════════════════════════════
class RuleEngine:
    RULES = [
        {"c":"days_abandoned>30","o":"⚠️ الانقطاع تجاوز 30 يوماً (ترك العمل)","cat":"عمل"},
        {"c":"days_abandoned>15 and days_abandoned<=30","o":"⚠️ انقطاع 15-30 يوماً (إنذار)","cat":"عمل"},
        {"c":"days_since_firing>365","o":"⛔ مضى أكثر من سنة على الفصل (سقط حق التقاضي)","cat":"تقادم"},
        {"c":"days_since_firing>180 and days_since_firing<=365","o":"⏳ مضى أكثر من 6 أشهر (تقادم جزئي)","cat":"تقادم"},
        {"c":"no_investigation","o":"⚖️ فصل بلا تحقيق (بطلان القرار)","cat":"إجراءات"},
        {"c":"arbitrary_dismissal","o":"⚖️ فصل تعسفي (يستحق تعويضاً)","cat":"عمل"},
        {"c":"violation_not_proven","o":"⚖️ لم تثبت المخالفة (يُلغى الفصل)","cat":"عمل"},
        {"c":"salary_delay","o":"⚖️ تأخير الراتب (تستحق تعويضاً)","cat":"عمل"},
        {"c":"eosb_not_paid","o":"⚖️ مكافأة نهاية الخدمة لم تُصرف","cat":"عمل"},
        {"c":"unlawful_deduction","o":"⚖️ خصم من الراتب بغير حق","cat":"عمل"},
        {"c":"absence_days>30","o":"⚠️ غياب أكثر من 30 يوماً (فصل)","cat":"غياب"},
        {"c":"absence_days>20 and absence_days<=30","o":"⚠️ غياب 20-30 يوماً (إنذار ثانٍ)","cat":"غياب"},
        {"c":"absence_days>15 and absence_days<=20","o":"⚠️ غياب 15-20 يوماً (إنذار أول)","cat":"غياب"},
        {"c":"service_length<2","o":"📌 خدمة أقل من سنتين (مكافأة نصف شهر/سنة)","cat":"مكافأة"},
        {"c":"service_length>=2 and service_length<5","o":"📌 خدمة 2-5 سنوات (شهر/سنة)","cat":"مكافأة"},
        {"c":"service_length>=5","o":"📌 خدمة أكثر من 5 سنوات (شهر ونصف/سنة)","cat":"مكافأة"},
        {"c":"notification_late","o":"⚖️ تبليغ بعد 7 أيام (إخلال إجرائي)","cat":"إجراءات"},
        {"c":"no_registered_letter","o":"⚖️ تبليغ بغير بريد مسجل","cat":"إجراءات"},
        {"c":"violation_date_missing","o":"⚖️ تاريخ المخالفة غير محدد (غموض لصالحك)","cat":"إجراءات"},
        {"c":"penalty_after_1_year","o":"⛔ مضى سنة على المخالفة بلا عقوبة (سقط الحق)","cat":"تقادم"},
        {"c":"judgment_without_hearing","o":"⚖️ حكم دون سماع أقوالك (بطلان)","cat":"إجراءات"},
        {"c":"no_response_90_days","o":"⚖️ مضت 90 يوماً بلا رد (موافقة ضمنية)","cat":"إجراءات"},
        {"c":"doc_unsigned","o":"⚖️ مستند غير موقع (لا حجية له)","cat":"مستندات"},
        {"c":"forgery_proven","o":"🚨 تزوير مثبت (جريمة جنائية)","cat":"مستندات"},
        {"c":"new_evidence_late","o":"📌 مستندات جديدة بعد الميعاد (مقبولة للنظام العام)","cat":"مستندات"},
        {"c":"opponent_hides_doc","o":"⚖️ الخصم يمتنع عن تقديم مستند (يُحكم ضده)","cat":"مستندات"},
        {"c":"witnesses_conflict","o":"⚖️ تناقض الشهود (تُرجح الأكثر عدالة)","cat":"شهادات"},
        {"c":"witness_is_relative","o":"⚖️ شاهد قريب للخصم (مردودة)","cat":"شهادات"},
        {"c":"two_vs_one_witness","o":"📌 شاهدان ضد واحد (تُقبل)","cat":"شهادات"},
        {"c":"settlement_offer is True and risk_score>60","o":"🤝 الصلح أفضل من التقاضي","cat":"صلح"},
        {"c":"settlement_offer is True and risk_score<=40","o":"⚖️ الصلح ممكن لكن القضية قوية","cat":"صلح"},
        {"c":"settlement_broken","o":"⚖️ نقض الصلح (يُلزَم بالتعويض)","cat":"صلح"},
        {"c":"reply_delay>30","o":"⏳ تأخير إداري أكثر من 30 يوماً","cat":"تأخير"},
        {"c":"reply_delay>15 and reply_delay<=30","o":"⏳ تأخير إداري 15-30 يوماً","cat":"تأخير"},
        {"c":"ambiguous_count>5","o":"🔍 عبارات غامضة كثيرة (تعسف واضح)","cat":"لغوي"},
        {"c":"ambiguous_count>3","o":"🔍 عبارات غامضة (طعن محتمل)","cat":"لغوي"},
        {"c":"contradictions>3","o":"⚡ تناقضات متعددة (فقدان المصداقية)","cat":"تناقضات"},
        {"c":"contradictions>1","o":"⚡ تناقض داخلي في مراسلات الخصم","cat":"تناقضات"},
        {"c":"force_majeure is True and days_abandoned>60","o":"📌 عذر قاهر يبرر الانقطاع","cat":"أعذار"},
        {"c":"proven_illness","o":"📌 مرض مثبت (عذر مقبول)","cat":"أعذار"},
        {"c":"natural_disaster","o":"📌 كارثة طبيعية (قوة قاهرة)","cat":"أعذار"},
        {"c":"epidemic","o":"📌 وباء (قوة قاهرة)","cat":"أعذار"},
        {"c":"health_quarantine","o":"📌 حجر صحي (قوة قاهرة)","cat":"أعذار"},
        {"c":"disproportionate_fine","o":"⚖️ غرامة غير متناسبة (تُخفَّض)","cat":"غرامات"},
        {"c":"fine_not_in_contract","o":"⚖️ غرامة غير محددة في العقد","cat":"غرامات"},
        {"c":"fine_illegal","o":"⚖️ غرامة مخالفة للنظام (تُلغى)","cat":"غرامات"},
        {"c":"court_grade=='Supreme' and similarity>0.8","o":"⭐ حكم مشابه من المحكمة العليا","cat":"سوابق"},
        {"c":"court_grade=='Appeal' and similarity>0.7","o":"📜 حكم من محكمة الاستئناف مشابه","cat":"سوابق"},
        {"c":"supreme_court_ruling","o":"⭐ حكم من المحكمة العليا","cat":"سوابق"},
        {"c":"high_similarity_ruling","o":"⭐ سابقة مباشرة (تشابه 90%+)","cat":"سوابق"},
        {"c":"expert_request_denied","o":"⚖️ رفض طلب الخبرة (إخلال بحق الدفاع)","cat":"إجراءات"},
        {"c":"unsigned_minutes","o":"⚖️ محضر اجتماع غير موقع","cat":"مستندات"},
        {"c":"opponent_threatens","o":"⚖️ تهديد متكرر من الخصم (تعسف)","cat":"سلوك"},
        {"c":"death_of_relative","o":"📌 وفاة قريب (إجازة عزاء رسمية)","cat":"أعذار"},
        {"c":"travel_ban","o":"📌 منع السفر (قوة قاهرة)","cat":"أعذار"},
        {"c":"apology_without_correction","o":"⚖️ اعتذار بلا تصحيح (لا قيمة قانونية)","cat":"سلوك"},
        {"c":"non_judicial_acknowledgment","o":"📌 إقرار غير قضائي (حجة على المُقِر)","cat":"مستندات"},
        {"c":"offer_rejected_by_opponent","o":"📌 عرضت الصلح ورفض (يحق لك التعويض)","cat":"صلح"},
        {"c":"eosb_not_paid","o":"⚖️ مكافأة نهاية الخدمة لم تُصرف","cat":"عمل"},
        {"c":"undefined_compensation","o":"⚖️ تعويض غير محدد (يُقدَّر بالضرر)","cat":"عمل"},
    ]

    def _eval(self, cond, ctx):
        try:
            for part in [p.strip() for p in cond.split(" and ")]:
                if not part: continue
                m = re.match(r"^(\w+)\s+is\s+(True|False)$", part)
                if m:
                    if bool(ctx.get(m[1], False)) != (m[2]=="True"): return False
                    continue
                m = re.match(r"^(\w+)$", part)
                if m:
                    if not bool(ctx.get(m[1], False)): return False
                    continue
                m = re.match(r"^(\w+)\s*(>=|<=|>|<)\s*([0-9.]+)$", part)
                if m:
                    lhs = float(ctx.get(m[1],0))
                    rhs = float(m[3])
                    ok = {">":lhs>rhs,">=":lhs>=rhs,"<":lhs<rhs,"<=":lhs<=rhs}[m[2]]
                    if not ok: return False
                    continue
                m = re.match(r"^(\w+)=='([^']*)'$", part.replace(" ",""))
                if m:
                    if str(ctx.get(m[1],"")) != m[2]: return False
                    continue
                return False
            return True
        except Exception:
            return False

    def apply(self, ctx):
        return [{"text":r["o"],"cat":r["cat"]} for r in self.RULES if self._eval(r["c"], ctx)]

# ══════════════════════════════════════════════
# ANALYSIS UTILITIES
# ══════════════════════════════════════════════
def detect_contradictions(texts):
    out = []
    for i, t in enumerate(texts):
        dates = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", t or "")
        if len(dates) >= 2 and dates[0] == dates[1]:
            out.append(f"تناقض في التواريخ بالملف {i+1}")
        if "مادة" in t and "خطأ" in t:
            out.append(f"خطأ في الإشارة لمادة بالملف {i+1}")
        if "توقيع" not in t and "ختم" in t:
            out.append(f"ختم بلا توقيع بالملف {i+1}")
    return out

def style_score(texts):
    s = 0
    for t in texts:
        if any(k in t for k in ["تهديد","فوراً","يجب"]): s += 1
        if any(k in t for k in ["نرجو","نأمل"]): s -= 1
        if "عاجل" in t: s += 2
    return max(s, 0)

def risk_score(tl, gaps, contras, ss):
    r = len(gaps)*2 + len(contras)*5 + ss
    if len(tl) < 2: r += 10
    if len(tl) > 10: r -= 5
    return min(max(r, 0), 100)

def cred_score(texts):
    s = 100
    for t in texts:
        if "نحن نؤكد" in t: s -= 5
        if "مادة" in t and "خطأ" in t: s -= 10
        if "كما سبق" in t: s -= 3
    return max(s, 0)

def fact_summary(tl):
    if not tl: return "لا توجد وقائع كافية."
    lines = ["تسلسل الأحداث:"]
    for ev in tl[:5]:
        dt = ev.get("date")
        if isinstance(dt, datetime):
            lines.append(f"- {dt.strftime('%d/%m/%Y')}: {ev.get('text','')[:100]}...")
    return "\n".join(lines)

def party_names(texts):
    kws = ["المدعي","المدعى عليه","الهيئة","الشركة","المؤسسة","الموظف","العامل"]
    found = []
    for t in texts:
        for k in kws:
            if k in (t or ""): found.append(k)
    return list(set(found)) or ["أطراف غير محددة"]

def dual_analysis(tl):
    s, w = set(), set()
    for ev in tl:
        t = (ev.get("text") or "").lower()
        full = ev.get("text") or ""
        if "أقر" in t or "اعترف" in t: w.add("اعتراف ضمني من الخصم")
        if any(k in t for k in ["عذر","مرض","ظروف"]): s.add("وجود أعذار رسمية")
        if "توقيع" not in t and "ختم" not in t: w.add("خطاب بلا توقيع")
        if "المادة" in full: s.add("استشهاد بمواد نظامية")
        if "تهديد" in t: w.add("لغة تهديدية من الخصم")
    return list(s), list(w)

def gen_strategy(tl, gaps, contras, risk):
    lines = []
    if gaps: lines.append("📌 استغل الفجوات الزمنية دليلاً على تعنت الخصم")
    if contras: lines.append("⚡ قدّم التناقضات لتقويض مصداقية الخصم")
    if risk > 70: lines.append("🚨 خطر مرتفع — يُوصى بالتصعيد القضائي الفوري")
    elif risk > 50: lines.append("⚠️ خطر متوسط — تفاوض مع الاحتفاظ بالخيار القضائي")
    else: lines.append("✅ خطر منخفض — المضي في الإجراءات بثقة")
    return "\n\n".join(lines) if lines else "🔎 الوضع مستقر، استمر في جمع المستندات."

TEMPLATES = {
"مذكرة دفاع": """بسم الله الرحمن الرحيم

السيد/ رئيس {court} المحترم

الموضوع: مذكرة دفاع — الدعوى رقم ({case_no})

نحن {client}، نرفع هذه المذكرة ضد {opponent}:

أولاً — الوقائع:
{facts}

ثانياً — الدفوع:
{defenses}

ثالثاً — الطلبات:
{requests}

المقدم: {client}
التاريخ: {date}
""",
"صحيفة دعوى": """بسم الله الرحمن الرحيم

السيد/ رئيس {court} المحترم

المدعي: {client}
المدعى عليه: {opponent}

الوقائع:
{facts}

الأسس القانونية:
{defenses}

الطلبات:
{requests}

التاريخ: {date}
""",
"عريضة اعتراض": """بسم الله الرحمن الرحيم

المقام الكريم/ رئيس {court}

الموضوع: اعتراض على القرار رقم ({case_no})

يرفع {client} هذا الاعتراض للأسباب:

{defenses}

الطلبات:
{requests}

التاريخ: {date}
""",
"إنذار رسمي": """بسم الله الرحمن الرحيم

إلى: {opponent}
من: {client}
التاريخ: {date}

أُنذركم رسمياً بشأن:
{facts}

في حال عدم الاستجابة خلال 15 يوماً ستُتَّخذ الإجراءات القانونية.

{requests}
""",
}

def gen_pleading(template, data):
    data.setdefault("date", datetime.now().strftime("%d/%m/%Y"))
    try: return TEMPLATES.get(template, "قالب غير موجود").format(**data)
    except KeyError as e: return f"خطأ: مفتاح مفقود {e}"

# ══════════════════════════════════════════════
# MEMORY
# ══════════════════════════════════════════════
def mem_add(text, tags=None, cat="عام"):
    m = {
        "id": hashlib.md5(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()[:8],
        "text": text, "tags": tags or [], "category": cat,
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state.memory.append(m)
    _save_mem()
    return m["id"]

def mem_del(mid):
    st.session_state.memory = [m for m in st.session_state.memory if m["id"] != mid]
    _save_mem()

def mem_edit(mid, new_text):
    for m in st.session_state.memory:
        if m["id"] == mid:
            m["text"] = new_text
            m["ts"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            break
    _save_mem()

def mem_search(q):
    q = q.lower()
    return [m for m in st.session_state.memory
            if q in m["text"].lower() or any(q in t.lower() for t in m.get("tags",[]))]

# ══════════════════════════════════════════════
# AI INTEGRATION — Claude + Gemini + Groq
# ══════════════════════════════════════════════
def call_ai(prompt: str, doc_ctx: str = "") -> str:
    provider = st.session_state.ai_provider

    # بناء system prompt مشترك
    mem_ctx = ""
    if st.session_state.memory:
        mem_ctx = "\n\nالذاكرة:\n" + "\n".join(
            f"- {m['text'][:150]}" for m in st.session_state.memory[-10:])

    law_ctx = ""
    if st.session_state.law_db:
        q_words = set(re.findall(r"[\u0600-\u06ff]{3,}", prompt))
        scored = sorted(
            [(sum(1 for w in q_words if w in r["text"]), r) for r in st.session_state.law_db],
            reverse=True)
        if scored and scored[0][0] > 0:
            law_ctx = "\n\nمواد قانونية ذات صلة:\n"
            for sc, r in scored[:4]:
                if sc > 0:
                    law_ctx += f"• [{r['law_name']}] {r['article']}: {r['text'][:250]}\n"

    system = f"""أنت محامٍ ومستشار قانوني سعودي خبير متخصص في نظام العمل والمرافعات والأنظمة السعودية.
- استند دائماً للأنظمة السعودية واذكر المواد
- كن محدداً وعملياً
- أجب بالعربية الفصحى{mem_ctx}{law_ctx}"""

    if doc_ctx:
        system += f"\n\nالمستندات:\n{doc_ctx[:4000]}"

    messages = []
    for msg in st.session_state.chat[-16:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})

    # ── Claude ──────────────────────────────
    if provider == "Claude (Anthropic)":
        key = st.session_state.api_key
        if not key: return "❌ أدخل Anthropic API Key في الإعدادات"
        payload = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 2048,
            "system": system,
            "messages": messages,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"Content-Type":"application/json",
                     "x-api-key":key,
                     "anthropic-version":"2023-06-01"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                d = json.loads(resp.read().decode())
                return d["content"][0]["text"]
        except urllib.error.HTTPError as e:
            return f"❌ Claude HTTP {e.code}: {e.read().decode()[:200]}"
        except Exception as e:
            return f"❌ Claude خطأ: {e}"

    # ── Gemini ──────────────────────────────
    elif provider == "Gemini (Google) — مجاني":
        key = st.session_state.gemini_key
        if not key: return "❌ أدخل Gemini API Key في الإعدادات"
        # دمج system مع أول رسالة
        full_messages = [{"role":"user","parts":[{"text": system + "\n\nالسؤال: " + prompt}]}]
        for msg in st.session_state.chat[-6:]:
            role = "user" if msg["role"]=="user" else "model"
            full_messages.append({"role":role,"parts":[{"text":msg["content"]}]})
        payload = json.dumps({"contents": full_messages}).encode("utf-8")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
        req = urllib.request.Request(url, data=payload,
            headers={"Content-Type":"application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                d = json.loads(resp.read().decode())
                return d["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            return f"❌ Gemini HTTP {e.code}: {e.read().decode()[:200]}"
        except Exception as e:
            return f"❌ Gemini خطأ: {e}"

    # ── Groq ────────────────────────────────
    elif provider == "Groq (مجاني وسريع)":
        key = st.session_state.groq_key
        if not key: return "❌ أدخل Groq API Key في الإعدادات"
        groq_messages = [{"role":"system","content":system}] + messages
        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": groq_messages,
            "max_tokens": 2048,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={"Content-Type":"application/json",
                     "Authorization":f"Bearer {key}"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                d = json.loads(resp.read().decode())
                return d["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            return f"❌ Groq HTTP {e.code}: {e.read().decode()[:200]}"
        except Exception as e:
            return f"❌ Groq خطأ: {e}"

    return "❌ اختر نموذج ذكاء اصطناعي من الإعدادات"

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚖️ Führer v2.0")
    st.markdown("---")

    st.markdown("**🤖 النموذج الذكي**")
    provider = st.selectbox("اختر النموذج", [
        "Claude (Anthropic)",
        "Gemini (Google) — مجاني",
        "Groq (مجاني وسريع)",
    ], label_visibility="collapsed")
    st.session_state.ai_provider = provider

    if provider == "Claude (Anthropic)":
        st.markdown("**🔑 Anthropic API Key**")
        k = st.text_input("Claude Key", value=st.session_state.api_key,
                          type="password", label_visibility="collapsed",
                          placeholder="sk-ant-api03-...")
        if k != st.session_state.api_key:
            st.session_state.api_key = k
        if k: st.success("✅ محفوظ")
        st.markdown("[احصل على Key مجاني ←](https://console.anthropic.com)", unsafe_allow_html=True)

    elif provider == "Gemini (Google) — مجاني":
        st.markdown("**🔑 Gemini API Key**")
        k = st.text_input("Gemini Key", value=st.session_state.gemini_key,
                          type="password", label_visibility="collapsed",
                          placeholder="AIza...")
        if k != st.session_state.gemini_key:
            st.session_state.gemini_key = k
        if k: st.success("✅ محفوظ")
        st.markdown("[احصل على Key مجاني ←](https://aistudio.google.com/apikey)", unsafe_allow_html=True)

    elif provider == "Groq (مجاني وسريع)":
        st.markdown("**🔑 Groq API Key**")
        k = st.text_input("Groq Key", value=st.session_state.groq_key,
                          type="password", label_visibility="collapsed",
                          placeholder="gsk_...")
        if k != st.session_state.groq_key:
            st.session_state.groq_key = k
        if k: st.success("✅ محفوظ")
        st.markdown("[احصل على Key مجاني ←](https://console.groq.com)", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**📋 نوع القضية**")
    ct = st.selectbox("النوع", [
        "قضية عمالية","نزاع تجاري","قضية عقارية",
        "نزاع إداري","قضية جنائية","إفلاس وتصفية"
    ], label_visibility="collapsed")
    st.session_state.case_ctx["type"] = ct

    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1: st.metric("الذاكرة", len(st.session_state.memory))
    with c2: st.metric("المستندات", len(st.session_state.docs))
    st.metric("مواد قانونية", len(st.session_state.law_db))

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
st.markdown("""
<div class="hdr">
<h1 style="margin:0;font-size:24px">⚖️ Führer   </h1>
<p style="color:#8090a0;margin:4px 0 0;font-size:12px">
تحليل المستندات • محرك القواعد • ذاكرة دائمة • Claude / Gemini / Groq
</p>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tabs = st.tabs([
    "📂 الملفات",
    "🤖 المستشار",
    "📅 الجدول الزمني",
    "⚖️ التحليل",
    "📜 القواعد",
    "📄 التقارير",
    "🧠 الذاكرة",
    "📚 القانون",
    "🔧 أدوات",
])
t_files,t_ai,t_tl,t_analysis,t_rules,t_reports,t_mem,t_law,t_tools = tabs

# ── TAB 1: الملفات ──────────────────────────
with t_files:
    st.subheader("📂 رفع وتحليل المستندات")
    uploaded = st.file_uploader(
        "اختر الملفات (PDF · DOCX · TXT · Parquet · JSON · CSV)",
        type=["pdf","docx","txt","parquet","json","csv"],
        accept_multiple_files=True,
    )
    if uploaded:
        st.info(f"✅ {len(uploaded)} ملف جاهز")
        if st.button("🔍 استخراج وتحليل", use_container_width=True):
            di = DocIntel()
            texts = []
            for f in uploaded:
                with st.expander(f"📄 {f.name}"):
                    txt = di.extract(f)
                    if txt:
                        texts.append(txt)
                        ents = di.entities(txt)
                        st.text(txt[:500] + ("..." if len(txt)>500 else ""))
                        if ents["articles"]:
                            st.markdown("**المواد:** " + " ".join(
                                f'<span class="badge">{a}</span>' for a in ents["articles"][:5]),
                                unsafe_allow_html=True)
                        if ents["dates"]:
                            st.markdown(f"**تواريخ:** {', '.join(ents['dates'][:5])}")
                        if ents["amounts"]:
                            st.markdown(f"**مبالغ:** {', '.join(ents['amounts'][:5])}")
                    else:
                        st.warning("⚠️ لم يُستخرج نص")
            st.session_state.docs = texts
            st.success(f"✅ {len(texts)} ملف | {sum(len(t) for t in texts):,} حرف")

# ── TAB 2: المستشار الذكي ───────────────────
with t_ai:
    st.subheader(f"🤖 المستشار — {st.session_state.ai_provider}")

    qp_cols = st.columns(4)
    qps = ["حلل وضعي القانوني","ما نقاط قوتي؟","ما المواعيد النظامية؟","اقترح استراتيجية"]
    for i,(col,q) in enumerate(zip(qp_cols,qps)):
        with col:
            if st.button(q, key=f"qp{i}", use_container_width=True):
                st.session_state.pending_q = q

    st.markdown("---")
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for msg in st.session_state.chat:
        cls = "chat-user" if msg["role"]=="user" else "chat-ai"
        ico = "👤" if msg["role"]=="user" else "⚖️"
        content = msg["content"].replace("\n","<br>")
        st.markdown(
            f'<div class="{cls}">{ico} {content}<br>'
            f'<small style="color:#556;font-size:10px">⏱ {msg.get("ts","")}</small></div>',
            unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    oc1,oc2 = st.columns(2)
    with oc1: use_docs = st.checkbox("📄 استخدم المستندات", value=True)
    with oc2: use_law  = st.checkbox("📚 استخدم قاعدة القانون", value=True)

    user_inp = st.text_area(
        "سؤالك",
        value=st.session_state.pending_q,
        height=100,
        placeholder="مثال: تأخر راتبي 3 أشهر وأُشعرت بالفصل — ما حقوقي؟"
    )

    sc1,sc2 = st.columns([4,1])
    with sc1: send_btn = st.button("📤 إرسال", use_container_width=True)
    with sc2:
        if st.button("🗑️", use_container_width=True):
            st.session_state.chat = []
            st.rerun()

    if send_btn and user_inp.strip():
        st.session_state.pending_q = ""
        doc_ctx = "\n\n".join(st.session_state.docs[:3])[:5000] if use_docs else ""
        ts = datetime.now().strftime("%H:%M")
        st.session_state.chat.append({"role":"user","content":user_inp,"ts":ts})
        with st.spinner("⚖️ يحلل..."):
            resp = call_ai(user_inp, doc_ctx=doc_ctx)
        st.session_state.chat.append({"role":"assistant","content":resp,"ts":ts})
        if len(resp)>80 and "❌" not in resp:
            mem_add(f"س: {user_inp[:80]} | ج: {resp[:150]}...",
                   tags=["محادثة", st.session_state.case_ctx.get("type","")],
                   cat="محادثة")
        st.rerun()

# ── TAB 3: الجدول الزمني ────────────────────
with t_tl:
    st.subheader("📅 الجدول الزمني")
    if not st.session_state.docs:
        st.info("⚠️ ارفع الملفات أولاً")
    else:
        tl_e = Timeline()
        tl   = tl_e.build(st.session_state.docs)
        gaps = tl_e.gaps(tl)
        dls  = tl_e.deadlines(tl)
        m1,m2,m3 = st.columns(3)
        with m1: st.metric("الأحداث", len(tl))
        with m2: st.metric("الفجوات", len(gaps))
        with m3: st.metric("المواعيد", len(dls))
        for ev in tl:
            dt = ev.get("date")
            if isinstance(dt, datetime):
                st.markdown(
                    f'<div class="tl-item"><strong>{dt.strftime("%d/%m/%Y")}</strong>'
                    f'<br><span style="color:#a0b0c0;font-size:13px">{ev.get("text","")[:120]}...</span></div>',
                    unsafe_allow_html=True)
        if gaps:
            st.markdown("### ⚠️ الفجوات")
            for g in gaps:
                clr = "#c04040" if g["sev"]=="high" else "#c08020"
                st.markdown(
                    f'<div class="tl-item tl-gap">'
                    f'<strong style="color:{clr}">⏰ {g["days"]} يوم</strong>'
                    f' من {g["from"]} إلى {g["to"]}</div>',
                    unsafe_allow_html=True)
        if dls:
            st.markdown("### ⏰ المواعيد القانونية")
            for d in dls:
                st.warning(f"**{d['type']}**: {d['ev'][:60]} → {d['dl']}")

# ── TAB 4: التحليل ──────────────────────────
with t_analysis:
    st.subheader("⚖️ تحليل نقاط القوة والضعف")
    if not st.session_state.docs:
        st.info("⚠️ ارفع الملفات أولاً")
    else:
        texts = st.session_state.docs
        tl_e  = Timeline()
        tl    = tl_e.build(texts)
        gaps  = tl_e.gaps(tl)
        contras = detect_contradictions(texts)
        ss    = style_score(texts)
        risk  = risk_score(tl, gaps, contras, ss)
        cred  = cred_score(texts)
        strs, weaks = dual_analysis(tl)
        mc = st.columns(4)
        with mc[0]: st.metric("مستوى الخطر", f"{risk}/100")
        with mc[1]: st.metric("مصداقية الخصم", f"{cred}/100")
        with mc[2]: st.metric("التناقضات", len(contras))
        with mc[3]: st.metric("الفجوات", len(gaps))
        color = "#c04040" if risk>70 else "#c08020" if risk>40 else "#40c060"
        st.markdown(f'<div style="background:#0d1320;border:1px solid #1e2a40;border-radius:6px;padding:8px;margin:8px 0"><div style="background:{color};width:{risk}%;height:8px;border-radius:4px"></div><small style="color:#8090a0">الخطر: {risk}%</small></div>', unsafe_allow_html=True)
        sc1,sc2 = st.columns(2)
        with sc1:
            st.markdown("### ✅ نقاط القوة")
            for s in strs: st.markdown(f'<div class="ok-card">✅ {s}</div>', unsafe_allow_html=True)
            if not strs: st.info("لا توجد")
        with sc2:
            st.markdown("### ❌ نقاط الضعف")
            for w in weaks: st.markdown(f'<div class="bad-card">⚠️ {w}</div>', unsafe_allow_html=True)
            if not weaks: st.success("لا توجد")
        if contras:
            st.markdown("### ⚡ التناقضات")
            for c in contras: st.error(f"⚡ {c}")

# ── TAB 5: القواعد ──────────────────────────
with t_rules:
    st.subheader(f"📜 محرك القواعد — {len(RuleEngine.RULES)} قاعدة")
    with st.expander("⚙️ بيانات القضية", expanded=True):
        rc1,rc2,rc3 = st.columns(3)
        with rc1:
            d_aban  = st.number_input("أيام الانقطاع", 0, 3000, 0)
            d_fire  = st.number_input("أيام منذ الفصل", 0, 3000, 0)
            d_reply = st.number_input("تأخر رد الخصم (يوم)", 0, 365, 0)
            d_abs   = st.number_input("أيام الغياب", 0, 365, 0)
        with rc2:
            svc    = st.number_input("سنوات الخدمة", 0.0, 50.0, 0.0, 0.5)
            rscore = st.number_input("درجة الخطر (0-100)", 0, 100, 50)
            sim    = st.number_input("تشابه السابقة (0-1)", 0.0, 1.0, 0.0, 0.1)
            cgrade = st.selectbox("درجة المحكمة", ["","Supreme","Appeal","First"])
        with rc3:
            no_inv  = st.checkbox("فصل بلا تحقيق")
            arb_dis = st.checkbox("فصل تعسفي")
            fm      = st.checkbox("عذر قاهر")
            settl   = st.checkbox("يوجد عرض صلح")
            forgery = st.checkbox("تزوير مثبت")
            sal_del = st.checkbox("تأخير الراتب")
            eosb    = st.checkbox("مكافأة لم تُصرف")
            ill     = st.checkbox("مرض مثبت")
            no_resp = st.checkbox("90 يوم بلا رد")

    if st.button("🔍 تطبيق القواعد", use_container_width=True):
        auto_ctx = {}
        if st.session_state.docs:
            auto_ctx["contradictions"] = len(detect_contradictions(st.session_state.docs))
            di = DocIntel()
            auto_ctx["ambiguous_count"] = sum(len(di.ambiguous(t)) for t in st.session_state.docs)
        ctx = {
            "days_abandoned":d_aban, "days_since_firing":d_fire,
            "reply_delay":d_reply,  "absence_days":d_abs,
            "service_length":svc,   "risk_score":rscore,
            "similarity":sim,       "court_grade":cgrade,
            "no_investigation":no_inv, "arbitrary_dismissal":arb_dis,
            "force_majeure":fm,     "settlement_offer":settl,
            "forgery_proven":forgery,"salary_delay":sal_del,
            "eosb_not_paid":eosb,   "proven_illness":ill,
            "no_response_90_days":no_resp, **auto_ctx,
        }
        alerts = RuleEngine().apply(ctx)
        if alerts:
            cats = {}
            for a in alerts: cats.setdefault(a["cat"],[]).append(a["text"])
            for cat,items in cats.items():
                st.markdown(f"**{cat}**")
                for item in items:
                    st.markdown(f'<div class="rule-card">{item}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ لا تنبيهات بناءً على البيانات المدخلة")

# ── TAB 6: التقارير ─────────────────────────
with t_reports:
    st.subheader("📄 التقارير واللوائح")
    rp1,rp2 = st.columns(2)
    with rp1:
        st.markdown("### 📊 تقرير شامل")
        if st.button("🖨️ إنشاء التقرير", use_container_width=True):
            if not st.session_state.docs:
                st.warning("ارفع الملفات أولاً")
            else:
                texts = st.session_state.docs
                tl_e  = Timeline()
                tl    = tl_e.build(texts)
                gaps  = tl_e.gaps(tl)
                dls   = tl_e.deadlines(tl)
                contras = detect_contradictions(texts)
                ss    = style_score(texts)
                risk  = risk_score(tl,gaps,contras,ss)
                cred  = cred_score(texts)
                strs,weaks = dual_analysis(tl)
                parties = party_names(texts)
                report = f"""تقرير قانوني — {datetime.now().strftime('%d/%m/%Y %H:%M')}
نوع القضية: {st.session_state.case_ctx.get('type','')}
{'='*40}
الخطر: {risk}/100 | المصداقية: {cred}/100
التناقضات: {len(contras)} | الفجوات: {len(gaps)}
الأطراف: {', '.join(parties)}

{fact_summary(tl)}

المواعيد:
""" + "".join(f"• {d['type']}: {d['ev'][:40]} → {d['dl']}\n" for d in dls) + """
نقاط القوة:
""" + "".join(f"• {s}\n" for s in strs) + """
نقاط الضعف:
""" + "".join(f"• {w}\n" for w in weaks) + f"""
الاستراتيجية:
{gen_strategy(tl,gaps,contras,risk)}"""
                st.text_area("التقرير", report, height=300)
                st.download_button("⬇️ تحميل",
                    data=report.encode("utf-8"),
                    file_name=f"تقرير_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain")

    with rp2:
        st.markdown("### ✍️ مسودة اللائحة")
        tmpl_name = st.selectbox("النوع", list(TEMPLATES.keys()))
        court_n  = st.text_input("المحكمة", "محكمة العمل")
        case_n   = st.text_input("رقم القضية", "___/___/____")
        client_n = st.text_input("الموكل", "")
        oppon_n  = st.text_input("الخصم", "")
        reqs     = st.text_area("الطلبات", "إلغاء القرار والتعويض", height=100)
        if st.button("✍️ إنشاء المسودة", use_container_width=True):
            if st.session_state.docs:
                tl_e = Timeline()
                tl   = tl_e.build(st.session_state.docs)
                strs,_ = dual_analysis(tl)
                facts  = fact_summary(tl)
                defenses = "\n".join(strs) or "سيتم تحديد الدفوع"
                parties  = party_names(st.session_state.docs)
            else:
                facts = "يرجى إضافة المستندات"
                defenses = "سيتم تحديد الدفوع"
                parties = []
            data = {
                "court":   court_n or "محكمة العمل",
                "case_no": case_n,
                "client":  client_n or (parties[0] if parties else "الموكل"),
                "opponent":oppon_n or (parties[1] if len(parties)>1 else "الخصم"),
                "facts":   facts,
                "defenses":defenses,
                "requests":reqs,
            }
            draft = gen_pleading(tmpl_name, data)
            st.text_area("المسودة", draft, height=400)
            st.download_button("⬇️ تحميل المسودة",
                data=draft.encode("utf-8"),
                file_name=f"مسودة_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain")

# ── TAB 7: الذاكرة ──────────────────────────
with t_mem:
    st.subheader("🧠 الذاكرة الدائمة")
    with st.expander("➕ إضافة ذاكرة"):
        mt   = st.text_area("النص", height=100, placeholder="مثال: الموكل يعمل منذ 2019")
        mcat = st.selectbox("الفئة", ["قضية","موكل","حكم","ملاحظة","استراتيجية","قانون","عام"])
        mtags = st.text_input("وسوم (فاصلة)")
        if st.button("💾 حفظ"):
            if mt.strip():
                tags = [x.strip() for x in mtags.split(",") if x.strip()]
                mid = mem_add(mt, tags, mcat)
                st.success(f"✅ محفوظ (ID: {mid})")
                st.rerun()

    mq = st.text_input("🔍 بحث في الذاكرة")
    mems = mem_search(mq) if mq else st.session_state.memory

    if not mems:
        st.info("الذاكرة فارغة")
    else:
        st.markdown(f"**{len(mems)} ذاكرة**")
        for m in reversed(mems):
            ec1,ec2,ec3 = st.columns([8,1,1])
            with ec1:
                badges = "".join(f'<span class="badge">{t}</span>' for t in m.get("tags",[]))
                st.markdown(
                    f'<div class="mem-card">'
                    f'<small style="color:#8090a0">{m.get("ts","")} · {m.get("category","")}</small>'
                    f'<br>{m["text"]}<br>{badges}</div>',
                    unsafe_allow_html=True)
            with ec2:
                if st.button("✏️", key=f"e_{m['id']}"):
                    st.session_state[f"edit_{m['id']}"] = True
            with ec3:
                if st.button("🗑", key=f"d_{m['id']}"):
                    mem_del(m["id"]); st.rerun()
            if st.session_state.get(f"edit_{m['id']}"):
                new_t = st.text_area("تعديل", value=m["text"], key=f"et_{m['id']}", height=100)
                if st.button("✅ حفظ", key=f"sv_{m['id']}"):
                    mem_edit(m["id"], new_t)
                    del st.session_state[f"edit_{m['id']}"]
                    st.rerun()

    st.markdown("---")
    ex1,ex2 = st.columns(2)
    with ex1:
        if st.button("📤 تصدير"):
            d = json.dumps(st.session_state.memory, ensure_ascii=False, indent=2)
            st.download_button("⬇️ JSON", d.encode("utf-8"), "fuehrer_memory.json", "application/json")
    with ex2:
        mf = st.file_uploader("📥 استيراد JSON", type=["json"], key="mf_up")
        if mf:
            try:
                imported = json.loads(mf.read())
                existing = {m["id"] for m in st.session_state.memory}
                new_ones = [m for m in imported if m.get("id") not in existing]
                st.session_state.memory.extend(new_ones)
                _save_mem()
                st.success(f"✅ {len(new_ones)} ذاكرة مستوردة")
            except Exception as e:
                st.error(f"❌ {e}")

# ── TAB 8: القانون ──────────────────────────
with t_law:
    st.subheader("📚 قاعدة الأنظمة السعودية")
    lc1,lc2 = st.columns(2)
    with lc1:
        pq = st.file_uploader("📂 ارفع ملف Parquet", type=["parquet"], key="pq_law")
        if pq and st.button("📥 تحميل القانون", use_container_width=True):
            with st.spinner("جاري الاستخراج..."):
                records = decode_parquet_arabic(_bytes(pq))
            if records:
                st.session_state.law_db = records
                st.success(f"✅ {len(records)} سجل قانوني")
                law_names = list(set(r["law_name"] for r in records))
                for ln in law_names[:8]:
                    st.markdown(f'<span class="badge">{ln}</span>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ لم يُستخرج محتوى")
    with lc2:
        st.markdown("**➕ إضافة مادة يدوياً**")
        ma_text = st.text_area("نص المادة", height=100, key="ma_t")
        ma_art  = st.text_input("اسم المادة", key="ma_a")
        ma_law  = st.text_input("اسم النظام", key="ma_l")
        if st.button("➕ إضافة"):
            if ma_text.strip():
                st.session_state.law_db.append({
                    "text":ma_text,"article":ma_art,
                    "law_name":ma_law or "نظام يدوي","source":"manual"})
                st.success("✅ تمت الإضافة")

    if st.session_state.law_db:
        st.metric("إجمالي السجلات", len(st.session_state.law_db))
        law_q = st.text_input("🔍 ابحث في الأنظمة")
        if law_q:
            q_words = set(re.findall(r"[\u0600-\u06FF]{3,}", law_q))
            scored = sorted(
                [(sum(1 for w in q_words if w in r.get("text","") or w in r.get("article","")), r)
                 for r in st.session_state.law_db],
                reverse=True)
            results = [(sc,r) for sc,r in scored if sc>0][:10]
            if results:
                for sc,r in results:
                    with st.expander(f"📜 {r.get('article','')} — {r.get('law_name','')}"):
                        st.write(r["text"])
                        if st.button("💾 حفظ في الذاكرة", key=f"ls_{hash(r['text'])%99999}"):
                            mem_add(f"[{r.get('law_name','')}] {r.get('article','')}: {r['text'][:200]}",
                                   tags=["قانون"], cat="قانون")
                            st.success("✅")
            else:
                st.info("لا نتائج")

# ── TAB 9: أدوات ────────────────────────────
with t_tools:
    st.subheader("🔧 الأدوات المتقدمة")
    tt = st.tabs(["📈 استراتيجية","🔍 كيانات","📤 تصدير"])

    with tt[0]:
        if not st.session_state.docs:
            st.info("ارفع الملفات أولاً")
        else:
            texts = st.session_state.docs
            tl_e  = Timeline()
            tl    = tl_e.build(texts)
            gaps  = tl_e.gaps(tl)
            contras = detect_contradictions(texts)
            ss    = style_score(texts)
            risk  = risk_score(tl,gaps,contras,ss)
            cred  = cred_score(texts)
            st.markdown(gen_strategy(tl,gaps,contras,risk))
            st.markdown("---")
            sa1,sa2 = st.columns(2)
            with sa1:
                st.markdown("**فرص الصلح:**")
                if risk>70: st.info("📉 منخفضة")
                elif risk<30 and cred>70: st.info("📈 عالية")
                else: st.info("📊 متوسطة")
            with sa2:
                st.markdown("**الأدلة الناقصة:**")
                di = DocIntel()
                claims_all = []
                for t in texts: claims_all.extend(di.claims(t))
                missing = [c for c in claims_all if not any(c in t for t in texts)]
                if missing:
                    for c in missing: st.error(f"❌ {c}")
                else:
                    st.success("✅ جميع الادعاءات مدعومة")

    with tt[1]:
        if not st.session_state.docs:
            st.info("ارفع الملفات أولاً")
        else:
            di = DocIntel()
            all_e = {"parties":[],"amounts":[],"articles":[],"dates":[]}
            for t in st.session_state.docs:
                e = di.entities(t)
                for k in all_e: all_e[k].extend(e[k])
            for k in all_e: all_e[k] = list(set(all_e[k]))
            ne1,ne2 = st.columns(2)
            with ne1:
                st.markdown("**👥 الأطراف:**")
                for p in all_e["parties"]: st.markdown(f'<span class="badge">{p}</span>', unsafe_allow_html=True)
                st.markdown("**📅 التواريخ:**")
                for d in all_e["dates"][:8]: st.markdown(f'<span class="badge">{d}</span>', unsafe_allow_html=True)
            with ne2:
                st.markdown("**💰 المبالغ:**")
                for a in all_e["amounts"]: st.markdown(f'<span class="badge">{a}</span>', unsafe_allow_html=True)
                st.markdown("**📜 المواد:**")
                for art in all_e["articles"][:6]: st.markdown(f'<span class="badge">{art}</span>', unsafe_allow_html=True)

    with tt[2]:
        if st.button("📦 تصدير كامل"):
            export = {
                "memory": st.session_state.memory,
                "chat": st.session_state.chat,
                "case_ctx": st.session_state.case_ctx,
                "exported_at": datetime.now().isoformat(),
                "version": "2.0",
            }
            d = json.dumps(export, ensure_ascii=False, indent=2)
            st.download_button("⬇️ تحميل",
                d.encode("utf-8"),
                f"fuehrer_backup_{datetime.now().strftime('%Y%m%d')}.json",
                "application/json")

st.markdown('<hr><p style="text-align:center;color:#303848;font-size:11px">Führer |Claude · Gemini · Groq</p>', unsafe_allow_html=True)
PYEOF
echo "Lines: $(wc -l < /mnt/user-data/outputs/fuehrer_v2.py)"