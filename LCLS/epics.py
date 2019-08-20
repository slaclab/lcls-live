#!/usr/bin/env python

import numpy as np
import json
import os
import sys


class epics_proxy(object):
    """
    EPICS proxy. This can be intialized from a JSON file 'file'.
    
    
    
    """
    def __init__(self, filename=None, epics=None, verbose=False):
        
        self.filename = filename
        self.epics = epics
        self.verbose=verbose
            
        # Internal data
        self.pvdata = {}
        
        # Monitors
        self.monitor = {}
        
        if filename and os.path.exists(filename): 
            self.load()
        else:
            print('File does not exist:', filename)
            raise 
        
            
    def load(self, filename=None):
        if not filename:
            fname = self.filename
        else:
            fname = filename
        with open(fname, 'r') as f:
            data = f.read()
        newdat = json.loads(data)               
        self.pvdata.update(newdat)
        self.vprint('Loaded', fname, 'with', len(list(newdat)), 'PVs')

    def save(self, filename=None):
        """
        Saves internal .pvdata to a JSON file. 
        """
        if not filename:
            fname = self.filename
        else:
            fname = filename
        with open(fname, 'w') as f:
            json.dump(self.pvdata, f, cls=NumpyEncoder, ensure_ascii=True, indent='  ')   
        self.vprint('Saved', fname)


 
    @property
    def all_monitors_connected(self):
        return all([self.monitor[m].wait_for_connection() for m in self.monitor])

    def connect_monitor(self, pvname, wait=False):
        m = self.epics.PV(pvname)
        if wait:
            m.wait_for_connection()
        self.monitor[pvname] = m
        return m

    def connect_monitors(self, wait=False):
        for pvname in self.pvdata:
            self.connect_monitor(pvname, wait=wait)        
    
    def caput(self, pvname, value):
        self.pvdata[pvname] = value
    
    def caget(self, pvname):
        if pvname not in self.pvdata:
            self.vprint('Error: pv not cached:', pvname)   
            if self.epics:
                self.vprint('Loading from epics')
                self.pvdata[pvname] = self.epics.caget(pvname)
        return self.pvdata[pvname]            

    def caget_many(self, pvnames):
        return [self.caget(n) for n in pvnames]

    def vprint(self, *args, **kwargs):
        # Verbose print
        if self.verbose:
            print(*args, **kwargs)
            
            
    def update(self):
        # load live values from epics
        # From Monitors:
        pvlist = []
        if not self.epics:
            self.vprint('Warning: no EPICS connected. Nothing to update')
            return
        
        for pvname in self.pvdata:
            if pvname in self.monitor:
                self.pvdata[pvname] = self.monitor[pvname].get()
            else:
                # Collect non-monitor pvs
                pvlist.append(pvname)
                
        if len(pvlist) > 0:
            self.vprint('caget_many on', pvlist)
            vals = self.epics.caget_many( pvlist)
            res = dict(zip(self.attributes, vals)) 
            self.pvdata.update(res)           
    
    def __str__(self):
        s = 'EPICS proxy with '+str(len(self.pvdata.keys()))+' PVs'
        return s        
        
        
        
        
        
# For dumping numpy arrays, from:
# https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)        