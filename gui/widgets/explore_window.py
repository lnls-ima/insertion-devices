
from enum import Enum
from PyQt6 import sip
import numpy as np
from PyQt6.QtWidgets import QTreeWidgetItem, QTreeWidget, QMenu, QInputDialog, QMessageBox, QDockWidget
from PyQt6.QtGui import QColor, QKeyEvent, QIcon
from PyQt6.QtCore import pyqtSignal, Qt, QItemSelectionModel, QItemSelection

from .basics import BasicTreeWidget
from . import get_path

class ExploreItem(QTreeWidgetItem):

    class ContainerType(Enum):
        ContainerData = 0
        ContainerModel = 1
        ContainerAnalyses = 2
        ContainerResults = 3

    class IDType(Enum):
        IDModel = 0
        IDData = 1
    
    #*: na tree, de analysis items pra baixo, nao podera' renomear
    class AnalysisType(Enum):
        CrossTalk = "Cross Talk"
        MagneticField = "Magnetic Field"
        Trajectory = "Trajectory"
        PhaseError = "Phase Error"
        Integrals = "Cumulative Integrals"
        IntegralsH = "Field Integrals vs X"
        RollOffPeaks = "Roll Off Peaks"
        RollOffAmp = "Roll Off Amplitude"
        HarmTuning = "Harmonics Tuning"
        Brilliance = "Brilliance"
        FluxDensity = "Flux Density"
        Custom = "Custom"
    
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

    def children(self) -> dict:
        return dict([(self.child(i).text(0),self.child(i)) for i in range(self.childCount())])
    
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
        x, y, z = [np.float64(i) for i in [x,y,z]]
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
        num_trajs = len([label for label in id_dict.keys()
                           if "Trajectory" in label])
        last_traj = "Trajectory" if num_trajs==1 else f"Trajectory {num_trajs}"
        traj_dict = id_dict[last_traj]
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
    def calcCumulative_Integrals(cls, analysis_item, id_dict: dict, integrals_kwargs):
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
    def calcField_Integrals_vs_X(cls, analysis_item, id_dict: dict, integralsH_kwargs):
        rtArray = cls.ResultType.ResultArray
        rtNumber = cls.ResultType.ResultNumeric

        ID = id_dict["InsertionDeviceObject"]
        z, x_list, y = integralsH_kwargs.values()

        ib, iib = [], []
        for x in x_list:
            intb, intintb = ID.calc_field_integrals(x=x,y=y,z_list=z)
            ib.append(intb[-1,:])
            iib.append(intintb[-1,:])
        ib = np.array(ib)
        iib = np.array(iib)
        
        id_dict[analysis_item.text(0)] = {'x [mm]': x_list,
                                          'IBx [G.cm]': ib[:,0], 'IBy [G.cm]': ib[:,1],
                                          'IBz [G.cm]': ib[:,2], 'IIBx [kG.cm2]': iib[:,0],
                                          'IIBy [kG.cm2]': iib[:,1], 'IIBz [kG.cm2]': iib[:,2]}

        result_items = [cls(rtArray,  analysis_item, ['x [mm]',  "List"]),
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
        x = rop_kwargs["x"]
        ropx, ropy, ropz = 100*ID.calc_roll_off_peaks(**rop_kwargs)

        if len(ropx):
            id_dict[analysis_item.text(0)] = {'x [mm]': x,
                                              'ROPx [%]': ropx.T,'ROPy [%]': ropy.T,'ROPz [%]': ropz.T}

            result_items = [cls(rtArray, analysis_item, ['x [mm]',  "List"]),
                            cls(rtArray, analysis_item, ['ROPx [%]',  "List"]),
                            cls(rtArray, analysis_item, ['ROPy [%]',  "List"]),
                            cls(rtArray, analysis_item, ['ROPz [%]',  "List"])]
        else:
            result_items = []
        
        return result_items

    #todo: por que em certas fazes roai varia tanto em relacao aos demais
    #porque o campo nessa componente e' quase nulo, o que faz o calculo produzir erros numericos
    #todo: parte da janela de visualizacao deve permitir esconder ou mostrar linhas/legendas graficadas
    @classmethod
    def calcRoll_Off_Amplitude(cls, analysis_item, id_dict: dict, roa_kwargs):
        rtArray = cls.ResultType.ResultArray

        ID = id_dict["InsertionDeviceObject"]
        x = roa_kwargs["x"]
        roax, roay, roaz = 100*ID.calc_roll_off_amplitude(**roa_kwargs)
        id_dict[analysis_item.text(0)] = {'x [mm]': x,
                                          'ROAx [%]': roax,'ROAy [%]': roay,'ROAz [%]': roaz}

        result_items = [cls(rtArray, analysis_item, ['x [mm]',  "List"]),
                        cls(rtArray, analysis_item, ['ROAx [%]',  "List"]),
                        cls(rtArray, analysis_item, ['ROAy [%]',  "List"]),
                        cls(rtArray, analysis_item, ['ROAz [%]',  "List"])]
        
        return result_items

    @classmethod
    def calcHarmonics_Tuning(cls, analysis_item, id_dict: dict, tuning_kwargs):
        rtArray = cls.ResultType.ResultArray
        rtNumber = cls.ResultType.ResultNumeric

        ID = id_dict["InsertionDeviceObject"]

        harm_energy, flux = ID.calc_radiation_tuning(**tuning_kwargs)

        id_dict[analysis_item.text(0)] = {}
        result_items = []
        for i, h_energy in enumerate(harm_energy.T):
            id_dict[analysis_item.text(0)][f'Harmonic {2*i+1} Energy [eV]'] = h_energy
            result_items.append(cls(rtArray, analysis_item, [f'Harmonic {2*i+1} Energy [eV]', "List"]))
        for i, h_flux in enumerate(flux.T):
            id_dict[analysis_item.text(0)][f'Flux {2*i+1} [photons/s/0.1%BW]'] = h_flux
            result_items.append(cls(rtArray, analysis_item, [f'Flux {2*i+1} [photons/s/0.1%BW]', "List"]))
        
        return result_items
    
    @classmethod
    def calcBrilliance(cls, analysis_item, id_dict: dict, brilliance_kwargs):
        rtArray = cls.ResultType.ResultArray

        ID = id_dict["InsertionDeviceObject"]

        harm_energy, flux = ID.calc_radiation_brilliance(**brilliance_kwargs)

        id_dict[analysis_item.text(0)] = {}
        result_items = []
        for i, h_energy in enumerate(harm_energy.T):
            id_dict[analysis_item.text(0)][f'Harmonic {2*i+1} Energy [eV]'] = h_energy
            result_items.append(cls(rtArray, analysis_item, [f'Harmonic {2*i+1} Energy [eV]', "List"]))
        for i, h_flux in enumerate(flux.T):
            id_dict[analysis_item.text(0)][f'Brilliance {2*i+1} [photons/s/mm2/mrad2/0.1%BW]'] = h_flux
            result_items.append(cls(rtArray, analysis_item, [f'Brilliance {2*i+1} [photons/s/mm2/mrad2/0.1%BW]', "List"]))
        
        return result_items

    @classmethod
    def calcFlux_Density(cls, analysis_item, id_dict: dict, fluxD_kwargs):
        rtArray = cls.ResultType.ResultArray

        ID = id_dict["InsertionDeviceObject"]

        energy, flux_density = ID.calc_radiation_flux_density(**fluxD_kwargs)

        id_dict[analysis_item.text(0)] = {"Energy [eV]": energy, "Flux D.": flux_density}
        result_items = [cls(rtArray, analysis_item, ['Energy [eV]', "List"]),
                        cls(rtArray, analysis_item, ['Flux D. [ph/s/mrad2/0.1%BW]', "List"])]
        
        return result_items

    def calcCross_Talk(self, id_dict: dict, correction_kwargs):
    
        id_item = self.parent()

        ID = id_dict["InsertionDeviceObject"]
        ID.correct_angles(**correction_kwargs["angles"])
        ID.correct_cross_talk(**correction_kwargs["cross_talk"])
        id_dict[self.text(0)] = True
        
        self.delete()
        id_item.setIcon(0,QIcon(get_path('icons','data-tick.png')))
        
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



class ExploreTreeWidget(BasicTreeWidget):

    keyPressed = pyqtSignal(QKeyEvent)
    noItemClicked = pyqtSignal()

    def __init__(self, parent=None,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)

        self.files_visible = False

        self.itemsSelected = []

        self.itemSelectionChanged.connect(self.selection_changed)
        
        self.header().resizeSection(0, 1.8*self.width())
        self.setMinimumWidth(self.parent().parent().width()*0.47)

        # Container items
        ## 0: primeiro da lista top level
        ctnData = ExploreItem.ContainerType.ContainerData
        data_container = ExploreItem(ctnData, ["Data", "Container"])
        data_container.setStatusTip(0,"Container for the undulator field maps data loaded")
        self.insertTopLevelItem(0, data_container)
        self.topLevelItem(0).setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        ## 1: segundo da lista top level
        ctnModel = ExploreItem.ContainerType.ContainerModel
        model_container = ExploreItem(ctnModel, ["Models", "Container"])
        model_container.setStatusTip(0,"Container for the undulator models constructed")
        self.insertTopLevelItem(1, model_container)
        self.topLevelItem(1).setTextAlignment(1, Qt.AlignmentFlag.AlignRight)

        # Menus
        self.menuContextAnalysis = QMenu(self)
        self.menuContextAnalysis.addAction("Delete")
        
        self.menuContextIDData = QMenu(self)
        self.menuContextIDData.addAction("Rename ...")
        self.menuContextIDData.addAction("Summary ...")
        self.menuContextIDData.addAction("Save field map ...")
        self.menuContextIDData.addAction("Delete")

        self.menuContextIDModel = QMenu(self)
        self.menuContextIDModel.addAction("Rename ...")
        self.menuContextIDModel.addAction("Delete")

        self.menuContextTraj = QMenu(self)
        self.menuContextTraj.addAction("Save Trajectory")
        self.menuContextTraj.addAction("Delete")

        # Operation dock
        ## dock widget
        self.dockOperations = QDockWidget("Operation Window")
        self.dockOperations.setHidden(True)
        ## tree widget
        self.treeOperations = BasicTreeWidget(parent=self.dockOperations)
        self.treeOperations.header().resizeSection(0, 0.6*self.width())
        ### containers
        ctnAnalyses = ExploreItem.ContainerType.ContainerAnalyses
        analyses_container = ExploreItem(ctnAnalyses,["Analyses", "Container"])
        analyses_container.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        analyses_container.setStatusTip(0,"Container for the operated analyses")
        self.treeOperations.insertTopLevelItem(0, analyses_container)
        ctnResults = ExploreItem.ContainerType.ContainerResults
        results_container = ExploreItem(ctnResults,["Results", "Container"])
        results_container.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        results_container.setStatusTip(0,"Container for the operated results")
        self.treeOperations.insertTopLevelItem(1, results_container)

        self.dockOperations.setWidget(self.treeOperations)

    

    def isFilesVisible(self):
        return self.files_visible
    
    def topLevelItem(self, index: int) -> ExploreItem:
        return super().topLevelItem(index)

    # talvez tenha algo inerente a tree widget que faça a mesma coisa que o abaixo
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
        if event.key() in [Qt.Key.Key_A, Qt.Key.Key_Backspace,
                           Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3,
                           Qt.Key.Key_4, Qt.Key.Key_5, Qt.Key.Key_6,
                           Qt.Key.Key_7, Qt.Key.Key_8, Qt.Key.Key_9]:
            self.keyPressed.emit(event)
        else:
            return super().keyPressEvent(event)
        

    def insertID(self, ID, IDType: ExploreItem.IDType, correct=False, filename='', name=''):

        ID.name = name

        #IDData value is 1 and IDModel is 0
        if IDType.value:
            container = self.topLevelItem(0)
            id_item = ExploreItem(IDType, container, [ID.name, "FieldMap"])
            if correct:
                id_item.setIcon(0,QIcon(get_path('icons','data-tick.png')))
            else:
                id_item.setIcon(0,QIcon(get_path('icons','data.png')))
            filename = "../"+"/".join(filename.split("/")[3:])
            id_item.status_tip = "File: "+filename
        else:
            container = self.topLevelItem(1)
            id_item = ExploreItem(IDType, container, [ID.name, "Model"])
            id_item.setIcon(0,QIcon(get_path('icons','model.png')))

        id_item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        if not container.isExpanded():
            self.expandItem(container)
        
        return id_item
