from django.urls import include, path
from .auth import urls as auth_urls
from tour.agency import urls as package_urls
from tour.user import urls as user_urls
from .admin import urls as admin_urls

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('', include(package_urls)),
    path('user/', include(user_urls)),
    path('admin/', include(admin_urls)),
]
