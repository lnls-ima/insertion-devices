
from enum import Enum
from PyQt6 import sip
import numpy as np
from PyQt6.QtWidgets import QTreeWidgetItem, QTreeWidget
from PyQt6.QtGui import QColor, QKeyEvent
from PyQt6.QtCore import pyqtSignal, Qt, QItemSelectionModel, QItemSelection


class ExploreItem(QTreeWidgetItem):

    energy = 3
    x0, y0, z0 = 0, 0, -900
    dxds0, dyds0, dzds0 = 0, 0, 1
    zmax = 900
    rkstep = 0.5
    skip_poles = 4
    Z = np.arange(-900,900,0.5)
    X = np.linspace(-5, 5, 23)

    class ContainerType(Enum):
        ContainerData = 0
        ContainerModel = 1

    class IDType(Enum):
        IDModel = 0
        IDData = 1
    
    #*: na tree, de analysis items pra baixo, nao podera' renomear
    class AnalysisType(Enum):
        MagneticField = "Magnetic Field"
        Trajectory = "Trajectory"
        PhaseError = "Phase Error"
        Integrals = "Field Integrals"
        RollOffPeaks = "Roll Off Peaks"
        RollOffAmp = "Roll Off Amplitude"
        CrossTalk = "Cross Talk"
    
    class ResultType(Enum):
        ResultArray = 0
        ResultNumeric = 1

    def __init__(self, item_type: Enum, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #*: talvez os resultados e objeto insertion device possam ser gravados aqui no
        #*: proprio item, assim nao seria necessario o dicionario insertiondevices em
        #*: ProjectWidget
        #*: os dados seriam feitos e gravados dependendo do depth do ExploreItem a ser
        #*: manipulado

        self.item_type = item_type

    def delete(self):
        sip.delete(self)

    def children(self):
        return [self.child(i) for i in range(self.childCount())]
    
    def type(self):
        return type(self.item_type)
    
    def flag(self):
        return self.item_type

    
    def parent(self) -> 'ExploreItem':
        return super().parent()
    
    def depth(self):
        
        if self.parent() is None:
            return 0
        else:
            return self.parent().depth()+1
        
    def IDName(self):

        depth = self.depth()

        if depth==1:
            id_name = self.text(0)
        elif depth==2:
            id_name = self.parent().text(0)
        elif depth==3:
            id_name = self.parent().parent().text(0)
        
        return id_name


    #ha metodo de QTreeWidgetItem para colocar child em si mesmo
    #todo: conferir como e' implementado dentro de QTreeWidget. se cria-se QTreeWidget dentro dela mesma

    #todo arg: params_dict_MagneticField
    def calcMagnetic_Field(self, id_dict: dict):

        ID = id_dict["InsertionDeviceObject"]
        B = ID.get_field(x=0, y=0, z=self.Z, nproc=None, chunksize=100)
        Bx, By, Bz = B.T
        id_dict[self.text(0)] = {"z [mm]": self.Z, "Bx [T]": Bx, "By [T]": By, "Bz [T]": Bz}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, self, ["z [mm]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ["Bx [T]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ["By [T]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ["Bz [T]", "List"])]
        
        return result_items
        
    #todo arg: params_dict
    def calcTrajectory(self, id_dict: dict):

        ID = id_dict["InsertionDeviceObject"]
        #energy = 3 x0 = 0 y0 = 0 z0 = -900 dxds0 = 0 dyds0 = 0 dzds0 = 1 zmax = 900 rkstep = 0.5
        traj = ID.calc_trajectory(self.energy,[self.x0,self.y0,self.z0,self.dxds0,self.dyds0,self.dzds0],self.zmax,self.rkstep, dz=0, on_axis_field=False)
        x, y, z, dxds, dyds, dzds = traj.T
        id_dict[self.text(0)] = {"x [mm]": x, "y [mm]": y, "z [mm]": z, "x' [rad]": dxds, "y' [rad]": dyds, "z' [rad]": dzds}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, self, ["x [mm]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ["y [mm]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ["z [mm]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ["x' [rad]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ["y' [rad]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ["z' [rad]", "List"])]
        
        return result_items
    
    #todo arg: params_dict
    def calcPhase_Error(self, id_dict: dict):

        ID = id_dict["InsertionDeviceObject"]
        traj_dict = id_dict[ExploreItem.AnalysisType.Trajectory.value]
        traj = np.array(list(traj_dict.values())).T
        bxamp, byamp, _, _ = ID.calc_field_amplitude()
        kh, kv = ID.calc_deflection_parameter(bxamp, byamp)
        z_list, pe, pe_rms = ID.calc_phase_error(self.energy, traj, bxamp, byamp, self.skip_poles, zmin=None, zmax=None, field_comp=None)
        #chaves do dicionario no membro direito devem ser iguais aos nomes usados nos respectivos items
        id_dict[self.text(0)] = {"z poles [mm]": z_list, "PhaseErr [deg]": pe*180/np.pi, "RMS [deg]": pe_rms*180/np.pi}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, self, ["z poles [mm]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ["PhaseErr [deg]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, self, ["RMS [deg]", f"{pe_rms*180/np.pi:.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, self, ["Bx Amp [T]", f"{bxamp:.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, self, ["By Amp [T]", f"{byamp:.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, self, ["Kh [T.mm]", f"{kh:.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, self, ["Kv [T.mm]", f"{kv:.1f}"])]
        
        return result_items
        
    #todo arg: params_dict
    def calcField_Integrals(self, id_dict: dict):

        ID = id_dict["InsertionDeviceObject"]
        #todo: conferir calculo de integrais de campo para modelos
        #*: dependendendo de como for calculado o campo antes, pode nao ser possivel calcular as integrais
        #*: apropriadamente, entao duplicarei o calculo de campo
        B_dict = id_dict[ExploreItem.AnalysisType.MagneticField.value]
        B = np.array(list(B_dict.values())[1:]).T
        ib, iib = ID.calc_field_integrals(z_list=self.Z, field_list=B)
        ibx, iby, ibz = ib.T
        iibx, iiby, iibz = iib.T
        id_dict[self.text(0)] = {'z [mm]': self.Z,
                                            'IBx [G.cm]': ibx, 'IBy [G.cm]': iby, 'IBz [G.cm]': ibz,
                                            'IIBx [kG.cm2]': iibx, 'IIBy [kG.cm2]': iiby, 'IIBz [kG.cm2]': iibz}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, self, ['z [mm]',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ['IBx [G.cm]',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ['IBy [G.cm]',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ['IBz [G.cm]',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ['IIBx [kG.cm2]', "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ['IIBy [kG.cm2]', "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ['IIBz [kG.cm2]', "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, self, ['IBx T  [G.cm]',   f"{ibx[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, self, ['IBy T  [G.cm]',   f"{iby[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, self, ['IBz T  [G.cm]',   f"{ibz[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, self, ['IIBx T [kG.cm2]', f"{iibx[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, self, ['IIBy T [kG.cm2]', f"{iiby[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, self, ['IIBz T [kG.cm2]', f"{iibz[-1]:7.1f}"])]
        
        return result_items
        
    #todo arg: params_dict
    def calcRoll_Off_Peaks(self, id_dict: dict):

        ID = id_dict["InsertionDeviceObject"]
        ropx, ropy, ropz = ID.calc_roll_off_peaks(z=self.Z,x=self.X,y=0,field_comp=None)
        id_dict[self.text(0)] = {'ROPx': ropx,'ROPy': ropy,'ROPz': ropz}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, self, ['ROPx',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ['ROPy',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ['ROPz',  "List"])]
        
        return result_items

    #todo arg: params_dict
    def calcRoll_Off_Amplitude(self, id_dict: dict):

        ID = id_dict["InsertionDeviceObject"]
        roax, roay, roaz = ID.calc_roll_off_amplitude(z=self.Z,x=self.X,y=0)
        id_dict[self.text(0)] = {'ROAx': roax,'ROAy': roay,'ROAz': roaz}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, self, ['ROAx',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ['ROAy',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, self, ['ROAz',  "List"])]
        
        return result_items

    #todo arg: params_dict
    def calcCross_Talk(self, id_dict: dict):
    
        id_item = self.parent()
        id_name = id_item.text(0)

        ID = id_dict["InsertionDeviceObject"]
        ID.correct_angles(angxy=0.15, angxz=-0.21, angyx=-0.01,
                            angyz=-0.02, angzx=0.01, angzy=-0.74)
        ky = [-0.006781104386361973,-0.01675247563602003,7.568631573320983e-06]
        kz = [-0.006170829583118335,-0.016051627320478382,7.886674928668737e-06]
        ID.correct_cross_talk(ky=ky,kz=kz)
        id_dict[self.text(0)] = {'angxy':  0.15, 'angxz': -0.21,
                                            'angyx': -0.01, 'angyz': -0.02,
                                            'angzx':  0.01, 'angzy': -0.74,
                                            'ky': ky, 'kz': kz}
        
        self.delete()
        id_new_name = id_name+' C'
        id_item.setText(0,id_new_name)
        
        result_items = []
        
        return result_items



#todo: modelo de selecao:
#todo: - mudar cor e comportamento apenas quando estiver no modo de plot
#todo: - desmarcar selecao quando clicar fora da tree
#todo: - nao poder selecionar resultados numericos
#todo: - nao poder selecionar mais de dois dados
#todo: - se clicou primeiro em analise, nao poder selecionar com ctrl outras coisas

class TreeSelectionModel(QItemSelectionModel):
    def __init__(self, model):
        super().__init__(model)

    def select(self, selection: 'QItemSelection', command) -> None:
        super().select(selection, command)

class ExploreTreeWidget(QTreeWidget):

    selectReturned = pyqtSignal(list)
    keyPressed = pyqtSignal(QKeyEvent)

    def __init__(self, parent=None,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)

        self.itemsSelected = []

        self.itemSelectionChanged.connect(self.selection_changed)
        
        self.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.setColumnCount(2)
        self.setHeaderLabels(["Item", "Content"])
        #self.setHeaderHidden(True)
        self.header().resizeSection(0, 1.8*self.width())
        self.setIndentation(12)
        self.headerItem().setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        self.setMinimumWidth(self.parent().parent().width()*0.47)

        # 0: primeiro da lista top level
        data_container = ExploreItem(ExploreItem.ContainerType.ContainerData, ["Data", "Container"])
        self.insertTopLevelItem(0, data_container)
        self.topLevelItem(0).setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        # 1: segundo da lista top level
        model_container = ExploreItem(ExploreItem.ContainerType.ContainerModel, ["Models", "Container"])
        self.insertTopLevelItem(1, model_container)
        self.topLevelItem(1).setTextAlignment(1, Qt.AlignmentFlag.AlignRight)


    def topLevelItem(self, index: int) -> ExploreItem:
        return super().topLevelItem(index)

    def selection_changed(self):
        
        selected_items = self.selectedItems()

        for item in selected_items:
            if item not in self.itemsSelected:
                item.setBackground(0, QColor("lightgreen"))
                item.setBackground(1, QColor("lightgreen"))
        for item in self.itemsSelected:
            if item not in selected_items:
                item.setBackground(0, QColor("white"))
                item.setBackground(1, QColor("white"))
        
        self.itemsSelected = selected_items

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key.Key_Space,Qt.Key.Key_Return,Qt.Key.Key_Enter]:
            self.selectReturned.emit(self.itemsSelected)
        elif event.key() in [Qt.Key.Key_G,Qt.Key.Key_P, Qt.Key.Key_T,
                             Qt.Key.Key_A, Qt.Key.Key_Backspace,
                             Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3,
                             Qt.Key.Key_4, Qt.Key.Key_5, Qt.Key.Key_6,
                             Qt.Key.Key_7, Qt.Key.Key_8, Qt.Key.Key_9]:
            self.keyPressed.emit(event)
        else:
            return super().keyPressEvent(event)
        

    def insertID(self, ID, IDType: ExploreItem.IDType, name=''):
        
        ID.name = name

        if IDType.value:
            container = self.topLevelItem(0)
            id_item = ExploreItem(IDType, container, [ID.name, "FieldMap"])
        else:
            container = self.topLevelItem(1)
            id_item = ExploreItem(IDType, container, [ID.name, "Model"])

        id_item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        if not container.isExpanded():
            self.expandItem(container)
