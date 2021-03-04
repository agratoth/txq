from txq_messages import SecureMessage


class CreateUserMessage(SecureMessage):
    fields = ['username', 'password', 'role', 'status']

    def __init__(self, **params):
        self.username = params.get('username')
        self.password = params.get('password')
        self.role = params.get('role')
        self.status = params.get('status')

        SecureMessage.__init__(self, **params)