import { NextResponse } from "next/server";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || "sk_test_placeholder", {
  apiVersion: "2024-12-18.acacia",
});

const tierPrices = {
  Starter: { priceId: "price_starter_24", amount: 2400 },
  Pro: { priceId: "price_pro_75", amount: 7500 },
  Enterprise: { priceId: "price_enterprise_150", amount: 15000 },
};

export async function POST(request) {
  try {
    const body = await request.json();
    const { tier, email, successUrl, cancelUrl } = body;

    if (!tier || !tierPrices[tier]) {
      return NextResponse.json(
        { error: "Invalid tier. Choose Starter, Pro, or Enterprise." },
        { status: 400 }
      );
    }

    // Create Stripe checkout session for subscription
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],
      mode: "subscription",
      customer_email: email || undefined,
      line_items: [
        {
          price_data: {
            currency: "usd",
            unit_amount: tierPrices[tier].amount,
            recurring: { interval: "month" },
            product_data: {
              name: `SentinelAPI ${tier}`,
              description: `SentinelAPI ${tier} plan - monthly subscription`,
            },
          },
          quantity: 1,
        },
      ],
      success_url: successUrl || `${process.env.NEXT_PUBLIC_APP_URL}/pricing?success=true`,
      cancel_url: cancelUrl || `${process.env.NEXT_PUBLIC_APP_URL}/pricing?canceled=true`,
    });

    return NextResponse.json({ sessionId: session.id, url: session.url });
  } catch (error) {
    console.error("Stripe checkout error:", error);
    return NextResponse.json(
      { error: error.message || "Failed to create checkout session" },
      { status: 500 }
    );
  }
}