from PyQt6.QtWidgets import (QWidget,
                             QDialog,
                             QScrollArea,
                             QLabel,
                             QVBoxLayout,
                             QDialogButtonBox,
                             QFormLayout,
                             QSizePolicy)
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

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        widget = QWidget()

        self.setWidget(widget)

        self.vbox = QVBoxLayout(widget)
        self.vbox.setSpacing(0) #!
        self.vbox.setContentsMargins(0,6,0,0) #!



        if ID is None:
            self.label_IDname = QLabel("ID Name", font=font10, alignment=alignHCenter)
        else:
            self.label_IDname = QLabel(str(ID.name), font=font10, alignment=alignHCenter)



        boxUnd = CollapsibleBox("Undulator Geometry")
        boxUnd.setContentExpanded(True)

        self.formUnd = QFormLayout(boxUnd.widget())

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
            self.label_nr_periods = QLabel(f"{ID.nr_periods:.3f}", font=font10, alignment=alignRight)
            self.label_period_length = QLabel(f"{ID.period_length:.3f}", font=font10, alignment=alignRight)
            self.label_gap = QLabel(f"{ID.gap:.3f}", font=font10, alignment=alignRight)

        self.formUnd.insertRow(0,"Nº Periods:",self.label_nr_periods)
        self.formUnd.insertRow(1,"Period Length [mm]:",self.label_period_length)
        self.formUnd.insertRow(2,"Gap [mm]:",self.label_gap)






        boxAmp = CollapsibleBox("Field Amplitudes and Phase")
        boxAmp.setContentExpanded(True)

        
        self.formAmp = QFormLayout(boxAmp.widget())

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
        
        self.label_rms = QLabel("-", font=font10, alignment=alignRight)

        self.formPhasErr.insertRow(0,"RMS [deg]:",self.label_rms)
        




        boxIntegrals = CollapsibleBox("Field Integrals")
        boxIntegrals.setContentExpanded(True)

        self.formIntegrals = QFormLayout(boxIntegrals.widget())
        
        self.label_ibx = QLabel("-", font=font10, alignment=alignRight)
        self.label_iby = QLabel("-", font=font10, alignment=alignRight)
        self.label_ibz = QLabel("-", font=font10, alignment=alignRight)
        self.label_iibx = QLabel("-", font=font10, alignment=alignRight)
        self.label_iiby = QLabel("-", font=font10, alignment=alignRight)
        self.label_iibz = QLabel("-", font=font10, alignment=alignRight)

        self.formIntegrals.insertRow(0,"IBx [G.cm]:",self.label_ibx)
        self.formIntegrals.insertRow(1,"IBy [G.cm]:",self.label_iby)
        self.formIntegrals.insertRow(2,"IBz [G.cm]:",self.label_ibz)
        self.formIntegrals.insertRow(3,"IIBx [kG.cm2]:",self.label_iibx)
        self.formIntegrals.insertRow(4,"IIBy [kG.cm2]:",self.label_iiby)
        self.formIntegrals.insertRow(5,"IIBz [kG.cm2]:",self.label_iibz)

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

    def clean_default_labels(self):

        self.vbox.removeWidget(self.label_IDname)
        self.label_IDname.deleteLater()
        
        self.formUnd.removeWidget(self.label_nr_periods)
        self.formUnd.removeWidget(self.label_period_length)
        self.formUnd.removeWidget(self.label_gap)
        self.label_nr_periods.deleteLater()
        self.label_period_length.deleteLater()
        self.label_gap.deleteLater()

        self.formAmp.removeWidget(self.label_bxamp)
        self.formAmp.removeWidget(self.label_byamp)
        self.formAmp.removeWidget(self.label_bzamp)
        self.formAmp.removeWidget(self.label_bxyphase)
        self.label_bxamp.deleteLater()
        self.label_byamp.deleteLater()
        self.label_bzamp.deleteLater()
        self.label_bxyphase.deleteLater()

        self.formK.removeWidget(self.label_kh)
        self.formK.removeWidget(self.label_kv)
        self.label_kh.deleteLater()
        self.label_kv.deleteLater()

    def clean_phaserr_label(self):
        self.formPhasErr.removeWidget(self.label_rms)
        self.label_rms.deleteLater()

    def clean_integrals_labels(self):
        self.formIntegrals.removeWidget(self.label_ibx)
        self.formIntegrals.removeWidget(self.label_iby)
        self.formIntegrals.removeWidget(self.label_ibz)
        self.formIntegrals.removeWidget(self.label_iibx)
        self.formIntegrals.removeWidget(self.label_iiby)
        self.formIntegrals.removeWidget(self.label_iibz)
        self.label_ibx.deleteLater()
        self.label_iby.deleteLater()
        self.label_ibz.deleteLater()
        self.label_iibx.deleteLater()
        self.label_iiby.deleteLater()
        self.label_iibz.deleteLater()
    
    def set_insertion_device(self, ID):

        self._ID = ID

        #todo: colocar condicao pra saber se ja foi inserido widgets na form
        self.clean_default_labels()
        


        if ID is None:
            self.label_IDname = QLabel("ID Name", font=font10, alignment=alignHCenter)

            self.label_bxamp = QLabel("-", font=font10, alignment=alignRight)
            self.label_byamp = QLabel("-", font=font10, alignment=alignRight)
            self.label_bzamp = QLabel("-", font=font10, alignment=alignRight)
            self.label_bxyphase = QLabel("-", font=font10, alignment=alignRight)

            self.label_kh = QLabel("-", font=font10, alignment=alignRight)
            self.label_kv = QLabel("-", font=font10, alignment=alignRight)

            self.label_nr_periods = QLabel("-", font=font10, alignment=alignRight)
            self.label_period_length = QLabel("-", font=font10, alignment=alignRight)
            self.label_gap = QLabel("-", font=font10, alignment=alignRight)

        else:
            self.label_IDname = QLabel(str(ID.name), font=font10, alignment=alignHCenter)

            bxamp, byamp, bzamp, bxyphase = ID.calc_field_amplitude()
            self.label_bxamp = QLabel(f"{bxamp:.3f}", font=font10, alignment=alignRight)
            self.label_byamp = QLabel(f"{byamp:.3f}", font=font10, alignment=alignRight)
            self.label_bzamp = QLabel(f"{bzamp:.3f}", font=font10, alignment=alignRight)
            self.label_bxyphase = QLabel(f"{bxyphase*180/np.pi:.3f}", font=font10, alignment=alignRight)

            kh, kv = ID.calc_deflection_parameter(bxamp, byamp)
            self.label_kh = QLabel(f"{kh:.3f}", font=font10, alignment=alignRight)
            self.label_kv = QLabel(f"{kv:.3f}", font=font10, alignment=alignRight)

            self.label_nr_periods = QLabel(f"{ID.nr_periods:.3f}", font=font10, alignment=alignRight)
            self.label_period_length = QLabel(f"{ID.period_length:.3f}", font=font10, alignment=alignRight)
            self.label_gap = QLabel(f"{ID.gap:.3f}", font=font10, alignment=alignRight)

        self.vbox.insertWidget(0,self.label_IDname)
        
        self.formUnd.setWidget(0,roleField,self.label_nr_periods)
        self.formUnd.setWidget(1,roleField,self.label_period_length)
        self.formUnd.setWidget(2,roleField,self.label_gap)

        self.formAmp.setWidget(0,roleField,self.label_bxamp)
        self.formAmp.setWidget(1,roleField,self.label_byamp)
        self.formAmp.setWidget(2,roleField,self.label_bzamp)
        self.formAmp.setWidget(3,roleField,self.label_bxyphase)

        self.formK.setWidget(0,roleField,self.label_kh)
        self.formK.setWidget(1,roleField,self.label_kv)



    def update_phaserr(self, rms):
        self.clean_phaserr_label()
        
        if rms:
            self.label_rms = QLabel(f"{rms:.3f}", font=font10, alignment=alignRight)
        else:
            self.label_rms = QLabel(f"-", font=font10, alignment=alignRight)
        
        self.formPhasErr.setWidget(0,roleField,self.label_rms)


    def update_integrals(self, integrals):
        self.clean_integrals_labels()

        if integrals:
            ibx, iby, ibz, iibx, iiby, iibz = integrals
            self.label_ibx = QLabel(f"{ibx[-1]:.3f}", font=font10, alignment=alignRight)
            self.label_iby = QLabel(f"{iby[-1]:.3f}", font=font10, alignment=alignRight)
            self.label_ibz = QLabel(f"{ibz[-1]:.3f}", font=font10, alignment=alignRight)
            self.label_iibx = QLabel(f"{iibx[-1]:.3f}", font=font10, alignment=alignRight)
            self.label_iiby = QLabel(f"{iiby[-1]:.3f}", font=font10, alignment=alignRight)
            self.label_iibz = QLabel(f"{iibz[-1]:.3f}", font=font10, alignment=alignRight)
        else:
            self.label_ibx = QLabel(f"-", font=font10, alignment=alignRight)
            self.label_iby = QLabel(f"-", font=font10, alignment=alignRight)
            self.label_ibz = QLabel(f"-", font=font10, alignment=alignRight)
            self.label_iibx = QLabel(f"-", font=font10, alignment=alignRight)
            self.label_iiby = QLabel(f"-", font=font10, alignment=alignRight)
            self.label_iibz = QLabel(f"-", font=font10, alignment=alignRight)

        self.formIntegrals.setWidget(0,roleField,self.label_ibx)
        self.formIntegrals.setWidget(1,roleField,self.label_iby)
        self.formIntegrals.setWidget(2,roleField,self.label_ibz)
        self.formIntegrals.setWidget(3,roleField,self.label_iibx)
        self.formIntegrals.setWidget(4,roleField,self.label_iiby)
        self.formIntegrals.setWidget(5,roleField,self.label_iibz)

        






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

