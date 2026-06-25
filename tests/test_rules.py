# tests/test_rules.py
import pytest
from rules_engine import eval_simple_condition, eval_rule_v2


def test_flag_true():
    ctx = {"no_investigation": True}
    assert eval_simple_condition("no_investigation", ctx) is True


def test_is_true_false():
    ctx = {"settlement_offer": True}
    assert eval_simple_condition("settlement_offer is True", ctx) is True
    assert eval_simple_condition("settlement_offer is False", ctx) is False


def test_numeric_compare():
    ctx = {"days_abandoned": 40}
    assert eval_simple_condition("days_abandoned>30", ctx) is True
    assert eval_simple_condition("days_abandoned<=30", ctx) is False


def test_combined_and():
    ctx = {"settlement_offer": True, "risk_score": 70}
    assert eval_rule_v2("settlement_offer is True and risk_score>60", ctx) is True
    assert eval_rule_v2("settlement_offer is True and risk_score>80", ctx) is False
