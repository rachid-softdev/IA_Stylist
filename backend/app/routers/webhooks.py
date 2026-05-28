from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.models.processed_event import ProcessedEvent
from app.services.credits import CreditService

VALID_PLANS = {"free", "pro", "creator", "starter", "growth", "enterprise"}
MAX_WEBHOOK_CREDITS = 1_000_000


def _safe_webhook_plan(plan: str | None) -> str:
    """Validate and sanitize plan from Stripe metadata."""
    if plan not in VALID_PLANS:
        return "pro"
    return plan


def _safe_webhook_credits(credits: str | int | None) -> int:
    """Validate and sanitize credits from Stripe metadata.

    Stripe metadata values are always strings, but the default
    may be an int, hence str | int | None.
    """
    try:
        credits_int = int(credits if credits is not None else 100)
    except (TypeError, ValueError):
        credits_int = 100
    return max(0, min(credits_int, MAX_WEBHOOK_CREDITS))


settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhook events (idempotent via two-phase commit)."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return JSONResponse(
            status_code=400,
            content={"data": None, "error": {"code": "INVALID_SIGNATURE", "message": "Invalid Stripe signature"}},
        )

    event_type = event["type"]
    event_id = event["id"]
    data = event["data"]["object"]
    credit_service = CreditService(db)

    # Phase 1: Register the event as processing (independent transaction)
    try:
        processed = ProcessedEvent(
            event_id=event_id,
            event_type=event_type,
            status="processing",
            processed_at=datetime.now(timezone.utc),
        )
        db.add(processed)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return {"status": "ignored_duplicate", "event_id": event_id}

    # Phase 2: Process credits/plans in a new transaction
    try:
        match event_type:
            case "customer.subscription.created":
                customer_id = data.get("customer")
                if customer_id:
                    metadata = data.get("metadata", {})
                    user_id = metadata.get("user_id")
                    plan = _safe_webhook_plan(metadata.get("plan", "pro"))
                    credits = _safe_webhook_credits(metadata.get("credits", 100))

                    if user_id:
                        result = await db.execute(select(User).where(User.id == user_id))
                        user = result.scalar_one_or_none()
                        if user:
                            user.plan = plan
                            await credit_service.add_credits(
                                user_id, credits, "purchase", f"Subscription: {plan}"
                            )

            case "customer.subscription.deleted":
                customer_id = data.get("customer")
                if customer_id:
                    metadata = data.get("metadata", {})
                    user_id = metadata.get("user_id")
                    if user_id:
                        result = await db.execute(select(User).where(User.id == user_id))
                        user = result.scalar_one_or_none()
                        if user:
                            user.plan = "free"

            case "customer.subscription.updated":
                customer_id = data.get("customer")
                if customer_id:
                    metadata = data.get("metadata", {})
                    user_id = metadata.get("user_id")
                    plan_value = metadata.get("plan")
                    if user_id and plan_value:
                        new_plan = _safe_webhook_plan(plan_value)
                        result = await db.execute(select(User).where(User.id == user_id))
                        user = result.scalar_one_or_none()
                        if user:
                            user.plan = new_plan

            case "invoice.payment_succeeded":
                customer_id = data.get("customer")
                if customer_id:
                    metadata = data.get("metadata", {})
                    user_id = metadata.get("user_id")
                    credits = _safe_webhook_credits(metadata.get("credits", 100))
                    if user_id:
                        await credit_service.add_credits(
                            user_id, credits, "purchase", "Monthly credit renewal"
                        )

            case "invoice.payment_failed":
                pass

        # After processing, update status to completed
        await db.execute(
            update(ProcessedEvent)
            .where(ProcessedEvent.event_id == event_id)
            .values(status="completed")
        )
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return {"status": "ok"}
