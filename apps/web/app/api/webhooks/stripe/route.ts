import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET || ''

function getStripe() {
  const key = process.env.STRIPE_SECRET_KEY
  if (!key) throw new Error('STRIPE_SECRET_KEY is not set')
  return new Stripe(key, { apiVersion: '2026-05-27.dahlia' })
}

export async function POST(request: NextRequest) {
  const body = await request.text()
  const signature = request.headers.get('stripe-signature') || ''

  try {
    getStripe().webhooks.constructEvent(body, signature, webhookSecret)

    // Forward to backend
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/webhooks/stripe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'stripe-signature': signature,
      },
      body,
    })

    return NextResponse.json({ received: true })
  } catch (err) {
    return NextResponse.json({ error: 'Webhook error' }, { status: 400 })
  }
}
