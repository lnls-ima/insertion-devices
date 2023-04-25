# padrao #

# object name das actions:     actionNew
# acessamos com self.actionNew

# para actions, fazemos a conexao signal-slot com "triggered",
# para botoes, fazemos com "clicked"

# slots das actions: actionNewPressed


import sys

from  PyQt6.QtWidgets import    (QApplication,
                                QWidget,
                                QMainWindow,
                                QTabWidget,
                                QStatusBar,
                                QToolBar,
                                QPushButton,
                                QLabel,
                                QLineEdit,
                                QMenu)
from   PyQt6.QtGui    import   (QAction,
                                QIcon,
                                QKeySequence,
                                QPixmap,
                                QPainter,
                                QPolygon,
                                QCursor)
from   PyQt6.QtCore   import   (Qt,
                                QPoint,
                                QSize,
                                pyqtSignal)

from random import choice

adress = 'images\\'
tabs_figures = [
    'Ryujin.jpg',
    'Geistkampfer.jpg',
    'Shibaraku.jpg',
    'Kabuto Mushi.jpg',
    'Lord.jpg'
]


class CustomButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setFixedSize(32,32)

        self.clicked.connect(self.clicou)

        self.custom_buttonMenu = QMenu(self)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        L = int(min(self.width(),self.height())/2)
        W = self.width()
        H = self.height()
        
        # coordinates of the polygon points must be integers
        square = QPolygon([QPoint(W,H),
                           QPoint(W,H-L),
                           QPoint(W-L,H-L),
                           QPoint(W-L, H)])
        painter.setBrush(Qt.GlobalColor.blue)
        painter.drawPolygon(square)
        painter.end()
    
    def clicou(self,s):

        cursor_pos = QCursor.pos()
        widget_pos = self.mapFromGlobal(cursor_pos)

        x, y = widget_pos.x(), widget_pos.y()

        L = min(self.width(),self.height())/2

        if (self.width()-L <= x <= self.width()) and (self.height()-L <= y <= self.height()):
            print('dentro')
            self.show_menu()
        else:
            print('fora')

    def show_menu(self):
        self.custom_buttonMenu.popup(self.mapToGlobal(self.rect().bottomLeft()))




class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # botao
        self.PlusButton = QPushButton("+")
        
        # tab widget
        self.tabs = QTabWidget()
        ## tabs features
        self.tabs.setDocumentMode(True) # talvez possa ser desabilitado
        self.tabs.setMovable(True)
        #self.tabs.setTabsClosable(True) #definir quando houver mais de uma aba
        ## signals
        self.PlusButton.clicked.connect(self.buttonPlusClicked)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        ## adicionando tab inicial
        self.tabs.addTab(QWidget(),'Blank')
        ## adicionando botao
        self.tabs.setCornerWidget(self.PlusButton,corner=Qt.Corner.TopLeftCorner)


        # actions

        button_actionA = QAction(QIcon("icons/icons/animal-penguin.png"), "&Abutton", self)
        button_actionA.setStatusTip("This is your button A")
        #button_actionA.triggered.connect(self.onMyToolBarButtonClick)
        button_actionA.setCheckable(True)
        button_actionA.setShortcut(QKeySequence("Ctrl+P"))

        ## File menu
        self.actionNew_Project = QAction("New Project", self)
        self.actionOpen_Data = QAction("Open Data ...", self)
        #self.actionOpen_Data.setObjectName(u"actionOpen_data")
        self.actionGenerate_Model = QAction("Generate Model", self)
        #self.actionGenerate_Model.setObjectName(u"actionGenerate_Model")
        self.actionClose = QAction("Close", self)

        ## Edit menu
        self.actionUndo = QAction("Undo", self)
        #self.actionUndo.setObjectName(u"actionUndo")
        self.actionRedo = QAction("Redo", self)
        # self.actionRedo.setObjectName(u"actionRedo")


        # menubar
        self.menubar = self.menuBar()
        ## File
        self.menuFile = self.menubar.addMenu("&File")
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen_Data)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionGenerate_Model)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        ## Edit
        self.menuEdit = self.menubar.addMenu("&Edit")
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionRedo)
        ## Settings
        self.menuSettings = self.menubar.addMenu("&Settings")
        ## Help
        self.menuHelp = self.menubar.addMenu("&Help")


        # tool bar
        self.toolbar = QToolBar("PapelDobrado")
        self.addToolBar(self.toolbar)
        ## icons
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.addAction(button_actionA)
        self.toolbar.addSeparator()

        # button analysis as a CustomButton
        toolbar_buttonAnalysis = CustomButton("Analysis")
        actionPhaseError = QAction("Phase Error", self)
        actionRollOff = QAction("Roll Off", self)
        actionKickmap = QAction("Kickmap", self)
        actionTrajectory = QAction("Trajectory", self)
        actionMagneticField = QAction("Magnetic  Field", self)
        actionShimming = QAction("Shimming", self)
        actionCrossTalk = QAction("Cross Talk", self)
        actionFieldIntegral = QAction("Field Integral", self)
        toolbar_buttonAnalysis.custom_buttonMenu.addActions(([actionPhaseError,
                                                              actionRollOff,
                                                              actionKickmap,
                                                              actionTrajectory,
                                                              actionMagneticField,
                                                              actionShimming,
                                                              actionCrossTalk,
                                                              actionFieldIntegral]))
        self.toolbar.addWidget(toolbar_buttonAnalysis)
        self.toolbar.addSeparator()

        toolbar_buttonPlot = CustomButton("Plot")
        self.toolbar.addWidget(toolbar_buttonPlot)
        self.toolbar.addSeparator()
        toolbar_buttonTable = CustomButton("Table")
        self.toolbar.addWidget(toolbar_buttonTable)
        
        a = toolbar_buttonTable.text()
        print(a)


        # status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)


        # coisas de Qmainwindow
        self.setWindowTitle("IMAIDS Interface")
        self.setCentralWidget(self.tabs)
        self.resize(500,400)
        


    #def onMyToolBarButtonClick(self, s):
    #    print('clique', s)


    def buttonPlusClicked(self, i):
        print('um clique',i)

        origami = choice(tabs_figures)
        self.adicionando_abas(origami)
        

    def adicionando_abas(self, origami):

        #print('numero de tabs antes de adicionar:',self.tabs.count())

        if self.tabs.count() == 1:
            self.tabs.setTabsClosable(True) 
       
        dobradura = QLabel()
        dobradura.setPixmap(QPixmap(adress+origami))
        dobradura.setAlignment(Qt.AlignmentFlag.AlignCenter)

        i = self.tabs.addTab(dobradura, origami.split('.')[0])
        self.tabs.setCurrentIndex(i)

        #print('numero de tabs depois de adicionar:',self.tabs.count())

        
    def close_current_tab(self, i):

        # if there is only one tab
        if self.tabs.count() == 1:
            # do nothing
            return

        # else remove the tab
        self.tabs.removeTab(i)

        if self.tabs.count() == 1:
            self.tabs.setTabsClosable(False)




# execution

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())