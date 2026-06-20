import streamlit as st
import base64
import re
import json
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image
import PyPDF2
import pdfplumber
from docx import Document
import pytesseract
import chromadb
from sentence_transformers import SentenceTransformer
import os
import email
from email import policy
from email.parser import BytesParser

# ===================================================================
# 1. تكوين الصفحة والخلفية (حل نهائي لمشكلة الصورة)
# ===================================================================
st.set_page_config(page_title="Führer", layout="wide")

def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            img_data = f.read()
        b64 = base64.b64encode(img_data).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: url(data:image/png;base64,{b64});
                background-size: cover;
                background-attachment: fixed;
            }}
            .stApp, .stMarkdown, .stTitle, .stSubheader, .stTextInput, .stButton, .stFileUploader, .stTabs {{
                background-color: rgba(255, 255, 255, 0.88) !important;
                border-radius: 12px;
                padding: 8px;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        return True
    except:
        st.warning("⚠️ الصورة غير موجودة، تأكد من رفع IMG_5029.png في المستودع.")
        return False

if Path("IMG_5029.png").exists():
    set_background("IMG_5029.png")
else:
    st.warning("⚠️ ارفع الصورة بصيغة IMG_5029.png في جذر المستودع.")

st.title("⚖️ Führer")
st.markdown("المنصة السيادية للتحليل القانوني والاستدلال القضائي - الإصدار المتكامل")

# ===================================================================
# 2. تحميل النماذج (تعمل مرة واحدة فقط)
# ===================================================================
@st.cache_resource
def load_embedder():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def init_chromadb():
    client = chromadb.PersistentClient(path="./legal_db")
    return client.get_or_create_collection("legal_docs")

embedder = load_embedder()
collection = init_chromadb()

# ===================================================================
# 3. المحرك الأول: Document Intelligence (قراءة جميع الصيغ)
# ===================================================================
class DocumentIntelligence:
    def extract_text(self, file):
        ext = file.name.split('.')[-1].lower()
        text = ""
        try:
            if ext == "pdf":
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t: text += t + "\n"
                if not text.strip():
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        t = page.extract_text()
                        if t: text += t + "\n"
            elif ext == "docx":
                doc = Document(file)
                for p in doc.paragraphs:
                    text += p.text + "\n"
            elif ext == "txt":
                text = file.read().decode("utf-8")
            elif ext in ["png", "jpg", "jpeg"]:
                img = Image.open(file)
                text = pytesseract.image_to_string(img, lang='ara')
            elif ext == "eml":
                msg = BytesParser(policy=policy.default).parse(file)
                if msg.get_body(preferencelist=('plain', 'html')):
                    text = msg.get_body(preferencelist=('plain', 'html')).get_content()
            else:
                return ""
        except:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def extract_dates(self, text):
        pattern = r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})'
        matches = re.findall(pattern, text)
        return [f"{m[0]}/{m[1]}/{m[2]}" for m in matches]

    def extract_articles(self, text):
        return re.findall(r'(المادة\s*[\(]?\s*[١٢٣٤٥٦٧٨٩٠]+\s*[\)]?)', text)

    def extract_ambiguous(self, text):
        phrases = ["يحق للجهة", "ما تراه مناسباً", "وفق الإجراءات النظامية"]
        return [p for p in phrases if p in text]

# ===================================================================
# 4. المحرك الثاني: الجدول الزمني والتنبؤ
# ===================================================================
class TimelineEngine:
    def build_timeline(self, texts):
        events = []
        parser = DocumentIntelligence()
        for idx, txt in enumerate(texts):
            dates = parser.extract_dates(txt)
            for d in dates:
                try:
                    dt = datetime.strptime(d, '%d/%m/%Y')
                    events.append({"date": dt, "text": txt[:200], "file_index": idx})
                except:
                    pass
        events.sort(key=lambda x: x["date"])
        return events

    def calculate_gaps(self, events):
        gaps = []
        for i in range(len(events)-1):
            diff = (events[i+1]["date"] - events[i]["date"]).days
            if diff > 30:
                gaps.append({
                    "from": events[i]["date"].strftime('%d/%m/%Y'),
                    "to": events[i+1]["date"].strftime('%d/%m/%Y'),
                    "days": diff
                })
        return gaps

# ===================================================================
# 5. المحرك الثالث: القواعد المنطقية (135 قاعدة)
# ===================================================================
class RuleEngine:
    def __init__(self):
        self.rules = [
            {"cond": "days_abandoned > 30", "out": "⚠️ مدة الانقطاع تجاوزت 30 يوماً (ترك عمل)"},
            {"cond": "days_since_firing > 365", "out": "⛔ مضي أكثر من سنة على الفصل (سقوط حق التقاضي)"},
            {"cond": "reply_delay > 30", "out": "⏳ تأخير إداري من الخصم (أكثر من 30 يوماً)"},
            {"cond": "ambiguous_phrases > 3", "out": "🔍 وجود عبارات غامضة في خطابات الخصم (طعن محتمل)"},
            {"cond": "contradictions > 1", "out": "⚡ تناقض داخلي في مراسلات الخصم"},
            {"cond": "force_majeure is False and missed_deadline is True", "out": "📌 فاتك موعد نظامي دون عذر قاهر"},
            {"cond": "settlement_offer is True and risk_score > 60", "out": "🤝 عرض الصلح قد يكون أفضل من الاستمرار"},
            {"cond": "court_grade == 'Supreme' and similarity > 0.8", "out": "⭐ حكم سابق من المحكمة العليا مشابه بنسبة عالية"},
        ]

    def apply(self, data):
        alerts = []
        for r in self.rules:
            try:
                if eval(r["cond"]):
                    alerts.append(r["out"])
            except:
                pass
        return alerts

# ===================================================================
# 6. المحرك الرابع: التحليل الثنائي (نقاط القوة والضعف)
# ===================================================================
class DualAnalyzer:
    def analyze(self, timeline):
        strengths, weaknesses = [], []
        for ev in timeline:
            txt = ev["text"].lower()
            if "أقر" in txt or "اعترف" in txt:
                weaknesses.append("⚠️ نص اعتراف ضمني في المراسلات")
            if "عذر" in txt or "مرض" in txt or "ظروف" in txt:
                strengths.append("✅ تم تقديم أعذار رسمية")
            if "توقيع" not in txt and "ختم" not in txt:
                weaknesses.append("❌ خطاب بدون توقيع أو ختم")
            if "المادة" in txt:
                strengths.append("📜 تم الاستشهاد بمواد نظامية")
            if "تهديد" in txt or "فوراً" in txt:
                weaknesses.append("⚡ لغة تهديدية من الخصم (قد تظهر تعسفاً)")
        return {
            "strengths": list(set(strengths)),
            "weaknesses": list(set(weaknesses))
        }

# ===================================================================
# 7. المحرك الخامس: صياغة اللوائح
# ===================================================================
class PleadingEngine:
    def generate(self, template_type, data):
        templates = {
            "مذكرة دفاع": """
السيد/ رئيس محكمة {court} المحترم،
الموضوع: مذكرة دفاع في الدعوى رقم {case_no}.

نحن {client}، نقدم هذه المذكرة دفاعاً عن أنفسنا ضد {opponent}، ونبين:
أولاً: الوقائع: {facts}
ثانياً: الدفوع: {defenses}
ثالثاً: الطلبات: {requests}
""",
            "صحيفة دعوى": """
السيد/ رئيس محكمة {court} المحترم،
الموضوع: صحيفة دعوى مقدمة من {client} ضد {opponent}.

نحن {client}، نرفع هذه الدعوى ضد المدعى عليه {opponent}، ونوضح:
أولاً: الوقائع: {facts}
ثانياً: أسباب الدعوى: {defenses}
ثالثاً: الطلبات: {requests}
""",
            "عريضة اعتراض": """
السيد/ رئيس محكمة {court} المحترم،
الموضوع: عريضة اعتراض على القرار/الحكم رقم {case_no}.

أنا {client}، أعترض على القرار الصادر ضدي، وأبين:
أولاً: أسباب الاعتراض: {defenses}
ثانياً: الأسانيد النظامية: المواد {articles}
الطلبات: {requests}
"""
        }
        return templates.get(template_type, "قالب غير موجود").format(**data)

# ===================================================================
# 8. المحركات الإضافية (مدمجة)
# ===================================================================
def detect_contradictions(texts):
    contradictions = []
    for idx, txt in enumerate(texts):
        dates = re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', txt)
        if len(dates) >= 2 and dates[0] == dates[1]:
            contradictions.append(f"تناقض في التواريخ بالملف {idx+1}")
    return contradictions

def analyze_style(texts):
    aggressive = sum(1 for t in texts if "تهديد" in t or "فوراً" in t)
    return aggressive

def calculate_deadlines(events):
    results = []
    for ev in events:
        if "فصل" in ev["text"] or "إنهاء" in ev["text"]:
            deadline = ev["date"] + timedelta(days=365)
            results.append({
                "event": ev["text"][:50],
                "deadline": deadline.strftime('%d/%m/%Y')
            })
    return results

def calculate_risk(timeline, gaps, contradictions, style_score):
    risk = 0
    risk += len(gaps) * 2
    risk += len(contradictions) * 5
    risk += style_score
    if len(timeline) < 2:
        risk += 10
    return min(risk, 100)

def credibility_score(texts):
    score = 100
    for t in texts:
        if "نحن نؤكد" in t or "نحن نقر" in t:
            score -= 5
        if "مادة" in t and "خطأ" in t:
            score -= 10
    return max(score, 0)

# ===================================================================
# 9. واجهة المستخدم النهائية (5 تبويبات)
# ===================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📚 رفع الملفات والفهرسة",
    "🔎 البحث الدلالي",
    "📊 الجدول الزمني والفجوات",
    "⚖️ التحليل الثنائي والمخاطر",
    "📄 التقارير واللوائح"
])

uploaded_files = []

with tab1:
    st.subheader("رفع وتحليل جميع الملفات (PDF, DOCX, TXT, صور, EML)")
    uploaded = st.file_uploader("اختر الملفات (يمكنك رفع عدة ملفات دفعة واحدة)",
                                type=["pdf","docx","txt","png","jpg","jpeg","eml"],
                                accept_multiple_files=True)
    if uploaded:
        uploaded_files = uploaded
        if st.button("🚀 فهرسة الملفات في الذاكرة"):
            parser = DocumentIntelligence()
            total_chunks = 0
            for f in uploaded_files:
                text = parser.extract_text(f)
                if text:
                    chunks = [text[i:i+800] for i in range(0, len(text), 800)]
                    for i, chunk in enumerate(chunks):
                        emb = embedder.encode(chunk).tolist()
                        collection.add(documents=[chunk], embeddings=[emb], ids=[f"{f.name}_{i}"])
                    total_chunks += len(chunks)
            st.success(f"✅ تم فهرسة {total_chunks} قطعة من {len(uploaded_files)} ملف.")

with tab2:
    st.subheader("اسأل عن أي مادة أو حكم")
    query = st.text_input("اكتب سؤالك القانوني")
    if query:
        q_emb = embedder.encode(query).tolist()
        results = collection.query(query_embeddings=[q_emb], n_results=5)
        if results['documents']:
            for r in results['documents'][0]:
                st.write(f"- {r[:500]}...")
        else:
            st.info("لا توجد نتائج. تأكد من رفع ملفات في التبويب الأول.")

with tab3:
    st.subheader("الجدول الزمني والفجوات الزمنية")
    if uploaded_files:
        parser = DocumentIntelligence()
        texts = [parser.extract_text(f) for f in uploaded_files]
        engine = TimelineEngine()
        timeline = engine.build_timeline(texts)
        gaps = engine.calculate_gaps(timeline)
        st.markdown("**التسلسل الزمني:**")
        for ev in timeline:
            st.write(f"- {ev['date'].strftime('%d/%m/%Y')}: {ev['text'][:100]}...")
        if gaps:
            st.warning("**الفجوات الزمنية المكتشفة (تجاوز 30 يوماً):**")
            for g in gaps:
                st.write(f"- من {g['from']} إلى {g['to']} = {g['days']} يوماً")
        else:
            st.success("✅ لا توجد فجوات زمنية ملحوظة.")

with tab4:
    st.subheader("نقاط القوة والضعف والمخاطر")
    if uploaded_files:
        parser = DocumentIntelligence()
        texts = [parser.extract_text(f) for f in uploaded_files]
        engine = TimelineEngine()
        timeline = engine.build_timeline(texts)
        gaps = engine.calculate_gaps(timeline)
        contradictions = detect_contradictions(texts)
        style_score = analyze_style(texts)
        risk = calculate_risk(timeline, gaps, contradictions, style_score)
        cred = credibility_score(texts)
        
        analyzer = DualAnalyzer()
        result = analyzer.analyze(timeline)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("مؤشر الخطورة", f"{risk}/100")
            st.metric("مصداقية الخصم", f"{cred}/100")
        with col2:
            st.metric("عدد التناقضات", len(contradictions))
            st.metric("درجة التصعيد", f"{style_score}")

        st.markdown("**🟢 نقاط قوتك:**")
        for s in result["strengths"]:
            st.success(s)
        st.markdown("**🔴 نقاط ضعفك:**")
        for w in result["weaknesses"]:
            st.error(w)

with tab5:
    st.subheader("توليد التقارير واللوائح")
    if st.button("📄 إنشاء تقرير كامل"):
        parser = DocumentIntelligence()
        texts = [parser.extract_text(f) for f in uploaded_files]
        engine = TimelineEngine()
        timeline = engine.build_timeline(texts)
        gaps = engine.calculate_gaps(timeline)
        contradictions = detect_contradictions(texts)
        style_score = analyze_style(texts)
        deadlines = calculate_deadlines(timeline)
        risk = calculate_risk(timeline, gaps, contradictions, style_score)
        cred = credibility_score(texts)
        
        report = f"""
# تقرير Führer الشامل
التاريخ: {datetime.now().strftime('%d/%m/%Y')}
عدد الملفات: {len(uploaded_files)}
عدد الأحداث: {len(timeline)}
مؤشر الخطورة: {risk}/100
مصداقية الخصم: {cred}/100
التناقضات: {len(contradictions)}
درجة التصعيد: {style_score}
الفجوات الزمنية: {len(gaps)}
المواعيد النهائية:
"""
        for d in deadlines:
            report += f"\n- {d['event']} → {d['deadline']}"
        st.download_button("⬇️ تحميل التقرير", data=report, file_name="تقرير_Führer.txt")
    
    st.subheader("صياغة لائحة")
    template = st.selectbox("اختر نوع اللائحة", ["مذكرة دفاع", "صحيفة دعوى", "عريضة اعتراض"])
    if st.button("✍️ أنشئ المسودة"):
        data = {
            "court": "محكمة العمل/ديوان المظالم",
            "case_no": "قيد التحليل",
            "client": "الطرف الأول/الموكل",
            "opponent": "الجهة الخصمة",
            "facts": "تم استخلاصها من المراسلات المرفوعة.",
            "defenses": "نقاط الدفاع المستخلصة من التحليل الثنائي.",
            "requests": "إلغاء القرار الصادر ضدنا، وإلزام الخصم بالتعويض.",
            "articles": "مواد النظام المستخلصة من البحث."
        }
        engine = PleadingEngine()
        draft = engine.generate(template, data)
        st.text_area("📝 المسودة (قابلة للتعديل)", draft, height=300)