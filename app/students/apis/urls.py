from django.urls import path
from students.apis.views import  StudentHomeAPIView, StudentCourseEnroleAPIView,\
    StudentCourseDetailAPIView, StudentSessionDetailAPIView, StudentGetFinancialAidAPIView

urlpatterns = [
     path('home/', StudentHomeAPIView.as_view(), name='home'),
     path('course/<int:course_id>/',
          StudentCourseDetailAPIView.as_view(), name="course_detail"),
     path('session/<int:session_id>/',
          StudentSessionDetailAPIView.as_view(), name="session_detail"),
     path('financial-aids/',
          StudentGetFinancialAidAPIView.as_view(), name="financial-aids"),
]
