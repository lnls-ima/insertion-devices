
from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QIcon, QAction

from . import analysis_button, painted_button

class IMAIDsToolBar(QToolBar):

    def __init__(self, title='', parent=None):
        super().__init__(title, parent)

        grafico = QIcon("icons/icons/guide.png")
        self.tabela = QIcon("icons/icons/table.png")
        self.dog = QIcon("icons/icons/animal-dog.png")
        self.cat = QIcon("icons/icons/animal.png")
        self.bug = QIcon("icons/icons/bug.png")
        
        self.actiontabela = QAction(self.tabela,"tabela",self)
        self.actiontabela.triggered.connect(self.action_swap)
        self.actiontabela.setObjectName("tabela")
        self.actiondog = QAction(self.dog,"cachorro",self)
        self.actiondog.triggered.connect(self.action_swap)
        self.actiondog.setObjectName("dog")
        self.actioncat = QAction(self.cat,"gato",self)
        self.actioncat.triggered.connect(self.action_swap)
        self.actioncat.setObjectName("cat")
        self.actionbug = QAction(self.bug,"inseto",self)
        self.actionbug.triggered.connect(self.action_swap)
        self.actionbug.setObjectName("bug")

        # tool bar
        self.setObjectName("Tool Bar")
        ## tool bar - analysis button: executar analise de dados
        self.buttonAnalysis = analysis_button.AnalysisPushButton(menu_parent=parent,
                                                                 button_text="Analysis",
                                                                 button_parent=self)
        #self.buttonAnalysis.apply.clicked.connect(self.aplicar_AnalysisForAll)
        self.addWidget(self.buttonAnalysis)
        self.addSeparator()
        ## tool bar - plot button: fazer graficos dos dados
        self.buttonPlot = painted_button.PaintedButton("Plot")
        self.buttonPlot.setIcon(grafico)
        self.addWidget(self.buttonPlot)
        self.addSeparator()
        ## tool bar - table button: fazer tabelas dos dados
        self.buttonTable = painted_button.PaintedButton("Table")
        self.buttonTable.setIcon(self.tabela)
        self.buttonTable.setObjectName(self.actiontabela.objectName())
        self.tabela = self.buttonTable.icon()
        self.buttonTable.custom_buttonMenu.addActions([self.actiontabela,
                                                               self.actioncat,
                                                               self.actiondog,
                                                               self.actionbug])
        self.addWidget(self.buttonTable)

    def action_swap(self):
        action = self.sender()
        self.buttonTable.setIcon(action.icon())
        self.buttonTable.setChecked(True)
        self.buttonTable.setObjectName(action.objectName())
