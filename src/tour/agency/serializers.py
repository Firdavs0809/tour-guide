from rest_framework import serializers
from tour.agency.models import TourPackage
from tour.agency.models import City
from tour.agency.models import Company
from tour.agency.models import Destination
from tour.agency.models import Activity,Feature


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
    features = FeatureSerializer(many=True,read_only=True)

    class Meta:
        model = City
        fields = ['name', 'is_popular', 'features']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name', ]


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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['tours_in_city'] = self.context.get('tours_in_city')
        ret['tours_in_period'] = self.context.get('tours_in_period')
        return ret
