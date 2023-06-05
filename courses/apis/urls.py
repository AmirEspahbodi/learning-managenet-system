from django.urls import path
from .views import CourseSearchAPIView, CourseSearchDetailAPIView, \
    CourseEnrollAPIView

urlpatterns = [
    path('search/', CourseSearchAPIView.as_view(), name="search"),
    path('search/<int:course_id>/',
         CourseSearchDetailAPIView.as_view(), name="search_detail"),
    path('enroll/<int:course_id>/',
         CourseEnrollAPIView.as_view(), name="search_detail")
]
