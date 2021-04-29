import dataclasses
import pandas as pd
import numpy as np
import json
import os

@dataclasses.dataclass
class TabularDataMap:
    """
    
    DataMap instantiated from a table (pd.Dataframe)

    Parameters
    ----------
    data :  pd.DataFrame
        Data to extract the mapping info
    pvname : str
        column name for pvname
    element : str
        column name for element        
    attribute : str
        column name for attribute         
    factor : str, optional
        column name for factor   
    offset : str, optional
        column name for offset  
        
    Attributes
    ----------
    pvlist : list[str]
        list of PV names needed for mapping
    
    Methods
    -------
    evaluate(pvdata) :
        Returns
        -------
        pd.Series
            enld : float
                energy gain in MeV
            phase : float
                phase in deg
            in_use : bool
    
    """
    data : pd.DataFrame
    
    # Columns to extract data from
    pvname : str 
    element : str 
    attribute: str = ''
    factor : str = ''
    offset : str = ''
        
    # Special formats
    bmad_format : str = '{element}[{attribute}] = {value}'
    tao_format  : str = 'set ele {element} {attribute} = {value}'
        
    @property
    def pvlist(self):
        return self.data[self.pvname].tolist()
        
    def evaluate(self, pvdata):
        """
        Extract values from pvdata
        """        
        vals = self.data[self.pvname].apply(pvdata.get)
        
        # Only set valid_val values
        valid_val = ~vals.isnull()        
        
        elements = self.data[self.element]
        
        if self.attribute:
            attributes = self.data[self.attribute]        
        else:
            attributes = np.full(len(vals), '')
    
        if self.factor:
            factors =  self.data[self.factor].fillna(1)
        else:
            factors = np.full(len(vals), 1)
            
        if self.offset:
            offsets = self.data[self.offset].fillna(0)
        else:
            offsets = np.zeros(len(vals))

        
        return elements, attributes, vals, factors, offsets, valid_val
        

    def output_str(self, element, attribute, value, factor, offset, valid_val, x_format):
        """
        Output formatted string, including additional factor and offset.
        """
        if not valid_val:
            return f'! Bad value for {element}[{attribute}]: {value}'
        
        val = str(value)
        
        if factor != 1:
            val = f'{factor} * {val}'
        if offset != 0:
            val += f' + {offset}'
        
        return x_format.format(element=element, attribute=attribute, value=val)
    
    def as_bmad(self, pvdata):
        """
        Return a list of strings to be read by Bmad's parser
        """
        result = self.evaluate(pvdata)
        
        f = lambda x: self.output_str( *x, self.bmad_format)
                
        lines = [f(x) for x in zip(*result)]

        return lines
    
    def as_tao(self, pvdata):
        """
        Return a list of strings to be read by Bmad's parser
        """
        result = self.evaluate(pvdata)
        
        f = lambda x: self.output_str( *x, self.tao_format)
                
        lines = [f(x) for x in zip(*result)]

        return lines    
    
    def to_json(self, file=None):
        """
        Returns a JSON string
        """
        d = {}
        for k, v in self.__dict__.items():
            if k == 'data':
                d[k] = v.to_json()
            else:
                d[k] = v
        s = json.dumps(d)
        
        if file:
            with open(file, 'w') as f:
                f.write(s)
        else:
            return s
    
    @classmethod
    def from_json(cls, s):
        """
        Creates a new TablularDataMap from a JSON string
        """
        if os.path.exists(s):
            d = json.load(open(s))
        else:
            d = json.loads(s)
        data = pd.read_json(d.pop('data'))
        return cls(data=data, **d)