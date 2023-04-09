import matplotlib.pyplot as plt
import mplhep as hep
from .data_handler import Data, FFTData

from .analysis import *

def initialize_plot():
    import mplhep as hep
    plt.style.use(['std-colors',hep.style.ATLAS])
    plt.rcParams['yaxis.labellocation'] = 'center'
    plt.rcParams['xaxis.labellocation'] = 'center'
    
    