from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import TourPackage, City, Company, Destination, Activity, Feature, Hotel, ImageUploadModel, Options, \
    Category
from ..api.v1.auth.serializers import phone_regex

# ~12MB
MAX_FILE_SIZE = 12 * 2 ** 20


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'name']


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ['id', 'name']


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['id', 'name']


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
    name = serializers.CharField(required=False)
    website = serializers.CharField(required=False)

    class Meta:
        model = Company
        fields = "__all__"


class HotelSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    stars = serializers.IntegerField(required=True)
    link = serializers.CharField(required=True)

    class Meta:
        model = Hotel
        fields = "__all__"

    def create(self, validated_data):
        return super().create(validated_data)


class HotelListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class OptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TourPackageSerializer(serializers.ModelSerializer):
    city_from = serializers.CharField()
    city_to = CitySerializer()
    destinations = DestinationSerializer(read_only=True, many=True)
    activities = ActivitySerializer(read_only=True, many=True)
    options = OptionsSerializer(read_only=True, many=True)
    hotels = HotelSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True, many=True)

    class Meta:
        model = TourPackage
        exclude = ['language', 'is_expired', 'is_featured', 'number_people']

    def validate(self, attrs):
        return attrs


class TourPackageSerializerList(serializers.ModelSerializer):
    class Meta:
        model = TourPackage
        fields = ['id', 'title', 'image', 'description', 'starting_date', 'ending_date', 'price', 'city_from',
                  'city_to']
        # exclude = ['destinations', 'activities', 'hotels', 'language', 'is_expired',
        #            'is_featured', 'options', 'category', 'images', 'number_people']


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUploadModel
        fields = ['file']

    def validate_file(self, image):
        if image.size > MAX_FILE_SIZE:
            raise ValidationError({"detail": 'Image size should be under 12MB.'})
        return image


class ConfirmBookingSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13, min_length=12, required=True, write_only=True,
                                         validators=[phone_regex])
    comment = serializers.CharField(required=False)
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)

    def save(self, **kwargs):
        profile = self.context.get('profile')
        if not profile.first_name or profile.first_name != self.validated_data.get('first_name'):
            profile.first_name = self.validated_data.get('first_name')
        if not profile.last_name or profile.last_name != self.validated_data.get('last_name'):
            profile.last_name = self.validated_data.get('last_name')
        profile.save()
        return profile
