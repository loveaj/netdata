<!--
title: "IBM i monitoring with Netdata"
-->

# IBM i monitoring with Netdata

Monitors the performance and health metrics of the the IBM i platform (aka IBM AS/400, IBM iSeries).

## Requirements

-   `pyodbc` package  
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

1.  Install `pyodbc` and `unixODBC-devel` packages:  
    `sudo yum install pyodbc unixODBC-devel`  
   
2.  Install the IBM i Access ODBC Driver for Linux ([link](https://ibmi-oss-docs.readthedocs.io/en/latest/odbc/installation.html#linux)).  
    Install the repository:  
    `curl https://public.dhe.ibm.com/software/ibmi/products/odbc/rpms/ibmi-acs.repo | sudo tee /etc/yum.repos.d/ibmi-acs.repo`  
    Install the ODBC driver:  
    `sudo yum install --refresh ibm-iaccess`

3.  Create a read-only `netdata` user with proper access to your IBM i Server.  


## Configuration

Edit the `python.d/ibmi.conf` configuration file using `edit-config` from the Netdata [config
directory](/docs/configure/nodes.md), which is typically at `/etc/netdata`.

```bash
cd /etc/netdata   # Replace this path with your Netdata config directory, if different
sudo ./edit-config python.d/ibmi.conf
```

```yaml
remote:
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
