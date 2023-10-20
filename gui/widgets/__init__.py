
import os
import json
# from pathlib import Path

def get_path(file_dir,filename):

    # if file_dir==".":
    #     direc = str(Path(__file__).parent)
    # else:
    #     direc = str(Path(__file__).with_name(file_dir))

    # return str(Path(direc,filename))

    basedir = os.path.dirname(__file__)

    return os.path.join(basedir,file_dir,filename)


with open(get_path('','models_parameters.json')) as f:
    models_parameters = json.load(f)

#todo: trocar undulator por ID
def getUndulatorName(filename):
    models = list(models_parameters.keys())
    
    acertos = []
    possible_names = ["Delta","Prototype","Sabia"]
    
    for modelname in possible_names+models:
        if modelname in filename:
            acertos.append(modelname)
    if acertos:
        return acertos[-1]
    else:
        return ""

def getUndulatorPhase(filename):
    phase_idx = filename.find("Phase")
    if phase_idx!=-1:
        phase = filename[phase_idx:].lstrip("Phase")[:3]
        phase = "".join([char for char in list(phase) if char.isdigit()])
        return phase
    else:
        return "N"

def isUndulatorCorrected(filename):
    corrected = False
    if "Corrected" in filename:
        corrected = True
    return corrected

from . import basics
from . import _mpl_layout_mod, _mpl_options_mod, visual_elements
from . import explore_window, visualization_window, projects
from . import painted_button, analysis, window_bars
from . import dialog_layouts
from . import data_dialog, model_dialog, save_dialog, summary_dialog