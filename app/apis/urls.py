from django.urls import path, include
from apis.views import CheckConnection

urlpatterns = [
    path("is_up/", CheckConnection.as_view()),
    path(
        "accounts/", include(("accounts.apis.urls", "accounts"), namespace="accounts")
    ),
    path(
        "teachers/", include(("teachers.apis.urls", "teachers"), namespace="teachers")
    ),
    path("courses/", include(("courses.apis.urls", "courses"), namespace="courses")),
    path(
        "students/", include(("students.apis.urls", "students"), namespace="students")
    ),
]
