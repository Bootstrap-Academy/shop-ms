from starlette import status

from api.exceptions.api_exception import APIException


class NotEnoughCoinsError(APIException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    detail = "Not enough coins"
    description = "The user does not have enough coins to perform this action."
