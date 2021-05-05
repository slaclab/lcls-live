from .klystron import KlystronDataMap
from .tabular import TabularDataMap
import imp
from lcls_live import data_dir
import json
import os

def get_datamaps(config_name: str):
    """ Utility function for building data maps given a configuration file.

    Args:
        config_name (str): Choice of beamline to generate datamaps for (currently cu_hxr, cu_sxr)
    """

    with open(os.path.join(data_dir, 'datamaps_master.json'), "r") as f:
        dms = json.load(f)

    # select configs for given line
    config_dms = dms[config_name]
    loaded_dms = []

    for dm in config_dms: 
        if dm["class"] == "tabular":
            loaded = TabularDataMap.from_json(dm["data"])
        elif dm["class"] == "klystron":
            loaded = KlystronDataMap.from_json(dm["data"])
        loaded_dms.append(loaded)

    return loaded_dms

    



