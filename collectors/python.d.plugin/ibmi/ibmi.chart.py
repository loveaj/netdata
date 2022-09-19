# -*- coding: utf-8 -*-
# Description: IBM i netdata python.d external collector module
# Author: Andrew Love

from copy import deepcopy
from xml.etree.ElementTree import tostring
from bases.FrameworkServices.SimpleService import SimpleService


try:
    import pyodbc as dbdb2
    import psycopg as dbmock
    HAS_DB = True
except ImportError: 
    HAS_DB = False

ORDER = [
    'asp_utilisation',
    'asp_used_percent',
    'cpu_utilisation',
    'job_stats',
]

CHARTS = {
    'asp_utilisation': {
        'options': [None, 'System ASP Utilisation', 'Tb', 'storage statistics', 'ibmi.asp_utilisation', 'line'], 
        'lines': [
            ['system_disk_capacity', 'total capacity', 'absolute', 1, 1000000], 
            ['system_disk_used', 'used', 'absolute', 1, 1000000], 
            ['system_disk_free', 'free', 'absolute', 1, 1000000]
        ]
    }, 
    'asp_used_percent': {
        'options': [None, 'System ASP Percent Used', '%', 'storage statistics', 'ibmi.asp_used_percent', 'line'], 
        'lines': [
            ['system_disk_used_percent', 'used percent', 'absolute', 1, 1]
        ]
    }, 
    'cpu_utilisation': {
        'options': [None, 'System CPU Utilisation', '%', 'cpu statistics', 'ibmi.cpu_utilisation', 'line'], 
        'lines': [
            ['system_current_cpu_capacity', 'total', 'absolute', 1, 1], 
            ['system_avg_cpu_utilisation', 'average utilisation', 'absolute', 1, 1], 
            ['system_max_cpu_utilisation', 'maximum utilisation', 'absolute', 1, 1], 
            ['system_min_cpu_utilisation', 'minimum utilisation', 'absolute', 1, 1]
        ]
    }, 
    'job_stats': {
        'options': [None, 'System Job Statistics', 'Count', 'job statistics', 'ibmi.job_stats', 'line'], 
        'lines': [
            ['system_total_jobs', 'total', 'absolute', 1, 1], 
            ['system_active_jobs', 'active', 'absolute', 1, 1], 
            ['system_interactive_jobs', 'interactive', 'absolute', 1, 1]
        ]
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
FROM qsys2.system_status_info
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


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
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

    def connect(self):
        
        match self.rdbms:
            case 'db2':
                dsn = f'DRIVER=IBM i Access ODBC Driver;SYSTEM={self.server};UID={self.user};PWD={self.password}'
                self.db = dbdb2
            case 'mock':
                self.db = dbmock
            case _:
                HAS_DB = False
                self.alive = False
                return self.alive
                
        if self.conn:
            self.conn.close()
            self.conn = None

        try:
            match self.rdbms:
                case 'db2':
                    self.conn = self.db.connect(dsn)
                case 'mock':
                    self.conn = self.db.connect(
                        host=self.server,
                        dbname=self.database,
                        user=self.user,
                        password=self.password
                    )
                case _:
                    raise self.db.OperationalError("Invalid database type in ibmi.conf")
        except self.db.OperationalError as error:
            self.error(error)
            self.alive = False
        else:
            self.alive = True

        return self.alive


    def reconnect(self):
        return self.connect()

    def check(self):
        if not HAS_DB:
            match self.rdbms:
                case 'db2':
                    self.error("'pyodbc' package is needed to use pyodbc module")
                case 'mock':
                    self.error("'psycopg' package is needed to use psycopg module")
                case _:
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
                
        return data or None


    def gather_system_status_metrics(self):
        """
        :return:
        
        [['System ASP Storage', 0],
         ['System ASP Used', 0]]
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
                    offline = True
                    system_main_storage_size = 0
                else:
                    offline = False
                    system_main_storage_size = float(MAIN_STORAGE_SIZE)
                    metrics.append(["MAIN_STORAGE_SIZE", system_main_storage_size])                

                # ASP metrics
                if SYSTEM_ASP_USED is None:
                    offline = True
                    system_disk_used_percent = 0
                else:
                    offline = False
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
                    metrics.extend((["SYSTEM_ASP_STORAGE_CAPACITY", system_disk_capacity], ["SYSTEM_ASP_STORAGE_USED", system_disk_used], ["SYSTEM_ASP_STORAGE_FREE", system_disk_free]))

                # CPU metrics
                if CURRENT_CPU_CAPACITY is None:
                    offline = True
                    system_current_cpu_capacity = 0
                else:
                    offline = False
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
