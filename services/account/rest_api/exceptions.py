from django.http import JsonResponse
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from rest_api.helpers import ReturnDict, ReturnList
from rest_api import status


def _get_error_details(data, default_code=None):
    """
    Descend into a nested data structure, forcing any
    lazy translation strings or strings into `ErrorDetail`.
    """
    if isinstance(data, (list, tuple)):
        ret = [_get_error_details(item, default_code) for item in data]
        if isinstance(data, ReturnList):
            return ReturnList(ret, serializer=data.serializer)
        return ret
    elif isinstance(data, dict):
        ret = {
            key: _get_error_details(value, default_code) for key, value in data.items()
        }
        if isinstance(data, ReturnDict):
            return ReturnDict(ret, serializer=data.serializer)
        return ret

    text = force_str(data)
    code = getattr(data, "code", default_code)
    return ErrorDetail(text, code)


def _get_codes(error):
    if isinstance(error, list):
        return [_get_codes(item) for item in error]
    elif isinstance(error, dict):
        return {key: _get_codes(value) for key, value in error.items()}
    return error.code


def _get_full_details(error):
    if isinstance(error, list):
        return [_get_full_details(item) for item in error]
    elif isinstance(error, dict):
        return {key: _get_full_details(value) for key, value in error.items()}
    return {"message": error, "code": error.code}


class ErrorDetail(str):
    """
    A string-like object that can additionally have a code.
    """

    code = None

    def __new__(cls, string, code=None):
        self = super().__new__(cls, string)
        self.code = code
        return self

    def __eq__(self, other):
        result = super().__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        try:
            return result and self.code == other.code
        except AttributeError:
            return result

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __repr__(self):
        return "ErrorDetail(string=%r, code=%r)" % (
            str(self),
            self.code,
        )

    def __hash__(self):
        return hash(str(self))


class APIException(Exception):
    """
    Base class for REST framework exceptions.
    Subclasses should provide `.status_code` and `.default_detail` properties.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _("A server error occurred.")
    default_code = "error"

    def __init__(self, error=None, code=None):
        if error is None:
            error = self.default_detail
        if code is None:
            code = self.default_code

        self.error = _get_error_details(error, code)

    def __str__(self):
        return str(self.error)

    def get_codes(self):
        """
        Return only the code part of the error details.

        Eg. {"name": ["required"]}
        """
        return _get_codes(self.error)

    def get_full_details(self):
        """
        Return both the message & code parts of the error details.

        Eg. {"name": [{"message": "This field is required.", "code": "required"}]}
        """
        return _get_full_details(self.error)


class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Invalid input.")
    default_code = "invalid"

    def __init__(self, error=None, code=None):
        if error is None:
            error = self.default_detail
        if code is None:
            code = self.default_code

        # For validation failures, we may collect many error together,
        # so the details should always be coerced to a list if not already.
        if isinstance(error, tuple):
            error = list(error)
        elif not isinstance(error, dict) and not isinstance(error, list):
            error = [error]

        self.error = _get_error_details(error, code)


class ParseError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Malformed request.")
    default_code = "parse_error"


class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Incorrect authentication credentials.")
    default_code = "authentication_failed"


class NotAuthenticated(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Authentication credentials were not provided.")
    default_code = "not_authenticated"


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("You do not have permission to perform this action.")
    default_code = "permission_denied"


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("Not found.")
    default_code = "not_found"


class MethodNotAllowed(APIException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = _('Method "{method}" not allowed.')
    default_code = "method_not_allowed"

    def __init__(self, method, error=None, code=None):
        if error is None:
            error = force_str(self.default_detail).format(method=method)
        super().__init__(error, code)


class NotAcceptable(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = _("Could not satisfy the request Accept header.")
    default_code = "not_acceptable"

    def __init__(self, error=None, code=None, available_renderers=None):
        self.available_renderers = available_renderers
        super().__init__(error, code)


class UnprocessableEntity(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = _("Error in validation.")
    default_code = "unprocessable_entity"

    def __init__(self, error=None, code=None, available_renderers=None):
        self.available_renderers = available_renderers
        super().__init__(error, code)


class UnsupportedMediaType(APIException):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    default_detail = _('Unsupported media type "{media_type}" in request.')
    default_code = "unsupported_media_type"

    def __init__(self, media_type, error=None, code=None):
        if error is None:
            error = force_str(self.default_detail).format(media_type=media_type)
        super().__init__(error, code)


def server_error(request, *args, **kwargs):
    """
    Generic 500 error handler.
    """
    data = {"error": "Internal Server Error"}
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def bad_request(request, exception, *args, **kwargs):
    """
    Generic 400 error handler.
    """
    data = {"error": "Bad Request"}
    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
