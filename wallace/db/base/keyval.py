import uuid
from wallace.db.base.errors import DoesNotExist, ValidationError
from wallace.db.base.model import Base, Model
from wallace.db.base.utils import get_primary_key_fields


class Key(object):

    def __get__(self, inst, _):
        if inst._new_key:
            return inst._new_key

        if inst.is_new:
            inst._new_key = uuid.uuid4().hex
            return inst._new_key

        if inst._key_in_db:
            return inst._key_in_db

        raise ValidationError('no key has been set')

    def __set__(self, inst, val):
        inst._new_key = val

    def __delete__(self, inst):
        inst._new_key = None


class ComposedKey(object):

    def __get__(self, inst, _):
        if inst._key_in_db:
            return inst._key_in_db
        return self._format_key(inst)

    def _format_key(self, inst):
        for attr in inst._cbs_primary_key_fields:
            if getattr(inst, attr, None) is None:
                raise ValidationError('%s cannot be null' % attr)

        fields = list(inst._cbs_primary_key_fields)
        fields.sort()

        values = [getattr(inst, f) for f in fields]
        if values.count(None):
            raise ValidationError('%s cannot be null' % 'foo')

        return '|'.join(values)


class KeyValueBase(Base):

    def __new__(cls, name, bases, dct):
        pk_fields = get_primary_key_fields(bases, dct)
        key = dct.get('key')

        if not key:
            if pk_fields:
                dct['key'] = ComposedKey()
            else:
                dct['key'] = Key()

        the_class = super(KeyValueBase, cls).__new__(cls, name, bases, dct)
        the_class._cbs_primary_key_fields = pk_fields
        return the_class


class KeyValueModel(Model):

    __metaclass__ = KeyValueBase

    @classmethod
    def fetch(cls, key=None, **kwargs):
        inst = cls.construct(new=False, **kwargs)
        if key:
            inst._key_in_db = key
        inst.pull()
        return inst


    def __init__(self):
        super(KeyValueModel, self).__init__()
        self._new_key = ''  # used only by the Key descriptor
        self._key_in_db = ''

    @property
    def key_in_db(self):
        if self.is_new:
            raise DoesNotExist('new model')

        return self._key_in_db


    def push(self, *a, **kw):
        super(KeyValueModel, self).push(*a, **kw)
        self._key_in_db = self.key
        return self

    def pull(self, *a, **kw):
        super(KeyValueModel, self).pull(*a, **kw)
        self._key_in_db = self.key
        return self

    def delete(self):
        super(KeyValueModel, self).delete()
        if not self.key_in_db:
            raise DoesNotExist
