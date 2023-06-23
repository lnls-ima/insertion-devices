
import time

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

        # projects tab widget
        self.projects = projects.ProjectsTabWidget(parent=self)
        self.projects.tabAdded.connect(self.project_connect)
        self.projects.addTab(text='Project')
        self.projects.currentWidget().visuals.tabAdded.connect(self.visuals_connect)
        

        # --------------------- construcao da status bar --------------------- #

        self.statusbar = window_bars.StatusBar()


        # ---------------------- contrucao da tool bar ---------------------- #

        self.toolbar = window_bars.ToolBar(title="Tool Bar",parent=self)
        self.toolbar.buttonAnalysis.Menu.apply.clicked.connect(self.applyAnalysis)
        

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
        if event.key() in [Qt.Key.Key_G,Qt.Key.Key_P]:
            self.toolbar.buttonPlot.modeChanged.emit(True)
        elif event.key() == Qt.Key.Key_T:
            self.toolbar.buttonTable.modeChanged.emit(True)
        elif event.key() == Qt.Key.Key_A:
            if isinstance(visuals.currentWidget(),Canvas):
                visuals.changeIcon(not visuals.isModeAdd())
        elif event.key() in [Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3,
                             Qt.Key.Key_4, Qt.Key.Key_5, Qt.Key.Key_6,
                             Qt.Key.Key_7, Qt.Key.Key_8, Qt.Key.Key_9]:
            index = int(str(Qt.Key(event.key()))[-1])-1
            if index < visuals.count():
                visuals.setCurrentIndex(index)
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
        self.menubar.actionDockTree.triggered.connect(self.setDockVisible)
        self.menubar.actionDockSummary.triggered.connect(self.setDockVisible)
        self.menubar.actionDockCommand.triggered.connect(self.setDockVisible)
        self.menubar.actionToolBar.triggered.connect(self.toolbar.setVisible)
        self.menubar.actionStatusBar.triggered.connect(self.statusbar.setVisible)

    def update_menu(self):
        project = self.projects.currentWidget()
        self.menubar.actionDockTree.setChecked(project.dockTree.isVisible())
        self.menubar.actionDockSummary.setChecked(project.dockSummary.isVisible())
        self.menubar.actionDockCommand.setChecked(project.dockCommand.isVisible())
        self.menubar.actionToolBar.setChecked(self.toolbar.isVisible())
    
    ## file slots

    def open_files(self, checked):
        project = self.projects.currentWidget()

        ID_list, filenames, name_list = data_dialog.DataDialog.getOpenFileIDs(files=project.filenames, parent=self)
        
        for ID, filename, name in zip(ID_list, filenames, name_list):
            project.filenames.append(filename)
            project.insertiondevices[name] = {"InsertionDeviceObject": ID, "filename": filename}
            project.tree.insertID(ID=ID, IDType=ExploreItem.IDType.IDData,name=name)

    def model_generation(self):
        
        ID, name = model_dialog.ModelDialog.getSimulatedID(parent=self)

        if ID is not None:
            project = self.projects.currentWidget()
            num = project.countIDnames(name)
            name = f'{name} {num}'
            project.insertiondevices[name] = {"InsertionDeviceObject": ID}
            project.tree.insertID(ID=ID, IDType=ExploreItem.IDType.IDModel,name=name)
    
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

        if self.menubar.actionApplyForAll.isChecked():
            #executar analises para todos
            project = self.projects.currentWidget()
            for item in project.tree.topLevelItem(0).children():
                self.tree_item_clicked(item)

        elif self.toolbar.buttonAnalysis.Menu.checkedItems():
            self.toolbar.buttonAnalysis.setChecked(True)

    ## edit slots

    def edit_analysis_parameters(self):
        project = self.projects.currentWidget()
        analysis.AnalysisDialog.updateParameters(params_kwargs=project.params, parent=self)
        #project.params = parameters_dict
    
    ## view slots

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


    # project slots

    def project_connect(self, proj_idx):
        project = self.projects.widget(proj_idx)
        project.tree.itemClicked.connect(self.tree_item_clicked)
        project.tree.selectReturned.connect(self.tree_items_returned)
        project.tree.keyPressed.connect(self.keyPressEvent)

    ## tree slots

    def tree_item_clicked(self, item: ExploreItem, column=0):

        analysis_menu = self.toolbar.buttonAnalysis.Menu
        analysis_button = self.toolbar.buttonAnalysis
        table_button = self.toolbar.buttonTable
        save_action = self.toolbar.actionSave
        project = self.projects.currentWidget()

        # ----------------------------- analysis ----------------------------- #

        if analysis_button.isChecked() and item.type() is ExploreItem.IDType:

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

        # ------------------------------ table ------------------------------ #

        #*: por enquanto sem roll off peaks, pois deveria haver uma tabela para cada pico
        #*: por enquanto sem exibir tabela para apenas um numero
        if  table_button.isChecked() and \
            table_button.selectedAction.text()=="Table" and \
            item.type() is not ExploreItem.ContainerType and \
            item.flag() is not ExploreItem.ResultType.ResultNumeric and \
            item.flag() is not ExploreItem.AnalysisType.RollOffPeaks:

            project.displayTable(item)

        # ------------------------------- save ------------------------------- #

        if  save_action.isChecked() and \
            item.flag() is ExploreItem.IDType.IDData:

            project.saveFieldMap(item)


        # ----------------------------- summary ----------------------------- #

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
