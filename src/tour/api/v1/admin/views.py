from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.utils import json

from ....agency.models import TourPackage, Company, Options
from ....agency.serializers import CompanySerializer
from ....user.models import User
import requests
from .serializers import AgencyRegistrationSerializer, AgencyRegistrationActivationSerializer, \
    TourPackageCreateSerializer, \
    ChangeAgencyInfoSerializer
from .custom_permissions import IsAdminIsOwnerOrReadOnly, IsAdminIsAuthenticated


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


class GetAgencyAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanySerializer

    def get(self, request, pk):
        agency = Company.objects.filter(id=pk).first()
        if agency:
            serializer = self.serializer_class(instance=agency)
            data = serializer.data
            data['phone_number'] = agency.admin.phone_number
            return Response({"agency": data})
        return Response({'success': False, 'message': "Tour not Found"}, status=status.HTTP_400_BAD_REQUEST)


class AgencyRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminIsOwnerOrReadOnly,)
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


# class ChangeAgencyInfoAPIView(GenericAPIView):
#     serializer_class = AgencySerializer
#     permission_classes = (AllowAny,)
#
#     def put(self, reqeust):
#         super().pu
#
#     def patch(self, request):
#         pass


class TourPackageCreateAPIView(CreateAPIView):
    serializer_class = TourPackageCreateSerializer
    permission_classes = (IsAdminIsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'admin': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
