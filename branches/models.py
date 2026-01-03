from django.db import models
from django.utils.text import slugify
from core.models import Agency


# a branch must belong to an agency as it stores geolocation data 
# used as a choice field or FK in the Booking model to standardize pickup and dropoff locations    
class Branch(models.Model):
    # Updated reference to 'core.Agency'
    agency = models.ForeignKey('core.Agency', on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100)

    # contact info
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    # location info
    city = models.CharField(max_length=100)
    address = models.TextField()
    country = models.CharField(max_length=100) # country in case of international locations
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Operating hours
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    is_active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)

    is_pickup_point = models.BooleanField(default=False)
    is_dropoff_point = models.BooleanField(default=False)

    # using a method for the slug 
    def save(self, *args, **kwargs):
        if not self.slug:
            #generate the slug from the name
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # now ensuring uniqueness by adding counter
            while Branch.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} - {self.agency.agency_name}"
