from pydantic import BaseModel, EmailStr, ConfigDict
from accounts.models import User
from accounts.validators import validate_password


class SignupL1Schema(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    phone_number: str | None = None
    role: int
    password1: str
    password2: str

    async def custom_validation(self, error):
        # validate password
        if self.password1 != self.password2:
            if "password1" not in error:
                error["password1"] = ["passwords do not match"]
            else:
                error["password1"].append("passwords do not match")
            password_error = validate_password(error["password1"])
            if password_error:
                if "password1" not in error:
                    error["password1"] = password_error
                else:
                    error["password1"].extend(password_error)
        user = User.objects.get(username=self.username)
        if user is not None:
            error["username"] = ["user already exists with this username"]

        user = User.objects.get(username=self.phone_number)
        if user is not None:
            error["username"] = ["user already exists with this phone number"]

        user = User.objects.get(username=self.email)
        if user is not None:
            error["username"] = ["user already exists with this email"]

        return error

    model_config = ConfigDict(extra="forbid")
