# padrao de nomeacao de variaveis #

# actions
## object name das actions: action<action_name>
## acessamos certa action com self.action<action_name>
## slots das actions: actionNewPressed


import time

t = time.time()
import os
import sys
#import getpass
dt = time.time()-t
print('imports menores =',dt*1000,'ms')

t = time.time()
from  PyQt6.QtWidgets import   (QApplication,
                                QMainWindow,
                                QStatusBar,
                                QFileDialog,
                                QMenuBar,
                                QMessageBox,
                                QDialog)
from   PyQt6.QtGui    import   (QAction,
                                QCursor)
from   PyQt6.QtCore   import    Qt
dt = time.time()-t
print('imports pyqt =',dt*1000,'ms')

t = time.time()
from widgets import analysis_dialog, model_dialog, projects, table_model, toolbar, canvas
from widgets.items import ExploreItem
dt = time.time()-t
print('imports widgets =',dt*1000,'ms')

t = time.time()
from imaids.insertiondevice import InsertionDeviceData
import imaids.models as models
dt = time.time()-t
print('imports imaids =',dt*1000,'ms')


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # -------------- construcao de tab widgets de projetos -------------- #

        # projects tab widget
        self.projects = projects.TabProjects(parent=self)
        self.projects.widget(0).tree.itemClicked.connect(self.on_item_clicked)
        self.projects.itemconnect.connect(
            lambda i: self.projects.widget(i).tree.itemClicked.connect(
                self.on_item_clicked
            )
        )

        # --------------------- construcao da status bar --------------------- #

        # status bar
        self.statusbar = QStatusBar()
        self.statusbar.setObjectName("Status Bar")


        # ---------------------- contrucao da tool bar ---------------------- #

        self.toolbar = toolbar.IMAIDsToolBar(title="Tool Bar",parent=self)
        

        # ------------------- construcao do main menu bar ------------------- #

        # main menu bar
        self.menubar = QMenuBar(parent=self)
        ## main menu bar - File menu
        self.menuFile = self.menubar.addMenu("&File")
        ### main menu bar - File menu - New Project action
        self.actionNew_Project = QAction("New Project", self)
        self.actionNew_Project.triggered.connect(self.projects.add_project)
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
        self.setCentralWidget(self.projects)

        self.setWindowTitle("IMAIDs Interface")
        self.resize(900,600)
        


    # SLOTS
    
    # window slots
    

    # menu slots

    # procurar dados e carregar enderecos dos seus arquivos
    def browse_for_data(self,s):
        #username = os.getlogin()
        #username = os.environ.get('USER', os.environ.get('USERNAME'))
        #username = getpass.getuser()
        #username = pwd.getpwuid(os.getuid())[0] (not tested)
        #print(username)

        userhome = os.path.expanduser('~')
        
        # filenames: file adress + file name of the selected data files
        filenames, _ =QFileDialog.getOpenFileNames(parent=self, 
                                                   caption='Open data',
                                                   directory=f"{userhome}\\Documents",
                                                   filter="Data files (*.txt *.dat *.csv)")

        if len(filenames):
            #print('ok button')
            self.check_files(filenames=filenames)
            #return True
        # else:
        #     print('cancel button')
        #     return False

    def check_files(self, filenames):

        # arquivos carregados novamente
        reloaded_files = []
        
        # iterando sobre cada endereco+nome dos arquivos da lista filenames
        for filename in filenames:
            if filename not in self.projects.currentWidget().filenames:
                
                # criando objeto insertion device
                ID = InsertionDeviceData(filename=filename)
                # colocando endereco do arquivo na lista de enderecos do respectivo project
                self.projects.currentWidget().filenames.append(filename)
                # inserindo texto do dado na arvore
                self.treeInsert(ID=ID, ID_type="Data")
            else:
                # guardando nome do arquivo ja carregado
                filename = os.path.basename(filename)
                reloaded_files.append(filename)
        
        # alertando sobre os arquivos ja carregados
        if len(reloaded_files):
            QMessageBox.warning(self,
                                "Files Warning",
                                f"Files already loaded! They are:\n{reloaded_files}")

    def model_generation(self):
        # todo: ter opcao de carregar arquivo com o conjunto de pontos para ter forma dos blocos
        dialog = model_dialog.ModelDialog(parent=self)
        answer = dialog.exec()
        
        if (answer == QDialog.DialogCode.Accepted) and (dialog.comboboxModels.currentText() != ''):
            #print('modelo ok')
            # valores usados nas spin boxes (parametros e posicoes dos cassetes)
            ID_name, kwargs_model, kwargs_cassettes = dialog.get_values()

            modelo_class = dialog.models_dict[dialog.comboboxModels.currentText()]
            
            ID = modelo_class(**kwargs_model)
            #*: polemico, ja que usa-se mesmo padrao de nome para dado e modelo
            #ID.name = ID_name
            ID.set_cassete_positions(**kwargs_cassettes)

            #ID.draw()

            # *: podera' criar modelos iguais uns aos outros, entao nao precisa checar se ja foi adicionado
            self.treeInsert(ID=ID,ID_type="Model", name=ID_name)
            return
        # elif answer == QDialog.DialogCode.Rejected:
        #     print('model cancel')
        #     return
    
    def treeInsert(self, ID, ID_type, name=''):

        id_num = {"Data": 0, "Model": 1}
        
        if ID_type=="Data":
            childs = self.projects.currentWidget().tree.topLevelItem(id_num[ID_type]).childCount()+1
            ID.name = f'{ID_type} {childs}'
        elif ID_type=="Model":
            models_names = [device.rstrip(device.split()[-1]).rstrip() 
                            for device in self.projects.currentWidget().insertiondevices]
            num = models_names.count(name)+1
            ID.name = f'{name} {num}'

        self.projects.currentWidget().insertiondevices[ID.name] = ID
        #todo: type deve ser diferente de modelo para dado
        self.projects.currentWidget().tree.topLevelItem(id_num[ID_type]).addChild(ExploreItem(ExploreItem.Type.ItemData,[ID.name]))
    
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
            self.toolbar.buttonAnalysis.apply.clicked.disconnect(self.toolbar.buttonAnalysis.aplicar)
            self.toolbar.buttonAnalysis.apply.clicked.connect(self.aplicar_AnalysisForAll)
        else:
            self.toolbar.buttonAnalysis.apply.clicked.disconnect(self.aplicar_AnalysisForAll)
            self.toolbar.buttonAnalysis.apply.clicked.connect(self.toolbar.buttonAnalysis.aplicar)

    def aplicar_AnalysisForAll(self):
        print('analysis button aplicar')
        #analysis_button2.AnalysisPushButton.aplicar()
        #self.buttonAnalysis.aplicar()

        self.toolbar.buttonAnalysis.Menu.setHidden(True)
        self.toolbar.buttonAnalysis.checkBoxSelectAll.setChecked(False)

        if self.actionApply.isChecked():
            #executar analises para todos
            for item in self.projects.currentWidget().tree.topLevelItem(0).children():
                # analise: trajetoria

                #todo: colocar condicao para calcular trajetoria so para os dados que ainda nao estao no dict de trajs
                self.calc_traj(item)
    

    ## edit slots

    def edit_analysis_parameters(self):
        dialog = analysis_dialog.AnalysisDialog(parent=self)
        answer = dialog.exec()
        if answer == QDialog.DialogCode.Accepted:
            print('edit ok')
    

    # tool bar slots

    def calc_traj(self, id_item: ExploreItem):

        id_name = id_item.text(0)
        num = id_name.split()[1]
        if id_name not in self.projects.currentWidget().insertiondevice_trajectories:

            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            traj = ExploreItem(ExploreItem.Type.ItemTrajectory, id_item, [f'Trajectory {num}'])
            traj.addChildren([ExploreItem(ExploreItem.Type.ItemResult, traj, ["x"]),
                              ExploreItem(ExploreItem.Type.ItemResult, traj, ["y"]),
                              ExploreItem(ExploreItem.Type.ItemResult, traj, ["z"]),
                              ExploreItem(ExploreItem.Type.ItemResult, traj, ["x'"]),
                              ExploreItem(ExploreItem.Type.ItemResult, traj, ["y'"]),
                              ExploreItem(ExploreItem.Type.ItemResult, traj, ["z'"])])
            
            #energy = 3 x0 = 0 y0 = 0 z0 = -900 dxds0 = 0 dyds0 = 0 dzds0 = 1 zmax = 900 rkstep = 0.5
            traj_imaids = id_meas.calc_trajectory(3,[0,0,-900,0,0,1],900,0.5)
            self.projects.currentWidget().insertiondevice_trajectories[id_name] = traj_imaids
            return
        else:
            QMessageBox.warning(self,
                                "Trajectories Warning",
                                f"Trajectories {num} already calculated!")
            return
    
    def plotar(self, id_item: ExploreItem):

        id_name = id_item.parent().text(0)
        traj_imaids = self.projects.currentWidget().insertiondevice_trajectories[id_name]

        # tracando grafico padrao
        chart = canvas.Grafico()
        chart.Plot(traj_imaids[:,2],traj_imaids[:,3])
        chart.plotStuff(title='Trajectory - Angular Deviation in x',
                        xlabel='z (mm)',
                        ylabel="x' (rad)")
        
        # colocando tabela no visuals
        i = self.projects.currentWidget().visuals.addTab(chart, f"Plot {id_name} - x' vs z")
        self.projects.currentWidget().visuals.setCurrentIndex(i)
    
    #todo: ampliar recursos da tabela
    def table_data(self, id_meas_item: ExploreItem):

        id_meas_name = id_meas_item.text(0)
        
        meas = self.projects.currentWidget().insertiondevices[id_meas_name]
        
        #contrucao da tabela
        tabela = table_model.Table(meas)
        
        # colocando tabela no visuals
        i = self.projects.currentWidget().visuals.addTab(tabela, f"Table {id_meas_name} - x, y, z, Bx, By, Bz")
        self.projects.currentWidget().visuals.setCurrentIndex(i)
    

    # tab bar slots


    # tree slots

    def on_item_clicked(self, item: ExploreItem, column):

        # analise: trajetoria
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemTrajectory.checkState() == Qt.CheckState.Checked and \
            item.item_type == ExploreItem.Type.ItemData:

            self.calc_traj(item)

        # plot
        if  self.toolbar.buttonPlot.isChecked() and \
            item.item_type == ExploreItem.Type.ItemTrajectory:
            
            self.plotar(item)
        
        # tabela
        if self.toolbar.buttonTable.isChecked() and \
            self.toolbar.buttonTable.objectName()==self.toolbar.actiontabela.objectName() and \
            item.item_type == ExploreItem.Type.ItemData:
            
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
