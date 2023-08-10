from django.urls import path
from .views import CourseSearchAPIView, CourseSearchDetailAPIView
from .student_views import StudentCourseEnrole

urlpatterns = [
    path('search/', CourseSearchAPIView.as_view(), name="search"),
    path('search/<int:course_id>/',
         CourseSearchDetailAPIView.as_view(), name="search_detail"),
    path('<int:course_id>/enroll/',
         StudentCourseEnrole.as_view(), name="student_enroll"),
]
