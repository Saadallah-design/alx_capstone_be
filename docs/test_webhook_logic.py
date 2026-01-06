import os
import django
import stripe
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carRentalConfig.settings')
django.setup()

from payments.models import Payment
from payments.views import StripeWebhookView

def test_manual_webhook_processing(payment_uuid):
    print(f"--- Testing Manual Webhook Processing for {payment_uuid} ---")
    
    try:
        payment = Payment.objects.get(uuid=payment_uuid)
        booking = payment.booking
        
        print(f"Initial Payment Status: {payment.status}")
        print(f"Initial Booking Status: {booking.booking_status}")
        
        # Mock a Stripe checkout session object
        mock_session = {
            'id': 'cs_test_mock',
            'payment_intent': 'pi_test_mock',
            'metadata': {'payment_uuid': str(payment_uuid)}
        }
        
        # We need to mock the stripe.PaymentIntent.retrieve call since we are using a mock ID
        import unittest.mock as mock
        with mock.patch('stripe.PaymentIntent.retrieve') as mock_retrieve:
            mock_intent = mock.MagicMock()
            mock_intent.status = 'succeeded'
            mock_intent.id = 'pi_test_mock'
            mock_retrieve.return_value = mock_intent
            
            # Manually call the internal processing method
            view = StripeWebhookView()
            view._process_payment_success(str(payment_uuid), mock_session)
            
        # Refresh from DB
        payment.refresh_from_db()
        booking.refresh_from_db()
        
        print(f"Updated Payment Status: {payment.status}")
        print(f"Updated Booking Status: {booking.booking_status}")
        
        if booking.booking_status == 'CONFIRMED' and payment.status == 'COMPLETED':
            print("SUCCESS: Signal and Webhook logic are functional.")
        else:
            print("FAILURE: Statuses did not update as expected.")
            
    except Payment.DoesNotExist:
        print(f"Error: Payment with UUID {payment_uuid} not found.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_manual_webhook_processing(sys.argv[1])
    else:
        print("Usage: python3 test_webhook_logic.py <payment_uuid>")
