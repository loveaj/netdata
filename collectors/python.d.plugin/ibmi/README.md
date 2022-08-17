<!--
title: "IBM i monitoring with Netdata"
-->

# IBM i monitoring with Netdata

Monitors the performance and health metrics of the the IBM i platform (aka IBM AS/400, IBM iSeries).

## Requirements

-   `ibm_db` package.

It produces following charts:

- System
  - CPU Utilization %
  - Interactive CPU Utilization %
  - Scaled Speed Vs. Nominal %
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

1.  Install `ibm_db` package ([link](https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html)).  

2.  Create a read-only `netdata` user with proper access to your IBM i Server.  


## Configuration

Edit the `python.d/ibmi.conf` configuration file using `edit-config` from the Netdata [config
directory](/docs/configure/nodes.md), which is typically at `/etc/netdata`.

```bash
cd /etc/netdata   # Replace this path with your Netdata config directory, if different
sudo ./edit-config python.d/ibmi.conf
```

```yaml
remote:
  user: 'netdata-service'
  password: 'secret'
  server: '10.0.0.1'
```

All parameters are required. Without them module will fail to start.


