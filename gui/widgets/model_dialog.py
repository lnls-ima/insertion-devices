
import os

from PyQt6.QtWidgets import (QWidget,
                             QGroupBox,
                             QSpinBox,
                             QDoubleSpinBox,
                             QLabel,
                             QLineEdit,
                             QComboBox,
                             QDialog,
                             QDialogButtonBox,
                             QHBoxLayout,
                             QVBoxLayout,
                             QFormLayout)

import imaids.models as models

import json


class ModelLayout(QGroupBox):
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


class ModelDialog(QDialog):

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

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Generate Model")

        self.models_dict = {}
        for name in dir(models):
            obj = getattr(models, name)
            if isinstance(obj, type):
                self.models_dict[name] = obj

        # deixar apenas modelos especificos no dicionario de modelos
        #todo: colocar condicao na criacao do models dict que checa se classe e' subclassed
        #todo: com isso, pegaremos apenas os modelos especificos
        for model_type in ["Delta","AppleX","AppleII","APU","Planar"]:
            self.models_dict.pop(model_type)
        
        # ajustando widgets principais em um layout
        
        self.dialogvbox = QVBoxLayout()

        self.layoutModelInput = QHBoxLayout() #nome da variavel indicar que e' horizontal

        self.labelModels = QLabel("Enter the model:")
        self.comboboxModels = QComboBox()
        self.comboboxModels.addItems(["",*self.parameters.keys()])
        self.comboboxModels.currentIndexChanged.connect(self.model_chose)

        self.layoutModelInput.addWidget(self.labelModels)
        self.layoutModelInput.addWidget(self.comboboxModels)

        self.groups = {}
        for model_name in self.models_dict:
            self.groups[model_name] = ModelLayout(model_name=model_name, parent=self, **self.parameters[model_name])

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
        ## dialog button box - signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.dialogvbox.addLayout(self.layoutModelInput)
        for group in self.groups.values():
            group.setHidden(True)
            self.dialogvbox.addWidget(group)
        self.dialogvbox.addWidget(self.widgetNaming)
        self.dialogvbox.addWidget(self.buttonBox)

        self.setLayout(self.dialogvbox)



    def model_chose(self,index):
        print("modelo escolhido:", self.comboboxModels.currentText())
        
        #escondendo modelo escolhido anteriormente
        self.currentModelGroup.setHidden(True)
    
        currentModel = self.comboboxModels.currentText()
        
        if index != 0:
            self.currentModelGroup = self.groups[currentModel]
            self.currentModelGroup.setHidden(False)
            self.lineModelNaming.setText(self.comboboxModels.currentText())
            self.widgetNaming.setHidden(False)
        else:
            self.widgetNaming.setHidden(True)
            self.adjustSize()

    def get_values(self):
        
        model_label = self.lineModelNaming.text()

        parameters = {}
        for parameter in [self.currentModelGroup.spin_nr_periods,
                          self.currentModelGroup.spin_period_length,
                          self.currentModelGroup.spin_gap,
                          self.currentModelGroup.spin_longitudinal_distance,
                          self.currentModelGroup.spin_mr]:
            #storing parameter
            parameters[parameter.objectName()] = parameter.value()
        
        Nrows = self.currentModelGroup.formCassettePos.rowCount()

        cassette_positions = {}
        for row_index in range(Nrows):
            # cassette displacement
            dcassette = self.currentModelGroup.formCassettePos.itemAt(row_index,
                                                                      QFormLayout.ItemRole.FieldRole)
            dcassette = dcassette.widget()
            #storing displacement
            cassette_positions[dcassette.objectName()] = dcassette.value()

        return model_label, parameters, cassette_positions
    
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
