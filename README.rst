.. image:: https://pypip.in/download/wallace/badge.png
    :target: https://pypi.python.org/pypi/wallace/
    :alt: Downloads

.. image:: https://pypip.in/version/wallace/badge.png
    :target: https://pypi.python.org/pypi/wallace/
    :alt: Latest Version

.. image:: https://pypip.in/license/wallace/badge.png
    :target: https://pypi.python.org/pypi/wallace/
    :alt: License


.. _Python: http://python.org/

.. _PostgreSQL: http://www.postgresql.org/
.. _psycopg: https://pypi.python.org/pypi/psycopg2

.. _Redis: http://www.redis.io
.. _redispy: https://pypi.python.org/pypi/redis/


=======
Wallace
=======

Wallace wraps database adapters to ease connection handling and data
modeling in Python_ apps. Wallace extends the enterprise libraries
it uses, it does not override or replace their funcionality, so
the interfaces and performance profiles you're familiar with remain intact.
Major features include:

* **Databases:** Currently supports PostgreSQL_ (psycopg_) and Redis_ (redispy_). More to come
* **Modeling:** A bare-bones ORM that provides a consistent interface to model attributes across backends. There's no need to use the ORM if your problem doesn't require it: Wallace consists largely of connection utilities and table-level abstractions
* **Caching:** Automatic connection pool sharing across all layers of abstraction


Basic Usage
~~~~~~~~~~~

To spin up a Postgres connection pool, pass DNS connection info and an optional min/max number of connections:

.. code-block:: python

  >>> from wallace import PostgresPool
  >>> dns = {'host': '/tmp/', 'database': 'postgres', 'user': 'chris', 'password': ''}
  >>> pool = PostgresPool.construct(**dns)  # defaults to max 1 connection in the pool
  >>>
  >>> # or, specifying a max pool size:
  >>> pool = PostgresPool.construct(maxconn=5, **dns)


To use the standard interface, wrap a table:

.. code-block:: python

  >>> from wallace import PostgresTable
  >>> class UserTable(PostgresTable):
  >>>     table_name = 'user'
  >>>
  >>> user_table = UserTable.construct(pool)
  >>> user_table.add(name='chris', email='email@someplace.com')
  >>> user_table.fetchall()
  [{'name': 'chris', 'email': 'email@someplace.com'}]


Then create a model (and plug in the table):

.. code-block:: python

  >>> from wallace import PostgresModel, String
  >>> class User(PostgresModel):
  >>>     table = user_table
  >>>     name = String()
  >>>     email = String(pk=True)
  >>>
  >>> # models may be used to retrieve existing records,
  >>> me = User.fetch(email='email@someplace.com')
  >>> me.name
  'chris'
  >>>
  >>> # create new ones,
  >>> newguy = User.construct(name='guido', email='bdfl@python.org')
  >>> newguy.push()
  >>>
  >>> # and execute searches
  >>> [u.email for u in User.find_all(name='guido')]
  ['bdfl@python.org']


Update, delete, etc. are available too of course:

.. code-block:: python

  >>> me.email = 'new_email@somewherenew.com'
  >>> me.push()
  >>>
  >>> User.fetch(email='email@someplace.com')
  Traceback (most recent call last):
  ...
  wallace.db.base.errors.DoesNotExist
  >>>
  >>> u = User.fetch(email='new_email@somewherenew.com')
  >>> u.name
  'chris'
  >>>
  >>> u.delete()
  >>> User.fetch(email='new_email@somewherenew.com')
  Traceback (most recent call last):
  ...
  wallace.db.base.errors.DoesNotExist


Download and Install
~~~~~~~~~~~~~~~~~~~~

``pip install wallace`` to install the latest stable release.


License
~~~~~~~

.. __: https://github.com/csira/wallace/raw/master/LICENSE.txt

Code, tutorials, and documentation for wallace are all open source under the BSD__ license.


*Enjoy your data.*