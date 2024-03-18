from django.urls import path

from .views import AgencyRegisterAPIView, AgencyRegistrationActivationAPIView, TourPackageCreateAPIView, \
    AgencyUpdateDestroyAPIView, AgencyListAPIView, TourPackageCreateNotifyAPIView, \
    TourPackageRetrieveUpdateDestroyAPIView, AgencyListWaitingAPIView, AgencyMeAPIView,AgencyAcceptAPIView
from tour.api.v1.auth.views import SignInView

urlpatterns = [
    path('agency/register/', AgencyRegisterAPIView.as_view(), name='agency-register'),
    path('agency/activation/', AgencyRegistrationActivationAPIView.as_view(), name='agency-activation'),
    path('agency/sign-in/', SignInView.as_view(), name='agency-sign-in'),

    # get agency details
    path('agency/', AgencyListAPIView.as_view(), name='get-agency-list'),
    path('agency/me', AgencyMeAPIView.as_view(), name='agency-me'),
    path('agency/waiting/', AgencyListWaitingAPIView.as_view(), name='get-agency-waiting'),
    path('agency/<int:pk>/', AgencyUpdateDestroyAPIView.as_view(), name='agency-destroy-update'),

    # accept company
    path('agency/<int:pk>/accept/', AgencyAcceptAPIView.as_view(), name='agency-accept'),

    path('agency/packages/create/', TourPackageCreateAPIView.as_view(), name='package-create'),
    path('agency/packages/<int:pk>/', TourPackageRetrieveUpdateDestroyAPIView.as_view(),
         name='package-update-delete-retrieve'),
    path('agency/packages/create/notify/', TourPackageCreateNotifyAPIView.as_view(), name='package-create-notify'),
]
