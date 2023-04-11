import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep

@dataclass
class Data:
    name: str
    pulse_duration: float
    freq_sampling: float
    samples: int
    time: np.ndarray
    TC: np.ndarray
    RISC: np.ndarray
    PT100: np.ndarray
    
    def __init__(self, obj, pulse_duration: float, ID=None):
        self.time, self.TC, self.RISC, self.PT100 = obj
        self.pulse_duration = pulse_duration
        self.freq_sampling = 1/(self.time[1]-self.time[0])
        self.samples = len(self.time)
        self.name = f'samples/freq./pulse dur.: \
{self.samples}/{self.freq_sampling:.1f}Hz/{self.pulse_duration:.1f}s'
        self.ID = ID
    
    def __str__(self):
        return f'{self.name}'

    def prelim_plot(self, xlimLo=None, xlimUp=None, cut=False):
        fig = plt.figure(figsize=(7,7))
        gs = fig.add_gridspec(5, 1)
        PT100ax = fig.add_subplot(gs[4])
        PT100ax.plot(self.time, self.PT100, 'r')
        PT100ax.set_xlabel('Time (s)')
        PT100ax.set_ylabel('PT100 (V)')
        RISCax = fig.add_subplot(gs[3], sharex=PT100ax)
        RISCax.plot(self.time, self.RISC, 'r')
        RISCax.set_ylabel('RISC (V)')
        RISCax.tick_params(labelbottom=False)
        TCax = fig.add_subplot(gs[0:3],sharex=PT100ax)
        TCax.plot(self.time, self.TC, 'r', label=self.name)
        TCax.set_ylabel('TC (V)')
        TCax.tick_params(labelbottom=False)
        TCax.legend()
        hep.label.exp_text('L3','Preliminary', ax=TCax)
        hep.label.lumitext(f'ID {self.ID}')
        if xlimUp is not None:
            loLim = xlimLo if xlimLo is not None else 0
            if cut:
                PT100ax.set_xlim(xlimLo, xlimUp)
            else:
                for ax in [PT100ax, RISCax, TCax]:
                    ax.axvspan(loLim, xlimUp, edgecolor='k', facecolor='gray')