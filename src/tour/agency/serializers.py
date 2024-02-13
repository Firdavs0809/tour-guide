from rest_framework import serializers
from tour.agency.models import TourPackage
from tour.agency.models import City
from tour.agency.models import Company
from tour.agency.models import Destination
from tour.agency.models import Activity, Feature,Hotel

from tour.user.serializers import ProfileSerializer


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['name']


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ['name']


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['name']


class CitySerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = ['name', 'is_popular', 'features']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ['id', 'total_rating']


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        exclude = ['name','website']


class TourPackageSerializer(serializers.ModelSerializer):
    city_from = serializers.CharField()
    city_to = CitySerializer(read_only=True, )
    agency = serializers.CharField()
    destinations = DestinationSerializer(read_only=True, many=True)
    activities = ActivitySerializer(read_only=True, many=True)

    class Meta:
        model = TourPackage
        fields = "__all__"

    def validate(self, attrs):
        return attrs


class ImageUploadSerializer(serializers.Serializer):
    file = serializers.CharField(max_length=500, required=True, write_only=True)


class ConfirmBookingSerializer(serializers.Serializer):
    tg_username = serializers.CharField(max_length=200, required=True, write_only=True)
