from django.db import models
from django.utils import timezone

#this one stores the business details of the rental company. 
# the oentoone link ensures only one agency profile per agency user account
class Agency(models.Model):
    CITY_CHOICES = [
        ('PATONG', 'Patong'),
        ('KATA', 'Kata'),
        ('KARON', 'Karon'),
        ('PHUKET_TOWN', 'Phuket Town'),
        ('KAMALA', 'Kamala'),
        ('BANG_TAO', 'Bang Tao'),
        ('RAWAI', 'Rawai'),
        ('CHALONG', 'Chalong'),
    ]
    # Updated reference to 'users.User'
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='agency_profile')
    agency_name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=100)
    city = models.CharField(max_length=50, choices=CITY_CHOICES, default='PATONG')

    is_verified = models.BooleanField(default=False)
    verification_note = models.TextField(null=True, blank=True)
    verification_date = models.DateTimeField(null=True, blank=True)

    submitted_on = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.agency_name
