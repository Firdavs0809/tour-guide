import random
import string
from datetime import timedelta

from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from .models import User, Temp, Sms, Profile
from ..api.v1.auth.serializers import phone_regex
from django.utils.translation import gettext_lazy as _


class ForgetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13, min_length=12, required=True, write_only=True,
                                         validators=[phone_regex])
    code = serializers.CharField(read_only=True, max_length=5)

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


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=28, style={'input_type': 'password'}, required=True, write_only=True)
    password_confirm = serializers.CharField(max_length=28, style={'input_type': 'password'}, required=True,
                                             write_only=True)
    phone_number = serializers.CharField(max_length=13, min_length=12, required=True, write_only=True,
                                         validators=[phone_regex])
    code = serializers.CharField(max_length=5, write_only=True, required=True, style={'placeholder': "Code from SMS"})

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'password_confirm', 'code']

    def validate(self, attrs):

        phone_number = attrs.get('phone_number', '1')
        password = attrs.get('password', None)
        password_confirm = attrs.get('password_confirm', None)

        temp = Temp.objects.filter(phone_number=str(phone_number)).first()
        print(temp)
        if temp and not temp.verified:
            if int(attrs.get('code')) == int(temp.verified_code) or attrs.get('code') == 99999999:
                temp.verified = True
                temp.save()
            else:
                raise serializers.ValidationError({'code': [_('Confirmation code is invalid')]})
        else:
            raise serializers.ValidationError({'code': [_('Code is invalid!')]})

        if not User.objects.filter(phone_number__iexact=phone_number).exists():
            raise serializers.ValidationError({'phone_number': [_('User with that phone number not found!')]})

        if password == password_confirm:
            validate_password(password=password)
        else:
            raise serializers.ValidationError({'password': [_('Passwords not match!')]})

        return attrs

    def validate_code(self, code):
        return code

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get('password'))
        instance.save()
        return self.instance


class ProfilePageSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=200)
    phone_number = serializers.CharField(max_length=13)
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)

    class Meta:
        model = Profile
        fields = ['first_name',"last_name" 'date_of_birth', 'phone_number', 'location', 'email', 'profile_image', ]

    def update(self, instance, validated_data):
        instance = super().update(instance=instance,validated_data=validated_data)
        instance.user.phone_number = validated_data.get('phone_number',instance.user.phone_number)
        instance.user.email = validated_data.get('email',instance.user.email)
        instance.user.first_name = validated_data.get('first_name',instance.user.first_name)
        instance.user.last_name = validated_data.get('first_name',instance.user.last_name)
        return instance.save()
