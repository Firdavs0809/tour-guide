from django.db.models.signals import post_save
from .models import Profile, User


def profile_create(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            phone_number=instance.phone_number,
            email=instance.email,
        )
        # send welcome email


def user_update(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user
    if not created:
        user.phone_number = profile.phone_number
        user.email = profile.phone_number
        user.first_name = profile.first_name
        user.last_name = profile.last_name
        user.save()


post_save.connect(profile_create, User)
post_save.connect(user_update, Profile)
