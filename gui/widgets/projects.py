import typing

from  PyQt6.QtWidgets import   (QMainWindow,
                                QLineEdit,
                                QToolButton,
                                QDockWidget,
                                QMessageBox)
from   PyQt6.QtGui    import    QIcon
from   PyQt6.QtCore   import   Qt, QPoint

from .basics import BasicTabWidget
from .explore_window import ExploreItem, ExploreTreeWidget
from .visual_elements import Canvas, Table
from .visualization_window import VisualizationTabWidget
from .save_dialog import SaveDialog
from .summary_dialog import SummaryDialog, SummaryWidget

import numpy as np



class ProjectWidget(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.filenames = []
        self.insertiondevices = {}
        self.params = {
            "Magnetic Field": {
                "x": 0,
                "y": 0,
                "z": np.arange(-900,900+0.5,0.5),
                "nproc": None,
                "chunksize": 100
            },
            "Trajectory": {
                "energy": 3,
                "r0": [0,0,-900,0,0,1],
                "zmax": 900,
                "rkstep": 0.5,
                "dz": 0,
                "on_axis_field": False
            },
            "Phase Error": {
                "energy": 3,
                "traj": "calculated",
                "bx_amp": "calculated",
                "by_amp": "calculated",
                "skip_poles": 4,
                "zmin": None,
                "zmax": None,
                "field_comp": None
            },
            "Field Integrals": {
                "z_list": np.arange(-900,900+0.5,0.5),
                "x": 0,
                "y": 0,
                "field_list": None,
                "nproc": None,
                "chunksize": 100
            },
            "Roll Off Peaks": {
                "z": np.arange(-900,900+0.5,0.5),
                "x": np.arange(-5,5+0.5,0.5),
                "y": 0,
                "field_comp": None
            },
            "Roll Off Amplitude": {
                "z": np.arange(-900,900+0.5,0.5),
                "x": np.arange(-5,5+0.5,0.5),
                "y": 0
            }
        }

        self.visuals = VisualizationTabWidget()

        self.dockTree = QDockWidget("Explore Window",self)
        #todo: change qtreewidget to qtreeview to allow a better customization
        self.tree = ExploreTreeWidget(parent=self.dockTree)
        self.tree.customContextMenuRequested.connect(self.open_context)
        self.tree.noItemClicked.connect(self.tree_clicked_not_item)
        self.dockTree.setWidget(self.tree)

        self.dockSummary = QDockWidget("Summary Window",self)
        self.summary = SummaryWidget()
        self.dockSummary.setWidget(self.summary)
        
        self.dockCommand = QDockWidget("Command Line",self)
        self.command_line = QLineEdit()
        self.command_line.setContentsMargins(4, 0, 4, 4)
        self.dockCommand.setWidget(self.command_line)

        #todo: tentar depois deixar visuals dentro de dockwidget tambem, mas sem dar bugs
        self.setCentralWidget(self.visuals)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.dockTree)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.dockSummary)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea,self.dockCommand)

    

    def treeItemInfo(self, item: ExploreItem):

        #todo: fazer com que isso retorne dicionario, nao todos os items um, dois, tres
        
        if item.type() is ExploreItem.ContainerType:
            return {}
        
        elif item.type() is ExploreItem.IDType:

            id_name = item.text(0)
            id_dict = self.insertiondevices[id_name]
            return {"id_item": item, "id_name": id_name, "id_dict": id_dict}
        
        elif item.type() is ExploreItem.AnalysisType:
            info = self.treeItemInfo(item.parent())
            id_dict = info["id_dict"]

            info["analysis_item"] = item
            analysis = item.text(0)
            info["analysis"] = analysis
            analysis_dict = id_dict[analysis]
            info["analysis_dict"] = analysis_dict
            return info

        elif item.type() is ExploreItem.ResultType:
            info = self.treeItemInfo(item.parent())
            analysis_dict = info["analysis_dict"]

            info["result_item"] = item
            result = item.text(0)
            info["result"] = result
            result_arraynum = analysis_dict[result]
            info["result_arraynum"] = result_arraynum
            return info

    def countIDnames(self, IDname):
        models_names = [device[:-2] for device in self.insertiondevices]
        num = models_names.count(IDname)+1
        return num

    def analyzeItem(self, id_item: ExploreItem, analysis_actived: list):

        id_name = id_item.text(0)
        id_dict = self.insertiondevices[id_name]

        for calcAnalysis in analysis_actived:
            analysis = calcAnalysis.__name__.lstrip("calc").replace("_"," ")

            #todo: quando realiza a analise, mudar cursor para cursor de espera
            
            #todo: checar item, nao o texto
            if analysis not in id_dict:
                analysisType = ExploreItem.AnalysisType(analysis)
                analysis_item = ExploreItem(analysisType, id_item, [str(analysis), "Analysis"])
                analysis_item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight)
                if not id_item.isExpanded():
                    self.tree.expandItem(id_item)

                if analysis=="Cross Talk":
                    result_items = calcAnalysis(analysis_item, id_dict)
                    self.update_ids_dict_key(key=id_name, new_key=id_item.text(0))
                else:
                    result_items = calcAnalysis(analysis_item, id_dict, self.params[analysis])
                [item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight) for item in result_items]
            
            else:
                QMessageBox.warning(self,
                                    f"Analysis Warning",
                                    f"{analysis} of ({id_name}) already calculated!")

    def update_ids_dict_key(self, key, new_key):
        ids_dict = self.insertiondevices

        if key in ids_dict:
            value = ids_dict.pop(key)
            ids_dict[new_key] = value
            return True
        else:
            return False

    def drawItems(self, items: typing.List[ExploreItem]):

        visuals = self.visuals

        isModeAdd = not visuals.tabIcon(visuals.currentIndex()).isNull()

        if isModeAdd:
            chart = visuals.currentWidget()
            legend = chart.ax.legend_
            old_handles = legend.legendHandles
            old_labels = [label.get_text() for label in legend.get_texts()]
        else:
            chart = Canvas()
            chart.ax.grid(visible=True)
            old_handles, old_labels = [], []

        if len(items)==1:
            item, = items

            if item.type() is ExploreItem.AnalysisType:
                analysis_info = self.treeItemInfo(item)
                new_handles, new_labels = visuals.plotAnalysis(chart, analysis_info, isModeAdd)
                if not (new_handles or new_labels):
                    chart.deleteLater()
                    return False
            
            elif item.flag() is ExploreItem.ResultType.ResultArray:
                result_info = self.treeItemInfo(item)
                new_handles, new_labels = visuals.plotArray(chart, result_info, isModeAdd)

        elif len(items)==2:

            #*: por enquanto so' plotar dados de mesma analise e mesmo mapa de campo

            x_item, y_item = items
            x_info = self.treeItemInfo(x_item)
            y_info = self.treeItemInfo(y_item)
            new_handles, new_labels = visuals.plotPair(chart, x_info, y_info, isModeAdd)
        
        chart.ax.legend(old_handles+new_handles, old_labels+new_labels)

        #maneira de nao criar nada se nao e' selecionado nada nos menus de traj e integral
        # colocando grafico no self
        if not isModeAdd:
            visuals.addTab(chart, "Plot")
        
        # Trigger the canvas to update and redraw
        chart.draw()

        chart.fig.tight_layout()

        return True

    def displayTable(self, item: ExploreItem):
        
        # tabela: mapa de campo
        if item.flag() is ExploreItem.IDType.IDData:

            id_item = item
            id_dict = self.treeItemInfo(id_item)["id_dict"]

            ID_meas = id_dict["InsertionDeviceObject"]
            xyz_cols = ID_meas._raw_data[:,:3]
            bx_col = ID_meas._bx.T.reshape(-1,1)
            by_col = ID_meas._by.T.reshape(-1,1)
            bz_col = ID_meas._bz.T.reshape(-1,1)
            data = np.concatenate((xyz_cols,bx_col,by_col,bz_col),axis=1)
            header = ['X[mm]', 'Y[mm]', 'Z[mm]', 'Bx[T]', 'By[T]', 'Bz[T]']

        # tabela: analise
        elif item.type() is ExploreItem.AnalysisType:

            analysis_item = item
            analysis_dict = self.treeItemInfo(analysis_item)["analysis_dict"]

            data = []
            header = []
            for param, content in analysis_dict.items():
                if not isinstance(content, (int, float)):
                    header.append(param)
                    data.append(content)
            data = np.array(data).T

        # tabela: resultado
        elif item.flag() is ExploreItem.ResultType.ResultArray:

            result_item = item
            result_info = self.treeItemInfo(result_item)
            result = result_info["result"]
            result_array = result_info["result_arraynum"]

            data = result_array.reshape(-1,1)
            header = [result]

        #contrucao da tabela
        tabela = Table(data, header)

        # colocando tabela no visuals
        self.visuals.addTab(tabela, "Table")

    def open_context(self, pos):

        item = self.tree.itemAt(pos)
        position = self.mapToGlobal(pos)+QPoint(1,49)

        if item is not None:
            if item.flag() is ExploreItem.IDType.IDData:
                action = self.tree.menuContextID.exec(position) #todo: consertar pos
                if action:
                    if action.text()=="Save field map":
                        self.saveFieldMap(item)
                    elif action.text()=="Summary":
                        self.summaryID(item)

            elif item.flag() is ExploreItem.AnalysisType.Trajectory:
                action = self.tree.menuContextTraj.exec(position)
                if action:
                    self.saveTrajectory(item)

    def saveFieldMap(self, id_item: ExploreItem):

        id_info = self.treeItemInfo(id_item)
        id_name = id_info["id_name"]
        id_dict = id_info["id_dict"]
        ID = id_dict["InsertionDeviceObject"]
        file = id_dict["filename"]

        if id_name[-2:]==" C":
            i = file.find("Fieldmap")+len("Fieldmap")
            file = file[:i]+"Corrected"+file[i:]

        file_path, coords_range, saveForSpectra = SaveDialog.getSaveData(file,self)

        if file_path: #todo: checar se precisa usar isso aqui ou coloca so' direto la' no dialog
            px, py, pz = coords_range
            if saveForSpectra:
                print('salvou spectra')
                ID.save_fieldmap_spectra(file_path, px, py, pz,
                                         nproc=None, chunksize=100)
            else:
                print('salvou normal')
                ID.save_fieldmap(file_path, px, py, pz, header=None,
                                nproc=None, chunksize=100)

        

        # QMessageBox.information(self,
        #                         "Save Information",
        #                         f"The Field Map ({id_name}) was saved in the file directory:\n({filedir})")

    def saveTrajectory(self, item: ExploreItem):

        analysis_info = self.treeItemInfo(item)
        id_name = analysis_info["id_name"].replace(" ","_")
        analysis_dict = analysis_info["analysis_dict"]

        M_traj = [content for content in analysis_dict.values()
                    if not isinstance(content, (int, float))]
        M_traj = np.array(M_traj).T
        #M_traj.round(8)

        with open(f'trajectory_{id_name}.dat', 'w') as electrontraj:

            electrontraj.write("X[mm]\tY[mm]\tZ[mm]\tX'[rad]\tY'[rad]\tZ'[rad]\n")
            electrontraj.write(
                '----------------------------------------' +
                '----------------------------------------' +
                '----------------------------------------' +
                '----------------------------------------\n')

            line_fmt = '{0:g}\t{1:g}\t{2:g}\t{3:g}\t{4:g}\t{5:g}\n'

            for row in M_traj:
                x, y, z, dxds, dyds, dzds = row
                line = line_fmt.format(x, y, z, dxds, dyds, dzds)
                electrontraj.write(line)

    def summaryID(self, item: ExploreItem):

        id_dict = self.treeItemInfo(item)["id_dict"]
        ID = id_dict["InsertionDeviceObject"]
        
        dialog = SummaryDialog(ID) #passar o id_dict
        phaserr_dict = id_dict.get("Phase Error")
        if phaserr_dict:
            dialog.summary.update_phaserr(phaserr_dict["RMS [deg]"])
        integrals_dict = id_dict.get("Field Integrals")
        if integrals_dict:
            _, *integrals = integrals_dict.values()
            dialog.summary.update_integrals(integrals)
        dialog.exec()

    def update_summary(self, item: ExploreItem):
        id_dict = self.treeItemInfo(item).get("id_dict")
        if id_dict is None:
            if self.summary.ID is not None:
                self.summary.set_insertion_device(None)
                self.summary.update_phaserr(None)
                self.summary.update_integrals(None)
        else:
            ID = id_dict["InsertionDeviceObject"]
            if ID != self.summary.ID:
                self.summary.set_insertion_device(ID)
                phaserr_dict = id_dict.get("Phase Error")
                integrals_dict = id_dict.get("Field Integrals")

                self.summary.update_phaserr(phaserr_dict["RMS [deg]"] if phaserr_dict else None)

                if integrals_dict:
                    _, *integrals = integrals_dict.values()
                    self.summary.update_integrals(integrals)
                else:
                    self.summary.update_integrals(None)

    def tree_clicked_not_item(self):
        if self.summary.ID is not None:
            self.summary.set_insertion_device(None)
            self.summary.update_phaserr(None)
            self.summary.update_integrals(None)

    

class ProjectsTabWidget(BasicTabWidget):

    def __init__(self,parent):
        super().__init__(parent, leftSpace=22)

        self.setTabsClosable(False)

        # plus button: abrir novo projeto
        self.PlusButton = QToolButton()
        self.PlusButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.PlusButton.setIcon(QIcon("icons/icons/plus-button.png"))
        self.PlusButton.pressed.connect(self.addTab)
        self.setCornerWidget(self.PlusButton,corner=Qt.Corner.TopLeftCorner)

    # metodo widget redefinido apenas para impor que o retorno e' objeto do tipo ProjectWidget
    def widget(self, index: int) -> ProjectWidget:
        return super().widget(index)
    # metodo currentWidget redefinido apenas para impor que o retorno e' objeto do tipo ProjectWidget
    def currentWidget(self) -> ProjectWidget:
        return super().currentWidget()
    
    def addTab(self, widget='ProjectWidget', text='default'):
        
        if self.count() == 1:
            self.setTabsClosable(True)

        if widget=='ProjectWidget':
            widget=ProjectWidget()
        if text=='default':
            text=f"Project {self.count()+1}"
        
        i = super().addTab(widget=widget,text=text)

        # *: o abaixo sera feito na main_window, apos conectar com sinal
        #self.widget(i).tree.itemClicked.connect(self.on_item_clicked)

        return i

    def closeTab(self, i):
        super().closeTab(i)
        
        #because of the deleteLater behaviour, the count method still counts the tab whom we use deleteLater.
        #So to check if there is only one remaining tab, we still count the "deleted" and check if count==2
        if self.count() == 2:
            self.setTabsClosable(False)
