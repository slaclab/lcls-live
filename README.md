# lcls2-live



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
