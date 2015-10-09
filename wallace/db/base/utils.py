from wallace.db.base.attrs import DataType


def is_not_base_model(bases):
    '''Confirm the class is not one of the base models.

    The model inheritance structure looks like this:
        <model> -> <DB model wrapper (eg PostgresModel)> ->
        RelationalModel -> Model -> object

    So the hierarchy cardinality for any user-defined subclass is at least 4.

    '''
    base_tree = []
    while bases:
        base_tree.append(bases)
        bases = map(lambda b: list(b.__bases__), bases)
        bases = sum(bases, [])

    return len(base_tree) > 3


def get_primary_key_fields(bases, dct):
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
