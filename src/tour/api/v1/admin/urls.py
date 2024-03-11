from django.urls import path

from .views import AgencyRegisterAPIView, AgencyRegistrationActivationAPIView, TourPackageCreateAPIView, \
    GetAgencyAPIView,GetAgencyListAPIView
from tour.api.v1.auth.views import SignInView

urlpatterns = [
    path('agency/register/', AgencyRegisterAPIView.as_view(), name='agency-register'),
    path('agency/activation/', AgencyRegistrationActivationAPIView.as_view(), name='agency-activation'),
    path('agency/sign-in/', SignInView.as_view(), name='agency-sign-in'),

    # get agency details
    path('agency/<int:pk>/', GetAgencyAPIView.as_view(), name='get-agency'),
    path('agency/', GetAgencyListAPIView.as_view(), name='get-agency-list'),

    path('agency/packages/create/', TourPackageCreateAPIView.as_view(), name='package-create'),
]
