# utils.py
"""
مجموعات مساعدة عامة المستخدمة عبر التطبيق.
"""
from datetime import datetime
import io, re


def _bytes(f):
    """Return bytes for a file-like or bytes object."""
    if hasattr(f, "getvalue"):
        return f.getvalue()
    try:
        p = f.tell(); d = f.read(); f.seek(p); return d
    except Exception:
        return f.read()


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip()


def new_sid() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")
