import nkeys
import base64

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

from .base_pipe import BasePipe


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
        print(self._direction)
        await self._client.connect(
            servers=[f'nats://{self._host}:{self._port}'],
            token=self._token,
        )

    async def shutdown_pipe(self):
        await self._client.close()