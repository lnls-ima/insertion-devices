from pathlib import Path

def get_path(file_dir,filename):

    if file_dir==".":
        direc = str(Path(__file__).parent)
    else:
        direc = str(Path(__file__).with_name(file_dir))

    return str(Path(direc,filename))

from . import basics
from . import _mpl_layout_mod, _mpl_options_mod, visual_elements
from . import explore_window, visualization_window, projects
from . import painted_button, analysis, window_bars
from . import dialog_layouts
from . import data_dialog, model_dialog, save_dialog, summary_dialog