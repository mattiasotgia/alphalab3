from .style import STYLE

import matplotlib as mpl
import matplotlib.pyplot as plt

def make_style():
    plt.style.use(['std-colors', STYLE])