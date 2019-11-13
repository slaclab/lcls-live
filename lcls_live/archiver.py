#!/usr/bin/env python

import requests



def lcls_archiver_restore(pvlist, isotime='2018-08-11T10:40:00.000-07:00', verbose=True):
    """
    Returns a dict of {'pvname':val} given a list of pvnames, at a time in ISO 8601 format, using the EPICS Archiver Appliance:
    
    https://slacmshankar.github.io/epicsarchiver_docs/userguide.html
    
    
    """
    
    url="http://lcls-archapp.slac.stanford.edu/retrieval/data/getDataAtTime?at="+isotime+"&includeProxies=true"
    headers = {'Content-Type':'application/json'}
    
    if verbose:
        print('Requesting:', url)
    
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




def lcls_archiver_history(pvname, start='2018-08-11T10:40:00.000-07:00', end='2018-08-11T11:40:00.000-07:00', verbose=True):
    """
    Get time series data from a PV name pvname,
        with start and end times in ISO 8601 format, using the EPICS Archiver Appliance:
    
    https://slacmshankar.github.io/epicsarchiver_docs/userguide.html
    
    
    """
    url="http://lcls-archapp.slac.stanford.edu/retrieval/data/getData.json?"
    url += "pv="+pvname
    url += "&from="+start
    url += "&to="+end
    #url += "&donotchunk"
    #url="http://lcls-archapp.slac.stanford.edu/retrieval/data/getData.json?pv=VPIO:IN20:111:VRAW&donotchunk"
    print(url)
    r = requests.get(url)
    data =  r.json()
    secs = [x['secs'] for x in data[0]['data']]
    vals = [x['val'] for x in data[0]['data']]
    return secs, vals