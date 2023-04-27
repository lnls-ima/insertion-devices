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
                                QMenuBar,
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

from widgets import model_dialog, project, table_model, analysis_button, painted_button

from imaids import fieldsource, insertiondevice


'''
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
'''

'''
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
'''


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # atributo filename
        # atributo que vai guardar filename quando carregarmos os dados e
        # sera chamado quando for criar a tabela de dados
        self.filename = {}
        self.dados = {}


        # -------------- construcao de tab widgets de projetos -------------- #

        # projects tab widget
        self.projects = QTabWidget()
        ## projects tab widget - features
        self.projects.setDocumentMode(True) # talvez possa ser desabilitado
        self.projects.setMovable(True)
        ## projects tab widget - signals
        self.projects.tabCloseRequested.connect(self.close_current_tab)
        self.projects.tabBarDoubleClicked.connect(self.start_rename)
        ## projects tab widget - tab inicial
        self.projects.addTab(project.ProjectWidget(),'Project')
        self.projects.widget(0).tree.itemClicked.connect(self.on_item_clicked)
        #print(self.projects.currentWidget().tree)
        ## projects tab widget - plus button: abrir mais uma aba de projeto
        self.PlusButton = QToolButton()
        self.PlusButton.setText("+")
        self.PlusButton.clicked.connect(self.add_project)
        self.projects.setCornerWidget(self.PlusButton,corner=Qt.Corner.TopLeftCorner)


        # --------------------- construcao da status bar --------------------- #

        self.statusbar = QStatusBar()
        self.statusbar.setObjectName("Barra de Status")


        # ---------------------- contrucao da tool bar ---------------------- #

        # tool bar
        self.toolbar = QToolBar("Barra de Ferramentas")
        self.toolbar.setObjectName("Barra de Ferramentas")
    
        ## button analysis
        self.buttonAnalysis = analysis_button.AnalysisPushButton(menu_parent=self,
                                                                 button_text="Analysis",
                                                                 button_parent=self.toolbar)
        #self.buttonAnalysis.apply.clicked.connect(self.manage_analysis)
        self.buttonAnalysis.signalTrajectory.connect(self.calc_traj)
        self.toolbar.addWidget(self.buttonAnalysis)
        self.toolbar.addSeparator()

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

        self.toolbar_buttonPlot = painted_button.PaintedButton("Plot")
        self.toolbar_buttonPlot.setIcon(grafico)
        self.toolbar_buttonPlot.setCheckable(True)
        self.toolbar.addWidget(self.toolbar_buttonPlot)
        self.toolbar.addSeparator()

        self.toolbar_buttonTable = painted_button.PaintedButton("Table")
        self.toolbar_buttonTable.setIcon(self.tabela)
        self.toolbar_buttonTable.setObjectName(self.actiontabela.objectName())
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
        

        # ------------------- construcao do main menu bar ------------------- #

        # main menu bar
        self.menubar = QMenuBar(parent=self)   #self.menuBar()
        ## main menu bar - File menu
        self.menuFile = self.menubar.addMenu("&File")
        ### main menu bar - File menu - New Project action
        self.actionNew_Project = QAction("New Project", self)
        self.actionNew_Project.triggered.connect(self.add_project)
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addSeparator()
        ### main menu bar - File menu - Open Data action
        self.actionOpen_Data = QAction("Open Data ...", self)
        self.actionOpen_Data.triggered.connect(self.browse_for_data)
        self.menuFile.addAction(self.actionOpen_Data)
        self.menuFile.addSeparator()
        ### main menu bar - File menu - Generate Model action
        self.actionGenerate_Model = QAction("Generate Model", self)
        self.actionGenerate_Model.triggered.connect(self.model_generation)
        self.menuFile.addAction(self.actionGenerate_Model)
        self.menuFile.addSeparator()
        ### main menu bar - File menu - Quit action
        self.actionQuit = QAction("Quit", self)
        self.actionQuit.triggered.connect(self.quit_app)
        self.menuFile.addAction(self.actionQuit)
        ## main menu bar - Edit menu
        self.menuEdit = self.menubar.addMenu("&Edit")
        ### main menu bar - Edit menu - Undo action
        self.actionUndo = QAction("Undo", self)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addSeparator()
        ### main menu bar - Edit menu - Redo action
        self.actionRedo = QAction("Redo", self)
        self.menuEdit.addAction(self.actionRedo)
        ## main menu bar - View menu: contem opcoes de esconder widgets, tais como toolbar
        self.menuView = self.menubar.addMenu("&View")
        ### main menu bar - View menu - ToolBar action
        actionToolBar = QAction(self.toolbar.objectName(), self, checkable=True)
        actionToolBar.setChecked(True)
        actionToolBar.triggered.connect(self.toolbar.setVisible)
        self.menuView.addAction(actionToolBar)
        ### main menu bar - View menu - StatusBar action
        actionStatusBar = QAction(self.statusbar.objectName(), self, checkable=True)
        actionStatusBar.setChecked(True)
        actionStatusBar.triggered.connect(self.statusbar.setVisible)
        self.menuView.addAction(actionStatusBar)
        ## main menu bar - Settings menu
        self.menuSettings = self.menubar.addMenu("&Settings")
        ## main menu bar - Help menu: documentacao da interface
        self.menuHelp = self.menubar.addMenu("&Help")


        # --------------------- contrucao da main window --------------------- #

        self.app = app
        self.setStatusBar(self.statusbar)
        self.addToolBar(self.toolbar)
        self.setMenuBar(self.menubar)
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
        self.projects.widget(i).tree.itemClicked.connect(self.on_item_clicked)

    def browse_for_data(self,s):
        filenames, _ =QFileDialog.getOpenFileNames(self, 'Open data', '', 'Data (*.dat)')

        number_of_files = len(filenames)
        
        #pegar indice do project atual e acessar tree do project atual
        #por fim, na tree atual, inserir Dados 1
        
        #melhorar condicao para algo como isempty
        if filenames != []:
            self.treeInsertData(number_of_files)
            for index in range(number_of_files):
                self.filename[f'Dados {index+1}'] = filenames[index]
            return True
        else:
            #print('else')
            return False

        #index = self.projects.currentIndex()

    def treeInsertData(self, number_of_files):

        print(number_of_files)

        # tree.topLevelItemCount() retorna o numero de items mais externos
        # se nao ha, retorna 0, que e' equivalente a False
        # not False e' True e entra na condicao quando nao ha toplevel items
        
        dados_childs = self.projects.currentWidget().tree.topLevelItem(0).childCount()+1
        print(dados_childs)  # -> 1
        for index in range(number_of_files):
            print('iteracao',index,f'Dados {dados_childs+index}')
            novo_dado = QTreeWidgetItem([f'Dados {dados_childs+index}'])
            self.dados[f'Dados {dados_childs+index}'] = novo_dado
            self.projects.currentWidget().tree.topLevelItem(0).addChild(novo_dado)
        
        print(self.dados)
        # ?: conferir qual a utilidade de self.dados

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

    def calc_traj(self):
        # obter lista dos items checked
        #self.menuAnalysis.list.
        print('calcular trajetoria')
        energy = 3
        x0 = 0
        y0 = 0
        z0 = -900
        dxds0 = 0
        dyds0 = 0
        dzds0 = 1
        zmax = 900
        rkstep = 0.5

        traj = QTreeWidgetItem(['Trajectory 1'])
        self.dados['Dados 1'].addChild(traj)

        x = QTreeWidgetItem(['x'])
        y = QTreeWidgetItem(['y'])
        z = QTreeWidgetItem(['z'])
        dxds = QTreeWidgetItem(["x'"])
        dyds = QTreeWidgetItem(["y'"])
        dzds = QTreeWidgetItem(["z'"])
        traj.addChild(x)
        traj.addChild(y)
        traj.addChild(z)
        traj.addChild(dxds)
        traj.addChild(dyds)
        traj.addChild(dzds)
        return
    
    def action_swap(self):
        action = self.sender()
        self.toolbar_buttonTable.setIcon(action.icon())
        self.toolbar_buttonTable.setChecked(True)
        self.toolbar_buttonTable.setObjectName(action.objectName())

    def table_data(self,filename):
        
        # todo: passar essa condicao para outro lugar e torna-la mais geral
        if self.projects.currentWidget().visuals.count() == 1:
            self.projects.currentWidget().visuals.setTabsClosable(True)
        
        tabela = QTableView()
        modelo = table_model.TableModel(filename)
        tabela.setModel(modelo)

        horizontal_color = QColor.fromRgb(80, 174, 144)
        vertical_color = QColor.fromRgb(136, 59, 144, int(0.8*255))
        horizontal_header_style = "QHeaderView::section {{background-color: {} }}".format(horizontal_color.name())
        vertical_header_style = "QHeaderView::section {{background-color: {} }}".format(vertical_color.name())
        tabela.horizontalHeader().setStyleSheet(horizontal_header_style)
        tabela.verticalHeader().setStyleSheet(vertical_header_style)

        i = self.projects.currentWidget().visuals.addTab(tabela, "tabela")
        self.projects.currentWidget().visuals.setCurrentIndex(i)
    

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

        #print('button is checked',self.toolbar_buttonTable.isChecked())
        #print('button object name',self.toolbar_buttonTable.objectName())
        #print('action tabela object name',self.actiontabela.objectName())
        
        # plotar tabela
        if self.toolbar_buttonTable.isChecked() and \
            self.toolbar_buttonTable.objectName()==self.actiontabela.objectName():
            
            print(item.text(0))
            #print(self.dados.keys())
            print('keys',self.filename.keys(),'\n')
            print('values',self.filename.values())
            if item.text(0) in self.dados.keys():
                filename = self.filename[item.text(0)]
                self.table_data(filename)
    
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
