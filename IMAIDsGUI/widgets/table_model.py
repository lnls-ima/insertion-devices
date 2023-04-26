
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QAbstractTableModel
import numpy as np


class TableModel(QAbstractTableModel):

    def __init__(self, filename):
        super(TableModel, self).__init__()

        with open(filename, 'r') as f:
            self._header = f.readline().split()
            
        self._data = np.loadtxt(filename, skiprows=2)


    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data[index.row(), index.column()]
            return str(value)
        
        if role == Qt.ItemDataRole.BackgroundRole:
            color = [206,171, 71, int(0.3*255)]
            return QColor.fromRgb(*color)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:

            if orientation == Qt.Orientation.Horizontal:
                return self._header[section]

            if orientation == Qt.Orientation.Vertical:
                return range(1, self._data.shape[0]+1)[section]
        
        if role==Qt.ItemDataRole.ForegroundRole:
            if orientation == Qt.Orientation.Vertical:
                return QColor.fromRgb(255, 255, 255)

