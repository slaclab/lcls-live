from lcls_live.klystron import all_fault_strings, unusable_faults, existing_LCLS_klystrons_sector_station
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
    description: str
    ampl_act_pvname: str
    ampl_des_pvname: str
    phase_act_pvname: str
    phase_des_pvname: str
    accelerate_pvname: str = ''
    swrd_pvname: str = ''
    stat_pvname: str = ''
    hdsc_pvname: str = ''
    dsta_pvname: str = ''
    use_des: bool = False
    
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
        if self.use_des:
            names = [self.ampl_des_pvname, self.phase_des_pvname]
        else:
            names = [self.ampl_act_pvname, self.phase_act_pvname]
        
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
        if self.sector == 26 and self.station == 3: #Always disable mothballed 26-3 klystron.
            is_accelerating = False
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
        # TODO: Raise exception
        in_use = is_accelerating and is_usable
        if self.use_des:
            phase = pvdata[self.phase_des_pvname]
        else:
            phase = pvdata[self.phase_act_pvname]
        if phase is None or np.isnan(phase):
            phase = 0
        
        if self.use_des:
            enld = pvdata[self.ampl_des_pvname]
        else:
            enld = pvdata[self.ampl_act_pvname]
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
    def from_json(cls, s, use_des=False):
        """
        Creates a new TablularDataMap from a JSON string
        """
        if os.path.exists(s):
            d = json.load(open(s))
        else:
            d = json.loads(s)
        d["use_des"] = use_des
        return cls(**d)    
    
    def to_json(self, file=None):
        """
        Returns a JSON string
        """
        d = self.asdict()
        del d["use_des"] #Don't put the use_des property in the json file, it is ephemeral.
        
        if file:
            with open(file, 'w') as f:
                json.dump(d, f)
        else:
            s = json.dumps(d)
            return s    
    
        
    
def klystron_pvinfo(sector, station, beamcode=1):
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
        ampl_act_pvname
        ampl_des_pvname
        phase_act_pvname
        phase_des_pvname
        accelerate_pvname
        
    and optionally:
        swrd_pvname
        stat_pvname
        hdsc_pvname
        dsta_pvname
        
    
    """
        
    # Defaults
    name = f'K{sector}_{station}'
    phase_des = '{base}:PDES'
    phase_act = '{base}:PHAS'
    ampl_act =  '{base}:ENLD'
    ampl_des =  '{base}:ENLD'
    description = f'Klystron in sector {sector}, station {station}, beamcode {beamcode}'
    
    ss = (sector, station)
    
    has_beamcode = False
    has_fault_pvs = False
    
    # Datastore suffix 0, 1 for beamcodes 1, 2
    DS = f'_DS{beamcode-1}'
    
    if ss == (20, 6):
        description += ' for the GUN'
        base = 'GUN:IN20:1' 
        ampl_des = '{base}:GN1_ADES'
        phase_des = '{base}:GN1_PDES'
        ampl_act = '{base}:GN1_AAVG'
        phase_act = '{base}:GN1_PAVG'
    elif ss == (20, 7):
        description += ' for L0A'
        base = 'ACCL:IN20:300'
        ampl_des = '{base}:L0A_ADES'+DS
        phase_des = '{base}:L0A_PDES'+DS
        ampl_act = '{base}:L0A_AACT'+DS
        phase_act = '{base}:L0A_PACT'+DS
    elif ss == (20, 8):
        description += ' for L0B'
        base = 'ACCL:IN20:400'
        ampl_des = '{base}:L0B_ADES'+DS  
        phase_des = '{base}:L0B_PDES'+DS
        ampl_act = '{base}:L0B_AACT'+DS  
        phase_act = '{base}:L0B_PACT'+DS
    elif ss == (21, 1):
        description += ' for L1S'
        base = 'ACCL:LI21:1'
        ampl_des = 'ACCL:LI21:1:L1S_ADES'+DS
        phase_des = 'ACCL:LI21:1:L1S_PDES'+DS
        ampl_act = 'ACCL:LI21:1:L1S_AACT'+DS
        phase_act = 'ACCL:LI21:1:L1S_PACT'+DS
    elif ss == (21, 2):
        description += ' for L1X'
        base = 'ACCL:LI21:180'
        ampl_des = 'ACCL:LI21:180:L1X_ADES'+DS
        phase_des = 'ACCL:LI21:180:L1X_PDES'+DS
        ampl_act = 'ACCL:LI21:180:L1X_AACT'+DS
        phase_act = 'ACCL:LI21:180:L1X_PACT'+DS
    elif sector == 24 and station in (1, 2, 3):
        description += ' for special feedback'
        base =  f'KLYS:LI{sector}:{station}1'     # Normal base
        phase_des = f'ACCL:LI24:{station}00:KLY_PDES' # Readback
        phase_act = f'ACCL:LI24:{station}00:KLY_PDES' # No ACT PV available, always use DES

        # Add beamcode suffix
        phase_des += f':SETDATA_{beamcode}' # GETDATA should be better, but missing in the archiver
        phase_act += f':SETDATA_{beamcode}' # GETDATA should be better, but missing in the archiver
        
        has_fault_pvs = True
        has_beamcode = True        
        
    # Do not do anything special for 29, 30. Feedback is in the subboosters for sectors 29, 30
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
        
    # Broken Klystron. Was a test-bed for a mothballed project to upgrade the electronics for the klystrons.    
    if ss == (26, 3):
        has_beamcode = False
        has_fault_pvs = False
        
    info = {}
    info['name'] = name
    info['sector'] = sector
    info['station'] = station
    info['description'] = description
    info['ampl_act_pvname']  = ampl_act.format(base=base)
    info['ampl_des_pvname']  = ampl_des.format(base=base)
    info['phase_act_pvname'] = phase_act.format(base=base)
    info['phase_des_pvname'] = phase_des.format(base=base)
    
    # For is_accelerating
    if has_beamcode:
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
    if swrd is None: 
        return False
    if stat is None:
        return False
    if hdsc is None:
        return False
    if dsta is None:
        return False
    
    swrd = int(swrd)
    stat = int(stat)
    hdsc = int(hdsc)
    dsta = list(map(int, dsta))
    
    fault_strings = all_fault_strings(swrd=swrd, stat=stat, hdsc=hdsc, dsta=dsta)
    return set(fault_strings).isdisjoint(unusable_faults)    





SUBBOOSTER_SECTORS = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

def subbooster_pvinfo(sector, beamcode):
    """
    Returns basic PV information about a subbooster in a given sector
    
    Parameters
    ----------
    sector : int
        sector in  [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    
    beamcode : int in [1, 2]
        beam code, == 1 for HXR
                   == 2 for SXR
    
    Returns
    -------
    dict with:
        name : str
        description : str
        phase_act_pvname : str
        phase_des_pvname : str
        
    """
    
    name = f'SBST_{sector}'
    
    if sector in [21, 22, 23, 24, 25, 26, 27, 28]:
        description = 'Normal subbooster'
        phase_act_pvname = f'SBST:LI{sector}:1:PHAS'
        phase_des_pvname = f'SBST:LI{sector}:1:PDES'
    elif sector in [29, 30]:
        phase_act_pvname = f'ACCL:LI{sector}:0:KLY_PDES'
        
        if beamcode == 2:
            phase_act_pvname += ':SETDATA_1'
        phase_des_pvname = phase_act_pvname
        description = f'Special feedback subbooster, beamcode {beamcode}'
        
    else:
        raise ValueError(f'No subboosters for sector {sector}')

    dat = dict(name=name,
               phase_act_pvname=phase_act_pvname,
               phase_des_pvname=phase_des_pvname,
               desciption=description)
    
    return dat