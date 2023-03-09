from starlette import status

from api.exceptions.api_exception import APIException


class CreditNoteNotYetAvailableError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Credit note not yet available"
    description = "The requested credit note is not yet available."
