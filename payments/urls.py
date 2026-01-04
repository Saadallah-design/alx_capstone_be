# project/urls.py or payments/urls.py
from django.urls import path
from .views import CreateCheckoutSessionView, StripeWebhookView, InitiatePaymentView

urlpatterns = [
    # The endpoint for the Stripe CLI: localhost:8000/payments/webhook/
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    
    # Endpoint to initiate payment and get payment_uuid
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),

    # The endpoint React will call to start the payment
    path('create-session/<uuid:payment_uuid>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
]