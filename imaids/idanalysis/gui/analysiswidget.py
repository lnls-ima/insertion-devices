"""Analysis widget for the Moving Wire Control application."""

import os as _os
import sys as _sys
import numpy as _np
import time as _time
import pandas as _pd
import imaids as _imaids
import traceback as _traceback

from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    QVBoxLayout as _QVBoxLayout,
    )
from qtpy.QtCore import Qt as _Qt
from qtpy.QtWidgets import QFileDialog as _QFileDialog
import qtpy.uic as _uic

from idanalysis.gui.utils import (
    get_ui_file as _get_ui_file,
    sleep as _sleep,
    update_db_name_list as _update_db_name_list,
    pandas_load_db_measurements as _pandas_load_db_measurements,
    pandas_load_db_maps as _pandas_load_db_maps,
    json_to_array as _json_to_array
    )

import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as _FigureCanvas)
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as _NavigationToolbar)
from matplotlib.figure import Figure


class MplCanvas(_FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class AnalysisWidget(_QWidget):
    """Analysis widget class for the ID Analysis application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.connect_signal_slots()
        self.set_pyplot()
        # self.set_plot_flag = True

        self.data = None

    # @property
    # def database_name(self):
    #     """Database name."""
    #     return _QApplication.instance().database_name
    #
    # @property
    # def mongo(self):
    #     """MongoDB database."""
    #     return _QApplication.instance().mongo
    #
    # @property
    # def server(self):
    #     """Server for MongoDB database."""
    #     return _QApplication.instance().server

    @property
    def directory(self):
        """Return the default directory."""
        return _QApplication.instance().directory

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        self.ui.cmb_plot.currentIndexChanged.connect(self.plot)
        self.ui.pbt_analyse.clicked.connect(self.run_analysis)
        self.ui.pbt_spectra_fieldmap.clicked.connect(self.save_spectra)
        self.ui.pbt_multipoles.clicked.connect(self.multipoles)
        self.ui.tbt_filedialog.clicked.connect(self.file_dialog)

    def set_pyplot(self):
        """Configures plot widget"""
        self.canvas = MplCanvas(self, width=5, height=8, dpi=100)
        _toolbar = _NavigationToolbar(self.canvas, self)
        
        _layout = _QVBoxLayout()
        _layout.addWidget(self.canvas)
        _layout.addWidget(_toolbar)
        
        self.wg_plot.setLayout(_layout)

    def file_dialog(self):
        """Opens file dialog to select the fieldmap."""
        try:
            filename, _ = _QFileDialog.getOpenFileName(self,"Fieldmap file",
                "","All Files (*);;Python Files (*.py)")
            self.ui.cmb_filename.setCurrentText(filename)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def run_analysis(self):
        """Runs analysis on fieldmap."""
        try:
            # Loads the file
            filename = self.ui.cmb_filename.currentText()
            nr_periods = self.ui.sb_periods.value()
            period_length = self.ui.dsb_period_length.value()
            gap = self.ui.dsb_gap.value()
            
            self.data = _imaids.insertiondevice.InsertionDeviceData(
                filename=filename, nr_periods=nr_periods,
                period_length=period_length, gap=gap)

            if self.ui.chb_angle.isChecked():
                self.data.correct_angles()
            if self.ui.chb_crosstalk.isChecked():
                self.data.correct_crosstalk()

            # Parameters for calculus:
            
            energy = 3
            rkstep = 0.5
            skip_poles = 4

            # Calculations
            self.data.b = self.data.get_field(x=0, y=0, z=self.data.pz)
            
            self.data.roll_off = self.data.calc_roll_off_amplitude(
                self.data.pz, self.data.px)
            self.data.ib, self.data.iib = self.data.calc_field_integrals(
                z_list=self.data.pz)
            
            self.data.integs = _np.array(
                [self.data.calc_field_integrals(self.data.pz, x=xp, y=0) 
                 for xp in self.data.px])
            
            self.data.traj = self.data.calc_trajectory(
                energy, [0, 0, self.data.pz[0], 0, 0, 1],
                self.data.pz[-1], rkstep)
            self.data.bxamp, self.data.byamp, _, _ = (
                self.data.calc_field_amplitude())
            self.data.kh, self.data.kv = self.data.calc_deflection_parameter(
                self.data.bxamp, self.data.byamp)
            zpe, pe, perms = self.data.calc_phase_error(
                energy, self.data.traj, self.data.bxamp, self.data.byamp,
                skip_poles=skip_poles)
            self.data.pe = pe*180/_np.pi
            self.data.perms = perms*180/_np.pi

            self.ui.le_I1x.setText('{:.2f}'.format(self.data.ib[:, 0][-1]))
            self.ui.le_I1y.setText('{:.2f}'.format(self.data.ib[:, 1][-1]))
            self.ui.le_I2x.setText('{:.2f}'.format(self.data.iib[:, 0][-1]))
            self.ui.le_I2y.setText('{:.2f}'.format(self.data.iib[:, 1][-1]))
            self.ui.le_perms.setText('{:.2f}'.format(self.data.perms))
            if self.data.bxamp > self.data.byamp:
                self.ui.le_bamp.setText('{:.2f}'.format(self.data.bxamp))
            else:
                self.ui.le_bamp.setText('{:.2f}'.format(self.data.byamp))
            self.ui.le_kh.setText('{:.2f}'.format(self.data.kh))
            self.ui.le_kv.setText('{:.2f}'.format(self.data.kv))

            self.plot()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def plot(self):
        """Plots measurement data."""
        try:

            # if self.set_plot_flag:
            #     self.set_pyplot()
            #     self.set_plot_flag = False

            self.canvas.axes.cla()

            if self.ui.cmb_plot.currentText() == 'BxByBz':
                z = self.data.pz
                self.canvas.axes.plot(z, self.data.b[:, 0], label='Bx')
                self.canvas.axes.plot(z, self.data.b[:, 1], label='By')
                self.canvas.axes.plot(z, self.data.b[:, 2], label='Bz')
                self.canvas.axes.set_xlabel('z [mm]')
                self.canvas.axes.set_ylabel('Field [T]')
                self.canvas.axes.legend()
                self.canvas.axes.grid(1)

            elif self.ui.cmb_plot.currentText() == 'Bx':
                z = self.data.pz
                self.canvas.axes.plot(z, self.data.b[:, 0], label='Bx')
                self.canvas.axes.set_xlabel('z [mm]')
                self.canvas.axes.set_ylabel('Field [T]')
                self.canvas.axes.legend()
                self.canvas.axes.grid(1)

            elif self.ui.cmb_plot.currentText() == 'By':
                z = self.data.pz
                self.canvas.axes.plot(z, self.data.b[:, 1], label='By')
                self.canvas.axes.set_xlabel('z [mm]')
                self.canvas.axes.set_ylabel('Field [T]')
                self.canvas.axes.legend()
                self.canvas.axes.grid(1)

            elif self.ui.cmb_plot.currentText() == 'Bz':
                z = self.data.pz
                self.canvas.axes.plot(z, self.data.b[:, 2], label='Bz')
                self.canvas.axes.set_xlabel('z [mm]')
                self.canvas.axes.set_ylabel('Field [T]')
                self.canvas.axes.legend()
                self.canvas.axes.grid(1)

            elif self.ui.cmb_plot.currentText() == 'Roll-off':
                x = self.data.px
                self.canvas.axes.plot(x, 100*self.data.roll_off[1],
                                      label='Roll-off')
                self.canvas.axes.set_xlabel('x [mm]')
                self.canvas.axes.set_ylabel('Roll-off [%]')
                self.canvas.axes.legend()
                self.canvas.axes.grid(1)

            elif self.ui.cmb_plot.currentText() == 'Trajectory X':
                z = _np.linspace(self.data.pz[0], self.data.pz[-1],
                                 len(self.data.traj[:, 0]))
                self.canvas.axes.plot(z, self.data.traj[:, 0],
                                      label='X trajectory')
                self.canvas.axes.set_xlabel('z [mm]')
                self.canvas.axes.set_ylabel('x [mm]')
                self.canvas.axes.legend()
                self.canvas.axes.grid(1)

            elif self.ui.cmb_plot.currentText() == 'Trajectory Y':
                z = _np.linspace(self.data.pz[0], self.data.pz[-1],
                                 len(self.data.traj[:, 0]))
                self.canvas.axes.plot(z, self.data.traj[:, 1],
                                      label='Y trajectory')
                self.canvas.axes.set_xlabel('z [mm]')
                self.canvas.axes.set_ylabel('x [mm]')
                self.canvas.axes.legend()
                self.canvas.axes.grid(1)
            
            elif self.ui.cmb_plot.currentText() == 'Phase Error':
                poles = list(range(1, len(self.data.pe)+1))
                self.canvas.axes.plot(poles, self.data.pe, '-o')
                    
                self.canvas.axes.grid(1)
                self.canvas.axes.set_xlabel('Pole Number')
                self.canvas.axes.set_ylabel(r'Phase Error ($\mathbf{\phi)}$ [°]')
                self.canvas.axes.axhline(0, color='k', linestyle='--')
            
            elif self.ui.cmb_plot.currentText() == 'I1x vs x':
                x = self.data.px
                self.canvas.axes.plot(x, self.data.integs[:, 0, -1, 0],
                                      label='I1x')
                self.canvas.axes.set_xlabel('x [mm]')
                self.canvas.axes.set_ylabel('First Field Integral [G.cm]')
                self.canvas.axes.legend()
                self.canvas.axes.grid(1)
            
            elif self.ui.cmb_plot.currentText() == 'I1y vs x':
                x = self.data.px
                self.canvas.axes.plot(x, self.data.integs[:, 0, -1, 1],
                                      label='I1y')
                self.canvas.axes.set_xlabel('x [mm]')
                self.canvas.axes.set_ylabel('First Field Integral [G.cm]')
                self.canvas.axes.legend()
                self.canvas.axes.grid(1)
            
            elif self.ui.cmb_plot.currentText() == 'I2x vs x':
                x = self.data.px
                self.canvas.axes.plot(x, self.data.integs[:, 1, -1, 0],
                                      label='I2x')
                self.canvas.axes.set_xlabel('x [mm]')
                self.canvas.axes.set_ylabel('Second Field Integral [kG.cm2]')
                self.canvas.axes.legend()
                self.canvas.axes.grid(1)
            
            elif self.ui.cmb_plot.currentText() == 'I2y vs x':
                x = self.data.px
                self.canvas.axes.plot(x, self.data.integs[:, 1, -1, 1],
                                      label='I2x')
                self.canvas.axes.set_xlabel('x [mm]')
                self.canvas.axes.set_ylabel('Second Field Integral [kG.cm2]')
                self.canvas.axes.legend()
                self.canvas.axes.grid(1)

            self.canvas.figure.tight_layout()
            self.canvas.draw()

        except Exception:
            _traceback.print_exc(file=_sys.stdout)


    def update_cmb_transv_pos(self):
        """Updates transversal positions combobox in order to plot map data"""
        try:
            _map_name = self.ui.cmb_map_name.currentText()
            _hor_axis = self.ui.cmb_hor.currentText()

            _maps = _pandas_load_db_maps()
            # _meas_I1, _meas_I2 = _pandas_load_db_measurements()
            #
            _map = _maps.loc[_maps['name'] == _map_name]
            #
            # _I1_id0 = _map['I1_start_id'].values[0] - 1
            # _I1_idf = _map['I1_end_id'].values[0]
            # _I2_id0 = _map['I2_start_id'].values[0] - 1
            # _I2_idf = _map['I2_end_id'].values[0]
            #
            # if _I1_idf != 0:
            #     _I1 = _meas_I1.iloc[_I1_id0:_I1_idf]
            #     _I1x = _I1.loc[_I1['motion_axis'] == 'Y']
            #     if len(_I1x) == 0:
            #         _I1x = None
            #     _I1y = _I1.loc[_I1['motion_axis'] == 'X']
            #     if len(_I1y) == 0:
            #         _I1y = None
            # else:
            #     _I1 = None
            #     _I1x = None
            #     _I1y = None
            #
            # if _I2_idf != 0:
            #     _I2 = _meas_I2.iloc[_I2_id0:_I2_idf]
            #     _I2x = _I2.loc[_I2['motion_axis'] == 'Y']
            #     if len(_I2x) == 0:
            #         _I2x = None
            #     _I2y = _I2.loc[_I2['motion_axis'] == 'X']
            #     if len(_I2y) == 0:
            #         _I2y = None
            # else:
            #     _I2 = None
            #     _I2x = None
            #     _I2y = None
            #
            # if _I1 is not None:
            #     _x_pos_array = _I1['x_pos'].drop_duplicates().values
            #     _y_pos_array = _I1['y_pos'].drop_duplicates().values
            # elif _I2 is not None:
            #     _x_pos_array = _I2['x_pos'].drop_duplicates().values
            #     _y_pos_array = _I2['y_pos'].drop_duplicates().values

            _x_pos_array = _json_to_array(_map['x_pos_array'].values[0])
            _y_pos_array = _json_to_array(_map['y_pos_array'].values[0])

            self.ui.cmb_transv_pos.clear()

            if _hor_axis != 'Meas #':
                if _hor_axis == 'X [mm]':
                    _pos_array = _y_pos_array
                if _hor_axis == 'Y [mm]':
                    _pos_array = _x_pos_array
                self.ui.cmb_transv_pos.addItems(
                    [str(pos) for pos in _pos_array])
                self.ui.cmb_transv_pos.setCurrentIndex(0)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def multipoles(self):
        """Prints multipoles (from higher to lower harmonics)."""
        try:
            an, bn = self.data.calc_integral_multipole_coef(self.data.pz,
                                                            self.data.px)

            _msg = 'Normal:\n{}\n\nSkew:\n{}'.format(bn, an)
            print(_msg)
            _QMessageBox.information(self, 'Multipoles', _msg, _QMessageBox.Ok)
        except Exception:
            print(_traceback.print_exc(file=_sys.stdout))
            return False

    def save_spectra(self):
        pass