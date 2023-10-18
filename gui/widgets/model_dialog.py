from PyQt6.QtWidgets import QDialog, QFormLayout, QMessageBox

from imaids import models
from .dialog_layouts import ModelLayout
from . import models_parameters

# todo: ter opcao de carregar arquivo com o conjunto de pontos para ter forma dos blocos
class ModelDialog(QDialog):

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

        self.layoutModel = ModelLayout(models_parameters=models_parameters,parent=self)
        self.layoutModel.comboboxModels.currentIndexChanged.connect(self.model_chose)
        ## dialog button box - signals
        self.layoutModel.buttonBox.accepted.connect(self.accept)
        self.layoutModel.buttonBox.rejected.connect(self.reject)


    def model_chose(self,index):
        print("modelo escolhido:", self.layoutModel.comboboxModels.currentText())
        
        #escondendo modelo escolhido anteriormente
        self.layoutModel.currentModelGroup.setHidden(True)
    
        currentModel = self.layoutModel.comboboxModels.currentText()
        
        if index != 0:
            self.layoutModel.currentModelGroup = self.layoutModel.groups_dict[currentModel]
            self.layoutModel.currentModelGroup.setHidden(False)
            self.layoutModel.lineModelNaming.setText(self.layoutModel.comboboxModels.currentText())
            self.layoutModel.widgetNaming.setHidden(False)
        else:
            self.layoutModel.widgetNaming.setHidden(True)
            self.adjustSize()

    def get_values(self):
        
        model_name = self.layoutModel.lineModelNaming.text()
        model_group = self.layoutModel.currentModelGroup

        parameters = {}
        for parameter in [model_group.spin_nr_periods,
                          model_group.spin_period_length,
                          model_group.spin_gap,
                          model_group.spin_longitudinal_distance,
                          model_group.spin_mr]:
            #storing parameter
            parameters[parameter.objectName()] = parameter.value()
        
        Nrows = model_group.formCassettePos.rowCount()

        cassette_positions = {}
        for row_index in range(Nrows):
            # cassette displacement
            dcassette = model_group.formCassettePos.itemAt(row_index,
                                                           QFormLayout.ItemRole.FieldRole)
            dcassette = dcassette.widget()
            #storing displacement
            cassette_positions[dcassette.objectName()] = dcassette.value()

        return model_name, parameters, cassette_positions
    
    @classmethod
    def getSimulatedID(cls, parent=None):

        dialog = cls(parent)
        answer = dialog.exec()

        if  answer == QDialog.DialogCode.Accepted:

            if dialog.layoutModel.comboboxModels.currentText() == "":
                return None, ""

            # valores usados nas spin boxes (parametros e posicoes dos cassetes)
            ID_name, kwargs_model, kwargs_cassettes = dialog.get_values()

            modelo_class = dialog.models_dict[dialog.layoutModel.comboboxModels.currentText()]
            
            ID = modelo_class(**kwargs_model)
            #*: polemico, ja que usa-se mesmo padrao de nome para dado e modelo
            #ID.name = ID_name
            ID.set_cassete_positions(**kwargs_cassettes)
            #ID.draw()

            # *: podera' criar modelos iguais uns aos outros, entao nao precisa checar se ja foi adicionado
            return ID, ID_name

        if answer == QDialog.DialogCode.Rejected:
            return None, ""
        
    def accept(self) -> None:

        model_group = self.layoutModel.currentModelGroup
        magneticGeometry = [model_group.spin_nr_periods.value(),
                          model_group.spin_period_length.value(),
                          model_group.spin_gap.value(),
                          model_group.spin_mr.value()]
        
        if 0 in magneticGeometry:
            QMessageBox.critical(self,
                                 "Critical Warning",
                                 "Nº of Periods, Period, Gap and Magnetization must be non zero!")
        else:
            return super().accept()

# ?: como conseguir string do nome da classe
#  : usando o atributo __name__
# ?: como conseguir dict diretamente das classes sem precisar construir como abaixo

#dircionario = {DeltaLayout.__name__: DeltaLayout, ModelDialog.__name__: ModelDialog}

#print(dircionario)
