# -*- coding: utf-8 -*-

"""Main entry point to the ID Analysis application."""

import os as _os
import sys as _sys
import threading as _threading
from qtpy.QtWidgets import QApplication as _QApplication

from idanalysis.gui import utils as _utils
from idanalysis.gui.idanalysiswindow import (
    IDAnalysisWindow as _IDAnalysisWindow)



class IDAnalysisApp(_QApplication):
    """Moving Wire application."""

    def __init__(self, args):
        """Start application."""
        super().__init__(args)
        self.setStyle(_utils.WINDOW_STYLE)

        self.directory = _utils.BASEPATH
        self.database_name = _utils.DATABASE_NAME
        self.mongo = _utils.MONGO
        self.server = _utils.SERVER
        # self.create_database()

        # positions dict
        self.positions = {}
        self.current_max = 0
        self.current_min = 0

        # create dialogs
#         self.view_probe_dialog = _ViewProbeDialog()

        # devices instances
        # self.ppmac = _ppmac
        # self.fdi = _fdi
        # self.volt = _volt
        # self.ps = _ps


class GUIThread(_threading.Thread):
    """GUI Thread."""

    def __init__(self):
        """Start thread."""
        _threading.Thread.__init__(self)
        self.app = None
        self.window = None
        self.daemon = True
        self.start()

    def run(self):
        """Thread target function."""
        self.app = None
        if not _QApplication.instance():
            self.app = IDAnalysisApp([])
            self.window = _IDAnalysisWindow(
                width=_utils.WINDOW_WIDTH, height=_utils.WINDOW_HEIGHT)
            self.window.show()
            self.window.centralize_window()
            _sys.exit(self.app.exec_())


def run():
    """Run idanalysis application."""
    app = None
    if not _QApplication.instance():
        app = IDAnalysisApp([])
        window = _IDAnalysisWindow(
            width=_utils.WINDOW_WIDTH, height=_utils.WINDOW_HEIGHT)
        window.show()
        # window.centralize_window()
        _sys.exit(app.exec_())


def run_in_thread():
    """Run idanalysis application in a thread."""
    return GUIThread()
