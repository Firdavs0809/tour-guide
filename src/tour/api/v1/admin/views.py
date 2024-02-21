from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

from ....agency.models import TourPackage, Company
from ....user.models import User
import requests
from .serializers import AgencyRegisterSerializer, AgencyRegistrationActivationSerializer


class AgencyRegisterAPIView(GenericAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = AgencyRegisterSerializer

    def register_user(self, serializer):
        data = {
            'first_name': serializer.validated_data['name'],
            'phone_number': serializer.validated_data['phone_number'],
            'password': serializer.validated_data['password']
        }
        return requests.post(serializer.validated_data.pop('registration_url'), data=data).json()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['registration_url'] = request.build_absolute_uri(reverse('api:auth-registration'))
        response = self.register_user(serializer)
        if response.get('activation_code', None):
            serializer.save()
            return Response(response, status=status.HTTP_201_CREATED)
        print(response)
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class AgencyRegistrationActivationAPIView(GenericAPIView):
    serializer_class = AgencyRegistrationActivationSerializer
    permission_classes = [AllowAny, ]

    def check_user_activation(self, serializer):
        data = {
            'phone_number': serializer.validated_data['phone_number'],
            'code': serializer.validated_data['code']
        }
        return requests.post(serializer.validated_data.pop('activation_url'), data=data).json()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['activation_url'] = request.build_absolute_uri(
            reverse('api:auth-register-activation'))
        response = self.check_user_activation(serializer)
        print(response)
        serializer.save()
        return Response({'detail': 'ok'})


class CreateHotelAPIView():
    pass
