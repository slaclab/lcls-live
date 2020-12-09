# LCLS Live Modeling Overview

The LCLS accelerator complex consists of multiple electron sources and multiple beam paths.
Live models are computer simulation programs that continuously execute with inputs taken from the machine, and serve physics predictions of the beam behavior.






## Design models

The input files for various simulation software are collected in the [LCLS-Lattice](https://github.com/slaclab/lcls-lattice) repository (login required).
 


## Simulation software
- [Bmad and Tao](../bmad/index.md) for charged particle beam dynamics.
- [LUME-Impact](https://github.com/ChristopherMayes/lume-impact) for running [Impact-T](https://github.com/impact-lbl/IMPACT-T) from Python.
- [tensorflow](https://www.tensorflow.org/) for neural network-based machine learning (ML) surrogate models. 

## Current Live Models
- [Live Bmad accelerator models](https://github.com/slaclab/lcls_live_model)
  
    - `cu_hxr`
    - `cu_sxr`
    
     These read magnet and klystron PV at a rate of about 1 Hz, and serve transfer matrices, and Twiss parameters computed from these based on nominal starting conditions.

- [Live cu_inj surrogate model](https://github.com/slaclab/lcls-cu-inj-live)
    
    - `cu_inj` currently streaming to [YouTube](https://www.youtube.com/watch?v=Cg4TU8ZUfzk)  ![YouTube](https://img.youtube.com/vi/Cg4TU8ZUfzk/0.jpg) 
    
    This is an ML model trained on Impact-T simulations of the `cu_inj` beam path. 

## Computing requirements


## Future models:
- Bmad models for the `sc_X` for the superconducting linac beam paths. 
- Impact-T
- Bunch tracking 
- FEL interaction
- X-ray optics 



