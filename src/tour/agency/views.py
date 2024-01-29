from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListAPIView

from tour.agency.models import TourPackage
from tour.agency.serializers import TourPackageSerializer

from tour.agency.custom_pagination import CustomPagination


class TourPackageListAPIView(ListAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializer
    # filter_backends = [DjangoFilterBackend]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title','city_from__name','city_to__name']

    pagination_class = CustomPagination


class TourPackageDetailAPIView(RetrieveAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'city_from', 'city_to']

