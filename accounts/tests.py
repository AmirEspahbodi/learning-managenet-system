from django.test import TestCase, RequestFactory
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from accounts.api.views import (
    UserRegisterAPIView
)

# Create your tests here.
User = get_user_model()


class UserObjectTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def register_endpoint_request(self, data):
        request = self.factory.post(
            '127.0.0.1:8000/api/accounts/register/',
            content_type='application/json',
            data=data
        )
        response  = UserRegisterAPIView.as_view()(request)
        return response
    
    def test_register_endpoint_status_code(self):
        """send a post request to /api/accounts/register/"""
        response = self.register_endpoint_request({
                "first_name":"test1",
                "last_name":"test",
                "username":"test1",
                "email":"test1@test.test",
                "phone_number":"+989013971301",
                "password1":"Abcd_1234",
                "password2":"Abcd_1234"
            })
        self.assertEqual(response.status_code, 200)

        
    def test_register_endpoint_user_created(self):
        response = self.register_endpoint_request({
                "first_name":"test1",
                "last_name":"test",
                "username":"test1",
                "email":"test1@test.test",
                "phone_number":"+989013971301",
                "password1":"Abcd_1234",
                "password2":"Abcd_1234"
            })
        try:
            user = User.objects.get(username = "test1")
        except ObjectDoesNotExist:
            user = None
        self.assertNotEqual(user, None)


    def test_register_endpoint_unique_username(self):
        response = self.register_endpoint_request({
            "first_name":"test1",
            "last_name":"test",
            "username":"test1",
            "email":"test1@test.test",
            "phone_number":"+989013971301",
            "password1":"Abcd_1234",
            "password2":"Abcd_1234"
        })
        response2 = self.register_endpoint_request({
            "first_name":"test1",
            "last_name":"test",
            "username":"test1",
            "email":"test2@test.test",
            "phone_number":"+989013971302",
            "password1":"Abcd_1234",
            "password2":"Abcd_1234"
        })
        response3 = self.register_endpoint_request({
            "first_name":"test1",
            "last_name":"test",
            "username":"test2",
            "email":"test1@test.test",
            "phone_number":"+989013971302",
            "password1":"Abcd_1234",
            "password2":"Abcd_1234"
        })
        response4 = self.register_endpoint_request({
            "first_name":"test1",
            "last_name":"test",
            "username":"test2",
            "email":"test2@test.test",
            "phone_number":"+989013971301",
            "password1":"Abcd_1234",
            "password2":"Abcd_1234"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response2.status_code, 409)
        self.assertEqual(response3.status_code, 409)
        self.assertEqual(response4.status_code, 409)
