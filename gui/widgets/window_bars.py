
from PyQt6.QtWidgets import QStatusBar, QToolBar, QMenuBar, QLabel
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal

from . import analysis, painted_button, get_path


class StatusBar(QStatusBar):

    name = "Status Bar"

    def __init__(self):
        super().__init__()

        #self.setContentsMargins(0,0,0,6)
        self.setContentsMargins(4,0,0,0)

        self.label_button = QLabel("<b>Table</b> active")

        self.addWidget(self.label_button)


class ToolBar(QToolBar):

    modeChanged = pyqtSignal()
    
    name = "Tool Bar"

    def __init__(self, title='', parent=None):
        super().__init__(title, parent)

        #todo: consertar posicao do analysis menu para tornar True abaixo
        self.setMovable(False)

        self.buttonChecked = None

        plus = QIcon(get_path('icons','plus.png'))
        minus = QIcon(get_path('icons','minus.png'))
        grafico = QIcon(get_path('icons','guide.png'))
        tabela = QIcon(get_path('icons','table.png'))
        dog = QIcon(get_path('icons','animal-dog.png'))
        cat = QIcon(get_path('icons','animal.png'))
        bug = QIcon(get_path('icons','bug.png'))
        
        # tool bar
        self.setObjectName(self.name)

        ## tool bar - cursor action: explore window without affect items
        self.actionCursor = QAction(icon=QIcon(get_path('icons','cursor.png')),
                                    text="<b>Cursor</b> (C)<br>"+
                                         "Select item or tab",
                                    parent=self)
        self.actionCursor.setObjectName("Cursor")
        self.actionCursor.setShortcut("Esc")
        self.actionCursor.setCheckable(True)
        self.actionCursor.triggered.connect(self.mode_swap) #todo: ver como e' o bool que manda
        self.addAction(self.actionCursor)
        self.addSeparator()

        ## tool bar - analysis button: executar analise de dados
        self.buttonAnalysis = analysis.AnalysisPushButton(text="Analysis  ",
                                                                 parent=self)
        self.buttonAnalysis.setObjectName("Analysis")
        self.buttonAnalysis.setToolTip("<b>Analysis</b> (Ctrl+A)<br>"+
                                       "Click to open the menu.<br>"+
                                       "Choose the analysis, apply and finally select the ID item")
        #self.buttonAnalysis.apply.clicked.connect(self.aplicar_AnalysisForAll)
        self.buttonAnalysis.modeChanged.connect(self.mode_swap)
        self.addWidget(self.buttonAnalysis)
        
        ## tool bar - operation button: realizar operações básicas entre análises
        self.buttonOperation = painted_button.PaintedButton("Operation   ")
        self.buttonOperation.setObjectName("Operation")
        self.buttonOperation.setShortcut("P")
        self.buttonOperation.setToolTip("<b>Operation</b> (P)<br>"+
                                       "Select two analysis items then press spacebar")
        self.buttonOperation.modeChanged.connect(self.mode_swap)
        self.buttonOperation.setIcon(minus)

        self.actionminus = QAction(icon=minus,text="Minus Analyses")
        self.actionminus.triggered.connect(self.buttonOperation.action_swap)
        self.actionplus = QAction(icon=plus,text="Plus Analyses")
        self.actionplus.triggered.connect(self.buttonOperation.action_swap)
        self.buttonOperation.selectedAction = self.actionminus
        self.buttonOperation.Menu.addActions([self.actionminus,
                                              self.actionplus])
        self.addWidget(self.buttonOperation)

        ## tool bar - plot button: fazer graficos dos dados
        self.buttonPlot = painted_button.PaintedButton("Plot")
        self.buttonPlot.setObjectName("Plot")
        self.buttonPlot.setShortcut("G")
        self.buttonPlot.setToolTip("<b>Plot</b> (G)<br>"+
                                   "Select or Analysis item or one result item or two result items, then press spacebar")
        self.buttonPlot.modeChanged.connect(self.mode_swap)
        self.buttonPlot.setIcon(grafico)

        self.actiongrafico = QAction(icon=grafico,text="Plot")
        self.actiongrafico.triggered.connect(self.buttonPlot.action_swap)
        self.buttonPlot.selectedAction = self.actiongrafico
        self.buttonPlot.Menu.addActions([self.actiongrafico])
        self.addWidget(self.buttonPlot)
        #self.addSeparator()

        ## tool bar - table button: fazer tabelas dos dados
        self.buttonTable = painted_button.PaintedButton("Table")
        self.buttonTable.setObjectName("Table")
        self.buttonTable.setShortcut("T")
        self.buttonTable.setToolTip("<b>Table</b> (T)<br>"+
                                    "Click over an item (ID, Analysis or Result)")
        self.buttonTable.modeChanged.connect(self.mode_swap)
        self.buttonTable.setChecked(True)
        self.buttonChecked = self.buttonTable
        self.buttonTable.setIcon(tabela)

        self.actiontabela = QAction(icon=tabela,text="Table")
        self.actiontabela.triggered.connect(self.buttonTable.action_swap)
        self.actiondog = QAction(icon=dog,text="cachorro")
        self.actiondog.triggered.connect(self.buttonTable.action_swap)
        self.actioncat = QAction(icon=cat,text="gato")
        self.actioncat.triggered.connect(self.buttonTable.action_swap)
        self.actionbug = QAction(icon=bug,text="inseto")
        self.actionbug.triggered.connect(self.buttonTable.action_swap)
        self.buttonTable.selectedAction = self.actiontabela
        self.buttonTable.Menu.addActions([self.actiontabela])
        self.addWidget(self.buttonTable)
        self.addSeparator()

        
        ## tool bar - save action: salvar tabelas dos mapas de campo
        self.actionSave = QAction(icon=QIcon(get_path('icons','database-export.png')),
                                  text="<b>Save</b> (S)<br>"+
                                       "Select Data ID item or Analysis item",
                                  parent=self)
        self.actionSave.setObjectName("Save")
        self.actionSave.setShortcut("S")
        self.actionSave.setCheckable(True)
        self.actionSave.triggered.connect(self.mode_swap)
        self.addAction(self.actionSave)
        self.addSeparator()

        ## tool bar - model_meas action: transformar modelo em mapa de campo
        self.actionModelData = QAction(icon=QIcon(get_path('icons','clipboard-block.png')),
                                       text="<b>ModelData</b> (M)<br>"+
                                            "Select Model ID item",
                                       parent=self)
        self.actionModelData.setObjectName("ModelData")
        self.actionModelData.setShortcut("M")
        self.actionModelData.setCheckable(True)
        self.actionModelData.triggered.connect(self.mode_swap)
        self.addAction(self.actionModelData)

    def swap_apply(self,for_all):
        self.buttonAnalysis.Menu.apply.setText(
            "Apply for All" if for_all else "Apply"
        )
        self.buttonAnalysis.setIcon(QIcon(
            get_path('icons','wand-hat.png') if for_all else None
        ))

    def mode_swap(self,isSelfUnchecking):

        toolbar_button = self.sender()

        self.buttonChecked.setChecked(False)

        if  toolbar_button==self.buttonChecked and (isSelfUnchecking or \
            type(toolbar_button) is QAction):
            
            self.actionCursor.setChecked(True)
            self.buttonChecked = self.actionCursor

        else:
            toolbar_button.setChecked(True)
            if self.buttonChecked==self.buttonAnalysis:
                self.buttonAnalysis.Menu.uncheckAnalysisMenu()
            self.buttonChecked = toolbar_button

        self.modeChanged.emit()



class MenuBar(QMenuBar):

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # icons
        ## icons - File menu
        iconNew_Project = QIcon(get_path('icons','projection-screen--plus.png'))
        iconOpen_Data = QIcon(get_path('icons','database-import.png'))
        iconGenerate_Model = QIcon(get_path('icons','magnet-blue.png'))
        iconExit = QIcon(get_path('icons','door-open-out.png'))
        ## icons - Edit Menu
        iconAnalysis = QIcon(get_path('icons','beaker--pencil'))
        ## icons - View Menu
        iconToolBar = QIcon(get_path('icons','toolbox.png'))
        iconStatusBar = QIcon(get_path('icons','ui-status-bar-blue.png'))
        ## icons - Settings Menu
        iconApplyForAll = QIcon(get_path('icons','wand-hat.png'))
        ## icons - Help Menu
        iconShortcuts = QIcon(get_path('icons','notebook--shortcut.png'))
        iconManual = QIcon(get_path('icons','book.png'))
        
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
        self.actionGenerate_Model = QAction(iconGenerate_Model,"Generate Model ...", self)
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
        self.actionAnalysis = QAction(iconAnalysis,"Custom Analysis ...", self)
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
        ## View menu - file action
        self.actionFile = QAction("Data Filenames", self, checkable=True)
        self.menuView.addAction(self.actionFile)
        ## View menu - DockTree action
        self.actionDockTree = QAction("Explore Window", self, checkable=True)
        self.actionDockTree.setObjectName("dockTree")
        self.actionDockTree.setChecked(True)
        self.menuView.addAction(self.actionDockTree)
        ## View menu - DockOperations action
        self.actionDockOperations = QAction("Operation Window", self, checkable=True)
        self.actionDockOperations.setObjectName("dockOperations")
        self.menuView.addAction(self.actionDockOperations)
        ## View menu - DockSummary action
        self.actionDockSummary = QAction("Summary Window", self, checkable=True)
        self.actionDockSummary.setObjectName("dockSummary")
        self.actionDockSummary.setChecked(True)
        self.menuView.addAction(self.actionDockSummary)
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
        ## Help menu - Shortcuts action
        self.actionShortcuts = QAction(iconShortcuts, "Shortcuts", self)
        self.menuHelp.addAction(self.actionShortcuts)
        ## Help menu - Manual action
        self.actionManual = QAction(iconManual, "Manual", self)
        self.menuHelp.addAction(self.actionManual)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()
        return super().mousePressEvent(event)