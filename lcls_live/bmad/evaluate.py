
from . import LCLSTaoModel
from lcls_live.epics import epics_proxy
from lcls_live.tools import fingerprint


from pytao.tao_ctypes.core import apply_settings
from pytao.tao_ctypes import util

from h5py import File
import os


def run_LCLSTao(settings=None,
                model_name='lcls_classic',
                input_file=None,
                ploton=False,
                epics_json=None,
                verbose=False
               ):
    """
    Creates an LCLSTaoModel object, applies settings, and runs the beam.
    
    """
    
    if epics_json:
        epics = epics_proxy(epics_json, verbose=verbose)
    else:
        epics = None
    
    M = LCLSTaoModel(model_name=model_name,
                     input_file=input_file,
                     ploton=ploton,
                     epics=epics,
                     verbose=verbose)
    
    if settings:
        apply_settings(M, settings)
    
    M.run_beam()
    
    return M
    
    
    
def evaluate_LCLSTao(settings,
                model_name='lcls_classic',
                input_file=None,
                ploton=False,
                epics_json=None,
                verbose=False,
                beam_archive_path=None,
                expressions=['lat::orbit.x[end]']
               ):
    """
    
    
    
    Expressions is a list of expressions that will be used to form the output
    
    
    beam::n_particle_loss[end]
    
    """

    M = run_LCLSTao(settings=settings,
                model_name=model_name,
                input_file=input_file,
                ploton=ploton,
                epics_json=epics_json,    
                verbose= verbose
    )
    
    
    
    output = {}
    
    for expression in expressions:
        try:
            val = M.evaluate(expression)
        except:
            print(f'error with {expression}')
            val = None
        output[expression] = val    
    
    if beam_archive_path:
        ff = fingerprint({'model_name':model_name, 'input_file':input_file, 'settings':settings})
        beam_archive_path = os.path.expandvars(beam_archive_path)
        beam_archive = os.path.abspath(os.path.join(beam_archive_path, f'bmad_beam_{ff}'+'.h5'))
        if verbose:
            print('Archiving beam to', beam_archive)
        M.cmd(f'write beam -at * {beam_archive}')    
        output['beam_archive'] = beam_archive
        
        
        # Reopen and attach settings
        with File(beam_archive, 'r+') as h5:
            # Input
            g = h5.create_group('input')
            g.attrs['model_name'] = model_name
            
            #g.attrs['input_file'] = input_file
            
            
            # Settings
            g = h5.create_group('settings')
            for k, v in settings.items():
                g.attrs[k] = v
    
            g = h5.create_group('expressions')
            for k, v in output.items():
                if v:
                    g.attrs[k] = v
        
    
    return output