from starlette import status

from api.exceptions.api_exception import APIException


class NotEnoughCoinsError(APIException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    detail = "Not enough coins"
    description = "The user does not have enough coins to perform this action."


class CouldNotCreateOrderError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Could not create order"
    description = "The order could not be created."


class OrderNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Order not found"
    description = "The order does not exist."


class CouldNotCaptureOrderError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Could not capture order"
    description = "The order could not be captured."
