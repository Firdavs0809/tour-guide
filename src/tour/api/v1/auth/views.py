import json
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError, Throttled
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from oauthlib.oauth2 import Server

from tour.oauth2.models import Application

from tour.user.models import User
from .serializers import (SignInSerializer, RefreshTokenSerializer, LogoutSerializer,
                          RegistrationSerializer, ActivationSerializer, ForgetPasswordSerializer,
                          ResetPasswordSerializer, ConfirmPhoneNumberSerializer)
from tour.oauth2.oauth2_validators import OAuth2V1Validator, OAuth2FrontValidator
from tour.oauth2.oauth2_backends import JSONOAuthLibCore

from .throttle import UserRegisterRateThrottle


# code for recaptcha goes here


class RegistrationView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    # recaptcha logic
    throttle_classes = (UserRegisterRateThrottle,)

    def throttled(self, request, wait):
        raise Throttled(detail={
            "message": "recaptcha_required",
        })

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.save()
        return Response({"activation_code": int(code.verified_code)}, status=status.HTTP_200_OK)


class RegistrationActivationView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ActivationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            root = serializer.save()
            if root:
                return Response({"detail": "success"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "invalid verification"})

        except Exception as e:
            error = e
            return Response({"detail": e})


class SignInView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SignInSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """API for sign in"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.request.data
        oauth2 = JSONOAuthLibCore(
            Server(OAuth2FrontValidator()))
        uri, headers, body, status = oauth2.create_token_response(request)

        data = json.loads(body)
        if status != 200:
            raise ValidationError({'username': [data['error']]})

        return Response(data, status=status)


class RefreshTokenView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RefreshTokenSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """ API for refresh token. When access token expires, 401 error returned. In this case, new access token
        should retreived. """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        oauth2 = JSONOAuthLibCore(Server(OAuth2V1Validator()))
        uri, headers, body, status = oauth2.create_token_response(request)
        return Response(json.loads(body), status=status)


class LogoutView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_response(self):
        oauth2 = JSONOAuthLibCore(Server(OAuth2V1Validator()))
        url, headers, body, status = oauth2.create_revocation_response(self.request)
        if status != 200:
            result = json.loads(body)
        else:
            result = {"detail": _("success logout")}
        return Response(result, status=status)

    def post(self, request, *args, **kwargs):
        '''API for logout.'''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.get_response()


class ForgetPasswordView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.save()
        return Response({"code": int(code.verified_code)}, status=status.HTTP_200_OK)


class ConfirmPhoneNumberAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConfirmPhoneNumberSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'detail': 'Ok'}, status=status.HTTP_200_OK)


# Reset Password
class ResetPasswordView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(queryset=User, phone_number=request.data.get('phone_number'))
        serializer = self.serializer_class(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"password": 'Password reset successful!', 'detail': 'success'}, status=status.HTTP_200_OK)
