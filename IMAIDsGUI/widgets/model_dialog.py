
from PyQt6.QtWidgets import (QGroupBox,
                             QSpinBox,
                             QDoubleSpinBox,
                             QLabel,
                             QComboBox,
                             QDialog,
                             QDialogButtonBox,
                             QHBoxLayout,
                             QVBoxLayout,
                             QFormLayout)


class ModelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Model")

        self.models_list = ["Delta Prototype",
                            "Delta Sabia",
                            "Delta Carnauba",
                            "AppleX Sabia",
                            "AppleX Carnauba",
                            "AppleII Sabia",
                            "AppleII Carnauba",
                            "Kyma 22",
                            "Kyma 58",
                            "PAPU",
                            "Hybrid APU",
                            "Hybrid Planar",
                            "Mini Planar Sabia"]
        
        
        # ajustando widgets principais em um layout
        
        self.dialogvbox = QVBoxLayout()

        self.layoutModelInput = QHBoxLayout() #indicar que e' horizontal

        self.labelModels = QLabel("Enter the model:")
        self.models = QComboBox()
        self.models.addItems(["",*self.models_list])
        self.models.activated.connect(self.model_chose)

        self.layoutModelInput.addWidget(self.labelModels)
        self.layoutModelInput.addWidget(self.models)

        
        # ajustando labels e spinboxes em group boxes

        self.groupDeltaSabia = QGroupBox(title="Delta Sabia Parameters",parent=self)

        self.layout_group_h = QHBoxLayout(self.groupDeltaSabia)

        self.layout_group_form = QFormLayout()

        self.label_nr_periods = QLabel("Number of Periods:")
        self.label_period_length = QLabel("Period Length:")
        self.label_gap = QLabel("Gap Length:")
        self.label_longitudinal_distance = QLabel("Longitudinal Distance:")
        self.label_mr = QLabel("Magnetization Remanent:")

        self.spin_nr_periods = QSpinBox(parent=self.groupDeltaSabia)
        self.spin_nr_periods.setObjectName("nr_periods")
        self.spin_nr_periods.setProperty("value",21)
        self.spin_period_length = QDoubleSpinBox(parent=self.groupDeltaSabia)
        self.spin_period_length.setObjectName("period_length")
        self.spin_period_length.setDecimals(1)
        self.spin_period_length.setProperty("value",52.5)
        self.spin_period_length.setSuffix(" mm")
        self.spin_gap = QDoubleSpinBox(parent=self.groupDeltaSabia)
        self.spin_gap.setObjectName("gap")
        self.spin_gap.setDecimals(1)
        self.spin_gap.setProperty("value",13.6)
        self.spin_gap.setSuffix(" mm")
        self.spin_longitudinal_distance = QDoubleSpinBox(parent=self.groupDeltaSabia)
        self.spin_longitudinal_distance.setObjectName("longitudinal_distance")
        self.spin_longitudinal_distance.setDecimals(3)
        self.spin_longitudinal_distance.setProperty("value",0.125)
        self.spin_longitudinal_distance.setSuffix(" mm")
        self.spin_mr = QDoubleSpinBox(parent=self.groupDeltaSabia)
        self.spin_mr.setObjectName("mr")
        self.spin_mr.setDecimals(2)
        self.spin_mr.setProperty("value",1.39)
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

        self.group2 = QGroupBox(title="Cassette Parameters",parent=self)

        self.layout_group2_form = QFormLayout(parent=self.group2)

        self.label_dp = QLabel("dp:")
        self.label_dcp = QLabel("dcp:") 
        self.label_dgv = QLabel("dgv:")
        self.label_dgh = QLabel("dgh:")

        self.spin_dp = QDoubleSpinBox(parent=self.group2)
        self.spin_dp.setObjectName("dp")
        self.spin_dp.setDecimals(2)
        self.spin_dp.setSuffix(" mm")
        self.spin_dcp = QDoubleSpinBox(parent=self.group2)
        self.spin_dcp.setObjectName("dcp")
        self.spin_dcp.setDecimals(2)
        self.spin_dcp.setSuffix(" mm")
        self.spin_dgv = QDoubleSpinBox(parent=self.group2)
        self.spin_dgv.setObjectName("dgv")
        self.spin_dgv.setDecimals(2)
        self.spin_dgv.setSuffix(" mm")
        self.spin_dgh = QDoubleSpinBox(parent=self.group2)
        self.spin_dgh.setObjectName("dgh")
        self.spin_dgh.setDecimals(2)
        self.spin_dgh.setSuffix(" mm")

        self.layout_group2_form.setWidget(0,QFormLayout.ItemRole.LabelRole,self.label_dp)
        self.layout_group2_form.setWidget(0,QFormLayout.ItemRole.FieldRole,self.spin_dp)
        self.layout_group2_form.setWidget(1,QFormLayout.ItemRole.LabelRole,self.label_dcp)
        self.layout_group2_form.setWidget(1,QFormLayout.ItemRole.FieldRole,self.spin_dcp)
        self.layout_group2_form.setWidget(2,QFormLayout.ItemRole.LabelRole,self.label_dgv)
        self.layout_group2_form.setWidget(2,QFormLayout.ItemRole.FieldRole,self.spin_dgv)
        self.layout_group2_form.setWidget(3,QFormLayout.ItemRole.LabelRole,self.label_dgh)
        self.layout_group2_form.setWidget(3,QFormLayout.ItemRole.FieldRole,self.spin_dgh)

        self.layout_group_h.addWidget(self.group2)

        self.groupDeltaSabia.setHidden(True)


        # botoes a serem usados
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        # criando os botoes
        self.buttonBox = QDialogButtonBox(buttons)
        # signals
        ## signal sent from Ok button to the handler accept of QDialog class
        self.buttonBox.accepted.connect(self.accept)
        ## signal sent from Ok button to the handler reject of QDialog class
        self.buttonBox.rejected.connect(self.reject)


        self.dialogvbox.addLayout(self.layoutModelInput)
        self.dialogvbox.addWidget(self.groupDeltaSabia)
        self.dialogvbox.addWidget(self.buttonBox)

        self.setLayout(self.dialogvbox)



    def model_chose(self,index):
        model = self.models_list[index-1]
        print("modelo escolhido:",model)
        if model=='Delta Sabia':
            self.groupDeltaSabia.setHidden(False)
        else:
            self.groupDeltaSabia.setHidden(True)

    # def accept(self) -> None:
    #     print('aceito')
    #     return super().accept()
    
    # def reject(self) -> None:
    #     print('rejeitado')
    #     return super().reject()
