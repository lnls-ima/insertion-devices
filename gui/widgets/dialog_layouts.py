import typing
from PyQt6.QtWidgets import (QWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QFormLayout,
                             QGridLayout,
                             QLabel,
                             QLineEdit,
                             QCheckBox,
                             QComboBox,
                             QToolButton,
                             QDialogButtonBox,
                             QSpinBox,
                             QDoubleSpinBox,
                             QScrollArea,
                             QGroupBox,
                             QSizePolicy,
                             QRadioButton,
                             QTabWidget)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from .basics import VerticalTabWidget

import numpy as np


# --------------------- FLAGS --------------------- #

fontConsolas8 = QFont("Consolas",8)
fontConsolas10 = QFont("Consolas",10)
fontConsolas14 = QFont("Consolas",14)
sizeFixed = QSizePolicy.Policy.Fixed
sizePreferred = QSizePolicy.Policy.Preferred
alignLeft = Qt.AlignmentFlag.AlignLeft
alignHCenter = Qt.AlignmentFlag.AlignHCenter
alignRight = Qt.AlignmentFlag.AlignRight
alignVCenter = Qt.AlignmentFlag.AlignVCenter
alignCenter = Qt.AlignmentFlag.AlignCenter

# ------------------------------------------------- #


class DataLayout(QVBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.gridFiles = QGridLayout()

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
        
        self.button_browse = QToolButton()
        self.button_browse.setText("...")
        #button_browse.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        

        self.checkbox_valuesforall = QCheckBox("Use period values change for all")
        self.checkbox_valuesforall.setChecked(True)
        

        hbox_browse = QHBoxLayout()
        hbox_browse.addWidget(label_browse)
        hbox_browse.addWidget(self.button_browse)

        self.gridFiles.addLayout(hbox_browse,0,0,Qt.AlignmentFlag.AlignLeft)
        self.gridFiles.addWidget(self.checkbox_valuesforall,0,2,1,2)
        self.gridFiles.addWidget(label_files,1,0)
        self.gridFiles.addWidget(label_names,1,1)
        self.gridFiles.addWidget(label_nr_periods,1,2)
        self.gridFiles.addWidget(label_period_length,1,3)

        ## dialog button box - buttons
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        # dialog button box
        self.buttonBox = QDialogButtonBox(buttons)
        
        
        self.addLayout(self.gridFiles)
        self.addWidget(self.buttonBox)


    def gridFiles_insertAfterRow(self, filename: str, pre_row_index: int) -> typing.Tuple[QLineEdit, QSpinBox, QDoubleSpinBox]:
        
        label_file = QLabel(filename)
        line_name = QLineEdit()
        spin_nr_periods = QSpinBox()
        spin_period_length = QDoubleSpinBox()
        spin_period_length.setSuffix(" mm")
        
        self.gridFiles.addWidget(label_file,pre_row_index,0)
        self.gridFiles.addWidget(line_name,pre_row_index,1)
        self.gridFiles.addWidget(spin_nr_periods,pre_row_index,2)
        self.gridFiles.addWidget(spin_period_length,pre_row_index,3)

        return line_name, spin_nr_periods, spin_period_length
    



class ModelGroupBox(QGroupBox):
    def __init__(self,model_name='',parent=None,
                 nr_periods=0,period_length=0,gap=0,longitudinal_distance=0,mr=0,
                 *args,**kwargs):
        
        super().__init__(title=f'{model_name} Parameters',parent=parent,
                         *args,**kwargs)

        self.layout_group_h = QHBoxLayout(self)

        self.layout_group_form = QFormLayout()

        self.label_nr_periods = QLabel("Number of Periods:")
        self.label_period_length = QLabel("Period Length:")
        self.label_gap = QLabel("Gap Length:")
        self.label_longitudinal_distance = QLabel("Longitudinal Distance:")
        self.label_mr = QLabel("Magnetization Remanent:") #todo: mudar nome

        self.spin_nr_periods = QSpinBox(parent=self)
        self.spin_nr_periods.setObjectName("nr_periods")
        self.spin_nr_periods.setProperty("value",nr_periods)
        self.spin_period_length = QDoubleSpinBox(parent=self)
        self.spin_period_length.setObjectName("period_length")
        self.spin_period_length.setDecimals(1)
        self.spin_period_length.setProperty("value",period_length)
        self.spin_period_length.setSuffix(" mm")
        self.spin_gap = QDoubleSpinBox(parent=self)
        self.spin_gap.setObjectName("gap")
        self.spin_gap.setDecimals(1)
        self.spin_gap.setProperty("value",gap)
        self.spin_gap.setSuffix(" mm")
        self.spin_longitudinal_distance = QDoubleSpinBox(parent=self)
        self.spin_longitudinal_distance.setObjectName("longitudinal_distance")
        self.spin_longitudinal_distance.setDecimals(3)
        self.spin_longitudinal_distance.setProperty("value",longitudinal_distance)
        self.spin_longitudinal_distance.setSuffix(" mm")
        self.spin_mr = QDoubleSpinBox(parent=self)
        self.spin_mr.setObjectName("mr")
        self.spin_mr.setDecimals(2)
        self.spin_mr.setProperty("value",mr)
        self.spin_mr.setSuffix(" T")

        #checar se ha' maneira mais simples de povoar o form layout
        self.layout_group_form.setWidget(0,QFormLayout.ItemRole.LabelRole,self.label_nr_periods)
        self.layout_group_form.setWidget(0,QFormLayout.ItemRole.FieldRole,self.spin_nr_periods)
        self.layout_group_form.setWidget(1,QFormLayout.ItemRole.LabelRole,self.label_period_length)
        self.layout_group_form.setWidget(1,QFormLayout.ItemRole.FieldRole,self.spin_period_length)
        self.layout_group_form.setWidget(2,QFormLayout.ItemRole.LabelRole,self.label_gap)
        self.layout_group_form.setWidget(2,QFormLayout.ItemRole.FieldRole,self.spin_gap)
        self.layout_group_form.setWidget(4,QFormLayout.ItemRole.LabelRole,self.label_longitudinal_distance)
        self.layout_group_form.setWidget(4,QFormLayout.ItemRole.FieldRole,self.spin_longitudinal_distance)
        self.layout_group_form.setWidget(3,QFormLayout.ItemRole.LabelRole,self.label_mr)
        self.layout_group_form.setWidget(3,QFormLayout.ItemRole.FieldRole,self.spin_mr)
        
        self.layout_group_h.addLayout(self.layout_group_form)

        self.groupCassettePositions = QGroupBox(title="Cassette Parameters",parent=self)

        self.formCassettePos = QFormLayout(parent=self.groupCassettePositions)

        self.label_dp = QLabel("dp:")
        self.label_dcp = QLabel("dcp:") 
        self.label_dg = QLabel("dg:")
        self.label_dgv = QLabel("dgv:")
        self.label_dgh = QLabel("dgh:")

        self.spin_dp = QDoubleSpinBox()#parent=self.groupCassettePositions)
        self.spin_dp.setObjectName("dp")
        self.spin_dp.setDecimals(2)
        self.spin_dp.setSuffix(" mm")
        self.spin_dcp = QDoubleSpinBox()
        self.spin_dcp.setObjectName("dcp")
        self.spin_dcp.setDecimals(2)
        self.spin_dcp.setSuffix(" mm")
        self.spin_dg = QDoubleSpinBox()
        self.spin_dg.setObjectName("dg")
        self.spin_dg.setDecimals(2)
        self.spin_dg.setSuffix(" mm")
        self.spin_dgv = QDoubleSpinBox()
        self.spin_dgv.setObjectName("dgv")
        self.spin_dgv.setDecimals(2)
        self.spin_dgv.setSuffix(" mm")
        self.spin_dgh = QDoubleSpinBox()
        self.spin_dgh.setObjectName("dgh")
        self.spin_dgh.setDecimals(2)
        self.spin_dgh.setSuffix(" mm")

        self.formCassettePos.setWidget(0,QFormLayout.ItemRole.LabelRole,self.label_dp)
        self.formCassettePos.setWidget(0,QFormLayout.ItemRole.FieldRole,self.spin_dp)
        self.formCassettePos.setWidget(1,QFormLayout.ItemRole.LabelRole,self.label_dcp)
        self.formCassettePos.setWidget(1,QFormLayout.ItemRole.FieldRole,self.spin_dcp)
        self.formCassettePos.setWidget(2,QFormLayout.ItemRole.LabelRole,self.label_dg)
        self.formCassettePos.setWidget(2,QFormLayout.ItemRole.FieldRole,self.spin_dg)
        self.formCassettePos.setWidget(3,QFormLayout.ItemRole.LabelRole,self.label_dgv)
        self.formCassettePos.setWidget(3,QFormLayout.ItemRole.FieldRole,self.spin_dgv)
        self.formCassettePos.setWidget(4,QFormLayout.ItemRole.LabelRole,self.label_dgh)
        self.formCassettePos.setWidget(4,QFormLayout.ItemRole.FieldRole,self.spin_dgh)

        if 'Delta' not in model_name:
            self.formCassettePos.removeRow(4)
            self.formCassettePos.removeRow(3)
            if 'Apple' not in model_name:
                self.formCassettePos.removeRow(1)
                self.formCassettePos.removeRow(0)
        else:
            self.formCassettePos.removeRow(2)
        
        self.layout_group_h.addWidget(self.groupCassettePositions)

class ModelLayout(QVBoxLayout):
    def __init__(self,models_parameters,parent=None):
        super().__init__(parent)

        self.parameters = models_parameters

        self.layoutModelInput = QHBoxLayout() #nome da variavel indicar que e' horizontal

        self.labelModels = QLabel("Enter the model:")
        self.comboboxModels = QComboBox()
        self.comboboxModels.setPlaceholderText("Choose Model")
        self.comboboxModels.addItems(["",*self.parameters.keys()])
        #todo: testar depois so addItems(self.params.keys()), por causa do place holder text
        

        self.layoutModelInput.addWidget(self.labelModels)
        self.layoutModelInput.addWidget(self.comboboxModels)

        self.groups_dict = {}
        for model_name in self.parameters:
            self.groups_dict[model_name] = ModelGroupBox(model_name=model_name,
                                                         parent=parent,
                                                         **self.parameters[model_name])

        self.currentModelGroup = QGroupBox()


        self.widgetNaming = QWidget()
        
        self.layoutModelNaming = QHBoxLayout()
        
        self.labelModelNaming = QLabel("Name model label:")
        self.lineModelNaming = QLineEdit()
        

        self.layoutModelNaming.addWidget(self.labelModelNaming)
        self.layoutModelNaming.addWidget(self.lineModelNaming)

        self.widgetNaming.setLayout(self.layoutModelNaming)
        self.widgetNaming.setHidden(True)

        ## dialog button box - buttons
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        # dialog button box
        self.buttonBox = QDialogButtonBox(buttons)
        

        self.addLayout(self.layoutModelInput)
        for group in self.groups_dict.values():
            group.setHidden(True)
            self.addWidget(group)
        self.addWidget(self.widgetNaming)
        self.addWidget(self.buttonBox)



class NumericComboBox(QComboBox):
    def __init__(self, nums_list=[]):
        super().__init__()

        self.nums_list = nums_list

        if not nums_list:
            self.addItems(["None","Number"])
            self.setInsertPolicy(QComboBox.InsertPolicy.InsertAtCurrent)
            self.currentIndexChanged.connect(self.setItemEditable)
            self.currentTextChanged.connect(self.setTextNumber)
        else:
            self.addItems(["None"]+nums_list)
    
    def setItemEditable(self, index):
        if index==0:
            self.setEditable(False)
        elif index==1:
            self.setEditable(True)
            self.lineEdit().selectAll()

    def isTextNumeric(self, text):
        if "-" in text:
            abstext = text[1:]
        else:
            abstext = text
        if text=="None":
            return True
        return abstext.isdigit()

    def setTextNumber(self, text):
        if text=="Number" or (text!="None" and self.isTextNumeric(text)):
            self.setItemText(1,text)

    def setIndex(self, num):
        if isinstance(num, (int,float)):
            self.setCurrentIndex(num+1)

    def setItem(self, num):
        if num is not None:
            self.setCurrentIndex(1)
            self.setTextNumber(str(num))

    def setValue(self, val):
        if val is None:
            if not self.nums_list:
                self.setItemText(1,"Number")
            self.setCurrentIndex(0)
        else:
            self.setTextNumber(val)
            self.setCurrentIndex(1)

    def value(self):
        val = self.currentText()
        if val=="None":
            return None
        else:
            return int(val)



# fonts monospaced:
## cascadia code
## cascadia mono
## consolas
## courier
## lucida console
## MS alguma coisa
## OCR A
## System
## terminal

class MagneticFieldEditWidget(QWidget):

    def __init__(self, field_kwargs):
        super().__init__()

        x, y, z, nproc, chunksize = field_kwargs.values()

        line = [x,0,0,y,0,0,z]

        self.indexListChecked = -1
        if not isinstance(x, (int,float)):
            self.indexListChecked = 0
        elif not isinstance(y, (int, float)):
            self.indexListChecked = 3
        elif not isinstance(z, (int, float)):
            self.indexListChecked = 6

        vbox = QVBoxLayout(self)

        self.gridMagneticField = QGridLayout()
        self.gridMagneticField.setSpacing(0)

        label_get_field = QLabel("get_field")
        label_get_field.setFont(fontConsolas10)
        label_leftparenthesis = QLabel("(")
        label_leftparenthesis.setFont(fontConsolas14)
        label_leftparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        hbox_coords = QHBoxLayout()
        #todo: mudar listas abaixo para dicionarios
        self.radio_numbers = [0,0,0,3,0,0,6]
        self.radio_lists = [0,0,0,3,0,0,6]
        self.spins_coord = [0,0,0,3,0,0,6]
        self.spins_start = [0,0,0,3,0,0,6]
        self.spins_end = [0,0,0,3,0,0,6]
        self.spins_step = [0,0,0,3,0,0,6]
        for i, coord in [(0,"x"), (3,"y"), (6,"z")]:
            groupCoord = QGroupBox(title=f"{coord} coordinate")
            vboxCoord = QVBoxLayout(groupCoord)
            radioNumber = QRadioButton(text="Number")
            radioNumber.setSizePolicy(sizePreferred,sizeFixed)
            self.radio_numbers[i] = radioNumber
            radioList = QRadioButton(text="List")
            radioList.setSizePolicy(sizePreferred,sizeFixed)
            self.radio_lists[i] = radioList
            if i==self.indexListChecked:
                radioList.setChecked(True)
            else:
                radioNumber.setChecked(True)
            radioList.toggled.connect(self.toggleListNumber)
            vboxCoord.addWidget(radioNumber)
            vboxCoord.addWidget(radioList)
            hbox_coords.addWidget(groupCoord)

            label_coord = QLabel(f"{coord} = ")
            label_coord.setFont(fontConsolas10)
            label_start = QLabel("[start: ")
            label_start.setSizePolicy(sizeFixed,sizePreferred)
            label_start.setAlignment(alignRight|alignVCenter)
            label_start.setFont(fontConsolas8)
            label_end = QLabel("end: ")
            label_end.setFont(fontConsolas8)
            label_step = QLabel("step: ")
            label_step.setFont(fontConsolas8)

            spin_coord = QDoubleSpinBox()
            spin_coord.setMinimum(-10000)
            spin_coord.setMaximum(10000)
            spin_coord.setProperty("value",0)
            spin_coord.setSuffix(" mm")
            spin_coord.setSizePolicy(sizeFixed,sizeFixed)
            self.spins_coord[i] = spin_coord
            spin_start = QDoubleSpinBox()
            spin_start.setMinimum(-10000)
            spin_start.setMaximum(10000)
            spin_start.setProperty("value",0)
            spin_start.setSuffix(" mm")
            spin_start.setSizePolicy(sizeFixed,sizeFixed)
            self.spins_start[i] = spin_start
            spin_end = QDoubleSpinBox()
            spin_end.setMinimum(-10000)
            spin_end.setMaximum(10000)
            spin_end.setProperty("value",0)
            spin_end.setSuffix(" mm")
            self.spins_end[i] = spin_end
            spin_step = QDoubleSpinBox()
            spin_step.setMinimum(-10000)
            spin_step.setMaximum(10000)
            spin_step.setProperty("value",0)
            spin_step.setSingleStep(0.5)
            spin_step.setSuffix(" mm")
            self.spins_step[i] = spin_step

            label_comma_coord = QLabel(",")
            label_comma_coord.setFont(fontConsolas10)
            label_comma_end = QLabel(",")
            label_comma_end.setFont(fontConsolas10)
            label_rightbracket_step = QLabel("],")
            label_rightbracket_step.setFont(fontConsolas10)
            label_rightbracket_step.setSizePolicy(sizeFixed,sizePreferred)

            self.gridMagneticField.addWidget(label_coord,i,2,alignRight)
            self.gridMagneticField.addWidget(label_start,i,3)
            self.gridMagneticField.addWidget(spin_coord,i,4)
            self.gridMagneticField.addWidget(spin_start,i,4)
            self.gridMagneticField.addWidget(label_comma_coord,i,5)
            self.gridMagneticField.addWidget(label_end,i+1,3,alignRight)
            self.gridMagneticField.addWidget(spin_end,i+1,4)
            self.gridMagneticField.addWidget(label_comma_end,i+1,5)
            self.gridMagneticField.addWidget(label_step,i+2,3,alignRight)
            self.gridMagneticField.addWidget(spin_step,i+2,4)
            self.gridMagneticField.addWidget(label_rightbracket_step,i+2,5)

            if i==self.indexListChecked:
                spin_coord.setHidden(True)
                array = line[i]
                spin_start.setProperty("value", float(array[0]))
                spin_end.setProperty("value", float(array[-1]))
                spin_step.setProperty("value", float(array[1]-array[0]))
            else:
                label_start.setHidden(True)
                label_end.setHidden(True)
                label_step.setHidden(True)
                spin_start.setHidden(True)
                spin_end.setHidden(True)
                spin_step.setHidden(True)
                label_comma_end.setHidden(True)
                label_rightbracket_step.setHidden(True)
                spin_coord.setProperty("value",line[i])

        label_nproc = QLabel("nproc = ")
        label_nproc.setFont(fontConsolas10)
        label_comma_nproc = QLabel(",")
        label_comma_nproc.setFont(fontConsolas10)
        label_chunksize = QLabel("chunksize = ")
        label_chunksize.setFont(fontConsolas10)
        label_chunksize.setSizePolicy(sizeFixed,sizePreferred) #todo: fazer em todos params
        label_chunksize.setAlignment(alignRight|alignVCenter)

        self.combo_nproc = NumericComboBox()
        self.combo_nproc.setItem(nproc)

        self.spin_chunksize = QSpinBox()
        self.spin_chunksize.setMaximum(1000)
        self.spin_chunksize.setProperty("value",chunksize)

        label_rightparenthesis = QLabel(")")
        label_rightparenthesis.setFont(fontConsolas14)
        label_rightparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        self.gridMagneticField.addWidget(label_get_field,0,0,alignHCenter)
        self.gridMagneticField.addWidget(label_leftparenthesis,0,1)
        self.gridMagneticField.addWidget(label_nproc,9,2,alignRight)
        self.gridMagneticField.addWidget(self.combo_nproc,9,4)
        self.gridMagneticField.addWidget(label_comma_nproc,9,5)
        self.gridMagneticField.addWidget(label_chunksize,10,2)
        self.gridMagneticField.addWidget(self.spin_chunksize,10,4)
        self.gridMagneticField.addWidget(label_rightparenthesis,10,5)

        vbox.addLayout(hbox_coords)
        vbox.addLayout(self.gridMagneticField)

    def toggleListNumber(self, toList: bool):

        #indice da coordenada mudada
        currentListIdx = self.radio_lists.index(self.sender())
        #indice da coordenada que era lista previamente
        lastListIdx = self.indexListChecked

        self.spins_coord[currentListIdx].setHidden(toList)
        self.spins_start[currentListIdx].setHidden(not toList)
        for row in range(currentListIdx,currentListIdx+2+1):
            for col in [3,4,5]:
                if (row,col) not in [(currentListIdx,4),(currentListIdx,5)]:
                    item = self.gridMagneticField.itemAtPosition(row,col)
                    item.widget().setHidden(not toList)

        if toList and currentListIdx!=lastListIdx:
            if lastListIdx != -1:
                self.radio_numbers[lastListIdx].setChecked(True)
            self.indexListChecked = currentListIdx

    def set_values(self, values_dict):
        self.radio_lists[6].setChecked(True)
        
        self.spins_coord[0].setValue(values_dict["x"])
        self.spins_start[0].setValue(0)
        self.spins_end[0].setValue(0)
        self.spins_step[0].setValue(0)
        self.spins_coord[3].setValue(values_dict["y"])
        self.spins_start[3].setValue(0)
        self.spins_end[3].setValue(0)
        self.spins_step[3].setValue(0)
        self.spins_coord[6].setValue(0)
        self.spins_start[6].setValue(values_dict["z"][0])
        self.spins_end[6].setValue(values_dict["z"][-1])
        self.spins_step[6].setValue(values_dict["z"][1]-values_dict["z"][0])
        self.combo_nproc.setValue(None)
        self.spin_chunksize.setValue(values_dict["chunksize"])


    def get_values(self):
        x = self.spins_coord[0].value()
        y = self.spins_coord[3].value()
        z = self.spins_coord[6].value()
        if self.radio_lists[0].isChecked():
            x = np.arange(self.spins_start[0].value(),
                          self.spins_end[0].value()+self.spins_step[0].value(),
                          self.spins_step[0].value())
        elif self.radio_lists[3].isChecked():
            y = np.arange(self.spins_start[3].value(),
                          self.spins_end[3].value()+self.spins_step[3].value(),
                          self.spins_step[3].value())
        elif self.radio_lists[6].isChecked():
            z = np.arange(self.spins_start[6].value(),
                          self.spins_end[6].value()+self.spins_step[6].value(),
                          self.spins_step[6].value())
        nproc = self.combo_nproc.value()
        chunksize = self.spin_chunksize.value()

        return x, y, z, nproc, chunksize


class TrajectoryEditWidget(QWidget):

    def __init__(self, traj_kwargs):
        super().__init__()

        energy, r0, zmax, rkstep, dz, on_axis_field = traj_kwargs.values()

        gridTrajectory = QGridLayout(parent=self)
        gridTrajectory.setSpacing(0)

        label_calc_trajectory = QLabel("calc_trajectory")
        label_calc_trajectory.setFont(fontConsolas10)
        label_leftparenthesis = QLabel("(")
        label_leftparenthesis.setFont(fontConsolas14)
        label_leftparenthesis.setSizePolicy(sizeFixed,sizePreferred)
        
        label_energy = QLabel("energy = ")
        label_energy.setFont(fontConsolas10)
        label_x0     = QLabel("r0 = [x0 = ")
        label_x0.setFont(fontConsolas10)
        label_y0     = QLabel("y0 = ")
        label_y0.setFont(fontConsolas10)
        label_z0     = QLabel("z0 = ")
        label_z0.setFont(fontConsolas10)
        label_dxds0  = QLabel("dxds0 = ")
        label_dxds0.setFont(fontConsolas10)
        label_dyds0  = QLabel("dyds0 = ")
        label_dyds0.setFont(fontConsolas10)
        label_dzds0  = QLabel("dzds0 = ")
        label_dzds0.setFont(fontConsolas10)
        label_zmax   = QLabel("zmax = ")
        label_zmax.setFont(fontConsolas10)
        label_rkstep = QLabel("rkstep = ")
        label_rkstep.setFont(fontConsolas10)
        label_dz = QLabel("dz = ")
        label_dz.setFont(fontConsolas10)
        label_on_axis_field = QLabel("on_axis_field = ")
        label_on_axis_field.setFont(fontConsolas10)
        label_on_axis_field.setSizePolicy(sizeFixed,sizePreferred)
        label_on_axis_field.setAlignment(alignRight|alignVCenter)

        label_rightparenthesis = QLabel(")")
        label_rightparenthesis.setFont(fontConsolas14)
        label_rightparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        for row in [0,1,2,3,4,5,7,8,9]:
            label_comma = QLabel(",")
            label_comma.setFont(fontConsolas10)
            label_comma.setSizePolicy(sizeFixed,sizePreferred)
            gridTrajectory.addWidget(label_comma,row,4)
        label_rightbracket = QLabel("],")
        label_rightbracket.setFont(fontConsolas10)
        label_rightbracket.setSizePolicy(sizeFixed,sizePreferred)
        
        self.spin_energy = QDoubleSpinBox()
        self.spin_energy.setProperty("value",energy)
        self.spin_energy.setSuffix(" GeV")
        self.spin_x0 = QDoubleSpinBox()
        self.spin_x0.setMinimum(-10000)
        self.spin_x0.setMaximum(10000)
        self.spin_x0.setProperty("value",r0[0])
        self.spin_x0.setSuffix(" mm")
        self.spin_y0 = QDoubleSpinBox()
        self.spin_y0.setMinimum(-10000)
        self.spin_y0.setMaximum(10000)
        self.spin_y0.setProperty("value",r0[1])
        self.spin_y0.setSuffix(" mm")
        self.spin_z0 = QDoubleSpinBox()
        self.spin_z0.setMinimum(-10000)
        self.spin_z0.setMaximum(10000)
        self.spin_z0.setProperty("value",r0[2])
        self.spin_z0.setSuffix(" mm")
        self.spin_dxds0 = QDoubleSpinBox()
        self.spin_dxds0.setMinimum(-1.5)
        self.spin_dxds0.setMaximum(1.5)
        self.spin_dxds0.setProperty("value",r0[3])
        self.spin_dxds0.setSuffix(" rad")
        self.spin_dyds0 = QDoubleSpinBox()
        self.spin_dyds0.setMinimum(-1.5)
        self.spin_dyds0.setMaximum(1.5)
        self.spin_dyds0.setProperty("value",r0[4])
        self.spin_dyds0.setSuffix(" rad")
        self.spin_dzds0 = QDoubleSpinBox()
        self.spin_dzds0.setMinimum(-1.5)
        self.spin_dzds0.setMaximum(1.5)
        self.spin_dzds0.setProperty("value",r0[5])
        self.spin_dzds0.setSuffix(" rad")
        self.spin_zmax = QDoubleSpinBox()
        self.spin_zmax.setMinimum(-10000)
        self.spin_zmax.setMaximum(10000)
        self.spin_zmax.setProperty("value",zmax)
        self.spin_zmax.setSuffix(" mm")
        self.spin_zmax.setSizePolicy(sizeFixed,sizeFixed)
        self.spin_rkstep = QDoubleSpinBox()
        self.spin_rkstep.setProperty("value",rkstep)
        self.spin_rkstep.setSingleStep(0.5)
        self.spin_rkstep.setSuffix(" mm")
        self.spin_dz = QDoubleSpinBox()
        self.spin_dz.setProperty("value",dz)
        self.spin_dz.setSuffix(" mm")
        self.combo_on_axis_field = QComboBox()
        self.combo_on_axis_field.addItems(["False","True"])
        if on_axis_field is not False:
            self.combo_on_axis_field.setCurrentIndex(1)

        gridTrajectory.addWidget(label_calc_trajectory,0,0,alignHCenter)
        gridTrajectory.addWidget(label_leftparenthesis,0,1)
        gridTrajectory.addWidget(label_energy,0,2,alignRight)
        gridTrajectory.addWidget(self.spin_energy,0,3)
        gridTrajectory.addWidget(label_x0,1,2,alignRight)
        gridTrajectory.addWidget(self.spin_x0,1,3)
        gridTrajectory.addWidget(label_y0,2,2,alignRight)
        gridTrajectory.addWidget(self.spin_y0,2,3)
        gridTrajectory.addWidget(label_z0,3,2,alignRight)
        gridTrajectory.addWidget(self.spin_z0,3,3)
        gridTrajectory.addWidget(label_dxds0,4,2,alignRight)
        gridTrajectory.addWidget(self.spin_dxds0,4,3)
        gridTrajectory.addWidget(label_dyds0,5,2,alignRight)
        gridTrajectory.addWidget(self.spin_dyds0,5,3)
        gridTrajectory.addWidget(label_dzds0,6,2,alignRight)
        gridTrajectory.addWidget(self.spin_dzds0,6,3)
        gridTrajectory.addWidget(label_rightbracket,6,4)
        gridTrajectory.addWidget(label_zmax,7,2,alignRight)
        gridTrajectory.addWidget(self.spin_zmax,7,3)
        gridTrajectory.addWidget(label_rkstep,8,2,alignRight)
        gridTrajectory.addWidget(self.spin_rkstep,8,3)
        gridTrajectory.addWidget(label_dz,9,2,alignRight)
        gridTrajectory.addWidget(self.spin_dz,9,3)
        gridTrajectory.addWidget(label_on_axis_field,10,2)
        gridTrajectory.addWidget(self.combo_on_axis_field,10,3)
        gridTrajectory.addWidget(label_rightparenthesis,10,4)


    def set_values(self, values_dict):
        self.spin_energy.setValue(values_dict["energy"])
        self.spin_x0.setValue(values_dict["r0"][0])
        self.spin_y0.setValue(values_dict["r0"][1])
        self.spin_z0.setValue(values_dict["r0"][2])
        self.spin_dxds0.setValue(values_dict["r0"][3])
        self.spin_dyds0.setValue(values_dict["r0"][4])
        self.spin_dzds0.setValue(values_dict["r0"][5])
        self.spin_zmax.setValue(values_dict["zmax"])
        self.spin_rkstep.setValue(values_dict["rkstep"])
        self.spin_dz.setValue(values_dict["dz"])
        self.combo_on_axis_field.setCurrentIndex(0)

    def get_values(self):
        energy = self.spin_energy.value()
        r0 = [self.spin_x0.value(),
                self.spin_y0.value(),
                self.spin_z0.value(),
                self.spin_dxds0.value(),
                self.spin_dyds0.value(),
                self.spin_dzds0.value()]
        zmax = self.spin_zmax.value()
        rkstep = self.spin_rkstep.value()
        dz = self.spin_dz.value()
        on_axis_field = self.combo_on_axis_field.currentText()
        if on_axis_field=="True":
            on_axis_field = True
        else:
            on_axis_field = False
        
        return energy, r0, zmax, rkstep, dz, on_axis_field


class PhaseErrorEditWidget(QWidget):
    def __init__(self, phaserr_kwargs):
        super().__init__()

        energy, *_, skip_poles, zmin, zmax, field_comp = phaserr_kwargs.values()

        gridPhaseError = QGridLayout(parent=self)
        gridPhaseError.setSpacing(0)

        label_calc_phase_error = QLabel("calc_phase_error")
        label_calc_phase_error.setFont(fontConsolas10)
        label_leftparenthesis = QLabel("(")
        label_leftparenthesis.setFont(fontConsolas14)
        label_leftparenthesis.setSizePolicy(sizeFixed,sizePreferred)
        
        label_energy = QLabel("energy = ")
        label_energy.setFont(fontConsolas10)
        label_trajectory = QLabel("trajectory = ")
        label_trajectory.setFont(fontConsolas10)
        label_bx_amp = QLabel("bx_amp = ")
        label_bx_amp.setFont(fontConsolas10)
        label_by_amp = QLabel("by_amp = ")
        label_by_amp.setFont(fontConsolas10)
        label_skip_poles = QLabel("skip_poles = ")
        label_skip_poles.setFont(fontConsolas10)
        label_zmin = QLabel("zmin = ")
        label_zmin.setFont(fontConsolas10)
        label_zmax = QLabel("zmax = ")
        label_zmax.setFont(fontConsolas10)
        label_field_comp = QLabel("field_comp = ")
        label_field_comp.setFont(fontConsolas10)
        label_field_comp.setSizePolicy(sizeFixed,sizePreferred)
        label_field_comp.setAlignment(alignRight|alignVCenter)

        for row in [0,1,2,3,4,5,6]:
            label_comma = QLabel(",")
            label_comma.setFont(fontConsolas10)
            label_comma.setSizePolicy(sizeFixed,sizePreferred)
            gridPhaseError.addWidget(label_comma,row,4)

        self.spin_energy = QDoubleSpinBox()
        self.spin_energy.setProperty("value",energy)
        self.spin_energy.setSuffix(" GeV")
        self.spin_energy.setSizePolicy(sizeFixed,sizeFixed)
        label_trajectory_value = QLabel("calculated")
        label_trajectory_value.setFont(fontConsolas8)
        label_trajectory_value.setSizePolicy(sizePreferred,sizeFixed)
        label_bx_amp_value = QLabel("calculated")
        label_bx_amp_value.setFont(fontConsolas8)
        label_bx_amp_value.setSizePolicy(sizePreferred,sizeFixed)
        label_by_amp_value = QLabel("calculated")
        label_by_amp_value.setFont(fontConsolas8)
        label_by_amp_value.setSizePolicy(sizePreferred,sizeFixed)
        self.spin_skip_poles = QSpinBox()
        self.spin_skip_poles.setProperty("value",skip_poles)
        self.combo_zmin = NumericComboBox()
        self.combo_zmin.setItem(zmin)
        self.combo_zmax = NumericComboBox()
        self.combo_zmax.setItem(zmax)
        self.combo_field_comp = NumericComboBox(nums_list=["0","1"])
        self.combo_field_comp.setIndex(field_comp)

        label_rightparenthesis = QLabel(")")
        label_rightparenthesis.setFont(fontConsolas14)
        label_rightparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        gridPhaseError.addWidget(label_calc_phase_error,0,0,alignHCenter)
        gridPhaseError.addWidget(label_leftparenthesis,0,1)
        gridPhaseError.addWidget(label_energy,0,2,alignRight)
        gridPhaseError.addWidget(self.spin_energy,0,3)
        gridPhaseError.addWidget(label_trajectory,1,2,alignRight)
        gridPhaseError.addWidget(label_trajectory_value,1,3,alignHCenter)
        gridPhaseError.addWidget(label_bx_amp,2,2,alignRight)
        gridPhaseError.addWidget(label_bx_amp_value,2,3,alignHCenter)
        gridPhaseError.addWidget(label_by_amp,3,2,alignRight)
        gridPhaseError.addWidget(label_by_amp_value,3,3,alignHCenter)
        gridPhaseError.addWidget(label_skip_poles,4,2,alignRight)
        gridPhaseError.addWidget(self.spin_skip_poles,4,3)
        gridPhaseError.addWidget(label_zmin,5,2,alignRight)
        gridPhaseError.addWidget(self.combo_zmin,5,3)
        gridPhaseError.addWidget(label_zmax,6,2,alignRight)
        gridPhaseError.addWidget(self.combo_zmax,6,3)
        gridPhaseError.addWidget(label_field_comp,7,2)
        gridPhaseError.addWidget(self.combo_field_comp,7,3)
        gridPhaseError.addWidget(label_rightparenthesis,7,4)

    def set_values(self, values_dict):
        self.spin_energy.setValue(values_dict["energy"])
        self.spin_skip_poles.setValue(values_dict["skip_poles"])
        self.combo_zmin.setValue(values_dict["zmin"])
        self.combo_zmax.setValue(values_dict["zmax"])
        self.combo_field_comp.setValue(values_dict["field_comp"])

    def get_values(self):
        energy = self.spin_energy.value()
        skip_poles = self.spin_skip_poles.value()
        zmin = self.combo_zmin.value()
        zmax = self.combo_zmax.value()
        field_comp = self.combo_field_comp.value()

        return energy, skip_poles, zmin, zmax, field_comp
        
#todo: alterar integrals, vai definir os parametros e jogar para calcMagField
#todo: realmente vai ter que duplicar o get_field
class IntegralsEditWidget(QWidget):

    def __init__(self, integrals_kwargs):
        super().__init__()
        
        z_list, x, y, field_list, nproc, chunksize = integrals_kwargs.values()

        gridIntegrals = QGridLayout(parent=self)
        gridIntegrals.setSpacing(0)

        label_calc_phase_error = QLabel("calc_field_integrals")
        label_calc_phase_error.setFont(fontConsolas10)
        label_leftparenthesis = QLabel("(")
        label_leftparenthesis.setFont(fontConsolas14)
        label_leftparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        label_z_list = QLabel("z_list = ")
        label_z_list.setFont(fontConsolas10)
        label_x = QLabel("x = ")
        label_x.setFont(fontConsolas10)
        label_y = QLabel("y = ")
        label_y.setFont(fontConsolas10)
        label_field_list = QLabel("field_list = ")
        label_field_list.setFont(fontConsolas10)
        label_field_list.setSizePolicy(sizeFixed,sizePreferred)
        label_field_list.setAlignment(alignRight|alignVCenter)
        label_field_list_start = QLabel("[start: ")
        label_field_list_start.setFont(fontConsolas8)
        label_field_list_start.setSizePolicy(sizeFixed,sizePreferred)
        label_field_list_start.setAlignment(alignRight|alignVCenter)
        label_field_list_end = QLabel("end: ")
        label_field_list_end.setFont(fontConsolas8)
        label_field_list_step = QLabel("step: ")
        label_field_list_step.setFont(fontConsolas8)
        label_nproc = QLabel("nproc = ")
        label_nproc.setFont(fontConsolas10)
        label_chunksize = QLabel("chunksize = ")
        label_chunksize.setFont(fontConsolas10)


        for row in [0,1,3,4,5,6]:
            label_comma = QLabel(",")
            label_comma.setFont(fontConsolas10)
            label_comma.setSizePolicy(sizeFixed,sizePreferred)
            gridIntegrals.addWidget(label_comma,row,5)
        label_rightbracket = QLabel("],")
        label_rightbracket.setFont(fontConsolas10)
        label_rightbracket.setSizePolicy(sizeFixed,sizePreferred)
        gridIntegrals.addWidget(label_rightbracket,2,5)
        
        self.spin_z_list_start = QDoubleSpinBox()
        self.spin_z_list_start.setMinimum(-10000)
        self.spin_z_list_start.setMaximum(10000)
        self.spin_z_list_start.setSuffix(" mm")
        self.spin_z_list_start.setProperty("value",float(z_list[0]))
        self.spin_z_list_start.setSizePolicy(sizeFixed,sizeFixed)
        self.spin_z_list_end = QDoubleSpinBox()
        self.spin_z_list_end.setMinimum(-10000)
        self.spin_z_list_end.setMaximum(10000)
        self.spin_z_list_end.setSuffix(" mm")
        self.spin_z_list_end.setProperty("value",float(z_list[-1]))
        self.spin_z_list_step = QDoubleSpinBox()
        self.spin_z_list_step.setMinimum(-100)
        self.spin_z_list_step.setMaximum(100)
        self.spin_z_list_step.setSuffix(" mm")
        self.spin_z_list_step.setProperty("value",float(z_list[1]-z_list[0]))
        self.spin_z_list_step.setSingleStep(0.5)
        self.spin_x = QDoubleSpinBox()
        self.spin_x.setSuffix(" mm")
        self.spin_x.setProperty("value",x)
        self.spin_y = QDoubleSpinBox()
        self.spin_y.setMinimum(-100)
        self.spin_y.setMaximum(100)
        self.spin_y.setSuffix(" mm")
        self.spin_y.setProperty("value",y)
        label_field_list_value = QLabel("None")
        label_field_list_value.setSizePolicy(sizePreferred,sizeFixed)
        label_field_list_value.setContentsMargins(4,3,0,3)
        self.combo_nproc = NumericComboBox()
        self.combo_nproc.setItem(nproc)
        self.spin_chunksize = QSpinBox()
        self.spin_chunksize.setMaximum(1000)
        self.spin_chunksize.setProperty("value",chunksize)
        

        label_rightparenthesis = QLabel(")")
        label_rightparenthesis.setFont(fontConsolas14)

        gridIntegrals.addWidget(label_calc_phase_error,0,0,alignCenter)
        gridIntegrals.addWidget(label_leftparenthesis,0,1)
        gridIntegrals.addWidget(label_z_list,0,2,alignRight)
        gridIntegrals.addWidget(label_field_list_start,0,3)
        gridIntegrals.addWidget(self.spin_z_list_start,0,4)
        gridIntegrals.addWidget(label_field_list_end,1,3,alignRight)
        gridIntegrals.addWidget(self.spin_z_list_end,1,4)
        gridIntegrals.addWidget(label_field_list_step,2,3,alignRight)
        gridIntegrals.addWidget(self.spin_z_list_step,2,4)
        gridIntegrals.addWidget(label_x,3,2,alignRight)
        gridIntegrals.addWidget(self.spin_x,3,4)
        gridIntegrals.addWidget(label_y,4,2,alignRight)
        gridIntegrals.addWidget(self.spin_y,4,4)
        gridIntegrals.addWidget(label_field_list,5,2)
        gridIntegrals.addWidget(label_field_list_value,5,4)
        gridIntegrals.addWidget(label_nproc,6,2,alignRight)
        gridIntegrals.addWidget(self.combo_nproc,6,4)
        gridIntegrals.addWidget(label_chunksize,7,2,alignRight)
        gridIntegrals.addWidget(self.spin_chunksize,7,4)
        gridIntegrals.addWidget(label_rightparenthesis,7,5)
    
    def set_values(self, values_dict):
        self.spin_z_list_start.setValue(values_dict["z_list"][0])
        self.spin_z_list_end.setValue(values_dict["z_list"][-1])
        self.spin_z_list_step.setValue(values_dict["z_list"][1]-values_dict["z_list"][0])
        self.spin_x.setValue(values_dict["x"])
        self.spin_y.setValue(values_dict["y"])
        self.combo_nproc.setValue(values_dict["nproc"])
        self.spin_chunksize.setValue(values_dict["chunksize"])

    def get_values(self):
        z_list = np.arange(self.spin_z_list_start.value(),
                           self.spin_z_list_end.value()+self.spin_z_list_step.value(),
                           self.spin_z_list_step.value())
        x = self.spin_x.value()
        y = self.spin_y.value()
        nproc = self.combo_nproc.value()
        chunksize = self.spin_chunksize.value()

        return z_list, x, y, nproc, chunksize



class RollOffPeaksEditWidget(QWidget):

    def __init__(self, rop_kwargs):
        super().__init__()

        z, x, y, field_comp = rop_kwargs.values()

        gridRollOffPeaks = QGridLayout(parent=self)
        gridRollOffPeaks.setSpacing(0)

        label_calc_roll_off_peaks = QLabel("calc_roll_off_peaks")
        label_calc_roll_off_peaks.setFont(fontConsolas10)
        label_leftparenthesis = QLabel("(")
        label_leftparenthesis.setFont(fontConsolas14)
        label_leftparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        label_z = QLabel("z = ")
        label_z.setFont(fontConsolas10)
        label_x = QLabel("x = ")
        label_x.setFont(fontConsolas10)
        label_y = QLabel("y = ")
        label_y.setFont(fontConsolas10)
        label_field_comp = QLabel("field_comp = ")
        label_field_comp.setFont(fontConsolas10)
        label_field_comp.setSizePolicy(sizeFixed,sizePreferred)
        label_field_comp.setAlignment(alignRight|alignVCenter)

        label_zstart = QLabel("[start: ")
        label_zstart.setFont(fontConsolas8)
        label_zstart.setSizePolicy(sizeFixed,sizePreferred)
        label_zstart.setAlignment(alignRight|alignVCenter)
        label_zend = QLabel("end: ")
        label_zend.setFont(fontConsolas8)
        label_zstep = QLabel("step: ")
        label_zstep.setFont(fontConsolas8)
        label_xstart = QLabel("[start: ")
        label_xstart.setFont(fontConsolas8)
        label_xend = QLabel("end: ")
        label_xend.setFont(fontConsolas8)
        label_xstep = QLabel("step: ")
        label_xstep.setFont(fontConsolas8)

        self.spin_zstart = QDoubleSpinBox()
        self.spin_zstart.setMinimum(-10000)
        self.spin_zstart.setMaximum(10000)
        self.spin_zstart.setSuffix(" mm")
        self.spin_zstart.setProperty("value",float(z[0]))
        self.spin_zstart.setSizePolicy(sizeFixed,sizeFixed)
        self.spin_zend = QDoubleSpinBox()
        self.spin_zend.setMinimum(-10000)
        self.spin_zend.setMaximum(10000)
        self.spin_zend.setSuffix(" mm")
        self.spin_zend.setProperty("value",float(z[-1]))
        self.spin_zstep = QDoubleSpinBox()
        self.spin_zstep.setMinimum(-100)
        self.spin_zstep.setMaximum(100)
        self.spin_zstep.setSuffix(" mm")
        self.spin_zstep.setProperty("value",float(z[1]-z[0]))
        self.spin_zstep.setSingleStep(0.5)
        self.spin_xstart = QDoubleSpinBox()
        self.spin_xstart.setMinimum(-10000)
        self.spin_xstart.setMaximum(10000)
        self.spin_xstart.setSuffix(" mm")
        self.spin_xstart.setProperty("value",float(x[0]))
        self.spin_xend = QDoubleSpinBox()
        self.spin_xend.setMinimum(-10000)
        self.spin_xend.setMaximum(10000)
        self.spin_xend.setSuffix(" mm")
        self.spin_xend.setProperty("value",float(x[-1]))
        self.spin_xstep = QDoubleSpinBox()
        self.spin_xstep.setMinimum(-100)
        self.spin_xstep.setMaximum(100)
        self.spin_xstep.setSuffix(" mm")
        self.spin_xstep.setProperty("value",float(x[1]-x[0]))
        self.spin_xstep.setSingleStep(0.5)
        self.spin_y = QDoubleSpinBox()
        self.spin_y.setMinimum(-1000)
        self.spin_y.setMaximum(1000)
        self.spin_y.setSuffix(" mm")
        self.spin_y.setProperty("value",y)
        self.combo_field_comp = NumericComboBox(nums_list=["0","1"])
        self.combo_field_comp.setIndex(field_comp)

        for row in [0,1,3,4,6]:
            label_comma = QLabel(",")
            label_comma.setFont(fontConsolas10)
            label_comma.setSizePolicy(sizeFixed,sizePreferred)
            gridRollOffPeaks.addWidget(label_comma,row,5)
        label_zrightbracket = QLabel("],")
        label_zrightbracket.setFont(fontConsolas10)
        label_xrightbracket = QLabel("],")
        label_xrightbracket.setFont(fontConsolas10)

        label_rightparenthesis = QLabel(")")
        label_rightparenthesis.setFont(fontConsolas14)
        label_rightparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        gridRollOffPeaks.addWidget(label_calc_roll_off_peaks,0,0,alignHCenter)
        gridRollOffPeaks.addWidget(label_leftparenthesis,0,1)
        gridRollOffPeaks.addWidget(label_z,0,2,alignRight)
        gridRollOffPeaks.addWidget(label_zstart,0,3)
        gridRollOffPeaks.addWidget(self.spin_zstart,0,4)
        gridRollOffPeaks.addWidget(label_zend,1,3,alignRight)
        gridRollOffPeaks.addWidget(self.spin_zend,1,4)
        gridRollOffPeaks.addWidget(label_zstep,2,3,alignRight)
        gridRollOffPeaks.addWidget(self.spin_zstep,2,4)
        gridRollOffPeaks.addWidget(label_zrightbracket,2,5)
        gridRollOffPeaks.addWidget(label_x,3,2,alignRight)
        gridRollOffPeaks.addWidget(label_xstart,3,3,alignRight)
        gridRollOffPeaks.addWidget(self.spin_xstart,3,4)
        gridRollOffPeaks.addWidget(label_xend,4,3,alignRight)
        gridRollOffPeaks.addWidget(self.spin_xend,4,4)
        gridRollOffPeaks.addWidget(label_xstep,5,3,alignRight)
        gridRollOffPeaks.addWidget(self.spin_xstep,5,4)
        gridRollOffPeaks.addWidget(label_xrightbracket,5,5)
        gridRollOffPeaks.addWidget(label_y,6,2,alignRight)
        gridRollOffPeaks.addWidget(self.spin_y,6,4)
        gridRollOffPeaks.addWidget(label_field_comp,7,2)
        gridRollOffPeaks.addWidget(self.combo_field_comp,7,4)
        gridRollOffPeaks.addWidget(label_rightparenthesis,7,5)

    def set_values(self, values_dict):
        self.spin_zstart.setValue(values_dict["z"][0])
        self.spin_zend.setValue(values_dict["z"][-1])
        self.spin_zstep.setValue(values_dict["z"][1]-values_dict["z"][0])
        self.spin_xstart.setValue(values_dict["x"][0])
        self.spin_xend.setValue(values_dict["x"][-1])
        self.spin_xstep.setValue(values_dict["x"][1]-values_dict["x"][0])
        self.spin_y.setValue(values_dict["y"])
        self.combo_field_comp.setValue(values_dict["field_comp"])

    def get_values(self):
        z = np.arange(self.spin_zstart.value(),
                      self.spin_zend.value()+self.spin_zstep.value(),
                      self.spin_zstep.value())
        x = np.arange(self.spin_xstart.value(),
                      self.spin_xend.value()+self.spin_xstep.value(),
                      self.spin_xstep.value())
        y = self.spin_y.value()
        field_comp = self.combo_field_comp.value()

        return z, x, y, field_comp


class RollOffAmpEditWidget(QWidget):

    def __init__(self, roa_kwargs):
        super().__init__()

        z, x, y = roa_kwargs.values()

        gridRollOffAmp = QGridLayout(parent=self)
        gridRollOffAmp.setSpacing(0)

        label_calc_roll_off_amplitude = QLabel("calc_roll_off_amplitude")
        label_calc_roll_off_amplitude.setFont(fontConsolas10)
        label_leftparenthesis = QLabel("(")
        label_leftparenthesis.setFont(fontConsolas14)
        label_leftparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        label_z = QLabel("z = ")
        label_z.setFont(fontConsolas10)
        label_x = QLabel("x = ")
        label_x.setFont(fontConsolas10)
        label_y = QLabel("y = ")
        label_y.setFont(fontConsolas10)

        label_zstart = QLabel("[start: ")
        label_zstart.setFont(fontConsolas8)
        label_zstart.setSizePolicy(sizeFixed,sizePreferred)
        label_zstart.setAlignment(alignRight|alignVCenter)
        label_zend = QLabel("end: ")
        label_zend.setFont(fontConsolas8)
        label_zstep = QLabel("step: ")
        label_zstep.setFont(fontConsolas8)
        label_xstart = QLabel("[start: ")
        label_xstart.setFont(fontConsolas8)
        label_xend = QLabel("end: ")
        label_xend.setFont(fontConsolas8)
        label_xstep = QLabel("step: ")
        label_xstep.setFont(fontConsolas8)

        self.spin_zstart = QDoubleSpinBox()
        self.spin_zstart.setMinimum(-10000)
        self.spin_zstart.setMaximum(10000)
        self.spin_zstart.setSuffix(" mm")
        self.spin_zstart.setProperty("value",float(z[0]))
        self.spin_zstart.setSizePolicy(sizeFixed,sizeFixed)
        self.spin_zend = QDoubleSpinBox()
        self.spin_zend.setMinimum(-10000)
        self.spin_zend.setMaximum(10000)
        self.spin_zend.setSuffix(" mm")
        self.spin_zend.setProperty("value",float(z[-1]))
        self.spin_zstep = QDoubleSpinBox()
        self.spin_zstep.setMinimum(-100)
        self.spin_zstep.setMaximum(100)
        self.spin_zstep.setSuffix(" mm")
        self.spin_zstep.setProperty("value",float(z[1]-z[0]))
        self.spin_zstep.setSingleStep(0.5)
        self.spin_xstart = QDoubleSpinBox()
        self.spin_xstart.setMinimum(-10000)
        self.spin_xstart.setMaximum(10000)
        self.spin_xstart.setSuffix(" mm")
        self.spin_xstart.setProperty("value",float(x[0]))
        self.spin_xend = QDoubleSpinBox()
        self.spin_xend.setMinimum(-10000)
        self.spin_xend.setMaximum(10000)
        self.spin_xend.setSuffix(" mm")
        self.spin_xend.setProperty("value",float(x[-1]))
        self.spin_xstep = QDoubleSpinBox()
        self.spin_xstep.setMinimum(-100)
        self.spin_xstep.setMaximum(100)
        self.spin_xstep.setSuffix(" mm")
        self.spin_xstep.setProperty("value",float(x[1]-x[0]))
        self.spin_xstep.setSingleStep(0.5)
        self.spin_y = QDoubleSpinBox()
        self.spin_y.setMinimum(-10000)
        self.spin_y.setMaximum(10000)
        self.spin_y.setSuffix(" mm")
        self.spin_y.setProperty("value",y)

        for row in [0,1,3,4]:
            label_comma = QLabel(",")
            label_comma.setFont(fontConsolas10)
            label_comma.setSizePolicy(sizeFixed,sizePreferred)
            gridRollOffAmp.addWidget(label_comma,row,5)
        label_zrightbracket = QLabel("],")
        label_zrightbracket.setFont(fontConsolas10)
        label_xrightbracket = QLabel("],")
        label_xrightbracket.setFont(fontConsolas10)

        label_rightparenthesis = QLabel(")")
        label_rightparenthesis.setFont(fontConsolas14)
        label_rightparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        gridRollOffAmp.addWidget(label_calc_roll_off_amplitude,0,0,alignHCenter)
        gridRollOffAmp.addWidget(label_leftparenthesis,0,1)
        gridRollOffAmp.addWidget(label_z,0,2,alignRight)
        gridRollOffAmp.addWidget(label_zstart,0,3)
        gridRollOffAmp.addWidget(self.spin_zstart,0,4)
        gridRollOffAmp.addWidget(label_zend,1,3,alignRight)
        gridRollOffAmp.addWidget(self.spin_zend,1,4)
        gridRollOffAmp.addWidget(label_zstep,2,3,alignRight)
        gridRollOffAmp.addWidget(self.spin_zstep,2,4)
        gridRollOffAmp.addWidget(label_zrightbracket,2,5)
        gridRollOffAmp.addWidget(label_x,3,2,alignRight)
        gridRollOffAmp.addWidget(label_xstart,3,3,alignRight)
        gridRollOffAmp.addWidget(self.spin_xstart,3,4)
        gridRollOffAmp.addWidget(label_xend,4,3,alignRight)
        gridRollOffAmp.addWidget(self.spin_xend,4,4)
        gridRollOffAmp.addWidget(label_xstep,5,3,alignRight)
        gridRollOffAmp.addWidget(self.spin_xstep,5,4)
        gridRollOffAmp.addWidget(label_xrightbracket,5,5)
        gridRollOffAmp.addWidget(label_y,6,2,alignRight)
        gridRollOffAmp.addWidget(self.spin_y,6,4)
        gridRollOffAmp.addWidget(label_rightparenthesis,6,5)

    def set_values(self, values_dict):
        self.spin_zstart.setValue(values_dict["z"][0])
        self.spin_zend.setValue(values_dict["z"][-1])
        self.spin_zstep.setValue(values_dict["z"][1]-values_dict["z"][0])
        self.spin_xstart.setValue(values_dict["x"][0])
        self.spin_xend.setValue(values_dict["x"][-1])
        self.spin_xstep.setValue(values_dict["x"][1]-values_dict["x"][0])
        self.spin_y.setValue(values_dict["y"])

    def get_values(self):
        z = np.arange(self.spin_zstart.value(),
                      self.spin_zend.value()+self.spin_zstep.value(),
                      self.spin_zstep.value())
        x = np.arange(self.spin_xstart.value(),
                      self.spin_xend.value()+self.spin_xstep.value(),
                      self.spin_xstep.value())
        y = self.spin_y.value()

        return z, x, y






class AnalysisLayout(QVBoxLayout):
    def __init__(self, params_kwargs, parent=None):
        super().__init__(parent)

        tabs = VerticalTabWidget()

        self.editMagneticField = MagneticFieldEditWidget(params_kwargs["Magnetic Field"])
        self.editTrajectory = TrajectoryEditWidget(params_kwargs["Trajectory"])
        self.editPhaseError = PhaseErrorEditWidget(params_kwargs["Phase Error"])
        self.editIntegrals = IntegralsEditWidget(params_kwargs["Field Integrals"])
        self.editRollOffPeaks = RollOffPeaksEditWidget(params_kwargs["Roll Off Peaks"])
        self.editRollOffAmp = RollOffAmpEditWidget(params_kwargs["Roll Off Amplitude"])

        tabs.addTab(self.editMagneticField, "Edit Magnetic Field")
        tabs.addTab(self.editTrajectory, "Edit Trajectory")
        tabs.addTab(self.editPhaseError, "Edit Phase Error")
        tabs.addTab(self.editIntegrals, "Edit Field Integrals")
        tabs.addTab(self.editRollOffPeaks, "Edit Roll Off Peaks")
        tabs.addTab(self.editRollOffAmp, "Edit Roll Off Amplitude")


        # botoes a serem usados
        stdButtonOk = QDialogButtonBox.StandardButton.Ok
        stdButtonCancel = QDialogButtonBox.StandardButton.Cancel
        stdButtonRestore = QDialogButtonBox.StandardButton.RestoreDefaults
        stdButtons = stdButtonOk|stdButtonCancel|stdButtonRestore
        
        # criando os botoes
        self.buttonBox = QDialogButtonBox(stdButtons)
        

        self.addWidget(tabs)
        self.addWidget(self.buttonBox)