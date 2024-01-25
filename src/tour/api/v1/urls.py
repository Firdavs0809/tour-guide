from django.urls import include, path
from .auth import urls as auth_urls
# from src.tour.api.v1.auth import urls as auth_urls

urlpatterns = [
    path('auth/', include(auth_urls))
]
