from PyQt6.QtWidgets import (QApplication,
                             QWidget,
                             QDialog,
                             QScrollArea,
                             QLabel,
                             QVBoxLayout,
                             QDialogButtonBox,
                             QFormLayout,
                             QSizePolicy,
                             QMenu)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from .basics import CollapsibleBox

import numpy as np


font10 = QFont("MSSansSerif",10)

roleLabel = QFormLayout.ItemRole.LabelRole
roleField = QFormLayout.ItemRole.FieldRole

alignRight = Qt.AlignmentFlag.AlignRight
alignHCenter = Qt.AlignmentFlag.AlignHCenter

sizeFixed = QSizePolicy.Policy.Fixed
sizePreffered = QSizePolicy.Policy.Preferred

class SummaryWidget(QScrollArea):
    def __init__(self, ID=None, parent=None):
        super().__init__(parent)

        self._ID = ID
        self._phaserr = None
        self._integrals = None

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        widget = QWidget()

        self.setWidget(widget)

        self.vbox = QVBoxLayout(widget)
        self.vbox.setSpacing(0)
        self.vbox.setContentsMargins(0,6,0,0)



        if ID is None:
            self.label_IDname = QLabel("ID Name", font=font10, alignment=alignHCenter)
        else:
            self.label_IDname = QLabel(str(ID.name), font=font10, alignment=alignHCenter)



        boxUnd = CollapsibleBox("Undulator Geometry")
        boxUnd.setContentExpanded(True)

        self.formUnd = QFormLayout(boxUnd.widget())
        self.formUnd.setObjectName("Undulator Geometry")

        #label_dp
        #label_dcp
        #label_dg
        #label_dgv
        #label_dgh

        if ID is None:
            self.label_nr_periods = QLabel("-", font=font10, alignment=alignRight)
            self.label_period_length = QLabel("-", font=font10, alignment=alignRight)
            self.label_gap = QLabel("-", font=font10, alignment=alignRight)
        else:
            self.label_nr_periods = QLabel(f"{ID.nr_periods}", font=font10, alignment=alignRight)
            self.label_period_length = QLabel(f"{ID.period_length:.3f}", font=font10, alignment=alignRight)
            self.label_gap = QLabel(f"{ID.gap:.3f}", font=font10, alignment=alignRight)

        self.formUnd.insertRow(0,"Nº Periods:",self.label_nr_periods)
        self.formUnd.insertRow(1,"Period Length [mm]:",self.label_period_length)
        self.formUnd.insertRow(2,"Gap [mm]:",self.label_gap)






        boxAmp = CollapsibleBox("Field Amplitudes and Phase")
        boxAmp.setContentExpanded(True)

        
        self.formAmp = QFormLayout(boxAmp.widget())
        self.formAmp.setObjectName("Field Amplitudes and Phase")

        if ID is None:
            self.label_bxamp = QLabel("-", font=font10, alignment=alignRight)
            self.label_byamp = QLabel("-", font=font10, alignment=alignRight)
            self.label_bzamp = QLabel("-", font=font10, alignment=alignRight)
            self.label_bxyphase = QLabel("-", font=font10, alignment=alignRight)
        else:
            bxamp, byamp, bzamp, bxyphase = ID.calc_field_amplitude()
            self.label_bxamp = QLabel(f"{bxamp:.3f}", font=font10, alignment=alignRight)
            self.label_byamp = QLabel(f"{byamp:.3f}", font=font10, alignment=alignRight)
            self.label_bzamp = QLabel(f"{bzamp:.3f}", font=font10, alignment=alignRight)
            self.label_bxyphase = QLabel(f"{bxyphase*180/np.pi:.3f}", font=font10, alignment=alignRight)

        self.formAmp.insertRow(0,"Bx Amp [T]:",self.label_bxamp)
        self.formAmp.insertRow(1,"By Amp [T]:",self.label_byamp)
        self.formAmp.insertRow(2,"Bz Amp [T]:",self.label_bzamp)
        self.formAmp.insertRow(3,"Bxy Phase [deg]:",self.label_bxyphase)
        





        boxK = CollapsibleBox("Deflection Parameter")
        boxK.setContentExpanded(True)
        
        
        self.formK = QFormLayout(boxK.widget())
        self.formK.setObjectName("Deflection Parameter")
        
        if ID is None:
            self.label_kh = QLabel("-", font=font10, alignment=alignRight)
            self.label_kv = QLabel("-", font=font10, alignment=alignRight)
        else:
            kh, kv = ID.calc_deflection_parameter(bxamp, byamp)
            self.label_kh = QLabel(f"{kh:.3f}", font=font10, alignment=alignRight)
            self.label_kv = QLabel(f"{kv:.3f}", font=font10, alignment=alignRight)

        self.formK.insertRow(0,"Kh [T.mm]:",self.label_kh)
        self.formK.insertRow(1,"Kv [T.mm]:",self.label_kv)
        



        boxPhasErr = CollapsibleBox("Phase Error")
        boxPhasErr.setContentExpanded(True)

        self.formPhasErr = QFormLayout(boxPhasErr.widget())
        self.formPhasErr.setObjectName("Phase Error")
        
        self.label_rms = QLabel("-", font=font10, alignment=alignRight)

        self.formPhasErr.insertRow(0,"RMS P.E. [deg]:",self.label_rms)
        




        boxIntegrals = CollapsibleBox("Field Integrals")
        boxIntegrals.setContentExpanded(True)

        self.formIntegrals = QFormLayout(boxIntegrals.widget())
        self.formIntegrals.setObjectName("Field Integrals")
        
        self.labels_integrals = []
        for i in range(6):
            self.labels_integrals.append(QLabel("-", font=font10, alignment=alignRight))

        for i, label in enumerate(["IBx [G.cm]:","IBy [G.cm]:","IBz [G.cm]:",
                                   "IIBx [kG.cm2]:","IIBy [kG.cm2]:","IIBz [kG.cm2]:"]):
            
            self.formIntegrals.insertRow(i,label,self.labels_integrals[i])

        self.vbox.addWidget(self.label_IDname)
        self.vbox.addWidget(boxUnd)
        self.vbox.addWidget(boxAmp)
        self.vbox.addWidget(boxK)
        self.vbox.addWidget(boxPhasErr)
        self.vbox.addWidget(boxIntegrals)
        self.vbox.addStretch()

    @property
    def ID(self):
        return self._ID
    
    @property
    def phaserr(self):
        return self._phaserr
    
    @property
    def integrals(self):
        return self._integrals
    
    def get_forms(self):
        return [self.formUnd,self.formAmp,self.formK,self.formPhasErr,self.formIntegrals]
    
    def open_context(self, pos):

        menu = QMenu(self)
        menu.addAction("Copy")
        action = menu.exec(self.mapToGlobal(pos))
        if action and action.text()=="Copy":

            cb = QApplication.clipboard()

            cbText = ''
            for form in self.get_forms():
                # cbText += f'\n{form.objectName()}'
                for row in range(form.rowCount()):
                    label = form.itemAt(row,roleLabel).widget().text()
                    field = form.itemAt(row,roleField).widget().text()
                    cbText += f'\n{label}\t{field}'
            cbText = cbText.lstrip('\n')

            cb.setText(cbText)


    def update(self, id_dict):
        if id_dict is None:
            if self.ID is not None:
                self.update_ID(None)
                self.update_phaserr(None)
                self.update_integrals(None)
        else:
            ID = id_dict["InsertionDeviceObject"]

            isPhasErrAdded = id_dict.get("Phase Error") and \
                             not self.phaserr
            isIntegralsAdded = (id_dict.get("Cumulative Integrals") or \
                                id_dict.get("Field Integrals vs X")) and \
                                not self.integrals

            if ID != self.ID or isPhasErrAdded or isIntegralsAdded:

                self.update_ID(ID)
                phaserr_dict = id_dict.get("Phase Error")
                self.update_phaserr(phaserr_dict)

                integrals_dict, idx = None, None
                if "Cumulative Integrals" in id_dict:
                    integrals_dict, idx = id_dict["Cumulative Integrals"], -1
                elif "Field Integrals vs X" in id_dict:
                    integrals_dict = id_dict["Field Integrals vs X"]
                    coord, *_ = integrals_dict.values()
                    idxarray_zero = np.where(coord == 0)[0]
                    if idxarray_zero.size!=0:
                        idx = idxarray_zero[0]
                    else:
                        integrals_dict = None
                
                self.update_integrals(integrals_dict,idx)
    
    def update_ID(self, ID):

        self._ID = ID

        if ID is None:

            self.label_IDname.setText("ID Name")

            self.label_bxamp.setText("-")
            self.label_byamp.setText("-")
            self.label_bzamp.setText("-")
            self.label_bxyphase.setText("-")

            self.label_kh.setText("-")
            self.label_kv.setText("-")

            self.label_nr_periods.setText("-")
            self.label_period_length.setText("-")
            self.label_gap.setText("-")

        else:
            self.label_IDname.setText(str(ID.name))

            bxamp, byamp, bzamp, bxyphase = ID.calc_field_amplitude()
            self.label_bxamp.setText(f"{bxamp:.3f}")
            self.label_byamp.setText(f"{byamp:.3f}")
            self.label_bzamp.setText(f"{bzamp:.3f}")
            self.label_bxyphase.setText(f"{bxyphase*180/np.pi:.3f}")

            kh, kv = ID.calc_deflection_parameter(bxamp, byamp)
            self.label_kh.setText(f"{kh:.3f}")
            self.label_kv.setText(f"{kv:.3f}")

            self.label_nr_periods.setText(f"{ID.nr_periods:.3f}")
            self.label_period_length.setText(f"{ID.period_length:.3f}")
            self.label_gap.setText(f"{ID.gap:.3f}")

    def update_phaserr(self, phaserr_dict):

        self._phaserr = phaserr_dict

        self.label_rms.setText(f"{phaserr_dict['RMS [deg]']:.3f}"
                               if phaserr_dict
                               else "-")
    
    def update_integrals(self, integrals_dict, idx=-1):

        self._integrals = integrals_dict

        for i in range(6):
            label = self.labels_integrals[i]

            if integrals_dict:
                _, *integrals = integrals_dict.values()
                label.setText(f"{integrals[i][idx]:.3f}")
            else:
                label.setText("-")





class SummaryDialog(QDialog):
    def __init__(self, ID, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"{ID.name} Summary")

        dialogvbox = QVBoxLayout(self)

        self.summary = SummaryWidget(ID)


        # dialog button box
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)

        dialogvbox.addWidget(self.summary)
        dialogvbox.addWidget(self.buttonBox)

        self.setMinimumWidth(self.width()*0.4)


        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

