from django.urls import path
from .views import TourPackageListAPIView,TourPackageDetailAPIView,TourPackageSearchAPIView

urlpatterns = [
    path('home/',TourPackageListAPIView.as_view()),
    path('<int:pk>/',TourPackageDetailAPIView.as_view()),
    path('',TourPackageSearchAPIView.as_view()),

]