
from PyQt6.QtWidgets import QPushButton, QFrame, QListWidget, QListWidgetItem, QCheckBox, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QRect, pyqtSignal

from .items import AnalysisItem


class AnalysisPushButton(QPushButton):

    modeChanged = pyqtSignal(bool)

    def __init__(self, menu_parent, button_text, button_parent, *args, **kwargs):
        super().__init__(text=button_text, parent=button_parent, *args, **kwargs)

        # analysis button
        ## analysis button - features
        self.setCheckable(True)
        self.setShortcut("Ctrl+A")
        ## analysis button - signal
        self.clicked.connect(self.toggle_list_visibility)


        # analysis menu

        ## analysis menu - style
        self.Menu = QFrame(parent=menu_parent)
        self.Menu.setObjectName("frame")
        self.Menu.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.Menu.setLineWidth(1)
        self.Menu.setStyleSheet("QFrame#frame{background-color: #f0f0f0}")
        self.Menu.setHidden(True)
        
        ## analysis menu - list
        self.list = QListWidget(parent=self.Menu)
        self.list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.list.setStyleSheet("background-color: #f0f0f0")

        ### analysis menu - list - items:
        ### Create the items and automatically add them to the list widget
        self.itemMagneticField = AnalysisItem(text="Magnetic Field",parent=self.list)
        self.itemTrajectory = AnalysisItem(text="Trajectory",parent=self.list)
        self.itemPhaseError = AnalysisItem(text="Phase Error",parent=self.list)
        self.itemIntegrals = AnalysisItem(text="Field Integrals",parent=self.list)
        # kickmap temporariamente fora, pois nao esta devidamente implementado no imaids
        #self.itemKickmap = AnalysisItem(text="Kickmap",parent=self.list)
        # multipolos e multipolos dinamicos em avaliacao
        self.itemRollOffPeaks = AnalysisItem(text="Roll Off Peaks",parent=self.list)
        self.itemRollOffAmp = AnalysisItem(text="Roll Off Amplitude",parent=self.list)
        self.itemCrossTalk = AnalysisItem(text="Cross Talk",parent=self.list)
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
        
        ## analysis menu - layout
        layout = QVBoxLayout(self.Menu)
        layout.addWidget(self.list)
        layout.addWidget(self.checkBoxSelectAll)
        layout.addWidget(self.apply)



    # FUNCTIONS

    # analysis menu functions
    ## list functions

    # checked items list
    def checkedItems(self):
        return [item for item in self.items if item.checkState()==Qt.CheckState.Checked]
    # unchecked items list
    def uncheckedItems(self):
        return [item for item in self.items if item.checkState()==Qt.CheckState.Unchecked]


    # SLOTS

    # analysis button slot

    def uncheckAnalysisMenu(self):
        # uncheck all checked list items
        [item.setCheckState(Qt.CheckState.Unchecked) for item in self.checkedItems()]

        # uncheck checkbox, items and remove wand icon
        if self.checkBoxSelectAll.isChecked():
                self.checkBoxSelectAll.setChecked(False)
                self.check_all_items(False)
    
    def toggle_list_visibility(self):

        # se botao inicialmente estiver checked
        #todo: transformar em painted button para abrir menu e mudar analises de modo mais simples
        if not self.isChecked():
            # analysis button automatically unchecks itself

            self.uncheckAnalysisMenu()

            self.modeChanged.emit(True)

        # se botao inicialmente estiver unchecked
        else:
            # uncheck the analysis button
            self.setChecked(False)

            # hide the menu
            if self.Menu.isVisible():
                self.Menu.setHidden(True)
            
            # expose the menu
            else:
                #?: desmarcar items apos desexibir e exibir novamente
                # uncheck checkbox, items and remove wand icon if the menu was closed without apply analysis
                # if self.checkBoxSelectAll.isChecked():
                #     self.checkBoxSelectAll.setChecked(False)
                #     self.check_all_items(False)
                
                # uncheck items if there is anyone checked after just close the menu without apply analysis
                # items_checked = self.checkedItems()
                # if len(items_checked):
                #     for item in items_checked:
                #         item.setCheckState(Qt.CheckState.Unchecked)
                
                # positionate the menu
                topleft_corner = self.parent().mapToParent(self.geometry().bottomLeft())
                self.Menu.setGeometry(QRect(topleft_corner.x()+1, topleft_corner.y(), 160, 220))
                self.Menu.raise_()
                self.Menu.setHidden(False)
        
        # restaura valor padrao de changed
            self.changed = False
    

    # analysis menu slots

    ## list slot

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
    

    ## checkbox slot: check todos os items da lista

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
    

    ## apply button slots

    # coloca ou tira icone da varinha do botao apply
    def toggle_icon(self,state):
        if state:
            self.apply.setIcon(QIcon('icons/icons/wand.png'))
        else:
            self.apply.setIcon(QIcon(None))
    
    # funcionalidades do apply
    def applyHide(self):
        
        self.Menu.setHidden(True)

        if self.checkedItems():
            self.modeChanged.emit(False)
