from rest_framework import serializers

from tour.agency.models import TourPackage

from tour.agency.models import City

from tour.agency.models import Company

from tour.agency.models import Destination

from tour.agency.models import Activity


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ['name']


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['name']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'is_popular', ]


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
        if self.context.get('related_data'):
            ret['related_data'] = self.context['related_data']
        return ret
