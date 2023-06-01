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
                             QRadioButton)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


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
    def __init__(self):
        super().__init__()

        self.addItems(["None","Number"])
        self.setInsertPolicy(QComboBox.InsertPolicy.InsertAtCurrent)
        self.currentIndexChanged.connect(self.setItemEditable)
        self.currentTextChanged.connect(self.setNumber)
    
    def setItemEditable(self, index):
        if index==0:
            self.setEditable(False)
        elif index==1:
            self.setEditable(True)
            self.lineEdit().selectAll()
    
    def setNumber(self, text):
        if text!="None" and text.isdigit():
            self.setItemText(1,text)


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

class MagneticFieldGroupBox(QGroupBox):

    def __init__(self):
        super().__init__(title="Magnetic Field")

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
        for i, coord in [(0,"x"), (3,"y"), (6,"z")]:
            groupCoord = QGroupBox(title=f"{coord} coordinate")
            vboxCoord = QVBoxLayout(groupCoord)
            radioNumber = QRadioButton(text="Number")
            self.radio_numbers[i] = radioNumber
            radioList = QRadioButton(text="List")
            self.radio_lists[i] = radioList
            if coord=="z":
                radioList.setChecked(True)
                self.indexListChecked = 6
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
            spin_coord.setProperty("value",0)
            spin_coord.setSuffix(" mm")
            spin_coord.setSizePolicy(sizeFixed,sizeFixed)
            self.spins_coord[i] = spin_coord
            spin_start = QDoubleSpinBox()
            spin_start.setProperty("value",0)
            spin_start.setSuffix(" mm")
            spin_start.setSizePolicy(sizeFixed,sizeFixed)
            self.spins_start[i] = spin_start
            spin_end = QDoubleSpinBox()
            spin_end.setProperty("value",0)
            spin_end.setSuffix(" mm")
            spin_step = QDoubleSpinBox()
            spin_step.setProperty("value",0)
            spin_step.setSuffix(" mm")

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

            if coord!="z":
                label_start.setHidden(True)
                label_end.setHidden(True)
                label_step.setHidden(True)
                spin_start.setHidden(True)
                spin_end.setHidden(True)
                spin_step.setHidden(True)
                label_comma_end.setHidden(True)
                label_rightbracket_step.setHidden(True)

        label_nproc = QLabel("nproc = ")
        label_nproc.setFont(fontConsolas10)
        label_comma_nproc = QLabel(",")
        label_comma_nproc.setFont(fontConsolas10)
        label_chunksize = QLabel("chunksize = ")
        label_chunksize.setFont(fontConsolas10)
        label_chunksize.setSizePolicy(sizeFixed,sizePreferred) #todo: fazer em todos params
        label_chunksize.setAlignment(alignRight|alignVCenter)

        self.combo_nproc = NumericComboBox()
        spin_chunksize = QSpinBox()
        spin_chunksize.setMaximum(1000)
        spin_chunksize.setProperty("value",100)

        label_rightparenthesis = QLabel(")")
        label_rightparenthesis.setFont(fontConsolas14)
        label_rightparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        self.gridMagneticField.addWidget(label_get_field,0,0,alignHCenter)
        self.gridMagneticField.addWidget(label_leftparenthesis,0,1)
        self.gridMagneticField.addWidget(label_nproc,9,2,alignRight)
        self.gridMagneticField.addWidget(self.combo_nproc,9,4)
        self.gridMagneticField.addWidget(label_comma_nproc,9,5)
        self.gridMagneticField.addWidget(label_chunksize,10,2)
        self.gridMagneticField.addWidget(spin_chunksize,10,4)
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
            self.radio_numbers[lastListIdx].setChecked(True)
            self.indexListChecked = currentListIdx


class TrajectoryGroupBox(QGroupBox):

    def __init__(self):
        super().__init__(title="Trajectory")

        gridTrajectory = QGridLayout(parent=self)
        gridTrajectory.setSpacing(0)

        label_calc_trajectory = QLabel("calc_trajectory")
        label_calc_trajectory.setFont(fontConsolas10)
        label_leftparenthesis = QLabel("(")
        label_leftparenthesis.setFont(fontConsolas14)
        label_leftparenthesis.setSizePolicy(sizeFixed,sizePreferred)
        
        label_energy = QLabel("energy = ")
        label_energy.setFont(fontConsolas10)
        label_energy.setSizePolicy(sizeFixed,sizePreferred)
        label_energy.setAlignment(alignRight|alignVCenter)
        label_x0     = QLabel("[x0 = ")
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

        label_rightparenthesis = QLabel(")")
        label_rightparenthesis.setFont(fontConsolas14)
        label_rightparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        for row in [0,1,2,3,4,5,7]:
            label_comma = QLabel(",")
            label_comma.setFont(fontConsolas10)
            label_comma.setSizePolicy(sizeFixed,sizePreferred)
            gridTrajectory.addWidget(label_comma,row,4)
        label_rightbracket = QLabel("],")
        label_rightbracket.setFont(fontConsolas10)
        label_rightbracket.setSizePolicy(sizeFixed,sizePreferred)
        
        spin_energy = QDoubleSpinBox()
        spin_energy.setProperty("value",3.00)
        spin_energy.setSuffix(" GeV")
        spin_x0 = QDoubleSpinBox()
        spin_x0.setMinimum(-10000)
        spin_x0.setMaximum(10000)
        spin_x0.setProperty("value",-900)
        spin_x0.setSuffix(" mm")
        spin_y0 = QDoubleSpinBox()
        spin_y0.setMinimum(-10000)
        spin_y0.setMaximum(10000)
        spin_y0.setSuffix(" mm")
        spin_z0 = QDoubleSpinBox()
        spin_z0.setMinimum(-10000)
        spin_z0.setMaximum(10000)
        spin_z0.setSuffix(" mm")
        spin_dxds0 = QDoubleSpinBox()
        spin_dxds0.setMinimum(-1.5)
        spin_dxds0.setMaximum(1.5)
        spin_dxds0.setSuffix(" rad")
        spin_dyds0 = QDoubleSpinBox()
        spin_dyds0.setMinimum(-1.5)
        spin_dyds0.setMaximum(1.5)
        spin_dyds0.setSuffix(" rad")
        spin_dzds0 = QDoubleSpinBox()
        spin_dzds0.setMinimum(-1.5)
        spin_dzds0.setMaximum(1.5)
        spin_dzds0.setProperty("value",1.00)
        spin_dzds0.setSuffix(" rad")
        spin_zmax = QDoubleSpinBox()
        spin_zmax.setMinimum(-10000)
        spin_zmax.setMaximum(10000)
        spin_zmax.setProperty("value",900)
        spin_zmax.setSuffix(" mm")
        spin_zmax.setSizePolicy(sizeFixed,sizeFixed)
        spin_rkstep = QDoubleSpinBox()
        spin_rkstep.setProperty("value",0.50)
        spin_rkstep.setSuffix(" mm")

        gridTrajectory.addWidget(label_calc_trajectory,0,0,alignHCenter)
        gridTrajectory.addWidget(label_leftparenthesis,0,1)
        gridTrajectory.addWidget(label_energy,0,2)
        gridTrajectory.addWidget(spin_energy,0,3)
        gridTrajectory.addWidget(label_x0,1,2,alignRight)
        gridTrajectory.addWidget(spin_x0,1,3)
        gridTrajectory.addWidget(label_y0,2,2,alignRight)
        gridTrajectory.addWidget(spin_y0,2,3)
        gridTrajectory.addWidget(label_z0,3,2,alignRight)
        gridTrajectory.addWidget(spin_z0,3,3)
        gridTrajectory.addWidget(label_dxds0,4,2,alignRight)
        gridTrajectory.addWidget(spin_dxds0,4,3)
        gridTrajectory.addWidget(label_dyds0,5,2,alignRight)
        gridTrajectory.addWidget(spin_dyds0,5,3)
        gridTrajectory.addWidget(label_dzds0,6,2,alignRight)
        gridTrajectory.addWidget(spin_dzds0,6,3)
        gridTrajectory.addWidget(label_rightbracket,6,4)
        gridTrajectory.addWidget(label_zmax,7,2,alignRight)
        gridTrajectory.addWidget(spin_zmax,7,3)
        gridTrajectory.addWidget(label_rkstep,8,2,alignRight)
        gridTrajectory.addWidget(spin_rkstep,8,3)
        gridTrajectory.addWidget(label_rightparenthesis,8,4)


class PhaseErrorGroupBox(QGroupBox):
    def __init__(self):
        super().__init__(title="Phase Error")

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

        spin_energy = QDoubleSpinBox()
        spin_energy.setProperty("value",3.00)
        spin_energy.setSuffix(" GeV")
        spin_energy.setSizePolicy(sizeFixed,sizeFixed)
        label_trajectory_value = QLabel("calculated")
        label_trajectory_value.setFont(fontConsolas8)
        label_bx_amp_value = QLabel("calculated")
        label_bx_amp_value.setFont(fontConsolas8)
        label_by_amp_value = QLabel("calculated")
        label_by_amp_value.setFont(fontConsolas8)
        spin_skip_poles = QSpinBox()
        spin_skip_poles.setProperty("value",4)
        combo_zmin = NumericComboBox()
        combo_zmax = NumericComboBox()
        combo_field_comp = QComboBox()
        combo_field_comp.addItems(["None","0","1"])

        label_rightparenthesis = QLabel(")")
        label_rightparenthesis.setFont(fontConsolas14)
        label_rightparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        gridPhaseError.addWidget(label_calc_phase_error,0,0,alignHCenter)
        gridPhaseError.addWidget(label_leftparenthesis,0,1)
        gridPhaseError.addWidget(label_energy,0,2,alignRight)
        gridPhaseError.addWidget(spin_energy,0,3)
        gridPhaseError.addWidget(label_trajectory,1,2,alignRight)
        gridPhaseError.addWidget(label_trajectory_value,1,3,alignHCenter)
        gridPhaseError.addWidget(label_bx_amp,2,2,alignRight)
        gridPhaseError.addWidget(label_bx_amp_value,2,3,alignHCenter)
        gridPhaseError.addWidget(label_by_amp,3,2,alignRight)
        gridPhaseError.addWidget(label_by_amp_value,3,3,alignHCenter)
        gridPhaseError.addWidget(label_skip_poles,4,2,alignRight)
        gridPhaseError.addWidget(spin_skip_poles,4,3)
        gridPhaseError.addWidget(label_zmin,5,2,alignRight)
        gridPhaseError.addWidget(combo_zmin,5,3)
        gridPhaseError.addWidget(label_zmax,6,2,alignRight)
        gridPhaseError.addWidget(combo_zmax,6,3)
        gridPhaseError.addWidget(label_field_comp,7,2)
        gridPhaseError.addWidget(combo_field_comp,7,3)
        gridPhaseError.addWidget(label_rightparenthesis,7,4)
        
#todo: alterar integrals, vai definir os parametros e jogar para calcMagField
#todo: realmente vai ter que duplicar o get_field
class IntegralsGroupBox(QGroupBox):
    def __init__(self):
        super().__init__(title="Field Integrals")

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
        label_nproc = QLabel("nproc = ")
        label_nproc.setFont(fontConsolas10)
        label_chunksize = QLabel("chunksize = ")
        label_chunksize.setFont(fontConsolas10)

        for row in [0,1,2,3,4]:
            label_comma = QLabel(",")
            label_comma.setFont(fontConsolas10)
            label_comma.setSizePolicy(sizeFixed,sizePreferred)
            gridIntegrals.addWidget(label_comma,row,4)
        
        label_z_list_value = QLabel("get_field parameter")
        label_z_list_value.setFont(fontConsolas8)
        label_x_value = QLabel("get_field parameter")
        label_x_value.setFont(fontConsolas8)
        label_y_value = QLabel("get_field parameter")
        label_y_value.setFont(fontConsolas8)
        label_field_list_value = QLabel("calculated")
        label_field_list_value.setFont(fontConsolas8)
        label_nproc_value = QLabel("get_field parameter")
        label_nproc_value.setFont(fontConsolas8)
        label_chunksize_value = QLabel("get_field parameter")
        label_chunksize_value.setFont(fontConsolas8)
        label_chunksize_value.setSizePolicy(sizeFixed,sizePreferred)
        label_chunksize_value.setAlignment(alignCenter)

        label_rightparenthesis = QLabel(")")
        label_rightparenthesis.setFont(fontConsolas14)
        label_rightparenthesis.setSizePolicy(sizeFixed,sizePreferred)

        gridIntegrals.addWidget(label_calc_phase_error,0,0,alignCenter)
        gridIntegrals.addWidget(label_leftparenthesis,0,1)
        gridIntegrals.addWidget(label_z_list,0,2,alignRight)
        gridIntegrals.addWidget(label_z_list_value,0,3,alignCenter)
        gridIntegrals.addWidget(label_x,1,2,alignRight)
        gridIntegrals.addWidget(label_x_value,1,3,alignCenter)
        gridIntegrals.addWidget(label_y,2,2,alignRight)
        gridIntegrals.addWidget(label_y_value,2,3,alignCenter)
        gridIntegrals.addWidget(label_field_list,3,2)
        gridIntegrals.addWidget(label_field_list_value,3,3,alignCenter)
        gridIntegrals.addWidget(label_nproc,4,2,alignRight)
        gridIntegrals.addWidget(label_nproc_value,4,3,alignCenter)
        gridIntegrals.addWidget(label_chunksize,5,2,alignRight)
        gridIntegrals.addWidget(label_chunksize_value,5,3)
        gridIntegrals.addWidget(label_rightparenthesis,5,4,alignCenter)


class RollOffPeaksGroupBox(QGroupBox):
    def __init__(self):
        super().__init__(title="Roll Off Peaks")

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

        spin_zstart = QDoubleSpinBox()
        spin_zstart.setSuffix(" mm")
        spin_zstart.setSizePolicy(sizeFixed,sizeFixed)
        spin_zend = QDoubleSpinBox()
        spin_zend.setSuffix(" mm")
        spin_zstep = QDoubleSpinBox()
        spin_zstep.setSuffix(" mm")
        spin_xstart = QDoubleSpinBox()
        spin_xstart.setSuffix(" mm")
        spin_xend = QDoubleSpinBox()
        spin_xend.setSuffix(" mm")
        spin_xstep = QDoubleSpinBox()
        spin_xstep.setSuffix(" mm")
        spin_y = QDoubleSpinBox()
        spin_y.setSuffix(" mm")
        combo_field_comp = QComboBox()
        combo_field_comp.addItems(["None","0","1"])

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
        gridRollOffPeaks.addWidget(spin_zstart,0,4)
        gridRollOffPeaks.addWidget(label_zend,1,3,alignRight)
        gridRollOffPeaks.addWidget(spin_zend,1,4)
        gridRollOffPeaks.addWidget(label_zstep,2,3,alignRight)
        gridRollOffPeaks.addWidget(spin_zstep,2,4)
        gridRollOffPeaks.addWidget(label_zrightbracket,2,5)
        gridRollOffPeaks.addWidget(label_x,3,2,alignRight)
        gridRollOffPeaks.addWidget(label_xstart,3,3,alignRight)
        gridRollOffPeaks.addWidget(spin_xstart,3,4)
        gridRollOffPeaks.addWidget(label_xend,4,3,alignRight)
        gridRollOffPeaks.addWidget(spin_xend,4,4)
        gridRollOffPeaks.addWidget(label_xstep,5,3,alignRight)
        gridRollOffPeaks.addWidget(spin_xstep,5,4)
        gridRollOffPeaks.addWidget(label_xrightbracket,5,5)
        gridRollOffPeaks.addWidget(label_y,6,2,alignRight)
        gridRollOffPeaks.addWidget(spin_y,6,4)
        gridRollOffPeaks.addWidget(label_field_comp,7,2)
        gridRollOffPeaks.addWidget(combo_field_comp,7,4)
        gridRollOffPeaks.addWidget(label_rightparenthesis,7,5)


class RollOffAmpGroupBox(QGroupBox):
    def __init__(self):
        super().__init__(title="Roll Off Amplitude")

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

        spin_zstart = QDoubleSpinBox()
        spin_zstart.setSuffix(" mm")
        spin_zstart.setSizePolicy(sizeFixed,sizeFixed)
        spin_zend = QDoubleSpinBox()
        spin_zend.setSuffix(" mm")
        spin_zstep = QDoubleSpinBox()
        spin_zstep.setSuffix(" mm")
        spin_xstart = QDoubleSpinBox()
        spin_xstart.setSuffix(" mm")
        spin_xend = QDoubleSpinBox()
        spin_xend.setSuffix(" mm")
        spin_xstep = QDoubleSpinBox()
        spin_xstep.setSuffix(" mm")
        spin_y = QDoubleSpinBox()
        spin_y.setSuffix(" mm")

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
        gridRollOffAmp.addWidget(spin_zstart,0,4)
        gridRollOffAmp.addWidget(label_zend,1,3,alignRight)
        gridRollOffAmp.addWidget(spin_zend,1,4)
        gridRollOffAmp.addWidget(label_zstep,2,3,alignRight)
        gridRollOffAmp.addWidget(spin_zstep,2,4)
        gridRollOffAmp.addWidget(label_zrightbracket,2,5)
        gridRollOffAmp.addWidget(label_x,3,2,alignRight)
        gridRollOffAmp.addWidget(label_xstart,3,3,alignRight)
        gridRollOffAmp.addWidget(spin_xstart,3,4)
        gridRollOffAmp.addWidget(label_xend,4,3,alignRight)
        gridRollOffAmp.addWidget(spin_xend,4,4)
        gridRollOffAmp.addWidget(label_xstep,5,3,alignRight)
        gridRollOffAmp.addWidget(spin_xstep,5,4)
        gridRollOffAmp.addWidget(label_xrightbracket,5,5)
        gridRollOffAmp.addWidget(label_y,6,2,alignRight)
        gridRollOffAmp.addWidget(spin_y,6,4)
        gridRollOffAmp.addWidget(label_rightparenthesis,6,5)






class AnalysisLayout(QVBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        scroll = QScrollArea()

        widget = QWidget()

        scrollvbox = QVBoxLayout()

        groupMagneticField = MagneticFieldGroupBox()
        groupTrajectory = TrajectoryGroupBox()
        groupPhaseError = PhaseErrorGroupBox()
        groupIntegrals = IntegralsGroupBox()
        groupRollOffPeaks = RollOffPeaksGroupBox()
        groupRollOffAmp = RollOffAmpGroupBox()

        scrollvbox.addWidget(groupMagneticField)
        scrollvbox.addWidget(groupTrajectory)
        scrollvbox.addWidget(groupPhaseError)
        scrollvbox.addWidget(groupIntegrals)
        scrollvbox.addWidget(groupRollOffPeaks)
        scrollvbox.addWidget(groupRollOffAmp)

        widget.setLayout(scrollvbox)

        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        # botoes a serem usados
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        
        # criando os botoes
        self.buttonBox = QDialogButtonBox(buttons)
        

        self.addWidget(scroll)
        self.addWidget(self.buttonBox)