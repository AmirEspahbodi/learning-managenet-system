from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.apis.views import (
    UserRegisterAPIView
)

# Create your tests here.
client = Client()
User = get_user_model()


class UserObjectTestCase(TestCase):
    def register_endpoint_request(self, data):
        return client.post(
            reverse('apis:accounts:user_register'),
            data=data
        )

    def test_register_endpoint_status_code(self):
        response = self.register_endpoint_request({
            "first_name": "test a",
            "last_name": "test",
            "username": "test1",
            "email": "test1@test.test",
            "phone_number": "+989013971301",
            "password1": "Abcd__1234",
            "password2": "Abcd__1234"
        })
        self.assertEqual(response.status_code, 201)

    def test_register_endpoint_user_created(self):
        response = self.register_endpoint_request({
            "first_name": "test a",
            "last_name": "test",
            "username": "test1",
            "email": "test1@test.test",
            "phone_number": "+989013971301",
            "password1": "Abcd__1234",
            "password2": "Abcd__1234"
        })
        try:
            user = User.objects.get(username="test1")
        except ObjectDoesNotExist:
            user = None
        self.assertNotEqual(user, None)

    def test_register_endpoint_unique_username(self):
        response = self.register_endpoint_request({
            "first_name": "test a",
            "last_name": "test",
            "username": "test1",
            "email": "test1@test.test",
            "phone_number": "+989013971301",
            "password1": "Abcd__1234",
            "password2": "Abcd__1234"
        })
        response2 = self.register_endpoint_request({
            "first_name": "test a",
            "last_name": "test",
            "username": "test1",
            "email": "test2@test.test",
            "phone_number": "+989013971302",
            "password1": "Abcd__1234",
            "password2": "Abcd__1234"
        })
        response3 = self.register_endpoint_request({
            "first_name": "test a",
            "last_name": "test",
            "username": "test3",
            "email": "test1@test.test",
            "phone_number": "+989013971303",
            "password1": "Abcd__1234",
            "password2": "Abcd__1234"
        })
        response4 = self.register_endpoint_request({
            "first_name": "test a",
            "last_name": "test",
            "username": "test4",
            "email": "test4@test.test",
            "phone_number": "+989013971301",
            "password1": "Abcd__1234",
            "password2": "Abcd__1234"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response3.status_code, 400)
        self.assertEqual(response4.status_code, 400)
