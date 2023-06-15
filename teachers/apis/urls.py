from django.urls import path
from .views import TeacherCourseDetailAPIView

urlpatterns = [
    path('course/<int:course_id>/',
         TeacherCourseDetailAPIView.as_view(), name="course_detail")
]
