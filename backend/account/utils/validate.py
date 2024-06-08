import traceback

from rest_api.exceptions import UnprocessableEntity
from django.core.exceptions import ValidationError
import inspect


class Validate:
    def __init__(self, detail: dict | None = None):
        self.error = detail if detail else {}

    async def validate(self, request_body_schema):
        if hasattr(request_body_schema, "custom_validation"):
            try:
                if inspect.iscoroutinefunction(request_body_schema.custom_validation):
                    await request_body_schema.custom_validation(self.error)
                else:
                    request_body_schema.custom_validation(self.error)
            except BaseException as exp:
                print(
                    f"Exception type: {type(exp)}\n"
                    + f"Exception args: {exp.args}\n"
                    + f"Exception traceback: {traceback.format_exc()}"
                )
                raise ValidationError(message="internal server error")
            if self.error:
                return {"errors": self.error}
        return {}
