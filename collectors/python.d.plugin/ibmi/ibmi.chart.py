"""Netdata python.d external collector module for IBM i.

An external Netdata collector module that periodically polls a remote
IBM i Power system for key system metrics.
"""

from copy import deepcopy
from xmlrpc.client import boolean
from bases.FrameworkServices.SimpleService import SimpleService


try:
    import pyodbc as dbdb2
    import psycopg2 as dbmock
    HAS_DB = True
except ImportError:
    HAS_DB = False

ORDER = [
    'asp_utilisation',
    'asp_used_percent',
    'cpu_utilisation',
    'job_stats',
    'memory_current_size',
    'memory_database_faults',
    'memory_nondatabase_faults',
    'memory_total_faults',
    'memory_database_pages',
    'memory_nondatabase_pages',
    'memory_active_to_wait',
    'memory_wait_to_ineligible',
    'memory_active_to_ineligible'
]

CHARTS = {
    'asp_utilisation': {
        'options': [None, \
            'System ASP Utilisation', \
            'Tb', \
            'storage statistics', \
            'ibmi.asp_utilisation', \
            'line'],
        'lines': [
            ['system_disk_capacity', 'total capacity', 'absolute', 1, 1000000],
            ['system_disk_used', 'used', 'absolute', 1, 1000000],
            ['system_disk_free', 'free', 'absolute', 1, 1000000]
        ]
    },
    'asp_used_percent': {
        'options': [None, \
            'System ASP Percent Used', \
            '%', \
            'storage statistics', \
            'ibmi.asp_used_percent', \
            'line'],
        'lines': [
            ['system_disk_used_percent', 'used percent', 'absolute', 1, 1]
        ]
    },
    'cpu_utilisation': {
        'options': [None, \
            'System CPU Utilisation', \
            '%', \
            'cpu statistics', \
            'ibmi.cpu_utilisation', \
            'line'],
        'lines': [
            ['system_current_cpu_capacity', 'total', 'absolute', 1, 1],
            ['system_avg_cpu_utilisation', 'average utilisation', 'absolute', 1, 1],
            ['system_max_cpu_utilisation', 'maximum utilisation', 'absolute', 1, 1],
            ['system_min_cpu_utilisation', 'minimum utilisation', 'absolute', 1, 1]
        ]
    },
    'job_stats': {
        'options': [None, \
            'System Job Statistics', \
            'Count', \
            'job statistics', \
            'ibmi.job_stats', \
            'line'],
        'lines': [
            ['system_total_jobs', 'total', 'absolute', 1, 1],
            ['system_active_jobs', 'active', 'absolute', 1, 1],
            ['system_interactive_jobs', 'interactive', 'absolute', 1, 1]
        ]
    },
    'memory_current_size': {
        'options': [None, \
            'Memory Pool Current Size', \
            'Mb', \
            'memory statistics', \
            'ibmi.memory_pool_current_size', \
            'line'],
        'lines': []
    },
    'memory_database_faults': {
        'options': [None, \
            'Database Page Faults', \
            'Faults/s', \
            'memory statistics', \
            'ibmi.memory_database_faults', \
            'line'],
        'lines': []
    },
    'memory_nondatabase_faults': {
        'options': [None, \
            'NonDatabase Page Faults', \
            'Faults/s', \
            'memory statistics', \
            'ibmi.memory_nondatabase_faults', \
            'line'],
        'lines': []
    },
    'memory_total_faults': {
        'options': [None, \
            'Total Page Faults', \
            'Faults/s', \
            'memory statistics', \
            'ibmi.memory_total_faults', \
            'line'],
        'lines': []
    },
    'memory_database_pages': {
        'options': [None, \
            'Database Pages into Memory Pool', \
            'Pages/s', \
            'memory statistics', \
            'ibmi.memory_database_pages', \
            'line'],
        'lines': []
    },
    'memory_nondatabase_pages': {
        'options': [None, \
            'NonDatabase Pages into Memory Pool', \
            'Pages/s', \
            'memory statistics', \
            'ibmi.memory_nondatabase_pages', \
            'line'],
        'lines': []
    },
    'memory_active_to_wait': {
        'options': [None, \
            'Thread Transitions from Active to Wait', \
            'Transitions/m', \
            'memory statistics', \
            'ibmi.memory_active_to_wait', \
            'line'],
        'lines': []
    },
    'memory_wait_to_ineligible': {
        'options': [None, \
            'Thread Transitions from Wait to Ineligible', \
            'Transitions/m', \
            'memory statistics', \
            'ibmi.memory_wait_to_ineligible', \
            'line'],
        'lines': []
    },
    'memory_active_to_ineligible': {
        'options': [None, \
            'Thread Transitions from Active to Ineligible', \
            'Transitions/m', \
            'memory statistics', \
            'ibmi.memory_active_to_ineligible', \
            'line'],
        'lines': []
    }
}

QUERY_SYSTEM_STATUS_INFO = '''
SELECT 
    "MAIN_STORAGE_SIZE",
    "SYSTEM_ASP_STORAGE",
    "SYSTEM_ASP_USED",
    "CURRENT_CPU_CAPACITY",
    "MAXIMUM_CPU_UTILIZATION",
    "AVERAGE_CPU_UTILIZATION",
    "MINIMUM_CPU_UTILIZATION",
    "TOTAL_JOBS_IN_SYSTEM",
    "ACTIVE_JOBS_IN_SYSTEM",
    "INTERACTIVE_JOBS_IN_SYSTEM"
FROM qsys2.system_status_info_basic
'''

QUERY_MEMORY_POOL_INFO = '''
SELECT
    "POOL_NAME",
    "CURRENT_SIZE",
    "ELAPSED_DATABASE_FAULTS",
    "ELAPSED_NON_DATABASE_FAULTS",
    "ELAPSED_TOTAL_FAULTS",
    "ELAPSED_DATABASE_PAGES",
    "ELAPSED_NON_DATABASE_PAGES",
    "ELAPSED_ACTIVE_TO_WAIT",
    "ELAPSED_WAIT_TO_INELIGIBLE",
    "ELAPSED_ACTIVE_TO_INELIGIBLE"
FROM qsys2.memory_pool_info
'''

SYSTEM_STATUS_METRICS = {
    'MAIN_STORAGE_SIZE':'system_main_storage_size',
    'SYSTEM_ASP_STORAGE_CAPACITY':'system_disk_capacity',
    'SYSTEM_ASP_STORAGE_USED_PERCENT':'system_disk_used_percent',
    'SYSTEM_ASP_STORAGE_USED':'system_disk_used',
    'SYSTEM_ASP_STORAGE_FREE':'system_disk_free',
    'CURRENT_CPU_CAPACITY':'system_current_cpu_capacity',
    'MAXIMUM_CPU_UTILIZATION':'system_max_cpu_utilisation',
    'AVERAGE_CPU_UTILIZATION':'system_avg_cpu_utilisation',
    'MINIMUM_CPU_UTILIZATION':'system_min_cpu_utilisation',
    'TOTAL_JOBS_IN_SYSTEM':'system_total_jobs',
    'ACTIVE_JOBS_IN_SYSTEM':'system_active_jobs',
    'INTERACTIVE_JOBS_IN_SYSTEM':'system_interactive_jobs'
}

MEMORY_POOL_METRICS = {
    'POOL_NAME':'memory_pool_name',
    'CURRENT_SIZE':'memory_current_size',
    'ELAPSED_DATABASE_FAULTS':'memory_database_faults',
    'ELAPSED_NON_DATABASE_FAULTS':'memory_nondatabase_faults',
    'ELAPSED_TOTAL_FAULTS':'memory_total_faults',
    'ELAPSED_DATABASE_PAGES':'memory_database_pages',
    'ELAPSED_NON_DATABASE_PAGES':'memory_nondatabase_pages',
    'ELAPSED_ACTIVE_TO_WAIT':'memory_active_to_wait',
    'ELAPSED_WAIT_TO_INELIGIBLE':'memory_wait_to_ineligible',
    'ELAPSED_ACTIVE_TO_INELIGIBLE':'memory_active_to_ineligible'
}

class Service(SimpleService):
    """Implementation of the Netdata SimpleSevice class.

    It is the lowest-level class which implements most of module logic, like:

        - threading
        - handling run times
        - chart formatting
        - logging
        - chart creation and updating

    Args:
        SimpleService (configuration): Configuration object.
    """
    def __init__(self, configuration=None, name=None):
        """Initialiser.
        """
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = deepcopy(CHARTS)
        self.rdbms = configuration.get('rdbms')
        self.database = configuration.get('database')
        self.user = configuration.get('user')
        self.password = configuration.get('password')
        self.server = configuration.get('server')
        self.alive = False
        self.conn = None
        self.db = ""
        self.active_memory_pools = set()

    def connect(self):
        """Connects to remote system for metrics data collection.

        Connect to the remote RDBMS using the mock or DB2 ODBC driver, depending on config.

        Raises:
            self.db.OperationalError: There's been an error connecting to the remote system.

        Returns:
            self.alive: A boolean indicating whether the remote connecion alive or not.
        """
        if self.rdbms == 'db2':
            dsn = f'DRIVER=IBM i Access ODBC Driver; \
                SYSTEM={self.server}; \
                UID={self.user}; \
                PWD={self.password}'
            self.db = dbdb2
        elif self.rdbms == 'mock':
            self.db = dbmock
        else:
            self.alive = False
            return self.alive

        if self.conn:
            self.conn.close()
            self.conn = None

        try:
            if self.rdbms == 'db2':
                self.conn = self.db.connect(dsn)
            elif self.rdbms == 'mock':
                self.conn = self.db.connect(
                    host=self.server,
                    dbname=self.database,
                    user=self.user,
                    password=self.password
                )
            else:
                raise self.db.OperationalError("Invalid database type in ibmi.conf")
        except self.db.OperationalError as error:
            self.error(error)
            self.alive = False
        else:
            self.alive = True

        return self.alive


    def reconnect(self):
        """Reconnects to remote system for metrics data collection.

        Reconnects a broken remote system connection.

        Returns:
            self.alive: A boolean indicating whether the remote connecion alive or not.
        """
        return self.connect()

    def check(self):
        """Checks metrics data collection from the remote system.

        Retrieve raw data from the remote system and return True if all data is received otherwise
        it should return False.

        Returns:
            A boolean indicating if metrics data was retrieved successfully form teh remote system.
        """
        if not HAS_DB:
            if self.rdbms == 'db2':
                self.error("'pyodbc' package is needed to use pyodbc module")
            elif self.rdbms == 'mock':
                self.error("'psycopg' package is needed to use psycopg module")
            else:
                self.error("Invalid database type in ibmi.conf")
            return False

        if not all([
            self.database,
            self.user,
            self.password,
            self.server,
        ]):
            self.error("one of these parameters is not specified: database, user, password, server")
            return False

        return bool(self.get_data()) if self.connect() else False

    def get_data(self):
        """Get the required metrics data from the remote system.

        Retrieve the required metrics data from teh remote system

        Returns:
            data: A dict of required metrics data.
        """
        if not self.alive and not self.reconnect():
            return None

        data = {}

        # SYSTEM_STATUS_INFO
        try:
            rv = self.gather_system_status_metrics()
        except self.db.Error as error:
            self.error(error)
            self.alive = False
            return None
        else:
            for name, value in rv:
                if name not in SYSTEM_STATUS_METRICS:
                    continue
                data[SYSTEM_STATUS_METRICS[name]] = int(float(value))


        # MEMORY_POOL_INFO
        try:
            rv = self.gather_memory_pool_metrics()
        except self.db.Error as error:
            self.error(error)
            self.alive = False
            return None
        else:
            for memory_pool_name, \
                memory_current_size, \
                memory_database_faults, \
                memory_nondatabase_faults, \
                memory_total_faults, \
                memory_database_pages, \
                memory_nondatabase_pages, \
                memory_active_to_wait, \
                memory_wait_to_ineligible, \
                memory_active_to_ineligible in rv:
                    
                if not (self.charts):
                    continue
                if memory_pool_name not in self.active_memory_pools:
                    self.active_memory_pools.add(memory_pool_name)
                    self.add_memory_pool_to_charts(memory_pool_name)
                data['{0}_memory_current_size'.format(memory_pool_name)] = memory_current_size
                data['{0}_memory_database_faults'.format(memory_pool_name)] = memory_database_faults
                data['{0}_memory_nondatabase_faults'.format(memory_pool_name)] = memory_nondatabase_faults
                data['{0}_memory_total_faults'.format(memory_pool_name)] = memory_total_faults
                data['{0}_memory_database_pages'.format(memory_pool_name)] = memory_database_pages
                data['{0}_memory_nondatabase_pages'.format(memory_pool_name)] = memory_nondatabase_pages
                data['{0}_memory_active_to_wait'.format(memory_pool_name)] = memory_active_to_wait
                data['{0}_memory_wait_to_ineligible'.format(memory_pool_name)] = memory_wait_to_ineligible
                data['{0}_memory_active_to_ineligible'.format(memory_pool_name)] = memory_active_to_ineligible    
                
        return data or None


    def gather_system_status_metrics(self):
        """Gather the raw system metrics data into name value pairs.

        Access the remote system and query the metrics database.
        Format the results.

        Returns:
            metrics: A list of name, value pairs for the raw system metrics data.
        """
        metrics = []
        with self.conn.cursor() as cursor:
            cursor.execute(QUERY_SYSTEM_STATUS_INFO)

            for MAIN_STORAGE_SIZE, \
                SYSTEM_ASP_STORAGE, \
                SYSTEM_ASP_USED, \
                CURRENT_CPU_CAPACITY, \
                MAXIMUM_CPU_UTILIZATION, \
                AVERAGE_CPU_UTILIZATION, \
                MINIMUM_CPU_UTILIZATION, \
                TOTAL_JOBS_IN_SYSTEM, \
                ACTIVE_JOBS_IN_SYSTEM, \
                INTERACTIVE_JOBS_IN_SYSTEM in cursor.fetchall():

                # System resources
                if MAIN_STORAGE_SIZE is None:
                    system_main_storage_size = 0
                else:
                    system_main_storage_size = float(MAIN_STORAGE_SIZE)
                    metrics.append(["MAIN_STORAGE_SIZE", system_main_storage_size])

                # ASP metrics
                if SYSTEM_ASP_USED is None:
                    system_disk_used_percent = 0
                else:
                    system_disk_used_percent = float(SYSTEM_ASP_USED)
                    metrics.append(["SYSTEM_ASP_STORAGE_USED_PERCENT", system_disk_used_percent])

                if SYSTEM_ASP_STORAGE is None:
                    system_disk_capacity = 0
                    system_disk_used = 0
                    system_disk_free = 0
                else:
                    system_disk_capacity = float(SYSTEM_ASP_STORAGE)
                    system_disk_used = system_disk_used_percent*system_disk_capacity/100
                    system_disk_free = system_disk_capacity-system_disk_used
                    metrics.extend((["SYSTEM_ASP_STORAGE_CAPACITY", system_disk_capacity], \
                        ["SYSTEM_ASP_STORAGE_USED", system_disk_used], \
                        ["SYSTEM_ASP_STORAGE_FREE", system_disk_free]))

                # CPU metrics
                if CURRENT_CPU_CAPACITY is None:
                    system_current_cpu_capacity = 0
                else:
                    system_current_cpu_capacity = float(CURRENT_CPU_CAPACITY)
                    metrics.append(["CURRENT_CPU_CAPACITY", system_current_cpu_capacity])

                if MAXIMUM_CPU_UTILIZATION is None:
                    system_max_cpu_utilisation = 0
                else:
                    system_max_cpu_utilisation = float(MAXIMUM_CPU_UTILIZATION)
                    metrics.append(["MAXIMUM_CPU_UTILIZATION", system_max_cpu_utilisation])

                if AVERAGE_CPU_UTILIZATION is None:
                    system_avg_cpu_utilisation = 0
                else:
                    system_avg_cpu_utilisation = float(AVERAGE_CPU_UTILIZATION)
                    metrics.append(["AVERAGE_CPU_UTILIZATION", system_avg_cpu_utilisation])

                if MINIMUM_CPU_UTILIZATION is None:
                    system_min_cpu_utilisation = 0
                else:
                    system_min_cpu_utilisation = float(MINIMUM_CPU_UTILIZATION)
                    metrics.append(["MINIMUM_CPU_UTILIZATION", system_min_cpu_utilisation])

                # Jobs metrics
                if TOTAL_JOBS_IN_SYSTEM is None:
                    system_total_jobs = 0
                else:
                    system_total_jobs = float(TOTAL_JOBS_IN_SYSTEM)
                    metrics.append(["TOTAL_JOBS_IN_SYSTEM", system_total_jobs])

                if ACTIVE_JOBS_IN_SYSTEM is None:
                    system_active_jobs = 0
                else:
                    system_active_jobs = float(ACTIVE_JOBS_IN_SYSTEM)
                    metrics.append(["ACTIVE_JOBS_IN_SYSTEM", system_active_jobs])

                if INTERACTIVE_JOBS_IN_SYSTEM is None:
                    system_interactive_jobs = 0
                else:
                    system_interactive_jobs = float(INTERACTIVE_JOBS_IN_SYSTEM)
                    metrics.append(["INTERACTIVE_JOBS_IN_SYSTEM", system_interactive_jobs])


        return metrics


    def gather_memory_pool_metrics(self):
        """Gather the raw memory pool metrics data into name value pairs.

        Access the remote system and query the metrics database.
        Format the results.

        Returns:
            metrics: A list of name, value pairs for the raw memory pooll metrics data.
        """
        metrics = []
        with self.conn.cursor() as cursor:
            cursor.execute(QUERY_MEMORY_POOL_INFO)
            for POOL_NAME, \
                CURRENT_SIZE, \
                ELAPSED_DATABASE_FAULTS, \
                ELAPSED_NON_DATABASE_FAULTS, \
                ELAPSED_TOTAL_FAULTS, \
                ELAPSED_DATABASE_PAGES, \
                ELAPSED_NON_DATABASE_PAGES, \
                ELAPSED_ACTIVE_TO_WAIT, \
                ELAPSED_WAIT_TO_INELIGIBLE, \
                ELAPSED_ACTIVE_TO_INELIGIBLE in cursor.fetchall():

                # Memort pool resources
                if POOL_NAME is None:
                    memory_pool_name = "unavailable"
                else:
                    memory_pool_name = POOL_NAME

                if CURRENT_SIZE is None:
                    memory_current_size = 0
                else:
                    memory_current_size = float(CURRENT_SIZE)

                if ELAPSED_DATABASE_FAULTS is None:
                    memory_database_faults = 0
                else:
                    memory_database_faults = int(ELAPSED_DATABASE_FAULTS)

                if ELAPSED_NON_DATABASE_FAULTS is None:
                    memory_nondatabase_faults = 0
                else:
                    memory_nondatabase_faults = int(ELAPSED_NON_DATABASE_FAULTS)

                if ELAPSED_TOTAL_FAULTS is None:
                    memory_total_faults = 0
                else:
                    memory_total_faults = int(ELAPSED_TOTAL_FAULTS)

                if ELAPSED_DATABASE_PAGES is None:
                    memory_database_pages = 0
                else:
                    memory_database_pages = int(ELAPSED_DATABASE_PAGES)

                if ELAPSED_NON_DATABASE_PAGES is None:
                    memory_nondatabase_pages = 0
                else:
                    memory_nondatabase_pages = int(ELAPSED_NON_DATABASE_PAGES)

                if ELAPSED_ACTIVE_TO_WAIT is None:
                    memory_active_to_wait = 0
                else:
                    memory_active_to_wait = int(ELAPSED_ACTIVE_TO_WAIT)

                if ELAPSED_WAIT_TO_INELIGIBLE is None:
                    memory_wait_to_ineligible = 0
                else:
                    memory_wait_to_ineligible = int(ELAPSED_WAIT_TO_INELIGIBLE)

                if ELAPSED_ACTIVE_TO_INELIGIBLE is None:
                    memory_active_to_ineligible = 0
                else:
                    memory_active_to_ineligible = int(ELAPSED_ACTIVE_TO_INELIGIBLE)

                metrics.append([
                    memory_pool_name,
                    memory_current_size,
                    memory_database_faults,
                    memory_nondatabase_faults,
                    memory_total_faults,
                    memory_database_pages,
                    memory_nondatabase_pages,
                    memory_active_to_wait,
                    memory_wait_to_ineligible,
                    memory_active_to_ineligible
                    ])
        return metrics

    def add_memory_pool_to_charts(self, memory_pool_name):

        self.charts['memory_current_size'].add_dimension(
            [
                '{0}_memory_current_size'.format(memory_pool_name),
                memory_pool_name,
                'absolute',
                1,
                1,
            ])
        self.charts['memory_database_faults'].add_dimension(
            [
                '{0}_memory_database_faults'.format(memory_pool_name),
                memory_pool_name,
                'absolute',
                1,
                1,
            ])
        self.charts['memory_nondatabase_faults'].add_dimension(
            [
                '{0}_memory_nondatabase_faults'.format(memory_pool_name),
                memory_pool_name,
                'absolute',
                1,
                1,
            ])
        self.charts['memory_total_faults'].add_dimension(
            [
                '{0}_memory_total_faults'.format(memory_pool_name),
                memory_pool_name,
                'absolute',
                1,
                1,
            ])
        self.charts['memory_database_pages'].add_dimension(
            [
                '{0}_memory_database_page'.format(memory_pool_name),
                memory_pool_name,
                'absolute',
                1,
                1,
            ])
        self.charts['memory_nondatabase_pages'].add_dimension(
            [
                '{0}_memory_nondatabase_page'.format(memory_pool_name),
                memory_pool_name,
                'absolute',
                1,
                1,
            ])
        self.charts['memory_active_to_wait'].add_dimension(
            [
                '{0}_memory_active_to_wait'.format(memory_pool_name),
                memory_pool_name,
                'absolute',
                1,
                1,
            ])
        self.charts['memory_wait_to_ineligible'].add_dimension(
            [
                '{0}_memory_wait_to_ineligible'.format(memory_pool_name),
                memory_pool_name,
                'absolute',
                1,
                1,
            ])
        self.charts['memory_active_to_ineligible'].add_dimension(
            [
                '{0}_memory_active_to_ineligible'.format(memory_pool_name),
                memory_pool_name,
                'absolute',
                1,
                1,
            ])
        
