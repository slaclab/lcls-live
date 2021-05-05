import json
import os
import argparse
from lcls_live.epics import epics_proxy
from lcls_live.archiver import lcls_archiver_restore
from lcls_live.datamaps import get_datamaps
import epics
import yaml
import sys
import imp
import importlib
from typing import List


parser = argparse.ArgumentParser(description="Fetch PV data for Tao.")
parser.add_argument("beamline", type=str, choices=("cu_hxr, cu_sxr"))
parser.add_argument("source", type=str, choices=("archiver", "epics"), help="'archiver' or 'epics' source.")
parser.add_argument("config_file", type=str, help="Configuration yaml file.")
parser.add_argument("filename", type=str, help="Command output filename.")


def get_tao_from_epics(datamaps: list, config: dict) -> List[str]:
    """ Retrieve variable data using epics proxy and generate tao commands.

    Args:
        datamaps (list): List of datamaps to be used. 
        config (dict): Dictionary generated from configuration file.

    Returns:
        List of Tao commands

    """
    epics_source =  __import__(config["epics_proxy"]["epics"])
    epics_interface = epics_proxy(epics=epics_source, filename=config["epics_proxy"]["filename"])

    tao_cmds = []
    for dm in datamaps:
        pvs = dm.pvlist
        pvdata = epics_interface.caget_many(pvs)
        pvdata={pvs[i]: pvdata[i] for i in range(len(pvs))} 
    
        tao_cmds += dm.as_tao(pvdata)

    return tao_cmds
    

def get_tao_from_archiver(datamaps: list, config: dict):
    """ Retrieve variable data using archiver and generate tao commands. 

    Args:
        datamaps (list): List of datamaps to be used. 
        config (dict): Dictionary generated from configuration file.

    Returns:
        List of Tao commands

    """

    # check appropriate variables have been set
    if not os.environ.get("http_proxy"):
        print(f"Missing $http_proxy environment variable. Please configure archiver.")
        sys.exit()

    if not os.environ.get("HTTPS_PROXY"):
        print(f"Missing $HTTPS_PROXY environment variable. Please configure archiver.")
        sys.exit()

    if not os.environ.get("ALL_PROXY"):
        print(f"Missing $ALL_PROXY environment variable. Please configure archiver.")
        sys.exit()

    if not config["archiver"].get("isotime"):
        print("Must define isotime in configuration file.")
        sys.exit()

    tao_cmds = []

    all_pvs = []
    for dm in datamaps:
        all_pvs += dm.pvlist

    pvdata = lcls_archiver_restore(all_pvs, config["archiver"]["isotime"])

    for dm in datamaps:
        tao_cmds += dm.as_tao(pvdata)

    return tao_cmds



def main(config: dict, source: str, filename: str, beamline: str) -> None:
    """ Main function responsible for executing mapping and building configuration file.

    Args:
        config (dict): Dictionary generated from configuration file.
        source (str): Choice of 'epics' or 'archiver' for pulling data
        filename (str): Filename to write tao commands
        beamline (str): Choice of beamline to run

    """
    dms = []
    datamaps = get_datamaps(config["datamaps"])

    if source == "epics":
        tao_cmds = get_tao_from_epics(datamaps, config)

    elif source == "archiver":
        tao_cmds = get_tao_from_archiver(datamaps, config)


    with open(filename, "w") as f:
        for cmd in tao_cmds:
            f.write(f"{cmd}\n")


        
if __name__ == "__main__":
    args = parser.parse_args()

    source = args.source
    config_file = args.config_file
    filename = args.filename
    beamline = args.beamline

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        main(config, source, filename, beamline)
