from txq_messages import BaseMessage


class AuthUserMessage(BaseMessage):
    fields = ['username', 'password']

    def __init__(self, **params):
        self.username = params.get('username')
        self.password = params.get('password')

        BaseMessage.__init__(self, **params)