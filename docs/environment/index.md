# User Environment


- A compiled Bmad distribution, and enabled 
- Python 3.7 or greater environment with:
    - `pyepics`
    - `pytao`

- `$LCLS_LATTICE` environmental variable pointing to the LCLS-Lattice files
- EPICS installation (for live PVs)
- Archiver access (for archived PVs)


## LCLS Production

Enable Bmad and and LCLS-Lattice:
```bash
source /usr/local/lcls/package/bmad_distributions/enable
```

## SLAC Public

This is for public linux machines such as:

- `centos7.slac.stanford.edu`

Enable Bmad and and LCLS-Lattice:
```bash
source /u/ad/cmayes/nfs/bmad_distributions/enable
```

## SLAC SDF

This is for SDF machines such as:

- `sdf.slac.stanford.edu`

Enable Bmad and and LCLS-Lattice:
```bash
source /gpfs/slac/staas/fs1/g/g.beamphysics/cmayes/bmad_distributions/enable_sdf
```

## Laptop

Install Bmad according to the official [Instructions](https://wiki.classe.cornell.edu/ACC/ACL/OffsiteDoc)
    




