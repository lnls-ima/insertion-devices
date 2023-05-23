
import os
import json

from PyQt6.QtWidgets import (QDialog,
                             QFileDialog,
                             QMessageBox)

from imaids.insertiondevice import InsertionDeviceData
from .dialog_layouts import DataLayout

class DataDialog(QDialog):

    filename = 'models_parameters.json'

    # Get the current directory
    current_dir = os.getcwd()
    # Iterate over all the files in the directory tree
    for root, dirs, files in os.walk(current_dir):
        # Check if the file we're looking for is in the list of files
        if filename in files:
            # If it is, print the full path to the file
            filename = os.path.join(root, filename)
            break
    
    with open(filename) as f:
        parameters = json.load(f)

    def __init__(self, filenames=[] ,parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)

        self.setWindowTitle("Data Manager")

        self.spins_nr_periods = []
        self.spins_period_length = []
        #arquivos ja presentes no project
        self.oldfiles = filenames
        #novos arquivos
        self.newfiles = []
        self.lines_names = []

        self.layoutData = DataLayout(parent=self)

        self.layoutData.button_browse.clicked.connect(self.browse)
        ## dialog button box - signals
        self.layoutData.buttonBox.accepted.connect(self.accept)
        self.layoutData.buttonBox.rejected.connect(self.reject)

        #todo: impedir que o dialog seja esticavel para baixo
        #self.setFixedHeight(self.minimumSizeHint().height())



    # FUNCTIONS

    def getSpinsValues(self, spin_list):
        return [spin.value() for spin in spin_list]
    
    def check_files(self, files):

        reloaded_files = []
        loaded_files = []
        for file in files:
            if file in self.oldfiles+self.newfiles:
                # arquivo carregado novamente
                filename = os.path.basename(file)
                reloaded_files.append(filename)
            else:
                # arquivo carregado
                loaded_files.append(file)
                self.newfiles.append(file)

        # alertando sobre os arquivos ja carregados
        if reloaded_files:
            QMessageBox.warning(self,
                                "Files Warning",
                                f"Files already loaded! They are:\n{reloaded_files}")
            
        return loaded_files

    def loadedFilesParameters(self):
        return [self.getSpinsValues(self.spins_nr_periods),
                self.getSpinsValues(self.spins_period_length),
                self.newfiles,
                self.lines_names]
    
    def getUndulatorName(self,filename):
        models = list(self.parameters.keys())
        
        acertos = []
        possible_names = ["Delta","Prototype","Sabia"]
        
        for modelname in possible_names+models:
            if modelname in filename:
                acertos.append(modelname)
        if acertos:
            return acertos[-1]
        else:
            return ""
    
    def getUndulatorPhase(self, filename):
        phase_idx = filename.find("Phase")
        if phase_idx!=-1:
            phase = filename[phase_idx:].lstrip("Phase")[:3]
            phase = "".join([char for char in list(phase) if char.isdigit()])
            return phase
        else:
            return "N"
        
    @classmethod
    def getOpenFileIDs(cls, files=[] ,parent=None):
        
        dialog = cls(files, parent)
        answer = dialog.exec()
        
        if answer == QDialog.DialogCode.Accepted:
            
            *parameters, name_lines = dialog.loadedFilesParameters()
            
            ID_list = []
            file_list = []
            for nr_periods, period_length, filename in zip(*parameters):
                ID = InsertionDeviceData(nr_periods=nr_periods, period_length=period_length,filename=filename)
                ID_list.append(ID)
                file_list.append(filename)

            name_list = [line.text() for line in name_lines]

            return ID_list, file_list, name_list
        
        if answer == QDialog.DialogCode.Rejected:
            return [], [], []


    # SLOTS

    def accept(self) -> None:
       
        if 0 in self.getSpinsValues(self.spins_nr_periods)+self.getSpinsValues(self.spins_period_length):
            QMessageBox.critical(self,
                                 "Critical Warning",
                                 "All spin boxes must have values greater than 0!")
        else:
      
            return super().accept()

    def browse(self):

        userhome = os.path.expanduser('~')
        # filenames: file adress + file name of the selected data files
        files, _ = QFileDialog.getOpenFileNames(parent=self, 
                                                caption='Open data',
                                                directory=f"{userhome}\\Documents",
                                                filter="Data files (*.txt *.dat *.csv)")
        
        loaded_files = self.check_files(files=files)
        
        #todo: criar maneira de poder excluir uma linha depois de importa-la
        nr_oldfiles = len(self.oldfiles)
        rows = self.layoutData.gridFiles.rowCount()

        for i, file in enumerate(loaded_files):

            filename = os.path.basename(file)
            line_name, spin_nr_periods, spin_period_length = self.layoutData.gridFiles_insertAfterRow(filename, i+rows)

            line_name.textChanged.connect(self.resize_to_content)
            und_name = self.getUndulatorName(filename)
            und_phase = self.getUndulatorPhase(filename)
            if und_name!="":
                line_name.setText(f"{und_name} Phase {und_phase}")
            else:
                line_name.setText(f"Data {(rows-2)+nr_oldfiles+i+1}")
            self.lines_names.append(line_name)

            if und_name in self.parameters:
                spin_nr_periods.setValue(self.parameters[und_name]["nr_periods"])
                spin_period_length.setValue(self.parameters[und_name]["period_length"])
            spin_nr_periods.valueChanged.connect(self.spin_all)
            self.spins_nr_periods.append(spin_nr_periods)

            spin_period_length.valueChanged.connect(self.spin_all)
            self.spins_period_length.append(spin_period_length)
    
    def resize_to_content(self):
        lineedit = self.sender()
        lineedit.setMinimumWidth(10+lineedit.fontMetrics().boundingRect(lineedit.text()).width())

    def spin_all(self, value):

        # realizar o spin all somente quando a checkbox estiver marcada
        if self.layoutData.checkbox_valuesforall.isChecked():
        
            # QObject which the signal was sent
            spinbox = self.sender()
            
            # se a spin box e' de period length
            if spinbox in self.spins_period_length:
                for spin in self.spins_period_length:
                    if spin != spinbox:
                        spin.blockSignals(True)
                        spin.setValue(value)
                        spin.blockSignals(False)
            # se a spin box e' de number of periods
            else:
                for spin in self.spins_nr_periods:
                    if spin != spinbox:
                        # bloquear sinal, pois setValue emit valueChanged
                        spin.blockSignals(True)
                        spin.setValue(value)
                        spin.blockSignals(False)
            return
        else:
            return
