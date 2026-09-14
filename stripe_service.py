"""
stripe_service.py - Handles Stripe Checkout Sessions
"""
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

# Set your Stripe Secret Key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


def create_checkout_session(user_email, user_id, success_url, cancel_url):
    """
    Creates a Stripe Checkout Session for the Pro Subscription.
    """
    try:
        # Create a checkout session (One-time payment for testing simplicity)
        # In production, you would use 'subscription' mode with a Price ID
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'AI Assistant Pro - Lifetime Access',
                        'description': 'Unlock all AI features, unlimited posts, and premium support.',
                    },
                    'unit_amount': 2900, # $29.00 in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=user_email,
            metadata={'user_id': user_id}
        )
        return session.url
    except Exception as e:
        print(f"❌ Stripe Error: {e}")
        return None