from django.urls import path
from .views import TourPackageListAPIView,TourPackageDetailAPIView

urlpatterns = [
    path('',TourPackageListAPIView.as_view()),
    path('<int:pk>/',TourPackageDetailAPIView.as_view()),

]