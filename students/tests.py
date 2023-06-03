from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from students.models import Student
from django.contrib.auth import get_user_model

# Create your tests here.
clientAPI = APIClient()
User = get_user_model()

class StudentRegister(TestCase):
    def setUp(self):
        self.student_data = \
        {
            "school": "some",
            "degree": 1,
            "field": "some",
            "user": {
                "first_name": "test a",
                "last_name": "test",
                "email": "test1@test.test",
                "username": "test1",
                "phone_number": "+989013971501",
                "password1": "Abcd__8731",
                "password2": "Abcd__8731"
            }
        }
        self.student_register_url = reverse("apis:students:register")
        
    def test_user_created_has_student_role(self):
        response = clientAPI.post(
            self.student_register_url, 
            self.student_data,
            format='json'
        )
        user = User.objects.get(username='test1')
        student = Student.objects.get(user=user)
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(student, None)
        self.assertNotEqual(user, None)
        self.assertEqual(user.is_student(), True)
