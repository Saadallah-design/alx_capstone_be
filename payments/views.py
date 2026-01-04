import stripe
from decimal import Decimal
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

from .models import Payment
from rentals.models import Booking

# Initialize Stripe with your secret key
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@method_decorator(csrf_exempt, name='dispatch')
class CreateCheckoutSessionView(View):
    """
    Initiates the Stripe Checkout process.
    """
    def post(self, request, payment_uuid):
        # 1. Fetch our local payment record
        payment = get_object_or_404(Payment, uuid=payment_uuid)
        booking = payment.booking

        # 2. Determine if we are doing a "Hold" or a "Capture"
        # Security deposits use 'manual' capture so we don't take the money yet
        capture_method = 'manual' if payment.payment_type == 'SECURITY_DEPOSIT' else 'automatic'

        try:
            # Fix Precision: Use Decimal for amount calculation
            unit_amount = int(payment.amount * Decimal('100'))

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': payment.currency.lower(),
                        'product_data': {
                            'name': f"{payment.get_payment_type_display()} - Booking #{booking.id}",
                            'description': f"Vehicle: {booking.vehicle.make} {booking.vehicle.model}",
                        },
                        'unit_amount': unit_amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                payment_intent_data={
                    'capture_method': capture_method,
                    'metadata': {'payment_uuid': str(payment.uuid)},
                },
                # Metadata links this Stripe Session back to our DB record
                metadata={'payment_uuid': str(payment.uuid)},
                success_url=settings.SITE_URL + f"/rentals/booking/{booking.id}/success/",
                cancel_url=settings.SITE_URL + f"/rentals/booking/{booking.id}/cancel/",
            )
            # Returning JSON instead of redirect allows the frontend to handle the transition
            return JsonResponse({'checkout_url': session.url})
        except Exception as e:
            logger.error(f"Error creating Stripe checkout session: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """
    Listens for Stripe events to update Payment and Booking statuses.
    """
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            # Invalid payload or signature
            return HttpResponse(status=400)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            payment_uuid = session.get('metadata', {}).get('payment_uuid')
            if payment_uuid:
                self._process_payment_success(payment_uuid, session)

        elif event['type'] == 'payment_intent.payment_failed':
            intent = event['data']['object']
            payment_uuid = intent.get('metadata', {}).get('payment_uuid')
            if payment_uuid:
                self._process_payment_failure(payment_uuid, intent)

        elif event['type'] == 'charge.refunded':
            charge = event['data']['object']
            # Refunds might not have our metadata if done via Dashboard, but we can try to find the payment
            intent_id = charge.get('payment_intent')
            if intent_id:
                self._process_refund(intent_id, charge)

        else:
            logger.info(f"Unhandled Stripe event type: {event['type']}")

        return HttpResponse(status=200)

    def _process_payment_success(self, payment_uuid, session):
        try:
            payment = Payment.objects.get(uuid=payment_uuid)
            intent_id = session.get('payment_intent')
            intent = stripe.PaymentIntent.retrieve(intent_id)

            if intent.status == 'requires_capture':
                payment.status = 'AUTHORIZED'
            else:
                payment.status = 'COMPLETED'

            payment.provider_transaction_id = intent_id
            payment.gateway_response_raw = session
            payment.save()
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for UUID: {payment_uuid}")
        except Exception as e:
            logger.error(f"Error processing payment success: {str(e)}")

    def _process_payment_failure(self, payment_uuid, intent):
        try:
            payment = Payment.objects.get(uuid=payment_uuid)
            payment.status = 'FAILED'
            payment.gateway_response_raw = intent
            payment.save()
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for failure UUID: {payment_uuid}")

    def _process_refund(self, intent_id, charge):
        try:
            payments = Payment.objects.filter(provider_transaction_id=intent_id)
            for payment in payments:
                payment.status = 'REFUNDED'
                payment.save()
        except Exception as e:
            logger.error(f"Error processing refund for intent {intent_id}: {str(e)}")