# padrao de nomeacao de variaveis #

# actions
## object name das actions: action<action_name>
## acessamos certa action com self.action<action_name>
## slots das actions: actionNewPressed


import time

t = time.time()
import os
import sys
import getpass
import matplotlib
matplotlib.use('QtAgg')
dt = time.time()-t
print('imports menores =',dt*1000,'ms')

t = time.time()
from  PyQt6.QtWidgets import   (QApplication,
                                QWidget,
                                QMainWindow,
                                QTabWidget,
                                QStatusBar,
                                QToolBar,
                                QToolButton,
                                QLineEdit,
                                QFileDialog,
                                QMenuBar,
                                QVBoxLayout,
                                QTreeWidgetItem,
                                QMessageBox)
from   PyQt6.QtGui    import   (QAction,
                                QIcon,
                                QCursor)
from   PyQt6.QtCore   import   Qt
dt = time.time()-t
print('imports pyqt =',dt*1000,'ms')

t = time.time()
from widgets import analysis_dialog, model_dialog, project, table_model, analysis_button, painted_button, items
dt = time.time()-t
print('imports widgets =',dt*1000,'ms')

t = time.time()
from imaids.insertiondevice import InsertionDeviceData
import imaids.models as models
dt = time.time()-t
print('imports imaids =',dt*1000,'ms')

t = time.time()
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg,
                                                # matplotlib toolbar qt widget class
                                                NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
dt = time.time()-t
print('imports matplotlib estranho =',dt*1000,'ms')


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

        self.toolbar = QToolBar("Tool Bar")

        grafico = QIcon("icons/icons/guide.png")
        self.tabela = QIcon("icons/icons/table.png")
        self.dog = QIcon("icons/icons/animal-dog.png")
        self.cat = QIcon("icons/icons/animal.png")
        self.bug = QIcon("icons/icons/bug.png")
        
        self.actiontabela = QAction(self.tabela,"tabela",self.toolbar)
        self.actiontabela.triggered.connect(self.action_swap)
        self.actiontabela.setObjectName("tabela")
        self.actiondog = QAction(self.dog,"cachorro",self.toolbar)
        self.actiondog.triggered.connect(self.action_swap)
        self.actiondog.setObjectName("dog")
        self.actioncat = QAction(self.cat,"gato",self.toolbar)
        self.actioncat.triggered.connect(self.action_swap)
        self.actioncat.setObjectName("cat")
        self.actionbug = QAction(self.bug,"inseto",self.toolbar)
        self.actionbug.triggered.connect(self.action_swap)
        self.actionbug.setObjectName("bug")

        # tool bar
        self.toolbar.setObjectName("Tool Bar")
        ## tool bar - analysis button: executar analise de dados
        self.buttonAnalysis = analysis_button.AnalysisPushButton(menu_parent=self,
                                                                 button_text="Analysis",
                                                                 button_parent=self.toolbar)
        #self.buttonAnalysis.apply.clicked.connect(self.aplicar_AnalysisForAll)
        self.toolbar.addWidget(self.buttonAnalysis)
        self.toolbar.addSeparator()
        ## tool bar - plot button: fazer graficos dos dados
        self.buttonPlot = painted_button.PaintedButton("Plot")
        self.buttonPlot.setIcon(grafico)
        self.toolbar.addWidget(self.buttonPlot)
        self.toolbar.addSeparator()
        ## tool bar - table button: fazer tabelas dos dados
        self.buttonTable = painted_button.PaintedButton("Table")
        self.buttonTable.setIcon(self.tabela)
        self.buttonTable.setObjectName(self.actiontabela.objectName())
        self.tabela = self.buttonTable.icon()
        self.buttonTable.custom_buttonMenu.addActions([self.actiontabela,
                                                               self.actioncat,
                                                               self.actiondog,
                                                               self.actionbug])
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
        ### main menu bar - Settings menu - Apply action
        self.actionApply = QAction("Apply for All", self, checkable=True)
        self.actionApply.triggered.connect(self.enable_AnalysisForAll)
        self.menuSettings.addAction(self.actionApply)
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
        
        #username = os.getlogin()
        username = getpass.getuser()
        print(username)
        filenames, _ =QFileDialog.getOpenFileNames(self, 'Open data', f"C:\\Users\\{username}\\Documents", "Data files (*.txt *.dat *.csv)")

        #todo: melhorar condicao para algo como isempty; melhorar para pegar botao Ok ou Cancel
        # todo: detalhe: nao e' possivel sair do file dialog com Ok se nenhum arquivo for selecionado
        if len(filenames): #condicao equivalente a: filenames != []
            print('ok button')
            # haveria overload method para passar lista de objetos InsertionDeviceData
            self.treeInsertData(filenames)
            return True
        else:
            print('cancel button')
            return False

    def treeInsertData(self, filenames: list):

        reloaded = []
        
        for filename in filenames:
            #print(filename)
            if filename not in self.projects.currentWidget().filenames.values():
                id_meas = InsertionDeviceData(filename=filename)
                Dados_childs = self.projects.currentWidget().tree.topLevelItem(0).childCount()+1
                id_meas.name = f'Dados {Dados_childs}'
                # ?: guardar informacoes em dict acessado pelo nome do dado e' a melhor opcao
                self.projects.currentWidget().insertiondevice_datas[id_meas.name] = id_meas
                # colocando filename no dicionario de filenames do respectivo project
                self.projects.currentWidget().filenames[id_meas.name] = filename
                self.projects.currentWidget().tree.topLevelItem(0).addChild(items.ExploreItem(items.Items.DataItem,[id_meas.name]))
            else:
                reloaded.append(os.path.basename(filename))
        
        #print(reloaded)
        if len(reloaded):
            QMessageBox.warning(self,
                                "Files Warning",
                                f"Files already loaded! They are:\n{reloaded}")

    def model_generation(self):
        # todo: deve-se poder saber qual classe de modelos foi selecionada (Delta, AppleX, AppleII, APU ou Planar),
        # todo: bem como o modelo especifico selecionado. na classe, há metodos especificos para definir as posições
        # todo: dos cassetes, por isso passar a classe.

        # todo: saber os valores usados nas spin boxes

        # todo: ter opcao de carregar arquivo com o conjunto de pontos para ter forma dos blocos
        dialog = model_dialog.ModelDialog(parent=self)
        button = dialog.exec()
        #print(button)
        if button==1 and dialog.models.currentText() != '':   #todo: descobrir de onde vem cada numero
            print('modelo ok')
            kwargs_model, kwargs_cassettes = dialog.get_values() ## passar kwargs pra criacao de modelo


            models_dict = {}
            for name in dir(models):
                obj = getattr(models, name)
                if isinstance(obj, type):
                    models_dict[name] = obj

            modelo_class = models_dict[dialog.objectName()]

            id_model = modelo_class(**kwargs_model)
            Modelos_childs = self.projects.currentWidget().tree.topLevelItem(1).childCount()+1
            id_model.name = f'Data {Modelos_childs}'

            self.projects.currentWidget().insertiondevice_models[id_model.name] = id_model
            
            # *: podera' criar modelos iguais uns aos outros, entao nao precisa checar se ja foi adicionado
            self.treeInsertModel(dialog.objectName())
            return
        #elif button==0:
        #    print('model cancel')
    
    def treeInsertModel(self, id_model_name: str):
        self.projects.currentWidget().tree.topLevelItem(1).addChild(items.ExploreItem(items.Items.ModelItem,[id_model_name]))
    
    def quit_app(self):
        answer = QMessageBox.question(self,
                                      "Quit Question",
                                      "Are you sure you want to quit the application?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)

        if answer == QMessageBox.StandardButton.Yes:
            self.app.quit()

    def enable_AnalysisForAll(self,checked):
        print('checked',checked)
        if checked:
            self.buttonAnalysis.apply.clicked.disconnect(self.buttonAnalysis.aplicar)
            self.buttonAnalysis.apply.clicked.connect(self.aplicar_AnalysisForAll)
        else:
            self.buttonAnalysis.apply.clicked.disconnect(self.aplicar_AnalysisForAll)
            self.buttonAnalysis.apply.clicked.connect(self.buttonAnalysis.aplicar)

    def aplicar_AnalysisForAll(self):
        print('analysis button aplicar')
        #analysis_button2.AnalysisPushButton.aplicar()
        #self.buttonAnalysis.aplicar()

        self.buttonAnalysis.Menu.setHidden(True)
        self.buttonAnalysis.checkBoxSelectAll.setChecked(False)

        if self.actionApply.isChecked():
            #executar analises para todos
            for item in self.projects.currentWidget().tree.topLevelItem(0).children():
                # analise: trajetoria

                #todo: colocar condicao para calcular trajetoria so para os dados que ainda nao estao no dict de trajs
                self.calc_traj(item)
    

    ## edit slots

    def edit_analysis_parameters(self):
        dialog = analysis_dialog.AnalysisDialog(parent=self)
        button = dialog.exec()
        if button==1:   #todo: descobrir de onde vem cada numero
            print('edit ok')
    

    # tool bar slots

    def calc_traj(self, id_meas_item: items.ExploreItem):

        id_meas_name = id_meas_item.text(0)
        num = id_meas_name.split()[1]
        if id_meas_name not in self.projects.currentWidget().insertiondevice_trajectories:

            id_meas = self.projects.currentWidget().insertiondevice_datas[id_meas_name]

            traj = items.ExploreItem(items.Items.TrajectoryItem, id_meas_item, [f'Trajectory {num}'])
            traj.addChildren([QTreeWidgetItem(traj, ["x"]),
                            QTreeWidgetItem(traj, ["y"]),
                            QTreeWidgetItem(traj, ["z"]),
                            QTreeWidgetItem(traj, ["x'"]),
                            QTreeWidgetItem(traj, ["y'"]),
                            QTreeWidgetItem(traj, ["z'"])])
            
            #energy = 3 x0 = 0 y0 = 0 z0 = -900 dxds0 = 0 dyds0 = 0 dzds0 = 1 zmax = 900 rkstep = 0.5
            traj_imaids = id_meas.calc_trajectory(3,[0,0,-900,0,0,1],900,0.5)
            self.projects.currentWidget().insertiondevice_trajectories[id_meas_name] = traj_imaids
            return
        else:
            QMessageBox.warning(self,
                                "Trajectories Warning",
                                f"Trajectories {num} already calculated!")
            return
    
    def plot(self, id_meas_item: items.ExploreItem):

        id_meas_name = id_meas_item.parent().text(0)
        traj_imaids = self.projects.currentWidget().insertiondevice_trajectories[id_meas_name]

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
        i = self.projects.currentWidget().visuals.addTab(plot_widget, f"Plot {id_meas_name} - x' vs z")
        self.projects.currentWidget().visuals.setCurrentIndex(i)
    
    def action_swap(self):
        action = self.sender()
        self.buttonTable.setIcon(action.icon())
        self.buttonTable.setChecked(True)
        self.buttonTable.setObjectName(action.objectName())

    def table_data(self, id_meas_item: items.ExploreItem):

        id_meas_name = id_meas_item.text(0)
        print(id_meas_name)

        meas = self.projects.currentWidget().insertiondevice_datas[id_meas_name]
        
        #contrucao da tabela
        tabela = table_model.Table(meas)
        
        # colocando tabela no visuals
        i = self.projects.currentWidget().visuals.addTab(tabela, f"Table {id_meas_name} - x, y, z, Bx, By, Bz")
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
        # todo: corrigir como coloca-se y
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

    def on_item_clicked(self, item: items.ExploreItem, column):

        # analise: trajetoria
        if  self.buttonAnalysis.isChecked() and \
            self.buttonAnalysis.itemTrajectory.checkState() == Qt.CheckState.Checked and \
            item.item_type == items.Items.DataItem:

            self.calc_traj(item)

        # plot
        if  self.buttonPlot.isChecked() and \
            item.item_type == items.Items.TrajectoryItem:
            
            self.plot(item)
        
        # tabela
        if self.buttonTable.isChecked() and \
            self.buttonTable.objectName()==self.actiontabela.objectName() and \
            item.item_type == items.Items.DataItem:
            
            self.table_data(item)
    
    
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
