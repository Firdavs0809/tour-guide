from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, \
    get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.utils import json

from ....agency.custom_pagination import CustomPagination
from ....agency.models import TourPackage, Company, Options
from ....agency.serializers import CompanySerializer, TourPackageSerializer
from ....user.models import User
import requests
from .serializers import AgencyRegistrationSerializer, AgencyRegistrationActivationSerializer, \
    TourPackageCreateSerializer, CompanyListSerializer
from .custom_permissions import IsAdminIsOwner, IsAdminIsAuthenticatedIsTourOwner, IsSuperUser


class AgencyRegisterAPIView(GenericAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = AgencyRegistrationSerializer

    def register_user(self, serializer):
        data = {
            'first_name': serializer.validated_data['name'],
            'phone_number': serializer.validated_data['phone_number'],
            'password': serializer.validated_data['password']
        }
        return requests.post(serializer.validated_data.pop('registration_url'), data=data).json()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['registration_url'] = request.build_absolute_uri(reverse('api:auth-registration'))
        response = self.register_user(serializer)
        if response.get('activation_code', None):
            serializer.save()
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class AgencyRegistrationActivationAPIView(GenericAPIView):
    serializer_class = AgencyRegistrationActivationSerializer
    permission_classes = [AllowAny, ]

    def check_user_activation(self, serializer):
        data = {
            'phone_number': serializer.validated_data['phone_number'],
            'code': serializer.validated_data['code'],
            'client_id': self.request.data.get('client_id'),
            'client_secret': self.request.data.get('client_secret'),
            'grant_type': self.request.data.get('grant_type'),
            'password': self.request.data.get('password')
        }
        return requests.post(serializer.validated_data.pop('activation_url'), data=json.dumps(data),
                             headers={'Content-Type': 'application/json'})

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['activation_url'] = request.build_absolute_uri(
            reverse('api:auth-register-activation'))
        response = self.check_user_activation(serializer)
        if response.status_code == 200:
            serializer.save()
        return Response(response.json())


class AgencyUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminIsOwner,)
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class AgencyMeAPIView(GenericAPIView):
    permission_classes = (IsAdminIsOwner,)
    serializer_class = CompanySerializer

    def get(self, request):
        user = request.user
        try:
            data = self.serializer_class(instance=user.agency).data
        except Exception as e:
            data = {'success': False, 'message': _('You don\'t own a company! You are super!')}
        return Response(data=data)


class AgencyAcceptAPIView(GenericAPIView):
    permission_classes = (IsSuperUser,)

    def post(self, request, pk):
        agency = get_object_or_404(Company, id=pk)
        data = {'success': False, 'message': _(f'Agency: {agency.name} - is already verified.')}
        if not agency.is_verified and agency.is_waiting:
            agency.is_verified = True
            agency.is_waiting = False
            agency.save()
            data = {'success': True, 'message': _(f'Agency: {agency.name} - is successfully verified.')}
        return Response(data=data)


class AgencyListAPIView(ListAPIView):
    serializer_class = CompanyListSerializer
    permission_classes = (IsSuperUser,)
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Company.objects.all()
        return queryset


class AgencyListWaitingAPIView(ListAPIView):
    serializer_class = CompanyListSerializer
    permission_classes = (IsSuperUser,)
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Company.objects.filter(is_waiting=True)
        return queryset


class TourPackageCreateAPIView(CreateAPIView):
    serializer_class = TourPackageCreateSerializer
    permission_classes = (IsAdminIsAuthenticatedIsTourOwner,)

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'admin': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TourPackageRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TourPackageCreateSerializer
    permission_classes = (IsAdminIsAuthenticatedIsTourOwner,)
    queryset = TourPackage.objects.all()

    def retrieve(self, request, *args, **kwargs):
        serializer = TourPackageSerializer(self.get_object())
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        package = self.get_object()
        package.delete()
        return Response(data={
            'success': 'ok',
            'message': _('Tour deleted successfully!')
        })


class TourPackageCreateNotifyAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if request.user.is_staff:
            return Response({'detail': 'ok'})
        agency = request.user.agency
        if agency and not agency.is_waiting:
            agency.is_waiting = True
            agency.save()
            message = _(
                'The company has been notified. You can create your post soon after they confirmed your account!')
        else:
            message = _(
                'You have already notified the company. Please wait until they confirm you are real agency!')
        return Response({'success': True, 'message': message})
