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
    else:
        suffix = '1H'
    
    dm_x = datamap_from_tao_data(tao, 'orbit', 'x', tao_factor = .001, pv_attribute=':X'+suffix)
    dm_y = datamap_from_tao_data(tao, 'orbit', 'y', tao_factor = .001, pv_attribute=':Y'+suffix)    
    
    dm_charge = datamap_from_tao_data(tao, 'orbit', 'charge', tao_factor = e_charge, pv_attribute=':TMIT'+suffix)
    
    #dm_x.data.append(dm_y.data, ignore_index = True)
    #dm_x.data.append(dm_charge.data, ignore_index = True)    
    
    frames = [dm_x.data, dm_y.data, dm_charge.data]
    
    dm_x.data = pd.concat(frames, ignore_index=True)
    
    return dm_x



#---------------------------
# Correctors

def build_corrector_dm(tao):
    xeles = tao.lat_list('hkicker::*', 'ele.name', flags='-array_out -no_slaves')
    yeles = tao.lat_list('vkicker::*', 'ele.name', flags='-array_out -no_slaves')
    eles = xeles + yeles

    df = pd.DataFrame()
    df['bmad_name'] = pd.Series(eles)
    df['pvname'] = [ tao.ele_head(ele)['alias']+':BACT' for ele in df['bmad_name' ] ]
    df['bmad_factor'] = -1/10 # kG*m -> T (with the correct sign)
    df['bmad_attribute'] = 'bl_kick'

    dm = TabularDataMap(df, pvname='pvname', element='bmad_name', attribute = 'bmad_attribute', factor='bmad_factor')    
    
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
        'pvname': 'BEND:DMPH:400:EDES', # or EDES
        'tao_datum': 'L3.energy[2]',
        'factor': 1e9
        } ]
    
    ENERGY_MEAS_SXR = [ {
        'name': 'L3_SXR_energy',
        'pvname': 'BEND:DMPS:400:EDES', # or EDES
        'tao_datum': 'L3.energy[2]',
        'factor': 1e9
        } ]    
    
    if model == 'cu_hxr':
        df = pd.DataFrame(ENERGY_MEAS0 + ENERGY_MEAS_HXR)
    elif model == 'cu_sxr':
         df = pd.DataFrame(ENERGY_MEAS0 + ENERGY_MEAS_SXR)
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
    return d

def build_quad_dm(tao):
    quad_names = tao.lat_list('quad::*', 'ele.name', flags='-no_slaves')
    dfq = pd.DataFrame([quad_pvinfo(tao, ele) for ele in quad_names])
    dm = TabularDataMap(dfq, pvname='pvname_rbv', element='bmad_name', attribute = 'bmad_attribute', factor='bmad_factor')
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
    dm = TabularDataMap(df, pvname='phase_pvname', element='bmad_name', attribute='bmad_attribute')
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
