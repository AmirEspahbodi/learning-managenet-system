from django.urls import path
from .views import CourseSearchAPIView, CourseSearchDetailAPIView
from .student_views import FinancialAidsAPIView

urlpatterns = [
    path('search/', CourseSearchAPIView.as_view(), name="search"),
    path('search/<int:course_id>/',
         CourseSearchDetailAPIView.as_view(), name="search_detail"),
    path('<int:course_id>/financial-aid/',
         FinancialAidsAPIView.as_view(), name="financial-aid")
]
