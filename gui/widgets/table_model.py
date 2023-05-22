
from PyQt6.QtGui import QColor, QKeyEvent
from PyQt6.QtCore import (Qt,
                          QAbstractTableModel,
                          QModelIndex,
                          pyqtSignal,
                          QItemSelection,
                          QItemSelectionModel,
                          QItemSelectionRange)
from PyQt6.QtWidgets import QTableView

class TableModel(QAbstractTableModel):

    def __init__(self, data, header):
        super(TableModel, self).__init__()

        self._header = header
        self._data = data

    def data(self, index: QModelIndex, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data[index.row()][index.column()]
            if "e" in str(value):
                return f"{value:.2e}"
            else:
                return f"{value:.2f}"
        
        if role == Qt.ItemDataRole.BackgroundRole:
            color = [240,240, 240]
            return QColor.fromRgb(*color)

    def rowCount(self, index=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, index=QModelIndex()):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:

            if orientation == Qt.Orientation.Horizontal:
                return self._header[section]

            if orientation == Qt.Orientation.Vertical:
                return range(1, self._data.shape[0]+1)[section]


class TableSelectionModel(QItemSelectionModel):
    def __init__(self, model: QAbstractTableModel, view: QTableView):
        super().__init__(model)

        self.view = view

    def select(self, selection: QItemSelection, command):
        
        #caso entre apenas QModelIndex, o qual nao e' iteravel nem manipavel como QItemSelection
        if isinstance(selection, QModelIndex):
            selection = QItemSelection(selection, selection)
        
        viewcol = -1
        for index in self.view.selectedIndexes():
            viewcol = index.column()
            break
        
        indexes = selection.indexes()
        filtered_range = []

        if len(indexes)==1:
            filtered_range=indexes
        else:
            #filtrando indices
            for index in indexes:
                column = max(indexes[0].column(),viewcol)
                #aceitando apenas items da mesma coluna da primeira
                if index.column()==column:
                    filtered_range.append(index)

        filtered_selection = QItemSelection()
        if filtered_range:
            filtered_selection.select(filtered_range[0],filtered_range[-1])

        return super().select(filtered_selection, command)
        

class Table(QTableView):

    selectReturned = pyqtSignal(list)
    keyPressed = pyqtSignal(QKeyEvent)

    def __init__(self, data, header):
        super().__init__()

        modelTable = TableModel(data, header)
        self.setModel(modelTable)

        modelSelection = TableSelectionModel(model=modelTable, view=self)
        self.setSelectionModel(modelSelection)
        
        # estilo da tabela
        horizontal_color = QColor.fromRgb(200, 200, 200)
        vertical_color = QColor.fromRgb(200, 200, 200)
        horizontal_header_style = "QHeaderView::section {{background-color: {} }}".format(horizontal_color.name())
        vertical_header_style = "QHeaderView::section {{background-color: {} }}".format(vertical_color.name())
        self.horizontalHeader().setStyleSheet(horizontal_header_style)
        self.verticalHeader().setStyleSheet(vertical_header_style)
    
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key.Key_Space,Qt.Key.Key_Return,Qt.Key.Key_Enter]:
            self.selectReturned.emit(self.selectedIndexes())
        elif event.key() in [Qt.Key.Key_G,Qt.Key.Key_P, Qt.Key.Key_T]:
            self.keyPressed.emit(event)
        else:
            return super().keyPressEvent(event)
