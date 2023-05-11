
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSignal
from PyQt6.QtWidgets import QTableView


class TableModel(QAbstractTableModel):

    def __init__(self, data, header):
        super(TableModel, self).__init__()

        # acessar filename pelas variaveis de insertion device
        #filename = meas.filename

        # apenas pegar o header com o open
        # demais dados pegar pelos metodos e atributos de insertiondevice

        # abaixo so funciona se cabecalho estiver na primeira linha
        # with open(filename, 'r') as f:
        #     self._header = f.readline().split()
        
        # fechar arquivo com .close()

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
        
        '''
        if role==Qt.ItemDataRole.ForegroundRole:
            if orientation == Qt.Orientation.Vertical:
                return QColor.fromRgb(255, 255, 255)
        '''

class Table(QTableView):

    selectReturned = pyqtSignal(list)

    def __init__(self, data, header):
        super().__init__()

        self.modeltable = TableModel(data, header)
        self.setModel(self.modeltable)
        
        # estilo da tabela
        horizontal_color = QColor.fromRgb(200, 200, 200)
        vertical_color = QColor.fromRgb(200, 200, 200)
        horizontal_header_style = "QHeaderView::section {{background-color: {} }}".format(horizontal_color.name())
        vertical_header_style = "QHeaderView::section {{background-color: {} }}".format(vertical_color.name())
        self.horizontalHeader().setStyleSheet(horizontal_header_style)
        self.verticalHeader().setStyleSheet(vertical_header_style)
    
    
    def keyPressEvent(self, event) -> None:
        if event.key() in [Qt.Key.Key_Return,Qt.Key.Key_Enter]:
            self.selectReturned.emit(self.selectedIndexes())
        else:
            return super().keyPressEvent(event)
