from django.db.models import Q
from requests import Request
from rest_framework import filters
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from tour.agency.models import TourPackage
from tour.agency.serializers import TourPackageSerializer
from tour.agency.custom_pagination import CustomPagination

from tour.agency.models import City

from tour.agency.serializers import CitySerializer


class TourPackageListAPIView(ListAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'city_to__name', "city_to__destinations__name"]

    pagination_class = CustomPagination


class TourPackageDetailAPIView(RetrieveAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'city_from', 'city_to']

    def get_serializer_context(self):
        data = super().get_serializer_context()
        serializer = self.serializer_class(TourPackage.objects.filter(
            agency=self.get_object().agency, is_expired=False),
            many=True
        )

        data['related_data'] = serializer.data
        return data

    # def get(self,request,*args,**kwargs):
    #     serializer = self.serializer_class(self.get_object())
    #     data = serializer.data
    #     data['related_data']=self.serializer_class(TourPackage.objects.filter(agency=self.get_object().agency),many=True).data
    #     return Response(data)


class TourPackageSearchAPIView(APIView):

    def get(self, request):
        search = request.query_params.get('search')
        # if search value is city name
        if City.objects.filter(name=search).exists():

            duration_from, duration_to, activities, destinations = None, None, None, None
            if request.query_params.get('duration_from') and request.query_params.get('duration_to'):
                duration_from = request.query_params.get('duration_from')
                duration_to = request.query_params.get('duration_to')
            if request.query_params.get('activities'):
                activities = request.query_params.get('activities')
            if request.query_params.get('destinations'):
                destinations = request.query_params.get('destinations')

            # filtering against city name of the tour
            packages = TourPackage.objects.filter(
                Q(is_expired=False) &
                Q(city_to__name__iexact=search)
            )

            # filtering against duration of the tour
            if duration_from and duration_to:
                filtered_packages = []
                for package in packages:
                    if int(duration_to) >= (package.ending_date - package.starting_date).days >= int(duration_from):
                        filtered_packages.append(package)
                packages = filtered_packages

            # filtering against the activities included in the tour
            if activities:
                filtered_packages = []
                activity_list = [item.lower().title() for item in activities.split(',')]
                print(activity_list)
                for package in packages:
                    filtered_activities = [activity.name for activity in package.activities.all()]
                    print(filtered_activities)
                    tmp = [item for item in activity_list if item in filtered_activities]
                    if len(tmp) == len(activity_list):
                        filtered_packages.append(package)
                packages = filtered_packages

            # filtering against the destinations
            if destinations:
                filtered_packages = []
                destination_list = [item for item in destinations.split(',')]
                print(destination_list)
                for package in packages:
                    filtered_destinations = [activity.name for activity in package.destinations.all()]
                    print(filtered_destinations)
                    tmp = [item for item in destination_list if item in filtered_destinations]
                    if len(tmp) == len(destination_list):
                        filtered_packages.append(package)
                packages = filtered_packages

            serializer = TourPackageSerializer(packages, many=True)

        # otherwise
        else:
            packages = TourPackage.objects.filter(Q(title__icontains=search) | Q(city_to__name__iexact=search))
            serializer = TourPackageSerializer(packages, many=True)
        return Response(serializer.data)
