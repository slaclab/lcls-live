#!/usr/bin/env python



class Device(object):
    """
    Base class for a general EPICS device.
    
    
    Derived classes should set this as:
    .PVname = {'attrib_name':'full_PV_name'}
    
    Initialization does not call any methods. Derived classes should call to initialize:
    .update()
    
    
    Example:
    class Magnet(Device):
        def __init__(self, **kwargs): 
            super().__init__(**kwargs)
            
            # Full PV name dictionary. Keys will be attributes of this class
            self.PVname = {'bact': self.basePV+':BACT', 
                           'z': self.basePV+':Z',         
                           'madname': self.basePV+':MADNAME'}
            self.configure()
        
    """
    def __init__(self, basePV='DeviceType:Area:Position', 
                epics=None,
                verbose=False
                ):
        self.basePV = basePV
        self.epics = epics
        self.verbose = verbose
        
        # Full PV name dictionary. The user should set this
        self.PVname = {} 
        
        # Internal usage
        self.monitor = {}
        self.faults = []
        
    @property
    def type(self):
        return self.basePV.split(':')[0]
            
    @property
    def attributes(self):
        return list(self.PVname)
    
    def update(self):
        pvlist = []
        for attrib in self.attributes:
            # Do monitors first
            if attrib in self.monitor:
                self.vprint('Monitor get for', attrib)
                self.__dict__[attrib] = self.monitor[attrib].get()  
            else:
                # Collect non-monitor attributes
                pvlist.append(self.PVname[attrib])
                
        if len(pvlist) > 0:
            self.vprint('caget_many on', pvlist)
            vals = self.epics.caget_many( pvlist)
            res = dict(zip(self.attributes, vals)) 
            self.__dict__.update(res)

    # Monitors    
    def connect_monitor(self, attrib, callback=None):
        """
        Connects EPICS monitor to .monitor dictionary
        Example: attrib='stat' connects a monitor to KLYS:LI##:STAT, and sets:
                .monitor['stat']
                
        """
        pvname = self.PVname[attrib]
        monitor = self.epics.PV(pvname)   
        self.monitor[attrib] = monitor
        if callback: 
            monitor.add_callback(callback)   
   
    def connect_monitors(self):
        for name in self.attributes:    
            self.connect_monitor(name)  
        
        self.update()            
    
    def disconnect_monitors(self):
        self.monitor = {}    

    def vprint(self, *args, **kwargs):
        # Verbose print
        if self.verbose:
            print(*args, **kwargs)           
    
   # Disconnect monitors for pickling
    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        state['monitor'] = {}
        if self.verbose:
            for k in state:
                 print(state[k])
        return state
    # Reconnect monitors for unpickling
    def __setstate__(self, state):
        # Restore monitors
        self.__dict__.update(state)
        if self.use_monitors:
            self.connect_monitors()      
            
            
            
class Magnet(Device):
    """
    Magnet 
    
    """
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        
    
        # Full PV name dictionary. Keys will be attributes of this class
        self.PVname = {'bact': self.basePV+':BACT', 
                       'z': self.basePV+':Z',         
                       'madname': self.basePV+':MADNAME'}
    
        self.update()
  
     # String representation for printing:
    def __str__(self):
        s= self.type+' '+self.madname+' at z = '+str(self.z)+' and bact = '+str(self.bact)
        return s            
    
class BPM(Device):
    """
    BPM
    
    
    """
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        
        
        # Full PV name dictionary. Keys will be attributes of this class
        self.PVname = {'x': self.basePV+':X', 
                       'y': self.basePV+':Y',
                       'z': self.basePV+':Z',         
                       'madname': self.basePV+':MADN'}
        
        self.update()
        
     # String representation for printing:
    def __str__(self):
        s= self.type+' '+self.madname+' at z = '+str(self.z)+' and x = '+str(self.x)
        return s    
    
    
    
    
    