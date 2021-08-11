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
from typing import List, Optional
import epics


parser = argparse.ArgumentParser(description="Fetch PV data for Tao.")
parser.add_argument("--beampath", dest="beampath", type=str, choices=("cu_hxr", "cu_sxr"), help="Model to use. Currently cu_hxr or cu_sxr.", required=True)
parser.add_argument("--source", dest="source", type=str, choices=("archiver", "epics"), help="'archiver' or 'epics' source.", default="epics")
parser.add_argument("--tao", dest="tao", action="store_true", default=False, help="Generate tao commands.")
parser.add_argument("--bmad", dest="bmad", action="store_true", default=False, help="Generate bmad commands.")
parser.add_argument("--isotime", dest="isotime", type=str, help="Isotime for use with archiver.")


def get_tao_from_epics(datamaps: list, cmd_type: str) -> List[str]:
    """ Retrieve variable data using epics proxy and generate tao commands.

    Args:
        datamaps (list): List of datamaps to be used. 
        cmd_type (str): String indicating bmad or tao

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
        if cmd_type == "tao":
            cmds += dm.as_tao(pvdata)
        
        elif cmd_type == "bmad":
            cmds += dm.as_bmad(pvdata)

    return cmds
    

def get_tao_from_archiver(datamaps: list, isotime:str, cmd_type: str):
    """ Retrieve variable data using archiver and generate tao commands. 

    Args:
        datamaps (list): List of datamaps to be used. 
        config (dict): Dictionary generated from configuration file.
        cmd_type (str): string indicating tao or bmad

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

    for namme, dm in datamaps.items():
        if cmd_type == "tao":
            cmds += dm.as_tao(pvdata)
        
        elif cmd_type == "bmad":
            cmds += dm.as_bmad(pvdata)

    return cmds


def get_cmds(source: str, beampath: str, cmd_type: str, isotime: str=None, denylist: Optional[List[str]]=[]):
    """ Function for generating commands.

    Args:
        source (str): archiver or epics
        beampath (str): Model beampath
        isotime (str): Isotime stringpath
        cmd_type (str): tao or bmad
        denylist (list): list of datamap names to exclude.
    """
    dms = []
    dm_dict = get_datamaps(beampath)
    for name in dm_dict:
        if name not in denylist:
            dms.append(dm_dict[name])

    if source == "epics":
        cmds = get_tao_from_epics(dms, cmd_type)

    elif source == "archiver":
        cmds = get_tao_from_archiver(dms, isotime, cmd_type)

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

    cmd_type = "tao"
    if source == "archiver" and isotime is None:
        parser.error("archiver requires isotime.")

    if not bmad:
        tao = True
    else:
        cmd_type = "bmad"

    if bmad and tao:
        parser.error("Only one of tao or bmad may be specified.")

    cmds = get_cmds(source, beampath, cmd_type, isotime)

    for cmd in cmds:
        print(cmd)


if __name__ == "__main__":
    main()