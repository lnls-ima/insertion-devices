import typing

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

    def changeIcon(self):

        index = self.tabBar().tabAt(self.tabPos)

        if self.actionActiveAdd.isChecked():
            self.setTabIcon(index, QIcon("icons\icons\plus-white.png"))
        else:
            self.setTabIcon(index, QIcon(None))


    def plotArray(self, chart: Canvas, result, analysis_dict):

        result_line = chart.ax.plot(analysis_dict[result])

        plot_text = [result, "Values", "Indexes"]
        legend_info = [result_line, [result]]

        return plot_text, legend_info
    
    def plotPair(self, chart: Canvas, id_name, x, x_label, y, y_label):

        line = chart.ax.plot(x,y)

        x_label = x_label[:x_label.find("[")-1]
        y_label = y_label[:y_label.find("[")-1]

        plot_text = [f"{y_label} vs {x_label}", y_label, x_label]
        legend_info = [line, [f"{y_label} vs {x_label} of {id_name}"]]

        return plot_text, legend_info

    def plotAnalysis(self, chart: Canvas, id_name, analysisType: ExploreItem.AnalysisType, analysis_dict):

        if analysisType is ExploreItem.AnalysisType.MagneticField:
            
            z, *B = list(analysis_dict.values())
            B = np.array(B).T

            B_lines = chart.ax.plot(z,B)

            plot_text = "Magnetic Field", "Bx, By, Bz (T)", "z (mm)"
            legend_info = B_lines, [f"Bx of {id_name}",f"By of {id_name}",f"Bz of {id_name}"]
            
        if analysisType is ExploreItem.AnalysisType.Trajectory:
            
            x, y, z, dxds, dyds, dzds = analysis_dict.values()
            x_y = np.array([x,y]).T
            dxds_dyds = np.array([dxds,dyds]).T

            menuIntegral = QMenu(self)
            menuIntegral.addAction("Position Deviation")
            menuIntegral.addAction("Angular Deviation")
            #todo: consertar pos para pegar canto superior direito do item
            action = menuIntegral.exec(QCursor.pos())
            if action is None:
                return None
            
            dflt_x_label = "z (mm)"
            if action.text()=="Position Deviation":
                traj_line = chart.ax.plot(z,x_y)
                dflt_y_label = "x, y (mm)"
                dflt_title = "Trajectory"
                Label =  [f"x of {id_name}", f"y of {id_name}"]
                
            elif action.text()=="Angular Deviation":
                traj_line = chart.ax.plot(z,dxds_dyds)
                dflt_y_label = "x', y' (rad)"
                dflt_title = "Trajectory - Angular Deviation"
                Label = [f"x' of {id_name}", f"y' of {id_name}"]

            plot_text = dflt_title, dflt_y_label, dflt_x_label
            legend_info = traj_line, Label
            
        if  analysisType is ExploreItem.AnalysisType.PhaseError:

            z_poles, phaserr, phaserr_rms = analysis_dict.values()

            phaserr_line = chart.ax.plot(np.arange(1,len(phaserr)+1), phaserr,'o-')
            rms_line = chart.ax.plot([1,len(phaserr)], [phaserr_rms, phaserr_rms],'--',c=phaserr_line[0].get_color())
            dflt_title = "Phase Error"
            dflt_x_label = "Pole"
            dflt_y_label = "Phase Error (deg)"

            plot_text = dflt_title, dflt_y_label, dflt_x_label
            legend_info = phaserr_line+rms_line, [f"Phase Error of {id_name}",f"Phase Err RMS of {id_name}"]
            
        if analysisType is ExploreItem.AnalysisType.Integrals:

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
            
            dflt_x_label = "z (mm)"
            if action.text()=="First Integral":
                integral_line = chart.ax.plot(z,ib)
                dflt_y_label = "ibx, iby, ibz (G.cm)"
                dflt_title = "Field Integral - First"
                Label = [f"ibx of {id_name}", f"iby of {id_name}", f"ibz of {id_name}"]
                
            elif action.text()=="Second Integral":
                integral_line = chart.ax.plot(z,iib)
                dflt_y_label = "iibx, iiby, iibz (kG.cm2)"
                dflt_title = "Field Integral - Second"
                Label = [f"iibx of {id_name}", f"iiby of {id_name}", f"iibz of {id_name}"]

            plot_text = dflt_title, dflt_y_label, dflt_x_label
            legend_info = integral_line, Label
        
        return plot_text, legend_info
    

    def drawTableCols(self, indexes):

        plotColumns = indexes[0].column() != indexes[-1].column()
        modelTable = self.currentWidget().model()

        chart = Canvas()
        chart.ax.grid(visible=True)

        if plotColumns:
            colx = indexes[0].column()
            x_label = modelTable._header[colx]
            x_label = x_label[:x_label.find("[")]
            coly = indexes[-1].column()
            y_label = modelTable._header[coly]
            y_label = y_label[:y_label.find("[")]

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

        self.addTab(chart, "plot")

        chart.fig.tight_layout()
