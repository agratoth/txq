class BaseMessage:
    fields = []

    def __init__(self, **params):
        pass

    @classmethod
    def get_fields(cls):
        fields = cls.fields

        for base_class in cls.__bases__:
            fields.extend(base_class.fields)

        return fields

    @classmethod
    def detect_cls(cls, name):
        if cls.__name__ == name:
            return cls
        for subclass in cls.__subclasses__():
            result = subclass.detect_cls(name)
            if result:
                return result
        return None

    @classmethod
    def get_cls(cls): return cls

    @classmethod
    def from_dictionary(cls, data={}):
        model_name = data.get('_model', None)
        if not model_name:
            return None

        model_cls = BaseMessage.detect_cls(model_name)

        if not model_cls:
            return None

        params = {}

        def deserialize(node):
            if isinstance(node, (str, int, float)):
                return node
            elif isinstance(node, list):
                return [deserialize(elem) for elem in node]
            elif isinstance(node, dict):
                if '_model' in node:
                    return BaseMessage.from_dictionary(node)
                else:
                    return {
                        elem_name: deserialize(elem)
                        for elem_name, elem
                        in node.items()
                    }
            return None

        for field in model_cls.get_fields():
            field_value = data.get(field)
            params[field] = deserialize(field_value)

        return model_cls(**params)

    @property
    def dictionary(self):
        result = {
            '_model': self.__class__.__name__,
        }

        def serialize(node):
            if isinstance(node, (str, int, float)):
                return node
            elif isinstance(node, list):
                return [serialize(elem) for elem in node]
            elif isinstance(node, dict):
                return {
                    elem_name: serialize(elem)
                    for elem_name, elem
                    in node.items()
                }
            elif isinstance(node, BaseMessage):
                return node.dictionary
            return None

        for field in self.get_fields():
            field_value = getattr(self, field)
            result[field] = serialize(field_value)

        return result