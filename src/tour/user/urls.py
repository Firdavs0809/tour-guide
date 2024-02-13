from django.urls import path

from .views import ProfilePageView

urlpatterns = [
    path('me/', ProfilePageView.as_view(), name='user-profile-page'),
]
