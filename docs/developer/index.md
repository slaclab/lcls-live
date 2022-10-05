# SLAC Developer setup

## LCLS Production Environment

Developers on the LCLS production environment should use the nightly builds:
```bash
source $TOOLS/script/use_python3_devel.sh
``` 
This is described in [LCLS Python Environments](https://confluence.slac.stanford.edu/display/ppareg/LCLS+Python+Environments):lock:. This includes the lattice files.




## Local

Local developers should clone the [LCLS-Live repository](https://github.com/slaclab/lcls-live) and create a conda environment from the `environment-dev.yml`:
```bash
conda env create -f environment-dev.yml
conda activate lcls-live-dev
```

Lattice files are protected and must be install separately according to the instructions in [LCLS-Lattice-Data](https://github.com/slaclab/lcls-lattice-data) :lock:

This documentation can be built with:
```bash
mkdocs serve
```
