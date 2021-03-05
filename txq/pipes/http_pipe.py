import json

from aiohttp import web
from txq.logging import get_logger
from txq_messages import BaseMessage, ResponseMessage, SecureMessage

from .base_pipe import BasePipe


logger = get_logger(__name__)

class HTTPPipe(BasePipe):
    def __init__(self, **params):
        self._host = params.get('host')
        self._port = int(params.get('port'))
        self._endpoint = params.get('endpoint')

        BasePipe.__init__(self, **params)

    async def init_pipe(self, app):
        await BasePipe.init_pipe(self, app)

        if self._direction == 'sender':
            pass
        elif self._direction == 'recipient':
            self._server = web.Server(self._receive)
            self._runner = web.ServerRunner(self._server)
            await self._runner.setup()

            self._site = web.TCPSite(self._runner, self._host, self._port)
            await self._site.start()
        logger.info(f'HTTPPipe [{self._app_id}:{self._pipe_id}] - Init complete')

    async def shutdown_pipe(self):
        await self._site.stop()
        await self._runner.shutdown()
        await self._server.shutdown()

        logger.info(f'HTTPPipe [{self._app_id}:{self._pipe_id}] - Shutdown complete')

    async def send(self, message):
        pass

    async def _receive(self, request):
        if self._direction != 'recipient':
            return None

        if request.method not in ('POST', 'OPTIONS') or request.path != '/_pipe':
            return web.Response(status=400, text='HTTP Method or url path is not allowed!')

        if request.method == 'OPTIONS':
            pipe_info = {
                'allowed_messages': [m.__name__ for m in self._messages],
            }
            return web.Response(
                status=200,
                content_type='application/json',
                body=json.dumps(
                    ResponseMessage.create_success(pipe_info).dictionary
                )
            )

        try:
            data = await request.json()
            if '_model' not in data:
                raise Exception()
            message_cls = BaseMessage.detect_cls(data.get('_model'))
            if not message_cls:
                raise Exception()
        except Exception:
            return web.Response(
                status=200,
                content_type='application/json',
                body=json.dumps(
                    ResponseMessage.create_error(
                        'BAD_REQUEST', 'Bad request body!'
                    ).dictionary
                )
            )

        if message_cls not in self._messages:
            return web.Response(
                status=200,
                content_type='application/json',
                body=json.dumps(
                    ResponseMessage.create_error(
                        'BAD_MESSAGE_TYPE', 'This message is not allowed for the current pipe'
                    ).dictionary
                )
            )

        message = message_cls.from_dictionary(data)

        if not message:
            return web.Response(
                status=200,
                content_type='application/json',
                body=json.dumps(
                    ResponseMessage.create_error(
                        'BAD_MESSAGE_BODY', 'Error deserializing message'
                    ).dictionary
                )
            )

        result = await self._handler(message)
        return web.Response(
            status=200,
            content_type='application/json',
            body=json.dumps(result.dictionary),
        )