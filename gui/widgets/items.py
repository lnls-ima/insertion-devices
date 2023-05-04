
import enum
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTreeWidgetItem, QListWidgetItem


class ExploreItem(QTreeWidgetItem):

    class Type(enum.Enum):
        ContainerData = 0
        ContainerModel = 1
        ItemData = 2
        ItemModel = 3
        ItemMagneticField = 4
        ItemTrajectory = 5
        ItemPhaseError = 6
        ItemIntegrals = 7
        ItemRollOffPeaks = 8
        ItemRollOffAmp = 9
        ItemResult = 10

    def __init__(self, item_type: 'ExploreItem.Type', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.item_type = item_type



    def children(self):
        return [self.child(i) for i in range(self.childCount())]


class AnalysisItem(QListWidgetItem):

    #*: da maneira implementada aqui, um subordinado pode ter outros subordinados
    #*: e isso deve se comportar bem no menu
    def __init__(self, superiors=[], subordinates=[], text='', parent=None,
                 *args, **kwargs):
        super().__init__(text, parent, *args, **kwargs)

        self.superiors = superiors #list of superior items of this item
        self.subordinates = subordinates #list of subordinate items of this item
        
    

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