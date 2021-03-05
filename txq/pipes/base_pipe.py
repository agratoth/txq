from txq.config import Config


class BasePipe:
    _pipe_cls = {
        'http': 'HTTPPipe',
        'nats': 'NATSPipe',
        'internal': 'InternalPipe',
    }

    def __init__(self, **params):
        self._pipe_id = params.get('pipe_id')
        self._handler = params.get('handler')
        self._messages = params.get('messages')
        self._direction = params.get('direction')

    @classmethod
    def get_subclass(cls, name):
        for subclass in cls.__subclasses__():
            if subclass.__name__ == name:
                return subclass
        return None

    @classmethod
    def create(cls, app_id, pipe_id, **params):
        pipe_config = Config.pull(app_id, pipe_id)
        pipe_class_name = cls._pipe_cls.get(pipe_config.get('type'))
        pipe_class = cls.get_subclass(pipe_class_name)

        return pipe_class(
            pipe_id=pipe_id,
            **params,
            **pipe_config,
        )

    @property
    def pipe_id(self): return self._pipe_id

    async def init_pipe(self, app):
        self._app_id = app.app_id

    async def shutdown_pipe(self):
        pass

    async def send(self, message):
        pass

    async def _receive(self, message):
        pass