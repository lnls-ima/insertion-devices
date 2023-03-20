# -*- coding: utf-8 -*-

"""Run the id analysis application."""

from idanalysis.gui import idanalysisapp


THREAD = False


if THREAD:
    thread = idanalysisapp.run_in_thread()
else:
    idanalysisapp.run()
