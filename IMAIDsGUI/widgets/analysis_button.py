
from PyQt6.QtWidgets import QPushButton, QFrame, QListWidget, QListWidgetItem, QCheckBox, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QRect, pyqtSignal


class AnalysisPushButton(QPushButton):

    signalField = pyqtSignal()
    signalTrajectory = pyqtSignal()
    signalPhaseError = pyqtSignal()
    signalIntegrals = pyqtSignal()
    signalRollOff = pyqtSignal()
    signalKickma = pyqtSignal()
    signalCrossTalk = pyqtSignal()
    signalShimming = pyqtSignal()

    def __init__(self, menu_parent, button_text, button_parent, *args, **kwargs):
        super().__init__(text=button_text, parent=button_parent, *args, **kwargs)

        #sintaxe do botao

        self.setCheckable(True)

        self.clicked.connect(self.toggle_list_visibility)


        #sintaxe da lista
        ## lista + outros

        #menu = QMenu()
        #estilo = self.parent().style()

        self.Menu = QFrame(parent=menu_parent)
        self.Menu.setObjectName("frame")
        self.Menu.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.Menu.setLineWidth(1)

        #palette = self.palette()
        #background_color = palette.color(QPalette.ColorRole.Menu)

        # change the background color without affect the other widgets in the container:
        # https://stackoverflow.com/questions/62046679/qframe-background-color-overlapped-with-other-widgets-like-qlineedit-qlistboxwi
        self.Menu.setStyleSheet("QFrame#frame{background-color: #f0f0f0}")
        #self.Menu.setStyle(estilo)
        
        ## lista apenas
        self.list = QListWidget(parent=self.Menu)
        self.list.setStyleSheet("background-color: #f0f0f0")

        self.items_checked = []

        self.list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.list.itemChanged.connect(self.handle_item_changed)

        

        #*: importante ter cada item individual assim para poder chamar cada um na mainwindow e
        #*: e diferenciar as analises
        self.itemField = QListWidgetItem("Magnetic Field", self.list)
        self.itemTrajectory = QListWidgetItem("Trajectory", self.list)
        self.itemPhaseError = QListWidgetItem("Phase Error", self.list)
        self.itemIntegrals = QListWidgetItem("Field Integrals", self.list)
        self.itemRollOff = QListWidgetItem("Roll Off", self.list)
        self.itemKickmap = QListWidgetItem("Kickmap", self.list)
        self.itemCrossTalk = QListWidgetItem("Cross Talk", self.list)
        self.itemShimming = QListWidgetItem("Shimming", self.list)

        
        # todo: fazer isso pegando os items criados acima todos com algum metodo de qlistwidget
        # ?: talvez fazer isso com as actions na mainwindow tambem
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)

        ## checkbox apenas
        self.checkBoxSelectAll = QCheckBox("Select All",self)
        self.checkBoxSelectAll.stateChanged.connect(self.check)

        ## apply button apenas
        self.apply = QPushButton("Apply")
        self.apply.clicked.connect(self.aplicar)
        
        ## layout
        layout = QVBoxLayout(self.Menu)
        layout.addWidget(self.list)
        layout.addWidget(self.checkBoxSelectAll)
        layout.addWidget(self.apply)

        #self.installEventFilter(self)

        self.Menu.setHidden(True)


    # button slots
    
    def toggle_list_visibility(self):

        topleft_corner = self.parent().mapToParent(self.geometry().bottomLeft())
        print(topleft_corner)
        self.Menu.raise_()
        self.Menu.setGeometry(QRect(topleft_corner.x()+1, topleft_corner.y(), 150, 250))

        if self.Menu.isVisible():
            self.Menu.setHidden(True)
        else:
            self.Menu.setHidden(False)
    
    # menu slots

    # todo: criar metodo para retornar lista de items checked e unchecked

    def checkedItems(self):
        return [item for item in self.list.items()]
    
    # check todos os items da lista e coloca ou tira icone da varinha
    def check(self,checked):
    
        if checked:
            # quando check todos, mudar icone de apply para varinha ou chapeu
            self.apply.setIcon(QIcon('icons/icons/wand.png'))
            for i in range(self.list.count()):
                self.list.item(i).setCheckState(Qt.CheckState.Checked)
        else:
            self.apply.setIcon(QIcon(None))
            for i in range(self.list.count()):
                self.list.item(i).setCheckState(Qt.CheckState.Unchecked)
    
    # def eventFilter(self, obj, event) -> bool:
    #     if event.type() ==QEvent.Type.FocusOut:
    #         self.setHidden(True)
    #     return super().eventFilter(obj, event)

    def aplicar(self):
        print('aplicou')

        self.signalField.emit()
        self.signalTrajectory.emit()
        self.signalPhaseError.emit()
        self.signalIntegrals.emit()
        self.signalRollOff.emit()
        self.signalKickma.emit()
        self.signalCrossTalk.emit()
        self.signalShimming.emit()

        self.Menu.setHidden(True)

        self.setChecked(True)
    
    # list slots

    # usado apenas para formar a lista de items checked, que sera posteriormente usada
    # no proximo metodo, keyPressEvent
    def handle_item_changed(self, item):

        if item.checkState() == Qt.CheckState.Checked:
            if item not in self.items_checked:
                self.items_checked.append(item.text())
        else:
            if item.text() in self.items_checked:
                self.items_checked.remove(item.text())

    # imprime os itens checked da lista
    def keyPressEvent(self, event):
        print('enter')
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            print(self.items_checked)   
        else:
            super().keyPressEvent(event)