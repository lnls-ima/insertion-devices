
import time

t = time.time()
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
                                QDialog,
                                QMenu)
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

        self.tabela = None

        # -------------- construcao de tab widgets de projetos -------------- #

        # projects tab widget
        self.projects = projects.ProjectsTabWidget(parent=self)
        self.projects.projectAdded.connect(self.project_connect)
        self.projects.addTab(text='Project')
        

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
        self.actionNew_Project.triggered.connect(lambda: self.projects.addTab())
        self.actionNew_Project.setShortcut("Ctrl+N")
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addSeparator()
        ### main menu bar - File menu - Open Data action
        self.actionOpen_Data = QAction(QIcon("icons/icons/database-import.png"),"Open Data ...", self)
        self.actionOpen_Data.triggered.connect(self.open_files)
        self.actionOpen_Data.setShortcut("Ctrl+O")
        self.menuFile.addAction(self.actionOpen_Data)
        self.menuFile.addSeparator()
        ### main menu bar - File menu - Generate Model action
        self.actionGenerate_Model = QAction(QIcon("icons/icons/magnet-blue.png"),"Generate Model", self)
        self.actionGenerate_Model.triggered.connect(self.model_generation)
        self.actionGenerate_Model.setShortcut("Ctrl+M")
        self.menuFile.addAction(self.actionGenerate_Model)
        self.menuFile.addSeparator()
        ### main menu bar - File menu - Exit action
        self.actionExit = QAction(QIcon("icons/icons/door-open-out.png"),"Exit", self)
        self.actionExit.triggered.connect(self.close)
        self.actionExit.setShortcut("Alt+F4")
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

        self.setStatusBar(self.statusbar)
        self.addToolBar(self.toolbar)
        self.setMenuBar(self.menubar)
        self.setCentralWidget(self.projects)

        self.setWindowTitle("IMAIDs Interface")
        self.resize(1200,700)
        


    # FUNCTIONS

    
    # SLOTS
    
    # window slots

    def keyPressEvent(self, event) -> None:
        if event.key() in [Qt.Key.Key_G,Qt.Key.Key_P]:
            self.toolbar.buttonPlot.modeChanged.emit(True)
        elif event.key() == Qt.Key.Key_T:
            self.toolbar.buttonTable.modeChanged.emit(True)
        else:
            return super().keyPressEvent(event)
        
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

        self.projects.currentWidget().insertiondevices[ID.name] = {"InsertionDeviceObject": ID}
        #todo: type deve ser diferente de modelo para dado
        
        data_container = self.projects.currentWidget().tree.topLevelItem(id_num[ID_type])
        data = ExploreItem(ExploreItem.IDType.IDData, data_container, [ID.name, "Table"])
        data.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        if not data_container.isExpanded():
            self.projects.currentWidget().tree.expandItem(data_container)
    
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
                self.tree_item_clicked(item)

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

    ## Analysis slots

    def analysisDispenser(self, id_item: ExploreItem, analysis_actived: list):

        id_name = id_item.text(0)
        id_dict = self.projects.currentWidget().insertiondevices[id_name]

        for calcAnalysis in analysis_actived:
            analysis = calcAnalysis.__name__.lstrip("calc").replace("_"," ")
            
            if analysis not in id_dict:

                analysis_item = ExploreItem(ExploreItem.Analysis(analysis), id_item, [f"{analysis}", "Analysis"])
                analysis_item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight)
                if not id_item.isExpanded():
                    self.projects.currentWidget().tree.expandItem(id_item)

                result_items = calcAnalysis(id_dict, analysis_item)
                [item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight) for item in result_items]
            
            else:
                QMessageBox.warning(self,
                                    f"Analysis Warning",
                                    f"{analysis} of ({id_name}) already calculated!")

    def calcMagnetic_Field(self, id_dict: dict, analysis_item: ExploreItem):

        ID = id_dict["InsertionDeviceObject"]
        B = ID.get_field(x=0, y=0, z=self.Z, nproc=None, chunksize=100)
        Bx, By, Bz = B.T
        id_dict[analysis_item.text(0)] = {"z [mm]": self.Z, "Bx [T]": Bx, "By [T]": By, "Bz [T]": Bz}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["z [mm]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["Bx [T]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["By [T]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["Bz [T]", "List"])]
        
        return result_items
        

    def calcTrajectory(self, id_dict: dict, analysis_item: ExploreItem):

        ID = id_dict["InsertionDeviceObject"]
        #energy = 3 x0 = 0 y0 = 0 z0 = -900 dxds0 = 0 dyds0 = 0 dzds0 = 1 zmax = 900 rkstep = 0.5
        traj = ID.calc_trajectory(self.energy,[self.x0,self.y0,self.z0,self.dxds0,self.dyds0,self.dzds0],self.zmax,self.rkstep, dz=0, on_axis_field=False)
        x, y, z, dxds, dyds, dzds = traj.T
        id_dict[analysis_item.text(0)] = {"x [mm]": x, "y [mm]": y, "z [mm]": z, "x' [rad]": dxds, "y' [rad]": dyds, "z' [rad]": dzds}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["x [mm]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["y [mm]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["z [mm]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["x' [rad]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["y' [rad]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["z' [rad]", "List"])]
        
        return result_items
        
    def calcPhase_Error(self, id_dict: dict, analysis_item: ExploreItem):

        ID = id_dict["InsertionDeviceObject"]
        traj_dict = id_dict[ExploreItem.Analysis.Trajectory.value]
        traj = np.array(list(traj_dict.values())).T
        bxamp, byamp, _, _ = ID.calc_field_amplitude()
        kh, kv = ID.calc_deflection_parameter(bxamp, byamp)
        z_list, pe, pe_rms = ID.calc_phase_error(self.energy, traj, bxamp, byamp, self.skip_poles, zmin=None, zmax=None, field_comp=None)
        #chaves do dicionario no membro direito devem ser iguais aos nomes usados nos respectivos items
        #*: por enquanto, guardo no dict de analysis so' os arrays, porque da' problema na tabela
        id_dict[analysis_item.text(0)] = {"z poles [mm]": z_list, "PhaseErr [deg]": pe*180/np.pi, "RMS [deg]": pe_rms*180/np.pi}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["z poles [mm]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ["PhaseErr [deg]", "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, analysis_item, ["RMS [deg]", f"{pe_rms*180/np.pi:.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, analysis_item, ["Bx Amp [T]", f"{bxamp:.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, analysis_item, ["By Amp [T]", f"{byamp:.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, analysis_item, ["Kh [T.mm]", f"{kh:.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, analysis_item, ["Kv [T.mm]", f"{kv:.1f}"])]
        
        return result_items
        
    def calcField_Integrals(self, id_dict: dict, analysis_item: ExploreItem):

        ID = id_dict["InsertionDeviceObject"]
        #todo: conferir calculo de integrais de campo para modelos
        B_dict = id_dict[ExploreItem.Analysis.MagneticField.value]
        B = np.array(list(B_dict.values())[1:]).T
        ib, iib = ID.calc_field_integrals(z_list=self.Z, field_list=B)
        ibx, iby, ibz = ib.T
        iibx, iiby, iibz = iib.T
        id_dict[analysis_item.text(0)] = {'z [mm]': self.Z,
                                          'IBx [G.cm]': ibx, 'IBy [G.cm]': iby, 'IBz [G.cm]': ibz,
                                          'IIBx [kG.cm2]': iibx, 'IIBy [kG.cm2]': iiby, 'IIBz [kG.cm2]': iibz}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['z [mm]',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['IBx [G.cm]',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['IBy [G.cm]',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['IBz [G.cm]',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['IIBx [kG.cm2]', "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['IIBy [kG.cm2]', "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['IIBz [kG.cm2]', "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, analysis_item, ['IBx T  [G.cm]',   f"{ibx[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, analysis_item, ['IBy T  [G.cm]',   f"{iby[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, analysis_item, ['IBz T  [G.cm]',   f"{ibz[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, analysis_item, ['IIBx T [kG.cm2]', f"{iibx[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, analysis_item, ['IIBy T [kG.cm2]', f"{iiby[-1]:7.1f}"]),
                        ExploreItem(ExploreItem.ResultType.ResultNumeric, analysis_item, ['IIBz T [kG.cm2]', f"{iibz[-1]:7.1f}"])]
        
        return result_items
        
    def calcRoll_Off_Peaks(self, id_dict: dict, analysis_item: ExploreItem):

        ID = id_dict["InsertionDeviceObject"]
        ropx, ropy, ropz = ID.calc_roll_off_peaks(z=self.Z,x=self.X,y=0,field_comp=None)
        id_dict[analysis_item.text(0)] = {'ROPx': ropx,'ROPy': ropy,'ROPz': ropz}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['ROPx',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['ROPy',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['ROPz',  "List"])]
        
        return result_items

    def calcRoll_Off_Amplitude(self, id_dict: dict, analysis_item: ExploreItem):

        ID = id_dict["InsertionDeviceObject"]
        roax, roay, roaz = ID.calc_roll_off_amplitude(z=self.Z,x=self.X,y=0)
        id_dict[analysis_item.text(0)] = {'ROAx': roax,'ROAy': roay,'ROAz': roaz}

        result_items = [ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['ROAx',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['ROAy',  "List"]),
                        ExploreItem(ExploreItem.ResultType.ResultArray, analysis_item, ['ROAz',  "List"])]
        
        return result_items

    def calcCross_Talk(self, id_dict: dict, analysis_item: ExploreItem):
        
        id_item = analysis_item.parent()
        id_name = id_item.text(0)

        ID = id_dict["InsertionDeviceObject"]
        ID.correct_angles(angxy=0.15, angxz=-0.21, angyx=-0.01,
                          angyz=-0.02, angzx=0.01, angzy=-0.74)
        ky = [-0.006781104386361973,-0.01675247563602003,7.568631573320983e-06]
        kz = [-0.006170829583118335,-0.016051627320478382,7.886674928668737e-06]
        ID.correct_cross_talk(ky=ky,kz=kz)
        id_dict[analysis_item.text(0)] = {'angxy':  0.15, 'angxz': -0.21,
                                          'angyx': -0.01, 'angyz': -0.02,
                                          'angzx':  0.01, 'angzy': -0.74,
                                          'ky': ky, 'kz': kz}
        
        analysis_item.delete()
        id_new_name = id_name+' C'
        id_item.setText(0,id_new_name)
        self.update_dict_key(key=id_name, new_key=id_new_name)

        result_items = []
        
        return result_items

    def update_dict_key(self, key, new_key):
        ids_dict = self.projects.currentWidget().insertiondevices

        if key in ids_dict:
            value = ids_dict.pop(key)
            ids_dict[new_key] = value

    ## Plot slots

    def plotPair(self, whosSelected: list):

        #*: por enquanto so' plotar dados de mesma analise e mesmo mapa de campo

        x_item = whosSelected[0]
        y_item = whosSelected[1]

        id_name = x_item.parent().parent().text(0)
        id_dict = self.projects.currentWidget().insertiondevices[id_name]

        analysis = x_item.parent().item_type.value
        analysis_dict = id_dict[analysis]

        x_label = x_item.text(0)
        y_label = y_item.text(0)

        x = analysis_dict[x_label]
        y = analysis_dict[y_label]

        

        visuals = self.projects.currentWidget().visuals
        isModeAdd = not visuals.tabIcon(visuals.currentIndex()).isNull()

        if isModeAdd:
            chart = visuals.currentWidget()

            chart.ax.set_title("")
            chart.ax.set_xlabel("")
            chart.ax.set_ylabel("")
            legend = chart.ax.legend_
            handles = legend.legendHandles
            labels = [label.get_text() for label in legend.get_texts()]

        else:
            # tracando grafico padrao
            chart = canvas.Canvas()

            chart.ax.grid(visible=True)
            chart.ax.set_xlabel(x_label)
            chart.ax.set_ylabel(y_label)
            chart.ax.set_title(f"{y_label} vs {x_label}")
            handles, labels = [], []

        line = chart.ax.plot(x,y)
        handles.extend(line)
        x_label = x_label[:x_label.find("[")-1]
        y_label = y_label[:y_label.find("[")-1]
        labels.extend([f"{y_label} vs {x_label} of {id_name}"])
        chart.ax.legend(handles, labels)

        if not isModeAdd:
            self.projects.currentWidget().visuals.addTab(chart, "Plot")

        # Trigger the canvas to update and redraw
        chart.draw()

        # adjustment
        chart.fig.tight_layout()
    
    def plotAnalysis(self, analysis_item: ExploreItem):

        id_name = analysis_item.parent().text(0)
        id_dict = self.projects.currentWidget().insertiondevices[id_name]

        analysis = analysis_item.item_type.value
        analysis_dict = id_dict[analysis]

        visuals = self.projects.currentWidget().visuals
        isModeAdd = not visuals.tabIcon(visuals.currentIndex()).isNull()

        if isModeAdd:
            chart = visuals.currentWidget()

            chart.ax.set_title("")
            chart.ax.set_xlabel("")
            chart.ax.set_ylabel("")
            legend = chart.ax.legend_
            handles = legend.legendHandles
            labels = [label.get_text() for label in legend.get_texts()]

        else:
            # tracando grafico padrao
            chart = canvas.Canvas()

            chart.ax.grid(visible=True)
            handles, labels = [], []

        if analysis_item.item_type is ExploreItem.Analysis.MagneticField:
            
            z, *B = list(analysis_dict.values())
            B = np.array(B).T

            B_lines = chart.ax.plot(z,B)
            if not isModeAdd:
                chart.ax.set_xlabel("z (mm)")
                chart.ax.set_ylabel("Bx, By, Bz (T)")
                chart.ax.set_title("Magnetic Field")
            handles.extend(B_lines)
            labels.extend([f"Bx of {id_name}",f"By of {id_name}",f"Bz of {id_name}"])
            chart.ax.legend(handles,labels)
        
        if analysis_item.item_type is ExploreItem.Analysis.Trajectory:
            
            x, y, z, dxds, dyds, dzds = analysis_dict.values()
            x_y = np.array([x,y]).T
            dxds_dyds = np.array([dxds,dyds]).T

            menuIntegral = QMenu(self)
            menuIntegral.addAction("Position Deviation")
            menuIntegral.addAction("Angular Deviation")
            #todo: consertar pos para pegar canto superior direito do item
            action = menuIntegral.exec(QCursor.pos())
            if action is None:
                return
            
            chart.ax.set_xlabel("z (mm)")
            if action.text()=="Position Deviation":
                integral_line = chart.ax.plot(z,x_y)
                if not isModeAdd:
                    chart.ax.set_ylabel("x, y (mm)")
                    chart.ax.set_title("Trajectory")
                handles.extend(integral_line)
                labels.extend([f"x of {id_name}", f"y of {id_name}"])
                chart.ax.legend(handles,labels)
                
            elif action.text()=="Angular Deviation":
                integral_line = chart.ax.plot(z,dxds_dyds)
                if not isModeAdd:
                    chart.ax.set_ylabel("x', y' (rad)")
                    chart.ax.set_title("Trajectory - Angular Deviation")
                handles.extend(integral_line)
                labels.extend([f"x' of {id_name}", f"y' of {id_name}"])
                chart.ax.legend(handles,labels)

        if  analysis_item.item_type is ExploreItem.Analysis.PhaseError:

            z_poles, phaserr, phaserr_rms = analysis_dict.values()

            phaserr_line = chart.ax.plot(np.arange(1,len(phaserr)+1), phaserr,'o-')
            rms_line = chart.ax.plot([1,len(phaserr)], [phaserr_rms, phaserr_rms],'--',c=phaserr_line[0].get_color())
            if not isModeAdd:
                chart.ax.set_title("Phase Error")
                chart.ax.set_xlabel("Pole ")
                chart.ax.set_ylabel("Phase Error (deg)")
            handles.extend(phaserr_line+rms_line)
            labels.extend([f"Phase Error of {id_name}",f"Phase Err RMS of {id_name}"])
            legend = chart.ax.legend(handles,labels)

        if analysis_item.item_type is ExploreItem.Analysis.Integrals:

            z, ibx, iby, ibz, iibx, iiby, iibz = analysis_dict.values()
            ib = np.array([ibx, iby, ibz]).T
            iib = np.array([iibx, iiby, iibz]).T

            menuIntegral = QMenu(self)
            menuIntegral.addAction("First Integral")
            menuIntegral.addAction("Second Integral")
            #todo: consertar pos para pegar canto superior direito do item
            action = menuIntegral.exec(QCursor.pos())
            if action is None:
                return
            
            chart.ax.set_xlabel("z (mm)")
            if action.text()=="First Integral":
                integral_line = chart.ax.plot(z,ib)
                if not isModeAdd:
                    chart.ax.set_ylabel("ibx, iby, ibz (G.cm)")
                    chart.ax.set_title("Field Integral - First")
                handles.extend(integral_line)
                labels.extend([f"ibx of {id_name}", f"iby of {id_name}", f"ibz of {id_name}"])
                chart.ax.legend(handles,labels)
                
            elif action.text()=="Second Integral":
                integral_line = chart.ax.plot(z,iib)
                if not isModeAdd:
                    chart.ax.set_ylabel("iibx, iiby, iibz (kG.cm2)")
                    chart.ax.set_title("Field Integral - Second")
                handles.extend(integral_line)
                labels.extend([f"iibx of {id_name}", f"iiby of {id_name}", f"iibz of {id_name}"])
                chart.ax.legend(handles,labels)
        
        # colocando grafico no visuals
        if not isModeAdd:
            self.projects.currentWidget().visuals.addTab(chart, "Plot")

        # Trigger the canvas to update and redraw
        chart.draw()
        
        chart.fig.tight_layout()

    def plotArray(self, result_item: ExploreItem):

        id_name = result_item.parent().parent().text(0)
        id_dict = self.projects.currentWidget().insertiondevices[id_name]

        analysis = result_item.parent().item_type.value
        analysis_dict = id_dict[analysis]

        result = result_item.text(0)
        
        visuals = self.projects.currentWidget().visuals
        isModeAdd = not visuals.tabIcon(visuals.currentIndex()).isNull()
        
        if isModeAdd:
            chart = visuals.currentWidget()
            
            chart.ax.set_title("")
            legend = chart.ax.legend_
            handles = legend.legendHandles
            labels = [label.get_text() for label in legend.get_texts()]

        else:
            # tracando grafico padrao
            chart = canvas.Canvas()

            chart.ax.grid(visible=True)
            chart.ax.set_title(result)
            handles, labels = [], []

        result_line = chart.ax.plot(analysis_dict[result])

        chart.ax.set_ylabel("Values")
        chart.ax.set_xlabel("Indexes")
        handles.extend(result_line)
        labels.extend([result])
        
        chart.ax.legend(handles, labels)

        # colocando grafico no visuals
        if not isModeAdd:
            self.projects.currentWidget().visuals.addTab(chart, "Plot")
        
        # Trigger the canvas to update and redraw
        chart.draw()

        chart.fig.tight_layout()

    def plotTable(self, indexes):

        plotColumns = indexes[0].column() != indexes[-1].column()
        modelTable = self.projects.currentWidget().visuals.currentWidget().model()

        chart = canvas.Canvas()
        chart.ax.grid(visible=True)

        if plotColumns:
            colx = indexes[0].column()
            x_label = modelTable._header[colx]
            x_label = x_label[:x_label.find("[")]
            coly = indexes[-1].column()
            y_label = modelTable._header[coly]
            y_label = y_label[:y_label.find("[")]

            xx = []
            yy = []
            for index in indexes:
                row = index.row()
                col = index.column()
                if col==colx:
                    xx.append(modelTable._data[row,col])
                if col==coly:
                    yy.append(modelTable._data[row,col])

            chart.ax.plot(xx,yy)
            chart.ax.set_xlabel(x_label)
            chart.ax.set_ylabel(y_label)
            chart.ax.set_title(f"{y_label} vs {x_label}")

        else:
            col = indexes[0].column()
            title = modelTable._header[col]

            array = []
            for index in indexes:
                row = index.row()
                array.append(modelTable._data[row,col])

            chart.ax.plot(array)
            chart.ax.set_xlabel("Indexes")
            chart.ax.set_ylabel("Values")
            chart.ax.set_title(f"{title}")

        self.projects.currentWidget().visuals.addTab(chart, "plot")

        chart.fig.tight_layout()

    def displayTable(self, item: ExploreItem):

        # tabela: mapa de campo
        if item.item_type is ExploreItem.IDType.IDData:
            id_item = item

            id_name = id_item.text(0)
            id_dict = self.projects.currentWidget().insertiondevices[id_name]
            
            ID_meas = id_dict["InsertionDeviceObject"]
            data = ID_meas._raw_data
            header = ['X[mm]', 'Y[mm]', 'Z[mm]', 'Bx[T]', 'By[T]', 'Bz[T]']
            
            #contrucao da tabela
            self.tabela = table_model.Table(data, header)
        
        # tabela: analise
        elif type(item.item_type) is ExploreItem.Analysis:
            analysis_item = item

            id_name = analysis_item.parent().text(0)
            id_dict = self.projects.currentWidget().insertiondevices[id_name]

            analysis = analysis_item.item_type.value
            analysis_dict = id_dict[analysis]
            
            params_array = [param for param in analysis_dict.values()
                                      if not isinstance(param, (int, float))]
            params_array = np.array(params_array).T
            
            self.tabela = table_model.Table(params_array, list(analysis_dict.keys()))

        # tabela: resultado
        elif item.item_type is ExploreItem.ResultType.ResultArray:
            result_item = item

            id_name = result_item.parent().parent().text(0)
            id_dict = self.projects.currentWidget().insertiondevices[id_name]

            analysis = result_item.parent().item_type.value
            analysis_dict = id_dict[analysis]

            result = result_item.text(0)
            result_array = analysis_dict[result].reshape(-1,1)

            #contrucao da tabela
            self.tabela = table_model.Table(result_array, [result])

        self.tabela.selectReturned.connect(self.table_cells_returned)
        self.tabela.keyPressed.connect(self.keyPressEvent)

        # colocando tabela no visuals
        self.projects.currentWidget().visuals.addTab(self.tabela, "Table")


    # project slots

    def project_connect(self, proj_idx):
        self.projects.widget(proj_idx).tree.itemClicked.connect(self.tree_item_clicked)
        self.projects.widget(proj_idx).tree.selectReturned.connect(self.tree_items_returned)
        self.projects.widget(proj_idx).tree.keyPressed.connect(self.keyPressEvent)

    ## tree slots

    def tree_item_clicked(self, item: ExploreItem, column=0):

        # ----------------------------- analysis ----------------------------- #

        analysis_activated = []

        # analise: cross talk
        if  self.toolbar.buttonAnalysis.isChecked() and \
            self.toolbar.buttonAnalysis.itemCrossTalk.isChecked() and \
            item.item_type is ExploreItem.IDType.IDData:
      
            analysis_activated.append(self.calcCross_Talk)

        # analise: campo magnetico
        if  self.toolbar.buttonAnalysis.isChecked() and \
            type(item.item_type) is ExploreItem.IDType and \
            self.toolbar.buttonAnalysis.itemMagneticField.isChecked():
            
            analysis_activated.append(self.calcMagnetic_Field)
        
        # analise: trajetoria
        if  self.toolbar.buttonAnalysis.isChecked() and \
            type(item.item_type) is ExploreItem.IDType and \
            self.toolbar.buttonAnalysis.itemTrajectory.isChecked():

            analysis_activated.append(self.calcTrajectory)
        
        # analise: erro de fase
        if  self.toolbar.buttonAnalysis.isChecked() and \
            item.item_type is ExploreItem.IDType.IDData and \
            self.toolbar.buttonAnalysis.itemPhaseError.isChecked():
            
            analysis_activated.append(self.calcPhase_Error)

        # analise: integrais de campo
        if  self.toolbar.buttonAnalysis.isChecked() and \
            item.item_type is ExploreItem.IDType.IDData and \
            self.toolbar.buttonAnalysis.itemIntegrals.isChecked():
            
            analysis_activated.append(self.calcField_Integrals)

        # analise: roll off peaks
        if  self.toolbar.buttonAnalysis.isChecked() and \
            item.item_type is ExploreItem.IDType.IDData and \
            self.toolbar.buttonAnalysis.itemRollOffPeaks.isChecked():

            analysis_activated.append(self.calcRoll_Off_Peaks)
        
        # analise: roll off amplitude
        if  self.toolbar.buttonAnalysis.isChecked() and \
            item.item_type is ExploreItem.IDType.IDData and \
            self.toolbar.buttonAnalysis.itemRollOffAmp.isChecked():

            analysis_activated.append(self.calcRoll_Off_Amplitude)

        if analysis_activated:
            self.analysisDispenser(item, analysis_activated)

        # ------------------------------ table ------------------------------ #

        if self.toolbar.buttonTable.isChecked() and \
            self.toolbar.buttonTable.objectName()==self.toolbar.actiontabela.objectName() and \
            type(item.item_type) is not ExploreItem.Container:
            
            self.displayTable(item)

    def tree_items_returned(self, items):
        if self.toolbar.buttonPlot.isChecked():

            if len(items)==1:
                item = items[0]

                if type(item.item_type) is ExploreItem.Analysis:
                    self.plotAnalysis(item)
                elif item.item_type is ExploreItem.ResultType.ResultArray:
                    self.plotArray(item)
                else:
                    print("use apenas items que sao listas")

            elif len(items)>=3:
                print("selecione apenas 2 items")

            elif items[0].item_type and items[1].item_type is ExploreItem.ResultType.ResultArray:
                self.plotPair(items)
            
            else:
                print("use apenas items que sao listas")

    ## visuals slots

    def table_cells_returned(self, indexes):

        if  self.toolbar.buttonPlot.isChecked():
            self.plotTable(indexes)


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
