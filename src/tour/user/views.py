from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .serializers import ProfileSerializer
from ..agency.serializers import TourPackageSerializer,TourPackageSerializerList


class ProfilePageAPIView(GenericAPIView):
    serializer_class = ProfileSerializer

    def get(self, request):
        user = request.user
        profile = user.profile
        serializer = self.serializer_class(instance=profile)
        return Response({'user':serializer.data,})

    def put(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(instance=profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": 'success', 'detail': 'Updated successfully!'})

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()


class GetProfileTickets(GenericAPIView):
    serializer_class = TourPackageSerializerList

    def get(self, request):
        profile = request.user.profile
        packages = profile.packages.filter(
            starting_date__gte=timezone.now()
        )
        serializer = self.serializer_class(instance=packages, many=True)
        return Response({"count":len(packages),"tickets": serializer.data})
