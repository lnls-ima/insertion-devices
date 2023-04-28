
import enum
from PyQt6.QtWidgets import QTreeWidgetItem


class ExploreItem(QTreeWidgetItem):

    class Type(enum.Enum):
        ContainerData = 0
        ContainerModel = 1
        ItemData = 2
        ItemModel = 3
        ItemField = 4
        ItemTrajectory = 5
        ItemResult = 6

    def __init__(self, item_type: 'ExploreItem.Type', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.item_type = item_type

    def children(self):
        return [self.child(i) for i in range(self.childCount())]
