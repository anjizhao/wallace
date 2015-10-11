from wallace.db.base.errors import ValidationError


class ModelInterface(object):

    default = None

    def __init__(self, pk=False, default=None):
        self.attr = None
        self.is_pk = pk
        if default is not None:
            self.default = default

    def __get__(self, inst, owner):
        return inst._get_attr(self.attr)

    def __set__(self, inst, val):
        inst._set_attr(self.attr, val)

    def __delete__(self, inst):
        inst._del_attr(self.attr)


def is_default_valid(default, cast_func, validators):
    if default is None:
        return

    if callable(default):
        default = default()

    if cast_func:
        if not isinstance(default, cast_func):
            msg = 'default not a %s' % cast_func.__name__
            raise ValidationError(msg)

    for func in validators:
        if not func(default):
            msg = 'default `%s` does not validate' % default
            raise ValidationError(msg)
