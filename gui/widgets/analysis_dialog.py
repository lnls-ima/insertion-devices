
from PyQt6.QtWidgets import QDialog

from .dialog_layouts import AnalysisLayout

class AnalysisDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Analysis Parameters")

        self.layoutAnalysis = AnalysisLayout(parent=self)

        # signals
        ## signal sent from Ok button to the handler accept of QDialog class
        self.layoutAnalysis.buttonBox.accepted.connect(self.accept)
        ## signal sent from Ok button to the handler reject of QDialog class
        self.layoutAnalysis.buttonBox.rejected.connect(self.reject)


    # def analysis_chose(self, index):
    #     if index==1:

        