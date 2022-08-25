# -*- coding: utf-8 -*-
# Description: IBM i netdata python.d external collector module
# Author: Andrew Love

from copy import deepcopy

from bases.FrameworkServices.SimpleService import SimpleService

try:
    import psycopg
    from psycopg import extensions
    from psycopg import OperationalError
    HAS_DB = True
except ImportError:
    HAS_DB = False

ORDER = [
    'asp_utilisation',
]

CHARTS = {
    'asp_utilisation': {
        'options': [None, 'System ASP Utilisation', '%', 'storage statistics', 'ibmi.asp_utilisation', 'line'],
        'lines': [
            ['system_disk_storage', 'total', 'absolute', 1, 1000000],
            ['system_disk_used', 'used', 'absolute', 1, 1],
        ]
    },
}

DB_CONNECT_STRING = "{0}/{1}@//{2}/{3}"

QUERY_ASP = '''
SELECT 
    "SYSTEM_ASP_STORAGE", 
    "TOTAL_AUXILIARY_STORAGE", 
    "SYSTEM_ASP_USED" 
FROM system_status_info AS ssi
'''

ASP_METRICS = {
    'System ASP Storage':'system_asp_storage',
    'Total Auxillary Storage':'total_auxillary_storage',
    'System ASP Used':'system_asp_used',
    'System ASP Utilisation Percentage': 'asp_utilisation_precent',
}


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = deepcopy(CHARTS)
        self.database = configuration.get('database')
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
            self.error("'psycopg' package is needed to use psycopg module")
            return False

        if not all([
            self.database,
            self.user,
            self.password,
            self.server,
        ]):
            self.error("one of these parameters is not specified: database, user, password, server")
            return False

        if not self.connect():
            return False

        return bool(self.get_data())

    def get_data(self):
        if not self.alive and not self.reconnect():
            return None

        data = dict()

        # ASP usage
        try:
            rv = self.gather_asp_metrics()
        except psycopg.Error as error:
            self.error(error)
            self.alive = False
            return None
        else:
            for name, value in rv:
                if name not in ASP_METRICS:
                    continue
                data[ASP_METRICS[name]] = int(float(value) * 1000) 

        return data or None


    def gather_asp_metrics(self):
        """
        :return:

        [['System ASP Storage', 0],
         ['System ASP Used', 0],
         ['Total Auxiliary Storage', 0]]
        """
        metrics = list()
        with self.conn.cursor() as cursor:
            cursor.execute(QUERY_ASP)
            for SYSTEM_ASP_STORAGE, TOTAL_AUXILIARY_STORAGE, SYSTEM_ASP_USED in cursor.fetchall():
                if SYSTEM_ASP_USED is None:
                    offline = True
                    system_disk_used = 0
                else:
                    offline = False
                    system_disk_used = float(SYSTEM_ASP_USED)

                if SYSTEM_ASP_STORAGE is None:
                    system_disk_storage = 0
                else:
                    system_disk_storage = float(SYSTEM_ASP_STORAGE)

                if TOTAL_AUXILIARY_STORAGE is None:
                    system_disk_total_auxiliary_storage = 0
                else:
                    system_disk_total_auxiliary_storage = float(TOTAL_AUXILIARY_STORAGE)

                metrics.append(
                    [
                        offline,
                        system_disk_storage,
                        system_disk_used,
                        system_disk_total_auxiliary_storage,
                    ]
                )
        return metrics
