from rest_framework import filters
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from tour.agency.models import TourPackage
from tour.agency.serializers import TourPackageSerializer
from tour.agency.custom_pagination import CustomPagination


class TourPackageListAPIView(ListAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title','city_from__name','city_to__name']

    pagination_class = CustomPagination


class TourPackageDetailAPIView(RetrieveAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'city_from', 'city_to']

    def get_serializer_context(self):
        data = super().get_serializer_context()
        serializer = self.serializer_class(TourPackage.objects.filter(
            agency=self.get_object().agency,is_expired=False),
            many=True
        )

        data['related_data']=serializer.data
        return data

    # def get(self,request,*args,**kwargs):
    #     serializer = self.serializer_class(self.get_object())
    #     data = serializer.data
    #     data['related_data']=self.serializer_class(TourPackage.objects.filter(agency=self.get_object().agency),many=True).data
    #     return Response(data)

