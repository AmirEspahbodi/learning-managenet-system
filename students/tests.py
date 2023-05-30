from django.test import TestCase, Client
from django.urls import reverse
from students.models import Student
from django.contrib.auth import get_user_model

# Create your tests here.
client = Client()
User = get_user_model()

class StudentRegister(TestCase):
    def setUp(self):
        self.response = client.post(
            reverse("apis:students:register"), 
            {
                "first_name": "amir",
                "last_name": "espahbodi",
                "email": "amir@amir.amir",
                "username": "amir",
                "phone_number": "+989013971301",
                "password1": "Abcd__8731",
                "password2": "Abcd__8731",
                "school": "some",
                "degree": 1,
                "field": "some"
            }
        )
        
    def test_user_created_has_student_role(self):
        user = User.objects.get(username='amir')
        student = Student.objects.get(user=user)
        self.assertNotEqual(student, None)
        self.assertNotEqual(user, None)
        self.assertEqual(user.is_student(), True)
