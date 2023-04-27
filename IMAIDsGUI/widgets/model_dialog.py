
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

import imaids.models as models


class DeltaLayout(QGroupBox):
    def __init__(self,title,parent,
                 nr_periods,period_length,gap,longitudinal_distance,mr,
                 *args,**kwargs):
        
        super().__init__(title=title,parent=parent,
                         *args,**kwargs)

        self.layout_group_h = QHBoxLayout(self)

        self.layout_group_form = QFormLayout()

        self.label_nr_periods = QLabel("Number of Periods:")
        self.label_period_length = QLabel("Period Length:")
        self.label_gap = QLabel("Gap Length:")
        self.label_longitudinal_distance = QLabel("Longitudinal Distance:")
        self.label_mr = QLabel("Magnetization Remanent:")

        #todo: valores padrao mudam de modelo especifico para modelo especifico
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

        self.groups = []
        
        self.groupDeltaPrototype = DeltaLayout(title="Delta Prototype Parameters",parent=self,
                                           nr_periods=60,period_length=20, gap=7, longitudinal_distance=0, mr=1.36)
        self.groups.append(self.groupDeltaPrototype)
        self.groupDeltaPrototype.setHidden(True)
        self.groupDeltaSabia = DeltaLayout(title="Delta Sabia Parameters",parent=self,
                                           nr_periods=21,period_length=52.5, gap=13.6, longitudinal_distance=0.125, mr=1.39)
        self.groupDeltaSabia.setHidden(True)
        self.groupDeltaCarnauba = DeltaLayout(title="Delta Carnauba Parameters",parent=self,
                                           nr_periods=52,period_length=22, gap=7, longitudinal_distance=0.05, mr=1.37)
        self.groupDeltaCarnauba.setHidden(True)

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
        self.dialogvbox.addWidget(self.groupDeltaPrototype)
        self.dialogvbox.addWidget(self.groupDeltaSabia)
        self.dialogvbox.addWidget(self.groupDeltaCarnauba)
        self.dialogvbox.addWidget(self.buttonBox)

        self.setLayout(self.dialogvbox)



    def model_chose(self,index):
        print("modelo escolhido:", self.models.currentData(index))
        # todo: melhorar maneira de esconder os groups quando mudar de modelo especifico
        #self.past_model.setHidden(True)
        self.groupDeltaPrototype.setHidden(True)
        self.groupDeltaSabia.setHidden(True)
        self.groupDeltaCarnauba.setHidden(True)
        
        if index==1:
            self.setObjectName("DeltaPrototype")
            self.groupDeltaPrototype.setHidden(False)
        if index==2:
            self.setObjectName("DeltaSabia")
            self.groupDeltaSabia.setHidden(False)
        if index==3:
            self.setObjectName("DeltaCarnauba")
            self.groupDeltaCarnauba.setHidden(False)

    def get_values(self):
        cassette_positions = {self.groupDeltaSabia.spin_dp.objectName(): self.groupDeltaSabia.spin_dp.value(),
                              self.groupDeltaSabia.spin_dcp.objectName(): self.groupDeltaSabia.spin_dcp.value(),
                              self.groupDeltaSabia.spin_dgv.objectName(): self.groupDeltaSabia.spin_dgv.value(),
                              self.groupDeltaSabia.spin_dgh.objectName(): self.groupDeltaSabia.spin_dgh.value()}
        
        parameters = {self.groupDeltaSabia.spin_nr_periods.objectName(): self.groupDeltaSabia.spin_nr_periods.value(),
                      self.groupDeltaSabia.spin_period_length.objectName(): self.groupDeltaSabia.spin_period_length.value(),
                      self.groupDeltaSabia.spin_gap.objectName(): self.groupDeltaSabia.spin_gap.value(),
                      self.groupDeltaSabia.spin_longitudinal_distance.objectName(): self.groupDeltaSabia.spin_longitudinal_distance.value(),
                      self.groupDeltaSabia.spin_mr.objectName(): self.groupDeltaSabia.spin_mr.value()}
        
        return parameters, cassette_positions
    
    # def accept(self) -> None:
    #     print('aceito')
    #     return super().accept()
    
    # def reject(self) -> None:
    #     print('rejeitado')
    #     return super().reject()


# ?: como conseguir string do nome da classe
#  : usando o atributo __name__
# ?: como conseguir dict diretamente das classes sem precisar construir como abaixo

#dircionario = {DeltaLayout.__name__: DeltaLayout, ModelDialog.__name__: ModelDialog}

#print(dircionario)
