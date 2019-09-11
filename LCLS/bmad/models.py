from pytao import TaoModel
from LCLS.klystron import existing_LCLS_klystrons
from LCLS.bmad import tools
from LCLS.epics import lcls_classic_info
from LCLS import data_dir


from math import pi, cos, sqrt

import os

class LCLSTaoModel(TaoModel):
    """
    """
    def __init__(self,
                 input_file='tao.init',
                 ploton = True,
                 use_tempdir=True,
                 workdir=None,
                 verbose=True,
                 so_lib='',  # Passed onto Tao superclass
                 epics=None,
                 auto_configure=True
                ):
        
        # TaoModel needs these
        super().__init__(
                input_file,
                ploton,
                use_tempdir,
                workdir,
                verbose,
                so_lib,
                auto_configure = False)
        
        # Add EPICS support
        self.epics = epics
        
        if auto_configure:
            self.configure()
        
    def configure(self):
        super().configure()
        
        
        self.load_all_settings()
        self.offset_bunch_compressors()
        self.LEM()
        
        self.vprint('Configured.')
    
    
    # Custom routines
    
    def load_all_settings(self):
        self.vprint('Loading all settings')
        return load_all_settings(self)
   

    def load_corrector_settings(self):
        self.vprint('Loading corrector settings')
        return load_corrector_settings(self)   
        
    def load_quad_settings(self):
        self.vprint('Loading quad settings')
        return load_quad_settings(self)
    
 
        
    def LEM(self):
        self.vprint('LEMing')
        return LEM(self)
        
    def offset_bunch_compressors(self):
        self.vprint('offsetting bunch compressors')
        return offset_bunch_compressors(self)
        
        
        
    def __str__(self):
        s = super().__str__()
        info = lcls_classic_info(self.epics)
        return '\n'.join(info)        
        
        
        
        
        
        

        
        
        
def load_all_settings(model):
    """
    Loads klystron, linac, and collimator settings into model from its internal epics.
    
    """

    path = model.path
    verbose = model.verbose
    epics=model.epics
    
    # Klystrons
    klist = existing_LCLS_klystrons(epics)
    kfile='settings/klystron_settings.bmad'
    model.vprint('Reading:',  kfile)
    kfile = os.path.join(path, kfile)
    tools.write_bmad_klystron_settings(klist, filePath=kfile, verbose=verbose)
    cmd='read lattice '+kfile
    res=model.cmd(cmd)
    
    # Linac oveall
    linacfile='settings/linac_settings.bmad' 
    model.vprint('Reading:',  linacfile)
    linacfile = os.path.join(path,linacfile)
    tools.write_bmad_linac_phasing_lines(filePath=linacfile, epics=epics, verbose=verbose)
    cmd='read lattice '+linacfile
    model.cmd(cmd)
    
    # Collimators
    collfile = 'settings/collimator_settings.bmad'
    model.vprint('Reading:', collfile)
    collfile = os.path.join(path, collfile)
    tools.write_bmad_collimator_lines(filePath=collfile, epics=epics, verbose=verbose)
    cmd = 'read lattice '+collfile
    model.cmd(cmd)

    # BC and LEM settings 
    bclemfile = 'settings/LEM_settings.tao'
    model.vprint('Calling:', bclemfile)
    bclemfile = os.path.join(path, bclemfile)
    tools.write_tao_BC_and_LEM_lines(filePath=bclemfile, epics=epics, verbose=verbose)
    cmd = 'call '+bclemfile
    model.cmd(cmd)


    
    
    
def load_quad_settings(model):
    csvfile=os.path.join(data_dir, 'quad_mapping_classic.csv')
    qfile = os.path.join(model.path, 'settings/quad_settings.bmad')
    tools.bmad_from_csv(csvfile, model.epics, outfile=qfile)
    model.cmd('set ele quad::* field_master = T')
    model.cmd('read lattice '+qfile)    

    
def load_corrector_settings(model):
    csvfile=os.path.join(data_dir, 'cor_mapping_classic.csv')
    cor_file = os.path.join(model.path, 'settings/cor_settings.bmad')
    tools.bmad_from_csv(csvfile, model.epics, outfile=cor_file)
    model.cmd('set ele kicker::* field_master = T')
    model.cmd('read lattice '+cor_file)    
    
    
def offset_bunch_compressors(model, script='scripts/BC_offsets.tao'):
    """
    Sets bunch compressor offsets.

    """
    cmd = 'call '+os.path.join(model.path, script)
    model.vprint(cmd)
    res = model.cmd(cmd)
    return res    


def LEM(model, script='scripts/LEM.tao'):
    """
    Sets Linac fudge factors.
        
    """
    path = model.path
    verbose=model.verbose
    epics = model.epics
    
    cmd = 'call '+os.path.join(path, script)
    model.vprint(cmd)
    res = model.cmd(cmd)
    return res










