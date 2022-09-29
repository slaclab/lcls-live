# User Environment


- A compiled Bmad distribution, and enabled 
- Python 3.7 or greater environment with:
    - `pyepics`
    - `pytao`
    - `lcls_live`

- `$LCLS_LATTICE` environmental variable pointing to the LCLS-Lattice files
- EPICS installation (for live PVs)
- Archiver access (for archived PVs)


=== "LCLS Production"  

    Most LCLS users should use the standard Python environemt:
    ```bash
    source $TOOLS/script/use_python3.sh
    ``` 

    Developers should use the nightly environment:
    ```bash
    source $TOOLS/script/use_python3_nightly.sh
    ``` 

    These is described in [LCLS Python Environments](https://confluence.slac.stanford.edu/display/ppareg/LCLS+Python+Environments):lock: and includ the lattice files.

=== "Local"

    Local developers should clone the [LCLS-Live repository](https://github.com/slaclab/lcls-live) and create a conda environment from the `environment-dev.yml`:
    ```bash
    conda env create -f environment-dev.yml
    conda activate lcls-live-dev
    ```

    Lattice files are protected and must be install separately according to the instructions in [LCLS-Lattice-Data](https://github.com/slaclab/lcls-lattice-data) :lock:





