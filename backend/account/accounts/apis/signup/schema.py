from pydantic import BaseModel, EmailStr, ConfigDict, PrivateAttr
from accounts.models import User
from permissions.models import RoleCreationPrivilegeStatus, Role
from utils.password_validation import validate_password


class SignupL1Schema(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    roles: list[int]
    phone_number: str
    password1: str
    password2: str
    _db_roles: list[Role] = PrivateAttr(default=[])

    async def custom_validation(self, error):
        # validate password
        if self.password1 != self.password2:
            if "password1" not in error:
                error["password1"] = ["passwords do not match"]
            else:
                error["password1"].append("passwords do not match")
            password_error = validate_password(
                self.password1,
                self.first_name,
                self.last_name,
                self.email,
                self.phone_number,
            )
            if password_error:
                if "password1" not in error:
                    error["password1"] = password_error
                else:
                    error["password1"].extend(password_error)
        print(error)

        user = await User.objects.filter(username=self.username).afirst()
        if user is not None:
            error["username"] = ["user already exists with this username"]

        user = await User.objects.filter(phone_number=self.phone_number).afirst()
        if user is not None:
            error["phone_number"] = ["user already exists with this phone number"]

        user = await User.objects.filter(email=self.email).afirst()
        if user is not None:
            error["email"] = ["user already exists with this email"]

        async for role in Role.objects.filter(id__in=self.roles).aiterator():
            self._db_roles.append(role)

        roles_set = set([role for role in self.roles])
        if set([db_role.id for db_role in self._db_roles]) & roles_set == roles_set:
            error["roles"] = ["invalid roles"]

        for db_role in self._db_roles:
            if db_role.creation_privilege != RoleCreationPrivilegeStatus.OPEN:
                if "roles" in error:
                    error["roles"].append(
                        "you are not allowed to sign up with this role(s)."
                    )
                else:
                    error["roles"] = [
                        "you are not allowed to sign up with this role(s)."
                    ]
                break
        return error

    model_config = ConfigDict(extra="forbid")


class PhoneNumberScheme(BaseModel):
    as_international: str
    as_e164: str
    as_national: str
    as_rfc3966: str
    model_config = ConfigDict(
        extra="allow",
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class UserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    username: str
    phone_number: PhoneNumberScheme

    model_config = ConfigDict(
        extra="allow",
        from_attributes=True,
        arbitrary_types_allowed=True,
    )
