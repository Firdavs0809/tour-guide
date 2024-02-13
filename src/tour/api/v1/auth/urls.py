from django.urls import path
from .views import (SignInView, RefreshTokenView, LogoutView, RegistrationView, RegistrationActivationView,
                    ForgetPasswordView, ResetPasswordView,ConfirmPhoneNumberAPIView)

urlpatterns = [
    path('sign-up/', RegistrationView.as_view(), name='reg-login'),
    path('activation/', RegistrationActivationView.as_view(), name='reg-activation'),
    path('sign-in/', SignInView.as_view(), name='auth-login'),
    path('refresh-token/', RefreshTokenView.as_view(), name='auth-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),

    path('forget-password/', ForgetPasswordView.as_view(), name='auth-forget-pass'),
    path('confirm-phone/', ConfirmPhoneNumberAPIView.as_view(), name='auth-confirm-phone'),
    path('reset-password/', ResetPasswordView.as_view(), name='auth-reset-pass'),

]
