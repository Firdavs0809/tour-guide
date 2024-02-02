from django.urls import path

from .views import ForgetPasswordView, ResetPasswordView,ProfilePageView

urlpatterns = [
    path('forget-password/', ForgetPasswordView.as_view(), name='user-forget-pass'),
    path('reset-password/', ResetPasswordView.as_view(), name='user-reset-pass'),
    path('profile-page/', ProfilePageView.as_view(), name='user-profile-page'),
]
