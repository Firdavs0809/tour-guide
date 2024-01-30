from django.urls import path
from .views import TourPackageListAPIView,TourPackageDetailAPIView,TourPackageSearchAPIView

urlpatterns = [
    path('',TourPackageListAPIView.as_view()),
    path('<int:pk>/',TourPackageDetailAPIView.as_view()),
    path('search/',TourPackageSearchAPIView.as_view()),

]