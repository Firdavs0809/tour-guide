import json
import uuid

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from oauthlib.oauth2 import Server

from tour.user.models import User, Temp

from tour.oauth2.models import AccessToken, RefreshToken

from tour.agency.utils import set_default_application
from .serializers import (SignInSerializer, RefreshTokenSerializer, LogoutSerializer,
                          RegistrationSerializer, ActivationSerializer, ForgetPasswordSerializer,
                          ResetPasswordSerializer, ConfirmPhoneNumberSerializer)
from tour.oauth2.oauth2_validators import OAuth2V1Validator, OAuth2FrontValidator
from tour.oauth2.oauth2_backends import JSONOAuthLibCore


class RegistrationView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        data = request.data

        # logic for user not auth required
        if not data.get('password'):
            password = uuid.uuid4()
            try:
                data.update(password=str(password)[:30])
                print(data)
            except AttributeError:
                raise ValidationError({'success': False, 'message': _('Only json format is accepted.')})

        # Create a serializer with data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        code = serializer.save()
        return Response({"activation_code": int(code.verified_code)}, status=status.HTTP_200_OK)


class RegistrationActivationView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ActivationSerializer

    def post(self, request, *args, **kwargs):
        data = request.data

        # Create a serializer with data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            root = serializer.save()
            print(root)
            if root:

                # logic for user not auth required
                if not request.data.get('client_id'):
                    client_id, client_secret, grant_type = set_default_application()
                    temp = get_object_or_404(Temp, phone_number=data.get('phone_number'))

                    try:
                        request.data.update(
                            {'client_id': client_id, 'client_secret': client_secret, 'grant_type': grant_type,
                             'password': temp.password})
                    except AttributeError:
                        raise ValidationError({'success': False, 'message': _('Only json format is accepted.')})
                request.data.update(username=root.phone_number)

                # generating access_token and refresh_token
                oauth2 = JSONOAuthLibCore(
                    Server(OAuth2FrontValidator()))
                uri, headers, body, status_ = oauth2.create_token_response(request)
                data = json.loads(body)
                if status_ != 200:
                    raise ValidationError({'username': [data['error']]})
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "invalid verification"}, status=status.HTTP_400_BAD_REQUEST)

        except AttributeError as e:
            error = e
            return Response({"detail": f'error:{error.args}'})


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

        refresh_token = RefreshToken.objects.filter(
            user=User.objects.get(phone_number=request.data.get('phone_number'))).last()
        if refresh_token:
            access_token = refresh_token.access_token
            if access_token.is_expired():
                access_token.expires = timezone.now() + timezone.timedelta(days=30)
                access_token.save()
            return Response({'detail': 'Ok', 'access_token': access_token.token}, status=status.HTTP_200_OK)
        raise ValidationError({'success': False, 'message': _('User with that phone number not exists.')})


# Reset Password
class ResetPasswordView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"password": 'Password reset successful!', 'detail': 'success'}, status=status.HTTP_200_OK)
