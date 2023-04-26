# padrao de nomeacao de variaveis #

# actions
## object name das actions: action<action_name>
## acessamos certa action com self.action<action_name>
## slots das actions: actionNewPressed


import sys

from  PyQt6.QtWidgets import   (QApplication,
                                QWidget,
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
                                QCheckBox)
from   PyQt6.QtGui    import   (QAction,
                                QIcon,
                                QKeySequence,
                                QPixmap,
                                QPainter,
                                QPolygon,
                                QCursor,
                                QColor)
from   PyQt6.QtCore   import   (Qt,
                                QPoint,
                                QSize,
                                pyqtSignal,
                                QAbstractTableModel,
                                QTimer,
                                QEvent)

from widgets import model_dialog, project, table_model


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
        #self.setFixedSize(32,32)
    

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
            print('dentro')
            self.show_menu()
        else:
            print('fora')



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
        ## Analysis toolbar menu actions
        actionPhaseError = QAction("Phase Error", self)
        actionRollOff = QAction("Roll Off", self)
        actionKickmap = QAction("Kickmap", self)
        actionTrajectory = QAction("Trajectory", self)
        actionMagneticField = QAction("Magnetic  Field", self)
        actionShimming = QAction("Shimming", self)
        actionCrossTalk = QAction("Cross Talk", self)
        actionFieldIntegral = QAction("Field Integral", self)


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
        ## Help
        self.menuHelp = self.menubar.addMenu("&Help")


        # tool bar
        self.toolbar = QToolBar("Barra de Ferramentas")
        self.addToolBar(self.toolbar)

        # button analysis as a ButtonMenu
        toolbar_buttonAnalysis = ButtonMenu("Analysis")
        self.toolbar.addWidget(toolbar_buttonAnalysis)
        toolbar_buttonAnalysis.custom_buttonMenu.addActions(([actionPhaseError,
                                                              actionRollOff,
                                                              actionKickmap,
                                                              actionTrajectory,
                                                              actionMagneticField,
                                                              actionShimming,
                                                              actionCrossTalk,
                                                              actionFieldIntegral]))
        self.toolbar.addSeparator()

        # nos painted buttons deve-se passar action para ele ser exibido como padrao
        # testar com exemplo do penguin

        toolbar_buttonPlot = PaintedButton("Plot")
        self.toolbar.addWidget(toolbar_buttonPlot)
        self.toolbar.addSeparator()
        self.toolbar_buttonTable = PaintedButton("Table")
        self.toolbar_buttonTable.setCheckable(True)
        #self.toolbar_buttonTable.clicked.connect(self.table_data)
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

    def model_generation(self):
        dialog = model_dialog.ModelDialog(parent=self)
        dialog.exec()
    
    def quit_app(self):
        self.app.quit()

    
    # tool bar slots


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
        #print(rect)
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
        #self.tree_item = item.text()
        if self.toolbar_buttonTable.isChecked():
            #print(item.text(0))
            if item.text(0)=='Dados 1':
                self.table_data()
    

    # outros metodos

    def mousePressEvent(self, event):
        
        #posicao do cursor do mouse nas coordenadas da window
        cursor_pos = QCursor.pos()
        widget_pos = self.mapFromGlobal(cursor_pos)
        print("Current cursor position at widget: x = %d, y = %d" % (widget_pos.x(), widget_pos.y()))

        return




# execution

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())