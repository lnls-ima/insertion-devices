
from PyQt6.QtWidgets import QPushButton, QFrame, QListWidget, QListWidgetItem, QCheckBox, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QRect, pyqtSignal


class AnalysisPushButton(QPushButton):

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
        self.list.setStyleSheet("background-color: #f0f0f0")

        ### analysis menu - list - items:
        ### Create the items and automatically add them to the list widget
        self.itemField = QListWidgetItem("Magnetic Field", self.list)
        self.itemTrajectory = QListWidgetItem("Trajectory", self.list)
        self.itemPhaseError = QListWidgetItem("Phase Error", self.list)
        self.itemIntegrals = QListWidgetItem("Field Integrals", self.list)
        self.itemRollOff = QListWidgetItem("Roll Off", self.list)
        self.itemKickmap = QListWidgetItem("Kickmap", self.list)
        self.itemCrossTalk = QListWidgetItem("Cross Talk", self.list)
        self.itemShimming = QListWidgetItem("Shimming", self.list)
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)

        self.items = [self.list.item(i) for i in range(self.list.count())]

        ### analysis menu - list - signals
        self.list.itemClicked.connect(self.item_clicked)
        self.list.itemChanged.connect(lambda: setattr(self, 'changed', True))

        self.changed = False
        
        ## analysis menu - checkbox
        self.checkBoxSelectAll = QCheckBox("Select All",self)
        self.checkBoxSelectAll.clicked.connect(self.check_all_items)

        ## analysis menu - apply button
        self.apply = QPushButton("Apply")
        self.apply.setShortcut(Qt.Key.Key_Return)
        self.apply.clicked.connect(self.aplicar)
        
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
    
    def toggle_list_visibility(self):

        # se botao inicialmente estiver checked
        if not self.isChecked():
            # analysis button automatically unchecks itself

            # uncheck all checked list items
            [item.setCheckState(Qt.CheckState.Unchecked) for item in self.checkedItems()]

            # retoma valor padrao a changed, pois faz-se a mudanca acima
            self.changed = False

        # se botao inicialmente estiver unchecked
        else:
            # uncheck the analysis button
            self.setChecked(False)
            # hide the menu
            if self.Menu.isVisible():
                self.Menu.setHidden(True)
            
            # expose the menu
            else:
                # uncheck checkbox and remove the icon, for the case if it was checked
                # before the last hide
                if self.checkBoxSelectAll.isChecked():
                    self.checkBoxSelectAll.setChecked(False)
                    self.apply.setIcon(QIcon(None))
                # positionate the menu
                topleft_corner = self.parent().mapToParent(self.geometry().bottomLeft())
                self.Menu.setGeometry(QRect(topleft_corner.x()+1, topleft_corner.y(), 150, 250))
                self.Menu.raise_()
                self.Menu.setHidden(False)
    

    # analysis menu slots

    ## list slot

    def item_clicked(self, item: QListWidgetItem):
        print('item clicado')

        # caso o usuario marque tudo, depois clique em um item
        if self.checkBoxSelectAll.isChecked():
            self.checkBoxSelectAll.setChecked(False)

        # checkbox do item nao foi clicada
        if not self.changed:

            print('fora da checkbox')
            # bloquear sinal para nao ativar o itemChanged signal
            #?: talvez nem precise, ja que o itemChanged vai estar ligado a uma coisa que da' sempre True
            #self.blockSignals(True)
            if item.checkState()==Qt.CheckState.Unchecked:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

        # retomando changed ao seu valor padrao
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
    def aplicar(self):
        print('aplicou')

        self.Menu.setHidden(True)

        if len(self.checkedItems()):
            self.setChecked(True)
