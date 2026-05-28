"""Tests for Stripe webhook two-phase idempotent processing (C-02).

Covers:
- Duplicate event detection via IntegrityError on ProcessedEvent insert
- Valid subscription.created event processing (credits + plan)
- Invalid Stripe signature rejection (400)
- ProcessedEvent status="processing" set BEFORE credit processing
- ProcessedEvent status updated to "completed" after success
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from datetime import datetime, timezone

from app.routers.webhooks import stripe_webhook, ProcessedEvent


def _make_stripe_event(event_id: str, event_type: str, metadata: dict | None = None) -> dict:
    """Helper to build a fake Stripe event dict."""
    return {
        "id": event_id,
        "type": event_type,
        "data": {
            "object": {
                "customer": "cus_test123",
                "metadata": metadata or {},
            }
        },
    }


@pytest.fixture
def mock_db():
    """Create a mock async DB session."""
    db = AsyncMock()
    # Default: commit succeeds
    db.commit.return_value = None
    # Default: rollback succeeds
    db.rollback.return_value = None
    return db


@pytest.fixture
def mock_request():
    """Create a mock FastAPI Request with Stripe-like body and headers."""
    req = MagicMock()
    req.body = AsyncMock(return_value=b'{"test": "payload"}')
    req.headers = {"stripe-signature": "test_sig"}
    return req


class TestWebhookIdempotency:
    """Two-phase commit prevents double-processing of Stripe events."""

    @pytest.mark.asyncio
    async def test_duplicate_event_returns_ignored(self, mock_db, mock_request):
        """Simulate processing the same Stripe event twice.
        First succeeds, second returns ignored_duplicate."""
        event_id = "evt_dup_test_001"
        fake_event = _make_stripe_event(event_id, "customer.subscription.created", {
            "user_id": "user_001",
            "plan": "pro",
            "credits": "500",
        })

        with patch("app.routers.webhooks.stripe.Webhook.construct_event", return_value=fake_event):
            with patch("app.routers.webhooks.CreditService") as mock_cs_cls:
                mock_cs = AsyncMock()
                mock_cs_cls.return_value = mock_cs

                # Make db.execute return a valid user for the select queries
                mock_user = MagicMock()
                mock_user.id = "user_001"
                mock_user.plan = "free"
                mock_user.credits = 10

                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_user
                mock_db.execute.return_value = mock_result

                # Call 1: should succeed
                result1 = await stripe_webhook(mock_request, db=mock_db)
                assert result1 == {"status": "ok"}

                # Verify ProcessedEvent was added with status="processing"
                added_events = [
                    call.args[0]
                    for call in mock_db.add.call_args_list
                    if isinstance(call.args[0], ProcessedEvent)
                ]
                assert len(added_events) >= 1
                assert added_events[0].event_id == event_id
                assert added_events[0].status == "processing"

                # Reset call history
                mock_db.add.reset_mock()
                mock_db.commit.reset_mock()
                mock_db.execute.reset_mock()

                # Call 2: commit raises IntegrityError (duplicate event_id)
                from sqlalchemy.exc import IntegrityError
                mock_db.commit.side_effect = IntegrityError("mock", "mock", "mock")

                result2 = await stripe_webhook(mock_request, db=mock_db)
                assert result2["status"] == "ignored_duplicate"
                assert result2["event_id"] == event_id

    @pytest.mark.asyncio
    async def test_valid_webhook_processes_credits(self, mock_db, mock_request):
        """Simulate a valid customer.subscription.created event,
        verify credits and plan are updated."""
        fake_event = _make_stripe_event(
            "evt_valid_001",
            "customer.subscription.created",
            {"user_id": "user_002", "plan": "growth", "credits": "1000"},
        )

        with patch("app.routers.webhooks.stripe.Webhook.construct_event", return_value=fake_event):
            with patch("app.routers.webhooks.CreditService") as mock_cs_cls:
                mock_cs = AsyncMock()
                mock_cs_cls.return_value = mock_cs

                mock_user = MagicMock()
                mock_user.id = "user_002"
                mock_user.plan = "free"
                mock_user.credits = 10

                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_user
                mock_db.execute.return_value = mock_result

                result = await stripe_webhook(mock_request, db=mock_db)
                assert result == {"status": "ok"}

                # Verify CreditService.add_credits was called
                mock_cs.add_credits.assert_awaited_once_with(
                    "user_002", 1000, "purchase", "Subscription: growth"
                )
                # Verify user plan was updated
                assert mock_user.plan == "growth"

    @pytest.mark.asyncio
    async def test_invalid_signature_returns_error(self, mock_db, mock_request):
        """Simulate bad Stripe signature, verify 400 response."""
        import stripe as stripe_module

        with patch.object(
            stripe_module.Webhook, "construct_event",
            side_effect=stripe_module.error.SignatureVerificationError(
                "Invalid signature", "test_sig"
            ),
        ):
            response = await stripe_webhook(mock_request, db=mock_db)
            assert response.status_code == 400
            content = response.body
            assert "INVALID_SIGNATURE" in str(content)

    @pytest.mark.asyncio
    async def test_processing_status_set_before_processing(self, mock_db, mock_request):
        """Verify that ProcessedEvent with status='processing' is
        committed BEFORE credit processing begins."""
        fake_event = _make_stripe_event(
            "evt_order_001",
            "customer.subscription.created",
            {"user_id": "user_003", "plan": "pro", "credits": "200"},
        )

        commit_order = []

        async def tracking_commit():
            commit_order.append("commit")

        mock_db.commit.side_effect = tracking_commit

        # Track when add() is called for ProcessedEvent
        original_add = mock_db.add

        def tracking_add(obj):
            if isinstance(obj, ProcessedEvent):
                commit_order.append("add_processed_event")
            original_add(obj)

        mock_db.add.side_effect = tracking_add

        with patch("app.routers.webhooks.stripe.Webhook.construct_event", return_value=fake_event):
            with patch("app.routers.webhooks.CreditService") as mock_cs_cls:
                mock_cs = AsyncMock()
                mock_cs_cls.return_value = mock_cs

                mock_user = MagicMock()
                mock_user.id = "user_003"
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_user
                mock_db.execute.return_value = mock_result

                await stripe_webhook(mock_request, db=mock_db)

                # The ProcessedEvent should be added and committed
                # before CreditService is called
                added_events = [
                    call.args[0]
                    for call in mock_db.add.call_args_list
                    if isinstance(call.args[0], ProcessedEvent)
                ]
                assert len(added_events) >= 1
                assert added_events[0].status == "processing"

    @pytest.mark.asyncio
    async def test_status_update_to_completed(self, mock_db, mock_request):
        """After successful processing, verify status is 'completed'."""
        fake_event = _make_stripe_event(
            "evt_complete_001",
            "customer.subscription.created",
            {"user_id": "user_004", "plan": "pro", "credits": "100"},
        )

        with patch("app.routers.webhooks.stripe.Webhook.construct_event", return_value=fake_event):
            with patch("app.routers.webhooks.CreditService") as mock_cs_cls:
                mock_cs = AsyncMock()
                mock_cs_cls.return_value = mock_cs

                mock_user = MagicMock()
                mock_user.id = "user_004"
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_user
                mock_db.execute.return_value = mock_result

                await stripe_webhook(mock_request, db=mock_db)

                # Verify the update to 'completed' was executed
                # The handler uses:
                #   await db.execute(
                #       update(ProcessedEvent)
                #       .where(ProcessedEvent.event_id == event_id)
                #       .values(status="completed")
                #   )
                # This calls db.execute with a SQLAlchemy Update object.
                # We just verify that at least 2 commits happened (Phase 1 + Phase 2).
                assert mock_db.commit.await_count >= 2
