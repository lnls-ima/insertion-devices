
from PyQt6.QtWidgets import QMenu, QWidget, QDockWidget, QWidget, QVBoxLayout
from PyQt6.QtGui import QAction, QIcon, QCursor

from.basics import BasicTabWidget
from .visual_elements import Canvas
from widgets import _mpl_layout_mod as layout_mod
from .explore_window import ExploreItem

import numpy as np
from matplotlib.backends.qt_editor import _formlayout as _mpl_formlayout



class VisualizationTabWidget(BasicTabWidget):

    def __init__(self):
        super().__init__(leftSpace=-1)

        _mpl_formlayout.fedit = self.fedit

        self.dockFigOptions = QDockWidget("Figure Options",self.parent())
        widgetFigOptions = QWidget() #todo: set frame
        self.vboxFigOptions = QVBoxLayout(widgetFigOptions)
        self.dockFigOptions.setWidget(widgetFigOptions)

        self.dictFigOptions = {}
        self.currentFigOptions = None

        self.currentChanged.connect(self.hideFigOptions)

        self.actionActiveAdd = QAction("Add Mode")
        self.actionActiveAdd.setToolTip(
            "Change canvas mode.<br>"+
            "<b>Plus:</b> This canvas accepts new plots<br>"+
            "<b>No plus:</b> This canvas don't accept new plots")
        self.actionActiveAdd.setCheckable(True)
        self.actionActiveAdd.setVisible(False)
        self.actionActiveAdd.triggered.connect(self.changeIcon)
        self.menuContext.addAction(self.actionActiveAdd)


    def fedit(self, data, title="", comment="", icon=None, parent=None, apply=None):
        canvas = self.currentWidget()
        figOptions = self.dictFigOptions[id(canvas)]
        if figOptions:
            if not self.dockFigOptions.isVisible():
                if figOptions.isHidden():
                    figOptions.setHidden(False)
                    self.currentFigOptions = figOptions
                self.dockFigOptions.setVisible(True)
        else:
            formwidget = layout_mod.fedit(data, title, comment, icon, parent, apply)
            self.vboxFigOptions.addWidget(formwidget)
            self.currentFigOptions = formwidget
            self.dictFigOptions[id(canvas)]=formwidget
            self.dockFigOptions.setVisible(True)

    def hideFigOptions(self, i):
        if i!=-1:
            self.dockFigOptions.setVisible(False)
            if self.currentFigOptions:
                self.currentFigOptions.setHidden(True)

    def addTab(self, widget: QWidget, text: str) -> int:
        if isinstance(widget,Canvas):
            self.dictFigOptions[id(widget)] = None
        return super().addTab(widget, text)

    def closeTab(self, i):
        currentWidget = self.widget(i)
        if isinstance(currentWidget,Canvas):
            figOptions = self.dictFigOptions.pop(id(currentWidget))
            if figOptions:
                figOptions.deleteLater()
                self.dockFigOptions.setVisible(False)
            if figOptions==self.currentFigOptions:
                self.currentFigOptions = None
        return super().closeTab(i)

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

        chart.ax.plot(result_array,label=result)

        if addMode:
            chart.ax.set_title("")
        else:
            chart.ax.set_title(result)
        chart.ax.set_ylabel("Values")
        chart.ax.set_xlabel("Indexes")

    def plotPair(self, chart: Canvas, x_info, y_info, addMode=False):

        id_name = x_info["id_name"]
        x_label = x_info["result"]
        x = x_info["result_arraynum"]
        
        y_label = y_info["result"]
        y = y_info["result_arraynum"]
        
        line, = chart.ax.plot(x,y)

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
            line.set_label(f"{y_label} vs {x_label} of {id_name}")

    def plotAnalysis(self, chart: Canvas, analysis_info, addMode=False):

        #todo: no futuro, avaliar se uso analysis ou analysis_item para fazer as condicoes
        id_name = analysis_info["id_name"]
        analysis_item = analysis_info["analysis_item"]
        analysis_dict = analysis_info["analysis_dict"]
        titleyxlabel = []

        if analysis_item.flag() is ExploreItem.AnalysisType.MagneticField:
            
            x, y, z, *B = list(analysis_dict.values())
            B = np.array(B).T

            titleyxlabel.extend(["Magnetic Field", "Bx, By, Bz (T)"])
            label = [f"Bx of {id_name}",f"By of {id_name}",f"Bz of {id_name}"]
            if not isinstance(z, (int, float)):
                chart.ax.plot(z,B,label=label)
                titleyxlabel.append("z (mm)")
            elif not isinstance(x, (int, float)):
                chart.ax.plot(x,B,label=label)
                titleyxlabel.append("x (mm)")
            elif not isinstance(y, (int, float)):
                chart.ax.plot(y,B,label=label)
                titleyxlabel.append("y (mm)")

        elif analysis_item.flag() is ExploreItem.AnalysisType.Trajectory:
            
            x, y, z, dxds, dyds, dzds = analysis_dict.values()
            x_y = np.array([x,y]).T
            dxds_dyds = np.array([dxds,dyds]).T

            menuIntegral = QMenu(self)
            menuIntegral.addAction("Position Deviation")
            menuIntegral.addAction("Angular Deviation")
            #todo: consertar pos para pegar canto superior direito do item
            action = menuIntegral.exec(QCursor.pos())
            if action is None:
                return False
            
            if action.text()=="Position Deviation":
                chart.ax.plot(z,x_y,label=[f"x of {id_name}", f"y of {id_name}"])
                titleyxlabel.extend(["Trajectory","x, y (mm)"])
            elif action.text()=="Angular Deviation":
                chart.ax.plot(z,dxds_dyds,label=[f"x' of {id_name}", f"y' of {id_name}"])
                titleyxlabel.extend(["Trajectory - Angular Deviation","x', y' (rad)"])
            titleyxlabel.append("z (mm)")

        elif  analysis_item.flag() is ExploreItem.AnalysisType.PhaseError:

            z_poles, phaserr, phaserr_rms = analysis_dict.values()

            #phaserr_line = chart.ax.plot(np.arange(1,len(phaserr)+1), phaserr,'o-')
            phaserr_line, = chart.ax.plot(z_poles, phaserr,'o-',label=f"Phase Error of {id_name}")
            #rms_line = chart.ax.plot([1,len(phaserr)], [phaserr_rms, phaserr_rms],'--',c=phaserr_line[0].get_color())
            chart.ax.plot([z_poles[0],z_poles[-1]],
                                     [phaserr_rms, phaserr_rms],'--',
                                     label=f"Phase Err RMS of {id_name}",
                                     c=phaserr_line.get_color())

            titleyxlabel.extend(["Phase Error","Phase Error (deg)","z poles (mm)"])

        elif analysis_item.flag() is ExploreItem.AnalysisType.Integrals:

            z, ibx, iby, ibz, iibx, iiby, iibz = analysis_dict.values()
            ib = np.array([ibx, iby, ibz]).T
            iib = np.array([iibx, iiby, iibz]).T

            menuIntegral = QMenu(self)
            menuIntegral.addAction("First Integral")
            menuIntegral.addAction("Second Integral")
            #todo: consertar pos para pegar canto superior direito do item
            action = menuIntegral.exec(QCursor.pos())
            if action is None:
                return False
            
            if action.text()=="First Integral":
                chart.ax.plot(z,ib,label=[f"ibx of {id_name}", f"iby of {id_name}", f"ibz of {id_name}"])
                titleyxlabel.extend(["Field Integral - First","ibx, iby, ibz (G.cm)"])

            elif action.text()=="Second Integral":
                chart.ax.plot(z,iib,label=[f"iibx of {id_name}", f"iiby of {id_name}", f"iibz of {id_name}"])
                titleyxlabel.extend(["Field Integral - Second","iibx, iiby, iibz (kG.cm2)"])

            titleyxlabel.append("z (mm)")

        elif analysis_item.flag() is ExploreItem.AnalysisType.RollOffAmp:

            x, y, *roa = analysis_dict.values()
            roa = 100*np.array(roa).T

            chart.ax.plot(x,roa,label=[f"ROAx of {id_name}",f"ROAy of {id_name}",f"ROAz of {id_name}"])
            titleyxlabel.extend(["Roll Off Amplitude", "ROAx, ROAy, ROAz (%)", "x (mm)"])

        if addMode:
            chart.ax.set_title("")
            chart.ax.set_ylabel("")
            chart.ax.set_xlabel("")
        else:
            chart.ax.set_title(titleyxlabel[0])
            chart.ax.set_ylabel(titleyxlabel[1])
            chart.ax.set_xlabel(titleyxlabel[2])

        return True

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
