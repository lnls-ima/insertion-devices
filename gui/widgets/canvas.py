
from PyQt6.QtWidgets import QWidget, QVBoxLayout

import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                                # matplotlib toolbar qt widget class
                                                NavigationToolbar2QT as NavigationToolbar)

class Canvas(QWidget):

    def __init__(self, dpi=100):
        super().__init__()

        self.fig, self.ax = plt.subplots(dpi=dpi)
        self.figure = FigureCanvas(self.fig)

        self.figure.mpl_connect('draw_event',self.on_draw)

        layout = QVBoxLayout()

        toolbar = NavigationToolbar(self.figure, self)

        layout.addWidget(toolbar)
        layout.addWidget(self.figure)

        self.setLayout(layout)
    
    def draw(self):
        self.figure.draw()
    
    def on_draw(self, event):
        self.fig.tight_layout()
