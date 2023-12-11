
from PyQt6.QtWidgets import QPushButton, QMenu
from PyQt6.QtGui import QPainter, QPolygon, QCursor
from PyQt6.QtCore import QPoint, Qt, pyqtSignal

class PaintedButton(QPushButton):

    modeChanged = pyqtSignal(bool)

    def __init__(self, text="", parent=None, *args, **kwargs):
        super().__init__(text, parent, *args, **kwargs)

        self.selectedAction = None

        self.setCheckable(True)

        self.clicked.connect(self.button_clicked)

        self.Menu = QMenu(self)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()-2
        height = self.height()-2
        len = int(min(self.width(),self.height())/2)-4
        
        # coordinates of the polygon points must be integers
        square = QPolygon([QPoint(width,height),
                           QPoint(width,height-len),
                           QPoint(width-len,height-len),
                           QPoint(width-len, height)])
        painter.setBrush(Qt.GlobalColor.gray)
        painter.drawPolygon(square)
        painter.end()
    
    def button_clicked(self,s):

        cursor_pos = QCursor.pos()
        widget_pos = self.mapFromGlobal(cursor_pos)

        x, y = widget_pos.x(), widget_pos.y()

        width = self.width()
        height = self.height()
        len = min(self.width(),self.height())/2

        if (width-len <= x <= width) and (height-len <= y <= height):
            if self.isChecked():
                self.setChecked(False)
            else:
                self.setChecked(True)
            #dentro
            self.show_menu()
        else:
            #fora
            self.modeChanged.emit(True)


    def show_menu(self):
        action = self.Menu.exec(self.mapToGlobal(self.rect().bottomLeft()))
        if action:
            self.selectedAction = action
    
    def action_swap(self):

        action = self.sender()

        self.setIcon(action.icon())
        self.setChecked(True)
        # fazer swap da acao e ja mudar de botao
        self.modeChanged.emit(False)

        