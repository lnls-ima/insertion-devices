
from PyQt6.QtWidgets import (QWidget,
                             QTreeWidgetItem,
                             QTabWidget,
                             QSplitter,
                             QTreeWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QLabel,
                             QLineEdit,
                             QToolButton)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from .items import ExploreItem


class ProjectWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.filenames = []
        self.insertiondevices = {}
        self.insertiondevice_trajectories = {}

        self.Dados = ExploreItem(ExploreItem.Type.ContainerData, ['Data'])
        self.Modelos = ExploreItem(ExploreItem.Type.ContainerModel, ['Models'])

        #labels de parametros dos modelos
        
        self.visuals = QTabWidget()
        self.visuals.setDocumentMode(True) # talvez possa ser desabilitado
        self.visuals.setMovable(True)
        #self.visuals.addTab(QWidget(),'Blank')
        self.visuals.setTabsClosable(True)

        self.visuals.tabCloseRequested.connect(self.visuals.removeTab)

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Orientation.Horizontal)

        self.tree = QTreeWidget()
        self.tree.insertTopLevelItem(0,self.Dados)   # 0: primeiro da lista top level
        self.tree.insertTopLevelItem(1,self.Modelos) # 1: segundo da lista top level
        
        # todo: alterar modo de selecao da tree para poder clicar de novo e o item ficar desmarcado
        self.tree.setHeaderHidden(True)
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.visuals)

        vbox = QVBoxLayout(self)

        self.command_window_box = QHBoxLayout()
        self.command_window_box.setSpacing(0)
        
        self.command_label = QLabel(">>>")
        self.command_label.setFixedHeight(20)
        self.command_label.setStyleSheet(u"background-color: rgb(255, 255, 255)")
        self.command_line = QLineEdit()
        self.command_line.setFixedHeight(20)
        self.command_line.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
                                        "border-top: 1px solid #CCCCCC;\n"
                                        "border-left: 1px solid #DDDDDD;\n"
                                        "border-right: 1px solid #DDDDDD;\n"
                                        "border-bottom: 1px solid #DDDDDD; \n"
                                        "background-color: white;\n"
                                        "border: 0px")

        self.command_window_box.addWidget(self.command_label)
        self.command_window_box.addWidget(self.command_line)

        vbox.addWidget(self.splitter)
        # envolver a command window box com frame
        # animacao de line edit:
        #   quando esta sem foco, borda e' cinza
        #   quando esta sem foco e mouse passa por cima nada acontece
        #   quando esta em foco borda e' azul claro
        #   quando esta em foco e mouse passa por cima, borda volta a ser cinza
        vbox.addLayout(self.command_window_box)
        
        widt = self.width()

        self.splitter.setSizes([int(widt/4),int(3*widt/4)])


        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.handleResize)
        self.resize_timer.setInterval(500)

        # objetos
        self.Datas = None
        self.Models = None
        self.Tables = None
        self.Plots = None
    

    def resizeEvent(self, event):
        if not self.resize_timer.isActive():
            #print("Resizing...")

            widt_tree = self.tree.width()
            # setSizePolicy estava dando problema, mas da maneira abaixo funciona
            self.tree.setFixedWidth(widt_tree)
            self.resize_timer.start()

    def handleResize(self):
        #print("Resize done")

        widt_tree = self.tree.width()
        widt_visual = self.visuals.width()
        self.splitter.setSizes([widt_tree,widt_visual])

        # setSizePolicy estava dando problema, mas da maneira abaixo funciona
        self.tree.setMinimumWidth(0)
        self.tree.setMaximumWidth(self.splitter.width())
        self.resize_timer.stop()
    
    # def on_item_clicked(self, item, column):
    #     #self.tree_item = item.text()
    #     raise NotImplementedError


class TabProjects(QTabWidget):

    itemconnect = pyqtSignal(int) #pass a type/class as signal argument

    def __init__(self,parent):
        super().__init__(parent)

        ## projects tab widget - features
        self.setDocumentMode(True) # talvez possa ser desabilitado
        self.setMovable(True)
        ## projects tab widget - signals
        self.tabCloseRequested.connect(self.close_current_tab)
        self.tabBarDoubleClicked.connect(self.start_rename)
        ## projects tab widget - tab inicial
        self.addTab(ProjectWidget(),'Project')
        #self.widget(0).tree.itemClicked.connect(self.on_item_clicked)
        self.itemconnect.emit(0)
        ## projects tab widget - plus button: abrir mais uma aba de projeto
        self.PlusButton = QToolButton()
        self.PlusButton.setText("+")
        self.PlusButton.clicked.connect(self.add_project)
        self.setCornerWidget(self.PlusButton,corner=Qt.Corner.TopLeftCorner)

    # metodo widget redefinido apenas para impor que o retorno e' objeto do tipo ProjectWidget
    def widget(self, index: int) -> ProjectWidget:
        return super().widget(index)
    # metodo currentWidget redefinido apenas para impor que o retorno e' objeto do tipo ProjectWidget
    def currentWidget(self) -> ProjectWidget:
        return super().currentWidget()
    
    def add_project(self, i):

        if self.count() == 1:
            self.setTabsClosable(True)
        
        i = self.addTab(ProjectWidget(), f"Project {self.count()+1}")
        self.setCurrentIndex(i)

        # todo: emitir sinal de new_project
        # todo: descobir como emitir sinal e passar algo pelo sinal, como existem alguns que ja usei
        # *: o abaixo sera feito na main_window, apos conectar com sinal
        #self.widget(i).tree.itemClicked.connect(self.on_item_clicked)
        self.itemconnect.emit(i)

    def close_current_tab(self, i):

        # if there is only one tab
        if self.count() == 1:
            # do nothing
            return

        # else remove the tab
        self.removeTab(i)

        if self.count() == 1:
            self.setTabsClosable(False)

    #todo: corrigir self ai para ser o parent
    def start_rename(self, tab_index):
        self.editting_tab = tab_index
        rect = self.tabBar().tabRect(tab_index)
        pos = rect.bottomRight()
        w = rect.width()
    
        top_margin = 4
        left_margin = 2

        self.edit = QLineEdit(parent=self.parent())
        self.edit.show()
        # todo: corrigir como coloca-se y
        self.edit.move(pos.x()-w+20+left_margin,3*pos.y()+top_margin)

        # verificar se todos os rect das abas teem mesmo tamanho

        self.edit.resize(w, self.edit.height())
        self.edit.setText(self.tabText(tab_index))
        self.edit.selectAll()
        self.edit.setFocus() # talvez de problema quando clicar fora do line edit enquanto ele tiver aberto
        self.edit.editingFinished.connect(self.finish_rename)

    def finish_rename(self):
        self.setTabText(self.editting_tab, self.edit.text())
        self.edit.deleteLater()
