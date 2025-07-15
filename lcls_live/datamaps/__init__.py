from .klystron import KlystronDataMap
from .tabular import TabularDataMap
from lcls_live import data_dir
import json
import pandas as pd
import os
from typing import Union, List

# Parse all 
with open(os.path.join(data_dir, 'datamaps_master.json'), "r") as f:
     ALL_DATAMAPS = json.load(f)


def get_datamaps(config_name: str, use_des: Union[bool, List[str]] = False):
    """ Utility function for building data maps given a configuration file.

    Args:
        config_name (str): Choice of beamline to generate datamaps for (currently 
                           cu_hxr, cu_sxr, sc_inj, sc_diag0, sc_bsyd, sc_hxr, or sc_sxr)
                           
        use_des (bool or list[str], optional): Whether to use DES values instead of ACT.
                           If use_des is a bool, it will apply to all data maps.
                           If use_des is a list of strings, only the datamaps whose names
                           are in use_des will use DES instead of ACT.
        
    Returns:
        dict of name:datamap
        
    """

    # select configs for given line
    config_dms = ALL_DATAMAPS[config_name]
    loaded_dms = {}
    for dm in config_dms:
        if dm["class"] == "tabular":
            d = json.loads(dm["data"])
            data = pd.read_json(d.pop('data'))
            # Handle cases where use_des applies
            if dm["name"] in ("quad", "correctors", "solenoid", "quad_corrector", "subboosters", "cavities"):
                if (use_des is True) or (use_des is not False and dm["name"] in use_des):
                    d["pvname"] = "pvname" #convention is: pvname is the DES PV, pvname_rbv is the ACT PV.
            loaded = TabularDataMap(data=data, **d)
        elif dm["class"] == "klystron":
            use_des_for_klys = (use_des is True) or (use_des is not False and "klystron" in use_des)
            loaded = KlystronDataMap.from_json(dm["data"], use_des=use_des_for_klys)
        loaded_dms[dm["name"]] = loaded

    return loaded_dms


