from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import ProfileSerializer
from ..agency.models import TourPackage
from ..agency.serializers import TourPackageSerializer
from ..oauth2.authentication import OAuth2Authentication
from .models import User


class ProfilePageView(GenericAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (AllowAny,)

    # permission_classes = (IsAuthenticated,)
    # authentication_classes = (OAuth2Authentication,)

    # def get(self, request):
    #     profile = request.user.profile
    #     serializer = self.serializer_class(instance=profile)
    #     return Response({'data': serializer.data})
    def get(self, request):
        user = User.objects.get(id=4)
        profile = user.profile
        serializer = self.serializer_class(instance=profile)
        user_packages = TourPackageSerializer(profile.packages,many=True).data
        return Response({'data': {"user":serializer.data,'packages':user_packages}})

    def put(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(instance=profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": 'success', 'detail': 'Updated successfully!'})

    def delete(self, request):
        user = request.user
        user.delete()
