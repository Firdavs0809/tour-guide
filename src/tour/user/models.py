from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from tour.agency.models import TourPackage


class UserManager(BaseUserManager):
    def create_user(self, phone_number, first_name, password=None, is_staff=False,
                    is_active=True, **kwargs):
        user = self.model(first_name=first_name, phone_number=phone_number,
                          is_active=is_active, is_staff=is_staff, **kwargs)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password=None, **kwargs):
        return self.create_user(phone_number, '', password, is_staff=True, is_superuser=True, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    is_staff = models.BooleanField(default=False, )
    is_active = models.BooleanField(default=True, )
    lang = models.SmallIntegerField(default=1, )
    date_joined = models.DateTimeField(default=timezone.now, editable=False)

    USERNAME_FIELD = "phone_number"
    objects = UserManager()

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return self.first_name or self.phone_number or self.email

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]
        get_latest_by = "date_joined"


class Temp(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=200, blank=True, null=True, )
    last_name = models.CharField(max_length=200, blank=True, null=True, )
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    email = models.CharField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    verified = models.BooleanField(default=False, )
    verified_code = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = "user tem"
        verbose_name_plural = "Temp model"
        ordering = ["-created_at"]


class SmsManager(models.Manager):

    def create_sms(self, temp_id, phone_number, code, type):
        creation_args = {
            'temp_id': temp_id,
            'phone_number': phone_number,
            'code': code,
            'sms_type': type,
            'expires': timezone.now() + timedelta(seconds=600)
        }
        sms = self.create(**creation_args)
        return sms


class Sms(models.Model):
    temp = models.ForeignKey(Temp, null=True, blank=True,
                             related_name="user_sms",
                             on_delete=models.SET_NULL,
                             )
    sms_type = models.PositiveSmallIntegerField(null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    code = models.CharField(max_length=20, )
    is_active = models.BooleanField(default=False, null=False, blank=True)
    expires = models.DateTimeField()
    created_datetime = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, editable=False)
    objects = SmsManager()

    class Meta:
        verbose_name = "User sms"
        index_together = [
            ("phone_number", "code"),
        ]

    def __str__(self):
        return self.phone_number


class Profile(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name='profile')
    packages = models.ManyToManyField(TourPackage,)

    first_name = models.CharField(max_length=200, blank=True, null=True, )
    last_name = models.CharField(max_length=200, blank=True, null=True, )
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)

    profile_picture = models.CharField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.phone_number

    class Meta:
        verbose_name = 'profile'
