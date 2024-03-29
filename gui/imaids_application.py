
import time

t = time.time()
import sys

from  PyQt6.QtWidgets import   (QApplication,
                                QMainWindow,
                                QMessageBox)
from   PyQt6.QtCore   import    Qt

from widgets import analysis, model_dialog, projects, window_bars, data_dialog, shortcuts_dialog
from widgets.visual_elements import Canvas, Table
from widgets.explore_window import ExploreItem
dt = time.time()-t
print('all imports:',dt*1000,'ms')


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # -------------- construcao de tab widgets de projetos -------------- #

        self.projects = projects.ProjectsTabWidget(parent=self)
        self.projects.tabAdded.connect(self.project_connect)
        self.projects.addTab(text='Project')


        # --------------------- construcao da status bar --------------------- #

        self.statusbar = window_bars.StatusBar()


        # ---------------------- contrucao da tool bar ---------------------- #

        self.toolbar = window_bars.ToolBar(title="Tool Bar",parent=self)
        self.toolbar_connect()
        

        # ------------------- construcao do main menu bar ------------------- #

        self.menubar = window_bars.MenuBar(parent=self)
        self.menubar_connect()


        # --------------------- contrucao da main window --------------------- #

        self.setStatusBar(self.statusbar)
        self.addToolBar(self.toolbar)
        self.setMenuBar(self.menubar)
        self.setCentralWidget(self.projects)

        #todo: instalar event filter na classe do painted button para esconder menu quando e' clicado

        self.setWindowTitle("IMAIDs Interface")
        self.resize(1200,700)
        


    # FUNCTIONS

    
    # SLOTS

    # window slots

    def keyPressEvent(self, event) -> None:
        visuals = self.projects.currentWidget().visuals

        # Visualization Window shortcuts
        ## add mode
        if event.key() == Qt.Key.Key_A:
            if isinstance(visuals.currentWidget(),Canvas):
                visuals.changeIcon(not visuals.isModeAdd())
        ## visuals tab
        elif event.key() in [Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3,
                             Qt.Key.Key_4, Qt.Key.Key_5, Qt.Key.Key_6,
                             Qt.Key.Key_7, Qt.Key.Key_8, Qt.Key.Key_9]:
            index = int(str(Qt.Key(event.key()))[-1])-1
            if index < visuals.count():
                visuals.setCurrentIndex(index)
        ## erase visuals current tab
        elif event.key() == Qt.Key.Key_Backspace:
            if visuals.currentWidget() is not None:
                visuals.closeTab(visuals.currentIndex())

        else:
            return super().keyPressEvent(event)


    # menubar slots

    def menubar_connect(self):
        # Menubar
        self.menubar.clicked.connect(self.update_menu)
        # File menu
        self.menubar.actionNew_Project.triggered.connect(lambda: self.projects.addTab())
        self.menubar.actionOpen_Data.triggered.connect(self.open_files)
        self.menubar.actionGenerate_Model.triggered.connect(self.model_generation)
        self.menubar.actionExit.triggered.connect(self.close)
        # Edit menu
        self.menubar.actionAnalysis.triggered.connect(self.edit_analysis_parameters)
        # View menu
        self.menubar.actionFile.triggered.connect(self.setFilesVisible)
        self.menubar.actionDockTree.triggered.connect(self.setDockVisible)
        self.menubar.actionDockOperations.triggered.connect(self.setDockVisible)
        self.menubar.actionDockSummary.triggered.connect(self.setDockVisible)
        self.menubar.actionDockCommand.triggered.connect(self.setDockVisible)
        self.menubar.actionToolBar.triggered.connect(self.toolbar.setVisible)
        self.menubar.actionStatusBar.triggered.connect(self.statusbar.setVisible)
        # Setting menu
        self.menubar.actionApplyForAll.triggered.connect(self.toolbar.swap_apply)
        # Help menu
        self.menubar.actionShortcuts.triggered.connect(lambda checked:
        shortcuts_dialog.ShortcutsDialog(self).exec())

    def update_menu(self):
        project = self.projects.currentWidget()
        self.menubar.actionFile.setChecked(project.tree.isFilesVisible())
        self.menubar.actionDockTree.setChecked(project.dockTree.isVisible())
        self.menubar.actionDockOperations.setChecked(project.tree.dockOperations.isVisible())
        self.menubar.actionDockSummary.setChecked(project.dockSummary.isVisible())
        self.menubar.actionDockCommand.setChecked(project.dockCommand.isVisible())
        self.menubar.actionToolBar.setChecked(self.toolbar.isVisible())
    
    ## file slots

    def open_files(self, checked):
        project = self.projects.currentWidget()

        files = [id_dict.get("filename") for id_dict in project.insertiondevices.values()]
        IDs_params = data_dialog.DataDialog.getOpenFileIDs(files=files, parent=project)
        
        for ID, filename, name, correct in IDs_params:
            IDType = ExploreItem.IDType.IDData

            num = list(project.DftIDlabels.values()).count(name)
            ID_item = project.tree.insertID(IDType=IDType,
                                            ID=ID, correct=correct, filename=filename,
                                            name=name if num==0 else name+f' {num+1}')
            project.insertiondevices[id(ID_item)] = {"InsertionDeviceObject": ID,
                                                     "filename": filename,
                                                     "item": ID_item}
            project.DftIDlabels[id(ID_item)] = name

            if correct:
                project.insertiondevices[id(ID_item)]["Cross Talk"]=correct

    def model_generation(self):
        project = self.projects.currentWidget()

        ID, name = model_dialog.ModelDialog.getSimulatedID(parent=self)

        if ID:
            IDType = ExploreItem.IDType.IDModel

            num = list(project.DftIDlabels.values()).count(name)
            ID_item = project.tree.insertID(IDType=IDType,ID=ID,
                                            name=name if num==0 else name+f' {num+1}')
            project.insertiondevices[id(ID_item)] = {"InsertionDeviceObject": ID,
                                                     "item": ID_item}
            project.DftIDlabels[id(ID_item)] = name
    
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

    ## settings slots

    def applyAnalysis(self):
        project = self.projects.currentWidget()
        analysis_btn = self.toolbar.buttonAnalysis

        #run analysis for all ID items
        if self.menubar.actionApplyForAll.isChecked():
            for item in project.tree.topLevelItem(0).children().values():
                self._exec_analysis(item)
            analysis_btn.Menu.uncheckAnalysisMenu()
        elif analysis_btn.Menu.checkedItems():
            analysis_btn.modeChanged.emit(False)

    ## edit slots

    def edit_analysis_parameters(self):
        project = self.projects.currentWidget()
        analysis.EditAnalysisDialog.updateParameters(params_kwargs=project.params, parent=self)
        #project.params = parameters_dict

    ## view slots

    def setFilesVisible(self, visible):
        tree = self.projects.currentWidget().tree
        data_items = tree.topLevelItem(0).children().values()
        for item in data_items:
            tree.files_visible = visible
            if visible:
                item.set_Status_Tip()
            else:
                item.setStatusTip(0,"")

    def setDockVisible(self, visible):
        project = self.projects.currentWidget()
        dock_name = self.sender().objectName()
        if "Tree" in dock_name:
            project.dockTree.setVisible(visible)
        elif "Operations" in dock_name:
            project.tree.dockOperations.setVisible(visible)
        elif "Summary" in dock_name:
            project.dockSummary.setVisible(visible)
        elif "Command" in dock_name:
            project.dockCommand.setVisible(visible)


    # tool bar slots

    def toolbar_connect(self):
        analysis_btn = self.toolbar.buttonAnalysis
        analysis_btn.Menu.apply.clicked.disconnect(analysis_btn.applyChangeMode)
        analysis_btn.Menu.apply.clicked.connect(self.applyAnalysis)
        self.toolbar.modeChanged.connect(self.buttonActivateMessage)


    # status bar slots

    def buttonActivateMessage(self):
        toolbar_button = self.toolbar.buttonChecked
        self.statusbar.label_button.setText(f"<b>{toolbar_button.objectName()}</b> active")
        #bug for painted button when select other option


    # project slots

    def project_connect(self, proj_idx):
        project = self.projects.widget(proj_idx)
        project.tree.itemClicked.connect(self.tree_item_clicked)
        project.tree.selectReturned.connect(self.tree_items_returned)
        project.tree.keyPressed.connect(self.keyPressEvent)
        project.tree.treeOperations.itemClicked.connect(self.tree_item_clicked)
        project.tree.treeOperations.selectReturned.connect(self.tree_items_returned)
        project.visuals.tabAdded.connect(self.visuals_connect)

    ## tree slots

    def _exec_analysis(self, item):
        
        analysis_menu = self.toolbar.buttonAnalysis.Menu
        project = self.projects.currentWidget()

        analysis_activated = []
        analysis_funcs = [ExploreItem.calcCross_Talk,
                          ExploreItem.calcMagnetic_Field,
                          ExploreItem.calcTrajectory,
                          ExploreItem.calcPhase_Error,
                          ExploreItem.calcCumulative_Integrals,
                          ExploreItem.calcField_Integrals_vs_X,
                          ExploreItem.calcRoll_Off_Peaks,
                          ExploreItem.calcRoll_Off_Amplitude,
                          ExploreItem.calcHarmonics_Tuning,
                          ExploreItem.calcBrilliance,
                          ExploreItem.calcFlux_Density]

        for menu_item, func in zip(analysis_menu.items,analysis_funcs):
            if  menu_item.isChecked() and \
                ((menu_item is analysis_menu.itemCrossTalk and \
                    item.flag() is ExploreItem.IDType.IDData) or \
                    menu_item is not analysis_menu.itemCrossTalk):

                analysis_activated.append(func)

        project.analyzeItem(item,analysis_activated)

    def tree_item_clicked(self, item: ExploreItem, column=0):

        analysis_button = self.toolbar.buttonAnalysis
        table_button = self.toolbar.buttonTable
        project = self.projects.currentWidget()

        # ----------------------------- analysis ----------------------------- #
        
        #todo: learn to execute the analysis in other thread
        #todo: https://realpython.com/python-pyqt-qthread/
        if analysis_button.isChecked() and item.type() is ExploreItem.IDType:

            self._exec_analysis(item)


        # ------------------------------ table ------------------------------ #
        if  table_button.isChecked() and \
            table_button.selectedAction.text()=="Table" and \
            item.type() is not ExploreItem.ContainerType and \
            item.flag() is not ExploreItem.IDType.IDModel:

            project.displayTable(item)


        # ------------------------------- save ------------------------------- #
        if  self.toolbar.actionSave.isChecked() and \
            item.flag() is ExploreItem.IDType.IDData:

            project.saveFieldMap(item)


        # ---------------------------- modeldata ---------------------------- #
        if  self.toolbar.actionModelData.isChecked() and \
            item.flag() is ExploreItem.IDType.IDModel:

            project.modelToData(item)


        # ---------------------------- solvemodel ---------------------------- #
        if  self.toolbar.actionSolveModel.isChecked() and \
            item.flag() is ExploreItem.IDType.IDModel:

            project.solveModel(item)

        # ----------------------------- summary ----------------------------- #
        #*: A principio poderia apresentar resumo para o modelo, mas precisa calcular alguns
        #*: parametros tais como amplitude do campo e outros, o que demora um tanto, por isso
        #*: o resumo foi restringido a dados

        # prevent items from operation window update the summary
        # prevent items of models (including analysis and results) update the summary
        id_info = project.treeItemInfo(item)
        ctn_flag = id_info["ctn_item"].flag()
        isFromOperation = ctn_flag in [ExploreItem.ContainerType.ContainerAnalyses,
                                       ExploreItem.ContainerType.ContainerResults]
        if  not isFromOperation and \
            (item.type() is ExploreItem.ContainerType or \
             id_info.get("id_item").flag() is not ExploreItem.IDType.IDModel):

            project.summary.update(id_info.get("id_dict"))

    def tree_items_returned(self, items):
        plot_button = self.toolbar.buttonPlot
        project = self.projects.currentWidget()

        tpAnalysis = ExploreItem.AnalysisType
        tpResult = ExploreItem.ResultType
        rtArray = ExploreItem.ResultType.ResultArray
        
        #todo: action "Custom Analysis", ao selecionar items e retornar, primeiramente
        #todo: abre dialogo para inserir como será a operação a ser executada
        if self.toolbar.buttonOperation.isChecked():
            
            selected = self.toolbar.buttonOperation.selectedAction.text()
            sign = {"Plus Analyses": "+", "Minus Analyses": "-"}[selected]
            operation = f"{sign}".join([f"A{i}" for i in range(len(items))])

            if len(items) == 0:
                QMessageBox.information(self,
                                        "Operation Information",
                                        "Nothing selected to operate.")
            
            elif len(items) == 1:
                QMessageBox.information(self,
                                        "Operation Information",
                                        "Nothing to operate, select more than one item.")

            elif any(item.type() not in [tpAnalysis, tpResult] for item in items):
                QMessageBox.warning(self,
                                    "Operation Error",
                                    "Invalid items! Please select only Analyses or only Results.")

            elif any(item.type() != items[0].type() for item in items):
                QMessageBox.warning(self,
                                    "Operation Error",
                                    "Do not combine Analyses and Results items!")
            
            else:
                project.operateItems(operation,items)

        elif self.toolbar.buttonPlot.isChecked() and \
             plot_button.selectedAction.text()=="Plot":

            isOneDenied = len(items) == 1 and \
                          (items[0].type() is not tpAnalysis and \
                           items[0].flag() is not rtArray)
            isTwoDenied = len(items) == 2 and \
                          [items[0].flag(),items[1].flag()] != [rtArray,rtArray]

            if len(items) == 0:
                QMessageBox.information(self,
                                        "Plot Information",
                                        "Nothing selected to plot.")

            elif len(items) > 2:
                QMessageBox.warning(self,
                                    "Plot Error",
                                    "Select only two items!")
                
            elif isOneDenied:
                QMessageBox.warning(self,
                                    "Plot Error",
                                    "Plot cannot be performed. For one item, only Analysis or Result Array are allowed!")
            
            elif isTwoDenied:
                QMessageBox.warning(self,
                                    "Plot Error",
                                    "Plot cannot be performed. For two items, select only Result Arrays!")

            else:
                project.drawItems(items)

    ## visuals slots

    def visuals_connect(self, visual_idx):
        visual = self.projects.currentWidget().visuals.widget(visual_idx)
        if isinstance(visual, Table):
            visual.selectReturned.connect(self.table_cells_returned)
            visual.keyPressed.connect(self.keyPressEvent)

    def table_cells_returned(self, indexes):
        if  self.toolbar.buttonPlot.isChecked():
            visuals = self.projects.currentWidget().visuals
            visuals.drawTableCols(indexes)


    # outros metodos

    def mousePressEvent(self, event):
        #posicao do cursor do mouse nas coordenadas da window
        cursor_pos = event.pos()
        print("Current cursor position at widget: x = %d, y = %d" % (cursor_pos.x(), cursor_pos.y()))

        return
    
    def mouseDoubleClickEvent(self, a0) -> None:
        print('duplo')
        return super().mouseDoubleClickEvent(a0)




# execution

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
