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
                             QGroupBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


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
        self.comboboxModels.addItems(["",*self.parameters.keys()])
        

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





class AnalysisLayout(QVBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        scroll = QScrollArea()

        widget = QWidget()

        scrollvbox = QVBoxLayout()

        groupField = QGroupBox(title="Magnetic Field")
        groupTrajectory = QGroupBox(title="Trajectory")

        gridTrajectory = QGridLayout(parent=groupTrajectory)
        gridTrajectory.setSpacing(0)

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

        fontConsolas10 = QFont("Consolas",10)
        fontConsolas12 = QFont("Consolas",12)

        label_calc_trajectory = QLabel("calc_trajectory")
        label_calc_trajectory.setFont(fontConsolas10)
        label_leftparenthesis = QLabel("(")
        label_leftparenthesis.setFont(fontConsolas12)
        label_rightparenthesis = QLabel(")")
        label_rightparenthesis.setFont(fontConsolas12)
        label_comma04 = QLabel(",")
        label_comma04.setFont(fontConsolas10)
        label_comma14 = QLabel(",")
        label_comma14.setFont(fontConsolas10)
        label_comma24 = QLabel(",")
        label_comma24.setFont(fontConsolas10)
        label_comma34 = QLabel(",")
        label_comma34.setFont(fontConsolas10)
        label_comma44 = QLabel(",")
        label_comma44.setFont(fontConsolas10)
        label_comma54 = QLabel(",")
        label_comma54.setFont(fontConsolas10)
        label_comma74 = QLabel(",")
        label_comma74.setFont(fontConsolas10)
        label_rightbracket = QLabel("],")
        label_rightbracket.setFont(fontConsolas10)
        label_energy = QLabel("energy = ")
        label_energy.setFont(fontConsolas10)
        label_energy.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        label_x0     = QLabel("[x0 = ")
        label_x0.setFont(fontConsolas10)
        label_x0.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        label_y0     = QLabel("y0 = ")
        label_y0.setFont(fontConsolas10)
        label_y0.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        label_z0     = QLabel("z0 = ")
        label_z0.setFont(fontConsolas10)
        label_z0.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        label_dxds0  = QLabel("dxds0 = ")
        label_dxds0.setFont(fontConsolas10)
        label_dxds0.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        label_dyds0  = QLabel("dyds0 = ")
        label_dyds0.setFont(fontConsolas10)
        label_dyds0.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        label_dzds0  = QLabel("dzds0 = ")
        label_dzds0.setFont(fontConsolas10)
        label_dzds0.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        label_zmax   = QLabel("zmax = ")
        label_zmax.setFont(fontConsolas10)
        label_zmax.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        label_rkstep = QLabel("rkstep = ")
        label_rkstep.setFont(fontConsolas10)
        label_rkstep.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        spin_energy = QDoubleSpinBox(parent=groupTrajectory)
        spin_energy.setProperty("value",3.00)
        spin_energy.setSuffix(" GeV")
        spin_x0 = QDoubleSpinBox(parent=groupTrajectory)
        spin_x0.setMinimum(-10000)
        spin_x0.setMaximum(10000)
        spin_x0.setProperty("value",-900)
        spin_x0.setSuffix(" mm")
        spin_y0 = QDoubleSpinBox(parent=groupTrajectory)
        spin_y0.setMinimum(-10000)
        spin_y0.setMaximum(10000)
        spin_y0.setSuffix(" mm")
        spin_z0 = QDoubleSpinBox(parent=groupTrajectory)
        spin_z0.setMinimum(-10000)
        spin_z0.setMaximum(10000)
        spin_z0.setSuffix(" mm")
        spin_dxds0 = QDoubleSpinBox(parent=groupTrajectory)
        spin_dxds0.setMinimum(-1.5)
        spin_dxds0.setMaximum(1.5)
        spin_dxds0.setSuffix(" rad")
        spin_dyds0 = QDoubleSpinBox(parent=groupTrajectory)
        spin_dyds0.setMinimum(-1.5)
        spin_dyds0.setMaximum(1.5)
        spin_dyds0.setSuffix(" rad")
        spin_dzds0 = QDoubleSpinBox(parent=groupTrajectory)
        spin_dzds0.setMinimum(-1.5)
        spin_dzds0.setMaximum(1.5)
        spin_dzds0.setProperty("value",1.00)
        spin_dzds0.setSuffix(" rad")
        spin_zmax = QDoubleSpinBox(parent=groupTrajectory)
        spin_zmax.setMinimum(-10000)
        spin_zmax.setMaximum(10000)
        spin_zmax.setProperty("value",900)
        spin_zmax.setSuffix(" mm")
        spin_rkstep = QDoubleSpinBox(parent=groupTrajectory)
        spin_rkstep.setProperty("value",0.50)
        spin_rkstep.setSuffix(" mm")

        gridTrajectory.addWidget(label_calc_trajectory,0,0)
        gridTrajectory.addWidget(label_leftparenthesis,0,1)
        gridTrajectory.addWidget(label_energy,0,2)
        gridTrajectory.addWidget(spin_energy,0,3)
        gridTrajectory.addWidget(label_comma04,0,4)
        gridTrajectory.addWidget(label_x0,1,2)
        gridTrajectory.addWidget(spin_x0,1,3)
        gridTrajectory.addWidget(label_comma14,1,4)
        gridTrajectory.addWidget(label_y0,2,2)
        gridTrajectory.addWidget(spin_y0,2,3)
        gridTrajectory.addWidget(label_comma24,2,4)
        gridTrajectory.addWidget(label_z0,3,2)
        gridTrajectory.addWidget(spin_z0,3,3)
        gridTrajectory.addWidget(label_comma34,3,4)
        gridTrajectory.addWidget(label_dxds0,4,2)
        gridTrajectory.addWidget(spin_dxds0,4,3)
        gridTrajectory.addWidget(label_comma44,4,4)
        gridTrajectory.addWidget(label_dyds0,5,2)
        gridTrajectory.addWidget(spin_dyds0,5,3)
        gridTrajectory.addWidget(label_comma54,5,4)
        gridTrajectory.addWidget(label_dzds0,6,2)
        gridTrajectory.addWidget(spin_dzds0,6,3)
        gridTrajectory.addWidget(label_rightbracket,6,4)
        gridTrajectory.addWidget(label_zmax,7,2)
        gridTrajectory.addWidget(spin_zmax,7,3)
        gridTrajectory.addWidget(label_comma74,7,4)
        gridTrajectory.addWidget(label_rkstep,8,2)
        gridTrajectory.addWidget(spin_rkstep,8,3)
        gridTrajectory.addWidget(label_rightparenthesis,8,4)

        groupPhaseError = QGroupBox(title="Phase Error")
        groupIntegrals = QGroupBox(title="Field Integrals")
        groupRollOffPeaks = QGroupBox(title="Roll Off Peaks")
        groupRollOffAmp = QGroupBox(title="Roll Off Amplitude")

        scrollvbox.addWidget(groupField)
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