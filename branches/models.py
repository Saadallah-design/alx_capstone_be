from django.db import models

# used as a choice field or FK in the Booking model to standardize pickup and dropoff locations    
class Location(models.Model):
    # Updated reference to 'core.Agency'
    agency = models.ForeignKey('core.Agency', on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)
    address = models.TextField()

    is_pickup_point = models.BooleanField(default=False)
    is_dropoff_point = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.agency.agency_name}"
