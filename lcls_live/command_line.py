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
import epics


parser = argparse.ArgumentParser(description="Fetch PV data for Tao.")
parser.add_argument("--beampath", dest="beampath", type=str, choices=("cu_hxr", "cu_sxr"), help="Model to use. Currently cu_hxr or cu_sxr.", required=True)
parser.add_argument("--source", dest="source", type=str, choices=("archiver", "epics"), help="'archiver' or 'epics' source.", default="epics")
parser.add_argument("--tao", dest="tao", action="store_true", default=True, help="Generate tao commands.")
parser.add_argument("--bmad", dest="bmad", action="store_true", default=False, help="Generate bmad commands.")
parser.add_argument("--isotime", dest="isotime", type=str, help="Isotime for use with archiver.")


def get_tao_from_epics(datamaps: list, tao: bool, bmad: bool) -> List[str]:
    """ Retrieve variable data using epics proxy and generate tao commands.

    Args:
        datamaps (list): List of datamaps to be used. 
        config (dict): Dictionary generated from configuration file.

    Returns:
        List of Tao commands

    """
    if os.environ.get("CA_NAME_SERVER_PORT"):
        os.environ["EPICS_CA_NAME_SERVERS"] = f"localhost:{os.environ['CA_NAME_SERVER_PORT']}"

    epics_interface = epics_proxy(epics=epics)

    cmds = []

    all_pvs = []
    for dm in datamaps:
        all_pvs += dm.pvlist

    pvdata = epics_interface.caget_many(all_pvs)

    for dm in datamaps:
        if tao:
            cmds += dm.as_tao(pvdata)
        
        elif bmad:
            cmds += dm.as_bmad(pvdata)

    return cmds
    

def get_tao_from_archiver(datamaps: list, isotime:str, tao: bool, bmad: bool):
    """ Retrieve variable data using archiver and generate tao commands. 

    Args:
        datamaps (list): List of datamaps to be used. 
        config (dict): Dictionary generated from configuration file.

    Returns:
        List of Tao commands

    """

    if os.environ.get("SLAC_ARCHIVER_HOST"):
        os.environ["http_proxy"] = "socks5h://localhost:8080"
        os.environ["HTTPS_PROXY"] = "socks5h://localhost:8080"
        os.environ["ALL_PROXY"] = "socks5h://localhost:8080"


    cmds = []

    all_pvs = []
    for dm in datamaps:
        all_pvs += dm.pvlist

    pvdata = lcls_archiver_restore(all_pvs, isotime)

    for dm in datamaps:
        if tao:
            cmds += dm.as_tao(pvdata)
        
        elif bmad:
            cmds += dm.as_bmad(pvdata)

    return cmds



def main() -> None:
    """ Main function responsible for executing mapping and building configuration file.

    """
    args = parser.parse_args()
    source = args.source
    beampath = args.beampath
    isotime = args.isotime
    tao =args.tao
    bmad = args.bmad

    if source == "archiver" and isotime is None:
        parser.error("archiver requires isotime.")

    if source == bmad and tao:
        parser.error("Only one of tao or bmad may be specified.")


    dms = []
    datamaps = get_datamaps(beampath)

    if source == "epics":
        tao_cmds = get_tao_from_epics(datamaps, tao, bmad)

    elif source == "archiver":
        tao_cmds = get_tao_from_archiver(datamaps, isotime, tao, bmad)

    for cmd in tao_cmds:
        print(cmd)


if __name__ == "__main__":
    main()