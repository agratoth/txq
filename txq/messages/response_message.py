from .base_message import BaseMessage


class ResponseMessage(BaseMessage):
    fields = ['status', 'result', 'error', 'error_code']

    def __init__(self, **params):
        self.status = params.get('status')
        self.result = params.get('result')
        self.error = params.get('error')
        self.error_code = params.get('error_code')

    @classmethod
    def create_error(cls, error_code, error):
        return ResponseMessage(
            status=False,
            result=None,
            error_code=error_code,
            error=error,
        )

    @classmethod
    def create_success(cls, result):
        return ResponseMessage(
            status=True,
            result=result,
            error_code=None,
            error=None,
        )

    @classmethod
    def access_denied(cls):
        return ResponseMessage(
            status=False,
            result=None,
            error_code='ACCESS_DENIED',
            error='Access denied',
        )