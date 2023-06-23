
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction, QIcon, QCursor

from.basics import BasicTabWidget
from .visual_elements import Canvas
from .explore_window import ExploreItem

import numpy as np



class VisualizationTabWidget(BasicTabWidget):

    def __init__(self):
        super().__init__(leftSpace=-1)

        self.actionActiveAdd = QAction("Add Mode")
        self.actionActiveAdd.setCheckable(True)
        self.actionActiveAdd.setVisible(False)
        self.actionActiveAdd.triggered.connect(self.changeIcon)
        self.menuContext.addAction(self.actionActiveAdd)

    def isModeAdd(self):
        return not self.tabIcon(self.currentIndex()).isNull()
        
    
    def exec_context_menu(self, pos):

        self.tabPos = pos
        index = self.tabBar().tabAt(self.tabPos)

        if isinstance(self.widget(index),Canvas):
            self.actionActiveAdd.setVisible(True)

            # sincronizar checkstate da action com icone na tab clicada
            if self.tabIcon(index).isNull():
                self.actionActiveAdd.setChecked(False)
            else:
                self.actionActiveAdd.setChecked(True)
        else:
            self.actionActiveAdd.setVisible(False)
        
        super().exec_context_menu(self.tabPos)

    def changeIcon(self, change):

        #index = self.tabBar().tabAt(self.tabPos)
        index = self.currentIndex()

        if change:
            self.setTabIcon(index, QIcon("icons\icons\plus-white.png"))
        else:
            self.setTabIcon(index, QIcon(None))


    def plotArray(self, chart: Canvas, result_info, addMode=False):

        result = result_info["result"]
        result_array = result_info["result_arraynum"]

        result_line = chart.ax.plot(result_array)

        if addMode:
            chart.ax.set_title("")
        else:
            chart.ax.set_title(result)
        chart.ax.set_ylabel("Values")
        chart.ax.set_xlabel("Indexes")
        
        legend_info = [result_line, [result]]

        return legend_info
    
    def plotPair(self, chart: Canvas, x_info, y_info, addMode=False):

        id_name = x_info["id_name"]
        x_label = x_info["result"]
        x = x_info["result_arraynum"]
        
        y_label = y_info["result"]
        y = y_info["result_arraynum"]
        
        line = chart.ax.plot(x,y)

        if addMode:
            chart.ax.set_title("")
            chart.ax.set_ylabel("")
            chart.ax.set_xlabel("")
        else:
            chart.ax.set_ylabel(y_label)
            chart.ax.set_xlabel(x_label)

            x_label = x_label[:x_label.find("[")-1]
            y_label = y_label[:y_label.find("[")-1]
            chart.ax.set_title(f"{y_label} vs {x_label}")

        legend_info = line, [f"{y_label} vs {x_label} of {id_name}"]

        return legend_info

    def plotAnalysis(self, chart: Canvas, analysis_info, addMode=False):

        #todo: no futuro, avaliar se uso analysis ou analysis_item para fazer as condicoes
        id_name = analysis_info["id_name"]
        analysis_item = analysis_info["analysis_item"]
        analysis_dict = analysis_info["analysis_dict"]
        titleyxlabel = []

        if analysis_item.flag() is ExploreItem.AnalysisType.MagneticField:
            
            x, y, z, *B = list(analysis_dict.values())
            B = np.array(B).T

            if not isinstance(z, (int, float)):
                B_lines = chart.ax.plot(z,B)
                titleyxlabel.extend(["Magnetic Field", "Bx, By, Bz (T)", "z (mm)"])
            elif not isinstance(x, (int, float)):
                B_lines = chart.ax.plot(x,B)
                titleyxlabel.extend(["Magnetic Field", "Bx, By, Bz (T)", "x (mm)"])
            elif not isinstance(y, (int, float)):
                B_lines = chart.ax.plot(y,B)
                titleyxlabel.extend(["Magnetic Field", "Bx, By, Bz (T)", "y (mm)"])
            else:
                return [], []
            
            legend_info = B_lines, [f"Bx of {id_name}",f"By of {id_name}",f"Bz of {id_name}"]

        if analysis_item.flag() is ExploreItem.AnalysisType.Trajectory:
            
            x, y, z, dxds, dyds, dzds = analysis_dict.values()
            x_y = np.array([x,y]).T
            dxds_dyds = np.array([dxds,dyds]).T

            menuIntegral = QMenu(self)
            menuIntegral.addAction("Position Deviation")
            menuIntegral.addAction("Angular Deviation")
            #todo: consertar pos para pegar canto superior direito do item
            action = menuIntegral.exec(QCursor.pos())
            if action is None:
                return [], []
            
            if action.text()=="Position Deviation":
                traj_line = chart.ax.plot(z,x_y)
                titleyxlabel.extend(["Trajectory","x, y (mm)"])
                Label =  [f"x of {id_name}", f"y of {id_name}"]
                
            elif action.text()=="Angular Deviation":
                traj_line = chart.ax.plot(z,dxds_dyds)
                titleyxlabel.extend(["Trajectory - Angular Deviation","x', y' (rad)"])
                Label = [f"x' of {id_name}", f"y' of {id_name}"]

            titleyxlabel.append("z (mm)")
            legend_info = traj_line, Label

        if  analysis_item.flag() is ExploreItem.AnalysisType.PhaseError:

            z_poles, phaserr, phaserr_rms = analysis_dict.values()

            #phaserr_line = chart.ax.plot(np.arange(1,len(phaserr)+1), phaserr,'o-')
            phaserr_line = chart.ax.plot(z_poles, phaserr,'o-')
            #rms_line = chart.ax.plot([1,len(phaserr)], [phaserr_rms, phaserr_rms],'--',c=phaserr_line[0].get_color())
            rms_line = chart.ax.plot([z_poles[0],z_poles[-1]], [phaserr_rms, phaserr_rms],'--',c=phaserr_line[0].get_color())


            titleyxlabel.extend(["Phase Error","Phase Error (deg)","z poles (mm)"])
            legend_info = phaserr_line+rms_line, [f"Phase Error of {id_name}",f"Phase Err RMS of {id_name}"]

        if analysis_item.flag() is ExploreItem.AnalysisType.Integrals:

            z, ibx, iby, ibz, iibx, iiby, iibz = analysis_dict.values()
            ib = np.array([ibx, iby, ibz]).T
            iib = np.array([iibx, iiby, iibz]).T

            menuIntegral = QMenu(self)
            menuIntegral.addAction("First Integral")
            menuIntegral.addAction("Second Integral")
            #todo: consertar pos para pegar canto superior direito do item
            action = menuIntegral.exec(QCursor.pos())
            if action is None:
                return [], []
            
            if action.text()=="First Integral":
                integral_line = chart.ax.plot(z,ib)
                titleyxlabel.extend(["Field Integral - First","ibx, iby, ibz (G.cm)"])
                Label = [f"ibx of {id_name}", f"iby of {id_name}", f"ibz of {id_name}"]
                
            elif action.text()=="Second Integral":
                integral_line = chart.ax.plot(z,iib)
                titleyxlabel.extend(["Field Integral - Second","iibx, iiby, iibz (kG.cm2)"])
                Label = [f"iibx of {id_name}", f"iiby of {id_name}", f"iibz of {id_name}"]

            titleyxlabel.append("z (mm)")
            legend_info = integral_line, Label

        if analysis_item.flag() is ExploreItem.AnalysisType.RollOffAmp:

            x, y, *roa = analysis_dict.values()
            roa = np.array(roa).T

            roa_lines = chart.ax.plot(x,roa)
            titleyxlabel.extend(["Roll Off Amplitude", "ROAx, ROAy, ROAz", "x (mm)"])
            legend_info = roa_lines, [f"ROAx of {id_name}",f"ROAy of {id_name}",f"ROAz of {id_name}"]

            
        if addMode:
            chart.ax.set_title("")
            chart.ax.set_ylabel("")
            chart.ax.set_xlabel("")
        else:
            chart.ax.set_title(titleyxlabel[0])
            chart.ax.set_ylabel(titleyxlabel[1])
            chart.ax.set_xlabel(titleyxlabel[2])

        return legend_info
    

    def drawTableCols(self, indexes):

        plotColumns = indexes[0].column() != indexes[-1].column()
        modelTable = self.currentWidget().model()

        chart = Canvas()
        chart.ax.grid(visible=True)

        if plotColumns:
            colx = indexes[0].column()
            x_label = modelTable._header[colx]
            coly = indexes[-1].column()
            y_label = modelTable._header[coly]
            chart.ax.set_xlabel(x_label)
            chart.ax.set_ylabel(y_label)

            #todo: talvez passar essa parte de coleta dos dados para algum metodo de Table
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
            x_label = x_label[:x_label.find("[")]
            y_label = y_label[:y_label.find("[")]
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

        self.addTab(chart, "plot")

        chart.fig.tight_layout()
