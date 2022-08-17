# -*- coding: utf-8 -*-
# Description: IBMi netdata python.d module
# Author: Andrew Love

from copy import deepcopy

from bases.FrameworkServices.SimpleService import SimpleService

try:
    import psycopg
    from psycopg import extensions
    from psycopg.extras import DictCursor
    from psycopg import OperationalError
    HAS_DB = True
except ImportError:
    HAS_DB = False

ORDER = [
    'asp_utilisation',
]

CHARTS = {
    'asp_utilisation': {
        'options': [None, 'System ASP Used', '%', 'storage statistics', 'ibmi.asp_utilisation', 'line'],
        'lines': [
            ['system_asp_storage', 'total', 'absolute', 1, 1000000],
            ['system_asp_used', 'used', 'absolute', 1, 1],
        ]
    },
}

DB_CONNECT_STRING = "{0}/{1}@//{2}/{3}"

QUERY_ASP = '''
SELECT
  s.main_storage_size,
  s.system_asp_storage,
  s.system_asp_used
FROM
  system_status_info s
'''

SYS_METRICS = {
    'ASP Utilisation %': 'asp_utilisation',
}


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = deepcopy(CHARTS)
        self.user = configuration.get('user')
        self.password = configuration.get('password')
        self.server = configuration.get('server')
        self.alive = False
        self.conn = None

    def connect(self):
        if self.conn:
            self.conn.close()
            self.conn = None

        try:
            self.conn = psycopg.connect(**self.conn_params)
            self.conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            self.conn.set_session(readonly=True)
        except OperationalError as error:
            self.error(error)
            self.alive = False
        else:
            self.alive = True

        return self.alive

    def reconnect(self):
        return self.connect()

    def check(self):
        if not HAS_DB:
            self.error("'ibm_db' package is needed to use ibm_db module")
            return False

        if not all([
            self.user,
            self.password,
            self.server,
        ]):
            self.error("one of these parameters is not specified: user, password, server")
            return False

        if not self.connect():
            return False

        return bool(self.get_data())

    def get_data(self):
        if not self.alive and not self.reconnect():
            return None

        data = dict()

        return data or None
