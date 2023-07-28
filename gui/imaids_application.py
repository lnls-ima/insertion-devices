
import time
import os

t = time.time()
import sys
dt = time.time()-t
print('imports menores =',dt*1000,'ms')

t = time.time()
from  PyQt6.QtWidgets import   (QApplication,
                                QMainWindow,
                                QMessageBox)
from   PyQt6.QtCore   import    Qt
dt = time.time()-t
print('imports pyqt =',dt*1000,'ms')

t = time.time()
from widgets import analysis, model_dialog, projects, window_bars, data_dialog
from widgets.visual_elements import Canvas, Table
from widgets.explore_window import ExploreItem
dt = time.time()-t
print('imports widgets =',dt*1000,'ms')


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
        self.menubar.clicked.connect(self.update_menu)
        self.menubar.actionNew_Project.triggered.connect(lambda: self.projects.addTab())
        self.menubar.actionOpen_Data.triggered.connect(self.open_files)
        self.menubar.actionGenerate_Model.triggered.connect(self.model_generation)
        self.menubar.actionExit.triggered.connect(self.close)
        self.menubar.actionAnalysis.triggered.connect(self.edit_analysis_parameters)
        self.menubar.actionFile.triggered.connect(self.setFilesVisible)
        self.menubar.actionDockTree.triggered.connect(self.setDockVisible)
        self.menubar.actionDockSummary.triggered.connect(self.setDockVisible)
        self.menubar.actionDockCommand.triggered.connect(self.setDockVisible)
        self.menubar.actionToolBar.triggered.connect(self.toolbar.setVisible)
        self.menubar.actionStatusBar.triggered.connect(self.statusbar.setVisible)

    def update_menu(self):
        project = self.projects.currentWidget()
        self.menubar.actionFile.setChecked(project.tree.isFilesVisible())
        self.menubar.actionDockTree.setChecked(project.dockTree.isVisible())
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
            num = project.countIDnames(name,IDType)
            name += f" {num+1}" if num!=0 else ""
            ID_item = project.tree.insertID(IDType=IDType,
                                            ID=ID, correct=correct, filename=filename, name=name)
            project.insertiondevices[id(ID_item)] = {"InsertionDeviceObject": ID,
                                                     "filename": filename,
                                                     "item": ID_item}
            if correct:
                project.insertiondevices[id(ID_item)]["Cross Talk"]=correct

    def model_generation(self):
        
        ID, name = model_dialog.ModelDialog.getSimulatedID(parent=self)

        if ID is not None:
            project = self.projects.currentWidget()
            IDType = ExploreItem.IDType.IDModel
            num = project.countIDnames(name,IDType)
            name = f'{name} {num+1}'
            ID_item = project.tree.insertID(IDType=IDType,
                                            ID=ID, name=name)
            project.insertiondevices[id(ID_item)] = {"InsertionDeviceObject": ID,
                                                     "item": ID_item}
    
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
            for item in project.tree.topLevelItem(0).children():
                self._exec_analysis(item)
            analysis_btn.Menu.uncheckAnalysisMenu()
        elif analysis_btn.Menu.checkedItems():
            analysis_btn.modeChanged.emit(False)

    ## edit slots

    def edit_analysis_parameters(self):
        project = self.projects.currentWidget()
        analysis.AnalysisDialog.updateParameters(params_kwargs=project.params, parent=self)
        #project.params = parameters_dict

    ## view slots

    def setFilesVisible(self, visible):
        tree = self.projects.currentWidget().tree
        data_items = tree.topLevelItem(0).children()
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
                          ExploreItem.calcField_Integrals,
                          ExploreItem.calcRoll_Off_Peaks,
                          ExploreItem.calcRoll_Off_Amplitude]

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
        save_action = self.toolbar.actionSave
        project = self.projects.currentWidget()

        # ----------------------------- analysis ----------------------------- #
        
        #todo: learn to execute the analysis in other thread
        #todo: https://realpython.com/python-pyqt-qthread/
        if analysis_button.isChecked() and item.type() is ExploreItem.IDType:

            self._exec_analysis(item)


        # ------------------------------ table ------------------------------ #
        #*: por enquanto sem roll off peaks, pois deveria haver uma tabela para cada pico
        #*: por enquanto sem exibir tabela para apenas um numero
        if  table_button.isChecked() and \
            table_button.selectedAction.text()=="Table" and \
            (item.flag() in [ExploreItem.IDType.IDData,
                             ExploreItem.ResultType.ResultArray] or \
             (item.type() is ExploreItem.AnalysisType and \
              item.flag() is not ExploreItem.AnalysisType.RollOffPeaks)):

            project.displayTable(item)


        # ------------------------------- save ------------------------------- #
        if  save_action.isChecked() and \
            item.flag() is ExploreItem.IDType.IDData:

            project.saveFieldMap(item)

        # ----------------------------- summary ----------------------------- #
        #*: A principio poderia apresentar resumo para o modelo, mas precisa calcular alguns
        #*:   parametros tais como amplitude do campo e outros, o que demora um tanto, por isso
        #*:   o resumo foi restringido a dados
        if item.flag() is not ExploreItem.IDType.IDModel:
            project.update_summary(item)

    def tree_items_returned(self, items):
        if self.toolbar.buttonPlot.isChecked():

            if len(items) == 0:
                print("nada selecionado")

            #*: por enquanto sem roll off peaks, pois ha muitos graficos para
            #*: cada coordenada
            elif len(items) == 1 and \
                 (items[0].flag() is ExploreItem.AnalysisType.RollOffPeaks or \
                  (items[0].type() is not ExploreItem.AnalysisType and \
                   items[0].flag() is not ExploreItem.ResultType.ResultArray)):
                
                print("nao pode ser plotado")

            elif len(items) == 2 and \
                 ExploreItem.ResultType.ResultNumeric in [items[0].flag(),
                                                          items[1].flag()]:

                print("use apenas items que sao listas")

            elif len(items) > 2:
                print("selecione apenas 2 items")

            else:
                self.projects.currentWidget().drawItems(items)

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
