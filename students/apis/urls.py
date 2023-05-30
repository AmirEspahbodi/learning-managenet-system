from django.urls import path
from students.apis.views import StudentRegisterAPIView

urlpatterns = [
    path('register/', StudentRegisterAPIView.as_view(), name='register')
]