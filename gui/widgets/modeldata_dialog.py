
import os
from PyQt6.QtWidgets import QDialog, QFileDialog

from .dialog_layouts import	ModelDataLayout

import numpy as np

class ModelDataDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Model to Data")

        self.layoutModelData = ModelDataLayout(self)

        self.setMinimumWidth(282)

        self.layoutModelData.buttonBox.accepted.connect(self.accept)
        self.layoutModelData.buttonBox.rejected.connect(self.reject)

    @classmethod
    def getDataGrid(cls, parent=None):

        dialog = cls(parent)
        #dialog.setMinimumWidth(dialog.width()*2)
        answer = dialog.exec()

        if answer == QDialog.DialogCode.Accepted:

            coords_range = []
            for i in [0,1,2]:
                start = dialog.layoutModelData.spins_start[i].value()
                end = dialog.layoutModelData.spins_end[i].value()
                step = dialog.layoutModelData.spins_step[i].value()
                if i==1 and start==end:
                    i_range = [start]
                else:
                    i_range = np.arange(start,end+step,step)
                coords_range.append(i_range)

            return coords_range
        
        if answer == QDialog.DialogCode.Rejected:
            return []

