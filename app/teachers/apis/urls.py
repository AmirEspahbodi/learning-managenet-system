from django.urls import path
from .views import (
    TeacherCourseDetailAPIView,
    TeacherFinancialAidsAPIView,
    TeacherSessionDetailAPIView,
    TeacherHomeAPIView,
    TeacherExamCreateAPIView,
    TeacherExamQuestionAPIView,
    TeacherExamFtQuestionAnswerAPIView,
    TeacherMemberExamFtQuestionAPIView,
)


urlpatterns = [
    path("home/", TeacherHomeAPIView.as_view(), name="home"),
    path(
        "course/<int:course_id>/",
        TeacherCourseDetailAPIView.as_view(),
        name="course_detail",
    ),
    path(
        "session/<int:session_id>/",
        TeacherSessionDetailAPIView.as_view(),
        name="course_detail",
    ),
    path(
        "course/<int:course_id>/financial-aids/",
        TeacherFinancialAidsAPIView.as_view(),
        name="student_financial_aids",
    ),
    path(
        "session/<int:session_id>/exam/create",
        TeacherExamCreateAPIView.as_view(),
        name="exam_create",
    ),
    path(
        "exam/<int:exam_id>/",
        TeacherExamCreateAPIView.as_view(),
        name="exam_get",
    ),
    path(
        "exam/<int:exam_id>/ftquestion/create/",
        TeacherExamQuestionAPIView.as_view(),
        name="exam_ftquestion_create",
    ),
    path(
        "exam/ftquestion/<int:exam_ftquestion_id>/",
        TeacherExamQuestionAPIView.as_view(),
        name="exam_ftquestion_get",
    ),
    path(
        "exam/ftquestion/<int:exam_ftquestion_id>/answer/create/",
        TeacherExamFtQuestionAnswerAPIView.as_view(),
        name="exam_ftquestion_answer_create",
    ),
    path(
        "exam/ftquestion/member/answer/<int:member_exam_ftquestion_id>/score/",
        TeacherMemberExamFtQuestionAPIView.as_view(),
        name="exam_ftquestion_member_answer_score",
    ),
]
