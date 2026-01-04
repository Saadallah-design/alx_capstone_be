# payments/signals.py
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Payment)
def update_booking_on_payment(sender, instance, created, **kwargs):
    """
    Automatically confirms the booking when the rental fee is paid.
    """
    if instance.status == 'COMPLETED' and instance.payment_type == 'RENTAL_FEE':
        try:
            booking = instance.booking
            if booking.booking_status != 'CONFIRMED':
                booking.booking_status = 'CONFIRMED'
                booking.save()
        except Exception as e:
            logger.error(f"Failed to auto-confirm booking {instance.booking.id} after payment: {str(e)}")