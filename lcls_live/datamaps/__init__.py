from .klystron import KlystronDataMap
from .tabular import TabularDataMap
import imp
from lcls_live import data_dir
import json
import os


# Parse all 
with open(os.path.join(data_dir, 'datamaps_master.json'), "r") as f:
     ALL_DATAMAPS = json.load(f)


def get_datamaps(config_name: str):
    """ Utility function for building data maps given a configuration file.

    Args:
        config_name (str): Choice of beamline to generate datamaps for (currently 
                           cu_hxr, cu_sxr, sc_inj, sc_diag0, sc_bsyd, sc_hxr, or sc_sxr)
        
    Returns:
        dict of name:datamap
        
    """

    # select configs for given line
    config_dms = ALL_DATAMAPS[config_name]
    loaded_dms = {}

    for dm in config_dms: 
        if dm["class"] == "tabular":
            loaded = TabularDataMap.from_json(dm["data"])
        elif dm["class"] == "klystron":
            loaded = KlystronDataMap.from_json(dm["data"])
        loaded_dms[dm["name"]] = loaded

    return loaded_dms

    



