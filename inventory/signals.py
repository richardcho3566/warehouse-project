from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a default profile for new users.

    get_or_create() is used so signup code, admin-created users, and future
    import scripts do not collide with each other.
    """

    if created:
        Profile.objects.get_or_create(user=instance, defaults={"grade": "GRADE1"})
