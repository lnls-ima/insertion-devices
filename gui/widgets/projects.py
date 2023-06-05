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
from .visual_elements import Canvas, Table
from .visualization_window import VisualizationTabWidget

import numpy as np



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

    def treeItemInfo(self, item: ExploreItem):

        if item.type() is ExploreItem.IDType:

            id_name = item.text(0)
            id_dict = self.insertiondevices[id_name]
            return item, id_name, id_dict
        
        elif item.type() is ExploreItem.AnalysisType:

            *_, id_dict = self.treeItemInfo(item.parent())
            analysis = item.text(0)
            analysis_dict = id_dict[analysis]
            return *_, id_dict, item, analysis, analysis_dict

        elif item.flag() is ExploreItem.ResultType.ResultArray:

            *_, analysis_dict = self.treeItemInfo(item.parent())
            result = item.text(0)
            result_arraynum = analysis_dict[result]
            return *_, analysis_dict, item, result, result_arraynum

        '''depth = tree_item.depth()

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
                analysis_info = self.treeItemInfo(item)
                new_handles, new_labels = visuals.plotAnalysis(chart, analysis_info, isModeAdd)
            
            elif item.flag() is ExploreItem.ResultType.ResultArray:
                result_info = self.treeItemInfo(item)
                new_handles, new_labels = visuals.plotArray(chart, result_info, isModeAdd)

        elif len(items)==2:

            #*: por enquanto so' plotar dados de mesma analise e mesmo mapa de campo

            x_item, y_item = items
            x_info = self.treeItemInfo(x_item)
            y_info = self.treeItemInfo(y_item)
            new_handles, new_labels = visuals.plotPair(chart, x_info, y_info, isModeAdd)
        
        chart.ax.legend(old_handles+new_handles, old_labels+new_labels)

        #maneira de nao criar nada se nao e' selecionado nada nos menus de traj e integral
        # colocando grafico no self
        if not isModeAdd:
            visuals.addTab(chart, "Plot")
        
        # Trigger the canvas to update and redraw
        chart.draw()

        chart.fig.tight_layout()

    def displayTable(self, item: ExploreItem):
        
        # tabela: mapa de campo
        if item.flag() is ExploreItem.IDType.IDData:

            id_item = item
            *_, id_dict = self.treeItemInfo(id_item)
            
            ID_meas = id_dict["InsertionDeviceObject"]
            data = ID_meas._raw_data
            header = ['X[mm]', 'Y[mm]', 'Z[mm]', 'Bx[T]', 'By[T]', 'Bz[T]']
            
        # tabela: analise
        elif item.type() is ExploreItem.AnalysisType:

            analysis_item = item
            *_, analysis_dict = self.treeItemInfo(analysis_item)
            
            params_array = [param for param in analysis_dict.values()
                                      if not isinstance(param, (int, float))]
            data = np.array(params_array).T
            header = list(analysis_dict.keys())
            
        # tabela: resultado
        elif item.flag() is ExploreItem.ResultType.ResultArray:
            
            result_item = item
            *_, result, result_array = self.treeItemInfo(result_item)

            data = result_array.reshape(-1,1)
            header = [result]

        #contrucao da tabela
        tabela = Table(data, header)

        # colocando tabela no visuals
        self.visuals.addTab(tabela, "Table")

class ProjectsTabWidget(BasicTabWidget):

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

        return i

    def closeTab(self, i):
        super().closeTab(i)
        
        #because of the deleteLater behaviour, the count method still counts the tab whom we use deleteLater.
        #So to check if there is only one remaining tab, we still count the "deleted" and check if count==2
        if self.count() == 2:
            self.setTabsClosable(False)
