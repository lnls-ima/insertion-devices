
from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QIcon, QAction

from . import analysis_button, painted_button

class IMAIDsToolBar(QToolBar):

    def __init__(self, title='', parent=None):
        super().__init__(title, parent)

        self.grafico = QIcon("icons/icons/guide.png")
        self.grafico2x2 = QIcon("icons/icons/grid.png")
        self.graficos = QIcon("icons/icons/guide-snap.png")
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
        self.buttonPlot.setIcon(self.grafico)

        self.actiongrafico = QAction(self.grafico,"grafico",self.buttonPlot)
        self.actiongrafico.triggered.connect(self.action_swap)
        self.actiongrafico.setObjectName("graph")
        self.actiongrafico2x2 = QAction(self.grafico2x2,"grafico",self.buttonPlot)
        self.actiongrafico2x2.triggered.connect(self.action_swap)
        self.actiongrafico2x2.setObjectName("graph22")
        self.actiongraficos = QAction(self.graficos,"graficos",self.buttonPlot)
        self.actiongraficos.triggered.connect(self.action_swap)
        self.actiongraficos.setObjectName("graphs")

        self.buttonPlot.setObjectName(self.actiongrafico.objectName())
        self.grafico = self.buttonPlot.icon()
        self.buttonPlot.custom_buttonMenu.addActions([self.actiongrafico,
                                                      self.actiongrafico2x2,
                                                      self.actiongraficos])
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
        if self.buttonPlot==action.parent():
            self.buttonPlot.setIcon(action.icon())
            self.buttonPlot.setChecked(True)
            self.buttonPlot.setObjectName(action.objectName())
        else:
            self.buttonTable.setIcon(action.icon())
            self.buttonTable.setChecked(True)
            self.buttonTable.setObjectName(action.objectName())

    #todo: criar metodo aqui ou em painted button ou subclass QAction... para checar se o
    #todo: botao selecionou e' tal ou tal (exemplo: e' grafico ou e' grafico2x2)
