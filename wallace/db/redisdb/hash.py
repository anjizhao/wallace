from contextlib import contextmanager

from wallace.config import GetDBConn
from wallace.db.base import KeyValueModel, DoesNotExist


class RedisHash(KeyValueModel):

    db = GetDBConn()
    db_name = None

    @classmethod
    def fetch_many(cls, *keys):
        with cls.db.pipeline() as pipe:
            for key in keys:
                pipe.hgetall(key)
            data = pipe.execute()

        items = []
        for idx, attrs in enumerate(data):
            inst = cls.construct(key=keys[idx], new=False, **attrs)
            items.append(inst)

        return items


    @contextmanager
    def _pipe_state_mgr(self, pipe=None):
        if pipe is None:
            pipe = self.db.pipeline()
            execute = True
        else:
            execute = False

        yield pipe

        if execute:
            pipe.execute()

    def _read_data(self):
        return self.db.hgetall(self.key)

    def _write_data(self, state, _, pipe=None):
        with self._pipe_state_mgr(pipe) as pipe:
            pipe.delete(self.key_in_db)  # delete first to clear deleted fields
            pipe.hmset(self.key, state)  # and clean up orphans

    def delete(self, pipe=None):
        if not self.key_in_db:
            raise DoesNotExist

        with self._pipe_state_mgr(pipe) as pipe:
            pipe.delete(self.key_in_db)


class ExpiringRedisHash(RedisHash):

    ttl = 10 * 60

    def _write_data(self, state, _, pipe=None):
        with self._pipe_state_mgr(pipe) as pipe:
            super(ExpiringRedisHash, self)._write_data(state, _, pipe=pipe)
            pipe.expire(self.key_in_db, self.ttl)
