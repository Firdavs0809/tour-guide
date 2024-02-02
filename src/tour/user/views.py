from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import ProfilePageSerializer, ForgetPasswordSerializer, ResetPasswordSerializer


class ProfilePageView(GenericAPIView):
    serializer_class = ProfilePageSerializer
    authentication_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = self.serializer_class(instance=request.user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


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

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # user = serializer.save()
        return Response({"password": 'Password reset successful!', 'detail': 'success'}, status=status.HTTP_200_OK)
