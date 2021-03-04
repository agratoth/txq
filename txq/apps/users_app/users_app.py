import jwt

from pynsodm.rethinkdb_ext import Storage
from pynsodm.json_ext import encoder

from txq.apps import App
from txq.pipes import BasePipe
from txq.config import Config

from txq_messages import ResponseMessage

from .messages import AuthUserMessage
from .messages import CreateUserMessage
from .messages import UpdateUserMessage
from .messages import VerifyTokenMessage
from .models import User


class UsersApp(App):
    app_id = 'users-app'

    def __init__(self):
        self._commands = BasePipe.create(
            self.app_id, 'commands', handler=self.handle_commands,
            messages=(
                AuthUserMessage,
                CreateUserMessage,
                UpdateUserMessage,
            ),
        )
        self._verify_token_pipe = BasePipe.create(
            self.app_id, 'verify-token', handler=self.verify_token,
            messages=(
                VerifyTokenMessage,
            ),
        )
        self._jwt_secret = Config.pull(self.app_id, 'jwt-secret')
        _root_user = Config.pull(self.app_id, 'root-user')
        _root_password = Config.pull(self.app_id, 'root-password')

        storage_config = Config.pull(self.app_id, 'storage')
        self._storage = Storage(
            models='User',
            **storage_config,
        )
        self._storage.connect()

        finded_users = User.find(username=_root_user)
        if len(finded_users) < 1:
            root_user = User(
                username=_root_user,
                password=_root_password,
                role='admin',
                status='active')
            root_user.save()

        App.__init__(self)

    async def handle_commands(self, message):
        if message.get_cls() == AuthUserMessage:
            return await self.auth_user(message)
        elif message.get_cls() == CreateUserMessage:
            return await self.create_user(message)

    async def auth_user(self, message: AuthUserMessage):
        user: User = User.get_by_username(message.username)
        if not user:
            return ResponseMessage.create_error(
                'UNKNOWN_USER', 'User is not found'
            )

        if not user.verify_password(message.password):
            return ResponseMessage.create_error(
                'UNKNOWN_USER', 'User is not found'
            )

        token = jwt.encode(
            user.unsensitive_dictionary,
            self._jwt_secret,
            algorithm='HS256',
            json_encoder=encoder()
        )
        return ResponseMessage.create_success(token)

    async def create_user(self, message: CreateUserMessage):
        user_data = await self._verify_token(message.token)
        if not user_data or user_data.get('role', None) != 'admin':
            return ResponseMessage.access_denied()

        if User.get_by_username(message.username):
            return ResponseMessage.create_error(
                'EXIST_USER', 'User already exist'
            )

        try:
            user = User(
                username=message.username,
                password=message.password,
                role=message.role,
                status=message.status,
            )
            user.save()
        except Exception:
            return ResponseMessage.create_error(
                'SAVING_USER_ERROR', 'Saving user error'
            )
        
        return ResponseMessage.create_success(
            user.unsensitive_dictionary
        )

    async def _verify_token(self, token):
        try:
            return jwt.decode(
                token,
                self._jwt_secret,
                verify=True,
                algorithms=['HS256'],
            )
        except Exception:
            return None

    async def verify_token(self, message: VerifyTokenMessage):
        user_data = await self._verify_token(message.token)

        if not user_data:
            return ResponseMessage.create_error(
                'INVALID_TOKEN', 'Invalid token'
            )
        return ResponseMessage.create_success(user_data)