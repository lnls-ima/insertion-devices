
from PyQt6.QtWidgets import QDialog

from .dialog_layouts import ShortcutsLayout


class ShortcutsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Shortcuts sheet")

        layoutShortcuts = ShortcutsLayout(self)

        layoutShortcuts.buttonBox.accepted.connect(self.accept)
        layoutShortcuts.buttonBox.rejected.connect(self.reject)