import nkeys
import base64
import json

from txq.logging import get_logger
from txq_messages import BaseMessage, ResponseMessage
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

from .base_pipe import BasePipe


logger = get_logger(__name__)


class NATSPipe(BasePipe):
    def __init__(self, **params):
        self._queue = params.get('pipe')
        broker_params = params.get('broker', {})
        self._host = broker_params.get('host')
        self._port = int(broker_params.get('port'))
        self._token = broker_params.get('token')

        self._client = NATS()

        BasePipe.__init__(self, **params)

    async def init_pipe(self, app):
        await BasePipe.init_pipe(self, app)

        await self._client.connect(
            servers=[f'nats://{self._host}:{self._port}'],
            token=self._token,
        )
        if self._direction == 'recipient':
            await self._client.subscribe(
                self._queue,
                cb=self._receive,
            )
        logger.info(f'NATSPipe [{self._app_id}:{self._pipe_id}] - Init complete')

    async def shutdown_pipe(self):
        await self._client.close()
        logger.info(f'NATSPipe [{self._app_id}:{self._pipe_id}] - Shutdown complete')

    async def send(self, message):
        result = await self._client.request(
            self._queue,
            json.dumps(message.dictionary).encode(),
            timeout=180
        )
        
        data = result.data

        try:
            response = BaseMessage.from_dictionary(json.loads(data))
        except Exception:
            response = ResponseMessage.create_error(
                'BAD_COMMAND', 'Bad command'
            )

        return response

    async def _receive(self, request):
        reply = request.reply
        data = request.data

        try:
            message = BaseMessage.from_dictionary(json.loads(data))
            result = await self._handler(message)
            response = ResponseMessage.create_success(result)
        except Exception:
            response = ResponseMessage.create_error(
                'BAD_COMMAND', 'Bad command'
            )

        await self._client.publish(
            reply, json.dumps(response.dictionary).encode()
        )