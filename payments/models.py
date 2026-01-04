import uuid
from django.db import models

class Payment(models.Model):
    payment_status_choices = [
        ('PENDING', 'Pending'),
        ('AUTHORIZED', 'Authorized'), # For security deposits (hold on card)
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('PARTIALLY_REFUNDED', 'Partially Refunded'),
    ]

    payment_type_choices = [
        ('RENTAL_FEE', 'Rental Fee'),
        ('SECURITY_DEPOSIT', 'Security Deposit'),
        ('LATE_FEE', 'Late Fee'),
        ('DAMAGE_CHARGE', 'Damage Charge'),
    ]

    # Use UUID for public-facing references (more secure than ID numbers)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    booking = models.ForeignKey(
        'rentals.Booking', 
        on_delete=models.PROTECT, 
        related_name='payments'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD') 
    
    # Tracking the type of payment
    payment_type = models.CharField(max_length=20, choices=payment_type_choices, default='RENTAL_FEE')
    status = models.CharField(max_length=20, choices=payment_status_choices, default='PENDING')

    # Gateway Data
    provider = models.CharField(max_length=50) # Payment gateway provider 'Stripe', 'PayPal'
    provider_transaction_id = models.CharField(max_length=255, unique=True, db_index=True) # this one for tracking history of gateways
    
    # Useful for debugging/audit logs: it is good to keep raw logs
    gateway_response_raw = models.JSONField(null=True, blank=True) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.payment_type} - {self.amount} {self.currency} ({self.status})"