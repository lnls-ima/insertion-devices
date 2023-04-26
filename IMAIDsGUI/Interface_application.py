# padrao de nomeacao de variaveis #

# actions
## object name das actions: action<action_name>
## acessamos certa action com self.action<action_name>
## slots das actions: actionNewPressed


import sys

from  PyQt6.QtWidgets import   (QApplication,
                                QWidget,
                                QFrame,
                                QMainWindow,
                                QTabWidget,
                                QStatusBar,
                                QToolBar,
                                QToolButton,
                                QPushButton,
                                QLabel,
                                QLineEdit,
                                QComboBox,
                                QFileDialog,
                                QMenu,
                                QTableView,
                                QHBoxLayout,
                                QVBoxLayout,
                                QScrollArea,
                                QSplitter,
                                QSizePolicy,
                                QTreeWidget,
                                QTreeWidgetItem,
                                QListWidget,
                                QListWidgetItem,
                                QCheckBox,
                                QMessageBox)
from   PyQt6.QtGui    import   (QAction,
                                QIcon,
                                QKeySequence,
                                QPixmap,
                                QPainter,
                                QPolygon,
                                QCursor,
                                QColor,
                                QPalette)
from   PyQt6.QtCore   import   (Qt,
                                QPoint,
                                QSize,
                                pyqtSignal,
                                QAbstractTableModel,
                                QTimer,
                                QEvent,
                                QRect,
                                pyqtSlot)

from widgets import model_dialog, project, table_model

from imaids import fieldsource, insertiondevice



class CheckableListWidget(QListWidget):

    def __init__(self, items,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self.items_checked = []

        self.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.itemChanged.connect(self.handle_item_changed)

        # Create the list items and add them to the list widget
        items_list = []

        for list_item in items:
            itemn = QListWidgetItem(list_item, self)
            itemn.setFlags(itemn.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            itemn.setCheckState(Qt.CheckState.Unchecked)
            items_list.append(itemn)
        

    def handle_item_changed(self, item):

        if item.checkState() == Qt.CheckState.Checked:
            if item not in self.items_checked:
                self.items_checked.append(item.text())
        else:
            if item.text() in self.items_checked:
                self.items_checked.remove(item.text())
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            print(self.items_checked)   
        else:
            super().keyPressEvent(event)


class AnalysisMenu(QFrame):
    def __init__(self, items, *args, **kwargs):
        super().__init__(*args, **kwargs)

        menu = QMenu()
        estilo = menu.style()

        self.setObjectName("frame")

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.setLineWidth(1)
        
        #palette = self.palette()
        #background_color = palette.color(QPalette.ColorRole.Menu)

        # change the background color without affect the other widgets in the container:
        # https://stackoverflow.com/questions/62046679/qframe-background-color-overlapped-with-other-widgets-like-qlineedit-qlistboxwi
        self.setStyleSheet("QFrame#frame{background-color: #f0f0f0}")
        
        #self.setStyle(estilo)
        
        self.list = CheckableListWidget(items=items,parent=self)
        self.list.setStyleSheet("background-color: #f0f0f0")
        checkBoxSelectAll = QCheckBox("Select All",self)
        checkBoxSelectAll.stateChanged.connect(self.check)
        # todo: quando selecionar todos, mudar icone de apply para varinha ou chapeu
        self.apply = QPushButton("Apply")

        menuAnalysis_layout = QVBoxLayout(self)

        menuAnalysis_layout.addWidget(self.list)
        menuAnalysis_layout.addWidget(checkBoxSelectAll)
        menuAnalysis_layout.addWidget(self.apply)

    
    # todo: criar metodo para retornar lista de items checked e unchecked

    def checkedItems(self):
        return [item for item in self.list.items()]
    
    def check(self,checked):
        #self.list.selectAll()
        if checked:
            self.apply.setIcon(QIcon('icons/icons/wand.png'))
            for i in range(self.list.count()):
                self.list.item(i).setCheckState(Qt.CheckState.Checked)
        else:
            self.apply.setIcon(QIcon(None))
            for i in range(self.list.count()):
                self.list.item(i).setCheckState(Qt.CheckState.Unchecked)
    
    # def eventFilter(self, obj, event) -> bool:
    #     if event.type() ==QEvent.Type.FocusOut:
    #         self.setHidden(True)
    #     return super().eventFilter(obj, event)


class DoublePushButton(QPushButton):
    doubleClicked = pyqtSignal()
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clicked.emit)
        super().clicked.connect(self.checkDoubleClick)

    # melhorar essa implementacao, o intervalo de tempo esta sendo usado para
    # executar a acao de um clique tambem

    # na verdade nao ha como, e' preciso esperar para saber se e' clique duplo ou nao
    @pyqtSlot()
    def checkDoubleClick(self):
        if self.timer.isActive():
            self.doubleClicked.emit()
            self.timer.stop()
        else:
            self.timer.start(250)


class ButtonMenu(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setFixedSize(32,32)

        self.clicked.connect(self.button_clicked)

        self.custom_buttonMenu = QMenu(self)

    def button_clicked(self,s):
        self.show_menu()

    def show_menu(self):
        self.custom_buttonMenu.popup(self.mapToGlobal(self.rect().bottomLeft()))


class PaintedButton(ButtonMenu):

    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        len = int(min(self.width(),self.height())/2)
        
        # coordinates of the polygon points must be integers
        square = QPolygon([QPoint(width,height),
                           QPoint(width,height-len),
                           QPoint(width-len,height-len),
                           QPoint(width-len, height)])
        painter.setBrush(Qt.GlobalColor.blue)
        painter.drawPolygon(square)
        painter.end()
    
    def button_clicked(self,s):

        cursor_pos = QCursor.pos()
        widget_pos = self.mapFromGlobal(cursor_pos)

        x, y = widget_pos.x(), widget_pos.y()

        width = self.width()
        height = self.height()
        len = min(self.width(),self.height())/2

        if (width-len <= x <= width) and (height-len <= y <= height):
            self.setChecked(False)
            print('dentro')
            self.show_menu()
        else:
            print('fora')

    def show_menu(self):
        self.custom_buttonMenu.popup(self.mapToGlobal(self.rect().bottomLeft()))


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.filename = None
        self.dados = None

        # botao
        self.PlusButton = QToolButton()
        self.PlusButton.setText("+")
        ## signals
        self.PlusButton.clicked.connect(self.add_project)
        
        # tab widget
        self.projects = QTabWidget()
        ## tabs features
        self.projects.setDocumentMode(True) # talvez possa ser desabilitado
        self.projects.setMovable(True)
        ## signals
        self.projects.tabCloseRequested.connect(self.close_current_tab)
        self.projects.tabBarDoubleClicked.connect(self.start_rename)
        ## adicionando tab inicial
        self.project = project.ProjectWidget()
        self.project.tree.itemClicked.connect(self.on_item_clicked)
        self.projects.addTab(self.project,'Project')
        ## adicionando botao
        self.projects.setCornerWidget(self.PlusButton,corner=Qt.Corner.TopLeftCorner)


        # actions
        ## File menu actions
        self.actionNew_Project = QAction("New Project", self)
        self.actionNew_Project.triggered.connect(self.add_project)
        self.actionOpen_Data = QAction("Open Data ...", self)
        self.actionOpen_Data.triggered.connect(self.browse_for_data)
        self.actionGenerate_Model = QAction("Generate Model", self)
        self.actionGenerate_Model.triggered.connect(self.model_generation)
        self.actionClose = QAction("Close", self)
        ## Edit menu actions
        self.actionUndo = QAction("Undo", self)
        self.actionRedo = QAction("Redo", self)
        ## View menu action
        # mais pra frente
        ## Analysis toolbar menu actions
        # de outra maneira agora


        # menubar
        self.menubar = self.menuBar()
        ## File
        self.menuFile = self.menubar.addMenu("&File")
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen_Data)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionGenerate_Model)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.actionQuit = self.menuFile.addAction("Quit")
        self.actionQuit.triggered.connect(self.quit_app)
        ## Edit
        self.menuEdit = self.menubar.addMenu("&Edit")
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionRedo)
        ## View: contem opcoes de esconder widgets, tais como toolbar
        self.menuView = self.menubar.addMenu("&View")
        ## Settings
        self.menuSettings = self.menubar.addMenu("&Settings")
        ## Help: documentacao da interface
        self.menuHelp = self.menubar.addMenu("&Help")


        # tool bar
        self.toolbar = QToolBar("Barra de Ferramentas")
        self.toolbar.setObjectName("Barra de Ferramentas")
        actionToolbar = QAction(self.toolbar.objectName(), self, checkable=True)
        actionToolbar.setChecked(True)
        actionToolbar.triggered.connect(self.toolbar.setVisible)
        self.menuView.addAction(actionToolbar)
        self.addToolBar(self.toolbar)

        # button analysis
        self.buttonAnalysis = QPushButton("Analysis",parent=self.toolbar)
        print('button analysis parent:',self.buttonAnalysis.parent())
        self.buttonAnalysis.clicked.connect(self.toggle_list_visibility)
        #self.buttonAnalysis.doubleClicked.connect(self.clique_duplo)
        self.toolbar.addWidget(self.buttonAnalysis)
        self.toolbar.addSeparator()

        itens = ["Phase Error",
                 "Roll Off",
                 "Kickmap",
                 "Trajectory",
                 "Magnetic Field",
                 "Shimming",
                 "Cross Talk",
                 "Field Integral"]
        
        self.menuAnalysis = AnalysisMenu(items=itens,parent=self)
        #print(self.menuAnalysis.checkedItems())
        self.menuAnalysis.apply.clicked.connect(self.manage_analysis)
        self.menuAnalysis.setHidden(True)


        grafico = QIcon("icons/icons/guide.png")
        self.tabela = QIcon("icons/icons/table.png")
        self.dog = QIcon("icons/icons/animal-dog.png")
        self.cat = QIcon("icons/icons/animal.png")
        self.bug = QIcon("icons/icons/bug.png")
        
        self.actiontabela = QAction(self.tabela,"tabela",self)
        self.actiontabela.setObjectName("tabela")
        self.actiondog = QAction(self.dog,"cachorro",self)
        self.actiondog.setObjectName("dog")
        self.actioncat = QAction(self.cat,"gato",self)
        self.actioncat.setObjectName("cat")
        self.actionbug = QAction(self.bug,"inseto",self)
        self.actionbug.setObjectName("bug")


        self.toolbar_buttonPlot = PaintedButton("Plot")
        self.toolbar_buttonPlot.setIcon(grafico)
        self.toolbar_buttonPlot.setCheckable(True)
        self.toolbar.addWidget(self.toolbar_buttonPlot)
        self.toolbar.addSeparator()

        self.toolbar_buttonTable = PaintedButton("Table")
        self.toolbar_buttonTable.setIcon(self.tabela)
        self.tabela = self.toolbar_buttonTable.icon()
        self.toolbar_buttonTable.setCheckable(True)

        self.actiontabela.triggered.connect(self.action_swap)
        self.actiondog.triggered.connect(self.action_swap)
        self.actioncat.triggered.connect(self.action_swap)
        self.actionbug.triggered.connect(self.action_swap)

        self.toolbar_buttonTable.custom_buttonMenu.addActions([self.actiontabela,
                                                               self.actioncat,
                                                               self.actiondog,
                                                               self.actionbug])

        # self.toolbar_buttonTable.manager.connect(self.table_manager)
        self.toolbar.addWidget(self.toolbar_buttonTable)
        

        # status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)


        # coisas de Qmainwindow
        self.app = app
        self.setWindowTitle("IMAIDS Interface")
        self.setCentralWidget(self.projects)
        self.resize(900,600)
        


    # window slots
    

    # menu slots

    def add_project(self, i):

        if self.projects.count() == 1:
            self.projects.setTabsClosable(True)
        
        i = self.projects.addTab(project.ProjectWidget(), f"Project {self.projects.count()+1}")
        self.projects.setCurrentIndex(i)
    
    def browse_for_data(self,s):
        filename=QFileDialog.getOpenFileName(self, 'Open data', 'Documents', 'Data (*.dat)')
        filename = filename[0]

        self.filename = filename
        
        #pegar indice do project atual e acessar tree do project atual
        #por fim, na tree atual, inserir Dados 1
        self.treeInsertData(filename)

        #print(filename)
        # if filename != '':
        #     self.table_data(filename)
        # else:
        #     return
        #return filename

    def treeInsertData(self,filename):
        if not self.project.tree.topLevelItemCount():
            self.dados = QTreeWidgetItem(['Dados'])
            self.project.Datas = self.project.tree.insertTopLevelItem(0,self.dados)
        self.dados.addChild(QTreeWidgetItem([f'Dados {self.dados.childCount()+1}']))

    def model_generation(self):
        dialog = model_dialog.ModelDialog(parent=self)
        dialog.exec()
    
    def quit_app(self):
        answer = QMessageBox.question(self,
                                      "Quit Question",
                                      "Are you sure you want to quit the application?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)

        if answer == QMessageBox.StandardButton.Yes:
            self.app.quit()

    
    # tool bar slots

    def toggle_list_visibility(self):

        topleft_corner = self.toolbar.mapToParent(self.buttonAnalysis.geometry().bottomLeft())
        print(topleft_corner)
        self.menuAnalysis.raise_()
        self.menuAnalysis.setGeometry(QRect(topleft_corner.x()+1, topleft_corner.y(), 150, 300))

        if self.menuAnalysis.isVisible():
            self.menuAnalysis.setHidden(True)
        else:
            self.menuAnalysis.setHidden(False)
    
    def manage_analysis(self):
        # obter lista dos items checked
        #self.menuAnalysis.list.
        return
    
    def action_swap(self):
        action = self.sender()
        self.toolbar_buttonTable.setIcon(action.icon())
        self.toolbar_buttonTable.setChecked(True)
        self.toolbar_buttonTable.setObjectName(action.objectName())

    def table_data(self):
        
        # todo: passar essa condicao para outro lugar e torna-la mais geral
        if self.project.visuals.count() == 1:
            self.project.visuals.setTabsClosable(True)
        
        tabela = QTableView()
        modelo = table_model.TableModel(self.filename)
        tabela.setModel(modelo)

        horizontal_color = QColor.fromRgb(80, 174, 144)
        vertical_color = QColor.fromRgb(136, 59, 144, int(0.8*255))
        horizontal_header_style = "QHeaderView::section {{background-color: {} }}".format(horizontal_color.name())
        vertical_header_style = "QHeaderView::section {{background-color: {} }}".format(vertical_color.name())
        tabela.horizontalHeader().setStyleSheet(horizontal_header_style)
        tabela.verticalHeader().setStyleSheet(vertical_header_style)

        i = self.project.visuals.addTab(tabela, "tabela")
        self.project.visuals.setCurrentIndex(i)
    

    # tab bar slots
        
    def close_current_tab(self, i):

        # if there is only one tab
        if self.projects.count() == 1:
            # do nothing
            return

        # else remove the tab
        self.projects.removeTab(i)

        if self.projects.count() == 1:
            self.projects.setTabsClosable(False)
    
    def start_rename(self, tab_index):
        self.editting_tab = tab_index
        rect = self.projects.tabBar().tabRect(tab_index)
        pos = rect.bottomRight()   # map to parent aqui como foi feito em entrou_action
        w = rect.width()
    
        top_margin = 4
        left_margin = 2

        self.edit = QLineEdit(self)
        self.edit.show()
        self.edit.move(pos.x()-w+20+left_margin,3*pos.y()+top_margin)

        # verificar se todos os rect das abas teem mesmo tamanho

        self.edit.resize(w, self.edit.height())
        self.edit.setText(self.projects.tabText(tab_index))
        self.edit.selectAll()
        self.edit.setFocus() # talvez de problema quando clicar fora do line edit enquanto ele tiver aberto
        self.edit.editingFinished.connect(self.finish_rename)

    def finish_rename(self):
        self.projects.setTabText(self.editting_tab, self.edit.text())
        self.edit.deleteLater()


    # tree slots

    def on_item_clicked(self, item, column):
        #print(item.text(0))

        # por algum motivo muito obscuro, quando o icone e' tabela no botao,
        # self.toolbar_buttonTable.icon()==self.actiontabela.icon() aind e' False
        # Alem disso, as ids de actiontabela.icon() e actiondog.icon() sao as mesmas
        # solucao encontrada: em vez de comparar os icones, trocar tambem os nomes dos
        # objetos e comparar os nomes
        
        # plotar tabela
        if self.toolbar_buttonTable.isChecked() and \
            self.toolbar_buttonTable.objectName()==self.actiontabela.objectName():
            
            if item.text(0)=='Dados 1':
                self.table_data()
    
    def magnetic_field(self):
        print('entrou magnetic_field method')
        return
    
    def trajectory(self):
        print('entrou trajectory method')
        return
    
    def phase_error(self):
        print('entrou phase_error method')
        return


    # outros metodos

    def mousePressEvent(self, event):
        #posicao do cursor do mouse nas coordenadas da window
        cursor_pos = QCursor.pos()
        widget_pos = self.mapFromGlobal(cursor_pos)
        print("Current cursor position at widget: x = %d, y = %d" % (widget_pos.x(), widget_pos.y()))

        return
    
    def mouseDoubleClickEvent(self, a0) -> None:
        print('duplo')
        return super().mouseDoubleClickEvent(a0)




# execution

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
