
from PyQt6.QtWidgets import (QWidget,
                             QTabWidget,
                             QTabBar,
                             QMenu,
                             QInputDialog,
                             QLineEdit,
                             QStyle,
                             QStylePainter,
                             QStyleOptionTab,
                             QVBoxLayout,
                             QToolButton,
                             QLayout)

from PyQt6.QtCore import pyqtSignal, Qt, QRect, QPoint


class BasicTabWidget(QTabWidget):

    tabAdded = pyqtSignal(int)

    def __init__(self,parent=None, leftSpace=0):
        super().__init__(parent)

        self.leftSpace = leftSpace
        #para o triggered saber a posicao da tab do menu
        self.tabPos = None

        self.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        #todo: descobrir o que o documentMode faz e se pode tirar esse comando ou nao
        self.setDocumentMode(True) # talvez possa ser desabilitado
        self.setMovable(True)
        self.setTabsClosable(True)
        
        self.tabCloseRequested.connect(self.closeTab)
        self.tabBarDoubleClicked.connect(self.start_rename)
        self.tabBar().customContextMenuRequested.connect(self.exec_context_menu)

        self.menuContext = QMenu(self)
        self.menuContext.setToolTipsVisible(True)
        actionRename = self.menuContext.addAction("Rename Tab")
        actionRename.triggered.connect(self.rename_tab)


    def exec_context_menu(self, pos):
        self.tabPos = pos
        index = self.tabBar().tabAt(self.tabPos)
        if index != -1:
            self.menuContext.exec(self.mapToGlobal(self.tabPos))
    
    def rename_tab(self):
        
        index = self.tabBar().tabAt(self.tabPos)

        new_text, ok = QInputDialog.getText(
            self, 'Rename Item', 'Enter new name:', text=self.tabText(index)
        )
        
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
        self.edit.setFixedWidth(
            10+X_margin+self.edit.fontMetrics().boundingRect(self.edit.text()).width()
        )

    def finish_rename(self):
        self.setTabText(self.editting_tab, self.edit.text())
        self.edit.deleteLater()

    def addTab(self, widget: QWidget, text: str) -> int:
        i = super().addTab(widget, text)
        #addTab adiciona a nova tab, mas mantem o usuario na tab inicial, nao na adicionada
        #para mudar para a tab adicionada, usar o setcurrentindex abaixo
        self.setCurrentIndex(i)
        self.tabAdded.emit(i)
        return i
    
    def closeTab(self, i):
        self.widget(i).deleteLater()


class VerticalTabBar(QTabBar):

    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabLabel, opt)
            painter.restore()


class VerticalTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setTabBar(VerticalTabBar(self))
        self.setTabPosition(QTabWidget.TabPosition.West)


class CollapsibleBox(QWidget):
    def __init__(self, title=""):
        super().__init__()

        self.setContentsMargins(0,0,0,0) #!

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(0) #!
        self.vbox.setContentsMargins(0,0,0,0) #!

        self.button = QToolButton(text=title, checkable=True, checked=False)

        self.button.setStyleSheet("border: none")
        self.button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.button.setArrowType(Qt.ArrowType.RightArrow)
        self.button.clicked.connect(self.setContentExpanded)

        self.content = QWidget()
        self.content.setHidden(True)

        self.vbox.addWidget(self.button)
        self.vbox.addWidget(self.content)

    def setContentExpanded(self, expand):

        right = Qt.ArrowType.RightArrow
        down = Qt.ArrowType.DownArrow

        self.button.setChecked(expand)
        self.button.setArrowType(down if expand else right)
        self.content.setHidden(not expand)
    
    def isExpanded(self) -> bool:
        return not self.content.isHidden()

    def widget(self):
        return self.content

    def cleanContent(self):

        if type(self.content) is not QWidget:
            self.content.deleteLater()

        lay = self.content.layout()
        if lay is not None:
            lay.deleteLater()

    def setWidget(self, widget: QWidget):
        self.cleanContent()
        self.content = widget

        self.vbox.insertWidget(1,self.content)
        self.content.setHidden(True)

    def setContentLayout(self, layout: QLayout):
        self.cleanContent()
        self.content = QWidget()
        self.content.setLayout(layout)

        self.vbox.insertWidget(1,self.content)
        self.content.setHidden(True)