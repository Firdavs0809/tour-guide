from django.urls import path
from .views import TourPackageListAPIView, TourPackageDetailAPIView, TourPackageSearchAPIView, GetCityMatchAPIView, \
    ImageUploadView, ConfirmBookingAPIView, GetRelatedToursCityAPIView, GetRelatedToursPeriodAPIView, \
    GetFeaturedToursAPIView, GetFiltersAPIView, GetPopularCityAPIView, GetCityFeaturesAPIView, ExcludeExpiredPackages, \
    SetAgencyIdAPIView, CategoryListAPIView, OptoinsListAPIView, GetTourPackageCategoryAPIView, \
    GetTourPackageOptionsAPIView, HotelsDetailAPIView, CategoryDetailAPIView, OptionsDetailAPIView, \
    GetTourPackageHotelsAPIView,GetCountryMatchAPIView

urlpatterns = [
    # gives the top package to a city(default)
    path('packages/top/', TourPackageListAPIView.as_view(), name='package-top'),

    # package detail
    path('packages/<int:pk>/', TourPackageDetailAPIView.as_view(), name='package-detail'),

    # filters and search works in that view
    path('packages/search/', TourPackageSearchAPIView.as_view(), name='package-search'),

    # before creating any instance that has image field, that view should be visited. (uploads the image to s3)
    path('image-upload/', ImageUploadView.as_view(), name='image-upload'),
    path('packages/<int:pk>/confirm-booking/', ConfirmBookingAPIView.as_view(), name='confirm-booking'),

    # get related tours in the detail view
    path('packages/<int:pk>/related-tours/city/', GetRelatedToursCityAPIView.as_view(), name='related-tours-city'),
    path('packages/<int:pk>/related-tours/period/', GetRelatedToursPeriodAPIView.as_view(),
         name='related-tours-period'),

    # get package category and options
    path('packages/<int:pk>/category/', GetTourPackageCategoryAPIView.as_view(), name='get-tour-category'),
    path('packages/<int:pk>/options/', GetTourPackageOptionsAPIView.as_view(), name='get-tour-options'),
    path('packages/<int:pk>/hotels/', GetTourPackageHotelsAPIView.as_view(), name='get-tour-hotels'),

    # get featured tours in Home page
    path('featured-tours/', GetFeaturedToursAPIView.as_view(), name='get-related-tours'),

    # data regarding city
    path('city/', GetCityMatchAPIView.as_view(), name='get-city-match'),
    path('country/', GetCountryMatchAPIView.as_view(), name='get-country-match'),
    path('city/popular/', GetPopularCityAPIView.as_view(), name='get-city-popular'),
    path('city/<int:pk>/filters/', GetFiltersAPIView.as_view(), name='get-filters'),
    path('city/<int:cityId>/features/', GetCityFeaturesAPIView.as_view(), name='get-features'),

    # removes the expired packages
    path('packages/expire/', ExcludeExpiredPackages.as_view(), name='auto-expire-packages'),

    # sets the chat id of the agency on start telegram
    path('set-chat-id/', SetAgencyIdAPIView.as_view(), name='set-chat-id'),

    # needed for tour package creation gives the existing options and category
    path('options/', OptoinsListAPIView.as_view(), name='get-options'),
    path('category/', CategoryListAPIView.as_view(), name='get-categories'),

    # get option, category, hotel detail views
    path('options/<int:pk>/', OptionsDetailAPIView.as_view(), name='get-option-detail'),
    path('category/<int:pk>/', CategoryDetailAPIView.as_view(), name='get-category-detail'),
    path('hotel/<int:pk>/', HotelsDetailAPIView.as_view(), name='get-hotel-detail'),

]
