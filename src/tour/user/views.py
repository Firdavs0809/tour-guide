from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import ProfileSerializer, ForgetPasswordSerializer, ResetPasswordSerializer
from ..oauth2.authentication import OAuth2Authentication
from .models import User


class ProfilePageView(GenericAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (OAuth2Authentication,)

    def get(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(instance=profile)
        return Response({'data': serializer.data})

    def put(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(instance=profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": 'success', 'detail': 'Updated successfully!'})

    def delete(self, request):
        user = request.user
        user.delete()


# Forget password
class ForgetPasswordView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.save()
        return Response({"confirmation_code": int(code.verified_code)}, status=status.HTTP_200_OK)


# Reset Password
class ResetPasswordView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def put(self, request, *args, **kwargs):
        user = get_object_or_404(queryset=User,phone_number=request.data.get('phone_number'))
        serializer = self.serializer_class(instance=user,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"password": 'Password reset successful!', 'detail': 'success'}, status=status.HTTP_200_OK)
