import yaml


class Config:
    _config = {}

    @classmethod
    def pull(cls, app_id, param_id):
        return cls._config.get(app_id, {}).get(param_id, None)

    @classmethod
    def load(cls, rc_path='config.yaml'):
        with open(rc_path, 'r') as fp:
            loaded_config = yaml.load(fp, Loader=yaml.FullLoader)
            cls._config = loaded_config.get('config', {})