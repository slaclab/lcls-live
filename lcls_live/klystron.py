from .devices import Device

from math import pi, cos

class Klystron(Device):
    """
    Klystron
    
    """
    def __init__(self, name=None,
                sector=-1, station=-1,
                faults_callback=None, triggers_callback=None,
                epics=None, 
                verbose=False):
        
        if sector > -1 and station > -1:
            name = klystron_name(sector, station)
        else:
            sector, station = klystron_sector_station(name)    
        
        
        self.sector = sector
        self.station = station  
        self.name = klystron_name(sector, station)
        self.faults_callback = faults_callback
        self.triggers_callback = triggers_callback   
        super().__init__(name=self.name, epics=epics, verbose=verbose)
        
        # Full PV name dictionary. Keys will be attributes of this class
        self.PVname = {'enld':  klystron_enldPV(sector, station), 
                       'phase': klystron_phasePV(sector, station),         
                       'pdes': self.name+':PDES',              
                       'swrd': self.name+':SWRD',        
                       'stat':self.name+':STAT',
                       'hdsc':self.name+':HDSC', 
                       'dsta':self.name+':DSTA',
                       'acc_trigger_status':self.beamcodeStatPV(self.typicalBeamcode()) }
        
        self.update()


    def update(self):
        super().update()
        self.recalcFaults()    
            
    def is_accelerating(self):
        return self.acc_trigger_status == 1

    def has_faults(self):
        return len(self.faults) > 0
       
    # Monitors 
    def connect_monitors(self):
        for name in self.attributes:    
            self.connect_monitor(name)  
        
        self.update()    
        self.monitor['swrd'].add_callback(self.swrdCallback)
        self.monitor['stat'].add_callback(self.statCallback)
        self.monitor['hdsc'].add_callback(self.hdscCallback)
        self.monitor['dsta'].add_callback(self.dstaCallback)
        self.monitor['acc_trigger_status'].add_callback(self.triggersChanged)            
         
    def beamcodeStatPV(self, beamcode):
        return "{0}:BEAMCODE{1}_STAT".format(self.name, beamcode)
        
    def onbeamPV(self,beamcode):
        return "{0}:BEAMCODE{1}_TCTL".format(self.name, beamcode)  
    
    def typicalBeamcode(self):
        return typical_beam_code(self.sector, self.station)

    def correct_swrd(self):
        #Horrible hack to ignore the bit for 'low RF power' on LCLS front-end klystrons.
        if (self.sector == 20 and self.station == 7) or (self.sector == 21 and self.station == 1) or (self.sector == 21 and self.station == 2):
            self.swrd = int(self.swrd) & ~(1 << 5)
     
           
    #Define whether the station is available to be used
    def is_usable(self):
        #If there are none of the station's faults are in the unusable_faults list, return true.
        return set(self.faults).isdisjoint(unusable_faults)
    

    def deact(self, beamcode=None):
        return self.set_acc_triggers(0, beamcode=beamcode)
    
    def react(self, beamcode=None):
        return self.set_acc_triggers(1, beamcode=beamcode)                

    def triggersChanged(self, pvname=None, value=None, **kw):
        if value != self.acc_trigger_status:
            self.acc_trigger_status = value
            if self.triggers_callback:
                self.triggers_callback(self.sector, self.station, self.acc_trigger_status)
    def recalcFaults(self):
        self.faults = all_fault_strings(swrd=self.swrd, stat=self.stat, hdsc=self.hdsc, dsta=self.dsta)
        if self.faults_callback:
            self.faults_callback(self.sector, self.station, self.faults)

    # Set
    def set_acc_triggers(self, value, beamcode=None):
        if beamcode is None:
            beamcode = self.typicalBeamcode()
        return self.epics.caput(self.onbeamPV(beamcode), value) 
 
    # Callbacks 
    def swrdCallback(self, pvname=None, value=None, **kw):
        if value != self.swrd:
            self.swrd = value
            self.correct_swrd()
            self.recalcFaults()
        
    def statCallback(self, pvname=None, value=None, **kw):
        if value != self.stat:
            self.stat = value
            self.recalcFaults()
        
    def hdscCallback(self, pvname=None, value=None, **kw):
        if value != self.hdsc:
            self.hdsc = value
            self.recalcFaults()
        
    def dstaCallback(self, pvname=None, value=None, **kw):
        if not numpy.array_equal(value,self.dsta):
            self.dsta = value
            self.recalcFaults()
            
    # String representation for printing:
    def __str__(self):
        s= 'Klystron in sector '+str(self.sector)+', station '+str(self.station)
        if self.has_faults():
            s = s+', has faults'
        if not self.is_usable():
            s = s+', is NOT usable'
        if not self.is_accelerating():
            s = s+', is NOT accelerating'
    
        if self.is_usable() and self.is_accelerating():
            de = self.enld * cos(self.phase*pi/180)
            s += '\n   Approximate energy gain = '+str(self.enld) + '*cos('+str(self.phase)+'*pi/180) = '+ str(de)+' MeV'
                
        return s
    
def typical_beam_code(sector, station):
    if sector > 20:
        return 1
    if sector == 20 and station >= 5:
        return 1
    if sector >= 2:
        return 10
    if sector < 2:
        return 11         
        
        
           
def klystron_sector_station(name):
    """
    Decodes sector, station. Name should be of the form:
    KLYS:LI<sector>:<station>1
    
    (Note the extra 1)
    """
    x = name.split(':')
    assert x[0] == 'KLYS'
    
    sector = int(x[1].split('LI')[1])
    station = int(x[2][0])
    return sector, station                

# Sector, station dependent PV names
def klystron_name(sector, station):
    if station == 0:
        return "SBST:LI{0}:1".format(sector)
        
    return "KLYS:LI{0}:{1}1".format(sector, station)

def klystron_enldPV(sector, station):
    # L1 X-band special 
    if sector == 21 and station == 2:
        return 'ACCL:LI21:180:L1X_S_AV'
        
    return klystron_name(sector, station)+":ENLD"

def klystron_phasePV(sector, station):
    # L1 special
    if sector == 21 and station ==1:
        return 'ACCL:LI21:1:L1S_S_PV'

    # L1 X-band special 
    if sector == 21 and station == 2:
        return 'ACCL:LI21:180:L1X_S_PV'
        #enld =caget('ACCL:LI21:180:L1X_S_AV')     

    # L2 special 
    if sector == 24 and station ==1:
        return 'ACCL:LI24:100:KLY_PDES'
    if sector == 24 and station ==2:
        return 'ACCL:LI24:200:KLY_PDES'
    if sector == 24 and station ==3:
        return 'ACCL:LI24:300:KLY_PDES'

    # L3 special
    if sector == 29:
        return 'ACCL:LI29:0:KLY_PDES'  
    if sector == 30:
        return 'ACCL:LI30:0:KLY_PDES' 

    return klystron_name(sector, station)+":PHAS"

      
#Below is the module-level stuff for turning status words into faults.
#Each key is a bit position.  Each value is a (Fault Name, Priority) tuple.
swrd_fault_map = {
    0: ("Bad Cable Status", 55), 
    1: ("MKSU Protect", 80),
    2: ("No Triggers", 68),
    3: ("Modulator Fault", 67),
    5: ("Low RF Power", 80),
    6: ("Amplitude Mean", 70),
    7: ("Amplitude Jitter", 75),
    8: ("Lost Phase", 90),
    10: ("Phase Jitter", 75),
    14: ("No Sample Rate", 69)}
stat_fault_map = {
    1: ("Maintenance Mode", 10),
    2: ("Offline", 1),
    3: ("Out of Tolerance", 100),
    4: ("Bad CAMAC Status", 40),
    6: ("Dead Man Timeout", 50),
    7: ("Fox Phase Home Error", 57),
    9: ("Phase Mean", 75),
    12: ("IPL Required", 20),
    14: ("Update Required", 30)}
hdsc_fault_map = {
    2: ("To Be Replaced", 5),
    3: ("Awaiting Run Up", 5),
    6: ("Check Phase", 5)}
dsta1_fault_map = {
    2: ("SLED Motor Not At Limit", 65),
    3: ("SLED Upper Needle Fault", 65),
    4: ("SLED Lower Needle Fault",65),
    5: ("Electromagnet Current Out of Tolerance", 65),
    6: ("Klystron Temperature", 65),
    8: ("Reflected Energy", 65),
    9: ("Over Voltage", 65),
    10: ("Over Current", 65),
    11: ("PPYY Resync", 67),
    12: ("ADC Read Error", 50),
    13: ("ADC Out of Tolerance", 72),
    16: ("Water Summary Fault", 61),
    17: ("Acc Flowswitch #1", 60),
    18: ("Acc Flowswitch #2", 60),
    19: ("Waveguide Flowswitch #1", 60),
    20: ("Waveguide Flowswitch #2", 60),
    21: ("Klystron Water Flowswitch", 60),
    22: ("24 Volt Battery", 60),
    23: ("Waveguide Vacuum", 60),
    25: ("Klystron Vacuum", 60),
    26: ("Electromagnet Current", 60),
    27: ("Electromagnet Breaker", 60),
    28: ("MKSU Trigger Enable", 60)}
dsta2_fault_map = {
    4: ("EVOC", 65),
    6: ("End of Line Clipper", 65),
    7: ("Mod Trigger Overcurrent", 65),
    9: ("External Fault", 65),
    10: ("Fault Lockout", 65),
    11: ("HV Ready", 65),
    13: ("Klystron Heater Delay", 65),
    14: ("VVS Voltage", 65),
    15: ("Control Power", 65)}

unusable_faults = [
    'Bad Cable Status',
    'MKSU Protect',
    'Modulator Fault',
    'Maintenance Mode',
    'Offline',
    'To Be Replaced',
    'Awaiting Run Up',
    'Check Phase',
    'SLED Motor Not At Limit',
    'SLED Upper Needle Fault',
    'SLED Lower Needle Fault',
    'Water Summary Fault',
    'Acc Flowswitch #1',
    'Acc Flowswitch #2',
    'Waveguide Flowswitch #1',
    'Waveguide Flowswitch #2',
    'Klystron Water Flowswitch',
    '24 Volt Battery',
    'Waveguide Vacuum',
    'Klystron Vacuum',
    'Electromagnet Current',
    'Electromagnet Breaker',
    'MKSU Trigger Enable',
    'EVOC',
    'End of Line Clipper',
    'Mod Trigger Overcurrent',
    'External Fault',
    'Fault Lockout',
    'HV Ready',
    'Klystron Heater Delay',
    'VVS Voltage','Control Power']

#Input an integer, and you'll get a list of fault strings, ordered by priority.
def swrd_fault_strings(swrd):
    return strings_from_fault_tuple_list(swrd_faults(swrd))
    
def stat_fault_strings(stat):
    return strings_from_fault_tuple_list(stat_faults(stat))

def hdsc_fault_strings(hdsc):
    return strings_from_fault_tuple_list(hdsc_faults(hdsc))

def dsta_fault_strings(dsta):
    return strings_from_fault_tuple_list(dsta_faults(dsta))
    
def all_fault_strings(swrd=0, stat=0, hdsc=0, dsta=0):
    return strings_from_fault_tuple_list(all_faults(swrd=swrd, stat=stat, hdsc=hdsc, dsta=dsta))
    
def strings_from_fault_tuple_list(faults):
    return [fault[0] for fault in faults]

#Input an integer, and you'll get a list of tuples, ordered by priority (lower number = higher priority).
def swrd_faults(swrd):
    return list_faults(swrd_fault_map, swrd)
    
def stat_faults(stat):
    return list_faults(stat_fault_map, stat)

def hdsc_faults(hdsc):
    return list_faults(hdsc_fault_map, hdsc)

def dsta_faults(dsta):
    faults = list_faults(dsta1_fault_map, dsta[0])
    faults.extend(list_faults(dsta2_fault_map,dsta[1]))
    return faults

def all_faults(swrd=0, stat=0, hdsc=0, dsta=0):
    faults = swrd_faults(swrd)
    faults.extend(stat_faults(stat))
    faults.extend(hdsc_faults(hdsc))
    faults.extend(dsta_faults(dsta))
    faults.sort(key=lambda tup: tup[1])
    return faults

def list_faults(fault_map, word):
    faults = []
    for bit in fault_map:
        if testbit(word, bit):
            faults.append(fault_map[bit])
    faults.sort(key=lambda tup: tup[1])
    return faults

def testbit(word, offset):
    mask = 1 << offset
    return ((int(word) & mask) > 0)
    
#Make an LCLS complement dictionary
def lcls_complement():
    complement = {}
    complement[20] = {}
    for j in range(5,9):
        complement[20][j] = Klystron(20,j)
    for i in range(21,31):
        complement[i] = {}
        for j in range(1,9):
            if (i==24 and j==7) or (i==28 and j==2):
                continue
            complement[i][j] = Klystron(i,j)
    return complement






# List of all LCLS klystrons by sector, station    
existing_LCLS_klystrons_sector_station = (
                                                  # GUN, L0A, L0B
                                                 (20, 6), (20, 7), (20, 8),
    
    # L1S    L1X
    (21, 1), (21, 2),
    
    # L2
                      (21, 3), (21, 4), (21, 5), (21, 6), (21, 7), (21, 8), 
    (22, 1), (22, 2), (22, 3), (22, 4), (22, 5), (22, 6), (22, 7), (22, 8), 
    (23, 1), (23, 2), (23, 3), (23, 4), (23, 5), (23, 6), (23, 7), (23, 8),
    (24, 1), (24, 2), (24, 3), (24, 4), (24, 5), (24, 6),
    # L3
    (25, 1), (25, 2), (25, 3), (25, 4), (25, 5), (25, 6), (25, 7), (25, 8),
    (26, 1), (26, 2), (26, 3), (26, 4), (26, 5), (26, 6), (26, 7), (26, 8),
    (27, 1), (27, 2), (27, 3), (27, 4), (27, 5), (27, 6), (27, 7), (27, 8), 
    (28, 1), (28, 2), (28, 3), (28, 4), (28, 5), (28, 6), (28, 7), (28, 8), 
    (29, 1), (29, 2), (29, 3), (29, 4), (29, 5), (29, 6), (29, 7), (29, 8), 
    (30, 1), (30, 2), (30, 3), (30, 4), (30, 5), (30, 6), (30, 7), (30, 8))

# Convert these to device names
existing_LCLS_klystron_names = [klystron_name(x[0], x[1]) for x in existing_LCLS_klystrons_sector_station]

# Function to create list of objects
def existing_LCLS_klystrons(epics, skip=3): # skip GUN, L0A, L0B
    
    klist = [Klystron(name=devicename, epics=epics) for devicename in existing_LCLS_klystron_names[skip:]]
    return klist






