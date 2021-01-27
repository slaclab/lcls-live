


# Requirements for Models and Model Services (live models)

Physics-based `models` are intended to provide physical predictions of beam-related quantities. We have an immediate need for injector and beamline `model services` that continuously read from a common EPICS network and serve some of these quantities as PVs on the same network.  



The following are `minimal` requirements.



---
# Computing

- All models and model services should be able to run on the production, devel, and SDF environments. 


---
# Models


Models are collected in git repositories hosted at https://github.com/slaclab/

Baseline physics models are collected in the `lcls-lattice` git repository. The main source is hosted at:
https://github.com/slaclab/lcls-lattice
with the `$LCLS_LATTICE` enviromnental variable defined on local systems to point to a checked out version.


## lcls-cu-inj
- source: `$LCLS_LATTICE/impact/models/cu_inj`
- documentation: TODO
- dependencies: 
    - Impact-T executable

## lcls-cu-inj-surrogate

- source: https://github.com/slaclab/lcls-cu-inj-surrogate
- developers:
    - Auralee Edelen
- description: Pre-trained neural network surrogage model for the lcls-cu-inj model. 
- documentation: at source
- dependencies: 
    - Python 
        - tensorflow

    

## lcls-beamlines
- source: `$LCLS_LATTICE/bmad/models/cu_hxr`, `cu_sxr`
- documentation: TODO
- dependencies: Bmad distribution (executables and libraries)




---
# Model Services

## lcls-cu-inj-live 
    
- source: https://github.com/slaclab/lcls-cu-inj-live
- Developers:
    - Jaqueline Garrahan
    - Hugo Slepicka 


- documentation: https://github.com/slaclab/lcls-cu-inj-live/blob/main/README.md

- dependencies:
   - model: lcls-cu-inj-surrogate
   - software:
       - Python
           - tensorflow
           - lume-model
           - lume-epics
           

- EPICS inputs: 
    - laser parameters
    - Gun and Linac phases and amplitudes
    - Magnet strengths (Solenoid, corrector quads, quads)

- EPICS outputs:
    - beam sigma matrix at screens:
        - YAG02
        - OTR2
    - beam phase space projections at the same screens


## lcls-beamlines
- source: https://github.com/slaclab/lcls_live_model
- developers:
    - Matt Gibbs
    - Christopher Mayes
    - Hugo Slepicka
    
- documentation: TODO
- dependencies: 
    - lcls-beamlines models
    - Python
        - pyepics

        
- EPICS inputs: 
    - Initial Twiss (TODO)
    - Klystron level phases and amplitudes
    - Linac overall phases
    - quadrupole strengths
    - bunch compressor settings

- EPICS outputs:
    - Twiss parameters at all elements



# Deployment


## cu-inj-surrogate
on DMZ

retraining using SDF

## lcls-beamlines:sxr, hxr
on DMZ






