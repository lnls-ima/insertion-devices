
from PyQt6.QtWidgets import QWidget, QVBoxLayout

import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                                # matplotlib toolbar qt widget class
                                                NavigationToolbar2QT as NavigationToolbar)

class Canvas(FigureCanvas):
    def __init__(self, dpi=100):
        self.fig, self.ax = plt.subplots(dpi=dpi)
        super().__init__(self.fig)


class Grafico(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.chart = Canvas()
        self.chart.fig.tight_layout()
        self.chart.mpl_connect('draw_event',self.on_draw)

        toolbar = NavigationToolbar(self.chart, self)

        layout.addWidget(toolbar)
        layout.addWidget(self.chart)

        self.setLayout(layout)
    


    def on_draw(self, event):
        self.chart.fig.tight_layout()

    def Plot(self,x,y):
        self.chart.ax.plot(x,y)

        self.chart.fig.tight_layout()
    
    def plotStuff(self,title: str, xlabel: str, ylabel: str):
        self.chart.ax.set_title(title)
        self.chart.ax.set_xlabel(xlabel)
        self.chart.ax.set_ylabel(ylabel)

        self.chart.fig.tight_layout()
