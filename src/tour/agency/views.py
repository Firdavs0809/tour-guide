import time
from datetime import timedelta, datetime

from django.db.models import Q
from requests import Request
from rest_framework import filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from tour.agency.models import TourPackage
from tour.agency.serializers import TourPackageSerializer, ImageUploadSerializer
from tour.agency.custom_pagination import CustomPagination, CustomCursorPagination

from tour.agency.models import City, User

from tour.agency.serializers import ConfirmBookingSerializer, CitySerializer, CompanySerializer, FeatureSerializer, \
    DestinationSerializer
from .telegram_bot_setup import send_message

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


class TourPackageDetailAPIView(RetrieveAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializer

    def get_serializer_context(self):
        data = super().get_serializer_context()
        return data


class GetRelatedToursAPIView(GenericAPIView):
    serializer_class = TourPackageSerializer

    def get(self, request):
        obj = TourPackage.objects.get(id=request.query_params.get('id'))
        serializer_related_city = self.serializer_class(TourPackage.objects.filter(
            Q(city_to=obj.city_to, is_expired=False) & ~Q(id=obj.id)), many=True).data
        serializer_related_period = self.serializer_class(TourPackage.objects.filter(
            Q(starting_date__gte=obj.starting_date - timedelta(days=5),
              starting_date__lte=obj.starting_date + timedelta(days=5),
              ending_date__lte=obj.ending_date + timedelta(days=5),
              ending_date__gte=obj.ending_date - timedelta(days=5), is_expired=False) & ~Q(id=obj.id)), many=True).data
        return Response({'related_city': serializer_related_city, 'related_period': serializer_related_period})


# Get featured tours
class GetFeaturedToursAPIView(GenericAPIView):
    serializer_class = TourPackageSerializer

    def get(self, request):
        queryset = TourPackage.objects.filter(is_featured=True)
        featured_tours = self.serializer_class(queryset, many=True).data
        return Response({'featured_tours': featured_tours, })


class TourPackageSearchAPIView(GenericAPIView):
    queryset = TourPackage.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['starting_date']
    ordering = ['starting_date']

    def get(self, request):

        queryset = self.filter_queryset(queryset=self.get_queryset())
        city, starting_date, ending_date, number_of_people = request.query_params.get('city'), request.query_params.get(
            'starting_date'), request.query_params.get('ending_date'), request.query_params.get('number_of_people', )
        # if search value is city name
        if city and starting_date and ending_date:
            city = City.objects.filter(name=city)
            if city.exists():
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
                packages = queryset.filter(
                    Q(is_expired=False, city_to__in=city) &
                    Q(starting_date__gte=temp_start - timedelta(days=5),
                      starting_date__lte=temp_start + timedelta(days=5)) &
                    Q(ending_date__gte=temp_end - timedelta(days=5),
                      ending_date__lte=temp_end + timedelta(days=5))
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


# Confirm Booking API View
class ConfirmBookingAPIView(GenericAPIView):
    serializer_class = ConfirmBookingSerializer

    def post(self, request, pk):
        try:
            package = TourPackage.objects.get(pk=pk)
        except TourPackage.DoesNotExist:
            raise ValidationError({"success": False, "detail": "Tour Package not Found"})

        serializer = CompanySerializer(package.agency)

        message = (f"You have a client!\n"
                   f"Tour package: {package.title}\n"
                   f"user: Firdavs Jalolov\n"
                   f"username: @first_ac_firdavs\n"
                   f"phone_number: +998907689098")

        try:
            send_message(message,package.agency.chat_id)
        except:
            raise ValidationError({'detail': "Agency is not a member of the bot."})

        return Response({'agency': serializer.data})


# get city view
class GetCityAPIView(GenericAPIView):

    def get(self, request):
        city = request.query_params.get('city', None)
        print(request.query_params)
        print(city)
        if city:
            city_list = [city.name for city in City.objects.filter(name__icontains=city)]
            return Response({"city_list": city_list})
        return Response([])


# get filters view
class GetFiltersAPIView(GenericAPIView):

    def get(self, request):
        city = request.query_params.get('city')
        if city:
            city = City.objects.get(name=city)
            features = [feature.name for feature in city.features.all()]

            activities = []
            destinations = []
            durations = []

            packages = TourPackage.objects.filter(city_to=city)
            for package in packages:
                for dest in package.destinations.all():
                    if dest.name not in destinations:
                        destinations.append(dest.name)

                for activity in package.activities.all():
                    if activity.name not in activities:
                        activities.append(activity.name)

                if (package.ending_date - package.starting_date).days not in durations:
                    durations.append((package.ending_date - package.starting_date).days)

            durations_ = []

            # checking if duration period is less than 4
            if len(durations) <= 3:
                range_num = len(durations)
            else:
                range_num = 4

            # forming duration filter
            for _ in range(range_num):
                try:
                    durations_.append({"start": durations_[-1].get('end'), 'end': min(durations)})
                except IndexError:
                    durations_.append({"start": 0, 'end': min(durations)})
                finally:
                    durations.remove(min(durations))

            return Response(
                {"activities": activities, 'destinations': destinations, 'features': features, 'durations': durations_})
        return Response([])
