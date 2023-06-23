
import os
from PyQt6.QtWidgets import QDialog, QFileDialog

from .dialog_layouts import	SaveLayout

import numpy as np

class SaveDialog(QDialog):
    def __init__(self, file, parent=None):
        super().__init__(parent)

        self.file = file

        

        self.setWindowTitle("Save Field Map")

        self.layoutSave = SaveLayout(file, self)

        self.setMinimumWidth(self.layoutSave.lineName.width()*0.43)

        self.layoutSave.buttonBrowseDest.clicked.connect(lambda checked: self.saveAs(file))
        self.layoutSave.buttonBox.accepted.connect(self.accept)
        self.layoutSave.buttonBox.rejected.connect(self.reject)

    
    def saveAs(self, file):

        file_path, _ = QFileDialog.getSaveFileName(parent=self,
                                                   caption='Save Field Map',
                                                   directory=file,
                                                   filter="Data files (*.dat *.csv *.txt)")
        
        if file_path:
            filename = os.path.basename(file_path)
            filedir = os.path.dirname(file_path)
            self.layoutSave.lineName.setText(filename)
            self.layoutSave.lineDir.setText(filedir)

    @classmethod
    def getSaveData(cls, file, parent=None):

        dialog = cls(file, parent)
        dialog.setMinimumWidth(dialog.width()*2)
        answer = dialog.exec()

        if answer == QDialog.DialogCode.Accepted:

            filedir = dialog.layoutSave.lineDir.text()
            filename = dialog.layoutSave.lineName.text()
            file_path = os.path.join(filedir,filename)

            coords_range = []
            for i in [0,1,2]:
                start = dialog.layoutSave.spins_start[i].value()
                end = dialog.layoutSave.spins_end[i].value()
                step = dialog.layoutSave.spins_step[i].value()
                if i==1 and start==end:
                    i_range = [start]
                else:
                    i_range = np.arange(start,end+step,step)
                coords_range.append(i_range)
            saveForSpectra = dialog.layoutSave.comboFormats.currentText()=="Spectra"

            return file_path, coords_range, saveForSpectra
        
        if answer == QDialog.DialogCode.Rejected:
            return "", [], False

