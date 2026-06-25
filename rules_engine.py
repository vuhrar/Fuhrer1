# rules_engine.py
"""
محرك القواعد: يحتوي على RULES ودوال التقييم الآمنة.
"""
import re, operator
from typing import List, Dict

RULES = [
    {"c":"days_abandoned>30","o":"⚠️ انقطاع >30 يوم (ترك العمل)","cat":"عمل"},
    {"c":"days_abandoned>15 and days_abandoned<=30","o":"⚠️ انقطاع 15-30 يوم (إنذار)","cat":"عمل"},
    {"c":"days_since_firing>365","o":"⛔ مضى >سنة على الفصل (سقط حق التقاضي)","cat":"تقادم"},
    {"c":"days_since_firing>180 and days_since_firing<=365","o":"⏳ مضى >6 أشهر (تقادم جزئي)","cat":"تقادم"},
    {"c":"no_investigation","o":"⚖️ فصل بلا تحقيق (بطلان القرار)","cat":"إجراءات"},
    {"c":"arbitrary_dismissal","o":"⚖️ فصل تعسفي (تعويض واجب)","cat":"عمل"},
    {"c":"salary_delay","o":"⚖️ تأخير الراتب (تعويض)","cat":"عمل"},
    {"c":"eosb_not_paid","o":"⚖️ مكافأة نهاية الخدمة لم تُصرف","cat":"عمل"},
    {"c":"unlawful_deduction","o":"⚖️ خصم بغير حق (يُرد)","cat":"عمل"},
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
    {"c":"forgery_proven","o":"🚨 تزوير مثبت (جريمة جنائية)","cat":"مستندات"},
    {"c":"opponent_hides_doc","o":"⚖️ الخصم يخفي مستنداً (يُحكم ضده)","cat":"مستندات"},
    {"c":"new_evidence_late","o":"📌 أدلة جديدة بعد الميعاد (مقبولة)","cat":"مستندات"},
    {"c":"settlement_offer is True and risk_score>60","o":"🤝 الصلح أفضل من التقاضي","cat":"صلح"},
    {"c":"settlement_offer is True and risk_score<=40","o":"⚖️ الصلح ممكن والقضية قوية","cat":"صلح"},
    {"c":"settlement_broken","o":"⚖️ نقض الصلح (تعويض واجب)","cat":"صلح"},
    {"c":"offer_rejected_by_opponent","o":"📌 رفض الخصم الصلح (تعويض لك)","cat":"صلح"},
    {"c":"reply_delay>30","o":"⏳ تأخير إداري >30 يوم (تعنت)","cat":"تأخير"},
    {"c":"ambiguous_count>3","o":"🔍 عبارات غامضة (طعن محتمل)","cat":"لغوي"},
    {"c":"contradictions>1","o":"⚡ تناقض في مراسلات الخصم","cat":"تناقضات"},
    {"c":"force_majeure is True and days_abandoned>60","o":"📌 عذر قاهر يبرر الانقطاع","cat":"أعذار"},
    {"c":"proven_illness","o":"📌 مرض مثبت (عذر مقبول)","cat":"أعذار"},
    {"c":"natural_disaster","o":"📌 كارثة طبيعية (قوة قاهرة)","cat":"أعذار"},
    {"c":"travel_ban","o":"📌 منع السفر (قوة قاهرة)","cat":"أعذار"},
    {"c":"death_of_relative","o":"📌 وفاة قريب (إجازة رسمية)","cat":"أعذار"},
    {"c":"disproportionate_fine","o":"⚖️ غرامة غير متناسبة (تُخفَّض)","cat":"غرامات"},
    {"c":"fine_illegal","o":"⚖️ غرامة مخالفة للنظام (تُلغى)","cat":"غرامات"},
    {"c":"supreme_court_ruling","o":"⭐ سابقة من المحكمة العليا","cat":"سوابق"},
    {"c":"expert_request_denied","o":"⚖️ رفض الخبرة (إخلال بحق الدفاع)","cat":"إجراءات"},
    {"c":"non_judicial_acknowledgment","o":"📌 إقرار غير قضائي (حجة على المُقِر)","cat":"مستندات"},
    {"c":"opponent_threatens","o":"⚖️ تهديد متكرر (تعسف)","cat":"سلوك"},
    {"c":"witnesses_conflict","o":"⚖️ تناقض الشهود (تُرجح الأعدل)","cat":"شهادات"},
    {"c":"two_vs_one_witness","o":"📌 شاهدان ضد واحد (مقبول)","cat":"شهادات"},
    {"c":"no_registered_letter","o":"⚖️ تبليغ بغير بريد مسجل","cat":"إجراءات"},
]

OPS = {">": operator.gt, ">=": operator.ge, "<": operator.lt, "<=": operator.le, "==": operator.eq, "!=": operator.ne}


def eval_simple_condition(cond: str, ctx: dict) -> bool:
    cond = cond.strip()
    # flag (مثل: no_investigation)
    if re.fullmatch(r"[A-Za-z_]\w*$", cond):
        return bool(ctx.get(cond, False))
    # is True/False
    m = re.match(r"^([A-Za-z_]\w*)\s+is\s+(True|False)$", cond)
    if m:
        return bool(ctx.get(m.group(1), False)) == (m.group(2) == "True")
    # numeric comparison
    m = re.match(r"^([A-Za-z_]\w*)\s*(>=|<=|>|<|==|!=)\s*([0-9]+(?:\.[0-9]+)?)$", cond)
    if m:
        lhs = float(ctx.get(m.group(1), 0))
        rhs = float(m.group(3))
        return OPS[m.group(2)](lhs, rhs)
    # string equality like field == 'value'
    m = re.match(r"^([A-Za-z_]\w*)\s*==\s*'([^']*)'$", cond)
    if m:
        return str(ctx.get(m.group(1), "")) == m.group(2)
    return False


def eval_rule_v2(expression: str, ctx: dict) -> bool:
    parts = [p.strip() for p in expression.split(" and ") if p.strip()]
    return all(eval_simple_condition(p, ctx) for p in parts)


def apply_rules(ctx: dict, rules=RULES) -> List[Dict]:
    return [{"text": r["o"], "cat": r["cat"]} for r in rules if eval_rule_v2(r["c"], ctx)]
