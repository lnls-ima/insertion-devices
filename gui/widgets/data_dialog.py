
import os

from PyQt6.QtWidgets import (QDialog,
                             QFileDialog,
                             QMessageBox)

from imaids.insertiondevice import InsertionDeviceData
from .dialog_layouts import DataLayout
from . import (models_parameters, getUndulatorName,
               getUndulatorPhase, isUndulatorCorrected)

class DataDialog(QDialog):

    def __init__(self, filenames=[] ,parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)

        self.setWindowTitle("Data Manager")

        self.spins_nr_periods = []
        self.spins_period_length = []
        self.spins_gap = []
        self.checks_correction = []
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
        IDs_params = []
        for (line_name,
             new_file,
             spin_nr_periods,
             spin_period_length,
             spin_gap,
             check_correction) in zip(self.lines_names,
                                      self.newfiles,
                                      self.spins_nr_periods,
                                      self.spins_period_length,
                                      self.spins_gap,
                                      self.checks_correction):
            
            IDs_params.append([line_name.text(),
                               new_file,
                               spin_nr_periods.value(),
                               spin_period_length.value(),
                               spin_gap.value(),
                               check_correction.isChecked()])
        return IDs_params
    
    @classmethod
    def getOpenFileIDs(cls, files=[] ,parent=None):
        
        dialog = cls(files, parent)
        answer = dialog.exec()
        
        if answer == QDialog.DialogCode.Accepted:
            
            IDs_params = []
            files_fail = []
            for name, *args, correct in dialog.loadedFilesParameters():
                filename, nr_periods, period_length, gap = args
                try:
                    ID = InsertionDeviceData(nr_periods=nr_periods,
                                             period_length=period_length,
                                             gap=gap,
                                             filename=filename)
                    IDs_params.append([ID,filename,name,correct])
                except:
                    files_fail.append(os.path.basename(filename))
            if files_fail:
                QMessageBox.critical(dialog,
                                     "Insertion Device Fail",
                                     f"Incompatible format in files loaded! They are:\n{files_fail}")

            return IDs_params
        
        if answer == QDialog.DialogCode.Rejected:
            return []


    # SLOTS

    def accept(self) -> None:
        
        invalid_spin = 0 in [spin.value() for spin in self.spins_nr_periods] + \
                            [spin.value() for spin in self.spins_period_length] + \
                            [spin.value() for spin in self.spins_gap]
        invalid_line = True in [line.text()=="" or line.text().isspace()
                                    for line in self.lines_names]

        if invalid_spin:
            QMessageBox.critical(self,
                                 "Critical Warning",
                                 "All spin boxes must have values greater than 0!")
        elif invalid_line:
            QMessageBox.critical(self,
                                 "Critical Warning",
                                 "All data must have a label name!")
        else:
            return super().accept()

    def browse(self):

        # files: file adress + file name of the selected data files
        files, _ = QFileDialog.getOpenFileNames(parent=self, 
                                                caption='Open data',
                                                directory=self.parent().lastpath,
                                                filter="Data files (*.txt *.dat *.csv)")
        if files:
            self.parent().lastpath = os.path.dirname(files[-1])
        
        loaded_files = self.check_files(files=files)

        self.add_files(loaded_files)

    def add_files(self, loaded_files):
        
        #todo: criar maneira de poder excluir uma linha depois de importa-la
        nr_oldfiles = len(self.oldfiles)
        # name_fmt = "{0} Phase {1}{2}"
        # names_oldfiles = [self.getUndulatorName(oldfile)+\
        #                   f"Phase {self.getUndulatorPhase(oldfile)}"+
        #                   self.getUndulatorCorrection(oldfile)
        #                   for oldfile in self.oldfiles]
        rows = self.layoutData.gridFiles.rowCount()

        for i, file in enumerate(loaded_files):

            filename = os.path.basename(file)
            (line_name, spin_nr_periods,
             spin_period_length, spin_gap,
             check_correction) = self.layoutData.insertAfterRow(filename, i+rows)

            line_name.textChanged.connect(self.resize_to_content)
  
            und_name = getUndulatorName(filename)
            und_phase = getUndulatorPhase(filename)
            und_correct = isUndulatorCorrected(filename)
            
            if und_name!="":
                line_name.setText(f"{und_name} Phase {und_phase}")
            else:
                line_name.setText(f"Data {(rows-2)+nr_oldfiles+i+1}")
            self.lines_names.append(line_name)

            if und_name in models_parameters:
                spin_nr_periods.setValue(models_parameters[und_name]["nr_periods"])
                spin_period_length.setValue(models_parameters[und_name]["period_length"])
                spin_gap.setValue(models_parameters[und_name]["gap"])
                check_correction.setChecked(und_correct)

            spin_nr_periods.valueChanged.connect(self.spin_all)
            spin_period_length.valueChanged.connect(self.spin_all)
            spin_gap.valueChanged.connect(self.spin_all)

            self.spins_nr_periods.append(spin_nr_periods)
            self.spins_period_length.append(spin_period_length)
            self.spins_gap.append(spin_gap)
            self.checks_correction.append(check_correction)
    
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
            elif spinbox in self.spins_nr_periods:
                for spin in self.spins_nr_periods:
                    if spin != spinbox:
                        # bloquear sinal, pois setValue emit valueChanged
                        spin.blockSignals(True)
                        spin.setValue(value)
                        spin.blockSignals(False)
            else:
                for spin in self.spins_gap:
                    if spin != spinbox:
                        # bloquear sinal, pois setValue emit valueChanged
                        spin.blockSignals(True)
                        spin.setValue(value)
                        spin.blockSignals(False)
            return
        else:
            return
