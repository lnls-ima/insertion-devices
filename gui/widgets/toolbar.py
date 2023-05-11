
from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QIcon, QAction

from . import analysis_button, painted_button

class IMAIDsToolBar(QToolBar):

    def __init__(self, title='', parent=None):
        super().__init__(title, parent)

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
        self.setObjectName("Tool Bar")
        ## tool bar - cursor action: explore window without affect items
        self.actionCursor = QAction(QIcon("icons/icons/cursor.png"),"Cursor",self)
        self.actionCursor.setCheckable(True)
        self.actionCursor.triggered.connect(self.mode_swap) #todo: ver como e' o bool que manda
        self.addAction(self.actionCursor)
        self.addSeparator()
        ## tool bar - analysis button: executar analise de dados
        self.buttonAnalysis = analysis_button.AnalysisPushButton(menu_parent=parent,
                                                                 button_text="Analysis",
                                                                 button_parent=self)
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
        self.actiongrafico2x2 = QAction(self.grafico2x2,"grafico",self.buttonPlot)
        self.actiongrafico2x2.triggered.connect(self.buttonPlot.action_swap)
        self.actiongrafico2x2.setObjectName("graph22")
        self.actiongraficos = QAction(self.graficos,"graficos",self.buttonPlot)
        self.actiongraficos.triggered.connect(self.buttonPlot.action_swap)
        self.actiongraficos.setObjectName("graphs")
        self.actiongraficotable = QAction(self.graficotable,"grafico table",self.buttonPlot)
        self.actiongraficotable.triggered.connect(self.buttonPlot.action_swap)
        self.actiongraficotable.setObjectName("graphs")

        self.buttonPlot.setObjectName(self.actiongrafico.objectName())
        self.grafico = self.buttonPlot.icon()
        self.buttonPlot.custom_buttonMenu.addActions([self.actiongrafico,
                                                      self.actiongrafico2x2,
                                                      self.actiongraficos,
                                                      self.actiongraficotable])
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
                self.buttonAnalysis.uncheckAnalysisMenu()
            self.whoChecked = toolbar_button

    #todo: criar metodo aqui ou em painted button ou subclass QAction... para checar se o
    #todo: botao selecionou e' tal ou tal (exemplo: e' grafico ou e' grafico2x2)
