import time
from datetime import timedelta, datetime

from django.db.models import Q
from requests import Request
from rest_framework import filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from tour.agency.models import TourPackage
from tour.agency.serializers import TourPackageSerializer, ImageUploadSerializer
from tour.agency.custom_pagination import CustomPagination

from tour.agency.models import City


class TourPackageListAPIView(ListAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializer

    # pagination_class = CustomPagination
    # filter_backends = [filters.SearchFilter]
    # search_fields = ['title', 'city_to__name', ]

    def get_queryset(self):
        city = self.request.query_params.get('city', )
        packages = TourPackage.objects.filter(city_to__in=City.objects.filter(name=city), is_expired=False)
        return packages

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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
                                         starting_date__lte=self.get_object().starting_date + timedelta(days=3),
                                         ending_date__lte=self.get_object().ending_date + timedelta(days=3),
                                         ending_date__gte=self.get_object().ending_date - timedelta(days=3),
                                         is_expired=False) & ~Q(
                id=self.get_object().id)), many=True)

        data['tours_in_period'] = serializer_related_period.data
        data['tours_in_city'] = serializer_related_city.data
        return data


class ConfirmBookingAPIView(GenericAPIView):

    def post(self, request):
        pass


class TourPackageSearchAPIView(APIView):

    def get(self, request):
        city, starting_date, ending_date, number_of_people = request.query_params.get('city'), request.query_params.get(
            'starting_date'), request.query_params.get('ending_date'), request.query_params.get('number_of_people', )
        # if search value is city name
        if city and starting_date and ending_date:
            if City.objects.filter(name=city).exists():
                duration_from, duration_to, activities, destinations = None, None, None, None
                if request.query_params.get('duration_from') and request.query_params.get('duration_to'):
                    duration_from = request.query_params.get('duration_from')
                    duration_to = request.query_params.get('duration_to')
                if request.query_params.get('activities'):
                    activities = request.query_params.get('activities')
                if request.query_params.get('destinations'):
                    destinations = request.query_params.get('destinations')

                temp_start = datetime.strptime(starting_date, '%Y-%m-%d').date()
                temp_end = datetime.strptime(ending_date, '%Y-%m-%d').date()

                # filtering against city name of the tour
                packages = TourPackage.objects.filter(
                    Q(is_expired=False) &
                    Q(city_to__name__iexact=city) &
                    Q(starting_date__gte=temp_start - timedelta(days=3),
                      starting_date__lte=temp_start + timedelta(days=3)) |
                    Q(ending_date__gte=temp_end - timedelta(days=3),
                      ending_date__lte=temp_end + timedelta(days=3))
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
                    # print(activity_list)
                    for package in packages:
                        filtered_activities = [activity.name for activity in package.activities.all()]
                        # print(filtered_activities)
                        tmp = [item for item in activity_list if item in filtered_activities]
                        if len(tmp) == len(activity_list):
                            filtered_packages.append(package)
                    packages = filtered_packages

                # filtering against the destinations
                if destinations:
                    filtered_packages = []
                    destination_list = [item for item in destinations.split(',')]
                    # print(destination_list)
                    for package in packages:
                        filtered_destinations = [activity.name for activity in package.destinations.all()]
                        # print(filtered_destinations)
                        tmp = [item for item in destination_list if item in filtered_destinations]
                        if len(tmp) == len(destination_list):
                            filtered_packages.append(package)
                    packages = filtered_packages

                if starting_date:
                    pass
                serializer = TourPackageSerializer(packages, many=True)
                return Response(data=serializer.data)

        return Response([])


class ImageUploadView(APIView):
    serializer_class = ImageUploadSerializer

    def post(self, request, pk):
        file = request.data.get('file')
        try:
            package = TourPackage.objects.get(id=pk)
            package.images.append(file)
        except TourPackage.DoesNotExist:
            raise ValidationError({'success': False, "message": 'Tour Package with this id not found'},
                                  code=status.HTTP_404_NOT_FOUND)
        except AttributeError:
            package.images = [file, ]
            package.save()
        return Response({"success": True, 'message': 'Image was uploaded successfully!'})
