from django.urls import path
from students.apis.views import (
    StudentHomeAPIView,
    StudentCourseDetailAPIView,
    StudentSessionDetailAPIView,
    StudentGetFinancialAidAPIView,
    StudentExamAPIView,
    StudentExamFTQuestionAPIView,
    StudentAssignmentAPIView,
    StudentAssignmentFTQuestionAPIView,
    StudentContentAPIView,
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
    path(
        "assignment/<int:assignment_id>/",
        StudentAssignmentAPIView.as_view(),
        name="assignment",
    ),
    path(
        "assignment/ftquestion/<int:assignment_ftquestion_id>/answer/",
        StudentAssignmentFTQuestionAPIView.as_view(),
        name="assignment-ftquestion-answer-create",
    ),
    path(
        "assignment/ftquestion-answer/<int:member_assignment_ftquestion_id>/",
        StudentAssignmentFTQuestionAPIView.as_view(),
        name="assignment-question-answer",
    ),
    path("content/<int:content_id>/", StudentContentAPIView.as_view(), name="content"),
]
