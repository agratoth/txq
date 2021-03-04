from .base_message import BaseMessage


class SecureMessage(BaseMessage):
    fields = ['token']

    def __init__(self, **params):
        self.token = params.get('token')

        BaseMessage.__init__(self, **params)