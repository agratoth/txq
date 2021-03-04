from .base_pipe import BasePipe


class InternalPipe(BasePipe):
    def __init__(self, **params):
        self._instance = params.get('instance')
        self._instance_obj = None

        BasePipe.__init__(self, **params)

    def set_instance(self, instance_obj):
        self._instance_obj = instance_obj

    async def init_pipe(self, app):
        if self._direction == 'sender':
            self._instance_obj = app.get_instance(self._instance)

    async def send(self, message):
        if self._direction == 'sender' and self._instance_obj:
            pipe = self._instance_obj.get_pipe(self._pipe_id)
            return await pipe._receive(message)
        return None

    async def _receive(self, message):
        if self._direction == 'recipient':
            return await self._handler(message)