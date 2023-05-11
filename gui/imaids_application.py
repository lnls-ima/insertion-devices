# padrao de nomeacao de variaveis #

# actions
## object name das actions: action<action_name>
## acessamos certa action com self.action<action_name>
## slots das actions: actionNewPressed


import time

t = time.time()
import os
import sys
import numpy as np
dt = time.time()-t
print('imports menores =',dt*1000,'ms')

t = time.time()
from  PyQt6.QtWidgets import   (QApplication,
                                QMainWindow,
                                QStatusBar,
                                QMenuBar,
                                QMessageBox,
                                QDialog)
from   PyQt6.QtGui    import   (QAction,
                                QIcon,
                                QCursor)
from   PyQt6.QtCore   import    Qt
dt = time.time()-t
print('imports pyqt =',dt*1000,'ms')

t = time.time()
from widgets import analysis_dialog, model_dialog, projects, table_model, toolbar, canvas, data_dialog
from widgets.items import ExploreItem
dt = time.time()-t
print('imports widgets =',dt*1000,'ms')


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

        self.multiplotchart = canvas.Canvas()
        self.abscissa = []
        self.ordenada = []

        self.tabela = None

        # -------------- construcao de tab widgets de projetos -------------- #

        # projects tab widget
        self.projects = projects.TabProjects(parent=self)
        self.projects.widget(0).tree.itemClicked.connect(self.tree_item_clicked)
        self.projects.itemconnect.connect(
            lambda i: self.projects.widget(i).tree.itemClicked.connect(
                self.tree_item_clicked
            )
        )

        # --------------------- construcao da status bar --------------------- #

        # status bar
        self.statusbar = QStatusBar()
        self.statusbar.setObjectName("Status Bar")


        # ---------------------- contrucao da tool bar ---------------------- #

        self.toolbar = toolbar.IMAIDsToolBar(title="Tool Bar",parent=self)
        self.toolbar.buttonAnalysis.apply.clicked.connect(self.applyAnalysis)
        

        # ------------------- construcao do main menu bar ------------------- #

        # main menu bar
        self.menubar = QMenuBar(parent=self)
        ## main menu bar - File menu
        self.menuFile = self.menubar.addMenu("&File")
        ### main menu bar - File menu - New Project action
        self.actionNew_Project = QAction(QIcon("icons/icons/projection-screen--plus.png"),"New Project", self)
        self.actionNew_Project.triggered.connect(self.projects.add_project)
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addSeparator()
        ### main menu bar - File menu - Open Data action
        self.actionOpen_Data = QAction(QIcon("icons/icons/database-import.png"),"Open Data ...", self)
        self.actionOpen_Data.triggered.connect(self.open_files)
        self.menuFile.addAction(self.actionOpen_Data)
        self.menuFile.addSeparator()
        ### main menu bar - File menu - Generate Model action
        self.actionGenerate_Model = QAction(QIcon("icons/icons/magnet-blue.png"),"Generate Model", self)
        self.actionGenerate_Model.triggered.connect(self.model_generation)
        self.menuFile.addAction(self.actionGenerate_Model)
        self.menuFile.addSeparator()
        ### main menu bar - File menu - Exit action
        self.actionExit = QAction(QIcon("icons/icons/door-open-out.png"),"Exit", self)
        self.actionExit.triggered.connect(self.close)
        self.menuFile.addAction(self.actionExit)
        ## main menu bar - Edit menu
        self.menuEdit = self.menubar.addMenu("&Edit")
        ### main menu bar - Edit menu - Analysis action
        self.actionAnalysis = QAction(QIcon("icons/icons/beaker--pencil"),"Custom Analysis", self)
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
        actionToolBar = QAction(QIcon("icons/icons/toolbox.png"),self.toolbar.objectName(), self, checkable=True)
        actionToolBar.setChecked(True)
        actionToolBar.triggered.connect(self.toolbar.setVisible)
        self.menuView.addAction(actionToolBar)
        ### main menu bar - View menu - StatusBar action
        actionStatusBar = QAction(QIcon("icons/icons/ui-status-bar-blue.png"),self.statusbar.objectName(), self, checkable=True)
        actionStatusBar.setChecked(True)
        actionStatusBar.triggered.connect(self.statusbar.setVisible)
        self.menuView.addAction(actionStatusBar)
        ## main menu bar - Settings menu
        self.menuSettings = self.menubar.addMenu("&Settings")
        ### main menu bar - Settings menu - Apply action
        self.actionApplyForAll = QAction(QIcon("icons/icons/wand-hat.png"),"Apply for All", self, checkable=True)
        self.menuSettings.addAction(self.actionApplyForAll)
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

    def open_files(self, checked):
        #?: todo: criar datadialog no init e apenas fazer show dele quando abrir files
        #?: todo: quando terminar e fechar o dialog, apagar o que foi inserido
        
        ID_list, filenames, name_list = data_dialog.DataDialog.getOpenFileIDs(files=self.projects.currentWidget().filenames, parent=self)
        
        for ID, filename, name in zip(ID_list, filenames, name_list):
            self.projects.currentWidget().filenames.append(filename)
            self.treeInsert(ID=ID, ID_type="Data",name=name)

    #!: todo: passar criacao do objeto insertion device para dentro do dialog, um dos parametros do dialog vai ser o project tab atual
    #!: vai ajudar na parte de passar os parametros
    #!: ja vai poder colocar metodo accept la
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
    #!: tree insert dentro de projects, como metodo da tree mesmo
    def treeInsert(self, ID, ID_type, name=''):

        id_num = {"Data": 0, "Model": 1}
        
        if ID_type=="Data":
            #childs = self.projects.currentWidget().tree.topLevelItem(id_num[ID_type]).childCount()+1
            #ID.name = f'{ID_type} {childs}'
            ID.name = name
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
    
    def closeEvent(self, event):
        answer = QMessageBox.question(self,
                                      "Quit Confirmation",
                                      "Are you sure you want to quit the application?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)

        if answer == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def applyAnalysis(self):

        if self.actionApplyForAll.isChecked():
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

        elif self.toolbar.buttonAnalysis.checkedItems():
            self.toolbar.buttonAnalysis.setChecked(True)
    

    ## edit slots

    #!: this method can be in the AnalysisDialog class
    def edit_analysis_parameters(self):
        dialog = analysis_dialog.AnalysisDialog(parent=self)
        answer = dialog.exec()
        if answer == QDialog.DialogCode.Accepted:
            print('edit ok')
    

    # tool bar slots

    def calcMagneticField(self, id_item: ExploreItem):

        id_name = id_item.text(0)

        #todo: talvez fazer os enums serem as chaves e passar texto na atribuicao dos enums Type
        analysis = self.projects.currentWidget().analysis_dict["Magnetic Field"]

        if id_name not in analysis:

            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            B = id_meas.get_field(x=0, y=0, z=self.Z, nproc=None, chunksize=100)
            Bx, By, Bz = B.T
            analysis[id_name] = {"z": self.Z, "Bx": Bx, "By": By, "Bz": Bz}

            field = ExploreItem(ExploreItem.Type.ItemMagneticField, id_item, [f"Magnetic Field", "Analysis"])
            field.setTextAlignment(1,Qt.AlignmentFlag.AlignRight)
            children = [ExploreItem(ExploreItem.Type.ItemResult, field, ["z", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, field, ["Bx", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, field, ["By", "List"]),
                        ExploreItem(ExploreItem.Type.ItemResult, field, ["Bz", "List"])]
            [item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight) for item in children]
            field.addChildren(children)
            return
        else:
            QMessageBox.warning(self,
                                "Field Warning",
                                f"Magnetic Field of ({id_name}) already calculated!")
            return

    def calcTrajectory(self, id_item: ExploreItem):

        id_name = id_item.text(0)

        analysis = self.projects.currentWidget().analysis_dict["Trajectory"]
        
        if id_name not in analysis:

            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            #energy = 3 x0 = 0 y0 = 0 z0 = -900 dxds0 = 0 dyds0 = 0 dzds0 = 1 zmax = 900 rkstep = 0.5
            traj = id_meas.calc_trajectory(self.energy,[self.x0,self.y0,self.z0,self.dxds0,self.dyds0,self.dzds0],self.zmax,self.rkstep, dz=0, on_axis_field=False)
            x, y, z, dxds, dyds, dzds = traj.T
            analysis[id_name] = {"x": x, "y": y, "z": z, "x'": dxds, "y'": dyds, "z'": dzds}

            traj = ExploreItem(ExploreItem.Type.ItemTrajectory, id_item, [f"Trajectory", "Analysis"])
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
                                f"Trajectory of ({id_name}) already calculated!")
            return
    
    def calcPhaseError(self, id_item: ExploreItem):
        
        id_name = id_item.text(0)

        analysis = self.projects.currentWidget().analysis_dict["Phase Error"]
        
        if id_name not in analysis:
        
            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            traj_dict = self.projects.currentWidget().analysis_dict["Trajectory"][id_name]
            traj = np.array(list(traj_dict.values())).T
            bxamp, byamp, _, _ = id_meas.calc_field_amplitude()
            kh, kv = id_meas.calc_deflection_parameter(bxamp, byamp)
            z_list, pe, pe_rms = id_meas.calc_phase_error(self.energy, traj, bxamp, byamp, self.skip_poles, zmin=None, zmax=None, field_comp=None)
            #chaves do dicionario no membro direito devem ser iguais aos nomes usados nos respectivos items
            analysis[id_name] = {"z poles": z_list, "PhaseErr": pe, "RMS [rad]": pe_rms}

            phaserr = ExploreItem(ExploreItem.Type.ItemPhaseError, id_item, [f"Phase Error","Analysis"])
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
                                f"Phase Error of ({id_name}) already calculated!")
            return
    
    def calcIntegrals(self, id_item: ExploreItem):
        
        id_name = id_item.text(0)

        analysis = self.projects.currentWidget().analysis_dict["Field Integrals"]
        
        if id_name not in analysis:
        
            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            B_dict = self.projects.currentWidget().analysis_dict["Magnetic Field"][id_name]
            B = np.array(list(B_dict.values())[:-1]).T
            ib, iib = id_meas.calc_field_integrals(z_list=self.Z, x=0, y=0, field_list=B, nproc=None, chunksize=100)
            ibx, iby, ibz = ib.T
            iibx, iiby, iibz = iib.T
            analysis[id_name] = {'IBx': ibx, 'IBy': iby, 'IBz': ibz, 'IIBx': iibx, 'IIBy': iiby, 'IIBz': iibz}

            integrals = ExploreItem(ExploreItem.Type.ItemIntegrals, id_item, [f"Field Integrals", "Analysis"])
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
                                f"Field Integrals of ({id_name}) already calculated!")
            return
    
    def calcRollOffPeaks(self, id_item: ExploreItem):

        id_name = id_item.text(0)

        analysis = self.projects.currentWidget().analysis_dict["Roll Off Peaks"]
        
        if id_name not in analysis:
        
            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            ropx, ropy, ropz = id_meas.calc_roll_off_peaks(z=self.Z,x=self.X,y=0,field_comp=None)
            analysis[id_name] = {'ROPx': ropx,'ROPy': ropy,'ROPz': ropz}

            rollffp = ExploreItem(ExploreItem.Type.ItemRollOffPeaks, id_item, [f'Roll Off Peaks', "Analysis"])
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
                                f"Roll Off Peaks of ({id_name}) already calculated!")
            return
    
    def calcRollOffAmp(self, id_item: ExploreItem):

        id_name = id_item.text(0)

        analysis = self.projects.currentWidget().analysis_dict["Roll Off Amplitude"]
        
        if id_name not in analysis:
        
            id_meas = self.projects.currentWidget().insertiondevices[id_name]

            roax, roay, roaz = id_meas.calc_roll_off_amplitude(z=self.Z,x=self.X,y=0)
            analysis[id_name] = {'ROAx': roax,'ROAy': roay,'ROAz': roaz}

            rollffa = ExploreItem(ExploreItem.Type.ItemRollOffAmp, id_item, [f'Roll Off Amplitude', "Analysis"])
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
                                f"Roll Off Amplitude of ({id_name}) already calculated!")
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
                                f"Cross Talk of ({id_name}) already calculated!")
            return

    def update_dicts_key(self, key, new_key):
        dicts =[self.projects.currentWidget().insertiondevices,
                *self.projects.currentWidget().analysis_dict.values()]
        
        for dicti in dicts:
            if key in dicti:
                value = dicti.pop(key)
                dicti[new_key] = value
    
    def plotar(self, analysis_item: ExploreItem):

        analysis_name = analysis_item.parent().text(0)

        # tracando grafico padrao
        chart = canvas.Canvas()

        if  analysis_item.item_type is ExploreItem.Type.ItemTrajectory:
            traj_dict = self.projects.currentWidget().analysis_dict["Trajectory"][analysis_name]
            x, y, z, dxds, dyds, dzds = traj_dict.values()

            chart.ax.plot(z,dxds)
            chart.ax.grid()
            chart.ax.set_title("Trajectory - Angular Deviation in x")
            chart.ax.set_xlabel("z (mm)")
            chart.ax.set_ylabel("x' (rad)")

        if  analysis_item.item_type is ExploreItem.Type.ItemPhaseError:
            phaserr_dict = self.projects.currentWidget().analysis_dict["Phase Error"][analysis_name]
            z_poles, pe, perms = phaserr_dict.values()

            chart.ax.plot(np.arange(1,len(pe)+1), pe*180/np.pi,'o-')
            chart.ax.grid()
            chart.ax.set_title("Phase Error")
            chart.ax.set_xlabel("Pole")
            chart.ax.set_ylabel("Phase Error (°)")
        
        # colocando grafico no visuals
        i = self.projects.currentWidget().visuals.addTab(chart, f"Plot {analysis_name} - x' vs z")
        self.projects.currentWidget().visuals.setCurrentIndex(i)

        chart.fig.tight_layout()

    def plotar2x2(self, result_item: ExploreItem):

        param = result_item.text(0)
        calc = result_item.parent().text(0)
        data = result_item.parent().parent().text(0)
        params_dict = self.projects.currentWidget().analysis_dict[calc][data]

        #todo: abrir dialogo para personalizar o grafico

        if self.abscissa:
            if not self.ordenada:
                self.ordenada = [param, params_dict[param]]

                if self.toolbar.buttonPlot.objectName()==self.toolbar.actiongrafico2x2.objectName():
                    chart = canvas.Canvas()

                    chart.ax.set_title(f"{self.ordenada[0]} vs {self.abscissa[0]}")
                    chart.ax.set_xlabel(self.abscissa[0])
                    chart.ax.set_ylabel(self.ordenada[0])
                
                elif self.toolbar.buttonPlot.objectName()==self.toolbar.actiongraficos.objectName():
                    chart = self.multiplotchart

                isPlotEmpty = not (len(chart.ax.get_lines()) or \
                                   len(chart.ax.patches) or \
                                   len(chart.ax.images))
            
                chart.ax.plot(self.abscissa[1],self.ordenada[1])
                chart.ax.grid(visible=True)

                # colocando grafico no visuals
                if isPlotEmpty:
                    i = self.projects.currentWidget().visuals.addTab(chart, "Plot")
                    self.projects.currentWidget().visuals.setCurrentIndex(i)

                # Trigger the canvas to update and redraw
                chart.draw()

                # adjustment
                chart.fig.tight_layout()

                # restore abscissa and ordenada empty
                self.abscissa = []
                self.ordenada = []
        else:
            self.abscissa = [param, params_dict[param]]

    #*: metodo suspenso por enquanto
    # def plotar2x2_table_section(self, column):

    #     #tablemodel = self.tabela.modeltable
    #     tablemodel = self.projects.currentWidget().visuals.currentWidget().modeltable
    #     sectionData = tablemodel._data[:,column]
    #     sectionText = tablemodel.headerData(column, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)

    #     if self.abscissa:
    #         if not self.ordenada:
    #             self.ordenada = [sectionText,sectionData]

    #             chart = canvas.Canvas()

    #             chart.ax.set_title(f"{self.ordenada[0]} vs {self.abscissa[0]}")
    #             chart.ax.set_xlabel(self.abscissa[0])
    #             chart.ax.set_ylabel(self.ordenada[0])
    #             chart.ax.plot(self.abscissa[1], self.ordenada[1])
    #             chart.ax.grid(visible=True)

    #             i = self.projects.currentWidget().visuals.addTab(chart, "Plot")
    #             self.projects.currentWidget().visuals.setCurrentIndex(i)
                
    #             chart.fig.tight_layout()

    #             # restore abscissa and ordenada empty
    #             self.abscissa = []
    #             self.ordenada = []
    #     else:
    #         self.abscissa = [sectionText,sectionData]

    def plotar2x2_table_select(self, indexes):

        tablemodel = self.projects.currentWidget().visuals.currentWidget().modeltable

        colx = indexes[0].column()
        coly = indexes[-1].column()

        xx = []
        yy = []
        for index in indexes:
            row = index.row()
            col = index.column()
            if col==colx:
                xx.append(tablemodel._data[row,col])
            if col==coly:
                yy.append(tablemodel._data[row,col])

        chart = canvas.Canvas()
        chart.ax.plot(xx,yy)

        i = self.projects.currentWidget().visuals.addTab(chart, "plot")
        self.projects.currentWidget().visuals.setCurrentIndex(i)

    def table_data(self, id_meas_item: ExploreItem):

        id_meas_name = id_meas_item.text(0)
        
        meas = self.projects.currentWidget().insertiondevices[id_meas_name]
        data = meas._raw_data
        header = ['X[mm]', 'Y[mm]', 'Z[mm]', 'Bx[T]', 'By[T]', 'Bz[T]']
        
        #contrucao da tabela
        self.tabela = table_model.Table(data, header)
        #self.tabela.horizontalHeader().sectionClicked.connect(self.table_section_clicked)
        self.tabela.selectReturned.connect(self.table_cells_returned)
        
        # colocando tabela no visuals
        i = self.projects.currentWidget().visuals.addTab(self.tabela, f"Table {id_meas_name}")
        self.projects.currentWidget().visuals.setCurrentIndex(i)

    def table_result(self, result_item: ExploreItem):

        param = result_item.text(0)
        calc = result_item.parent().text(0)
        data = result_item.parent().parent().text(0)
        params_dict = self.projects.currentWidget().analysis_dict[calc][data]

        param_array = params_dict[param]
        param_array = param_array.reshape(-1,1)
        #print(param_array.shape)
        print(param)

        #contrucao da tabela
        tabela = table_model.Table(param_array, [param])

        # colocando tabela no visuals
        i = self.projects.currentWidget().visuals.addTab(tabela, f"Table {param} - {calc} - {data}")
        self.projects.currentWidget().visuals.setCurrentIndex(i)

    def table_cells_returned(self, indexes):

        if  self.toolbar.buttonPlot.isChecked() and \
            self.toolbar.buttonPlot.objectName()==self.toolbar.actiongraficotable.objectName():
            
            self.plotar2x2_table_select(indexes)

    #*: metodo suspenso por enquanto
    # def table_section_clicked(self, column):
        
    #     if  self.toolbar.buttonPlot.isChecked() and \
    #         self.toolbar.buttonPlot.objectName()==self.toolbar.actiongraficotable.objectName():
            
    #         self.plotar2x2_table_section(column)


    # tab bar slots


    # tree slots

    def tree_item_clicked(self, item: ExploreItem, column):

        # analise: campo magnetico
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemMagneticField.isChecked() and \
            item.item_type is ExploreItem.Type.ItemData:

            self.calcMagneticField(item)
        
        # analise: trajetoria
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemTrajectory.isChecked() and \
            item.item_type is ExploreItem.Type.ItemData:

            self.calcTrajectory(item)
        
        # analise: erro de fase
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemPhaseError.isChecked() and \
            item.item_type is ExploreItem.Type.ItemData:
            
            self.calcPhaseError(item)

        # analise: integrais de campo
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemIntegrals.isChecked() and \
            item.item_type is ExploreItem.Type.ItemData:
            
            self.calcIntegrals(item)

        # analise: roll off peaks
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemRollOffPeaks.isChecked() and \
            item.item_type is ExploreItem.Type.ItemData:

            self.calcRollOffPeaks(item)
        
        # analise: roll off amplitude
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemRollOffAmp.isChecked() and \
            item.item_type is ExploreItem.Type.ItemData:

            self.calcRollOffAmp(item)
        
        # analise: cross talk
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemCrossTalk.isChecked() and \
            item.item_type is ExploreItem.Type.ItemData:
      
            self.calcCrossTalk(item)

        # plot
        #todo: criar item que abarque todos os de analysis para que plot de phaseerror e trajectory
        #todo: seja feita em condicao mais simples
        if  self.toolbar.buttonPlot.isChecked() and \
            self.toolbar.buttonPlot.objectName()==self.toolbar.actiongrafico.objectName() and \
            (item.item_type is ExploreItem.Type.ItemTrajectory or \
             item.item_type is ExploreItem.Type.ItemPhaseError):
            
            self.plotar(item)

        # plot 2 a 2
        if  self.toolbar.buttonPlot.isChecked() and \
            (self.toolbar.buttonPlot.objectName()==self.toolbar.actiongrafico2x2.objectName() or \
             self.toolbar.buttonPlot.objectName()==self.toolbar.actiongraficos.objectName()) and \
            item.item_type is ExploreItem.Type.ItemResult:
                
            self.plotar2x2(item)

        # desmarcar botao de plot ou mudar tipo de plot e clicar em um item qualquer
        if  not self.toolbar.buttonPlot.isChecked() or \
            self.toolbar.buttonPlot.objectName()!=self.toolbar.actiongraficos.objectName():
            
            self.multiplotchart = canvas.Canvas()
        
        # tabela: mapa de campo
        if self.toolbar.buttonTable.isChecked() and \
            self.toolbar.buttonTable.objectName()==self.toolbar.actiontabela.objectName() and \
            item.item_type is ExploreItem.Type.ItemData:
            
            self.table_data(item)
        
        # tabela: resultado
        if  self.toolbar.buttonTable.isChecked() and \
            self.toolbar.buttonTable.objectName()==self.toolbar.actiontabela.objectName() and \
            item.item_type is ExploreItem.Type.ItemResult:
            
            self.table_result(item)
    
    
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
