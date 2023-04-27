# padrao de nomeacao de variaveis #

# actions
## object name das actions: action<action_name>
## acessamos certa action com self.action<action_name>
## slots das actions: actionNewPressed


import sys
import os
import matplotlib
matplotlib.use('QtAgg')

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
                                QDialog,
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
                                QMessageBox,
                                QSpacerItem)
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

from widgets import analysis_dialog, model_dialog, project, table_model, analysis_button, painted_button

from imaids.insertiondevice import InsertionDeviceData

from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg,
                                                # matplotlib toolbar qt widget class
                                                NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


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


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

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
        #self.buttonAnalysis.signalTrajectory.connect(self.calc_traj)
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

        self.buttonPlot = painted_button.PaintedButton("Plot")
        self.buttonPlot.setIcon(grafico)
        self.buttonPlot.setCheckable(True)
        self.toolbar.addWidget(self.buttonPlot)
        self.toolbar.addSeparator()

        self.buttonTable = painted_button.PaintedButton("Table")
        self.buttonTable.setIcon(self.tabela)
        self.buttonTable.setObjectName(self.actiontabela.objectName())
        self.tabela = self.buttonTable.icon()
        self.buttonTable.setCheckable(True)

        self.actiontabela.triggered.connect(self.action_swap)
        self.actiondog.triggered.connect(self.action_swap)
        self.actioncat.triggered.connect(self.action_swap)
        self.actionbug.triggered.connect(self.action_swap)

        self.buttonTable.custom_buttonMenu.addActions([self.actiontabela,
                                                               self.actioncat,
                                                               self.actiondog,
                                                               self.actionbug])

        # self.toolbar_buttonTable.manager.connect(self.table_manager)
        self.toolbar.addWidget(self.buttonTable)
        

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
        ### main menu bar - Edit menu - Analysis action
        self.actionAnalysis = QAction("Analysis", self)
        self.actionAnalysis.triggered.connect(self.edit_analysis_parameters)
        self.menuEdit.addAction(self.actionAnalysis)
        self.menuEdit.addSeparator()
        '''### main menu bar - Edit menu - Undo action
        self.actionUndo = QAction("Undo", self)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addSeparator()
        ### main menu bar - Edit menu - Redo action
        self.actionRedo = QAction("Redo", self)
        self.menuEdit.addAction(self.actionRedo)'''
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
        self.setWindowTitle("IMAIDs Interface")
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
        
        #filenames, _ = QFileDialog.getOpenFileNames(self, 'Open data', r"C:\Users\juventino.fonseca\OneDrive - CNPEM - Centro Nacional de Pesquisa em Energia e Materiais\Meus arquivos dos codiguinhos\dados", "Data files (*.txt *.dat *.csv)")
        #filenames, _ = QFileDialog.getOpenFileNames(self, 'Open data', r"C:\Users", "Data files (*.txt *.dat *.csv)")
        #filenames, _ = QFileDialog.getOpenFileNames(self, 'Open data', r"%userprofile%\Documents", "Data files (*.txt *.dat *.csv)")
        username = os.getlogin()
        print(username)
        filenames, _ =QFileDialog.getOpenFileNames(self, 'Open data', f"C:\\Users\\{username}\\Documents", "Data files (*.txt *.dat *.csv)")

        #todo: melhorar condicao para algo como isempty; melhorar para pegar botao Ok ou Cancel
        # todo: detalhe: nao e' possivel sair do file dialog com Ok se nenhum arquivo for selecionado
        if filenames != []:
            print('ok')
            # haveria overload method para passar lista de objetos InsertionDeviceData
            self.treeInsertData(filenames)
            return True
        else:
            print('cancel')
            return False

        #index = self.projects.currentIndex()

    def treeInsertData(self, filenames):

        for filename in filenames:
            if filename not in self.projects.currentWidget().filenames.values():
                
                meas = InsertionDeviceData(filename=filename)
                Dados_childs = self.projects.currentWidget().tree.topLevelItem(0).childCount()+1
                meas.name = f'Dados {Dados_childs}'

                # todo: conferir se vou querer guardar name ou item ou objeto insertion device
                self.projects.currentWidget().insertiondevice_datas[meas.name] = meas
                # colocando filename na lista de filenames do respectivo project
                self.projects.currentWidget().filenames[meas.name] = filename
                self.projects.currentWidget().tree.topLevelItem(0).addChild(QTreeWidgetItem([meas.name]))
            else:
                # todo: colocar aqui para abrir message box informativo falando que ja carregou o dado
                print('arquivo ja carregado')

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

    
    ## edit slots

    def edit_analysis_parameters(self):
        dialog = analysis_dialog.AnalysisDialog(parent=self)
        dialog.exec()
    

    # tool bar slots

    def calc_traj(self, meas_item):
        # obter lista dos items checked
        #self.menuAnalysis.list.
        print('calcular trajetoria')
        #energy = 3 x0 = 0 y0 = 0 z0 = -900 dxds0 = 0 dyds0 = 0 dzds0 = 1 zmax = 900 rkstep = 0.5

        meas_name = meas_item.text(0)

        if meas_name not in self.projects.currentWidget().insertiondevice_trajectories:

            meas = self.projects.currentWidget().insertiondevice_datas[meas_name]

            num = meas_name.split()[1]

            traj = QTreeWidgetItem(meas_item, [f'Trajectory {num}'])
            #self.dados['Dados 1'].addChild(traj)
            #dados.addChild(traj)

            # se precisar usar os x, y, ... em outro lugar, fazer x = QTreeWidgetItem...
            #QTreeWidgetItem(traj, ["x"]) # x
            #QTreeWidgetItem(traj, ["y"]) # y
            #QTreeWidgetItem(traj, ["z"]) # z
            #QTreeWidgetItem(traj, ["x'"]) # dxds
            #QTreeWidgetItem(traj, ["y'"]) # dyds
            #QTreeWidgetItem(traj, ["z'"]) # dzds
            #traj.addChildren([x, y, z, dxds, dyds, dzds])
            traj.addChildren([QTreeWidgetItem(traj, ["x"]),
                            QTreeWidgetItem(traj, ["y"]),
                            QTreeWidgetItem(traj, ["z"]),
                            QTreeWidgetItem(traj, ["x'"]),
                            QTreeWidgetItem(traj, ["y'"]),
                            QTreeWidgetItem(traj, ["z'"])])
            
            #energy = 3 x0 = 0 y0 = 0 z0 = -900 dxds0 = 0 dyds0 = 0 dzds0 = 1 zmax = 900 rkstep = 0.5
            
            traj_imaids = meas.calc_trajectory(3,[0,0,-900,0,0,1],900,0.5)

            self.projects.currentWidget().insertiondevice_trajectories[meas_name] = traj_imaids

            return
        else:
            print('trajetoria ja calculada')
            return
    
    def plot(self,meas_item):

        meas_name = meas_item.parent().text(0)

        traj_imaids = self.projects.currentWidget().insertiondevice_trajectories[meas_name]

        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot(traj_imaids[:,2],traj_imaids[:,3])
        sc.axes.set_xlabel('z (mm)')
        sc.axes.set_ylabel("x' (rad)")
        sc.axes.set_title('Trajectory - Angular Deviation in x')

        plot_toolbar = NavigationToolbar(sc, self)

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(plot_toolbar)
        plot_layout.addWidget(sc)

        plot_widget = QWidget()
        plot_widget.setLayout(plot_layout)

        # colocando tabela no visuals
        i = self.projects.currentWidget().visuals.addTab(plot_widget, f"Plot {meas_name} - x' vs z")
        self.projects.currentWidget().visuals.setCurrentIndex(i)

        #plt.plot(traj_imaids[:,2], traj_imaids[:,3], label="x'")
        #plt.plot(traj_imaids[:,2], traj_imaids[:,4], label="y'")
        #plt.xlabel('z (mm)')
        #plt.ylabel("x',y' (rad)")
        #plt.legend()
        #plt.show()
    
    def action_swap(self):
        action = self.sender()
        self.buttonTable.setIcon(action.icon())
        self.buttonTable.setChecked(True)
        self.buttonTable.setObjectName(action.objectName())

    def table_data(self, meas_item):

        meas_name = meas_item.text(0)
        print(meas_name)

        meas = self.projects.currentWidget().insertiondevice_datas[meas_name]
        
        #contrucao da tabela
        tabela = QTableView()
        modeltable = table_model.TableModel(meas)
        tabela.setModel(modeltable)

        # todo: passar estilo para dentro do .py de modelo da tabela
        # estilo da tabela
        '''horizontal_color = QColor.fromRgb(80, 174, 144)
        vertical_color = QColor.fromRgb(136, 59, 144, int(0.8*255))
        horizontal_header_style = "QHeaderView::section {{background-color: {} }}".format(horizontal_color.name())
        vertical_header_style = "QHeaderView::section {{background-color: {} }}".format(vertical_color.name())
        tabela.horizontalHeader().setStyleSheet(horizontal_header_style)
        tabela.verticalHeader().setStyleSheet(vertical_header_style)'''

        #estilo meh
        horizontal_color = QColor.fromRgb(200, 200, 200)
        vertical_color = QColor.fromRgb(200, 200, 200)
        horizontal_header_style = "QHeaderView::section {{background-color: {} }}".format(horizontal_color.name())
        vertical_header_style = "QHeaderView::section {{background-color: {} }}".format(vertical_color.name())
        tabela.horizontalHeader().setStyleSheet(horizontal_header_style)
        tabela.verticalHeader().setStyleSheet(vertical_header_style)

        # colocando tabela no visuals
        i = self.projects.currentWidget().visuals.addTab(tabela, f"Table {meas_name} - x, y, z, Bx, By, Bz")
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

    #!: aqui sera gerenciado os clicks nos items, esquecer ideia de classe que recebe sinais de outras classes
    #!  e passa adiante
    def on_item_clicked(self, item, column):

        print('\n')
        print(self.buttonTable.isChecked())
        print(self.buttonTable.objectName()==self.actiontabela.objectName())
        print(item.parent())
    
        # plotar tabela
        if self.buttonTable.isChecked() and \
            self.buttonTable.objectName()==self.actiontabela.objectName() and \
            item.parent() == self.projects.currentWidget().tree.topLevelItem(0):
            
            self.table_data(item)
        
        #*: alterando analysis button.py para poder acessar facilmente os items abaixo
        #*  alem disso, possivelmente usando o object name deles, dai checando se estao
        #*  checked e entao levando ao respectivo metodo
        # calcular trajetoria
        if  self.buttonAnalysis.isChecked() and \
            self.buttonAnalysis.itemTrajectory.checkState() == Qt.CheckState.Checked and \
            item.parent() == self.projects.currentWidget().tree.topLevelItem(0):

            self.calc_traj(item)

        # todo: melhorar condicao, esta aceitando qualquer item que nao seja Data,
        # todo: ou seja, aceitando Models e outros, quando nao deveria
        if  self.buttonPlot.isChecked() and \
            item.parent().parent() == self.projects.currentWidget().tree.topLevelItem(0):
            
            print("vai plotar")
            
            self.plot(item)
    
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
