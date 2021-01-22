


# Requirements for Model Services (live models)

Physics-based `models` are intended to provide physical predictions of beam-related quantities. We have am immediate need for injector and beamline `model services` that continuously read from a common EPICS network and serve some of these quantiies as PVs on the same network.  



The following are `minimal` requirements.



# Model Source

Models shall be collected in git repositories hosted at https://github.com/slaclab/

Baseline physics models are collected in the `lcls-lattice` git repository. The main source is hosted at:
https://github.com/slaclab/lcls-lattice
with the `$LCLS_LATTICE` enviromnental variable defined on local systems to point to a checked out version.



# lcls-cu-inj-live 
    
- source: https://github.com/slaclab/lcls-cu-inj-live

- dependencies:
   - model: https://github.com/slaclab/lcls-cu-inj-surrogate
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
        - YAGO2
        - OTR2
    - beam phase space projections at the same screens


# lcls-cu-beamline

source: 

model: `$LCLS_LATTICE/bmad/models/cu_hxr/` (Bmad/Tao)

EPICS inputs: 
    - Klystron level phases and amplitudes
    - Linac overall phases
    - quadrupole strengths
    - bunch compressor settings
 
EPICS outputs:
    - Twiss parameters at all elements



## cu_hxr



## cu_sxr
    Similar to cu_hxr



