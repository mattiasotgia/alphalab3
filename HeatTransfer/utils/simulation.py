import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from .analysis_utils import AnalysisData
from uncertainties import ufloat

from dataclasses import dataclass

from tqdm import tqdm



class Simulation:
    time: float
    time_samples: int
    bar_lenght: float
    bar_samples: int
    
    delta_lenght: float = 0
    delta_time: float = 0
    
    time_array: np.ndarray
    TC_data_array: np.ndarray
    
    D: float = 9.85e-5
    eta: float
    TC_position: float = 21e-3
    TC_position_index: int
    
    def __init__(self, time=50, time_samples: int=50_000, 
                 bar_lenght=63e-3, bar_samples=100, 
                 D=None):
        '''Simulation()
        Parameters:
            time: float, default to 70 (s)
                Set the maximum simulation time
            time_samples: int, default to 50_000
                Set time samples to generate
            bar_lenght: float, default to 63e-3
                Physical bar lenght
            bar_samples: int, default to 100
                Bar samples for simulation
            D: float, None, default to 9.85e-5 (if None)
                Heat diffusion coefficient D
                
        '''
        
        if D is not None: self.D = D
        self.time = time
        self.time_samples = time_samples
        self.bar_samples = bar_samples
        self.delta_time = self.time / time_samples
        self.delta_lenght = self.bar_lenght / bar_samples
        
        
        self.eta = self.D * self.delta_time / self.delta_lenght**2
        if self.eta > 0.5: raise Warning(f'eta {self.eta}>0.5, simulation may diverge')