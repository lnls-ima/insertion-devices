
import os
import json

from PyQt6.QtWidgets import (QVBoxLayout,
                             QHBoxLayout,
                             QGridLayout,
                             QLineEdit,
                             QLabel,
                             QDoubleSpinBox,
                             QCheckBox,
                             QDialog,
                             QDialogButtonBox,
                             QFileDialog,
                             QToolButton,
                             QSpinBox,
                             QMessageBox)
from PyQt6.QtCore import Qt

from imaids.insertiondevice import InsertionDeviceData

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

        self.vbox = QVBoxLayout()

        self.grid = QGridLayout()

        label_browse = QLabel("Browse for Data")
        label_files = QLabel("Files")
        label_files.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label_files.setStyleSheet("font-weight: bold")
        label_names = QLabel("Names")
        label_names.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label_names.setStyleSheet("font-weight: bold")
        label_nr_periods = QLabel("Number of Periods")
        label_nr_periods.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label_nr_periods.setStyleSheet("font-weight: bold")
        label_period_length = QLabel("Period Length")
        label_period_length.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label_period_length.setStyleSheet("font-weight: bold")
        
        button_browse = QToolButton()
        button_browse.setText("...")
        #button_browse.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        button_browse.clicked.connect(self.browse)

        self.checkbox_valuesforall = QCheckBox("Use period values change for all")
        self.checkbox_valuesforall.setChecked(True)
        

        hbox_browse = QHBoxLayout()
        hbox_browse.addWidget(label_browse)
        hbox_browse.addWidget(button_browse)

        self.grid.addLayout(hbox_browse,0,0,Qt.AlignmentFlag.AlignLeft)
        self.grid.addWidget(self.checkbox_valuesforall,0,2,1,2)
        self.grid.addWidget(label_files,1,0)
        self.grid.addWidget(label_names,1,1)
        self.grid.addWidget(label_nr_periods,1,2)
        self.grid.addWidget(label_period_length,1,3)

        ## dialog button box - buttons
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        # dialog button box
        self.buttonBox = QDialogButtonBox(buttons)
        ## dialog button box - signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.vbox.addLayout(self.grid)
        self.vbox.addWidget(self.buttonBox)

        self.setLayout(self.vbox)

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
        Nchars = len(filename)
        models = self.parameters.keys()
        
        acertos = []
        #variar tamanhos de pedacos da string de filename
        #percorrendo ao contrario para nao pegar trechos pequenos, sem sentido, dos models names
        for strlen in range(15,4-1,-1):
            #percorrer o filename e tirando pedacoes de tamanho strlen e procurando se ha models com esse texto
            for i in range(Nchars-strlen+1):
                teste = filename[i:i+strlen]
                #print('teste:',teste)
                if teste in models:
                    acertos.append(teste)
                    break
                for model in models:
                    if teste in model:
                        #print('houve acerto')
                        acertos.append(teste)
            else:
                continue
            break
        #print('acertos:',acertos)
        return acertos[-1]
    
    def getUndulatorPhase(self, filename):
        phase_idx = filename.find("Phase")
        phase = filename[phase_idx:].lstrip("Phase")[:2]
        return phase
        
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
        rows = self.grid.rowCount()


        for i, file in enumerate(loaded_files):

            filename = os.path.basename(file)
            label_file = QLabel(filename)

            line_name = QLineEdit()
            line_name.textChanged.connect(self.resize_to_content)
            #todo: mudar name e phase para um padrao caso nao encontre nada no filename
            und_name = self.getUndulatorName(filename)
            und_phase = self.getUndulatorPhase(filename)
            #line_name.setText(f"Data {(rows-2)+nr_oldfiles+i+1}")
            line_name.setText(f"Data {und_name} Phase {und_phase}")
            self.lines_names.append(line_name)
            
            spin_nr_periods = QSpinBox()
            spin_nr_periods.setValue(self.parameters[und_name]["nr_periods"])
            spin_nr_periods.valueChanged.connect(self.spin_all)
            self.spins_nr_periods.append(spin_nr_periods)
            spin_period_length = QDoubleSpinBox()
            spin_period_length.setValue(self.parameters[und_name]["period_length"])
            spin_period_length.setSuffix(" mm")
            spin_period_length.valueChanged.connect(self.spin_all)
            self.spins_period_length.append(spin_period_length)

            self.grid.addWidget(label_file,i+rows,0)
            self.grid.addWidget(line_name,i+rows,1)
            self.grid.addWidget(spin_nr_periods,i+rows,2)
            self.grid.addWidget(spin_period_length,i+rows,3)
    
    def resize_to_content(self):
        lineedit = self.sender()
        lineedit.setMinimumWidth(10+lineedit.fontMetrics().boundingRect(lineedit.text()).width())

    def spin_all(self, value):

        # realizar o spin all somente quando a checkbox estiver marcada
        if self.checkbox_valuesforall.isChecked():
        
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
