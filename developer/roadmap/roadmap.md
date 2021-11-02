# Development Roadmap



---
## Basic requirements for the accelerator models

- Read PVs from the live machine
- publish transfer matrices, computed Twiss as PV tables
- Refresh rate should be 1/2 Hz, to help an operator hand-tune. 
    - How fast can it be?
- Read initial Twiss from PVs (served from cu_inj surrogate)

---
## Next requirements
- Read correctors, serve orbit. (Needs some analysis)
- Serve response matrices:
    - Corrector to BPM
- LEM 
- Track particles (OpenMP will speed up)


---
## LCLS Live Model development TODO
Roughly in order of priority

https://github.com/slaclab/lcls_live_model?organization=slaclab&organization=slaclab

---
## Beam code switch for 'second beam'
- needs a command line switch on init?
- BEAMCODE 1, 2
- Current init is: cu_sxr, cu_hxr. 

---
## Read initial Twiss
- should be served by cu-inj-surrogate. S
    - Surrogate should serve sigma matrix, derived 'Twiss'
- Should read from PVs

---
## Offline use
- Simple method to test this without EPICs
- Collect internal state 
- Vanilla Tao

---
## Live Model -> Live Bmad models
- There will be other models
- multi-fidelity models (see below)


---
## Clean up ModelService class
- move NTTable init outside
- generalize to serve:
    - orbit
    - get ele dict info, other structures from pytao
    - response matrices (optional)
    - beam tracking (probably a seperate model instance for this, can use OpenMP)

- Tao object
    - Tao -> TaoModel -> (LCLSTaoModel that has all Tao commands.)

- Brige: PV -> bridge -> Vanilla Tao
    
- Model saving for simple reload in tao: `tao -lat lat.bmad`

- Make more similar to the cu-inj-surrogate, LUME-model, or vice-versa?

- keep track of internal state

---
## Generalize to compute on SDF
 - Tao, Impact-T, Impact-Z, Genesis 1.3, SRW... 
 - under LUME scope

---
## Add lcls-live as a dependency
- rely on CSV mapping from lcls-live
- Klystron class from lcls-live


---
## Clean up Klystron reader
- many things are hardcoded tao commands

---
## Clean up repository
- move Python code into a subdirector, add docs
- OR, make this a very small script that depends on lcls-live classes and functions. 

---
## Documentation
The code is pretty clear, but needs docstrings, examples, etc.

---
## CTRL-C doesn't kill

---
## Need to serve fake PVs for testing
- simulation mode, from JSON file
- or simple PV server from JSON
- expand lcls-live/epics_proxy


---
## Klystron reader fails when no PVs are there

```
lcls_live_model/klystron_tools.py", line 220, in testbit
    return ((int(word) & mask) > 0)
TypeError: int() argument must be a string, a bytes-like object or a number, not 'NoneType'
```