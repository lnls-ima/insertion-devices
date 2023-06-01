import typing

from  PyQt6.QtWidgets import   (QWidget,
                                QMainWindow,
                                QTabWidget,
                                QLineEdit,
                                QToolButton,
                                QDockWidget,
                                QInputDialog,
                                QMenu,
                                QMessageBox)
from   PyQt6.QtGui    import    QIcon, QAction
from   PyQt6.QtCore   import   (Qt,
                                pyqtSignal)

from .basics import BasicTabWidget
from .explore_window import ExploreItem, ExploreTreeWidget
from .visual_elements import Canvas
from .visualization_window import VisualizationTabWidget



class ProjectWidget(QMainWindow):

    def __init__(self):
        super().__init__()

        self.filenames = []
        self.insertiondevices = {}
        self.params = {}

        self.visuals = VisualizationTabWidget()

        self.dockTree = QDockWidget("Explore Window",self)
        #self.dockTree.visibilityChanged.connect(self.dockVisibility)
        #features = self.dockTree.features() ^ QDockWidget.DockWidgetFeature.DockWidgetClosable
        #self.dockTree.setFeatures(features)
        #todo: change qtreewidget to qtreeview to allow a better customization
        self.tree = ExploreTreeWidget(parent=self.dockTree)
        self.dockTree.setWidget(self.tree)
        
        self.dockCommand = QDockWidget("Command Line",self)
        self.command_line = QLineEdit()
        self.command_line.setContentsMargins(4, 0, 4, 4)
        self.dockCommand.setWidget(self.command_line)

        #todo: tentar depois deixar visuals dentro de dockwidget tambem, mas sem dar bugs
        self.setCentralWidget(self.visuals)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.dockTree)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea,self.dockCommand)

    '''def projectTreeItemInfo(self, tree_item: ExploreItem):

        depth = tree_item.depth()

        id_name = tree_item.idName()
        id_dict = self.insertiondevices[id_name]

        if depth>=2:
            second = tree_item.parent().text(0)
            if depth==3:
                third = tree_item.parent().parent().text(0)


        if depth>=1:
            id_dict = self.insertiondevices[id_name]
            if depth>=2:
                analysis = tree_item.item_type.value
                analysis_dict = id_dict[analysis]
                if depth>=3:
                    result = tree_item.text(0)
                    return id_dict, analysis_dict, result
                else:
                    return id_dict, analysis_dict
            else:
                return id_dict'''

    def countIDnames(self, IDname):
        models_names = [device[:-2] for device in self.insertiondevices]
        num = models_names.count(IDname)+1
        return num

    def analyzeItem(self, id_item: ExploreItem, analysis_actived: list):

        id_name = id_item.text(0)
        id_dict = self.insertiondevices[id_name]

        for calcAnalysis in analysis_actived:
            analysis = calcAnalysis.__name__.lstrip("calc").replace("_"," ")

            #todo: quando realiza a analise, mudar cursor para cursor de espera
            
            #todo: checar item, nao o texto
            if analysis not in id_dict:
                analysisType = ExploreItem.AnalysisType(analysis)
                analysis_item = ExploreItem(analysisType, id_item, [f"{analysis}", "Analysis"])
                analysis_item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight)
                if not id_item.isExpanded():
                    self.tree.expandItem(id_item)

                result_items = calcAnalysis(analysis_item, id_dict)
                [item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight) for item in result_items]
            
            else:
                QMessageBox.warning(self,
                                    f"Analysis Warning",
                                    f"{analysis} of ({id_name}) already calculated!")
    
            if analysis=="Cross Talk":
                self.update_ids_dict_key(key=id_name, new_key=id_item.text(0))

    def update_ids_dict_key(self, key, new_key):
        ids_dict = self.insertiondevices

        if key in ids_dict:
            value = ids_dict.pop(key)
            ids_dict[new_key] = value
            return True
        else:
            return False
        
    
    def drawItems(self, items: typing.List[ExploreItem]):

        visuals = self.visuals

        isModeAdd = not visuals.tabIcon(visuals.currentIndex()).isNull()

        if isModeAdd:
            chart = visuals.currentWidget()
            hideAxesLabels = True
            legend = chart.ax.legend_
            old_handles = legend.legendHandles
            old_labels = [label.get_text() for label in legend.get_texts()]
        else:
            chart = Canvas()
            chart.ax.grid(visible=True)
            old_handles, old_labels = [], []

        if len(items)==1:
            item, = items

            if item.type() is ExploreItem.AnalysisType:

                id_name = item.parent().text(0)
                id_dict = self.insertiondevices[id_name]
                analysis = item.item_type.value
                analysis_dict = id_dict[analysis]

                plot_text, legend = visuals.plotAnalysis(chart, id_name, item.flag(), analysis_dict)
                dflt_title, dflt_ylabel, dflt_xlabel = plot_text
                new_handles, new_labels = legend
            
            elif item.flag() is ExploreItem.ResultType.ResultArray:

                id_name = item.parent().parent().text(0)
                id_dict = self.insertiondevices[id_name]
                analysis = item.parent().item_type.value
                analysis_dict = id_dict[analysis]
                result = item.text(0)
                
                hideAxesLabels = False
                plot_text, legend = visuals.plotArray(chart,result,analysis_dict)
                dflt_title, dflt_ylabel, dflt_xlabel = plot_text
                new_handles, new_labels = legend

        elif len(items)==2:

            #*: por enquanto so' plotar dados de mesma analise e mesmo mapa de campo

            x_item, y_item = items

            id_name = x_item.parent().parent().text(0)
            id_dict = self.insertiondevices[id_name]
            analysis = x_item.parent().item_type.value
            analysis_dict = id_dict[analysis]
            x_label = x_item.text(0)
            y_label = y_item.text(0)
            x = analysis_dict[x_label]
            y = analysis_dict[y_label]

            plot_text, legend = visuals.plotPair(chart, id_name, x, x_label, y, y_label)
            dflt_title, dflt_ylabel, dflt_xlabel = plot_text
            new_handles, new_labels = legend
        
        chart.ax.legend(old_handles+new_handles, old_labels+new_labels)

        #maneira de nao criar nada se nao e' selecionado nada nos menus de traj e integral
        if isModeAdd:
            chart.ax.set_title("")
            if hideAxesLabels:
                chart.ax.set_xlabel("")
                chart.ax.set_ylabel("")
        else:
            # default text
            chart.ax.set_title(dflt_title)
            chart.ax.set_ylabel(dflt_ylabel)
            chart.ax.set_xlabel(dflt_xlabel)
            # colocando grafico no self
            self.visuals.addTab(chart, "Plot")
        
        # Trigger the canvas to update and redraw
        chart.draw()

        chart.fig.tight_layout()


class ProjectsTabWidget(BasicTabWidget):

    projectAdded = pyqtSignal(int)

    def __init__(self,parent):
        super().__init__(parent, leftSpace=22)

        self.setTabsClosable(False)

        # plus button: abrir novo projeto
        self.PlusButton = QToolButton()
        self.PlusButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.PlusButton.setIcon(QIcon("icons/icons/plus-button.png"))
        self.PlusButton.pressed.connect(self.addTab)
        self.setCornerWidget(self.PlusButton,corner=Qt.Corner.TopLeftCorner)

    # metodo widget redefinido apenas para impor que o retorno e' objeto do tipo ProjectWidget
    def widget(self, index: int) -> ProjectWidget:
        return super().widget(index)
    # metodo currentWidget redefinido apenas para impor que o retorno e' objeto do tipo ProjectWidget
    def currentWidget(self) -> ProjectWidget:
        return super().currentWidget()
    
    def addTab(self, widget='ProjectWidget', text='default'):
        
        if self.count() == 1:
            self.setTabsClosable(True)

        if widget=='ProjectWidget':
            widget=ProjectWidget()
        if text=='default':
            text=f"Project {self.count()+1}"
        
        i = super().addTab(widget=widget,text=text)

        # *: o abaixo sera feito na main_window, apos conectar com sinal
        #self.widget(i).tree.itemClicked.connect(self.on_item_clicked)
        self.projectAdded.emit(i)

        return i

    def closeTab(self, i):
        super().closeTab(i)
        
        #because of the deleteLater behaviour, the count method still counts the tab whom we use deleteLater.
        #So to check if there is only one remaining tab, we still count the "deleted" and check if count==2
        if self.count() == 2:
            self.setTabsClosable(False)
