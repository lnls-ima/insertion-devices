
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

from PyQt6.QtWidgets import (QDialog,
                             QWidget,
                             QScrollArea,
                             QVBoxLayout,
                             QGroupBox,
                             QGridLayout,
                             QLabel,
                             QDoubleSpinBox,
                             QDialogButtonBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class AnalysisDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Analysis Parameters")

        dialogvbox = QVBoxLayout()

        scroll = QScrollArea()

        widget = QWidget()

        scrollvbox = QVBoxLayout()

        groupField = QGroupBox(title="Magnetic Field")

        groupTrajectory = QGroupBox(title="Trajectory")

        gridTrajectory = QGridLayout(parent=groupTrajectory)
        gridTrajectory.setSpacing(0)

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
        groupRollOff = QGroupBox(title="Roll Off")
        groupKickmap = QGroupBox(title="Kickmap")
        groupCrossTalk = QGroupBox(title="Cross Talk")
        groupShimming = QGroupBox(title="Shimming")

        scrollvbox.addWidget(groupField)
        scrollvbox.addWidget(groupTrajectory)
        scrollvbox.addWidget(groupPhaseError)
        scrollvbox.addWidget(groupIntegrals)
        scrollvbox.addWidget(groupRollOff)
        scrollvbox.addWidget(groupKickmap)
        scrollvbox.addWidget(groupCrossTalk)
        scrollvbox.addWidget(groupShimming)

        widget.setLayout(scrollvbox)

        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        # botoes a serem usados
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        
        # criando os botoes
        self.buttonBox = QDialogButtonBox(buttons)
        
        # signals
        ## signal sent from Ok button to the handler accept of QDialog class
        self.buttonBox.accepted.connect(self.accept)
        ## signal sent from Ok button to the handler reject of QDialog class
        self.buttonBox.rejected.connect(self.reject)

        dialogvbox.addWidget(scroll)
        dialogvbox.addWidget(self.buttonBox)

        self.setLayout(dialogvbox)



    # def analysis_chose(self, index):
    #     if index==1:

        