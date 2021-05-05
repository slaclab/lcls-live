# lcls-live

Tools for setting up the LCLS live model.

## EPICS proxy

This is to facilitate caching of EPICS values and offline usage. Basic usage:

```python
from LCLS.epics import epics_proxy
epics = epics_proxy('data/epics_cache.json')

val = epics.caget('some_pv_name')

vals = epics.caget_many(['pv', 'name', 'list'])
```

## LCLS devices

See examples

## Tao tooling

`lcls-live` is packaged with a command line tool for generating tao commands from live or archived EPICS process variables. This command may be executed:  

``` $ get-lcls-live {cu_xhr or cu_sxr} {epics or archiver} {configuration filename} {output filename}```

In order to execute this tool, the configuration file must be properly formatted for the given source (epics or archiver). The archiver requires an isotime entry. The epics tool requires the package definition of epics to be used by the abstracted interface at lcls_live.epics.epics_proxy or the definition of a json file snapshot of pv values. When used in conjunction, the json file will be used as a fallback when epics is unable to reach a variable.

An example configuration is given below:

```yaml
epics_proxy:
  epics: epics
  filename: /Users/jgarra/sandbox/lcls-live/examples/data/PVDATA-2021-04-21T08:10:25.000000-07:00.json

archiver:
  isotime: '2021-04-21T08:10:25.000000-07:00'
```

A template for this file is included in `examples/files`, but won't be of particular use unless updated for your own configuration. The environment must also be properly configured to access the resources. 

This script may be run inside of Tao by calling:  

``` $ spawn get-lcls-live {cu_xhr or cu_sxr} {epics or archiver} {configuration filename} {output filename}```


### Epics proxy environment

Access to production process variables requires setting of the `$CA_NAME_SERVER_PORT`, `$LCLS_PROD_HOST`, and `$SLAC_MACHINE`. The utility script `configure-epics` is installed with `lcls-live`. The script will perform forward local connections to the `$CA_NAME_SERVER_PORT` to the `$LCLS_PROD_HOST` via a double hop ssh and will required entry of your SLAC password. The process will run in the background and will require manual kill, identifying the pid with `ps aux |grep ssh`.

```$ configure-epics```

### Archiver environment

The archiver requires an ssh tunnel, which can be configured using the `configure-archiver` script installed with lcls-live. This should be executed in a separate shell from the Tao command and the process allowed to continue for the duration of archiver use. The script requires setting the `$ARCHIVER_HOST` and `$SLAC_USERNAME` environment variables. 

```$ configure-archiver```


## Datamaps 

A utility notebook for generating datamaps is provided in `examples/LCLS_datamaps.ipynb`. This constructs relevant datamaps using the `pytao` Tao interface and requires setting the `$LCLS_LATTICE` and `$ACC_ROOT_DIR` 



## Using archiver

## Using 


get-lcls-live cu_hxr archiver examples/files/config.yaml cmd.txt