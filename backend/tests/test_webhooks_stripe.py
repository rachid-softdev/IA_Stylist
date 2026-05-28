"""Tests for Stripe webhook metadata validation.

Covers the pure functions _safe_webhook_plan and _safe_webhook_credits
from app.routers.webhooks. These functions sanitize incoming metadata
from Stripe webhook events before they reach the database.

No DB or network access required — pure unit tests.
"""
import pytest
from app.routers.webhooks import _safe_webhook_plan, _safe_webhook_credits


class TestSafeWebhookPlan:
    """Test _safe_webhook_plan(plan) validation and sanitization.

    The function validates that the plan name from Stripe metadata
    is one of the known plans. Invalid/unknown plans fall back to "pro".
    """

    def test_valid_plan_free(self):
        assert _safe_webhook_plan("free") == "free"

    def test_valid_plan_pro(self):
        assert _safe_webhook_plan("pro") == "pro"

    def test_valid_plan_creator(self):
        assert _safe_webhook_plan("creator") == "creator"

    def test_valid_plan_starter(self):
        assert _safe_webhook_plan("starter") == "starter"

    def test_valid_plan_growth(self):
        assert _safe_webhook_plan("growth") == "growth"

    def test_valid_plan_enterprise(self):
        assert _safe_webhook_plan("enterprise") == "enterprise"

    def test_unknown_plan_falls_back_to_pro(self):
        """Any plan not in VALID_PLANS must return 'pro'."""
        assert _safe_webhook_plan("super_admin") == "pro"

    def test_unknown_plan_random_string(self):
        assert _safe_webhook_plan("unknown_plan_xyz") == "pro"

    def test_none_plan_falls_back_to_pro(self):
        assert _safe_webhook_plan(None) == "pro"

    def test_empty_string_falls_back_to_pro(self):
        assert _safe_webhook_plan("") == "pro"

    def test_case_sensitive_not_normalized(self):
        """The function does NOT lowercase the input — 'Pro' is not in VALID_PLANS."""
        assert _safe_webhook_plan("Pro") == "pro"  # Not in set, falls back


class TestSafeWebhookCredits:
    """Test _safe_webhook_credits(credits) validation and sanitization.

    The function converts input to int, clamps negative values to 0,
    and defaults None/invalid to 100.
    """

    def test_valid_credits_positive(self):
        assert _safe_webhook_credits(100) == 100

    def test_valid_credits_zero(self):
        assert _safe_webhook_credits(0) == 0

    def test_valid_credits_large(self):
        assert _safe_webhook_credits(9999) == 9999

    def test_negative_credits_clamped_to_zero(self):
        assert _safe_webhook_credits(-50) == 0

    def test_none_credits_returns_100(self):
        """None should default to 100 before any clamping."""
        assert _safe_webhook_credits(None) == 100

    def test_string_numeric_credits_converted(self):
        """Numeric string should be converted to int."""
        assert _safe_webhook_credits("50") == 50

    def test_string_numeric_negative_converted(self):
        """Negative numeric string should become 0 after max(..., 0)."""
        assert _safe_webhook_credits("-10") == 0

    def test_invalid_string_returns_100(self):
        """Non-numeric string should fall back to default 100."""
        assert _safe_webhook_credits("abc") == 100

    def test_invalid_string_with_numbers_returns_100(self):
        """Alphanumeric string should fall back to default 100."""
        assert _safe_webhook_credits("100abc") == 100

    def test_empty_string_returns_100(self):
        """Empty string should fall back to default 100."""
        assert _safe_webhook_credits("") == 100

    def test_float_credits_truncated(self):
        """Float should be truncated to int (int(100.7) = 100)."""
        assert _safe_webhook_credits(100.7) == 100

    def test_negative_float_clamped(self):
        """Negative float should become 0 after max(..., 0)."""
        assert _safe_webhook_credits(-0.5) == 0
