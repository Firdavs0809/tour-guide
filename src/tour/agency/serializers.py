from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import TourPackage, City, Company, Destination, Activity, Feature, Hotel, ImageUploadModel, Options, \
    Category

# ~12MB
MAX_FILE_SIZE = 12 * 2 ** 20


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['name', 'icon']


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ['name']


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['name']


class CitySerializer(serializers.ModelSerializer):
    # features = FeatureSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name']


class PopularCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ['id', 'total_rating', 'admin', 'is_verified', 'is_bot_connected', 'is_waiting', 'chat_id']


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        exclude = ['name', 'website']


class TourPackageSerializer(serializers.ModelSerializer):
    city_from = serializers.CharField()
    city_to = CitySerializer()
    destinations = DestinationSerializer(read_only=True, many=True)
    activities = ActivitySerializer(read_only=True, many=True)

    class Meta:
        model = TourPackage
        exclude = ['language', 'is_expired', 'is_featured','number_people']

    def validate(self, attrs):
        return attrs


class TourPackageSerializerList(serializers.ModelSerializer):
    class Meta:
        model = TourPackage
        exclude = ['city_from', 'city_to', 'destinations', 'activities', 'hotels', 'language', 'is_expired',
                   'is_featured', 'options', 'category']


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUploadModel
        fields = ['file']

    def validate_file(self, image):
        if image.size > MAX_FILE_SIZE:
            raise ValidationError({"detail": 'Image size should be under 12MB.'})
        return image


class ConfirmBookingSerializer(serializers.Serializer):
    tg_username = serializers.CharField(max_length=200, required=True, write_only=True)
    comment = serializers.CharField(required=False)


class OptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
