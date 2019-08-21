#!/usr/bin/env python

import requests



def lcls_archiver_restore(pvlist, isotime='2018-10-22T10:40:00.000-07:00', verbose=True):
    """
    Returns a dict of {'pvname':val} given a list of pvnames, at a time in ISO 8601 format, using the EPICS Archiver Appliance:
    
    https://slacmshankar.github.io/epicsarchiver_docs/userguide.html
    
    
    """
    url="http://lcls-archapp.slac.stanford.edu/retrieval/data/getDataAtTime?at="+isotime+"&includeProxies=true"
    headers = {'Content-Type':'application/json'}
    data = pvlist
    r = requests.post(url, headers=headers, json=data)
    res = r.json()
    d = {}
    for k in pvlist:
        if k not in res:
            if verbose:
                print('Warning: Missing PV:', k)
        else:
            d[k] = res[k]['val']
    return d