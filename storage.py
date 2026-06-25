# storage.py
"""
وظائف التخزين لملفات JSON والجلسات والذاكرة وقاعدة القانون.
لا تحفظ مفاتيح API في هذا الملف — استخدم st.secrets أو المتغيرات البيئية للمفاتيح.
"""
import os, json
from typing import Any
from datetime import datetime

DATA_DIR     = "fuehrer_data"
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
MEMORY_FILE  = os.path.join(DATA_DIR, "memory.json")
SETTINGS_FILE= os.path.join(DATA_DIR, "settings.json")
LAW_FILE     = os.path.join(DATA_DIR, "law_db.json")
BG_FILE      = os.path.join(DATA_DIR, "bg.b64")

for d in [DATA_DIR, SESSIONS_DIR]:
    os.makedirs(d, exist_ok=True)


def load_json(path: str, default: Any):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except json.JSONDecodeError:
        # ملف تالف: إرجاع القيمة الافتراضية
        pass
    except Exception:
        pass
    return default


def save_json(path: str, data: Any):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        # لا نرمي الاستثناء هنا — caller يجب أن يتعامل مع الأخطاء إن لزم
        print(f"save_json error: {e}")


def list_sessions():
    out = []
    try:
        for fname in sorted(os.listdir(SESSIONS_DIR), reverse=True):
            if fname.endswith(".json"):
                d = load_json(os.path.join(SESSIONS_DIR, fname), {})
                out.append({
                    "id":      fname.replace(".json", ""),
                    "name":    d.get("name", "جلسة"),
                    "count":   len(d.get("messages", [])),
                    "updated": d.get("updated", ""),
                })
    except Exception:
        pass
    return out


def load_session(sid: str):
    return load_json(os.path.join(SESSIONS_DIR, f"{sid}.json"),
                     {"name": "جلسة جديدة", "messages": []})


def save_session(sid: str, data: dict):
    data = data.copy()
    data["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_json(os.path.join(SESSIONS_DIR, f"{sid}.json"), data)


def delete_session(sid: str):
    p = os.path.join(SESSIONS_DIR, f"{sid}.json")
    if os.path.exists(p):
        os.remove(p)


def save_settings(settings: dict):
    # تأكد من عدم حفظ مفاتيح حساسة هنا
    safe = {k: v for k, v in settings.items() if k != "ai_key"}
    save_json(SETTINGS_FILE, safe)


def load_settings():
    return load_json(SETTINGS_FILE, {})


def save_memory(mem):
    save_json(MEMORY_FILE, mem)


def save_law(law_db):
    save_json(LAW_FILE, law_db)
