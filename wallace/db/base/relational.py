from wallace.db.base.errors import DoesNotExist, ValidationError
from wallace.db.base.model import Base, Model
from wallace.db.base.utils import is_not_base_model, get_primary_key_fields


class _PKBase(Base):
    def __new__(cls, name, bases, dct):
        the_class = super(_PKBase, cls).__new__(cls, name, bases, dct)
        the_class._cbs_primary_key_fields = get_primary_key_fields(bases, dct)

        if is_not_base_model(bases):
            if not the_class._cbs_primary_key_fields:
                raise TypeError('no primary keys set')

        return the_class


def throw_null_pk_field_error(attr):
    msg = 'primary key field "%s" cannot be null' % attr
    raise ValidationError(msg)


class RelationalModel(Model):

    __metaclass__ = _PKBase

    @classmethod
    def fetch(cls, **kwargs):
        inst = cls.construct(new=False, **kwargs)
        inst.pull()
        return inst


    def pull(self):
        self._validate_pk()
        return super(RelationalModel, self).pull()

    def push(self, *a, **kw):
        self._validate_pk()
        return super(RelationalModel, self).push(*a, **kw)

    def delete(self):
        super(RelationalModel, self).delete()
        if not self.primary_key:
            raise DoesNotExist

    def _validate_pk(self):
        for attr in self._cbs_primary_key_fields:
            if getattr(self, attr, None) is None:
                throw_null_pk_field_error(attr)


    @property
    def primary_key(self):
        # The primary key CURRENTLY stored in the db.
        # If a pk field is changed, this will return the old
        # value so updates can find the row.

        if self.is_new:
            raise DoesNotExist('new model')

        pk = {}
        for attr in self._cbs_primary_key_fields:
            try:
                pk[attr] = self._cbs_db_data[attr]
            except KeyError:
                throw_null_pk_field_error(attr)
        return pk
