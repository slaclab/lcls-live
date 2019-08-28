from LCLS.klystron import Klystron, existing_LCLS_klystrons, unusable_faults
from math import isnan

def bmad_klystron_lines(klystron):
    '''
    Form Bmad lines to set klystron overlays.

    '''
    k = klystron
    kname = 'K'+str(k.sector)+'_'+str(k.station)
    bmad_name = 'O_'+kname  

    # Data 
    accelerating = k.is_accelerating()
    #usable = not any(x in k.faults for x in unusable_faults)
    usable=k.is_usable()
    has_faults = k.has_faults()
    phase=k.phase
    enld=k.enld

    good_phase = not isnan(phase)
    if not good_phase or not usable: 
        phase=0


    lines = ['!---------------', '! '+kname]
    if not accelerating:
        lines.append('! is not accelerating')
    if not usable:
        lines.append('! is NOT usable') 
    if has_faults:
        lines.append('! has faults:')
        for f in k.faults:
            lines.append('!   '+f)

    if accelerating and usable:
        lines.append(bmad_name+'[ENLD_MeV] = '+str(enld))
        lines.append(bmad_name+'[phase_deg] = '+str(phase))
    else:
        lines.append(bmad_name+'[ENLD_MeV] = 0')

    return lines

def write_bmad_klystron_settings(klystrons, filePath='klystron_settings.bmad', verbose=False):
    #timestamp = '! Acquired: '+ str(datetime.datetime.now()) + '\n'
    data =map(bmad_klystron_lines, klystrons)
    
    with open(filePath, 'w') as f:
        #f.write(timestamp)
        for l in data:
            for x in l:
                f.write(x+'\n')
    if verbose:
        print(filePath, 'written')
        
        
        
def bmad_linac_phasing_lines(epics):
    """
    Linac phasing
    
    Note that these overlays override individual klystron phases. 
    
    """
    lines = [
        '! Linac overall phasing',
        'O_L1[phase_deg] = 0 ! K21_1 sets this directly', 
        'O_L2[phase_deg] = '+str(epics.caget('SIOC:SYS0:ML00:CALC204')),
        'O_L3[phase_deg] = '+str(epics.caget('SIOC:SYS0:ML00:AO499'))
    ]
    return lines

def write_bmad_linac_phasing_lines(filePath='linac_settings.bmad', epics=None, verbose=False):
    """
    Writes linac phasing lines to a Bmad file. Requires epics (or proxy object). 
    """
    lines = bmad_linac_phasing_lines(epics)
    with open(filePath, 'w') as f:
        for l in lines:
            f.write(l+'\n')
    if verbose:
        print('Written:', filePath)



def tao_LEM_lines(epics):
    """
    Linac energy set points and bunch compressor offsets
    """
    bc1_e0=epics.caget('SIOC:SYS0:ML00:AO483')*1e6
    bc2_e0=epics.caget('SIOC:SYS0:ML00:AO489')*1e9
    l3_e0 =epics.caget('SIOC:SYS0:ML00:AO500')*1e9
    bc1_offset=epics.caget( 'BMLN:LI21:235:MOTR')*1e-3
    bc2_offset=epics.caget( 'BMLN:LI24:805:MOTR')*1e-3
    lines = []
    lines.append('set dat BC1.energy[1]|meas = '+str(bc1_e0))
    lines.append('set dat BC2.energy[1]|meas = '+str(bc2_e0))
    lines.append('set dat L3.energy[2]|meas = '+str(l3_e0))
    lines.append('set dat BC1.offset[1]|meas = '+str(bc1_offset))
    lines.append('set dat BC2.offset[1]|meas = '+str(bc2_offset))

    return lines 
def write_tao_LEM_lines(filePath='LEM_settings.tao', epics=None, verbose=False):
    """
    Writes tao LEM lines to a .tao file. Requires epics (or proxy object). 
    """
    lines =tao_LEM_lines(epics)
    with open(filePath, 'w') as f:
        for l in lines:
            f.write(l+'\n')
    if verbose:
        print('Written:', filePath)




INFO_PVS = {
    'GDET:FEE1:241:ENRC': 'FEL pulse energy from gas detector (mJ)',
    'SIOC:SYS0:ML00:AO470':'Bunch charge off the cathode', 
    'SIOC:SYS0:ML00:CALC252': 'Bunch charge in the LTU',
    'SIOC:SYS0:ML00:AO485': 'BC1 mean current (A)',
    'SIOC:SYS0:ML00:AO195': 'BC2 peak current (A)',
    'SIOC:SYS0:ML00:AO513':'DL1 Energy',
    'SIOC:SYS0:ML00:AO483':'BC1 Energy',
    'SIOC:SYS0:ML00:AO489':'BC2 Energy',
    'SIOC:SYS0:ML00:AO500':'DL2 Energy',
    'ACCL:LI21:1:L1S_S_PV': 'L1 Phase',
    'SIOC:SYS0:ML00:CALC204':'L2 Phase',
    'SIOC:SYS0:ML00:AO499':'L3 Phase',
    'ACCL:IN20:350:FUDGE': 'L0 energy fudge factor',
    'ACCL:LI21:1:FUDGE': 'L1 energy fudge factor',
    'ACCL:LI22:1:FUDGE': 'L2 energy fudge factor',
    'ACCL:LI25:1:FUDGE': 'L3 energy fudge factor',
    'BMLN:LI21:235:MOTR': 'BC1 offset (mm)',
    'BMLN:LI24:805:MOTR': 'BC2 offset (mm)',
    'IOC:IN20:BP01:QANN': 'Expected charge after gun (nC)',
    'BPMS:SYS0:2:QANN':'Expected Charge after BC charge cutting (nC)'}

