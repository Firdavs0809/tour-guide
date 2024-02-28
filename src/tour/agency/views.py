from datetime import timedelta, datetime
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, GenericAPIView, get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import TourPackage, Company, Booking
from .serializers import TourPackageSerializer, ImageUploadSerializer, TourPackageSerializerList
from .models import City, Options, Category
from .serializers import ConfirmBookingSerializer, CompanySerializer, FeatureSerializer, PopularCitySerializer, \
    OptionsSerializer, CategorySerializer
from .utils import send_message
from rest_framework.filters import OrderingFilter
from .custom_pagination import CustomPagination, CustomCursorPagination


class ExcludeExpiredPackages(GenericAPIView):

    def get(self, request):
        packages = TourPackage.objects.filter(starting_date__gte=timezone.now() + timedelta(hours=12))
        packages.set(is_expired=True)
        return Response({'detail': "ok"})


class TourPackageListAPIView(ListAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializerList
    permission_classes = (AllowAny,)

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
    permission_classes = (AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance)
        data = serializer.data
        return Response(data)


class GetRelatedToursAPIView(GenericAPIView):
    serializer_class = TourPackageSerializerList
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        obj = get_object_or_404(TourPackage, id=pk)
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
    permission_classes = (AllowAny,)

    def get(self, request):
        queryset = TourPackage.objects.filter(is_featured=True)
        featured_tours = self.serializer_class(queryset, many=True).data
        return Response({'featured_tours': featured_tours, })


class TourPackageSearchAPIView(GenericAPIView):
    queryset = TourPackage.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['starting_date']
    ordering = ['starting_date']
    permission_classes = (AllowAny,)

    def get(self, request):

        queryset = self.filter_queryset(queryset=self.get_queryset())
        city, starting_date, ending_date, number_of_people = request.query_params.get('city'), request.query_params.get(
            'starting_date'), request.query_params.get('ending_date'), request.query_params.get('number_of_people', )
        # if search value is city name
        if city and starting_date and ending_date:
            city = City.objects.filter(name=city)
            if city.exists():
                duration_from, duration_to, activities, destinations, category, options = None, None, None, None, None, None
                if request.query_params.get('duration_from') and request.query_params.get('duration_to'):
                    duration_from = request.query_params.get('duration_from')
                    duration_to = request.query_params.get('duration_to')
                if request.query_params.get('activities'):
                    activities = request.query_params.get('activities')
                if request.query_params.get('destinations'):
                    destinations = request.query_params.get('destinations')
                if request.query_params.get('options'):
                    options = request.query_params.get('options')
                if request.query_params.get('category'):
                    category = request.query_params.get('category')

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
                    activity_list = [item.lower() for item in activities.split(',')]
                    print(activity_list)
                    for package in packages:
                        filtered_activities = [activity.name.lower() for activity in package.activities.all()]
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
                        filtered_destinations = [destination.name for destination in package.destinations.all()]
                        # print(filtered_destinations)
                        tmp = [item for item in destination_list if item in filtered_destinations]
                        if len(tmp) == len(destination_list):
                            filtered_packages.append(package)
                    packages = filtered_packages

                # filtering against the options
                if options:
                    filtered_packages = []
                    options_list = [item for item in options.split(',')]
                    # print(options)
                    for package in packages:
                        filtered_options = [option.name for option in package.options.all()]
                        # print(filtered_options)
                        tmp = [item for item in options_list if item in filtered_options]
                        if len(tmp) == len(options_list):
                            filtered_packages.append(package)
                    packages = filtered_packages

                # filtering against the category
                if category:
                    filtered_packages = []
                    category_list = [item for item in category.split(',')]
                    for package in packages:
                        filtered_category = [each_category.name for each_category in package.category.all()]
                        # print(filtered_options)
                        tmp = [item for item in category_list if item in filtered_category]
                        if len(tmp) == len(category_list):
                            filtered_packages.append(package)
                    packages = filtered_packages

                serializer = TourPackageSerializer(packages, many=True)
                return Response(data=serializer.data)

        return Response([])


class ImageUploadView(GenericAPIView):
    serializer_class = ImageUploadSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj=serializer.save()
        return Response({"detail": "ok", 'image': str(obj.file).split('/')[-1]})


# Confirm Booking API View
class ConfirmBookingAPIView(GenericAPIView):
    serializer_class = ConfirmBookingSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            package = TourPackage.objects.get(pk=pk)
        except TourPackage.DoesNotExist:
            raise ValidationError({"success": False, "detail": "Tour Package not Found"})

        profile = request.user.profile
        if package not in profile.packages.all():
            profile.packages.add(package)
        else:
            raise ValidationError({"success": False, "detail": _("You have already booked that tour.")})

        (obj, created) = Booking.objects.get_or_create(package=package, profile=profile)
        if created:

            serializer = CompanySerializer(package.agency)
            data = serializer.data
            data['phone_number'] = package.agency.admin.phone_number
            obj.comment = request.data.get('comment', None)
            obj.save()

            message = (f"You have a client!\n"
                       f"Tour package: {package.title}\n"
                       f"user: {request.user.first_name}\n"
                       f"username: @fredo\n"
                       f"phone_number: +{request.user.phone_number}")

            try:
                send_message(message, package.agency.chat_id)
            except:
                raise ValidationError({'detail': "Agency is not a member of the bot."})

            return Response({'agency': data})
        raise ValidationError({'detail': _("You have already booked for that tour package.")})


# get city view
class GetCityMatchAPIView(GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        city = request.query_params.get('city', None)
        if city:
            city_list = [city.name for city in City.objects.filter(Q(name__istartswith=city))]
            city_list += [city.name for city in City.objects.filter(Q(name__icontains=city)) if
                          city.name not in city_list]
            return Response({"city_list": city_list})
        return Response([])


class GetCityFeaturesAPIView(GenericAPIView):
    serializer_class = FeatureSerializer
    permission_classes = (AllowAny,)

    def get(self, request, cityId):
        city = get_object_or_404(City, id=cityId)
        serializer = self.serializer_class(city.features, many=True)
        return Response({'features': serializer.data})


class GetPopularCityAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PopularCitySerializer

    def get(self, request):
        city_list = PopularCitySerializer(City.objects.filter(is_popular=True), many=True)
        return Response({'city_list': city_list.data})


# get filters view
class GetFiltersAPIView(GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        city = City.objects.filter(id=pk)
        if city.exists():
            city = city.first()
            features = [feature.name for feature in city.features.all()]

            activities = []
            destinations = []

            packages = TourPackage.objects.filter(city_to=city)
            for package in packages:
                for dest in package.destinations.all():
                    if dest.name not in destinations:
                        destinations.append(dest.name)

                for activity in package.activities.all():
                    if activity.name not in activities:
                        activities.append(activity.name)

            # STATIC duration generator no need for dynamic one
            # if (package.ending_date - package.starting_date).days not in durations:
            #     durations.append((package.ending_date - package.starting_date).days)

            # durations_ = []
            #
            # # checking if duration period is less than 4
            # if len(durations) <= 4:
            #     range_num = len(durations)
            # else:
            #     range_num = 4
            #
            # # forming duration filter
            # for _ in range(len(durations)):
            #     try:
            #         durations_.append({"start": str(durations_[-1].get('end')), 'end': str(min(durations))})
            #     except IndexError:
            #         durations_.append({"start": str(0), 'end': str(min(durations))})
            #     finally:
            #         durations.remove(min(durations))

            durations = []
            for _ in range(4):
                durations = [{'start': str(item), 'end': str(item + 3)} for item in
                             range(0, 10, 3)]

            return Response(
                {"activities": activities, 'destinations': destinations, 'features': features,
                 'durations': durations})
        return Response([])


class SetAgencyIdAPIView(GenericAPIView):

    def post(self, request):
        tg_username = request.data.get('tg_username')
        chat_id = request.data.get('chat_id')
        agency = get_object_or_404(Company, tg_username=tg_username)
        agency.chat_id = chat_id
        agency.is_bot_connected = True
        agency.save()
        return Response({'detail': 'ok'})


class GetOptionsAPIView(GenericAPIView):
    serializer_class = OptionsSerializer
    permission_classes = (AllowAny,)
    queryset = Options

    def get_queryset(self):
        return self.queryset.objects.all()

    def get(self, request):
        serializer = self.serializer_class(instance=self.get_queryset(), many=True)
        return Response({'options': serializer.data})


class GetCategoryAPIView(GenericAPIView):
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)
    queryset = Category

    def get_queryset(self):
        return self.queryset.objects.all()

    def get(self, request):
        serializer = self.serializer_class(instance=self.get_queryset(), many=True)
        return Response({'categories': serializer.data})


class GetTourOptionsAPIView(GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        package = TourPackage.objects.filter(id=pk).first()
        options = []
        if package:
            options = [option.name for option in package.options.all()]
        return Response({"options": options})


class GetTourCategoryAPIView(GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        package = TourPackage.objects.filter(id=pk).first()
        category_list = []
        if package:
            category_list = [category_obj.name for category_obj in package.category.all()]
        return Response({"category": category_list})
