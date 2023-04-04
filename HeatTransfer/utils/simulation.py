import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplhep as hep

from uncertainties import ufloat

from dataclasses import dataclass
from tqdm import tqdm

from .analysis_utils import AnalysisData

class Simulation:
    max_time: float
    time_samples: int
    time: np.ndarray
    
    bar_lenght: float
    bar_samples: int
    
    delta_lenght: float = 0
    delta_time: float = 0
    
    TC_data_array: np.ndarray
    
    D: float = 9.85e-5
    eta: float
    TC_position: float = 21e-3
    TC_position_idx: int
    
    simulated_data: AnalysisData
    
    ID = 'Fake data'
    name: str
    
    def __init__(self, max_time=50, time_samples: int=50_000, 
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
        self.max_time = max_time
        self.time_samples = time_samples
        self.time = np.linspace(0, max_time, time_samples)
        self.delta_time = self.time[1]-self.time[0]
        
        self.bar_samples = bar_samples
        self.bar_lenght = bar_lenght
        self.TC_data_array = np.linspace(0, bar_lenght, bar_samples)
        self.delta_lenght = self.TC_data_array[1]-self.TC_data_array[0]
        
        self.TC_position_idx = self.TC_position * self.bar_samples / self.bar_lenght
        
        self.eta = self.D * self.delta_time / self.delta_lenght**2
        if self.eta > 0.5: raise Warning(f'eta {self.eta}>0.5, simulation may diverge')
        
        self.name = f'samples/t. samples/t. freq./sim. time: \
{self.bar_samples}/{self.time_samples}/{1/self.delta_time:.1f}Hz/{self.max_time}s'
        
        self.simulated_data = AnalysisData(
            self.time,
            np.ones_like(self.time),
            np.zeros_like(self.time),
            0,
            self.name,
            self.ID
        )
    
    def __str__(self):
        return self.name
    
    def plot(self, time_limits: tuple = None):
        
        plt.figure()
        data = self.simulated_data
        
        TC = None
        if self.ID == 'Simulation':
            TC = self.simulated_data.T_TC
        else:
            TC = 1/np.sqrt(self.D * data.time) * np.exp(
                - self.TC_position**2 / (4 * self.D * data.time)
            )
        
        plt.plot(data.time, TC, label=self.name)
        plt.xlabel('Time (s)')
        if time_limits is not None:
            plt.xlim(*time_limits)
        plt.ylabel('Thermocouple Temperature (K)')
        hep.label.exp_text('L3 ', self.ID)
        plt.legend()
    
    def simulate(self):
        success = False ##> boolean return fake data to plot if fails
        '''Does simulation
        
        Return: ~utils.AnalysisData
            The simulated data package (T_PT100 channel is used as event control).
            Error is None (0)
        '''
        
        if success:
            self.ID = 'Simulation'

        return self.simulated_data
    
    
    