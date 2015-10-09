from wallace.db.base.attrs.interface import ModelInterface
from wallace.db.base.attrs.typecast_mixin import TypecastMixin
from wallace.db.base.attrs.validator_mixin import ValidatorMixin
from wallace.db.base.errors import ValidationError


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
        _check_default_validates(cls.default, cls.cast, cls.validators)

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

        _check_default_validates(self.default, self.cast, self.validators)

    def __set__(self, inst, val):
        if val is None:
            self.__delete__(inst)
            return

        val = self.typecast(inst, val)
        self.validate(val)
        super(DataType, self).__set__(inst, val)


def _check_default_validates(default, cast_func, validators):
    if default is None:
        return

    if callable(default):
        default = default()

    if cast_func:
        if not isinstance(default, cast_func):
            msg = 'default `%s` not a %s' % (default, cast_func.__name__,)
            raise ValidationError(msg)

    for func in validators:
        if not func(default):
            msg = 'default `%s` does not validate' % default
            raise ValidationError(msg)
