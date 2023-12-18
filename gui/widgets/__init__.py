
import os
# import json
import inspect
# from pathlib import Path

def get_path(file_dir,filename):

    # if file_dir==".":
    #     direc = str(Path(__file__).parent)
    # else:
    #     direc = str(Path(__file__).with_name(file_dir))

    # return str(Path(direc,filename))

    basedir = os.path.dirname(__file__)

    return os.path.join(basedir,file_dir,filename)


# with open(get_path('','models_parameters.json')) as f:
#     models_parameters = json.load(f)

from imaids import models

models_dict = {}
for name in dir(models):
    obj = getattr(models, name)
    # deixar apenas modelos especificos no dicionario de modelos
    if isinstance(obj, type) and obj.__bases__[0].__name__!="InsertionDeviceModel":
        models_dict[name] = obj

models_parameters = {}
for model_name, model_cls in models_dict.items():
    sig = inspect.signature(model_cls.__init__)
    models_parameters[model_name] = {param:sig.parameters[param].default
                                        for param in ["nr_periods",
                                                      "period_length",
                                                      "gap",
                                                      "mr",
                                                      "longitudinal_distance"]}


from . import basics
from . import _mpl_layout_mod, _mpl_options_mod, visual_elements
from . import explore_window, visualization_window, projects
from . import painted_button, analysis, window_bars
from . import dialog_layouts
from . import data_dialog, model_dialog, save_dialog, summary_dialog