from django.urls import path
from .views import TourPackageListAPIView, TourPackageDetailAPIView, TourPackageSearchAPIView, GetCityAPIView, \
    ImageUploadView, ConfirmBookingAPIView,GetRelatedToursAPIView,GetFeaturedToursAPIView,GetFiltersAPIView

urlpatterns = [
    path('packages/top/', TourPackageListAPIView.as_view(), name='package-top'),

    path('packages/<int:pk>/', TourPackageDetailAPIView.as_view(), name='package-detail'),

    path('packages/search/', TourPackageSearchAPIView.as_view(), name='package-search'),

    path('packages/<int:pk>/image-upload/', ImageUploadView.as_view(), name='package-image-upload'),
    path('packages/<int:pk>/confirm-booking/', ConfirmBookingAPIView.as_view(), name='confirm-booking'),

    path('city/', GetCityAPIView.as_view(), name='get-city-name'),
    path('related-tours/', GetRelatedToursAPIView.as_view(), name='get-related-tours'),
    path('featured-tours/', GetFeaturedToursAPIView.as_view(), name='get-related-tours'),
    path('filters/', GetFiltersAPIView.as_view(), name='get-filters'),

]
