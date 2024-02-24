from django.urls import path
from .views import TourPackageListAPIView, TourPackageDetailAPIView, TourPackageSearchAPIView, GetCityMatchAPIView, \
    ImageUploadView, ConfirmBookingAPIView, GetRelatedToursAPIView, GetFeaturedToursAPIView, GetFiltersAPIView, \
    GetPopularCityAPIView, GetCityFeaturesAPIView, ExcludeExpiredPackages, SetAgencyIdAPIView, GetCategoryAPIView, \
    GetOptionsAPIView, GetTourCategoryAPIView, GetTourOptionsAPIView

urlpatterns = [
    path('packages/top/', TourPackageListAPIView.as_view(), name='package-top'),

    path('packages/<int:pk>/', TourPackageDetailAPIView.as_view(), name='package-detail'),

    path('packages/search/', TourPackageSearchAPIView.as_view(), name='package-search'),

    path('image-upload/', ImageUploadView.as_view(), name='image-upload'),
    path('packages/<int:pk>/confirm-booking/', ConfirmBookingAPIView.as_view(), name='confirm-booking'),

    path('packages/<int:pk>/related-tours/', GetRelatedToursAPIView.as_view(), name='get-related-tours'),

    # get package category and options
    path('packages/<int:pk>/category/', GetTourCategoryAPIView.as_view(), name='get-tour-category'),
    path('packages/<int:pk>/options/', GetTourOptionsAPIView.as_view(), name='get-tour-options'),

    path('featured-tours/', GetFeaturedToursAPIView.as_view(), name='get-related-tours'),

    path('city/', GetCityMatchAPIView.as_view(), name='get-city-match'),
    path('city/popular/', GetPopularCityAPIView.as_view(), name='get-city-popular'),
    path('city/<int:pk>/filters/', GetFiltersAPIView.as_view(), name='get-filters'),
    path('city/<int:cityId>/features/', GetCityFeaturesAPIView.as_view(), name='get-features'),

    path('packages/expire/', ExcludeExpiredPackages.as_view(), name='auto-expire-packages'),

    path('set-chat-id/', SetAgencyIdAPIView.as_view(), name='set-chat-id'),

    # needed for tour package creation
    path('packages/options/', GetOptionsAPIView.as_view(), name='get-options'),
    path('packages/category/', GetCategoryAPIView.as_view(), name='get-categories'),

]
