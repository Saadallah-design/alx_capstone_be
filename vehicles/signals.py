import cloudinary.uploader
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import VehicleImage

@receiver(post_delete, sender=VehicleImage)
def delete_image_from_cloudinary(sender, instance, **kwargs):
    """
    Triggers when a VehicleImage is deleted from the DB.
    Deletes the physical file from Cloudinary storage.
    """
    if instance.image:
        # In Cloudinary, instance.image.name is the 'public_id'
        # we need to tell Cloudinary to destroy it.
        try:
            cloudinary.uploader.destroy(instance.image.name, invalidate=True)
            print(f"Successfully deleted {instance.image.name} from Cloudinary")
        except Exception as e:
            print(f"Error deleting from Cloudinary: {e}")