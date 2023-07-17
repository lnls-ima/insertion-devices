
from enum import Enum
from PyQt6 import sip
import numpy as np
from PyQt6.QtWidgets import QTreeWidgetItem, QTreeWidget, QMenu
from PyQt6.QtGui import QColor, QKeyEvent
from PyQt6.QtCore import pyqtSignal, Qt, QItemSelectionModel, QItemSelection


class ExploreItem(QTreeWidgetItem):

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
        self.status_tip = ""

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

    def set_Status_Tip(self) -> None:
        self.setStatusTip(0,self.status_tip)
    
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


    @classmethod
    def calcMagnetic_Field(cls, analysis_item, id_dict: dict, field_kwargs):
        rtArray = cls.ResultType.ResultArray
        rtNumber = cls.ResultType.ResultNumeric

        ID = id_dict["InsertionDeviceObject"]
        x, y, z = field_kwargs["x"], field_kwargs["y"], field_kwargs["z"]
        B = ID.get_field(**field_kwargs)
        Bx, By, Bz = B.T
        id_dict[analysis_item.text(0)] = {"x [mm]": x, "y [mm]": y, "z [mm]": z,
                                          "Bx [T]": Bx, "By [T]": By, "Bz [T]": Bz}

        numericCounter = 0
        try:
            x_item = cls(rtNumber, analysis_item, ["x [mm]", f"{x:.1f}"])
            numericCounter += 1
        except:
            x_item = cls(rtArray, analysis_item, ["x [mm]", "List"])
        try:
            y_item = cls(rtNumber, analysis_item, ["y [mm]", f"{y:.1f}"])
            numericCounter += 1
        except:
            y_item = cls(rtArray, analysis_item, ["y [mm]", "List"])
        try:
            z_item = cls(rtNumber, analysis_item, ["z [mm]", f"{z:.1f}"])
            numericCounter += 1
        except:
            z_item = cls(rtArray, analysis_item, ["z [mm]", "List"])

        if numericCounter == 3:
            field_items = [cls(rtNumber, analysis_item, ["Bx [T]", f"{Bx[0]:.1f}"]),
                           cls(rtNumber, analysis_item, ["By [T]", f"{By[0]:.1f}"]),
                           cls(rtNumber, analysis_item, ["Bz [T]", f"{Bz[0]:.1f}"])]
        else:
            field_items = [cls(rtArray, analysis_item, ["Bx [T]", "List"]),
                           cls(rtArray, analysis_item, ["By [T]", "List"]),
                           cls(rtArray, analysis_item, ["Bz [T]", "List"])]

        result_items = [x_item,y_item,z_item]+field_items

        return result_items
        
    @classmethod
    def calcTrajectory(cls, analysis_item, id_dict: dict, traj_kwargs):
        rtArray = cls.ResultType.ResultArray

        ID = id_dict["InsertionDeviceObject"]
        traj = ID.calc_trajectory(**traj_kwargs)
        x, y, z, dxds, dyds, dzds = traj.T
        id_dict[analysis_item.text(0)] = {"x [mm]": x, "y [mm]": y, "z [mm]": z,
                                          "x' [rad]": dxds, "y' [rad]": dyds, "z' [rad]": dzds}

        result_items = [cls(rtArray, analysis_item, ["x [mm]", "List"]),
                        cls(rtArray, analysis_item, ["y [mm]", "List"]),
                        cls(rtArray, analysis_item, ["z [mm]", "List"]),
                        cls(rtArray, analysis_item, ["x' [rad]", "List"]),
                        cls(rtArray, analysis_item, ["y' [rad]", "List"]),
                        cls(rtArray, analysis_item, ["z' [rad]", "List"])]
        
        return result_items
    
    @classmethod
    def calcPhase_Error(cls, analysis_item, id_dict: dict, phaserr_kwargs):
        rtArray = cls.ResultType.ResultArray
        rtNumber = cls.ResultType.ResultNumeric

        ID = id_dict["InsertionDeviceObject"]
        traj_dict = id_dict[cls.AnalysisType.Trajectory.value]
        traj = np.array(list(traj_dict.values())).T
        bxamp, byamp, _, _ = ID.calc_field_amplitude()
        energy = phaserr_kwargs["energy"]
        skip_poles = phaserr_kwargs["skip_poles"]
        zmin = phaserr_kwargs["zmin"]
        zmax = phaserr_kwargs["zmax"]
        field_comp = phaserr_kwargs["field_comp"]
        z_list, pe, pe_rms = ID.calc_phase_error(energy, traj, bxamp, byamp, skip_poles, zmin, zmax, field_comp)
        #chaves do dicionario no membro direito devem ser iguais aos nomes usados nos respectivos items
        id_dict[analysis_item.text(0)] = {"z poles [mm]": z_list, "PhaseErr [deg]": pe*180/np.pi, "RMS [deg]": pe_rms*180/np.pi}

        result_items = [cls(rtArray, analysis_item, ["z poles [mm]", "List"]),
                        cls(rtArray, analysis_item, ["PhaseErr [deg]", "List"]),
                        cls(rtNumber, analysis_item, ["RMS [deg]", f"{pe_rms*180/np.pi:.1f}"])]
        
        return result_items
        
    @classmethod
    def calcField_Integrals(cls, analysis_item, id_dict: dict, integrals_kwargs):
        rtArray = cls.ResultType.ResultArray
        rtNumber = cls.ResultType.ResultNumeric

        ID = id_dict["InsertionDeviceObject"]
        ib, iib = ID.calc_field_integrals(**integrals_kwargs)
        ibx, iby, ibz = ib.T
        iibx, iiby, iibz = iib.T
        id_dict[analysis_item.text(0)] = {'z [mm]': integrals_kwargs["z_list"],
                                          'IBx [G.cm]': ibx, 'IBy [G.cm]': iby, 'IBz [G.cm]': ibz,
                                          'IIBx [kG.cm2]': iibx, 'IIBy [kG.cm2]': iiby, 'IIBz [kG.cm2]': iibz}

        result_items = [cls(rtArray,  analysis_item, ['z [mm]',  "List"]),
                        cls(rtArray,  analysis_item, ['IBx [G.cm]',  "List"]),
                        cls(rtArray,  analysis_item, ['IBy [G.cm]',  "List"]),
                        cls(rtArray,  analysis_item, ['IBz [G.cm]',  "List"]),
                        cls(rtArray,  analysis_item, ['IIBx [kG.cm2]', "List"]),
                        cls(rtArray,  analysis_item, ['IIBy [kG.cm2]', "List"]),
                        cls(rtArray,  analysis_item, ['IIBz [kG.cm2]', "List"])]
        
        return result_items
        
    @classmethod
    def calcRoll_Off_Peaks(cls, analysis_item, id_dict: dict, rop_kwargs):
        rtArray = cls.ResultType.ResultArray

        ID = id_dict["InsertionDeviceObject"]
        ropx, ropy, ropz = ID.calc_roll_off_peaks(**rop_kwargs)
        id_dict[analysis_item.text(0)] = {'ROPx': ropx,'ROPy': ropy,'ROPz': ropz}

        result_items = [cls(rtArray, analysis_item, ['ROPx',  "List"]),
                        cls(rtArray, analysis_item, ['ROPy',  "List"]),
                        cls(rtArray, analysis_item, ['ROPz',  "List"])]
        
        return result_items

    #todo: por que em certas fazes roai varia tanto em relacao aos demais
    #porque o campo nessa componente e' quase nulo, o que faz o calculo produzir erros numericos
    #todo: parte da janela de visualizacao deve permitir esconder ou mostrar linhas/legendas graficadas
    @classmethod
    def calcRoll_Off_Amplitude(cls, analysis_item, id_dict: dict, roa_kwargs):
        rtArray = cls.ResultType.ResultArray
        rtNumber = cls.ResultType.ResultNumeric

        ID = id_dict["InsertionDeviceObject"]
        x, y = roa_kwargs["x"], roa_kwargs["y"]
        roax, roay, roaz = ID.calc_roll_off_amplitude(**roa_kwargs)
        id_dict[analysis_item.text(0)] = {'x [mm]': x, 'y [mm]': y,
                                          'ROAx': roax,'ROAy': roay,'ROAz': roaz}

        result_items = [cls(rtArray, analysis_item, ['x [mm]',  "List"]),
                        cls(rtNumber, analysis_item, ['y [mm]',  f"{y:.1f}"]),
                        cls(rtArray, analysis_item, ['ROAx',  "List"]),
                        cls(rtArray, analysis_item, ['ROAy',  "List"]),
                        cls(rtArray, analysis_item, ['ROAz',  "List"])]
        
        return result_items

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
    noItemClicked = pyqtSignal()

    def __init__(self, parent=None,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)

        self.files_visible = False

        self.itemsSelected = []

        self.itemSelectionChanged.connect(self.selection_changed)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.setMouseTracking(True)
        self.setColumnCount(2)
        self.setHeaderLabels(["Item", "Content"])
        #self.setHeaderHidden(True)
        self.header().resizeSection(0, 1.8*self.width())
        self.setIndentation(12)
        self.headerItem().setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        self.setMinimumWidth(self.parent().parent().width()*0.47)

        # 0: primeiro da lista top level
        ctnData = ExploreItem.ContainerType.ContainerData
        data_container = ExploreItem(ctnData, ["Data", "Container"])
        data_container.setStatusTip(0,"Container for the undulator field maps data loaded")
        self.insertTopLevelItem(0, data_container)
        self.topLevelItem(0).setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        # 1: segundo da lista top level
        ctnModel = ExploreItem.ContainerType.ContainerModel
        model_container = ExploreItem(ctnModel, ["Models", "Container"])
        model_container.setStatusTip(0,"Container for the undulator models constructed")
        self.insertTopLevelItem(1, model_container)
        self.topLevelItem(1).setTextAlignment(1, Qt.AlignmentFlag.AlignRight)

        self.menuContextID = QMenu(self)
        self.menuContextID.addAction("Summary")
        self.menuContextID.addAction("Save field map")

        self.menuContextTraj = QMenu(self)
        self.menuContextTraj.addAction("Save Trajectory")

    def isFilesVisible(self):
        return self.files_visible
    
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

    
    def mousePressEvent(self, event) -> None:
        if not self.indexAt(event.pos()).isValid():
            self.noItemClicked.emit()
        print('clique na tree:',event.pos())
        return super().mousePressEvent(event)


    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key.Key_Space,Qt.Key.Key_Return,Qt.Key.Key_Enter]:
            self.selectReturned.emit(self.itemsSelected)
        elif event.key() in [Qt.Key.Key_A, Qt.Key.Key_Backspace,
                             Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3,
                             Qt.Key.Key_4, Qt.Key.Key_5, Qt.Key.Key_6,
                             Qt.Key.Key_7, Qt.Key.Key_8, Qt.Key.Key_9]:
            self.keyPressed.emit(event)
        else:
            return super().keyPressEvent(event)
        

    def insertID(self, ID, IDType: ExploreItem.IDType, filename='', name=''):

        ID.name = name

        if IDType.value:
            container = self.topLevelItem(0)
            id_item = ExploreItem(IDType, container, [ID.name, "FieldMap"])
            filename = "../"+"/".join(filename.split("/")[3:])
            id_item.status_tip = "File: "+filename
        else:
            container = self.topLevelItem(1)
            id_item = ExploreItem(IDType, container, [ID.name, "Model"])

        id_item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        if not container.isExpanded():
            self.expandItem(container)
