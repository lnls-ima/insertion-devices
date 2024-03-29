import os
from typing import List, Dict, Literal

from  PyQt6.QtWidgets import   (QMainWindow,
                                QLineEdit,
                                QToolButton,
                                QDockWidget,
                                QMessageBox,
                                QMenu,
                                QDialog)
from   PyQt6.QtGui    import    QIcon, QCursor
from   PyQt6.QtCore   import   Qt, QPoint

from imaids.insertiondevice import InsertionDeviceData

from .basics import BasicTabWidget
from .explore_window import ExploreItem, ExploreTreeWidget
from .visual_elements import Canvas, Table
from .visualization_window import VisualizationTabWidget
from .save_dialog import SaveDialog
from .modeldata_dialog import ModelDataDialog
from .summary_dialog import SummaryDialog, SummaryWidget
from .dialog_operation import OperationAnalysisDialog
from . import get_path

import numpy as np



class ProjectWidget(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.insertiondevices = {}
        self.DftIDlabels = {}
        self.operations = {}
        self.params = {
            "Cross Talk": {
                "angles": {
                    "angxy":0.15,
                    "angxz":-0.21,
                    "angyx":-0.01,
                    "angyz":-0.02,
                    "angzx":0.01,
                    "angzy":-0.74
                },
                "cross_talk":{
                    "ky": [-0.006781104386361973,-0.01675247563602003,7.568631573320983e-06],
                    "kz": [-0.006170829583118335,-0.016051627320478382,7.886674928668737e-06]
                }
            },
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
                "skip_poles": 0,
                "zmin": -530,
                "zmax": 550,
                "field_comp": None
            },
            "Cumulative Integrals": {
                "z_list": np.arange(-900,900+0.5,0.5),
                "x": 0,
                "y": 0,
                "field_list": None,
                "nproc": None,
                "chunksize": 100
            },
            "Field Integrals vs X": {
                "z": np.arange(-900,900+0.5,0.5),
                "x": np.arange(-5,5+1,1),
                "y": 0
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
            },
            "Harmonics Tuning": {
                "harm_lim": [1,5],
                "K_lim": [0,4.5],
                "nr_points": 100,
                "I_b": 100,
                "beta": [17.2,3.6],
                "dist": 25,
                "ret_slit": [0.05,0.05]
            },
            "Brilliance": {
                "harm_lim": [1,5],
                "K_lim": [0,4.5],
                "nr_points": 100,
                "I_b": 100,
                "beta": [17.2,3.6],
                "dist": 25
            },
            "Flux Density": {
                "energy_lim": 'default',
                "energy_step": 1,
                "I_b": 100,
                "beta": [17.2,3.6],
                "dist": 25
            }
        }

        userhome = os.path.expanduser('~')
        self.lastpath = f"{userhome}\\Documents"

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

        self.visuals.dockFigOptions.setHidden(True)

        self.dockCommand = QDockWidget("Command Line",self)
        self.command_line = QLineEdit()
        self.command_line.setContentsMargins(3, 0, 3, 3)
        self.dockCommand.setWidget(self.command_line)

        #todo: tentar depois deixar visuals dentro de dockwidget tambem, mas sem dar bugs
        self.setCentralWidget(self.visuals)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.dockTree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.tree.dockOperations)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.dockSummary)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.visuals.dockFigOptions)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea,self.dockCommand)



    def treeItemInfo(self, item: ExploreItem) -> Dict[Literal['ctn_item',
                                                              'id_item','id_name','id_dict',
                                                              'analysis_item','analysis','analysis_dict',
                                                              'result_item','result','result_arraynum'],object]:
        """
        Give all necessary information about an Explore Item:
            {ctn_item,
             id_item, id_name, id_dict,
             analysis_item, analysis, analysis_dict,
             result_item, result, result_arraynum}
        """

        #todo: fazer com que isso retorne dicionario, nao todos os items um, dois, tres
        
        if item.type() is ExploreItem.ContainerType:
            return {"ctn_item": item}
        
        elif item.type() is ExploreItem.IDType:
            info = self.treeItemInfo(item.parent())

            id_name = item.text(0)
            id_dict = self.insertiondevices[id(item)]

            info.update({"id_item": item, "id_name": id_name, "id_dict": id_dict})
            return info
        
        elif item.type() is ExploreItem.AnalysisType:
            info = self.treeItemInfo(item.parent())

            analysis = item.text(0)
            try:
                id_dict = info["id_dict"]
                analysis_dict = id_dict[analysis]
            except:
                analysis_dict = self.operations[id(item)]
            info.update({"analysis_item": item, "analysis": analysis,
                         "analysis_dict": analysis_dict})
            return info

        elif item.type() is ExploreItem.ResultType:
            info = self.treeItemInfo(item.parent())

            result = item.text(0)
            try:
                analysis_dict = info["analysis_dict"]
                result_arraynum = analysis_dict[result]
            except:
                result_arraynum = self.operations[id(item)]

            info.update({"result_item": item, "result": result,
                         "result_arraynum": result_arraynum})
            return info

    def analyzeItem(self, ID_item: ExploreItem, analysis_actived: list):
        mainwindow = self.parent().parent().parent()

        id_name = ID_item.text(0)
        id_dict = self.insertiondevices[id(ID_item)]

        for calcAnalysis in analysis_actived:
            analysis = calcAnalysis.__name__.lstrip("calc").replace("_"," ")

            #todo: quando realiza a analise, mudar cursor para cursor de espera
            
            #todo: checar item, nao o texto

            replace = False
            add = False

            if analysis in id_dict:
                messagebox = QMessageBox(QMessageBox.Icon.Question,
                                         f"Analysis Warning",
                                         f"{analysis} of ({id_name}) already calculated! Do you want add a new {analysis}, replace the last one done or just ignore?")
                messagebox.addButton("Add",QMessageBox.ButtonRole.AcceptRole)
                messagebox.addButton("Replace", QMessageBox.ButtonRole.YesRole)
                btnIgnore = messagebox.addButton("Ignore",QMessageBox.ButtonRole.RejectRole)
                messagebox.setDefaultButton(btnIgnore)
                
                btn = messagebox.exec()
                if btn==0:
                    add = True
                elif btn==1:
                    replace = True
            
            if (analysis not in id_dict) or add or replace:

                items = ID_item.children()
                labels = [label for label in items.keys() if analysis in label]
                num = len(labels)

                analysis_label = analysis if not add else analysis+f" {num+1}"
                
                if replace:
                    analysis_label = analysis if num==1 else analysis+f" {num}"
                    self.insertiondevices[id(ID_item)].pop(analysis_label)
                    items.pop(analysis_label).delete()

                analysisType = ExploreItem.AnalysisType(analysis)
                analysis_item = ExploreItem(analysisType, ID_item, [analysis_label, "Analysis"])
                analysis_item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight)
                if not ID_item.isExpanded():
                    self.tree.expandItem(ID_item)

                #mainwindow.statusbar.showMessage(f"Running {analysis}",1000)
                result_items = calcAnalysis(analysis_item, id_dict, self.params[analysis])
                if analysis=="Roll Off Peaks" and not result_items:
                    analysis_item.delete()
                    QMessageBox.warning(self,
                                "Roll Off Warning",
                                f"There are no peaks in the greater magnetic field, Bx or By, of ({id_name}). Roll Off for Peaks cannot be calculated!")
                #mainwindow.statusbar.showMessage(f"{analysis} done!",1000)
                # self.update_ids_dict_key(key=id_name, new_key=ID_item.text(0))
                [item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight) for item in result_items]

    #todo: implementar delecao de analise customizada
    def operateItems(self, operation: str, items: List[ExploreItem]):
        sign = "+" if "+" in operation else "-"
        infos = [self.treeItemInfo(item) for item in items]

        rtArray = ExploreItem.ResultType.ResultArray
        rtNumber = ExploreItem.ResultType.ResultNumeric

        #Operate analyses
        isAnalysis = infos[0].get("result") is None
        if isAnalysis:
            print('operate analyses')
            dicts = [info["analysis_dict"] for info in infos]
            keys = dicts[0].keys()
            values = [dirct.values() for dirct in dicts]
            names = [info["analysis"] for info in infos]
            
            if any(analysis != names[0] for analysis in names):
                QMessageBox.warning(self,
                                    "Operation Error",
                                    "Analyses of different types cannot be operated!")
                return False
            
            answer, isUnchanged = OperationAnalysisDialog.getResultsUnchanged(infos[0],self)
            if answer == QDialog.DialogCode.Rejected:
                return False

            new_dict = {}
            result_items = []
            for key, *value in zip(keys,*values):
                
                if any(type(val_i) != type(value[0]) for val_i in value):
                    QMessageBox.warning(self,
                                        "Operation Error",
                                        "Analyses have different result types!")
                    return False
                if any(val_i.size != value[0].size for val_i in value):
                    QMessageBox.warning(self,
                                        "Operation Error",
                                        "The sizes of the arrays are different, operation cannot be done!")
                    return False
                
                op_tip = operation
                for i in range(len(items)):
                    operation = operation.replace(f"A{i}",f"value[{i}]")
                    op_tip.replace(f"A{i}",f"")
                new_dict[key] = dicts[0][key] if isUnchanged[key] else eval(operation)
                    
                isArray = type(dicts[0][key])==np.ndarray
                resultType, resultContent = (rtArray, "List") if isArray else (rtNumber, f"{new_dict[key]:.1f}")
                item = ExploreItem(resultType, [key, resultContent])
                item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight)
                result_items.append(item)
            
            container = self.tree.treeOperations.topLevelItem(0)
            analysisType = ExploreItem.AnalysisType(names[0])
            analysis_item = ExploreItem(analysisType, container, [infos[0]["analysis"], "Analysis"])
            msg = f"{sign}".join([f"({info.get('id_name')}/{info['analysis']})" for info in infos])
            analysis_item.setStatusTip(0,msg)
            analysis_item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight)
            analysis_item.addChildren(result_items)

            self.operations[id(analysis_item)] = new_dict
        
        # Operate results
        else:
            arraynums = [info["result_arraynum"] for info in infos]

            if any(type(arraynum_i) != type(arraynums[0]) for arraynum_i in arraynums):
                QMessageBox.warning(self,
                                    "Operation Error",
                                    "Different types of results cannot be operated!")
                return False
            if any(arraynum.size != arraynums[0].size for arraynum in arraynums):
                QMessageBox.warning(self,
                                    "Operation Error",
                                    "The sizes of the arrays are different, operation cannot be done!")
                return False

            for i in range(len(items)):
                operation = operation.replace(f"A{i}",f"arraynums[{i}]")
            new_arraynum = eval(operation)

            isArray = type(arraynums[0])==np.ndarray
            resultType, resultContent = (rtArray, "List") if isArray else (rtNumber, f"{new_arraynum:.1f}")

            container = self.tree.treeOperations.topLevelItem(1)
            equals = all(info["result"]==infos[0]["result"] for info in infos)
            resultName = infos[0]["result"] if equals else "Result"
            result_item = ExploreItem(resultType, container, [resultName, resultContent])
            msg = f"{sign}".join([f"({info.get('id_name')}/{info['analysis']}/{info['result']})" for info in infos])
            result_item.setStatusTip(0,msg)
            result_item.setTextAlignment(1,Qt.AlignmentFlag.AlignRight)

            self.operations[id(result_item)] = new_arraynum

        if not container.isExpanded():
            self.tree.treeOperations.expandItem(container)

        self.tree.dockOperations.setVisible(True)

    def drawItems(self, items: List[ExploreItem]):

        visuals = self.visuals

        isModeAdd = not visuals.tabIcon(visuals.currentIndex()).isNull()

        if isModeAdd:
            chart = visuals.currentWidget()
        else:
            chart = Canvas(parent=self.visuals)
            chart.ax.grid(visible=True)

        if len(items)==1:
            item, = items

            if item.type() is ExploreItem.AnalysisType:
                analysis_info = self.treeItemInfo(item)
                plot = visuals.plotAnalysis(chart, analysis_info, isModeAdd)
                if not plot:
                    return False
            
            elif item.flag() is ExploreItem.ResultType.ResultArray:
                result_info = self.treeItemInfo(item)
                visuals.plotArray(chart, result_info, isModeAdd)

        elif len(items)==2:

            #*: por enquanto so' plotar dados de mesma analise e mesmo mapa de campo

            x_item, y_item = items
            x_info = self.treeItemInfo(x_item)
            y_info = self.treeItemInfo(y_item)
            plot = visuals.plotPair(chart, x_info, y_info, isModeAdd)
            if not plot:
                return False
        
        labels0 = [line.get_label()[0] for line in chart.ax.get_lines()]
        if len(labels0) != labels0.count("_"):
            chart.ax.legend()

        #maneira de nao criar nada se nao e' selecionado nada nos menus de traj e integral
        # colocando grafico no self
        if not isModeAdd:
            visuals.addTab(chart, "Plot")
        
        # Trigger the canvas to update and redraw
        chart.draw()

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

            header = []
            data = []
            for param, content in analysis_dict.items():
                if not isinstance(content, (int, float)):
                    header.append(param)
                    data.append(content)

            if "ROP" in header[1]:

                menuPeaks = QMenu(self)
                actionx = menuPeaks.addAction("x component")
                actiony = menuPeaks.addAction("y component")
                actionz = menuPeaks.addAction("z component")
                action = menuPeaks.exec(QCursor.pos())
                if action is None:
                    return False
                i = [actionx, actiony, actionz].index(action)

                x = data[0].reshape(1,-1)
                rop = data[i+1].T
                data = np.append(x,rop,axis=0)

                header = ["x [mm]"]
                N = rop.shape[0]
                coord = ["x","y","z"][i]
                header.extend([f"ROP{i}{coord} [%]"
                               for i in range(1,N+1)])

            data = np.array(data).T

        # tabela: resultado
        elif item.type() is ExploreItem.ResultType:

            result_item = item
            result_info = self.treeItemInfo(result_item)
            result = result_info["result"]
            array_num = result_info["result_arraynum"]

            rtArray = ExploreItem.ResultType.ResultArray
            rtNumber = ExploreItem.ResultType.ResultNumeric

            if item.flag() is rtArray:
                cols = 1 if array_num.ndim==1 else array_num.shape[1]

                data = array_num.reshape(-1,cols)
                if "ROP" in result:
                    coord = result[3]
                    header = [f"ROP{i}{coord} [%]" for i in range(1,cols+1)]
                else:
                    header = [result]*cols
            
            elif item.flag() is rtNumber:
        
                data = np.array([[array_num]])
                header = [result]

        #contrucao da tabela
        tabela = Table(data, header)

        # colocando tabela no visuals
        self.visuals.addTab(tabela, "Table")

    def solveModel(self, item: ExploreItem):
        id_dict = self.treeItemInfo(item)["id_dict"]
        ID = id_dict["InsertionDeviceObject"]

        ID.solve()
        print('model solved')

        item.setIcon(0,QIcon(get_path('icons','model-tick.png')))

    #todo: passar pra tree
    def open_context(self, pos):

        item = self.tree.itemAt(pos)
        position = self.mapToGlobal(pos)+QPoint(1,49)

        if item:
            if item.type() is ExploreItem.IDType:
                if item.flag() is ExploreItem.IDType.IDData:
                    action = self.tree.menuContextIDData.exec(position) #todo: consertar pos
                    if action:
                        if action.text()=="Rename ...":
                            self.tree.rename_item(item)
                        elif action.text()=="Summary ...":
                            self.summaryID(item)
                        elif action.text()=="Save field map ...":
                            self.saveFieldMap(item) #todo: passar pra ExploreItem
                        elif action.text()=="Delete":
                            self.deleteItem(item)
                else:
                    action = self.tree.menuContextIDModel.exec(position)
                    if action:
                        if action.text()=="Rename ...":
                            self.tree.rename_item(item)
                        elif action.text()=="Delete":
                            self.deleteItem(item)

            elif item.flag() is ExploreItem.AnalysisType.Trajectory:
                action = self.tree.menuContextTraj.exec(position)
                if action:
                    if action.text()=="Save Trajectory":
                        self.saveTrajectory(item)
                    elif action.text()=="Delete":
                        self.deleteItem(item)

            elif item.type() is ExploreItem.AnalysisType:
                action = self.tree.menuContextAnalysis.exec(position)
                if action:
                    self.deleteItem(item)

    def saveFieldMap(self, id_item: ExploreItem):

        id_info = self.treeItemInfo(id_item)
        id_name = id_info["id_name"]
        id_dict = id_info["id_dict"]
        ID = id_dict["InsertionDeviceObject"]
        file = id_dict.get("filename")

        correct = id_dict.get("Cross Talk")
        if file and correct and ("Corrected" not in file):
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

    def modelToData(self, id_item: ExploreItem):
        
        id_info = self.treeItemInfo(id_item)
        id_dict = id_info["id_dict"]
        ID_model = id_dict["InsertionDeviceObject"]

        coords_range = ModelDataDialog.getDataGrid(self)

        if coords_range:
            px, py, pz = coords_range

            ID_data = InsertionDeviceData.from_model(ID_model,px,py,pz)
            ID_data._nr_periods = ID_model.nr_periods
            ID_data._period_length = ID_model.period_length
            ID_data._gap = ID_model.gap

            name = id_info["id_name"]
            ID_item = self.tree.insertID(IDType=ExploreItem.IDType.IDData,
                                        ID=ID_data, correct=True, name=name)
            self.insertiondevices[id(ID_item)] = {"InsertionDeviceObject": ID_data,
                                                    "item": ID_item,
                                                    "Cross Talk": True}

    def deleteItem(self, item: ExploreItem):
        if item in self.tree.itemsSelected:
            self.tree.itemsSelected.remove(item)
        if item.type() is ExploreItem.IDType:
            self.insertiondevices.pop(id(item))
            self.DftIDlabels.pop(id(item))
        elif item.type() is ExploreItem.AnalysisType:
            info = self.treeItemInfo(item)
            info["id_dict"].pop(info["analysis"])
        item.delete()

    #todo: mudar para exibir o widget que ja existe no dock
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

    def tree_clicked_not_item(self):
        if self.summary.ID is not None:
            self.summary.update_ID(None)
            self.summary.update_phaserr(None)
            self.summary.update_integrals(None)

    

class ProjectsTabWidget(BasicTabWidget):

    def __init__(self,parent):
        super().__init__(parent, leftSpace=22)

        self.setTabsClosable(False)

        # plus button: abrir novo projeto
        self.PlusButton = QToolButton()
        self.PlusButton.setShortcut("+")
        self.PlusButton.setToolTip("New Project (+)")
        self.PlusButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.PlusButton.setIcon(QIcon(get_path('icons','plus-button.png')))
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

        answer = QMessageBox.question(self,
                                      "Close Confirmation",
                                      "Are you sure you want to close a project?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)

        if answer == QMessageBox.StandardButton.Yes:
            super().closeTab(i)
        
            #because of the deleteLater behaviour, the count method still counts the tab whom we use deleteLater.
            #So to check if there is only one remaining tab, we still count the "deleted" and check if count==2
            if self.count() == 2:
                self.setTabsClosable(False)
