import enum
from PyQt6.QtWidgets import QTreeWidgetItem

class Items(enum.Enum):
    DataItem = 2
    ModelItem = 3
    FieldItem = 4
    TrajectoryItem = 5


class ExploreItem(QTreeWidgetItem):

    def __init__(self, item_type: Items, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.item_type = item_type

    def children(self):
        return [self.child(i) for i in range(self.childCount())]

