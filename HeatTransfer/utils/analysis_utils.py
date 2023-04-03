import numpy as np
from dataclasses import dataclass
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplhep as hep

from iminuit import Minuit
from iminuit.cost import LeastSquares

from scipy import stats
from uncertainties import ufloat

from .data_utils import Data

@dataclass
class AnalysisData():
    time: np.ndarray
    T_TC: np.ndarray
    T_PT100: np.ndarray
    error_TC: float
    ID: int
    
    def __init__(self, time, T_TC, T_PT100, error_TC, name, ID = None):
        self.time = time
        self.T_TC = T_TC
        self.T_PT100 = T_PT100
        self.error_TC = error_TC
        self.name = name
        self.ID = ID


def print_results(value, error, M, data):
    print(f'┌─────────────────────────────────────────────────────────────────────────\
    \n│ D = {ufloat(value, error):.uS} m^2/s \tfor {data.name} (D{data.ID})\
    \n│ (p-value: {1 - stats.chi2.cdf(M.fmin.fval, M.ndof)}, χ2/df = {M.fval, M.ndof})\n')
        
class Analysis():
    bar_lenght: float = 63e-3
    TC_position: float = 21e-3
    TC_conversion = 1/41e-6
    error: float = 0
    data = None
    
    ## Miscellanea plot styling
    markersize = 2
    
    ###############################################
    def __init__(self, data: Data, cut: float = 5):
        self.gain = 2000
        
        def PT100_temp(data):
            i_pt100 = 1/1100 ###> R_eq \simeq 1k + 0.1k
            return 14e-4 * (data.PT100 / i_pt100)**2 + 2.2959 * data.PT100 / i_pt100 + 29.77
    
        def TC_temp(data):
            return (data.TC / self.gain) * self.TC_conversion
        
        T_TC = TC_temp(data)
        T_PT100 = PT100_temp(data)
        
        self.offset = np.mean(
            np.extract(
                data.time < cut,
                T_TC
            )
        )
        error = np.std(
            np.extract(
                data.time < cut,
                T_TC
            )
        )
        
        T_TC = - (T_TC - self.offset) ##> Correzione: senso fisico mancante
        
        self.data = AnalysisData(data.time, T_TC, T_PT100, error, data.name, data.ID)

    
    def filter(self, min_time: float = 0, max_time: float = 120):
        data = self.data
        if min_time < np.min(data.time):
            raise ValueError(f'{min_time = } is out of bounds')
        if max_time > np.max(data.time):
            raise ValueError(f'{max_time = } is out of bounds')
        
        low_index = np.where(data.time == min_time)[0][0]
        hi_index = np.where(data.time == max_time)[0][0]
        
        self.data = AnalysisData(
            data.time[low_index:hi_index],
            data.T_TC[low_index:hi_index],
            data.T_PT100[low_index:hi_index],
            data.error_TC,
            data.name,
            data.ID
        )
        
        return self
    

    def plot_linearized(self):
        
        inverted_time = 1/self.data.time
        linearized_temperature = np.log(self.data.T_TC * np.sqrt(self.data.time))
        signal_error = 1/self.data.T_TC * self.data.error_TC
        
        plt.errorbar(inverted_time, linearized_temperature, signal_error, None, 'ko', 
                     markersize=self.markersize, 
                     # label=f'(TC) {self.data.name}'
                    )
        plt.xlabel(r'$1/t$ (s$^{-1}$)')
        plt.ylabel(r'$\log(\sqrt{t}\cdot T_\mathrm{TC})$')
        
        return inverted_time, linearized_temperature, signal_error
    
    def linearized_model_fit(self, coefficient: float=1, offset: float=0):
        
        def model(x, α, β):
            return x * α + β
        
        x, y, signal_error = self.plot_linearized()
        
        LSmodel = LeastSquares(x, y, signal_error, model)
        M1 = Minuit(LSmodel, α=coefficient, β=offset)
        M1.migrad()
        D = - self.TC_position**2 / (4 * M1.values['α'])
        err_D = self.TC_position**2 / (4 * M1.values['α']**2) * M1.errors['α']
        
        print_results(D, err_D, M1, self.data)
        
        plt.plot(x, model(x, *M1.values), 
                 label=f'D$_{{({self.data.ID})}}$ = ${ufloat(D, err_D):.uSL}$ m$^2$/s')
        
        return D, err_D, M1
    
    def plot_temp(self, which: str='TC'):

        data = self.data
        temp = None
        if which == 'TC': 
            temp = data.T_TC
        elif which == 'PT100': 
            temp = data.T_PT100
        else: raise Exception('which in [TC, PT100]')
        
        plt.figure()
        plt.plot(data.time, temp, label=f'({which}) {data.name}')
        plt.xlabel('Time (s)')
        plt.ylabel(f'Temperature$-{ufloat(self.offset, self.data.error_TC):.uS}$ (K)')
        hep.label.exp_text('L3 ','Analysis')
    
    def full_model_fit(self, fit_limits = (5, 30), 
                       D: float = 1e-6, C: float = 50, 
                       offset: float = 0):
        
        def model(t, D, C, offset):
            model = C/np.sqrt(D * t) * np.exp(- self.TC_position**2 / (4 * D * t)) + offset
            t0 = self.data.time[0]
            idx_tfn = np.where(self.data.time == t0 + 3)[0][0]
            pulse = np.zeros(idx_tfn)
            index = len(pulse)//3
            pulse[index::-index] += 1
            # return np.convolve(model, pulse, 'same')
            return model
        
        
        time = self.data.time
        T = self.data.T_TC
        σ_T = self.data.error_TC
        plt.errorbar(time, T, σ_T, None, 'ko', 
                     markersize=self.markersize, 
                     # label=f'(TC) {self.data.name}'
                    )
        plt.xlabel('Time (s)')
        plt.ylabel('Temperature (K)')
        
        filtered = self.filter(*fit_limits)
        t_fit = filtered.data.time
        T_fit = filtered.data.T_TC
        
        LSmodel = LeastSquares(t_fit, T_fit, σ_T, model)
        M1 = Minuit(LSmodel, D=D, C=C, offset=offset)
        M1.migrad()
        D, err_D = M1.values['D'], M1.errors['D']
        
        print_results(D, err_D, M1, self.data)
        
        plt.plot(t_fit, model(t_fit, *M1.values), zorder=100, 
                 label=f'D$_{{({self.data.ID})}}$ = ${ufloat(D, err_D):.uSL}$ m$^2$/s')
        
        return D, err_D, M1
        