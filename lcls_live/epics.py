#!/usr/bin/env python

from lcls_live.tools import NpEncoder

import numpy as np
import json
import os
import sys

from math import pi, sqrt, cos, sin


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
        elif not epics:
            print('File does not exist:', filename, 'and no epics source provided.')
            raise 
        
            
    def load(self, filename=None):
        if not filename:
            fname = self.filename
        else:
            fname = filename

        with open(fname, 'r') as f:
            data = f.read()

        if not data:
            self.vrpint(f"Unable to read data from file {fname}")


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
            json.dump(self.pvdata, f, cls=NpEncoder, ensure_ascii=True, indent='  ')   
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
        if self.epics:
            pvdata = self.epics.caget_many(pvnames)
            if any([pv is None for pv in pvdata]):
                self.vprint("Unable to execute caget_many. Trying individual caget with optional cache...")
                return [self.caget(n) for n in pvnames]
                
            else:
                return self.epics.caget_many(pvnames)

        else:
            return [self.caget(n) for n in pvnames]

    def PV(self, pvname, **kwargs):
        self.vprint(f'PV for {pvname}')
        m = PV_proxy(pvname, self.pvdata, epics=self.epics, **kwargs)
        self.monitor[pvname] = m
        return m
    
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
        
        

class PV_proxy:
    """
    Proxy class for the epics.PV object.
    
    Implements:
        .get
        .put
        .add_callback
    """
    
    def __init__(self, pvname, pvdata, epics=None, **kwargs):
        
        if epics:
            self.PV = epics.PV(pvname, **kwargs)
        else:
            self.PV = None
        
        self.pvname = pvname
        self.epics=epics
        self.pvdata = pvdata
        self.callbacks = []
        
    def get(self, **kwargs):
        if self.PV:
            value = self.PV.get(**kwargs)
            self.pvdata[self.pvname] = value
        return self.pvdata[self.pvname]
        
    def put(self, value, **kwargs):
        if self.PV:
            self.PV.put(value, **kwargs)         
        self.pvdata[self.pvname] = value       
        
    def add_callback(self, *args, **kwargs):
        if self.PV:
            self.PV.add_callback(*args, **kwargs)
        else:
            pass
            # TODO
        

def linac_line(name, energy, phase_deg, fudge=None):
    s = f'{name}    {energy*1e-9:10.6}    {phase_deg:10.4}'
    if fudge:
        s+=f'   {fudge*100.:10.4}'
    return s


def laser_heater_to_energy_spread(energy_uJ):
    """
    Returns rms energy spread in induced in keV.
    Based on fits to measurement in SLAC-PUB-14338
    
    """
    return 7.15*sqrt(energy_uJ)
        
        
def lcls_classic_info(epics):
    """
    Useful info for the LCLS Copper linac EPICS info
    
    """
    def get(x):
        return epics.caget(x)
    
    hline = '_______________________________________________'
    lines = [hline, hline]
    lines.append('LCLS Copper Linac EPICS info')
    lines.append('')
    charge0 = get('SIOC:SYS0:ML00:AO470')*1e3 # nC -> pC
    charge1 = get('SIOC:SYS0:ML00:CALC252')
    
    vcc_x = get('SIOC:SYS0:ML00:AO328') # mm
    vcc_y = get('SIOC:SYS0:ML00:AO329') # mm
    
    laser_heater_uJ = get('LASR:IN20:475:PWR1H') # uJ
    laser_heater_keV = laser_heater_to_energy_spread(laser_heater_uJ) # keV
    
    
    bc1current = get('SIOC:SYS0:ML00:AO485') # Averaged over 35 shots
    bc2current = get('SIOC:SYS0:ML00:AO195') # Averaged over 35 shots
    
    gdet = get('GDET:FEE1:241:ENRC')
    
    lines.append(f'Bunch charge off cathode: {charge0:6.4} pC')
    lines.append(f'VCC offset x, y: {vcc_x:6.3}, {vcc_y:6.3} mm')
    lines.append(f'Laser heater energy {laser_heater_uJ:10.4} \u03BCJ => {laser_heater_keV:6.4} keV rms energy spread')
    
    
    lines.append(f'Bunch charge in LTU:      {charge1:10.4} pC')
    lines.append(f'BC1 mean current:         {bc1current:10.4} A' )
    lines.append(f'BC2 peak current:         {bc2current:10.5} A' )
    
    # L1 + L1X
    
    voltage1x = get('ACCL:LI21:180:L1X_S_AV')*1e9
    phase1x  = get('ACCL:LI21:180:L1X_S_PV') 
    energy1x = get('SIOC:SYS0:ML00:AO483')*1e9 # BC1 Energy
    
    phase1 = get('ACCL:LI21:1:L1S_S_PV')
    energy1 =  energy1x - voltage1x*cos(pi/180.*phase1x)  # Estimate
    fudge1 =  get('ACCL:LI21:1:FUDGE')
    


    # L2
    phase2 = get('SIOC:SYS0:ML00:CALC204')
    energy2 = get('SIOC:SYS0:ML00:AO489')*1e12 # BC2 energy
    fudge2 = get('ACCL:LI22:1:FUDGE')

    # L3
    phase3 = get('SIOC:SYS0:ML00:AO499')
    energy3 = get('SIOC:SYS0:ML00:AO500')*1e12
    fudge3 = get('ACCL:LI25:1:FUDGE')    
    
    final_energy=get('SIOC:SYS0:ML00:AO500')
    
    lines.append('')
    lines.append('Linac    Energy (MeV)      Phase (deg)    fudge (%)')

    lines.append(linac_line('L1', energy1, phase1, fudge1))
    lines.append(linac_line('L1X', energy1x, phase1x))
    lines.append(linac_line('L2', energy2, phase2, fudge2))
    lines.append(linac_line('L3', energy3, phase3, fudge3))
    lines.append('')
    lines.append(f'FEL Pulse energy :         {gdet:10.2} mJ')
    
    lines.append(hline)
    
    return lines

