
from PyQt6.QtWidgets import QTabWidget, QMenu, QInputDialog, QLineEdit, QWidget
from PyQt6.QtCore import Qt


class BasicTabWidget(QTabWidget):
    def __init__(self,parent=None, leftSpace=0):
        super().__init__(parent)

        self.leftSpace = leftSpace
        #para o triggered saber a posicao da tab do menu
        self.tabPos = None

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        #todo: descobrir o que o documentMode faz e se pode tirar esse comando ou nao
        self.setDocumentMode(True) # talvez possa ser desabilitado
        self.setMovable(True)
        self.setTabsClosable(True)
        
        self.tabCloseRequested.connect(self.closeTab)
        self.tabBarDoubleClicked.connect(self.start_rename)
        self.customContextMenuRequested.connect(self.exec_context_menu)

        self.menuContext = QMenu(self)
        actionRename = self.menuContext.addAction("Rename Tab")
        actionRename.triggered.connect(self.rename_tab)


    def exec_context_menu(self, pos):
        self.tabPos = pos
        self.menuContext.exec(self.mapToGlobal(self.tabPos))
    
    def rename_tab(self):
        
        index = self.tabBar().tabAt(self.tabPos)

        new_text, ok = QInputDialog.getText(self, 'Rename Item', 'Enter new name:', text=self.tabText(index))
        
        if ok:
            self.setTabText(index, new_text)

    def start_rename(self, tab_index):
        self.editting_tab = tab_index

        tab_rect = self.tabBar().tabRect(tab_index)
        corner = self.mapToParent(tab_rect.topLeft())

        self.edit = QLineEdit(parent=self.parent())
        self.edit.textChanged.connect(self.resize_to_content)
        self.edit.editingFinished.connect(self.finish_rename)
        
        left_margin = 10
        self.edit.move(corner.x()+left_margin+self.leftSpace, corner.y())
        self.edit.setFixedHeight(tab_rect.height())

        self.edit.setText(self.tabText(tab_index))
        self.edit.selectAll()
        self.edit.setFocus() # talvez de problema quando clicar fora do line edit enquanto ele tiver aberto

        self.edit.show()

    def resize_to_content(self):
        X_margin = 15
        self.edit.setFixedWidth(10+X_margin+self.edit.fontMetrics().boundingRect(self.edit.text()).width())

    def finish_rename(self):
        self.setTabText(self.editting_tab, self.edit.text())
        self.edit.deleteLater()

    def addTab(self, widget: QWidget, text: str) -> int:
        i = super().addTab(widget, text)
        #addTab adiciona a nova tab, mas mantem o usuario na tab inicial, nao na adicionada
        #para mudar para a tab adicionada, usar o setcurrentindex abaixo
        self.setCurrentIndex(i)
        return i
    
    def closeTab(self, i):
        self.widget(i).deleteLater()

