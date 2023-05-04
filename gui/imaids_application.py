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
import numpy as np
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
dt = time.time()-t
print('import InsertionDeviceData =',dt*1000,'ms')


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.energy = 3
        self.x0, self.y0, self.z0 = 0, 0, -900
        self.dxds0, self.dyds0, self.dzds0 = 0, 0, 1
        self.zmax = 900
        self.rkstep = 0.5
        self.skip_poles = 4
        self.Z = np.arange(-900,900,0.5)
        self.X = np.linspace(-5, 5, 23)

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
        self.resize(1200,700)
        


    # SLOTS
    
    # window slots
    

    # menu slots

    # procurar dados e carregar enderecos dos seus arquivos
    def browse_for_data(self,s):
        
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
                #!: no momento so' esta' sendo possivel carregar dados de Delta Sabia
                #todo: criar janela de dialog intermediaria antes de carregar os arquivos onde
                #todo: sera feita a renomeacao e passagem dos parametros/selecao do modelo de
                #todo: ondulador que os dados seguem. havera tambem checkbox para escolher criar
                #todo: modelo relativo aos dados ou nao
                
                ID = InsertionDeviceData(nr_periods=21, period_length=52.5,filename=filename)
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
    
    #todo: maneira de passar children em vez de chamar esse metodo para todo arquivo e passar child
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
        data = ExploreItem(ExploreItem.Type.ItemData,[ID.name, "Table"])
        data.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        self.projects.currentWidget().tree.topLevelItem(id_num[ID_type]).addChild(data)
    
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
        print('aplicar para todos')

        self.toolbar.buttonAnalysis.Menu.setHidden(True)
        
        if self.actionApply.isChecked():
            #executar analises para todos
            for item in self.projects.currentWidget().tree.topLevelItem(0).children():
                
                #todo: colocar condicao para calcular trajetoria so para os dados que ainda nao estao no dict de trajs
                #todo: maneira mais geral de executar todas as analises selecionadas
                if self.toolbar.buttonAnalysis.itemCrossTalk.checkState() == Qt.CheckState.Checked:
                    self.calcCrossTalk(item)
                if self.toolbar.buttonAnalysis.itemMagneticField.checkState() == Qt.CheckState.Checked:
                    self.calcMagneticField(item)
                if self.toolbar.buttonAnalysis.itemTrajectory.checkState() == Qt.CheckState.Checked:
                    self.calcTrajectory(item)
                if self.toolbar.buttonAnalysis.itemPhaseError.checkState() == Qt.CheckState.Checked:
                    self.calcPhaseError(item)
                if self.toolbar.buttonAnalysis.itemIntegrals.checkState() == Qt.CheckState.Checked:
                    self.calcIntegrals(item)
                if self.toolbar.buttonAnalysis.itemRollOffPeaks.checkState() == Qt.CheckState.Checked:
                    self.calcRollOffPeaks(item)
                if self.toolbar.buttonAnalysis.itemRollOffAmp.checkState() == Qt.CheckState.Checked:
                    self.calcRollOffAmp(item)
        #else: aplicar normal
        
        self.toolbar.buttonAnalysis.checkBoxSelectAll.setChecked(False)
        [item.setCheckState(Qt.CheckState.Unchecked) for item in self.toolbar.buttonAnalysis.checkedItems()]
    

    ## edit slots

    def edit_analysis_parameters(self):
        dialog = analysis_dialog.AnalysisDialog(parent=self)
        answer = dialog.exec()
        if answer == QDialog.DialogCode.Accepted:
            print('edit ok')
    

    # tool bar slots

    def calcMagneticField(self, id_item: ExploreItem):

        id_name = id_item.text(0)

        if id_name not in self.projects.currentWidget().fields:

            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            result = id_meas.get_field(x=0, y=0, z=self.Z, nproc=None, chunksize=100)
            self.projects.currentWidget().fields[id_name] = result

            num = id_name.split()[1]
            field = ExploreItem(ExploreItem.Type.ItemMagneticField, id_item, [f"Magnetic Field {num}", "Analysis"])
            field.setTextAlignment(1,Qt.AlignmentFlag.AlignRight)
            children = [ExploreItem(ExploreItem.Type.ItemResult, field, ["Bx", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, field, ["By", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, field, ["Bz", "List"])]
            [item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight) for item in children]
            field.addChildren(children)
            return
        else:
            QMessageBox.warning(self,
                                "Field Warning",
                                f"Magnetic Field of {id_name} already calculated!")
            return

    def calcTrajectory(self, id_item: ExploreItem):

        id_name = id_item.text(0)
        
        if id_name not in self.projects.currentWidget().trajectories:

            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            #energy = 3 x0 = 0 y0 = 0 z0 = -900 dxds0 = 0 dyds0 = 0 dzds0 = 1 zmax = 900 rkstep = 0.5
            result = id_meas.calc_trajectory(self.energy,[self.x0,self.y0,self.z0,self.dxds0,self.dyds0,self.dzds0],self.zmax,self.rkstep, dz=0, on_axis_field=False)
            self.projects.currentWidget().trajectories[id_name] = result

            num = id_name.split()[1]
            traj = ExploreItem(ExploreItem.Type.ItemTrajectory, id_item, [f"Trajectory {num}", "Analysis"])
            traj.setTextAlignment(1,Qt.AlignmentFlag.AlignRight)
            children = [ExploreItem(ExploreItem.Type.ItemResult, traj, ["x", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, traj, ["y", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, traj, ["z", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, traj, ["x'", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, traj, ["y'", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, traj, ["z'", "List"])]
            [item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight) for item in children]
            traj.addChildren(children)
            return
        else:
            QMessageBox.warning(self,
                                "Trajectory Warning",
                                f"Trajectory of {id_name} already calculated!")
            return
    
    def calcPhaseError(self, id_item: ExploreItem):
        
        id_name = id_item.text(0)
        
        if id_name not in self.projects.currentWidget().phaserr:
        
            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            traj = self.projects.currentWidget().trajectories[id_name]
            bxamp, byamp, _, _ = id_meas.calc_field_amplitude()
            kh, kv = id_meas.calc_deflection_parameter(bxamp, byamp)
            z_list, pe, pe_rms = id_meas.calc_phase_error(self.energy, traj, bxamp, byamp, self.skip_poles, zmin=None, zmax=None, field_comp=None)
            self.projects.currentWidget().phaserr[id_name] = [z_list, pe, pe_rms]

            num = id_name.split()[1]
            phaserr = ExploreItem(ExploreItem.Type.ItemPhaseError, id_item, [f"Phase Error {num}","Analysis"])
            phaserr.setTextAlignment(1,Qt.AlignmentFlag.AlignRight)
            children = [ExploreItem(ExploreItem.Type.ItemResult, phaserr, ["z poles", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, phaserr, ["PhaseErr", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, phaserr, ["RMS [rad]", f"{pe_rms:.1f}"]),
                        ExploreItem(ExploreItem.Type.ItemResult, phaserr, ["Bx Amp [T]", f"{bxamp:.1f}"]),
                        ExploreItem(ExploreItem.Type.ItemResult, phaserr, ["By Amp [T]", f"{byamp:.1f}"]),
                        ExploreItem(ExploreItem.Type.ItemResult, phaserr, ["Kh [T.mm]", f"{kh:.1f}"]),
                        ExploreItem(ExploreItem.Type.ItemResult, phaserr, ["Kv [T.mm]", f"{kv:.1f}"])]
            [item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight) for item in children]
            phaserr.addChildren(children)
            return
        else:
            QMessageBox.warning(self,
                                "Phase Error Warning",
                                f"Phase Error of {id_name} already calculated!")
            return
    
    def calcIntegrals(self, id_item: ExploreItem):
        
        id_name = id_item.text(0)
        
        if id_name not in self.projects.currentWidget().integrals:
        
            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            B = self.projects.currentWidget().fields[id_name]
            ib, iib = id_meas.calc_field_integrals(z_list=self.Z, x=0, y=0, field_list=B, nproc=None, chunksize=100)
            self.projects.currentWidget().integrals[id_name] = [ib, iib]
            ibx, iby, ibz = ib.T
            iibx, iiby, iibz = iib.T

            num = id_name.split()[1]
            integrals = ExploreItem(ExploreItem.Type.ItemIntegrals, id_item, [f'Field Integrals {num}', "Analysis"])
            integrals.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
            children = [ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IBx',  "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IBy',  "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IBz',  "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IIBx', "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IIBy', "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IIBz', "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IBx T  [G.cm]',   f"{ibx[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IBy T  [G.cm]',   f"{iby[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IBz T  [G.cm]',   f"{ibz[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IIBx T [kG.cm2]', f"{iibx[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IIBy T [kG.cm2]', f"{iiby[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.Type.ItemResult, integrals, ['IIBz T [kG.cm2]', f"{iibz[-1]:7.1f}"])]
            [item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight) for item in children]
            integrals.addChildren(children)
            return
        else:
            QMessageBox.warning(self,
                                "Integrals Warning",
                                f"Field Integrals of {id_name} already calculated!")
            return
    
    def calcRollOffPeaks(self, id_item: ExploreItem):

        id_name = id_item.text(0)
        
        if id_name not in self.projects.currentWidget().rolloffpeaks:
        
            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            result = id_meas.calc_roll_off_peaks(z=self.Z,x=self.X,y=0,field_comp=None)
            self.projects.currentWidget().rolloffpeaks[id_name] = result

            num = id_name.split()[1]
            rollffp = ExploreItem(ExploreItem.Type.ItemRollOffPeaks, id_item, [f'Roll Off Peaks {num}', "Analysis"])
            rollffp.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
            children = [ExploreItem(ExploreItem.Type.ItemResult, rollffp, ['ROPx',  "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, rollffp, ['ROPy',  "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, rollffp, ['ROPz',  "List"])]
            [item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight) for item in children]
            rollffp.addChildren(children)
            return
        else:
            QMessageBox.warning(self,
                                "Roll Off Warning",
                                f"Roll Off Peaks of {id_name} already calculated!")
            return
    
    def calcRollOffAmp(self, id_item: ExploreItem):

        id_name = id_item.text(0)
        
        if id_name not in self.projects.currentWidget().rolloffamp:
        
            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            result = id_meas.calc_roll_off_amplitude(z=self.Z,x=self.X,y=0)
            self.projects.currentWidget().rolloffamp[id_name] = result

            num = id_name.split()[1]
            rollffa = ExploreItem(ExploreItem.Type.ItemRollOffAmp, id_item, [f'Roll Off Amplitude {num}', "Analysis"])
            rollffa.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
            children = [ExploreItem(ExploreItem.Type.ItemResult, rollffa, ['ROAx',  "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, rollffa, ['ROAy',  "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, rollffa, ['ROAz',  "List"])]
            [item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight) for item in children]
            rollffa.addChildren(children)
            return
        else:
            QMessageBox.warning(self,
                                "Roll Off Warning",
                                f"Roll Off Amplitude of {id_name} already calculated!")
            return
    
    def calcCrossTalk(self, id_item: ExploreItem):
        
        id_name = id_item.text(0)
        if id_name[-1] != 'C':
            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            id_meas.correct_angles(angxy=0.15, angxz=-0.21, angyx=-0.01,
                                angyz=-0.02, angzx=0.01, angzy=-0.74)
            id_meas.correct_cross_talk(ky=[-0.006781104386361973,
                                           -0.01675247563602003,
                                            7.568631573320983e-06],
                                       kz=[-0.006170829583118335,
                                           -0.016051627320478382,
                                            7.886674928668737e-06])
            
            id_new_name = id_name+' C'
            id_item.setText(0,id_new_name)
            self.update_dicts_key(key=id_name, new_key=id_new_name)
            return
        else:
            QMessageBox.warning(self,
                                "Cross Talk Warning",
                                f"Cross Talk of {id_name} already calculated!")
            return

    def update_dicts_key(self,key,new_key):
        dicts =[self.projects.currentWidget().insertiondevices,
                self.projects.currentWidget().fields,
                self.projects.currentWidget().trajectories,
                self.projects.currentWidget().phaserr,
                self.projects.currentWidget().integrals]
        
        for dirc in dicts:
            if key in dirc:
                value = dirc.pop(key)
                dirc[new_key] = value
    
    def plotar(self, id_item: ExploreItem):

        id_name = id_item.parent().text(0)

        # tracando grafico padrao
        chart = canvas.Grafico()

        if id_item.item_type is ExploreItem.Type.ItemTrajectory:
            traj = self.projects.currentWidget().trajectories[id_name]
            chart.Plot(traj[:,2],traj[:,3])
            chart.plotStuff(title='Trajectory - Angular Deviation in x',
                            xlabel='z (mm)',
                            ylabel="x' (rad)")
            
        if id_item.item_type is ExploreItem.Type.ItemPhaseError:
            z_poles, pe, perms = self.projects.currentWidget().phaserr[id_name]
            chart.Plot(np.arange(1,len(pe)+1), pe*180/np.pi)
            #ax.plot(,,'.-')
            chart.plotStuff(title='Phase Error',
                            xlabel='Pole',
                            ylabel='Phase Error (°)')
        
        # colocando grafico no visuals
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

        # analise: campo magnetico
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemMagneticField.checkState() == Qt.CheckState.Checked and \
            item.item_type is ExploreItem.Type.ItemData:

            self.calcMagneticField(item)
        
        # analise: trajetoria
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemTrajectory.checkState() == Qt.CheckState.Checked and \
            item.item_type is ExploreItem.Type.ItemData:

            self.calcTrajectory(item)
        
        # analise: erro de fase
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemPhaseError.checkState() == Qt.CheckState.Checked and \
            item.item_type is ExploreItem.Type.ItemData:
            
            self.calcPhaseError(item)

        # analise: integrais de campo
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemIntegrals.checkState() == Qt.CheckState.Checked and \
            item.item_type is ExploreItem.Type.ItemData:
            
            self.calcIntegrals(item)

        # analise: roll off peaks
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemRollOffPeaks.checkState() == Qt.CheckState.Checked and \
            item.item_type is ExploreItem.Type.ItemData:

            self.calcRollOffPeaks(item)
        
        # analise: roll off amplitude
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemRollOffAmp.checkState() == Qt.CheckState.Checked and \
            item.item_type is ExploreItem.Type.ItemData:

            self.calcRollOffAmp(item)
        
        # analise: cross talk
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemCrossTalk.checkState() == Qt.CheckState.Checked and \
            item.item_type is ExploreItem.Type.ItemData:
      
            self.calcCrossTalk(item)

        # plot
        #todo: criar item que abarque todos os de analysis para que plot de phaseerror e trajectory
        #todo: seja feita em condicao mais simples
        if  self.toolbar.buttonPlot.isChecked() and \
            (item.item_type is ExploreItem.Type.ItemTrajectory or \
             item.item_type is ExploreItem.Type.ItemPhaseError):
            
            self.plotar(item)
        
        # tabela
        if self.toolbar.buttonTable.isChecked() and \
            self.toolbar.buttonTable.objectName()==self.toolbar.actiontabela.objectName() and \
            item.item_type is ExploreItem.Type.ItemData:
            
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
