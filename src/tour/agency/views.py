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


class TourPackageListAPIView(ListAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializer

    # pagination_class = CustomPagination
    # filter_backends = [filters.SearchFilter]
    # search_fields = ['title', 'city_to__name', ]

    def get_queryset(self):
        return TourPackage.objects.filter(city_to__in=City.objects.filter(is_popular=True))[:4]


class TourPackageDetailAPIView(RetrieveAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializer

    def get_serializer_context(self):
        data = super().get_serializer_context()
        serializer_related_city = self.serializer_class(
            TourPackage.objects.filter(
                Q(agency=self.get_object().agency, is_expired=False) & ~Q(id=self.get_object().id)), many=True)
        serializer_related_period = self.serializer_class(
            TourPackage.objects.filter(Q(starting_date__gte=self.get_object().starting_date,
                                         ending_date__lte=self.get_object().ending_date, is_expired=False) & ~Q(
                id=self.get_object().id)), many=True)

        data['tours_in_period'] = serializer_related_period.data
        data['tours_in_city'] = serializer_related_city.data
        return data


class TourPackageSearchAPIView(APIView):

    def get(self, request):
        city = request.query_params.get('city')
        # if search value is city name
        if city:
            if City.objects.filter(name=city).exists():

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
                    Q(city_to__name__iexact=city)
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

        return Response([])
