from wallace.db.base.attrs import DataType
from wallace.db.base.kv import Key


class Base(type):
    def __new__(cls, name, bases, dct):
        defaults = cls._get_defaults(bases, dct)

        the_class = super(Base, cls).__new__(cls, name, bases, dct)
        the_class._cbs_default_fields = tuple(defaults)

        return the_class

    @staticmethod
    def _get_defaults(bases, dct):
        defaults = {}

        for base in bases:
            for key, val in getattr(base, '_cbs_default_fields', []):
                defaults[key] = val

        for key, val in dct.iteritems():
            if isinstance(val, DataType):
                val.attr = key

                if val.default is not None:
                    defaults[key] = val.default
                elif key in defaults:
                    defaults.pop(key)

        return defaults.items()


class PrimaryKeyBase(Base):
    def __new__(cls, name, bases, dct):
        the_class = super(PrimaryKeyBase, cls).__new__(cls, name, bases, dct)
        the_class._cbs_primary_key_fields = cls.get_pk_fields(bases, dct)

        if cls.is_subclass(bases):
            if not the_class._cbs_primary_key_fields:
                raise TypeError('no primary keys set')

        return the_class

    @staticmethod
    def get_pk_fields(bases, dct):
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
    def is_subclass(bases):
        '''Check this isn't a base class.

        Model hierarchy:
            <model> -> <DB model wrapper (eg PostgresModel)> ->
            Model -> object
        ergo, the bases cardinality for any implemented model subclass
        will be at least 4.

        '''
        base_tree = []
        while bases:
            base_tree.append(bases)
            bases = map(lambda b: list(b.__bases__), bases)
            bases = sum(bases, [])

        return len(base_tree) > 3


class KeyValueBase(PrimaryKeyBase):
    def __new__(cls, name, bases, dct):
        pk_fields = cls.get_pk_fields(bases, dct)
        key = dct.get('key')

        the_class = super(KeyValueBase, cls).__new__(cls, name, bases, dct)
        the_class._cbs_primary_key_fields = pk_fields

        if cls.is_subclass(bases):
            if not pk_fields and not key:
                raise TypeError

        if not key:
            dct['key'] = Key()
