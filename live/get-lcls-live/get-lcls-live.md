# Tao tooling

`lcls-live` is packaged with a command line tool for generating tao commands from live or archived EPICS process variables. This command may be executed using epics:  

```bash
get-lcls-live --tao --beampath cu_hxr --source epics > cmd.tao
```

And with archiver:

``` $ get-lcls-live --tao --beampath cu_hxr --source archiver --isotime '2021-04-21T08:10:25.000000-07:00' > cmd.tao```


At present the tool accomodates `--tao` or `--bmad` options for generating commands, `--beampath cu_hxr` or `--beampath cu_sxr`, `--source archiver` or `--source epics`.


### Epics remote environment

Access to production process variables requires setting of the `$CA_NAME_SERVER_PORT`, `$LCLS_PROD_HOST`, and `$SLAC_MACHINE`. The utility script `configure-epics-remote` is installed with `lcls-live`. The script will perform forward local connections to the `$CA_NAME_SERVER_PORT` to the `$LCLS_PROD_HOST` via a double hop ssh and will required entry of your SLAC password. The process will run in the background and will require manual kill, identifying the pid with `ps aux |grep ssh`.

```$ configure-epics-remote```

### Remote archiver environment

The remote archiver requires an ssh tunnel, which can be configured using the `configure-archiver-remote` script installed with lcls-live. This should be executed in a separate shell from the Tao command and the process allowed to continue for the duration of archiver use. The script requires setting the `$SLAC_ARCHIVER_HOST` and `$SLAC_USERNAME` environment variables. 

```$ configure-archiver-remote```


## Datamaps 

A utility notebook for generating datamaps is provided in `examples/LCLS_datamaps.ipynb`. This constructs relevant datamaps using the `pytao` Tao interface and requires setting the `$LCLS_LATTICE` and `$ACC_ROOT_DIR` 