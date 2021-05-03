import json
import os
import argparse
from lcls_live.epics import epics_proxy
from lcls_live.datamaps import get_datamaps
import epics
import pandas as pd
import yaml
import sys
import imp
import importlib

parser = argparse.ArgumentParser(description="Fetch PV data for Tao.")
parser.add_argument("source", type=str, choices=("archiver", "epics"), help="'archiver' or 'epics' source.")
parser.add_argument("config_file", type=str, help="Configuration yaml file.")
parser.add_argument("filename", type=str, help="Command output filename.")

def locate(path):
    module = ".".join(path.split(".")[:-1])
    classname = path.split(".")[-1]

    mod = importlib.import_module(module)
    class_obj = getattr(mod, classname)
    return class_obj

def get_epics_pvs(pvlist, epics_reference):
    epics = __import__(epics_reference)


def main(config, source, filename):
    """
    Main function responsible for executing mapping and building configuration file.
    """
    dms = []

    print(config["datamaps"])
    datamaps = get_datamaps(config["datamaps"])

    if source == "epics":
        epics_source =  __import__(config["epics_proxy"]["epics"])
        epics_interface = epics_proxy(epics=epics_source, filename=config["epics_proxy"]["filename"])

    tao_cmds = []
    for dm in datamaps:
        pvs = dm.pvlist
        if source == "epics":
            try:
                PVDATA = epics_interface.caget_many(pvs)
                PVDATA={pvs[i]: PVDATA[i] for i in range(len(pvs))} 
            except:
                breakpoint()

        tao_cmds += dm.as_tao(PVDATA)
    
    with open(filename, "w") as f:
        for cmd in tao_cmds:
            f.write(f"{cmd}\n")



        
if __name__ == "__main__":
    args = parser.parse_args()

    source = args.source
    config_file = args.config_file
    filename = args.filename

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        main(config, source, filename)
