from django.core.validators import RegexValidator
from django.db import transaction, IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tour.agency.models import Company, TempCompany

from tour.user.models import User
import requests

from tour.agency.utils import check_username_exists

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,12}$', message='invalid phone number')


class AgencyRegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    phone_number_2 = serializers.CharField(max_length=13, min_length=12, required=True, write_only=True,
                                           validators=[phone_regex])
    password = serializers.CharField(max_length=30, required=True, write_only=True)
    name = serializers.CharField(max_length=56, required=True, )
    licence_number = serializers.CharField(required=True, max_length=12, )
    address = serializers.CharField(required=True, max_length=95, )
    tg_username = serializers.CharField(required=True, max_length=32, min_length=5)
    website = serializers.CharField(max_length=200, )

    def validate_address(self, address):
        return address

    def validate_licence_number(self, licence_number):
        return licence_number

    def validate_tg_username(self, tg_username):
        if not check_username_exists(tg_username.replace('@', '')):
            message = _("Telegram username does not exist")
            raise ValidationError({'detial': message})
        return tg_username

    def save(self, **kwargs):
        tmp = self.getTempObject()
        if not tmp:
            try:
                tmp = TempCompany.objects.create(
                    name=self.validated_data.get('name', None),
                    phone_number="+"+self.validated_data.get('phone_number', None).replace('+',''),
                    phone_number_2=self.validated_data.get('phone_number_2', None),
                    licence_number=self.validated_data.get('licence_number', None),
                    address=self.validated_data.get('address', None),
                    tg_username=self.validated_data.get('tg_username', None),
                )
            except IntegrityError as error:
                error_message = _(
                    f"{str(error).split('(')[1].replace(')=', '')} already registered for another company.")
                raise ValidationError({'detail': error_message})
        return tmp

    def getTempObject(self, ):
        try:
            temp = TempCompany.objects.get(phone_number="+" + self.validated_data.get('phone_number').replace('+',''))
            try:
                temp.name = self.validated_data.get("name")
                temp.phone_number_2 = self.validated_data.get("phone_number_2")
                temp.licence_number = self.validated_data.get("licence_number")
                temp.address = self.validated_data.get("address")
                temp.tg_username = self.validated_data.get("tg_username")
                temp.is_verified = False
                temp.save()
                return temp
            except IntegrityError as error:
                if "UNIQUE constraint" in error:
                    error_message = _("The Unique constraint failed!")
                    raise ValidationError({'detail': error_message})
        except TempCompany.DoesNotExist:
            return False


class AgencyRegistrationActivationSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    def save(self, **kwargs):
        tmp = TempCompany.objects.filter(phone_number="+" + self.validated_data.get('phone_number').replace('+',''),
                                         is_verified=False).first()
        if not tmp:
            raise ValidationError(
                {'detail': _('Phone number is invalid. Please try the phone number used in registration!')})
        with transaction.atomic():
            try:
                agency = Company.objects.create(
                    admin=User.objects.get(phone_number=tmp.phone_number),
                    phone_number_2=tmp.phone_number_2,
                    licence_number=tmp.licence_number,
                    address=tmp.address,
                    name=tmp.name
                )

            except IntegrityError as e:
                print(e)
                if "UNIQUE constraint" in e.args:
                    error_message = "Please take a look at the Naming of the company that company already exists."
                else:
                    error_message = 'Error occurred during creation please contact support!'
                raise ValidationError(error_message)

            agency.is_waiting = True
            agency.save()
            tmp.is_verified = True
            tmp.save()
            return agency
        return None
