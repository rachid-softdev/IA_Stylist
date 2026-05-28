import stripe
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.services.credits import CreditService

VALID_PLANS = {"free", "pro", "creator", "starter", "growth", "enterprise"}


def _safe_webhook_plan(plan: str | None) -> str:
    """Validate and sanitize plan from Stripe metadata."""
    if plan not in VALID_PLANS:
        return "pro"
    return plan


def _safe_webhook_credits(credits: int | None) -> int:
    """Validate and sanitize credits from Stripe metadata."""
    try:
        credits_int = int(credits if credits is not None else 100)
    except (TypeError, ValueError):
        credits_int = 100
    return max(credits_int, 0)


settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return {"error": "Invalid signature"}, 400

    event_type = event["type"]
    data = event["data"]["object"]
    credit_service = CreditService(db)

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

    await db.commit()
    return {"status": "ok"}
