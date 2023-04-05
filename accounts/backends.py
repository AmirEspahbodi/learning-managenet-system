from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class MyModelBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, phone_number=None, password=None, **kwargs):
        if not ((username or email or phone_number) and password):
            return 
        try:
            if username:
                user = UserModel.objects.get(username=username)
            elif email:
                user = UserModel.objects.get(email=email)
            elif phone_number:
                user = UserModel.objects.get(phone_number=phone_number)

        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user