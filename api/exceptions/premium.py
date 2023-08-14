from starlette import status

from api.exceptions.api_exception import APIException


class NoPremiumError(APIException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    detail = "No premium"
    description = "The user is not a premium member"
