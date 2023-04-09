from scipy import fft
import matplotlib.pyplot as plt
import numpy as np

from .data_handler import FFTData, AnalysisData, Data

from scipy import fft
def signal_fft(data: Data):
    
    fft_data = FFTData(data)
    
    fft_data.source = 2.0/fft_data.samples * np.abs(fft.fft(fft_data.source, n=fft_data.samples)[:fft_data.samples//2])
    fft_data.receiver_1 = 2.0/fft_data.samples * np.abs(fft.fft(fft_data.receiver_1, n=fft_data.samples)[:fft_data.samples//2])
    fft_data.receiver_2 = 2.0/fft_data.samples * np.abs(fft.fft(fft_data.receiver_2, n=fft_data.samples)[:fft_data.samples//2])
    
    fft_data.time_clock = fft.fftfreq(fft_data.samples, 1/fft_data.freq_sampling)[:fft_data.samples//2]
    
    return fft_data

def response_function(data: Data):
    
    sfft = signal_fft(data)
    freq = sfft.time_clock
    H1 = 10 * np.log10(sfft.receiver_1/sfft.source)
    H2 = 10 * np.log10(sfft.receiver_2/sfft.source)
    
    plt.figure()
    hep.label.exp_text('L3 ', 'Preliminary')
    hep.label.lumitext(f'({data.name})')
    plt.plot(freq, H1, label='$H_1$ Transfer function (rec. 1)')
    plt.plot(freq, H2, label='$H_2$ Transfer function (rec. 2)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain $10\cdot\log|H|$ (dB)')
    plt.xlim(0, np.max(freq))
    plt.legend()