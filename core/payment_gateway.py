"""
MUCAMBO Nexus - Payment Gateway & Webhook Manager
Integrates Stripe & Mercado Pago to collect funds from global buyers before JIT source execution.
"""

import os
from typing import Dict, Any, Optional

class PaymentGateway:
    @classmethod
    def create_checkout_session(
        cls,
        opportunity_id: str,
        asset_title: str,
        price_usd: float,
        currency: str = "BRL",
        success_url: str = "https://mucambo-nexus.onrender.com/?success=true",
        cancel_url: str = "https://mucambo-nexus.onrender.com/?canceled=true"
    ) -> Dict[str, Any]:
        """Creates a real Stripe checkout session with local currency support."""
        stripe_key = os.getenv("STRIPE_SECRET_KEY")
        
        if stripe_key and stripe_key.startswith("sk_"):
            try:
                import stripe
                stripe.api_key = stripe_key
                
                # If BRL, convert from USD using reference rate
                from config import CURRENCY_RATES
                if currency.upper() == "BRL":
                    rate = CURRENCY_RATES.get("BRL", 5.65)
                    final_amount = round(price_usd * rate, 2)
                    unit_amount_cents = int(final_amount * 100)
                else:
                    currency = "USD"
                    unit_amount_cents = int(price_usd * 100)
                
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[{
                        "price_data": {
                            "currency": currency.lower(),
                            "unit_amount": unit_amount_cents,
                            "product_data": {
                                "name": f"MUCAMBO Ativo Digital: {asset_title}",
                                "description": "Entrega digital instantanea e verificada.",
                            },
                        },
                        "quantity": 1,
                    }],
                    mode="payment",
                    metadata={"opportunity_id": opportunity_id},
                    success_url=success_url,
                    cancel_url=cancel_url,
                )
                return {
                    "provider": "STRIPE",
                    "checkout_url": session.url,
                    "session_id": session.id,
                    "mode": "REAL"
                }
            except Exception as e:
                return {
                    "provider": "STRIPE_ERROR",
                    "error": str(e),
                    "mode": "ERROR"
                }

        # Fallback / Instant Mock URL for seamless testing
        return {
            "provider": "DIRECT_JIT_SETTLEMENT",
            "checkout_url": f"/?direct_fulfill={opportunity_id}",
            "mode": "MOCK_GATEWAY",
            "message": "Stripe key not defined in .env, using direct settlement gateway."
        }
