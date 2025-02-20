from lcls_live.datamaps.tabular import TabularDataMap, datamap_from_tao_data
from lcls_live.datamaps.klystron import KlystronDataMap, klystron_pvinfo, existing_LCLS_klystrons_sector_station, subbooster_pvinfo, SUBBOOSTER_SECTORS




import pandas as pd
from scipy.constants import e as e_charge



# beamcodes for cu_hxr and cu_sxr
def get_beamcode(model):
    if model == 'cu_hxr':
        beamcode = 1
    elif model == 'cu_sxr':
        beamcode = 2
    else:
        raise ValueError(f'Unknown model: {model}')
    return beamcode



#---------------------------
# BPMs

def build_bpm_dm(tao, model):
    """
    Build BPM datamaps
    """
    
    if model == 'cu_hxr':
        suffix = 'CUH1H' # 1 Hz
    elif model == 'cu_sxr':
        suffix = 'CUS1H' # 1 Hz
    elif model == 'cu_spec':
        suffix = '1H'
    elif model == 'sc_hxr':
        suffix = 'SCH1H'
    elif model == 'sc_sxr':
        suffix = 'SCS1H'
    elif model in ('sc_bsyd', 'sc_diag0', 'sc_inj'):
        suffix = ''
    else:
        suffix = '1H'
    
    dm_x = datamap_from_tao_data(tao, 'orbit', 'x',
                                 tao_factor = .001,
                                 pv_attribute=':X'+suffix,
                                 bmad_unit='m')
    dm_y = datamap_from_tao_data(tao, 'orbit', 'y',
                                 tao_factor = .001,
                                 pv_attribute=':Y'+suffix,
                                 bmad_unit='m')    
    dm_charge = datamap_from_tao_data(tao, 'orbit', 'charge',
                                      tao_factor = e_charge,
                                      pv_attribute=':TMIT'+suffix,
                                      bmad_unit = 'C')
    
    
    #dm_x.data.append(dm_y.data, ignore_index = True)
    #dm_x.data.append(dm_charge.data, ignore_index = True)    
    
    frames = [dm_x.data, dm_y.data, dm_charge.data]
    
    dm_x.data = pd.concat(frames, ignore_index=True)
    
    return dm_x


#---------------------------
# Cavities 
# sc_ lines only



def cavity_phase_pvinfo(tao, ele_name, model):
    """
    Returns dict of PV information for use in a DataMap
    """
    head = tao.ele_head(ele_name)
    attrs = tao.ele_gen_attribs(ele_name)
    device = head['alias']
    
    d = {}
    d['bmad_name'] = ele_name
    
    # Special for buncher
    if ele_name.startswith('BUN'):
        d['pvname_rbv'] = device+':PACT_AVG'
    else:
        d['pvname_rbv'] = device+':PACTMEAN'
        
    d['pvname'] = device+':PDES'    
    d['bmad_factor'] = 1/360 # deg -> rad/2pi
    d['bmad_attribute'] = 'phi0'
    d['bmad_unit'] = '2pi'
    return d

def cavity_amplitude_pvinfo(tao, ele_name, model):
    """
    Returns dict of PV information for use in a DataMap
    
    TODO: pvname for setting unknown
    """
    ele_name = ele_name.upper()
        
    head = tao.ele_head(ele_name)
    attrs = tao.ele_gen_attribs(ele_name)
    device = head['alias']
    
    d = {}
    d['bmad_name'] = ele_name
    
    
    # Special for buncher
    if ele_name.startswith('BUN'):
        suffix_rbv = ':AACT_AVG'
    else:
        suffix_rbv = ':AACTMEAN'
    
    if model == 'sc_inj':
        # Voltage reported is the v=c voltage

        # Buncher
        if ele_name.startswith('BUN'):
            # from v=c fieldmap integral
            bmad_factor = 1e6 * 1/0.038464987091053844# MV -> V/m
        # 1.3 GHz cavities
        elif  ele_name.startswith('CAVL'):      
            # voltage = E_max * 0.5370721151478917 m 
            # The fieldmap is scaled to E_max = 1, and field_autoscale scales that.
            # Analysis using $LCLS_LATTICE/bmad/fieldmaps/cavity9/cavity9_1300MHz_full.h5            
            bmad_factor = 1e6 * 1/0.5370721151478917# MV -> V/m
        else:
            raise ValueError(f'sc_inj, unknown cavity {ele_name}')
                             
        d['bmad_attribute'] = 'field_autoscale'    
        d['bmad_unit'] = 'V/m'
    else:
        bmad_factor = 1e6 # MV -> V
        d['bmad_attribute'] = 'voltage'      
        d['bmad_unit'] = 'V'        
    
    d['pvname'] = device+":ADES"
    d['pvname_rbv'] = device+suffix_rbv
    d['bmad_factor'] = bmad_factor
                             
    return d


def build_cavity_dm(tao, model):
    """
    Superconducting cavity phases and amplitudes datamap. 
    
    See:
        https://confluence.slac.stanford.edu/display/LCLSControls/LCLS-II+LLRF+Naming+Conventions
        https://aosd.slac.stanford.edu/wiki/index.php/Abstraction_Layer_API
        
    """
    
    # Check that this is SC line
    assert tao.branch1(ix_uni=1, ix_branch=0)['name'].startswith('SC_')
    
    # SRF cavities and the buncher
    # TODO: TX* elements
    eles1 = tao.lat_list('LCAVITY::CAV*', 'ele.name', flags='-array_out -no_slaves')
    eles2 = tao.lat_list('LCAVITY::BUN*', 'ele.name', flags='-array_out -no_slaves')
    eles = eles1 + eles2

    df1 = pd.DataFrame([cavity_phase_pvinfo(tao, ele_name, model) for ele_name in eles])
    df2 = pd.DataFrame([cavity_amplitude_pvinfo(tao, ele_name, model) for ele_name in eles])    
    
    df = pd.concat([df1, df2], ignore_index=True, axis=0)
    
    dm = TabularDataMap(df, pvname='pvname_rbv', element='bmad_name', attribute = 'bmad_attribute', factor='bmad_factor')
    return dm    
    
    

def old_build_cavity_dm(tao, model):
    """
    Superconducting cavity phases and amplitudes datamap. 
    
    See:
        https://confluence.slac.stanford.edu/display/LCLSControls/LCLS-II+LLRF+Naming+Conventions
    """
    
    # Check that this is SC line
    assert tao.branch1(ix_uni=1, ix_branch=0)['name'].startswith('SC_')
    
    # superconducting cavities only
    eles = tao.lat_list('LCAVITY::CAV*', 'ele.name', flags='-array_out -no_slaves')
    
    device_names = [tao.ele_head(ele)['alias'] for ele in eles]
    
    # Phases
    # Measured phase from cavity probe (degrees), averaged over LLRF waveform.
    # Identical to CAV:PMEAN. Typically averaged over ~350 ms, 
    # but this can vary depending on waveform settings.
    df1 = pd.DataFrame()
    df1['bmad_name'] = pd.Series(eles)
    df1['pvname'] = [d+':PACTMEAN' for d in device_names]
    df1['bmad_factor'] = 1/360 # deg -> rad/2pi
    df1['bmad_attribute'] = 'phi0'
    
    # Amplitudes
    # Measured amplitude from cavity probe (MV), 
    # averaged over LLRF waveform. Identical to CAV:AMEAN. 
    # Typically averaged over ~350 ms, but this can vary depending on waveform settings.
    
    df2 = pd.DataFrame()
    df2['bmad_name'] = pd.Series(eles)
    df2['pvname'] = [d+':AACTMEAN' for d in device_names]
    
    if model == 'sc_inj':
        # Voltage reported is the v=c voltage
        # voltage = E_max * 0.5370721151478917 m 
        # The fieldmap is scaled to E_max = 1, and field_autoscale scales that.
        # Analysis using $LCLS_LATTICE/bmad/fieldmaps/cavity9/cavity9_1300MHz_full.h5
        df2['bmad_factor'] = 1e6 * 1/0.5370721151478917# MV -> V
        df2['bmad_attribute'] = 'field_autoscale'    
    else:
        df2['bmad_factor'] = 1e6 # MV -> V
        df2['bmad_attribute'] = 'voltage'    
    
    df = pd.concat([df1, df2], ignore_index=True, axis=0)

    dm = TabularDataMap(df, pvname='pvname', element='bmad_name', attribute = 'bmad_attribute', factor='bmad_factor')    
    
    return dm



#---------------------------
# Correctors

def build_corrector_dm(tao):
    xeles = tao.lat_list('hkicker::*', 'ele.name', flags='-array_out -no_slaves')
    yeles = tao.lat_list('vkicker::*', 'ele.name', flags='-array_out -no_slaves')
    eles = xeles + yeles

    df = pd.DataFrame()
    df['bmad_name'] = pd.Series(eles)
    df['pvname'] = [ tao.ele_head(ele)['alias']+':BDES' for ele in df['bmad_name' ] ]
    df['pvname_rbv'] = [ tao.ele_head(ele)['alias']+':BACT' for ele in df['bmad_name' ] ]
    df['bmad_factor'] = -1/10 # kG*m -> T (with the correct sign)
    df['bmad_attribute'] = 'bl_kick'
    df['bmad_unit'] = 'T*m'

    dm = TabularDataMap(df, pvname='pvname_rbv', element='bmad_name', attribute = 'bmad_attribute', factor='bmad_factor')    
    
    return dm



#---------------------------
# Energy Measurements

def build_energy_dm(model):
    # The syntax is flexible enough to use for getting measurements for Tao
    ENERGY_MEAS0 = [
        {
        'name': 'L1_energy',
        'pvname': 'BEND:LI21:231:EDES', # or EDES
        'tao_datum': 'BC1.energy[1]',        
        'factor': 1e9
        },
        {
        'name': 'L2_energy',
        'pvname': 'BEND:LI24:790:EDES', # or EDES
        'tao_datum': 'BC2.energy[1]',
        'factor': 1e9
        }
    ]
    
    ENERGY_MEAS_HXR = [ {
        'name': 'L3_HXR_energy',
        'pvname': 'BEND:DMPH:400:EDES', 
        'tao_datum': 'L3.energy[2]',
        'factor': 1e9
        } ]
    
    ENERGY_MEAS_SXR = [ {
        'name': 'L3_SXR_energy',
        'pvname': 'BEND:DMPS:400:EDES', 
        'tao_datum': 'L3.energy[2]',
        'factor': 1e9
        } ]    
    
    # sc 
    ENERGY_MEAS_SC = [ {
        'name': 'L0B_energy',
        'pvname': 'BEND:HTR:480:BACT', 
        'tao_datum': 'L0B.energy[1]',
        'factor': 1e9
        } ]    
    
    if model == 'cu_hxr':
        df = pd.DataFrame(ENERGY_MEAS0 + ENERGY_MEAS_HXR)
    elif model == 'cu_sxr':
         df = pd.DataFrame(ENERGY_MEAS0 + ENERGY_MEAS_SXR)
    elif model.startswith('sc_'):
        df = pd.DataFrame(ENERGY_MEAS_SC)
    else:
        raise ValueError(f'Unknown model: {model}')    
    
    
    dm = TabularDataMap(df, pvname='pvname', element='tao_datum', factor='factor',
                       tao_format = 'set data {element}|meas  = {value}',
                       bmad_format = '! No equivalent Bmad format for: set data {element}|meas  = {value}'
                       )
    return dm



#---------------------------
# Linac

def build_linac_dm(model):
    dat0 = [
        
        {'name': 'BC1_offset',
         'pvname':'BMLN:LI21:235:MOTR',  # mm
         'bmad_factor': 0.001,
         'bmad_name': 'O_BC1_OFFSET',
         'bmad_attribute': 'offset'
        },
        
        {'name': 'BC2_offset',
         'pvname':'BMLN:LI24:805:MOTR', # mm
         'bmad_factor': 0.001,
         'bmad_name': 'O_BC2_OFFSET',
         'bmad_attribute': 'offset'
        },
        
        {
        'name': 'L1_phase',
        'description': 'Controls the L1 phase, which is the single klystron L21_1. We will disable this for now, because the KlystronDataMap handles the phase directly.',
        'pvname': 'ACCL:LI21:1:L1S_S_PV',
        'bmad_name':'O_L1',
        'bmad_factor': 0,  # We'll disable this for now. The Klystron handles it. 
        'bmad_attribute':'phase_deg'
        
    }
    ]
    
    dat_hxr = [
            {
        'name': 'L2_phase',
        'pvname': 'ACCL:LI22:1:PDES',
        'bmad_name':'O_L2',
        'bmad_factor': 1,
        'bmad_attribute':'phase_deg'
        
    },
        {
        'name': 'L3_phase',
        'pvname': 'ACCL:LI25:1:PDES',
        'bmad_name':'O_L3',
        'bmad_attribute':'phase_deg',
        'bmad_offset': 0
        
    }, 
    ]
    
    # SXR has different PVs
    dat_sxr = [
            {
        'name': 'L2_phase',
        'pvname': 'ACCL:LI22:1:PDES:SETDATA_1',
        'bmad_name':'O_L2',
        'bmad_factor': 1,
        'bmad_attribute':'phase_deg'
        
    },
        {
        'name': 'L3_phase',
        'pvname': 'ACCL:LI25:1:PDES:SETDATA_1',
        'bmad_name':'O_L3',
        'bmad_attribute':'phase_deg',
        'bmad_offset': 0
        
    }, 
    ]

    #Note that there are sone NaNs here. That's okay.
    if model == 'cu_hxr':
        df = pd.DataFrame(dat0+dat_hxr)
    elif model == 'cu_sxr':
        df = pd.DataFrame(dat0+dat_sxr)
    else:
        raise ValueError(f'Unknown model: {model}')
        
    dm = TabularDataMap(df, pvname='pvname', element='bmad_name', attribute='bmad_attribute', factor='bmad_factor', offset='bmad_offset')
    
    return dm



#---------------------------
# Klystrons

def build_klystron_dms(tao, model):
    

    beamcode = get_beamcode(model)
    
    klystron_names = tao.lat_list('overlay::K*', 'ele.name', flags='-no_slaves')

    klystron_datamaps = []
    for sector, station in existing_LCLS_klystrons_sector_station:
        info = klystron_pvinfo(sector, station, beamcode=beamcode)
        k = KlystronDataMap(**info)

        if k.name in klystron_names:
            klystron_datamaps.append(k)
    
    return klystron_datamaps



#---------------------------
# Quads

def quad_pvinfo(tao, ele):
    """
    Returns dict of PV information for use in a DataMap
    """
    head = tao.ele_head(ele)
    attrs = tao.ele_gen_attribs(ele)
    device = head['alias']
    
    d = {}
    d['bmad_name'] = ele
    d['pvname_rbv'] = device+':BACT'
    d['pvname'] = device+':BDES'    
    d['bmad_factor'] = -1/attrs['L']/10
    d['bmad_attribute'] = 'b1_gradient'
    d['bmad_unit'] = 'T/m'
    return d

def build_quad_dm(tao):
    quad_names = tao.lat_list('quad::*', 'ele.name', flags='-no_slaves')
    
    # This belongs in quad_correctors.
    if 'CQ02B' in quad_names:
        quad_names.remove('CQ02B')
    
    dfq = pd.DataFrame([quad_pvinfo(tao, ele) for ele in quad_names])
    dm = TabularDataMap(dfq, pvname='pvname_rbv', element='bmad_name', attribute = 'bmad_attribute', factor='bmad_factor')
    return dm


#---------------------------
# Quad correctors

def quad_corrector_pvinfo(tao, ele):
    """
    Returns dict of PV information for use in a DataMap
    
    These are for use with field_master = T,
    so that `k1l` is interpreted as `gradient*L`
    
    """
    head = tao.ele_head(ele)
    attrs = tao.ele_gen_attribs(ele)
    device = head['alias']
    
    key = head['key'].upper()
    assert key == 'MULTIPOLE'
    
    d = {}
    d['bmad_name'] = ele
    d['pvname_rbv'] = device+':BACT'
    d['pvname'] = device+':BDES'    
    d['bmad_factor'] = -1/10 # kG -> T, with LCLS's (wrong) sign convention
    d['bmad_attribute'] = 'k1l'
    d['bmad_unit'] = 'T'
    return d

def build_sc_quad_corrector_dm(tao):
    # These are actually mutipole elements
    quad_names = ['SQ01B', 'CQ01B', 'SQ02B'] 
    #  is a quadrupole element
    quad_info = [quad_corrector_pvinfo(tao, ele) for ele in quad_names] + [quad_pvinfo(tao, 'CQ02B')]
    
    dfq = pd.DataFrame(quad_info)
    dm = TabularDataMap(dfq, pvname='pvname_rbv', element='bmad_name', attribute = 'bmad_attribute', factor='bmad_factor')
    return dm


#---------------------------
# Solenoids
    
# Field integral conversion factors
# PVs report the field integral in kg-m
# Bmad models are scaled for the peak field
SC_INJ_SOLENOID_FACTOR = {
    'SOL1BKB': 0, # unknown
    'SOL1B': 0.1/0.08623995 , # kG-m to T:  \int B dL = B_max * 0.1/0.08623995 m
    'SOL2B': 0.1/0.08623995 , # Same as SOL1B
}
    
    
def solenoid_pvinfo(tao, ele, model):
    """
    Returns dict of PV information for use in a DataMap
    """
    head = tao.ele_head(ele)
    attrs = tao.ele_gen_attribs(ele)
    device = head['alias']
    
    # Get field integral conversion factor
    if model == 'sc_inj':
        factor = SC_INJ_SOLENOID_FACTOR[ele]
    else:
        # hard-edge
        L = attrs['L']
        if L == 0:
            factor = 0 # CANNOT DO ZERO LENGTH SOLENOID
        else:
            factor = 0.1/L  #\int BL in kG*m -> B_hard (T)
    
    d = {}
    d['bmad_name'] = ele
    d['pvname_rbv'] = device+':BACT'
    d['pvname'] = device+':BDES'    
    d['bmad_factor'] =factor
    d['bmad_attribute'] = 'bs_field'
    d['bmad_unit'] = 'T'
    return d

def build_solenoid_dm(tao, model):
    names = tao.lat_list('solenoid::*', 'ele.name', flags='-no_slaves')
    df = pd.DataFrame([solenoid_pvinfo(tao, ele, model) for ele in names])
    dm = TabularDataMap(df, pvname='pvname_rbv', element='bmad_name', attribute = 'bmad_attribute', factor='bmad_factor')
    return dm    

#---------------------------
# Subboosters

def build_subbooster_dm(model):
    
    beamcode = get_beamcode(model)
    
    subboosters = []
    for sector in SUBBOOSTER_SECTORS:

        dat = subbooster_pvinfo(sector, beamcode) 
        dat['bmad_name'] = f'SBST_{sector}'
        dat['bmad_attribute'] = 'phase_deg'
        subboosters.append(dat)
    df = pd.DataFrame(subboosters)    

    # Make the DataMap object, identifying the columns to be used
    dm = TabularDataMap(df, pvname='pvname_rbv', element='bmad_name', attribute='bmad_attribute')
    return dm


#---------------------------
# Twiss from measurements

def beginning_meas_twiss_datamap(name, pvprefix):
    dat =  [
    {
    'name': f'{name}_beta_x_meas',
    'pvname': f'{pvprefix}:BETA_X', 
    'bmad_name': 'beginning',   
    'bmad_attribute': 'beta_a'
    },
    {
    'name': f'{name}_beta_y_meas',
    'pvname': f'{pvprefix}:BETA_Y', 
    'bmad_name': 'beginning',   
    'bmad_attribute': 'beta_b'
    },
    {
    'name': f'{name}_alpha_x_meas',
    'pvname': f'{pvprefix}:ALPHA_X', 
    'bmad_name': 'beginning',   
    'bmad_attribute': 'alpha_a'
    },
    {
    'name': f'{name}_alpha_y_meas',
    'pvname': f'{pvprefix}:ALPHA_Y', 
    'bmad_name': 'beginning',   
    'bmad_attribute': 'alpha_b'
    },    
    ]
    
    df= pd.DataFrame(dat)

    return TabularDataMap(df, pvname='pvname', element='bmad_name', attribute = 'bmad_attribute')
