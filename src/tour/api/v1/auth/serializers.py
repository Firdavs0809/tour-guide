import random
import string

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.core.validators import RegexValidator
from datetime import timedelta
from django.db import IntegrityError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ....user.models import Sms, User, Temp

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,12}$', message='invalid phone number')


class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, required=False)
    phone_number = serializers.CharField(max_length=13, min_length=12, required=True, write_only=True,
                                         validators=[phone_regex])
    password = serializers.CharField(max_length=30, required=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number', '1')
        return attrs

    def getTempObject(self, **kwargs):
        try:
            temp = Temp.objects.get(phone_number=self.validated_data.get("phone_number"))
            temp.password = kwargs["password"]
            temp.verified_code = kwargs["sms_code"]
            temp.verified = False
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
                first_name=self.validated_data.get("first_name", None),
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
        if not temp:
            raise ValidationError({'success': False, 'message': _("User with that number not registered.")})
        if temp.verified:
            raise ValidationError({'success': False, 'message': _("User account already activated.")})
        if temp and not temp.verified:
            if int(self.validated_data.get("code")) == int(temp.verified_code) or self.validated_data.get(
                    "code") == 99999:
                with transaction.atomic():
                    try:
                        (root, created) = User.objects.get_or_create(
                            phone_number=temp.phone_number
                        )
                        if created:
                            root.first_name = temp.first_name
                        root.set_password(temp.password)
                        root.save()
                    except IntegrityError as e:
                        print(e)
                        if 'UNIQUE constraint' in str(e):
                            error_message = "This phone_number or email is already in use."
                        else:
                            error_message = "An error occurred while creating the user."
                        raise ValidationError(error_message)

                    temp.verified = True
                    temp.save()
                    return root
            else:
                raise ValidationError({'success': False, 'message': _("Code is invalid. Please check from SMS.")})
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


class ForgetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13, min_length=12, required=True, write_only=True,
                                         validators=[phone_regex])

    def getTempObject(self, **kwargs):
        try:
            temp = Temp.objects.get(phone_number=self.validated_data.get("phone_number"))
            temp.password = kwargs["password"]
            temp.verified_code = kwargs["sms_code"]
            temp.verified = False
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

    def save(self, **kwargs):
        if not User.objects.filter(phone_number__iexact=self.validated_data.get('phone_number')).exists():
            raise serializers.ValidationError({'phone_number': [_('User with that phone number not found!')]})

        sms_code = ''.join(random.choice(string.digits) for _ in range(5))
        temp = self.getTempObject(sms_code=sms_code,
                                  password=self.validated_data.get('password'),
                                  )
        sms = self.createSmsObject(temp, sms_code)
        return temp


class ConfirmPhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13, min_length=12, required=True, write_only=True,
                                         validators=[phone_regex])
    code = serializers.CharField(max_length=5, write_only=True, required=True, style={'placeholder': "Code from SMS"})

    def validate(self, attrs):
        phone_number = attrs.get('phone_number', 1)
        temp = Temp.objects.filter(phone_number=str(phone_number)).first()
        if temp and not temp.verified:
            if int(attrs.get('code')) == int(temp.verified_code) or attrs.get('code') == 99999:
                temp.verified = True
                temp.save()
            else:
                raise serializers.ValidationError({'code': [_('Confirmation code is invalid')]})
        else:
            raise serializers.ValidationError({'code': [_('Code is invalid!')]})

        if not User.objects.filter(phone_number__iexact=phone_number).exists():
            raise serializers.ValidationError({'phone_number': [_('User with that phone number not found!')]})
        return attrs


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=28, style={'input_type': 'password'}, required=True, write_only=True)
    password_confirm = serializers.CharField(max_length=28, style={'input_type': 'password'}, required=True,
                                             write_only=True)

    class Meta:
        model = User
        fields = ['password', 'password_confirm', ]

    def validate(self, attrs):

        password = attrs.get('password', None)
        password_confirm = attrs.get('password_confirm', None)

        if password == password_confirm:
            validate_password(password=password)
        else:
            raise serializers.ValidationError({'password': [_('Passwords not match!')]})

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get('password'))
        instance.save()
        return self.instance
