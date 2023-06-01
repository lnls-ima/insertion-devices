
from PyQt6 import QtGui
from PyQt6.QtWidgets import QStatusBar, QToolBar, QMenuBar
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, Qt

from . import analysis, painted_button


class StatusBar(QStatusBar):

    name = "Status Bar"

    def __init__(self):
        super().__init__()

class ToolBar(QToolBar):

    name = "Tool Bar"

    def __init__(self, title='', parent=None):
        super().__init__(title, parent)

        self.setWindowModality(Qt.WindowModality.NonModal)

        #todo: consertar posicao do analysis menu para tornar True abaixo
        self.setMovable(False)

        self.whoChecked = None

        self.grafico = QIcon("icons/icons/guide.png")
        self.grafico2x2 = QIcon("icons/icons/grid.png")
        self.graficos = QIcon("icons/icons/guide-snap.png")
        self.graficotable = QIcon("icons/icons/grid-snap-dot.png")
        self.tabela = QIcon("icons/icons/table.png")
        self.dog = QIcon("icons/icons/animal-dog.png")
        self.cat = QIcon("icons/icons/animal.png")
        self.bug = QIcon("icons/icons/bug.png")
        
        # tool bar
        self.setObjectName(self.name)
        ## tool bar - cursor action: explore window without affect items
        self.actionCursor = QAction(QIcon("icons/icons/cursor.png"),"Cursor",self)
        self.actionCursor.setCheckable(True)
        self.actionCursor.triggered.connect(self.mode_swap) #todo: ver como e' o bool que manda
        self.addAction(self.actionCursor)
        self.addSeparator()
        ## tool bar - analysis button: executar analise de dados
        self.buttonAnalysis = analysis.AnalysisPushButton(text="Analysis",
                                                                 parent=self)
        #self.buttonAnalysis.apply.clicked.connect(self.aplicar_AnalysisForAll)
        self.buttonAnalysis.modeChanged.connect(self.mode_swap)
        self.addWidget(self.buttonAnalysis)
        self.addSeparator()
        ## tool bar - plot button: fazer graficos dos dados
        self.buttonPlot = painted_button.PaintedButton("Plot")
        self.buttonPlot.modeChanged.connect(self.mode_swap)
        self.buttonPlot.setIcon(self.grafico)

        self.actiongrafico = QAction(self.grafico,"grafico",self.buttonPlot)
        self.actiongrafico.triggered.connect(self.buttonPlot.action_swap)
        self.actiongrafico.setObjectName("graph")

        self.buttonPlot.setObjectName(self.actiongrafico.objectName())
        self.grafico = self.buttonPlot.icon()
        self.buttonPlot.custom_buttonMenu.addActions([self.actiongrafico])
        self.addWidget(self.buttonPlot)
        self.addSeparator()
        ## tool bar - table button: fazer tabelas dos dados
        self.buttonTable = painted_button.PaintedButton("Table")
        self.buttonTable.modeChanged.connect(self.mode_swap)
        self.buttonTable.setChecked(True)
        self.whoChecked = self.buttonTable
        self.buttonTable.setIcon(self.tabela)

        self.actiontabela = QAction(self.tabela,"tabela")
        self.actiontabela.triggered.connect(self.buttonTable.action_swap)
        self.actiontabela.setObjectName("tabela")
        self.actiondog = QAction(self.dog,"cachorro")
        self.actiondog.triggered.connect(self.buttonTable.action_swap)
        self.actiondog.setObjectName("dog")
        self.actioncat = QAction(self.cat,"gato")
        self.actioncat.triggered.connect(self.buttonTable.action_swap)
        self.actioncat.setObjectName("cat")
        self.actionbug = QAction(self.bug,"inseto")
        self.actionbug.triggered.connect(self.buttonTable.action_swap)
        self.actionbug.setObjectName("bug")

        self.buttonTable.setObjectName(self.actiontabela.objectName())
        self.tabela = self.buttonTable.icon()
        self.buttonTable.custom_buttonMenu.addActions([self.actiontabela,
                                                       self.actioncat,
                                                       self.actiondog,
                                                       self.actionbug])
        self.addWidget(self.buttonTable)

    def mode_swap(self,isSelfUnchecking):

        toolbar_button = self.sender()

        self.whoChecked.setChecked(False)

        if toolbar_button==self.whoChecked and isSelfUnchecking:
            self.actionCursor.setChecked(True)
            self.whoChecked = self.actionCursor

        else:
            toolbar_button.setChecked(True)
            if self.whoChecked==self.buttonAnalysis:
                self.buttonAnalysis.Menu.uncheckAnalysisMenu()
            self.whoChecked = toolbar_button

    #todo: criar metodo aqui ou em painted button ou subclass QAction... para checar se o
    #todo: botao selecionou e' tal ou tal (exemplo: e' grafico ou e' grafico2x2)



class MenuBar(QMenuBar):

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # icons
        ## icons - File menu
        iconNew_Project = QIcon("icons/icons/projection-screen--plus.png")
        iconOpen_Data = QIcon("icons/icons/database-import.png")
        iconGenerate_Model = QIcon("icons/icons/magnet-blue.png")
        iconExit = QIcon("icons/icons/door-open-out.png")
        ## icons - Edit Menu
        iconAnalysis = QIcon("icons/icons/beaker--pencil")
        ## icons - View Menu
        iconToolBar = QIcon("icons/icons/toolbox.png")
        iconStatusBar = QIcon("icons/icons/ui-status-bar-blue.png")
        ## icons - Settings Menu
        iconApplyForAll = QIcon("icons/icons/wand-hat.png")
        
        # File menu
        self.menuFile = self.addMenu("&File")
        ## File menu - New Project action
        self.actionNew_Project = QAction(iconNew_Project,"New Project", self)
        self.actionNew_Project.setShortcut("Ctrl+N")
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addSeparator()
        ## File menu - Open Data action
        self.actionOpen_Data = QAction(iconOpen_Data,"Open Data ...", self)
        self.actionOpen_Data.setShortcut("Ctrl+O")
        self.menuFile.addAction(self.actionOpen_Data)
        self.menuFile.addSeparator()
        ## File menu - Generate Model action
        self.actionGenerate_Model = QAction(iconGenerate_Model,"Generate Model", self)
        self.actionGenerate_Model.setShortcut("Ctrl+M")
        self.menuFile.addAction(self.actionGenerate_Model)
        self.menuFile.addSeparator()
        ## File menu - Exit action
        self.actionExit = QAction(iconExit,"Exit", self)
        self.actionExit.setShortcut("Alt+F4")
        self.menuFile.addAction(self.actionExit)
        # Edit menu
        self.menuEdit = self.addMenu("&Edit")
        ## Edit menu - Analysis action
        self.actionAnalysis = QAction(iconAnalysis,"Custom Analysis", self)
        self.menuEdit.addAction(self.actionAnalysis)
        self.menuEdit.addSeparator()
        '''## Edit menu - Undo action
        self.actionUndo = QAction("Undo", self)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addSeparator()
        ## Edit menu - Redo action
        self.actionRedo = QAction("Redo", self)
        self.menuEdit.addAction(self.actionRedo)'''
        # View menu: contem opcoes de esconder widgets, tais como toolbar
        self.menuView = self.addMenu("&View")
        ## View menu - DockTree action
        self.actionDockTree = QAction("Explore Window", self, checkable=True)
        self.actionDockTree.setObjectName("dockTree")
        self.actionDockTree.setChecked(True)
        self.menuView.addAction(self.actionDockTree)
        ## View menu - DockCommand action
        self.actionDockCommand = QAction("Command Line", self, checkable=True)
        self.actionDockCommand.setObjectName("dockCommand")
        self.actionDockCommand.setChecked(True)
        self.menuView.addAction(self.actionDockCommand)
        ## View menu - ToolBar action
        self.actionToolBar = QAction(iconToolBar,ToolBar.name, self, checkable=True)
        self.actionToolBar.setChecked(True)
        self.menuView.addAction(self.actionToolBar)
        ## View menu - StatusBar action
        self.actionStatusBar = QAction(iconStatusBar,StatusBar.name, self, checkable=True)
        self.actionStatusBar.setChecked(True)
        self.menuView.addAction(self.actionStatusBar)
        # Settings menu
        self.menuSettings = self.addMenu("&Settings")
        ## Settings menu - Apply action
        self.actionApplyForAll = QAction(iconApplyForAll,"Apply for All", self, checkable=True)
        self.menuSettings.addAction(self.actionApplyForAll)
        # Help menu: documentacao da interface
        self.menuHelp = self.addMenu("&Help")

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()
        return super().mousePressEvent(event)