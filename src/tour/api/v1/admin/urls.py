from django.urls import path

from .views import AgencyRegisterAPIView, AgencyRegistrationActivationAPIView, TourPackageCreateAPIView, \
    AgencyRetrieveUpdateDestroyAPIView, AgencyListAPIView
from tour.api.v1.auth.views import SignInView

urlpatterns = [
    path('agency/register/', AgencyRegisterAPIView.as_view(), name='agency-register'),
    path('agency/activation/', AgencyRegistrationActivationAPIView.as_view(), name='agency-activation'),
    path('agency/sign-in/', SignInView.as_view(), name='agency-sign-in'),

    # get agency details
    path('agency/', AgencyListAPIView.as_view(), name='get-agency-list'),
    path('agency/<int:pk>/', AgencyRetrieveUpdateDestroyAPIView.as_view(), name='agency-retrieve-destroy-update'),

    path('agency/packages/create/', TourPackageCreateAPIView.as_view(), name='package-create'),
]
