import asyncio
import uvloop

from importlib import import_module

from txq.config import Config
from txq.pipes import BasePipe


class App:
    app_id = 'app'

    def __init__(self):
        self._pipes = {}

        for field in dir(self):
            field_value = getattr(self, field)
            if isinstance(field_value, BasePipe):
                self._pipes[field_value.pipe_id] = field_value

    async def _init_instances(self):
        self._instances = {}

        instances = Config.pull(self.app_id, 'subapps')
        if instances and isinstance(instances, dict):
            for instance_name, instance_config in instances.items():
                instance_package_name = instance_config.get('package')
                instance_cls_name = instance_config.get('class')

                instance_package = import_module(instance_package_name)
                instance_cls = getattr(instance_package, instance_cls_name)

                self._instances[instance_name] = instance_cls()
                await self._instances[instance_name]._init_pipes()

    async def _init_pipes(self):
        for _, pipe in self._pipes.items():
            await pipe.init_pipe(self)

    async def _shutdown_pipes(self):
        for _, pipe in self._pipes.items():
            await pipe.shutdown_pipe()

    async def _run(self):
        await self._init_instances()
        await self._init_pipes()

    def run(self):
        uvloop.install()

        self._loop = asyncio.get_event_loop()

        try:
            self._loop.run_until_complete(self._run())
            self._loop.run_forever()
        except KeyboardInterrupt:
            print("Received exit, exiting")
            self._loop.run_until_complete(self._shutdown_pipes())
            self._loop.close()
            exit()

    def get_pipe(self, pipe_id):
        return self._pipes.get(pipe_id, None)
    
    def get_instance(self, instance_id):
        return self._instances.get(instance_id, None)