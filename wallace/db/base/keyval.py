from contextlib import contextmanager
import uuid

from wallace.db.base.attrs import UUID4
from wallace.db.base.errors import DoesNotExist, ValidationError
from wallace.db.base.model import Model


class KeyValueModel(Model):
    '''
    Must declare a 'key' field for hand-created PK's,
    or a 'key' property to combine other fields into the PK.

    '''

    @property
    def key(self):
        pass

    @classmethod
    def fetch(cls, key=None, **kwargs):
        inst = cls.construct(new=False, **kwargs)
        if key:
            inst._key_in_db = key
        inst.pull()
        return inst

    @classmethod
    def construct(cls, key=None, new=True, **kwargs):
        inst = super(KeyValueModel, cls).construct(new=new, **kwargs)
        inst._cbs_ident = ident
        return inst

    def __init__(self):
        Model.__init__(self)
        self._key_in_db = None

    @property
    def ident(self):
        if self._cbs_ident is None:
            raise DoesNotExist('new model')
        return self._cbs_ident

    @property
    def db_key(self):
        return self.ident


    create_new_ident = staticmethod(lambda: uuid.uuid4().hex)

    def push(self, *args, **kwargs):
        with self._new_model_key_handler():
            return super(KeyValueModel, self).push(*args, **kwargs)

    @contextmanager
    def _new_model_key_handler(self):
        if not self.is_new and self._cbs_ident is None:
            msg = 'construction error, exists without an ident'
            raise ValidationError(msg)

        reset_key_on_error = False
        if self._cbs_ident is None:
            self._cbs_ident = self.create_new_ident()
            reset_key_on_error = True

        try:
            yield
        except:
            if reset_key_on_error:
                # todo may make sense to do an existence check here (or catch
                # a more specific error) so we don't end up with orphaned items
                self._cbs_ident = None
            raise
