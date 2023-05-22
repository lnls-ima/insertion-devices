
from enum import Enum
from PyQt6 import sip
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTreeWidgetItem, QListWidgetItem


class ExploreItem(QTreeWidgetItem):

    class Container(Enum):
        ContainerData = 0
        ContainerModel = 1

    class IDType(Enum):
        IDData = 0
        IDModel = 1
    
    #*: na tree, de analysis items pra baixo, nao podera' renomear
    class Analysis(Enum):
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

        self.item_type = item_type

    def delete(self):
        sip.delete(self)

    def children(self):
        return [self.child(i) for i in range(self.childCount())]
    
    def parent(self) -> 'ExploreItem':
        return super().parent()
    
    def depth(self):
        
        if self.parent() is None:
            return 0
        else:
            return self.parent().depth()+1
        
    def idName(self):

        depth = self.depth()

        if depth==1:
            id_name = self.text(0)
        elif depth==2:
            id_name = self.parent().text(0)
        elif depth==3:
            id_name = self.parent().parent().text(0)
        
        return id_name


class AnalysisItem(QListWidgetItem):

    #*: da maneira implementada aqui, um subordinado pode ter outros subordinados
    #*: e isso deve se comportar bem no menu
    def __init__(self, superiors=[], subordinates=[], text='', parent=None,
                 *args, **kwargs):
        super().__init__(text, parent, *args, **kwargs)

        self.superiors = superiors #list of superior items of this item
        self.subordinates = subordinates #list of subordinate items of this item
        
    def isChecked(self) -> bool:
        return bool(self.checkState() == Qt.CheckState.Checked)

    def hasSuperior(self) -> bool:
        return bool(len(self.superiors))
    
    def isSuperiorsChecked(self) -> bool:
        return sum([superior.checkState().value for superior in self.superiors])

    def setSuperior(self, item: 'AnalysisItem'):
        self.superiors = [item]

    def hasSubordinate(self) -> bool:
        return bool(len(self.subordinates))
    
    def setSubordinate(self, item: 'AnalysisItem'):
        self.subordinates = [item]
    
    def setCheckState(self, state: Qt.CheckState) -> None:
        
        if self.hasSubordinate() and state.value: #desmarcar item e nao desmarcar seus subordinados
        #if self.hasSubordinate(): #desmarcar item e desmarcar seus subordinados
            [subordinate.setCheckState(state) for subordinate in self.subordinates]
        return super().setCheckState(state)