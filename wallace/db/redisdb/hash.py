from contextlib import contextmanager

from wallace.config import GetDBConn
from wallace.db.base import KeyValueModel


class RedisHash(KeyValueModel):

    db = GetDBConn()
    db_name = None

    @classmethod
    def fetch_many(cls, *items):
        instances = []
        with cls.db.pipeline() as pipe:
            for attrs in items:
                inst = cls.construct(new=False, **attrs)
                inst.pull(pipe=pipe)
                instances.append(inst)

        return instances

    def read_db_data(self, pipe=None):
        with self._db_conn_manager(pipe) as pipe:
            return pipe.hgetall(self.key)

    def write_db_data(self, state, _, pipe=None):
        with self._db_conn_manager(pipe) as pipe:
            pipe.delete(self.key_in_db)  # delete first to clear deleted fields
            pipe.hmset(self.key, state)  # and clean up orphans

    def delete(self, pipe=None):
        super(RedisHash, self).delete()

        with self._db_conn_manager(pipe) as pipe:
            pipe.delete(self.key_in_db)

    @contextmanager
    def _db_conn_manager(self, pipe=None):
        if pipe is None:
            pipe = self.db.pipeline()
            execute = True
        else:
            execute = False

        yield pipe

        if execute:
            pipe.execute()


class ExpiringRedisHash(RedisHash):

    ttl = 10 * 60

    def write_db_data(self, state, _, pipe=None):
        with self._db_conn_manager(pipe) as pipe:
            super(ExpiringRedisHash, self).write_db_data(state, _, pipe=pipe)
            pipe.expire(self.key, self.ttl)
