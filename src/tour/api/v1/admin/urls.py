from django.urls import path

from .views import AgencyRegisterAPIView,AgencyRegistrationActivationAPIView
from tour.api.v1.auth.views import SignInView


urlpatterns = [
    path('agency/register/', AgencyRegisterAPIView.as_view(), name='register-agency'),
    path('agency/activation/', AgencyRegistrationActivationAPIView.as_view(), name='activation-agency'),
    path('agency/sign-in/', SignInView.as_view(), name='sign-in-agency'),
]
