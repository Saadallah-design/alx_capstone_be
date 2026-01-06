from rest_framework import serializers


class InitiatePaymentSerializer(serializers.Serializer):
    """Serializer for initiating a payment"""
    booking_id = serializers.IntegerField(required=True, help_text="ID of the booking to pay for")
    payment_type = serializers.ChoiceField(
        choices=['RENTAL_FEE', 'SECURITY_DEPOSIT'],
        default='RENTAL_FEE',
        help_text="Type of payment"
    )


class PaymentResponseSerializer(serializers.Serializer):
    """Serializer for payment initiation response"""
    payment_uuid = serializers.UUIDField(help_text="UUID of the created/existing payment")
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Payment amount")
    currency = serializers.CharField(max_length=3, help_text="Currency code (e.g., USD)")
    status = serializers.ChoiceField(
        choices=['CREATED', 'EXISTING'],
        help_text="Status indicating if payment was newly created or already existed"
    )
