import pandas as pd
import h5py
import numpy as np
import datetime
import os


BSA_DATA_SEARCH_PATHS = ['/gpfs/slac/staas/fs1/g/bsd/BSAService/data/',
                        '/nfs/slac/g/bsd/BSAService/data/'       
                        ]



def get_bsa_data_path():
    for d in BSA_DATA_SEARCH_PATHS:
        if os.path.exists(d):
            return d
    raise ValueError(f'Cannot find BSA data path. Searched: {BSA_DATA_SEARCH_PATHS}')
    
def bsa_h5file_end_time(filename):    
    time_str  =  os.path.splitext(os.path.split(filename)[1])[0][-15:]
    naive_time = datetime.datetime.strptime(time_str, '%Y%m%d_%H%M%S')          
    return pd.Timestamp(naive_time, tz='UTC')
    
def bsa_h5file(timestamp, beampath):
    """    
    Finds the BSA HDF5 file that contains the timestamp for a given beampath
    
    BSA data files are named as:
        CU_SXR_20211210_140742.h5
        
    Which corresponds to '{beampath}_{time_str}.h5' with time_str in the format: '%Y%m%d_%H%M%S'
        
    See the documentation in:
        https://www.slac.stanford.edu/grp/ad/docs/model/matlab/bsd.html
         "The data files are named with the UTC datestamp of the END of their data taking period"
         
    Parameters
    ----------
    
    timestamp: datetime-like, str, int, float
        This must be localized (not naive time).
    
    beampath : str
            one of ['cu_hxr', 'cu_sxr'] (case independent)
        
    Returns
    -------
    h5file : str
        Full path to the HDF5 file that should contain the time. 
            
            
    Examples
    --------
    
    >>> bsa_h5file('2021-12-11T00:00:00-08:00', 'cu_hxr')
    '/gpfs/slac/staas/fs1/g/bsd/BSAService/data/2021/12/11/CU_HXR_20211211_080825.h5'
    
    
    
    """
    
    timestamp = pd.Timestamp(timestamp).tz_convert('UTC') # Convert to UTC
    
    # Files should be prefixed with upper case beampaths
    beampath = beampath.upper()
    
    # Strings with zero padding
    year =  str(timestamp.year)
    month = f'{timestamp.month:02}'
    day = f'{timestamp.day:02}'
    
    # All h5 files should be in here
    root = get_bsa_data_path()
    
    # This is the nearest path
    path = os.path.join(root, year, month , day )
    
    # Find the file
    files = [f for f in os.listdir(path) if f.startswith(beampath) and f.endswith('.h5')]
    times = list(map(bsa_h5file_end_time, files))
    found = False
    for time, file in sorted(zip(times, files)):
        if  time > timestamp:
            found = True
            #print('FOUND', time, timestamp)
            break
    if not found:
        raise ValueError(f'Could not find BSA file containing {timestamp} in {path}')
        
    return os.path.join(path, file)



def extract_pvdata(h5file, timestamp, pvnames=None):
    """
    Extract as a snapshot (PV values) nearest a timestamp from a BSA HDF5 file.
    
    Parameters
    ----------
    h5file: str
        BSA HDF5 file with data that includes the timestamp
        
    timestamp: datetime-like, str, int, float
        This must be localized (not naive time).
    
    Returns
    -------
    pvdata: dict
        Dict of pvname:value
    
    found_timestamp : pd.Timestamp
        The exact time that the data was tagged at
        
            
    See Also
    --------        
    bsa_snapshot
    
    
    """
    
    timestamp = pd.Timestamp(timestamp).tz_convert('UTC') # Convert to UTC    
    
    with h5py.File(h5file) as h5:
        
        # Use pandas to get the nearest time
        s = h5['secondsPastEpoch'][:, 0]
        ns = h5['nanoseconds'][:, 0]
        df = pd.DataFrame({'s':s, 'ns':ns})
        df['time'] = pd.to_datetime(df['s'], unit='s', utc=True) + pd.to_timedelta(df['ns'], unit='nanoseconds')
        
        # Assure that the time is in here
        assert timestamp <= df.time.iloc[-1]
        assert timestamp >= df.time.iloc[0]
        
        # Search for the nearest time
        ix = df.time.searchsorted(timestamp)
        found_timestamp = df['time'].iloc[ix]
        
        # form snapshot dict
        pvdata = {}
    
        # Return everything
        if pvnames is None:
            pvnames = list(h5)
    
        for pvname in pvnames:
            if pvname in h5:
                pvdata[pvname] = np.squeeze(h5[pvname][ix])
            else:
                pvdata[pvname] = None

    return pvdata, found_timestamp




def bsa_snapshot(timestamp, beampath, pvnames=None):
    """
    Extract as a snapshot (PV values) nearest a timestamp from a BSA HDF5 file.
    
    Parameters
    ----------        
    timestamp: datetime-like, str, int, float
        This must be localized (not naive time).
        
        
    pvnames : list or None
        List of PV names to extract. If None, all PVs in the source file will be extracted.
        Optional, default=None
        
    Returns
    -------
    snapshot: dict
        Dict with:
            'pvdata' : dict of {pv name:pv value}
            'timestamp' : pd.Timestamp, including the nanosecond.
            'source' : Original HDF5 file that the data came from.
           
    Notes
    -----
    timestamp will be cast to a pd.Timestamp internally.
    See: https://pandas.pydata.org/docs/reference/api/pandas.Timestamp.html
    
    Examples
    --------
    >>>bsa_snapshot('2021-11-11T00:00:00-08:00', 'cu_hxr')
    
    """    
    h5file = bsa_h5file(timestamp, beampath)
    pvdata, found_timestamp = extract_pvdata(h5file, timestamp, pvnames=pvnames)
    
    snapshot = {}
    snapshot['pvdata'] = pvdata
    snapshot['timestamp'] = found_timestamp
    snapshot['source'] = h5file
    
    return snapshot





