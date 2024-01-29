from rest_framework import serializers

from tour.agency.models import TourPackage


class TourPackageSerializer(serializers.ModelSerializer):

    class Meta:
        model = TourPackage
        fields = "__all__"

    def validate(self,attrs):
        return attrs
