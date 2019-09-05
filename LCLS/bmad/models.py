from pytao import TaoModel
from LCLS.klystron import existing_LCLS_klystrons
from LCLS.bmad import tools

from math import pi, cos, sqrt

import os

class LCLSTaoModel(TaoModel):
    """
    """
    def __init__(self,
                 input_file='tao.init',
                 ploton = True,
                 use_tempdir=True,
                 workdir=None,
                 verbose=True,
                 so_lib='',  # Passed onto Tao superclass
                 epics=None,
                 auto_configure=True
                ):
        
        # TaoModel needs these
        super().__init__(
                input_file,
                ploton,
                use_tempdir,
                workdir,
                verbose,
                so_lib,
                auto_configure = False)
        
        # Add EPICS support
        self.epics = epics
        
        if auto_configure:
            self.configure()
        
    def configure(self):
        super().configure()
        
        
        self.load_all_settings()
        self.offset_bunch_compressors()
        self.LEM()
        
        self.vprint('Configured.')
    
    
    # Custom routines
    
    def load_all_settings(self):
        self.vprint('Loading all settings')
        return load_all_settings(self)
        
    def LEM(self):
        self.vprint('LEMing')
        return LEM(self)
        
    def offset_bunch_compressors(self):
        self.vprint('offsetting bunch compressors')
        return offset_bunch_compressors(self)
        
        
        
    def __str__(self):
        s = super().__str__()
        info = lcls_info(self.epics)
        return '\n'.join(info)        
        
        
        
        
        
        

        
        
        
def load_all_settings(model):
    """
    Loads klystron, linac, and collimator settings into model from its internal epics.
    
    """

    path = model.path
    verbose = model.verbose
    epics=model.epics
    
    # Klystrons
    klist = existing_LCLS_klystrons(epics)
    kfile='settings/klystron_settings.bmad'
    model.vprint('Reading:',  kfile)
    kfile = os.path.join(path, kfile)
    tools.write_bmad_klystron_settings(klist, filePath=kfile, verbose=verbose)
    cmd='read lattice '+kfile
    res=model.cmd(cmd)
    
    # Linac oveall
    linacfile='settings/linac_settings.bmad' 
    model.vprint('Reading:',  linacfile)
    linacfile = os.path.join(path,linacfile)
    tools.write_bmad_linac_phasing_lines(filePath=linacfile, epics=epics, verbose=verbose)
    cmd='read lattice '+linacfile
    model.cmd(cmd)
    
    # Collimators
    collfile = 'settings/collimator_settings.bmad'
    model.vprint('Reading:', collfile)
    collfile = os.path.join(path, collfile)
    tools.write_bmad_collimator_lines(filePath=collfile, epics=epics, verbose=verbose)
    cmd = 'read lattice '+collfile
    model.cmd(cmd)

    # BC and LEM settings 
    bclemfile = 'settings/LEM_settings.tao'
    model.vprint('Calling:', bclemfile)
    bclemfile = os.path.join(path, bclemfile)
    tools.write_tao_BC_and_LEM_lines(filePath=bclemfile, epics=epics, verbose=verbose)
    cmd = 'call '+bclemfile
    model.cmd(cmd)


    
    
def offset_bunch_compressors(model, script='scripts/BC_offsets.tao'):
    """
    Sets bunch compressor offsets.

    """
    cmd = 'call '+os.path.join(model.path, script)
    model.vprint(cmd)
    res = model.cmd(cmd)
    return res    


def LEM(model, script='scripts/LEM.tao'):
    """
    Sets Linac fudge factors.
        
    """
    path = model.path
    verbose=model.verbose
    epics = model.epics
    
    cmd = 'call '+os.path.join(path, script)
    model.vprint(cmd)
    res = model.cmd(cmd)
    return res







def linac_line(name, energy, phase_deg, fudge=None):
    s = f'{name}    {energy*1e-9:10.6}    {phase_deg:10.4}'
    if fudge:
        s+=f'   {fudge*100.:10.4}'
    return s
linac_line('afaf', 1e9, 1.,1.)



def laser_heater_to_energy_spread(energy_uJ):
    """
    Returns rms energy spread in induced in keV.
    Based on fits to measurement in SLAC-PUB-14338
    
    """
    return 7.15*sqrt(energy_uJ)

def lcls_info(epics):
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
    
    laser_heater_uJ = get('LASR:IN20:475:PWR1H') # uJ
    laser_heater_keV = laser_heater_to_energy_spread(laser_heater_uJ) # keV
    
    
    bc1current = get('SIOC:SYS0:ML00:AO485') # Averaged over 35 shots
    bc2current = get('SIOC:SYS0:ML00:AO195') # Averaged over 35 shots
    
    gdet = get('GDET:FEE1:241:ENRC')
    
    lines.append(f'Bunch charge off cathode: {charge0:6.4} pC')
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