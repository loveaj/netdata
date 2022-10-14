<!--
title: "IBM i monitoring with Netdata"
-->

# IBM i monitoring with Netdata

Monitors the performance and health metrics of the the IBM i platform (aka IBM AS/400, IBM iSeries).

## Requirements

-   `pyodbc` package 
-   `psycopg2` package  
-   `unixODBC-devel` package
-   `gcc` and `gcc-c++` packages 
-   IBM i Access ODBC Driver for Linux  

It produces following charts:

- System
  - CPU Utilization %
  - Interactive CPU Utilization %
  - Physical CPU % consumed in shared pool
  - Virtual CPU % consumed in shared pool
  - Disk ASP Used %
  - Disk Temporary Used %
  - Total Jobs
  - Active Jobs
  - Total Active Threads
<!-- - Job queues
  - Total
  - Active
  - Scheduled
  - Held
  - Released -->
## Prerequisite

To use the IBM i module do the following:

1.  Install `pyodbc`,`psycopg` and `unixODBC-devel` packages:  
    `sudo yum install pyodbc unixODBC-devel python3-psycopg2`
   
2.  Instal `gcc` and `gcc-c++` packages:
    `sudo yum instyall gcc gcc-c++`  

3.  Install the IBM i Access ODBC Driver for Linux ([link](https://ibmi-oss-docs.readthedocs.io/en/latest/odbc/installation.html#linux)).  
    Install the repository:  
    `curl https://public.dhe.ibm.com/software/ibmi/products/odbc/rpms/ibmi-acs.repo | sudo tee /etc/yum.repos.d/ibmi-acs.repo`  
    Install the ODBC driver:  
    `sudo yum install ibm-iaccess`  

*NB* The Python pyodbc package is used rather than ibm_db because the use of ibm_db from a remote client requires a paid for license from IBM. (Running it locally on the IBM i itself is free).  

4.  Create a read-only `netdata` user with proper access to your IBM i Server.  


## Configuration

Edit the `python.d/ibmi.conf` configuration file using `edit-config` from the Netdata [config
directory](/docs/configure/nodes.md), which is typically at `/etc/netdata`.

```bash
cd /etc/netdata   # Replace this path with your Netdata config directory, if different
sudo ./edit-config python.d/ibmi.conf
```

```yaml
remote:
  rdbms: 'db2'
  database: 'LPARNAME'
  user: 'netdata'
  password: 'secret'
  server: '10.0.0.1'
```

All parameters are required. Without them module will fail to start.


## OS specifics

### Linux
Netdata custom plugin `/usr/libexec/netdata/python.d`  
Netdata custom plugin config `/opt/homebrew/etc/netdata/python.d`  

### MacOS
Netdata custom plugin `/opt/homebrew/opt/netdata/libexec/netdata/python.d`  
Netdata custom plugin config `/etc/netdata/python.d`  

## Creating a mock system_status_info database for local development  
### Install Postgresql
`sudo yum install http://apt.postgresql.org/pub/repos/yum/reporpms/F-36-x86_64/pgdg-fedora-repo-latest.noarch.rpm`
`sudo yum install postgresql-server`
`sudo yum install postgresql-docs`
`sudo yum install postgresql-devel`
`sudo yum install postgresql14-libs postgresql14-odbc postgresql14-plperl postgresql14-plpython3 postgresql14-pltcl postgresql14-tcl postgresql14-contrib postgresql14-llvmjit`  

`sudo systemctl enable --now postgresql-14`
`sudo /usr/pgsql-14/bin/postgresql-14-setup initdb`

### Create a netdata user and set permissions

### Import mock data table

