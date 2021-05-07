# Getting Started



## Bmad and Tao Tutorial

If you are new to Bmad and Tao, please go to the official [Bmad website](https://www.classe.cornell.edu/bmad/) and follow the [Tutorial document](https://www.classe.cornell.edu/bmad/tutorial_bmad_tao.pdf) using the [Example files](https://www.classe.cornell.edu/bmad/tutorial_bmad_tao_files/).

The tutorial is designed to be self-paced, with an introductory video presentation and chapter-specific channels in the [Bmad Slack Workspace](http://bmad-simulation.slack.com)

## Setup

See [Enviromnent](environment/index.md) for how to set up your environment on various systems.


## Tao command line

```bash
tao -init $LCLS_LATTICE/bmad/models/cu_hxr/tao.init
```

## PyTao

```python
from pytao import Tao
tao = Tao('-init $LCLS_LATTICE/bmad/models/cu_hxr/tao.init')
```

## Live or archived PV data
Use the [get-lcls-live](live/get-lcls-live.md) command line tool to extract PV data from EPICS or the archiver, and form the appropriate tao commands:

```bash
get-lcls-live --beampath cu_hxr --source epics --tao > cmds.tao
```



## Examples

Explore the [Jupyter Notebook Examples](https://github.com/slaclab/lcls-live/tree/master/examples)

