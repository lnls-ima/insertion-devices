
from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction, QIcon

class IMAIDsMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # File menu
        self.menuFile = self.addMenu("&File")
        ## File menu - New Project action
        self.actionNew_Project = QAction(QIcon("icons/icons/projection-screen--plus.png"),"New Project", self)
        self.actionNew_Project.setShortcut("Ctrl+N")
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addSeparator()
        ## File menu - Open Data action
        self.actionOpen_Data = QAction(QIcon("icons/icons/database-import.png"),"Open Data ...", self)
        self.actionOpen_Data.setShortcut("Ctrl+O")
        self.menuFile.addAction(self.actionOpen_Data)
        self.menuFile.addSeparator()
        ## File menu - Generate Model action
        self.actionGenerate_Model = QAction(QIcon("icons/icons/magnet-blue.png"),"Generate Model", self)
        self.actionGenerate_Model.setShortcut("Ctrl+M")
        self.menuFile.addAction(self.actionGenerate_Model)
        self.menuFile.addSeparator()
        ## File menu - Exit action
        self.actionExit = QAction(QIcon("icons/icons/door-open-out.png"),"Exit", self)
        self.actionExit.setShortcut("Alt+F4")
        self.menuFile.addAction(self.actionExit)
        # Edit menu
        self.menuEdit = self.addMenu("&Edit")
        ## Edit menu - Analysis action
        self.actionAnalysis = QAction(QIcon("icons/icons/beaker--pencil"),"Custom Analysis", self)
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
        # Settings menu
        self.menuSettings = self.addMenu("&Settings")
        ## Settings menu - Apply action
        self.actionApplyForAll = QAction(QIcon("icons/icons/wand-hat.png"),"Apply for All", self, checkable=True)
        self.menuSettings.addAction(self.actionApplyForAll)
        # Help menu: documentacao da interface
        self.menuHelp = self.addMenu("&Help")
