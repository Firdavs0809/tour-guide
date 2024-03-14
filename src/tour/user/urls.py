from django.urls import path

from .views import ProfilePageAPIView, GetProfileTickets

urlpatterns = [
    path('me/', ProfilePageAPIView.as_view(), name='user-profile-page'),
    path('me/tickets/', GetProfileTickets.as_view(), name='user-profile-packages'),
]
