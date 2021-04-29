from lcls_live.klystron import all_fault_strings, unusable_faults, typical_beam_code,  existing_LCLS_klystrons_sector_station
import dataclasses
import numpy as np
import json
import os


@dataclasses.dataclass
class KlystronDataMap:
    """
    
    
    Attributes
    ----------
    bmad_name : str
    pvlist : list[str]
    
    Methods
    -------
    evaluate(pvdata) :
        Returns
        -------
        dict of:
            enld : float
                energy gain in MeV
            phase : float
                phase in deg
            in_use : bool
                
    as_bmad(pvdata)
        Returns
        -------
        list of str:
            Bmad lattice strings to set values extracted from pvdata
            
    as_tao(pvdata)
        Returns
        -------
        list of str:
            Tao command strings  
            
    to_json(file=None)
        Returns
        -------
            JSON string, or writes to file if given. 
    
    @classmethod
    from_json(s):
        Returns a new KlystronDataMap from a JSON string or file
        
    
    
    """
    name: str
    sector: int
    station: int
    description: str = ''
    enld_pvname: str = ''
    phase_pvname: str = ''
    accelerate_pvname: str = ''
    swrd_pvname: str = ''
    stat_pvname: str = ''
    hdsc_pvname: str = ''
    dsta_pvname: str = ''
        
        
    @property
    def bmad_name(self):
        return f'{self.name}'
        
    @property
    def has_fault_pvnames(self):
        return self.swrd_pvname != ''
        
        
    @property
    def pvlist(self):
        """
        Returns a list of PV names needed for evaluation
        """
        names = [self.enld_pvname, self.phase_pvname]
        
        if self.accelerate_pvname:
            names += [self.accelerate_pvname]
        
        if self.has_fault_pvnames:
            names += [self.swrd_pvname, self.stat_pvname, self.hdsc_pvname, self.dsta_pvname]
        return names
        
    def evaluate(self, pvdata):
        """
        Returns a dict of: enld, phase, in_use evaluated from pvdata (dict-like). 
        """
        
        d = {}
        
        is_accelerating = True
        if self.accelerate_pvname != '':
            is_accelerating = (pvdata[self.accelerate_pvname] == 1)
        
        is_usable = True
        if self.has_fault_pvnames:
            swrd=pvdata[self.swrd_pvname]
            stat=pvdata[self.stat_pvname]
            hdsc=pvdata[self.hdsc_pvname]
            dsta=pvdata[self.dsta_pvname]
            
            #Horrible hack to ignore the bit for 'low RF power' on LCLS front-end klystrons.
            #if (self.sector == 20 and self.station == 7) or (self.sector == 21 and self.station == 1) or (self.sector == 21 and self.station == 2):
            #    swrd = int(swrd) & ~(1 << 5)
                              
            is_usable = klystron_is_usable(swrd=swrd, stat=stat, hdsc=hdsc, dsta=dsta)
    
        # Combine these to form
        in_use = is_accelerating and is_usable
    
        #
        phase = pvdata[self.phase_pvname]
        if phase is None or np.isnan(phase):
            phase = 0
            
        enld = pvdata[self.enld_pvname]
        if enld is None or np.isnan(enld):
            enld = 0        
        
        return dict(enld=enld, phase=phase, in_use=in_use)
        
        
        
    def as_bmad(self, pvdata):
        
        dat = self.evaluate(pvdata)
        #out = {}
        #out[f'{self.bmad_name}[ENLD_MeV]'] = dat['enld']
        #out[f'{self.bmad_name}[phase_deg]'] = dat['phase']
        #out[f'{self.bmad_name}[in_use]'] =  1 if dat['in_use'] else 0
        
        enld = dat['enld']
        phase = dat['phase']
        in_use =  1 if dat['in_use'] else 0
        
        out = [
            f'{self.bmad_name}[ENLD_MeV] = {enld}',
            f'{self.bmad_name}[phase_deg] = {phase}',
            f'{self.bmad_name}[in_use] = {in_use}']        
        
        return out
    
    def as_tao(self, pvdata):
        dat = self.evaluate(pvdata)
        
        enld = dat['enld']
        phase = dat['phase']
        in_use =  1 if dat['in_use'] else 0
        
        out = [
            f'set ele {self.bmad_name} ENLD_MeV = {enld}',
            f'set ele {self.bmad_name} phase_deg = {phase}',
            f'set ele {self.bmad_name} in_use = {in_use}']
        
        return out    
    
    def asdict(self):
        return dataclasses.asdict(self)
    
    
    @classmethod
    def from_json(cls, s):
        """
        Creates a new TablularDataMap from a JSON string
        """
        if os.path.exists(s):
            d = json.load(open(s))
        else:
            d = json.loads(s)

        return cls(**d)    
    
    def to_json(self, file=None):
        """
        Returns a JSON string
        """
        d = self.asdict()
        s = json.dumps(d)
        
        if file:
            with open(file, 'w') as f:
                f.write(s)
        else:
            return s    
    
        
    
def klystron_pvinfo(sector, station):
    """
    Customized function for creating the data to instantiate a KlystronDataMap 
    for a klystron at s given sector, station. 
    
    
    Parameters
    ----------
    sectors : int
    station : int
    
    Returns
    -------
    dict with :
        name
        sector
        station
        description
        enld_pvname
        phase_pvname
        
    and optionally:
        swrd_pvname
        stat_pvname
        hdsc_pvname
        dsta_pvname
        
    
    """
        
    # Defaults
    name = f'K{sector}_{station}'
    phase = '{base}:PHAS'        
    enld =  '{base}:ENLD'      
    description = f'Klystron in sector {sector}, station {station}'
    
    ss = (sector, station)
    

    has_beamcode = False
    has_fault_pvs = False
    
    if ss == (20, 6):
        description += ' for the GUN'
        base = 'GUN:IN20:1' 
        enld = '{base}:GN1_AAVG'   
        phase = '{base}:GN1_PAVG'           
    elif ss == (20, 7):
        description += ' for L0A'
        base = 'ACCL:IN20:300'    
        enld = '{base}:L0A_AAVG'   
        phase = '{base}:L0A_PAVG'         
    elif ss == (20, 8):
        description += ' for L0B'
        base = 'ACCL:IN20:400'    
        enld = '{base}:L0B_AAVG'   
        phase = '{base}:L0B_PAVG'                
    elif ss == (21, 1):
        description += ' for L1S'
        base = 'ACCL:LI21:1'  
        # enld = '{base}:L1S_AAVG'  Not in the archiver
        enld = 'ACCL:LI21:1:L1S_S_AV'
        #phase = '{base}:L1S_PAVG' # Not in the archiver
        phase = 'ACCL:LI21:1:L1S_S_PV'        
    elif ss == (21, 2):
        description += ' for L1X'
        base = 'ACCL:LI21:180'            
        #enld = '{base}:L1X_AAVG'   # Not in the archiver
        enld = 'ACCL:LI21:180:L1X_S_AV'
        #phase = '{base}:L1X_PAVG'  # Not in the archiver 
        phase = 'ACCL:LI21:180:L1X_S_PV'        
    elif sector == 24 and station in (1, 2, 3):
        description += ' for special feedback'
        base =  f'KLYS:LI{sector}:{station}1'     # Normal base
        phase = f'ACCL:LI24:{station}00:KLY_PDES' # Readback
        has_fault_pvs = True
        has_beamcode = True        
    # Feedback is in the subboosters for sectors 29, 30
    #elif sector in [29, 30]:
    #    description += ' for special feedback'
    #    base =  f'KLYS:LI{sector}:{station}1'     # Normal base
    #    phase = f'ACCL:LI{sector}:0:KLY_PDES'  
           
    else:
        # Normal Klystron
        name = f'K{sector}_{station}'
        base =  f'KLYS:LI{sector}:{station}1'
        has_fault_pvs = True
        has_beamcode = True
        
        
    info = {}
    info['name'] = name
    info['sector'] = sector
    info['station'] = station
    info['description'] = description
    info['enld_pvname']  = enld.format(base=base)
    info['phase_pvname'] = phase.format(base=base)
    
    # For is_accelerating
    if has_beamcode:
        beamcode = typical_beam_code(sector, station)    
        info['accelerate_pvname'] = f'{base}:BEAMCODE{beamcode}_STAT'
    
    if has_fault_pvs:
        info.update(klystron_fault_pvnames(base))
        
    return info

def klystron_fault_pvnames(base):
    dat = {}
    dat['swrd_pvname'] = f'{base}:SWRD'
    dat['stat_pvname'] = f'{base}:STAT'
    dat['hdsc_pvname'] = f'{base}:HDSC' 
    dat['dsta_pvname'] = f'{base}:DSTA'    
    return dat
    
    
def klystron_is_usable(swrd=0, stat=0, hdsc=0, dsta=0):
    fault_strings = all_fault_strings(swrd=swrd, stat=stat, hdsc=hdsc, dsta=dsta)
    return set(fault_strings).isdisjoint(unusable_faults)    





SUBBOOSTER_SECTORS = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

def subbooster_pvinfo(sector):
    """
    Returns basic PV information about a subbooster in a given sector
    
    Parameters
    ----------
    sector : int
        sector in  [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    
    Returns
    -------
    dict with:
        name : str
        description : str
        phase_pvname : str
        
    """
    
    name = f'SBST_{sector}'
    
    if sector in [21, 22, 23, 24, 25, 26, 27, 28]:
        description = 'Normal subbooster'
        phase_pvname = f'SBST:LI{sector}:1:PHAS'
    
    elif sector in [29, 30]:
        phase_pvname = f'ACCL:LI{sector}:0:KLY_PDES'
        description = 'Special feedback subbooster'
        
    else:
        raise ValueError(f'No subboosters for sector {sector}')

    dat = dict(name=name,
               phase_pvname=phase_pvname,
              desciption=description)
    
    return dat