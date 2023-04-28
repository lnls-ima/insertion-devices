
from PyQt6.QtWidgets import (QWidget,
                             QTreeWidgetItem,
                             QTabWidget,
                             QSplitter,
                             QTreeWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QLabel,
                             QLineEdit)
from PyQt6.QtCore import Qt, QTimer

from . import items

class ProjectWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.filenames = {}
        self.insertiondevice_datas = {}
        self.insertiondevice_models = {}
        self.insertiondevice_trajectories = {}

        self.Dados = items.ExploreItem(items.Items.DataContainer, ['Data'])
        self.Modelos = items.ExploreItem(items.Items.ModelContainer, ['Models'])

        #labels de parametros dos modelos
        
        self.visuals = QTabWidget()
        self.visuals.setDocumentMode(True) # talvez possa ser desabilitado
        self.visuals.setMovable(True)
        #self.visuals.addTab(QWidget(),'Blank')
        self.visuals.setTabsClosable(True)

        self.visuals.tabCloseRequested.connect(self.close_current_tab)

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


    def close_current_tab(self, i):

        self.visuals.removeTab(i)
