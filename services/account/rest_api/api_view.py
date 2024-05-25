from typing import TypeVar, Type, Generic

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import JsonResponse
from django.views.generic import View
import orjson
from pydantic import BaseModel
from pydantic_core import ValidationError as PydanticValidationError

from rest_api import status
from utils.validate import Validate
from asgiref.sync import async_to_sync

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class APIView(View):
    SCHEMA_CLASS: Type[BaseModel] | None = None

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(
                self, request.method.lower(), self.http_method_not_allowed
            )
        else:
            handler = self.http_method_not_allowed

        return handler(request, *args, **kwargs)


class CreateAPIView(View, Generic[CreateSchemaType]):
    SCHEMA_CLASS: Type[CreateSchemaType] | None = None
    request_body_schema: CreateSchemaType | None = None

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(
                self, request.method.lower(), self.http_method_not_allowed
            )
        else:
            handler = self.http_method_not_allowed

        return self.helper(handler, request, *args, **kwargs)

    async def helper(self, func, request, *args, **kwargs):
        if self.SCHEMA_CLASS is not None:
            try:
                self.request_body_schema = self.SCHEMA_CLASS(
                    **(orjson.loads(request.body.decode("utf-8"))),
                )
            except PydanticValidationError as exp:
                error_detail = {"error": {}}
                for err in exp.errors():
                    if err["loc"][0] not in error_detail["error"]:
                        error_detail["error"][err["loc"][0]] = [err["msg"]]
                    else:
                        error_detail["error"][err["loc"][0]].append(err["msg"])

                return JsonResponse(
                    status=status.HTTP_400_BAD_REQUEST, data=error_detail
                )
        else:
            raise DjangoValidationError(
                message="in CreateApiView you must determine SCHEMA_CLASS"
            )

        try:
            validation_errors = await Validate().validate(self.request_body_schema)
            if validation_errors:
                print(validation_errors)
                return JsonResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    data=validation_errors,
                )
        except DjangoValidationError as exp:
            return JsonResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={"error": "internal server error"},
            )

        return await func(request, *args, **kwargs)
