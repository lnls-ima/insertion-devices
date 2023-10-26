from PyQt6.QtWidgets import QDialog

from .dialog_layouts import OperationAnalysisLayout

class OperationAnalysisDialog(QDialog):
    def __init__(self, analysis_info, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Check results")

        analysis = analysis_info["analysis"]
        analysis_keys = analysis_info["analysis_dict"].keys()

        self.layoutOpAnalysis = OperationAnalysisLayout(analysis,analysis_keys,self)

        self.layoutOpAnalysis.buttonBox.accepted.connect(self.accept)
        self.layoutOpAnalysis.buttonBox.rejected.connect(self.reject)

    @classmethod
    def getResultsUnchanged(cls, analysis_info, parent=None):

        dialog = cls(analysis_info, parent)
        answer = dialog.exec()

        if answer == QDialog.DialogCode.Accepted:
            isUnchanged_dict = {check.text():check.isChecked()
                           for check in dialog.layoutOpAnalysis.checkboxes}
            return True, isUnchanged_dict
            
        else:
            return False, {}