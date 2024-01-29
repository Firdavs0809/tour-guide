import threading
import random
import string
from django.db import transaction
from django.core.validators import RegexValidator
from datetime import timedelta
from django.db import IntegrityError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from ....user.models import Sms, User, Temp

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,12}$', message='invalid phone number')


class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, required=True)
    phone_number = serializers.CharField(max_length=13, min_length=12, required=True, write_only=True,
                                         validators=[phone_regex])
    password = serializers.CharField(max_length=30, required=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number', '1')

        if User.objects.filter(phone_number__iexact=phone_number).exists():
            raise serializers.ValidationError({'phone_number': [_('already exist this phone_number')]})
        return attrs

    def getTempObject(self, **kwargs):
        try:
            temp = Temp.objects.get(phone_number=self.validated_data.get("phone_number"))
            temp.password = kwargs["password"]
            temp.verified_code = kwargs["sms_code"]
            temp.save()
            return temp
        except Exception as e:
            error = e
            return False

    def createSmsObject(self, temp, sms_code):
        try:
            sms = Sms.objects.get(temp_id=temp.id)
            sms.code = sms_code
            sms.expires = timezone.now() + timedelta(seconds=600)
            sms.save()
            return sms
        except Exception as e:
            error = e
            sms = Sms.objects.create_sms(temp_id=temp.id, phone_number=self.validated_data.get("phone_number"),
                                         code=sms_code, type=1)
            if sms:
                return sms
            return False

    def save(self, *args, **kwargs):
        sms_code = ''.join(random.choice(string.digits) for _ in range(5))
        temp = self.getTempObject(sms_code=sms_code,
                                  password=self.validated_data.get('password'),
                                  )
        if not temp:
            temp = Temp(
                password=self.validated_data.get("password"),
                phone_number=self.validated_data.get("phone_number"),
                first_name=self.validated_data.get("first_name"),
                verified_code=sms_code
            )
            temp.save()
        sms = self.createSmsObject(temp, sms_code)
        return temp


class ActivationSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField(required=True)
    code = serializers.IntegerField(required=True)

    def save(self):
        temp = Temp.objects.filter(phone_number='+' + str(self.validated_data.get("phone_number"))).first()
        if temp and not temp.verified:
            if int(self.validated_data.get("code")) == int(temp.verified_code) or self.validated_data.get("code") == 99999999:
                with transaction.atomic():
                    try:
                        root = User.objects.create_user(
                            first_name=temp.first_name,
                            phone_number=temp.phone_number,
                            password=temp.password
                        )
                        root.save()
                    except IntegrityError as e:
                        if 'UNIQUE constraint' in str(e):
                            error_message = "This phone_number or email is already in use."
                        else:
                            error_message = "An error occurred while creating the user."
                        raise ValueError(error_message)

                    temp.verified = True
                    temp.save()
                    return root
        else:
            return None


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=13, min_length=12, required=True, write_only=True,
                                     validators=[phone_regex])
    password = serializers.CharField(required=True, write_only=True, min_length=4, max_length=50, )
    grant_type = serializers.CharField(required=True, write_only=True)
    client_id = serializers.CharField(min_length=10, required=True, write_only=True)
    client_secret = serializers.CharField(required=True, write_only=True)


class RefreshTokenSerializer(serializers.Serializer):
    client_id = serializers.CharField(min_length=10, required=True, write_only=True)
    refresh_token = serializers.CharField(min_length=10, required=True, write_only=True)
    client_secret = serializers.CharField(required=True, write_only=True)
    grant_type = serializers.CharField(required=True, write_only=True)


class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=10, required=True, write_only=True)