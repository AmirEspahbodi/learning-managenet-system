from django.urls import path
from students.apis.views import (
    StudentHomeAPIView,
    StudentCourseEnroleAPIView,
    StudentCourseDetailAPIView,
    StudentSessionDetailAPIView,
    StudentGetFinancialAidAPIView,
    StudentExamAPIView,
    StudentExamFTQuestionAPIView,
)

urlpatterns = [
    path("home/", StudentHomeAPIView.as_view(), name="home"),
    path(
        "course/<int:course_id>/",
        StudentCourseDetailAPIView.as_view(),
        name="course_detail",
    ),
    path(
        "session/<int:session_id>/",
        StudentSessionDetailAPIView.as_view(),
        name="session_detail",
    ),
    path(
        "financial-aids/",
        StudentGetFinancialAidAPIView.as_view(),
        name="financial-aids",
    ),
    path(
        "exam/<int:exam_id>/",
        StudentExamAPIView.as_view(),
        name="exam",
    ),
    path(
        "exam/ftquestion/<int:exam_ftquestion_id>/answer/",
        StudentExamFTQuestionAPIView.as_view(),
        name="exam-ftquestion-answer-create",
    ),
    path(
        "exam/ftquestion-answer/<int:member_exam_ftquestion_id>/",
        StudentExamFTQuestionAPIView.as_view(),
        name="exam-question-answer",
    ),
]
