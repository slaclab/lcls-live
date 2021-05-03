from .klystron import KlystronDataMap
from .tabular import TabularDataMap
import imp

# TODO: Fix mappings and granularity of the configuration

BASE = imp.find_module('lcls_live')[1]

DATAMAP_REFERENCES={
    "subboosters": BASE + "/data/cu/subboosters_TabularDataMap.json",
    "linac": BASE + "/data/cu/linac_TabularDataMap.json",
    "beginning_OTR2": BASE + "/data/cu/beginning_OTR2_TabularDataMap.json",
    "quad": BASE + "/data/cu_hxr/quad_TabularDataMap.json",
    "kystron": BASE + "/data/cu/sector{}_station{}_klystron_datamap.json",
    "tao_energy_measurements": BASE + "/data/cu_hxr/tao_energy_measurements_TabularDataMap.json"
}

KLYSTRON_SECTOR_STATION_MAP = {20: [6,7,8], 21: [1,2,3,4,5,6,7,8], 22: [1,2,3,4,5,6,7,8], 23: [1,2,3,4,5,6,7,8], 24: [1,2,3,4,5,6], 25: [1,2,3,4,5,6,7,8], 26: [1,2,3,4,5,6,7,8], 27: [1,2,3,4,5], 28: [1,2,3,4,5,6,7,8], 29: [1,2,3,4,5,6,7,8], 30: [1,2,3,4,5,6,7,8]}

def get_datamaps(config):
    """
    Utility function for building data maps given a configuration file.
    """
    dms = []

    if "linac" in config:
        dm = TabularDataMap.from_json(DATAMAP_REFERENCES["linac"])
        dms.append(dm)

    if "quad" in config:
        dm = TabularDataMap.from_json(DATAMAP_REFERENCES["quad"])
        dms.append(dm)

    if "tao_energy_measurements" in config:
        dm = TabularDataMap.from_json(DATAMAP_REFERENCES["tao_energy_measurements"])
        dms.append(dm)

    if "subboosters" in config:
        dm = TabularDataMap.from_json(DATAMAP_REFERENCES["subboosters"])
        dms.append(dm)

    if "beginning_OTR2" in config:
        dm = TabularDataMap.from_json(DATAMAP_REFERENCES["beginning_OTR2"])
        dms.append(dm)

    if "klystron" in config:
      #  if config["klystron"].get("all"):
        for sector in KLYSTRON_SECTOR_STATION_MAP:
            for station in KLYSTRON_SECTOR_STATION_MAP[sector]:
                dm = TabularDataMap.from_json(DATAMAP_REFERENCES["beginning_OTR2"]).format(sector, station)
                dms.append(dm)

      #  elif config["kylstron"].get("sector") and config["kylstron"]["sectors"].get("station"):
       #     dm = TabularDataMap(DATAMAP_REFERENCES["beginning_OTR2"]).format(sector, station)
       #     dms.append(dm)

    return dms

    



