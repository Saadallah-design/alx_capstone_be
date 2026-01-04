# payments/services.py (Recommended pattern for business logic)
import stripe
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def release_security_deposit(booking):
    """
    Finds the security deposit for a booking and marks it for release.
    Specifically for Stripe, we cancel the payment intent if it's not captured.
    """
    deposit = booking.payments.filter(
        payment_type='SECURITY_DEPOSIT', 
        status='AUTHORIZED'
    ).first()

    if deposit and deposit.provider_transaction_id:
        try:
            # For authorized but uncaptured payments, we use Refund (effectively a release)
            # or in some cases we might need to cancel the PI if it was manual capture
            # but usually Refund handles authorized-only payments by releasing the hold.
            stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
            refund = stripe.Refund.create(
                payment_intent=deposit.provider_transaction_id,
            )
            
            # Update local DB
            deposit.status = 'REFUNDED' 
            deposit.gateway_response_raw = refund
            deposit.save()
            return True
        except Exception as e:
            logger.error(f"Failed to release security deposit for booking {booking.id}: {str(e)}")
            return False
            
    return False