
from PyQt6.QtWidgets import (QPushButton,
                             QFrame,
                             QListWidget,
                             QListWidgetItem,
                             QCheckBox,
                             QVBoxLayout,
                             QDialog,
                             QMessageBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QTimer

from .dialog_layouts import AnalysisLayout
from . import get_path

import numpy as np


class AnalysisItem(QListWidgetItem):

    #*: da maneira implementada aqui, um subordinado pode ter outros subordinados
    #*: e isso deve se comportar bem no menu
    def __init__(self, superiors=[], subordinates=[], text='', parent=None,
                 *args, **kwargs):
        super().__init__(text, parent, *args, **kwargs)

        self.superiors = superiors #list of superior items of this item
        self.subordinates = subordinates #list of subordinate items of this item
        
    def isChecked(self) -> bool:
        return bool(self.checkState() == Qt.CheckState.Checked)

    def hasSuperior(self) -> bool:
        return bool(len(self.superiors))
    
    def isSuperiorsChecked(self) -> bool:
        return sum([superior.checkState().value for superior in self.superiors])

    def setSuperior(self, item: 'AnalysisItem'):
        self.superiors = [item]

    def hasSubordinate(self) -> bool:
        return bool(len(self.subordinates))
    
    def setSubordinate(self, item: 'AnalysisItem'):
        self.subordinates = [item]
    
    def setCheckState(self, state: Qt.CheckState) -> None:
        
        if self.hasSubordinate() and state.value: #desmarcar item e nao desmarcar seus subordinados
        #if self.hasSubordinate(): #desmarcar item e desmarcar seus subordinados
            [subordinate.setCheckState(state) for subordinate in self.subordinates]
        return super().setCheckState(state)



class AnalysisMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.WindowType.Popup)

        # analysis menu

        ## analysis menu - style
        self.setObjectName("frame")
        self.setStyleSheet("QFrame#frame{background-color: #f0f0f0; border: 1.2px solid #c0c0c0}")
        
        ## analysis menu - list
        self.list = QListWidget(parent=self)
        self.list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.list.setStyleSheet("background-color: #f0f0f0")

        ### analysis menu - list - items:
        ### Create the items and automatically add them to the list widget
        self.itemCrossTalk = AnalysisItem(text="Cross Talk",parent=self.list)
        self.itemMagneticField = AnalysisItem(text="Magnetic Field",parent=self.list)
        self.itemTrajectory = AnalysisItem(text="Trajectory",parent=self.list)
        self.itemPhaseError = AnalysisItem(text="Phase Error",parent=self.list)
        self.itemIntegrals = AnalysisItem(text="Cumulative Integrals",parent=self.list)
        self.itemIntegralsH = AnalysisItem(text="Field Integrals vs X",parent=self.list)
        # kickmap temporariamente fora, pois nao esta devidamente implementado no imaids
        #self.itemKickmap = AnalysisItem(text="Kickmap",parent=self.list)
        # multipolos e multipolos dinamicos em avaliacao
        self.itemRollOffPeaks = AnalysisItem(text="Roll Off Peaks",parent=self.list)
        self.itemRollOffAmp = AnalysisItem(text="Roll Off Amplitude",parent=self.list)
        # shimming fora, pois e' um calculo muito personalizado e que exige cuidado
        #self.Shimming = AnalysisItem(text="Shimming",parent=self.list)
        
        self.itemTrajectory.setSuperior(self.itemPhaseError)
        self.itemPhaseError.setSubordinate(self.itemTrajectory)

        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)

        self.items = [self.list.item(i) for i in range(self.list.count())]

        ### analysis menu - list - signals
        self.list.itemClicked.connect(self.item_clicked)
        self.list.itemChanged.connect(lambda: setattr(self, 'changed', True))
        #self.list.itemChanged.connect(self.item_changed)

        self.changed = False

        ## analysis menu - checkbox
        self.checkBoxSelectAll = QCheckBox("Select All",self)
        self.checkBoxSelectAll.clicked.connect(self.check_all_items)

        ## analysis menu - apply button
        self.apply = QPushButton("Apply")
        self.apply.setShortcut(Qt.Key.Key_Return)
        self.apply.clicked.connect(self.applyHide)

        ## analysis menu - hide timer
        self.timerHide = QTimer()
        self.timerHide.timeout.connect(lambda: self.timerHide.stop())
        self.timerHide.setInterval(100)
        
        ## analysis menu - layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.list)
        layout.addWidget(self.checkBoxSelectAll)
        layout.addWidget(self.apply)


        self.installEventFilter(self)
        #self.parent().installEventFilter(self)




    # FUNCTIONS

    # list functions

    def checkedItems(self):
        return [item for item in self.items if item.checkState()==Qt.CheckState.Checked]
    
    def uncheckedItems(self):
        return [item for item in self.items if item.checkState()==Qt.CheckState.Unchecked]

    def uncheckAnalysisMenu(self):
        # uncheck all checked list items
        [item.setCheckState(Qt.CheckState.Unchecked) for item in self.checkedItems()]

        # uncheck checkbox, items and remove wand icon
        if self.checkBoxSelectAll.isChecked():
            self.checkBoxSelectAll.setChecked(False)
            self.check_all_items(False)

    # SLOTS

    # list slot

    def item_clicked(self, item: AnalysisItem):
        print('item clicado')
        
        # caso o usuario marque tudo, depois clique em um item
        if self.checkBoxSelectAll.isChecked():
            self.checkBoxSelectAll.setChecked(False)

        # restaurando estado do item antes de clicar na checkbox
        if self.changed:
            # setcheckstate de qlistwidget para nao alterar estado dos subordinados tambem
            QListWidgetItem.setCheckState(item,Qt.CheckState(2-item.checkState().value))

        '''#item checkbox clicked
        if self.changed:
            # se o superior estiver marcado
            if item.hasSuperior() and item.isSuperiorsChecked():
                item.setCheckState(Qt.CheckState(2-item.checkState().value))
            if item.hasSubordinate() and item.checkState().value:
                [subordinate.setCheckState(item.checkState()) for subordinate in item.subordinates]
        
        #item label clicked (not item checkbox)
        else:
            if not item.hasSuperior() or (item.hasSuperior() and not item.isSuperiorsChecked()):
                item.setCheckState(Qt.CheckState(2-item.checkState().value))'''
        
        # mudar estado de item comum, sem superior
        # bloquear mudanca de estado para item subordinado a outro quando algum
        # de seus superiores estiver checked
        if  (not item.hasSuperior()) or \
            (item.hasSuperior() and not item.isSuperiorsChecked()):

            item.setCheckState(Qt.CheckState(2-item.checkState().value))

        # restaurando changed ao seu valor padrao
        self.changed = False
        

        # alterar ou nao icone do apply
        if len(self.checkedItems())==self.list.count():
            self.checkBoxSelectAll.setChecked(True)
            self.toggle_icon(state=2)
        else:
            self.toggle_icon(state=0)
    

    # checkbox slot: check todos os items da lista

    def check_all_items(self,checked):
        if checked:
            for item in self.uncheckedItems():
                item.setCheckState(Qt.CheckState.Checked)
        else:
            for item in self.checkedItems():
                item.setCheckState(Qt.CheckState.Unchecked)
        
        self.toggle_icon(state=checked)

        # ao final dos comandos passados no metodo, changed muda para True,
        # e´preciso retomar ele ao seu valor padrao
        self.changed = False
    

    # apply button slots

    # coloca ou tira icone da varinha do botao apply
    def toggle_icon(self,state):
        if state:
            self.apply.setIcon(QIcon(get_path('icons','wand.png')))
        else:
            self.apply.setIcon(QIcon(None))
    
    # funcionalidades do apply
    def applyHide(self):
        self.setHidden(True)

    def eventFilter(self, obj, event: QEvent):

        if event.type()==QEvent.Type.MouseButtonPress:

            geometry = self.parent().geometry()
            geometry.moveTo(0,-geometry.height())

            if geometry.contains(event.pos()):
                self.timerHide.start()
            
        return super().eventFilter(obj, event)


class AnalysisPushButton(QPushButton):

    modeChanged = pyqtSignal(bool)

    def __init__(self, text, parent, *args, **kwargs):
        super().__init__(text=text, parent=parent, *args, **kwargs)

        # features
        self.setCheckable(True)
        self.setShortcut("Ctrl+A")
        # signal
        self.clicked.connect(self.showMenu)
        # menu
        
        self.Menu = AnalysisMenu(parent=self)
        self.Menu.apply.clicked.connect(self.applyChangeMode)

    
    def showMenu(self):
        # se botao inicialmente estiver checked
        #todo: transformar em painted button para abrir menu e mudar analises de modo mais simples
        if not self.isChecked():
            # analysis button automatically unchecks itself
            self.Menu.uncheckAnalysisMenu()
            self.modeChanged.emit(True)

        # se botao inicialmente estiver unchecked
        else:
            # uncheck the analysis button
            self.setChecked(False)

            # expose the menu
            if not self.Menu.timerHide.isActive():
                # positionate the menu
                corner = self.parent().mapToGlobal(self.geometry().bottomLeft())
                self.Menu.setGeometry(corner.x()+1, corner.y(), 180, 240)
                self.Menu.show()

            # restaura valor padrao de changed
            self.Menu.changed = False
    
    def applyChangeMode(self):
        if self.Menu.checkedItems():
            self.modeChanged.emit(False)


class AnalysisDialog(QDialog):

    default_params = {
        "Magnetic Field": {"x": 0,
                           "y": 0,
                           "z": np.arange(-900,900+0.5,0.5),
                           "nproc": None,
                           "chunksize": 100},
        "Trajectory": {"energy": 3,
                       "r0": [0,0,-900,0,0,1],
                       "zmax": 900,
                       "rkstep": 0.5,
                       "dz": 0,
                       "on_axis_field": False},
        "Phase Error": {"energy": 3,
                        "traj": "calculated",
                        "bx_amp": "calculated",
                        "by_amp": "calculated",
                        "skip_poles": 4,
                        "zmin": None,
                        "zmax": None,
                        "field_comp": None},
        "Cumulative Integrals": {"z_list": np.arange(-900,900+0.5,0.5),
                                 "x": 0,
                                 "y": 0,
                                 "field_list": None,
                                 "nproc": None,
                                 "chunksize": 100},
        "Field Integrals vs X": {"z": np.arange(-900,900+0.5,0.5),
                                 "x": np.arange(-5,5+1,1),
                                 "y": 0},
        "Roll Off Peaks": {"z": np.arange(-900,900+0.5,0.5),
                           "x": np.arange(-5,5+0.5,0.5),
                           "y": 0,
                           "field_comp": None},
        "Roll Off Amplitude": {"z": np.arange(-900,900+0.5,0.5),
                               "x": np.arange(-5,5+0.5,0.5),
                               "y": 0}
    }

    def __init__(self, params_kwargs, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setWindowTitle("Analysis Parameters")

        self.layoutAnalysis = AnalysisLayout(params_kwargs, parent=self)

        # signals
        buttonBox = self.layoutAnalysis.buttonBox
        buttonRestore = buttonBox.buttons()[2]
        buttonRestore.setToolTip("Restore the parameters values to default")
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        buttonRestore.clicked.connect(self.restore)


    def restore(self):
        self.layoutAnalysis.editMagneticField.set_values(self.default_params["Magnetic Field"])
        self.layoutAnalysis.editTrajectory.set_values(self.default_params["Trajectory"])
        self.layoutAnalysis.editPhaseError.set_values(self.default_params["Phase Error"])
        self.layoutAnalysis.editIntegrals.set_values(self.default_params["Field Integrals"])
        self.layoutAnalysis.editRollOffPeaks.set_values(self.default_params["Roll Off Peaks"])
        self.layoutAnalysis.editRollOffAmp.set_values(self.default_params["Roll Off Amplitude"])

    @classmethod
    def updateParameters(cls, params_kwargs, parent=None):

        dialog = cls(params_kwargs, parent)
        answer = dialog.exec()

        if answer==QDialog.DialogCode.Accepted:

            field = dialog.layoutAnalysis.editMagneticField
            traj = dialog.layoutAnalysis.editTrajectory
            phaserr = dialog.layoutAnalysis.editPhaseError
            integrals = dialog.layoutAnalysis.editIntegrals
            integralsH = dialog.layoutAnalysis.editIntegralsH
            rop = dialog.layoutAnalysis.editRollOffPeaks
            roa = dialog.layoutAnalysis.editRollOffAmp

            #MagneticField
            x, y, z, nproc, chunksize = field.get_values()
            params_kwargs["Magnetic Field"] = {"x": x,
                                               "y": y,
                                               "z": z,
                                               "nproc": nproc,
                                               "chunksize": chunksize}

            #Trajectory
            energy, r0, zmax, rkstep, dz, on_axis_field = traj.get_values()
            params_kwargs["Trajectory"] = {"energy": energy,
                                           "r0": r0,
                                           "zmax": zmax,
                                           "rkstep": rkstep,
                                           "dz": dz,
                                           "on_axis_field": on_axis_field}

            #PhaseError
            energy, skip_poles, zmin, zmax, field_comp = phaserr.get_values()
            params_kwargs["Phase Error"] = {"energy": energy,
                                            "traj": "calculated",
                                            "bx_amp": "calculated",
                                            "by_amp": "calculated",
                                            "skip_poles": skip_poles,
                                            "zmin": zmin,
                                            "zmax": zmax,
                                            "field_comp": field_comp}

            #Integrals
            z_list, x, y, nproc, chunksize = integrals.get_values()
            params_kwargs["Cumulative Integrals"] = {"z_list": z_list,
                                                     "x": x,
                                                     "y": y,
                                                     "field_list": None,
                                                     "nproc": nproc,
                                                     "chunksize": chunksize}

            z, x, y = integralsH.get_values()
            params_kwargs["Field Integrals vs X"] = {"z": z,
                                                     "x": x,
                                                     "y": y}

            #RollOffPeaks
            z, x, y, field_comp = rop.get_values()
            params_kwargs["Roll Off Peaks"] = {"z": z,
                                               "x": x,
                                               "y": y,
                                               "field_comp": field_comp}

            #RollOffAmp
            z, x, y = roa.get_values()
            params_kwargs["Roll Off Amplitude"] = {"z": z,
                                                   "x": x,
                                                   "y": y}

        return params_kwargs #*: retornar a mesma coisa, mesmo se nao houver edicao

    def accept(self) -> None:

        field = self.layoutAnalysis.editMagneticField
        i = field.indexListChecked
        phaserr = self.layoutAnalysis.editPhaseError
        integrals = self.layoutAnalysis.editIntegrals
        rop = self.layoutAnalysis.editRollOffPeaks
        roa = self.layoutAnalysis.editRollOffAmp

        StepZero = (i != -1 and field.spins_step[i].value() == 0) or \
                   integrals.spin_z_list_step.value() == 0 or \
                   rop.spin_zstep.value() == 0 or \
                   rop.spin_xstep.value() == 0

        StartEqualEnd = \
            (i != -1 and field.spins_start[i].value() == field.spins_end[i].value()) or \
            integrals.spin_z_list_start.value() == integrals.spin_z_list_end.value() or \
            rop.spin_zstart.value() == rop.spin_zend.value() or \
            rop.spin_xstart.value() == rop.spin_xend.value() or \
            roa.spin_zstart.value() == roa.spin_zend.value() or \
            roa.spin_xstart.value() == roa.spin_zend.value()

        StartGreaterEnd_StepPositive = \
            (i != -1 and (field.spins_start[i].value() > field.spins_end[i].value() and \
             field.spins_step[i].value() > 0)) or \
            (integrals.spin_z_list_start.value() > integrals.spin_z_list_end.value() and \
             integrals.spin_z_list_step.value() > 0) or \
            (rop.spin_zstart.value() > rop.spin_zend.value() and \
             rop.spin_zstep.value() > 0) or \
            (rop.spin_xstart.value() > rop.spin_xend.value() and \
             rop.spin_xstep.value() > 0) or \
            (roa.spin_zstart.value() > roa.spin_zend.value() and \
             roa.spin_zstep.value() > 0) or \
            (roa.spin_xstart.value() > roa.spin_xend.value() and \
             roa.spin_xstep.value() > 0)

        StartLessEnd_StepNegative = \
            (i != -1 and (field.spins_start[i].value() < field.spins_end[i].value() and \
             field.spins_step[i].value() < 0)) or \
            (integrals.spin_z_list_start.value() < integrals.spin_z_list_end.value() and \
             integrals.spin_z_list_step.value() < 0) or \
            (rop.spin_zstart.value() < rop.spin_zend.value() and \
             rop.spin_zstep.value() < 0) or \
            (rop.spin_xstart.value() < rop.spin_xend.value() and \
             rop.spin_xstep.value() < 0) or \
            (roa.spin_zstart.value() < roa.spin_zend.value() and \
             roa.spin_zstep.value() < 0) or \
            (roa.spin_xstart.value() < roa.spin_xend.value() and \
             roa.spin_xstep.value() < 0)
        
        #todo: procurar maneira de permitir digitar apenas texto numerico
        field_combotext = field.combo_nproc.currentText()
        phaserr_zmintext = phaserr.combo_zmin.currentText()
        phaserr_zmaxtext = phaserr.combo_zmax.currentText()
        integrals_combotext = integrals.combo_nproc.currentText()
        TextNumeric = \
            field.combo_nproc.isTextNumeric(field_combotext) and \
            phaserr.combo_zmin.isTextNumeric(phaserr_zmintext) and \
            phaserr.combo_zmax.isTextNumeric(phaserr_zmaxtext) and \
            integrals.combo_nproc.isTextNumeric(integrals_combotext)

        if StepZero:
            QMessageBox.critical(self,
                                 "Critical Warning",
                                 "The arrays must have nonzero steps!")
        elif StartEqualEnd:
            QMessageBox.critical(self,
                                 "Critical Warning",
                                 "The arrays must have different start and end points!")
        #todo: caso do start menor e step negativo
        elif StartGreaterEnd_StepPositive:
            QMessageBox.critical(self,
                                 "Critical Warning",
                                 "Arrays with start greater than end must have negative step!")
        elif StartLessEnd_StepNegative:
            QMessageBox.critical(self,
                                 "Critical Warning",
                                 "Arrays with start less than end must have positive step!")
        elif not TextNumeric:
            QMessageBox.critical(self,
                                 "Critical Warning",
                                 "Numeric Combo Boxes must have numeric values!")
        else:
            return super().accept()

        