from rest_framework import serializers

from tour.agency.models import TourPackage

from tour.agency.models import City

from tour.agency.models import Company


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'is_popular']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name', ]


class TourPackageSerializer(serializers.ModelSerializer):
    city_from = serializers.CharField()
    city_to = serializers.CharField()
    agency=serializers.CharField()

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
