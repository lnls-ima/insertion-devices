# padrao de nomeacao de variaveis #

# actions
## object name das actions: action<action_name>
## acessamos certa action com self.action<action_name>
## slots das actions: actionNewPressed


import sys

from  PyQt6.QtWidgets import    (QApplication,
                                QWidget,
                                QMainWindow,
                                QTabWidget,
                                QStatusBar,
                                QToolBar,
                                QToolButton,
                                QPushButton,
                                QLabel,
                                QLineEdit,
                                QComboBox,
                                QFileDialog,
                                QMenu,
                                QTableView,
                                QHBoxLayout,
                                QVBoxLayout,
                                QScrollArea,
                                QSplitter,
                                QSizePolicy,
                                QTreeWidget,
                                QTreeWidgetItem)
from   PyQt6.QtGui    import   (QAction,
                                QIcon,
                                QKeySequence,
                                QPixmap,
                                QPainter,
                                QPolygon,
                                QCursor,
                                QColor)
from   PyQt6.QtCore   import   (Qt,
                                QPoint,
                                QSize,
                                pyqtSignal,
                                QAbstractTableModel,
                                QTimer,
                                QEvent)

from random import choice
import numpy as np

adress = 'images\\'
tabs_figures = [
    'Ryujin.jpg',
    'Geistkampfer.jpg',
    'Shibaraku.jpg',
    'Kabuto Mushi.jpg',
    'Lord.jpg'
]


class TableModel(QAbstractTableModel):

    def __init__(self, filename):
        super(TableModel, self).__init__()

        with open(filename, 'r') as f:
            self._header = f.readline().split()
            
        self._data = np.loadtxt(filename, skiprows=2)


    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data[index.row(), index.column()]
            return str(value)
        
        if role == Qt.ItemDataRole.BackgroundRole:
            color = [206,171, 71, int(0.3*255)]
            return QColor.fromRgb(*color)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:

            if orientation == Qt.Orientation.Horizontal:
                return self._header[section]

            if orientation == Qt.Orientation.Vertical:
                return range(1, self._data.shape[0]+1)[section]
        
        if role==Qt.ItemDataRole.ForegroundRole:
            if orientation == Qt.Orientation.Vertical:
                return QColor.fromRgb(255, 255, 255)


class ButtonMenu(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setFixedSize(32,32)

        self.clicked.connect(self.button_clicked)

        self.custom_buttonMenu = QMenu(self)

    def button_clicked(self,s):
        self.show_menu()

    def show_menu(self):
        self.custom_buttonMenu.popup(self.mapToGlobal(self.rect().bottomLeft()))


class PaintedButton(ButtonMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setFixedSize(32,32)
    

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        len = int(min(self.width(),self.height())/2)
        
        # coordinates of the polygon points must be integers
        square = QPolygon([QPoint(width,height),
                           QPoint(width,height-len),
                           QPoint(width-len,height-len),
                           QPoint(width-len, height)])
        painter.setBrush(Qt.GlobalColor.blue)
        painter.drawPolygon(square)
        painter.end()
    
    def button_clicked(self,s):

        cursor_pos = QCursor.pos()
        widget_pos = self.mapFromGlobal(cursor_pos)

        x, y = widget_pos.x(), widget_pos.y()

        width = self.width()
        height = self.height()
        len = min(self.width(),self.height())/2

        if (width-len <= x <= width) and (height-len <= y <= height):
            print('dentro')
            self.show_menu()
        else:
            print('fora')



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # botao
        self.PlusButton = QToolButton()
        self.PlusButton.setText("+")
        ## signals
        self.PlusButton.clicked.connect(self.buttonPlusClicked)
        
        # tab widget
        self.projects = QTabWidget()
        ## tabs features
        self.projects.setDocumentMode(True) # talvez possa ser desabilitado
        self.projects.setMovable(True)
        ## signals
        self.projects.tabCloseRequested.connect(self.close_current_tab)
        self.projects.tabBarDoubleClicked.connect(self.start_rename)
        ## adicionando tab inicial
        

        self.main_area = QWidget()

        #labels de parametros dos modelos
        
        self.visuals = QTabWidget()
        self.visuals.addTab(QWidget(),'Blank')

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Orientation.Horizontal)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.visuals)

        
        vbox = QVBoxLayout(self.main_area)

        self.command_window = QLineEdit()

        vbox.addWidget(self.splitter)
        vbox.addWidget(self.command_window)

        
        self.projects.addTab(self.main_area,'Blank Project')

        widt = self.main_area.width()

        self.splitter.setSizes([int(widt/4),int(3*widt/4)])


        ## adicionando botao
        self.projects.setCornerWidget(self.PlusButton,corner=Qt.Corner.TopLeftCorner)


        # actions
        ## A action
        self.button_actionA = QAction(QIcon("icons/icons/animal-penguin.png"), "&Abutton", self)
        self.button_actionA.setStatusTip("This is your button A")
        self.button_actionA.triggered.connect(self.action_clicked)
        self.button_actionA.hovered.connect(self.entrou_action)
        self.button_actionA.setCheckable(True)
        self.button_actionA.setShortcut(QKeySequence("Ctrl+P"))
        ## B action
        self.button_actionB = QAction(QIcon("icons/icons/bug.png"), "&Bbutton", self)
        self.button_actionB.setStatusTip("This is your button B")
        self.button_actionB.triggered.connect(self.replace_action)
        self.button_actionB.hovered.connect(self.entrou_action)
        self.button_actionB.setCheckable(True)
        self.button_actionB.setShortcut(QKeySequence("Ctrl+B"))
        ## C action
        self.button_actionC = QAction(QIcon("icons/icons/animal-dog.png"), "&Cbutton", self)
        self.button_actionC.setStatusTip("This is your button C")
        self.button_actionC.triggered.connect(self.replace_action)
        self.button_actionC.hovered.connect(self.entrou_action)
        self.button_actionC.setCheckable(True)
        self.button_actionC.setShortcut(QKeySequence("Ctrl+D"))
        ## File menu actions
        self.actionNew_Project = QAction("New Project", self)
        self.actionOpen_Data = QAction("Open Data ...", self)
        self.actionOpen_Data.triggered.connect(self.browse_for_data)
        self.actionGenerate_Model = QAction("Generate Model", self)
        self.actionClose = QAction("Close", self)
        ## Edit menu actions
        self.actionUndo = QAction("Undo", self)
        self.actionRedo = QAction("Redo", self)
        ## Analysis toolbar menu actions
        actionPhaseError = QAction("Phase Error", self)
        actionRollOff = QAction("Roll Off", self)
        actionKickmap = QAction("Kickmap", self)
        actionTrajectory = QAction("Trajectory", self)
        actionMagneticField = QAction("Magnetic  Field", self)
        actionShimming = QAction("Shimming", self)
        actionCrossTalk = QAction("Cross Talk", self)
        actionFieldIntegral = QAction("Field Integral", self)


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
        self.actionQuit = self.menuFile.addAction("Quit")
        self.actionQuit.triggered.connect(self.quit_app)
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
        self.toolbar.addAction(self.button_actionA)    # e' aqui que penguin e' adicionado a toolbar
        self.toolbar.addSeparator()

        # button analysis as a ButtonMenu
        toolbar_buttonAnalysis = ButtonMenu("Analysis")
        self.toolbar.addWidget(toolbar_buttonAnalysis)
        toolbar_buttonAnalysis.custom_buttonMenu.addActions(([actionPhaseError,
                                                              actionRollOff,
                                                              actionKickmap,
                                                              actionTrajectory,
                                                              actionMagneticField,
                                                              actionShimming,
                                                              actionCrossTalk,
                                                              actionFieldIntegral]))
        self.toolbar.addSeparator()

        # nos painted buttons deve-se passar action para ele ser exibido como padrao
        # testar com exemplo do penguin

        toolbar_buttonPlot = PaintedButton("Plot")
        self.toolbar.addWidget(toolbar_buttonPlot)
        self.toolbar.addSeparator()
        toolbar_buttonTable = PaintedButton("Table")
        self.toolbar.addWidget(toolbar_buttonTable)
        

        # status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)


        # coisas de Qmainwindow
        self.app = app
        self.setWindowTitle("IMAIDS Interface")
        self.setCentralWidget(self.projects)
        self.resize(500,400)
        #self.setGeometry(100,100,400,500)
        ## signal
        #self.resized.connect(self.someFunction)

        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.handleResize)
        self.resize_timer.setInterval(500)



    # window slots

    def resizeEvent(self, event):
        if not self.resize_timer.isActive():
            print("Resizing...")

            widt_tree = self.tree.width()
            # setSizePolicy estava dando problema, mas da maneira abaixo funciona
            self.tree.setFixedWidth(widt_tree)
            self.resize_timer.start()

    def handleResize(self):
        print("Resize done")

        widt_tree = self.tree.width()
        widt_visual = self.visuals.width()
        self.splitter.setSizes([widt_tree,widt_visual])

        # setSizePolicy estava dando problema, mas da maneira abaixo funciona
        self.tree.setMinimumWidth(0)
        self.tree.setMaximumWidth(self.splitter.width())
        self.resize_timer.stop()


    # menu slots

    def browse_for_data(self,s):
        filename=QFileDialog.getOpenFileName(self, 'Open data', 'Documents', 'Data (*.dat)')
        filename = filename[0]
        self.table_data(filename)
    
    def table_data(self, filename):
        
        if self.projects.count() == 1:
            self.projects.setTabsClosable(True)
        
        tabela = QTableView()
        modelo = TableModel(filename)
        tabela.setModel(modelo)

        horizontal_color = QColor.fromRgb(80, 174, 144)
        vertical_color = QColor.fromRgb(136, 59, 144, int(0.8*255))
        horizontal_header_style = "QHeaderView::section {{background-color: {} }}".format(horizontal_color.name())
        vertical_header_style = "QHeaderView::section {{background-color: {} }}".format(vertical_color.name())
        tabela.horizontalHeader().setStyleSheet(horizontal_header_style)
        tabela.verticalHeader().setStyleSheet(vertical_header_style)

        i = self.projects.addTab(tabela, "tabela")
        self.projects.setCurrentIndex(i)

    def quit_app(self):
        self.app.quit()

    
    # tool bar slots

    def action_clicked(self,s):

        cursor_pos = QCursor.pos()
        widget_pos = self.mapFromGlobal(cursor_pos)

        x, y = widget_pos.x(), widget_pos.y()

        self.status.showMessage(r"clicou na ação", 1000)
        
        print(x,y)
    
    def entrou_action(self):
        print("entrou no button A")
        actiongeo = self.toolbar.actionGeometry(self.button_actionA)
        print('actiongeo:',actiongeo)
        action_topleft = self.toolbar.mapToParent(actiongeo.topLeft())
        action_bottomright = self.toolbar.mapToParent(actiongeo.bottomRight())
        action_bottomleft = self.toolbar.mapToParent(actiongeo.bottomLeft())
        w = action_bottomright.x()-action_topleft.x()
        h = action_bottomright.y()-action_topleft.y()
  
        cursor_pos = QCursor.pos()
        widget_pos = self.mapFromGlobal(cursor_pos)
        cursor_x, cursor_y = widget_pos.x(), widget_pos.y()

        if (action_bottomright.x()-w/2 <= cursor_x <= action_bottomright.x()) and \
           (action_bottomright.x()-h/2) <= cursor_y <= action_bottomright.y():
            print("ja era, ta no canto")

            menu_penguin = QMenu(self)   # conferir se está usando corretamente o parent aqui
            menu_penguin.addActions([self.button_actionB,self.button_actionC])

            menu_penguin.popup(self.mapToGlobal(action_bottomleft))

    def replace_action(self,s):
        print(s)


    # tab bar slots

    def buttonPlusClicked(self, i):
        print('um clique',i)

        origami = choice(tabs_figures)
        self.adicionando_abas(origami)
        
    def adicionando_abas(self, origami):

        if self.projects.count() == 1:
            self.projects.setTabsClosable(True) 
       
        dobradura = QLabel()
        dobradura.setPixmap(QPixmap(adress+origami))
        dobradura.setAlignment(Qt.AlignmentFlag.AlignCenter)

        i = self.projects.addTab(dobradura, origami.split('.')[0])
        self.projects.setCurrentIndex(i)
        
    def close_current_tab(self, i):

        # if there is only one tab
        if self.projects.count() == 1:
            # do nothing
            return

        # else remove the tab
        self.projects.removeTab(i)

        if self.projects.count() == 1:
            self.projects.setTabsClosable(False)
    
    def start_rename(self, tab_index):
        self.editting_tab = tab_index
        rect = self.projects.tabBar().tabRect(tab_index)
        #print(rect)
        pos = rect.bottomRight()   # map to parent aqui como foi feito em entrou_action
        w = rect.width()
    
        top_margin = 4
        left_margin = 2

        self.edit = QLineEdit(self)
        self.edit.show()
        self.edit.move(pos.x()-w+20+left_margin,3*pos.y()+top_margin)

        # verificar se todos os rect das abas teem mesmo tamanho

        self.edit.resize(w, self.edit.height())
        self.edit.setText(self.projects.tabText(tab_index))
        self.edit.selectAll()
        self.edit.setFocus() # talvez de problema quando clicar fora do line edit enquanto ele tiver aberto
        self.edit.editingFinished.connect(self.finish_rename)

    def finish_rename(self):
        self.projects.setTabText(self.editting_tab, self.edit.text())
        self.edit.deleteLater()


    # outros metodos

    def mousePressEvent(self, event):
        
        #posicao do cursor do mouse nas coordenadas da window
        cursor_pos = QCursor.pos()
        widget_pos = self.mapFromGlobal(cursor_pos)
        print("Current cursor position at widget: x = %d, y = %d" % (widget_pos.x(), widget_pos.y()))

        #alterar action no comeco: penguin, bug, dog
        return




# execution

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())