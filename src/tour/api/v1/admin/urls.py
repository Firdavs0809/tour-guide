from django.urls import path

from .views import AgencyRegisterAPIView, AgencyRegistrationActivationAPIView, TourPackageCreateAPIView, \
    GetAgencyAPIView, AgencyRetrieveUpdateDestroyAPIView
from tour.api.v1.auth.views import SignInView

urlpatterns = [
    path('agency/register/', AgencyRegisterAPIView.as_view(), name='agency-register'),
    path('agency/activation/', AgencyRegistrationActivationAPIView.as_view(), name='agency-activation'),
    path('agency/sign-in/', SignInView.as_view(), name='agency-sign-in'),

    # get agency details
    # path('agency/<int:pk>/', GetAgencyAPIView.as_view(), name='get-agency'),
    path('agency/<int:pk>/', AgencyRetrieveUpdateDestroyAPIView.as_view(), name='agency-retrieve-destroy-update'),

    path('agency/packages/create/', TourPackageCreateAPIView.as_view(), name='package-create'),
]
