
from  PyQt6.QtWidgets import   (QWidget,
                                QMainWindow,
                                QTabWidget,
                                QTreeWidget,
                                QLineEdit,
                                QToolButton,
                                QDockWidget,
                                QInputDialog,
                                QMenu)
from   PyQt6.QtGui    import    QColor, QIcon, QAction, QKeyEvent
from   PyQt6.QtCore   import   (Qt,
                                pyqtSignal,
                                QItemSelection,
                                QItemSelectionModel,
                                QItemSelectionRange)

from .items import ExploreItem
from .canvas import Canvas



class BasicTabWidget(QTabWidget):
    def __init__(self,parent=None, leftSpace=0):
        super().__init__(parent)

        self.leftSpace = leftSpace
        #para o triggered saber a posicao da tab do menu
        self.tabPos = None

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        #todo: descobrir o que o documentMode faz e se pode tirar esse comando ou nao
        self.setDocumentMode(True) # talvez possa ser desabilitado
        self.setMovable(True)
        self.setTabsClosable(True)
        
        self.tabCloseRequested.connect(self.closeTab)
        self.tabBarDoubleClicked.connect(self.start_rename)
        self.customContextMenuRequested.connect(self.exec_context_menu)

        self.menuContext = QMenu(self)
        actionRename = self.menuContext.addAction("Rename Tab")
        actionRename.triggered.connect(self.rename_tab)


    def exec_context_menu(self, pos):
        self.tabPos = pos
        self.menuContext.exec(self.mapToGlobal(self.tabPos))
    
    def rename_tab(self):
        
        index = self.tabBar().tabAt(self.tabPos)

        new_text, ok = QInputDialog.getText(self, 'Rename Item', 'Enter new name:', text=self.tabText(index))
        
        if ok:
            self.setTabText(index, new_text)

    def start_rename(self, tab_index):
        self.editting_tab = tab_index

        tab_rect = self.tabBar().tabRect(tab_index)
        corner = self.mapToParent(tab_rect.topLeft())

        self.edit = QLineEdit(parent=self.parent())
        self.edit.textChanged.connect(self.resize_to_content)
        self.edit.editingFinished.connect(self.finish_rename)
        
        left_margin = 10
        self.edit.move(corner.x()+left_margin+self.leftSpace, corner.y())
        self.edit.setFixedHeight(tab_rect.height())

        self.edit.setText(self.tabText(tab_index))
        self.edit.selectAll()
        self.edit.setFocus() # talvez de problema quando clicar fora do line edit enquanto ele tiver aberto

        self.edit.show()

    def resize_to_content(self):
        X_margin = 15
        self.edit.setFixedWidth(10+X_margin+self.edit.fontMetrics().boundingRect(self.edit.text()).width())

    def finish_rename(self):
        self.setTabText(self.editting_tab, self.edit.text())
        self.edit.deleteLater()

    def addTab(self, widget: QWidget, text: str) -> int:
        i = super().addTab(widget, text)
        #addTab adiciona a nova tab, mas mantem o usuario na tab inicial, nao na adicionada
        #para mudar para a tab adicionada, usar o setcurrentindex abaixo
        self.setCurrentIndex(i)
        return i
    
    def closeTab(self, i):
        self.widget(i).deleteLater()




class VisualizationTabWidget(BasicTabWidget):

    def __init__(self):
        super().__init__(leftSpace=-1)

        self.actionActiveAdd = QAction("Add Mode")
        self.actionActiveAdd.setCheckable(True)
        self.actionActiveAdd.setVisible(False)
        self.actionActiveAdd.triggered.connect(self.changeIcon)
        self.menuContext.addAction(self.actionActiveAdd)
        
    
    def exec_context_menu(self, pos):

        self.tabPos = pos
        index = self.tabBar().tabAt(self.tabPos)

        if isinstance(self.widget(index),Canvas):
            self.actionActiveAdd.setVisible(True)

            # sincronizar checkstate da action com icone na tab clicada
            if self.tabIcon(index).isNull():
                self.actionActiveAdd.setChecked(False)
            else:
                self.actionActiveAdd.setChecked(True)
        else:
            self.actionActiveAdd.setVisible(False)
        
        super().exec_context_menu(self.tabPos)

    def changeIcon(self):

        index = self.tabBar().tabAt(self.tabPos)

        if self.actionActiveAdd.isChecked():
            self.setTabIcon(index, QIcon("icons\icons\plus-white.png"))
        else:
            self.setTabIcon(index, QIcon(None))
        

#todo: modelo de selecao:
#todo: - mudar cor e comportamento apenas quando estiver no modo de plot
#todo: - desmarcar selecao quando clicar fora da tree
#todo: - nao poder selecionar resultados numericos
#todo: - nao poder selecionar mais de dois dados
#todo: - se clicou primeiro em analise, nao poder selecionar com ctrl outras coisas

class TreeSelectionModel(QItemSelectionModel):
    def __init__(self, model):
        super().__init__(model)

    def select(self, selection: 'QItemSelection', command) -> None:
        super().select(selection, command)

class ExploreTreeWidget(QTreeWidget):

    selectReturned = pyqtSignal(list)
    keyPressed = pyqtSignal(QKeyEvent)

    def __init__(self, parent=None,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)

        self.whosSelected = []

        self.itemSelectionChanged.connect(self.selection_changed)
        
        self.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.setColumnCount(2)
        self.setHeaderLabels(["Item", "Content"])
        #self.setHeaderHidden(True)
        self.header().resizeSection(0, 1.8*self.width())
        self.setIndentation(12)
        self.headerItem().setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        self.setMinimumWidth(self.parent().parent().width()*0.47)

        # 0: primeiro da lista top level
        data_container = ExploreItem(ExploreItem.Container.ContainerData, ["Data", "Container"])
        self.insertTopLevelItem(0, data_container)
        self.topLevelItem(0).setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        # 1: segundo da lista top level
        model_container = ExploreItem(ExploreItem.Container.ContainerModel, ["Models", "Container"])
        self.insertTopLevelItem(1, model_container)
        self.topLevelItem(1).setTextAlignment(1, Qt.AlignmentFlag.AlignRight)


    def selection_changed(self):
        
        selected_items = self.selectedItems()

        for item in selected_items:
            if item not in self.whosSelected:
                item.setBackground(0, QColor("lightgreen"))
                item.setBackground(1, QColor("lightgreen"))
        for item in self.whosSelected:
            if item not in selected_items:
                item.setBackground(0, QColor("white"))
                item.setBackground(1, QColor("white"))
        
        self.whosSelected = selected_items

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key.Key_Space,Qt.Key.Key_Return,Qt.Key.Key_Enter]:
            self.selectReturned.emit(self.whosSelected)
        elif event.key() in [Qt.Key.Key_G,Qt.Key.Key_P, Qt.Key.Key_T]:
            self.keyPressed.emit(event)
        else:
            return super().keyPressEvent(event)


class ProjectWidget(QMainWindow):

    def __init__(self):
        super().__init__()

        self.filenames = []
        self.insertiondevices = {}

        self.visuals = VisualizationTabWidget()

        self.dockTree = QDockWidget("Explore Window",self)
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

class ProjectsTabWidget(BasicTabWidget):

    projectAdded = pyqtSignal(int)

    def __init__(self,parent):
        super().__init__(parent, leftSpace=22)

        self.setTabsClosable(False)

        ## projects tab widget - tab inicial
        #self.addTab(text='Project')
        ## projects tab widget - plus button: abrir mais uma aba de projeto
        #todo: passar action par toolbutton virar action tal como visto em sua documentacao
        #todo: passar + dos bultin icons ou algum icon que baixei
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
