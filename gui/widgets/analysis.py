
from PyQt6.QtWidgets import QPushButton, QFrame, QListWidget, QListWidgetItem, QCheckBox, QVBoxLayout, QDialog
from PyQt6.QtGui import QIcon, QWindow
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QTimer

from .dialog_layouts import AnalysisLayout


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



class AnalysisMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.WindowType.Popup)

        # analysis menu

        ## analysis menu - style
        self.setObjectName("frame")
        self.setStyleSheet("QFrame#frame{background-color: #f0f0f0; border: 1.2px solid #c0c0c0}")
        
        ## analysis menu - list
        self.list = QListWidget(parent=self)
        self.list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.list.setStyleSheet("background-color: #f0f0f0")

        ### analysis menu - list - items:
        ### Create the items and automatically add them to the list widget
        self.itemCrossTalk = AnalysisItem(text="Cross Talk",parent=self.list)
        self.itemMagneticField = AnalysisItem(text="Magnetic Field",parent=self.list)
        self.itemTrajectory = AnalysisItem(text="Trajectory",parent=self.list)
        self.itemPhaseError = AnalysisItem(text="Phase Error",parent=self.list)
        self.itemIntegrals = AnalysisItem(text="Field Integrals",parent=self.list)
        # kickmap temporariamente fora, pois nao esta devidamente implementado no imaids
        #self.itemKickmap = AnalysisItem(text="Kickmap",parent=self.list)
        # multipolos e multipolos dinamicos em avaliacao
        self.itemRollOffPeaks = AnalysisItem(text="Roll Off Peaks",parent=self.list)
        self.itemRollOffAmp = AnalysisItem(text="Roll Off Amplitude",parent=self.list)
        # shimming fora, pois e' um calculo muito personalizado e que exige cuidado
        #self.Shimming = AnalysisItem(text="Shimming",parent=self.list)
        
        self.itemMagneticField.setSuperior(self.itemIntegrals)
        self.itemTrajectory.setSuperior(self.itemPhaseError)
        self.itemPhaseError.setSubordinate(self.itemTrajectory)
        #print('phase error tem subordinado:',self.itemPhaseError.hasSubordinate())
        self.itemIntegrals.setSubordinate(self.itemMagneticField)
        
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)

        self.items = [self.list.item(i) for i in range(self.list.count())]

        ### analysis menu - list - signals
        self.list.itemClicked.connect(self.item_clicked)
        self.list.itemChanged.connect(lambda: setattr(self, 'changed', True))
        #self.list.itemChanged.connect(self.item_changed)

        self.changed = False

        ## analysis menu - checkbox
        self.checkBoxSelectAll = QCheckBox("Select All",self)
        self.checkBoxSelectAll.clicked.connect(self.check_all_items)

        ## analysis menu - apply button
        self.apply = QPushButton("Apply")
        self.apply.setShortcut(Qt.Key.Key_Return)
        self.apply.clicked.connect(self.applyHide)

        ## analysis menu - hide timer
        self.timerHide = QTimer()
        self.timerHide.timeout.connect(lambda: self.timerHide.stop())
        self.timerHide.setInterval(100)
        
        ## analysis menu - layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.list)
        layout.addWidget(self.checkBoxSelectAll)
        layout.addWidget(self.apply)


        self.installEventFilter(self)
        #self.parent().installEventFilter(self)




    # FUNCTIONS

    # list functions

    def checkedItems(self):
        return [item for item in self.items if item.checkState()==Qt.CheckState.Checked]
    
    def uncheckedItems(self):
        return [item for item in self.items if item.checkState()==Qt.CheckState.Unchecked]

    def uncheckAnalysisMenu(self):
        # uncheck all checked list items
        [item.setCheckState(Qt.CheckState.Unchecked) for item in self.checkedItems()]

        # uncheck checkbox, items and remove wand icon
        if self.checkBoxSelectAll.isChecked():
            self.checkBoxSelectAll.setChecked(False)
            self.check_all_items(False)

    # SLOTS

    # list slot

    def item_clicked(self, item: AnalysisItem):
        print('item clicado')
        
        # caso o usuario marque tudo, depois clique em um item
        if self.checkBoxSelectAll.isChecked():
            self.checkBoxSelectAll.setChecked(False)

        # restaurando estado do item antes de clicar na checkbox
        if self.changed:
            # setcheckstate de qlistwidget para nao alterar estado dos subordinados tambem
            QListWidgetItem.setCheckState(item,Qt.CheckState(2-item.checkState().value))

        '''#item checkbox clicked
        if self.changed:
            # se o superior estiver marcado
            if item.hasSuperior() and item.isSuperiorsChecked():
                item.setCheckState(Qt.CheckState(2-item.checkState().value))
            if item.hasSubordinate() and item.checkState().value:
                [subordinate.setCheckState(item.checkState()) for subordinate in item.subordinates]
        
        #item label clicked (not item checkbox)
        else:
            if not item.hasSuperior() or (item.hasSuperior() and not item.isSuperiorsChecked()):
                item.setCheckState(Qt.CheckState(2-item.checkState().value))'''
        
        # mudar estado de item comum, sem superior
        # bloquear mudanca de estado para item subordinado a outro quando algum
        # de seus superiores estiver checked
        if  (not item.hasSuperior()) or \
            (item.hasSuperior() and not item.isSuperiorsChecked()):

            item.setCheckState(Qt.CheckState(2-item.checkState().value))

        # restaurando changed ao seu valor padrao
        self.changed = False
        

        # alterar ou nao icone do apply
        if len(self.checkedItems())==self.list.count():
            self.checkBoxSelectAll.setChecked(True)
            self.toggle_icon(state=2)
        else:
            self.toggle_icon(state=0)
    

    # checkbox slot: check todos os items da lista

    def check_all_items(self,checked):
        if checked:
            for item in self.uncheckedItems():
                item.setCheckState(Qt.CheckState.Checked)
        else:
            for item in self.checkedItems():
                item.setCheckState(Qt.CheckState.Unchecked)
        
        self.toggle_icon(state=checked)

        # ao final dos comandos passados no metodo, changed muda para True,
        # e´preciso retomar ele ao seu valor padrao
        self.changed = False
    

    # apply button slots

    # coloca ou tira icone da varinha do botao apply
    def toggle_icon(self,state):
        if state:
            self.apply.setIcon(QIcon('icons/icons/wand.png'))
        else:
            self.apply.setIcon(QIcon(None))
    
    # funcionalidades do apply
    def applyHide(self):
        self.setHidden(True)

    def eventFilter(self, obj, event: QEvent):

        if event.type()==QEvent.Type.MouseButtonPress:

            geometry = self.parent().geometry()
            geometry.moveTo(0,-geometry.height())

            if geometry.contains(event.pos()):
                self.timerHide.start()
            
        return super().eventFilter(obj, event)


class AnalysisPushButton(QPushButton):

    modeChanged = pyqtSignal(bool)

    def __init__(self, text, parent, *args, **kwargs):
        super().__init__(text=text, parent=parent, *args, **kwargs)

        # features
        self.setCheckable(True)
        self.setShortcut("Ctrl+A")
        # signal
        self.clicked.connect(self.showMenu)
        # menu
        
        self.Menu = AnalysisMenu(parent=self)
        self.Menu.apply.clicked.connect(self.applyChangeMode)

    
    def showMenu(self):
        # se botao inicialmente estiver checked
        #todo: transformar em painted button para abrir menu e mudar analises de modo mais simples
        if not self.isChecked():
            # analysis button automatically unchecks itself
            self.Menu.uncheckAnalysisMenu()
            self.modeChanged.emit(True)

        # se botao inicialmente estiver unchecked
        else:
            # uncheck the analysis button
            self.setChecked(False)
            print('executou click botao')

            # expose the menu
            if not self.Menu.timerHide.isActive():
                # positionate the menu
                corner = self.parent().mapToGlobal(self.geometry().bottomLeft())
                self.Menu.setGeometry(corner.x()+1, corner.y(), 160, 220)
                self.Menu.show()

            # restaura valor padrao de changed
            self.Menu.changed = False
    
    def applyChangeMode(self):
        if self.Menu.checkedItems():
            self.modeChanged.emit(False)



class AnalysisDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Analysis Parameters")

        self.layoutAnalysis = AnalysisLayout(parent=self)

        # signals
        ## signal sent from Ok button to the handler accept of QDialog class
        self.layoutAnalysis.buttonBox.accepted.connect(self.accept)
        ## signal sent from Ok button to the handler reject of QDialog class
        self.layoutAnalysis.buttonBox.rejected.connect(self.reject)


    # def analysis_chose(self, index):
    #     if index==1:

        