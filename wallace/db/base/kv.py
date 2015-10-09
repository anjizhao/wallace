import uuid
from wallace.db.base.attrs import DataType
from wallace.db.base.errors import ValidationError
from wallace.db.base.model import Base, Model
from wallace.db.base.errors import DoesNotExist


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
        fields = list(inst._cbs_primary_key_fields)
        fields.sort()
        values = [getattr(inst, f) for f in fields]
        if values.count(None):
            raise ValidationError('%s cannot be null' % 'foo')
        return '|'.join(values)


class KVBase(Base):
    def __new__(cls, name, bases, dct):
        pk_fields = cls._get_pk_fields(bases, dct)
        key = dct.get('key')

        if not key:
            if pk_fields:
                dct['key'] = ComposedKey()
            else:
                dct['key'] = Key()

        the_class = super(KVBase, cls).__new__(cls, name, bases, dct)
        the_class._cbs_primary_key_fields = pk_fields
        return the_class


    @staticmethod
    def _get_pk_fields(bases, dct):
        pk_fields = set()

        for base in bases:  # support model inheritance
            for key in getattr(base, '_cbs_primary_key_fields', []):
                pk_fields.add(key)

        for key, val in dct.iteritems():
            if isinstance(val, DataType) and val.is_pk:
                pk_fields.add(key)
            elif key in pk_fields:      # catch any superclass pk fields
                pk_fields.remove(key)   # overridden here by a non-pk one

        return tuple(pk_fields)

    @staticmethod
    def _is_proper_model(bases):
        # Model hierarchy:
        #     <model> -> <DB model wrapper (eg PostgresModel)> ->
        #     Model -> Model -> object
        # ergo, the hierarchy cardinality for any proper model subclass
        # will be at least 4
        # (that is, check this isn't a base class)

        base_tree = []
        while bases:
            base_tree.append(bases)
            bases = map(lambda b: list(b.__bases__), bases)
            bases = sum(bases, [])

        return len(base_tree) > 3


class KeyValueModel(Model):

    __metaclass__ = KVBase

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

    def pull(self):
        super(KeyValueModel, self).pull()
        self._key_in_db = self.key
