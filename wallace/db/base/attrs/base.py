from wallace.db.base.attrs.interface import ModelInterface
from wallace.db.base.attrs.interface import is_default_valid
from wallace.db.base.attrs.typecast_mixin import TypecastMixin
from wallace.db.base.attrs.validator_mixin import ValidatorMixin


class _Base(type):

    def __new__(cls, name, bases, dct):
        default = dct.get('default')
        if default and callable(default):
            dct['default'] = staticmethod(default)

        validators = dct.get('validators', ())
        if validators:
            dct['validators'] = cls._merge_base_validators(bases, validators)

        return super(_Base, cls).__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(_Base, cls).__init__(name, bases, dct)
        is_default_valid(cls.default, cls.cast, cls.validators)

    @staticmethod
    def _merge_base_validators(bases, validators):
        all_validators = []
        for base in bases:
            for val in getattr(base, 'validators', ()):
                all_validators.append(val)

        for val in validators:
            all_validators.append(val)

        return tuple(all_validators)


class DataType(ModelInterface, ValidatorMixin, TypecastMixin):

    __metaclass__ = _Base

    def __init__(self, validators=None, **kwargs):
        ModelInterface.__init__(self, **kwargs)
        ValidatorMixin.__init__(self, validators)
        TypecastMixin.__init__(self)

        is_default_valid(self.default, self.cast, self.validators)

    def __set__(self, inst, val):
        if val is None:
            self.__delete__(inst)
            return

        val = self.typecast(inst, val)
        self.validate(val)
        super(DataType, self).__set__(inst, val)
