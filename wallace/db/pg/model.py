from wallace.db.base import RelationalModel
from wallace.db.base import DoesNotExist, ValidationError


class PostgresModel(RelationalModel):

    table = None

    @classmethod
    def find_one(cls, **kwargs):
        data = cls.table.fetchall(limit=2, **kwargs)
        if not data:
            raise DoesNotExist
        if len(data) != 1:
            raise ValidationError('expected a unique result')
        return cls.construct(new=False, **data[0])

    @classmethod
    def find_all(cls, **kwargs):
        rows = cls.table.fetchall(**kwargs)
        return map(lambda row: cls.construct(new=False, **row), rows)


    def read_from_db(self):
        return self.table.fetchone(**self.primary_key)

    def write_to_db(self, state, changes):
        if self.is_new:
            self.table.add(**state)
        else:
            self.table.update(changes, **self.primary_key)


    def delete(self):
        super(PostgresModel, self).delete()
        self.table.delete(**self.primary_key)
