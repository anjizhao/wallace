from wallace.db.base.errors import ValidationError


class TypecastMixin(object):

    cast = None

    @classmethod
    def typecast(cls, inst, val):
        try:
            return cls.cast(val) if cls.cast else val
        except ValueError:
            raise ValidationError(val)
