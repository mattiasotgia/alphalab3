import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt

@dataclass
class MetaData:

    name: str = None
    
    distance: float = None
    freq_sampling: float = None
    samples: int = None
    
    
    time_clock: np.ndarray = None
    source: np.ndarray = None
    receiver_1: np.ndarray = None
    receiver_2: np.ndarray = None
    
    __xlabel: str = None
    __ylabel: str = None
        
    def __str__(self):
        return self.name
    
    def __getitem__(self, key):
        return self.time_clock[key], self.source[key], self.receiver_1[key], self.receiver_2[key]
    
    def plot(self, tmin: float = None, tmax: float = None, cut = False):
        
        fig, (SRCax, RC1ax, RC2ax) = plt.subplots(3,1,figsize=(7,7), sharex=True)
        
        time = self.time_clock
        SRC = self.source
        RC1 = self.receiver_1
        RC2 = self.receiver_2
        
        SRCax.plot(time, SRC)
        RC1ax.plot(time, RC1)
        RC2ax.plot(time, RC2)
        SRCax.set_ylabel(f'{self.__ylabel} source')
        RC1ax.set_ylabel(f'{self.__ylabel} rec. 1')
        RC2ax.set_ylabel(f'{self.__ylabel} rec. 2')
        RC2ax.set_xlabel(self.__xlabel)
        
        if tmax is not None:
            tmin = tmin if tmin is not None else 0
            if cut:
                SRCax.set_xlim(tmin, tmax)
            else:
                for ax in [SRCax, RC1ax, RC2ax]:
                    ax.axvspan(tmin, tmax, edgecolor='k', facecolor='gray')
        
        
    
class Data(MetaData):
    '''Wrapper for data for SoundSpeed L3 analysis
    '''
    
    def __init__(self, filename: str):
        
        self.distance = 0.01 * float(filename.split('/')[1].split('cm_')[0])
        
        time, amp, m1, m2 = np.loadtxt(filename, skiprows=23, unpack=True)
        self.time_clock = time
        self.source = amp
        self.receiver_1 = m1
        self.receiver_2 = m2
        
        self.freq_sampling = 1/(time[1]-time[0])
        self.samples = len(time)
        
        self._MetaData__xlabel = 'Time (s)'
        self._MetaData__ylabel = 'Amplitude '
        
        self.name = f'samples/freq./time/distance: {self.samples}/{self.freq_sampling:.0f}Hz/{np.max(time):.3f}s/{self.distance:.2f}m'
        
class FFTData(MetaData):
    
    def __init__(self, data: Data):
        self.distance = data.distance
        self.source = data.source
        self.receiver_1 = data.receiver_1
        self.receiver_2 = data.receiver_2
        self.name = data.name
        self.time_clock = data.time_clock
        self.samples = data.samples
        self.freq_sampling = data.freq_sampling
        
        self._MetaData__ylabel = 'FFT '
        self._MetaData__xlabel = 'Frequency (Hz)'
        
class AnalysisData(MetaData):
    
    def __init__(self, data: Data):
        self.distance = data.distance
        self.source = data.source
        self.receiver_1 = data.receiver_1
        self.receiver_2 = data.receiver_2
        self.name = data.name
        self.time_clock = data.time_clock
        self.samples = data.samples
        self.freq_sampling = data.freq_sampling
        
        self._MetaData__xlabel = 'Time (s)'
        self._MetaData__ylabel = 'Amplitude '