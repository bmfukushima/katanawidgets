
from qtpy.QtWidgets import (
    QLabel, QVBoxLayout, QWidget
)

from qtpy.QtCore import Qt, QEvent

from cgwidgets.utils import attrs
from cgwidgets.widgets import TansuModelViewWidget, TansuHeaderTreeView, StringInputWidget

try:
    from Katana import UI4, NodegraphAPI, Utils
    from Widgets2 import AbstractSuperToolEditor, NodeTypeListWidget
    from Utils2 import nodeutils
except (ImportError, ModuleNotFoundError) as e:
    pass

class NodeTreeEditor(AbstractSuperToolEditor):
    def __init__(self, parent, node):
        super(NodeTreeEditor, self).__init__(parent, node)
        """
        Class:
        NodeTreeEditor --|> AbstractSuperToolEditor
            | --
        """

        self._node_type = "<multi>"
        # setup layout
        QVBoxLayout(self)

        # create node tree
        self._node_tree = NodeTreeMainWidget(parent=self, node=self.node)

        # add tree to layout
        self.layout().addWidget(self.nodeTree())
        self.insertResizeBar()

    """ PROPERTIES """
    def nodeTree(self):
        return self._node_tree

    def setNodeTree(self, _node_tree):
        self._node_tree = _node_tree

    def nodeType(self):
        return self._node_type

    def setNodeType(self, _node_type):
        self._node_type = _node_type


class NodeTreeMainWidget(TansuModelViewWidget):
    def __init__(self, parent=None, node=None):
        super(NodeTreeMainWidget, self).__init__(parent)
        self.node = node

        # setup view
        view = NodeTreeViewWidget(self)

        # setup header
        self.setHeaderViewWidget(view)
        self.setHeaderPosition(attrs.WEST, attrs.NORTH)
        self.setHeaderData(['name', 'type'])

        # set dynamic
        self.setDelegateType(
            TansuModelViewWidget.DYNAMIC,
            dynamic_widget=NodeTreeDynamicWidget,
            dynamic_function=NodeTreeDynamicWidget.updateGUI
        )

        # node create widget
        header_delegate_widget = NodeTreeHeaderDelegate(self)
        self.setHeaderDelegateWidget(header_delegate_widget)

        # events
        self.setHeaderItemDropEvent(self.nodeMovedEvent)
        header_delegate_widget.setUserFinishedEditingEvent(self.createNewNode)
        self.setHeaderItemTextChangedEvent(self.nodeNameChangedEvent)
        # setup attrs
        self.setMultiSelect(True)
        # set hotkey to activate
        #self.TOGGLE_DELEGATE_KEYS = [Qt.Key_T, Qt.Key_1]

        # print(self, self.node)

    def getSelectedIndex(self):
        """Returns the currently selected item"""
        indexes = self.getAllSelectedIndexes()
        if len(indexes) == 0: return None
        else: return indexes[0]

    def getParentIndex(self):
        """Gets the current parent index for node creation"""
        index = self.getSelectedIndex()
        if index:
            node_name = index.internalPointer().columnData()["name"]
            node = NodegraphAPI.GetNode(node_name)
            if node.getType() != "Group":
                return index.parent()
            else:
                return index

    def getParentNodeFromIndex(self, index):
        """Returns the currently selected node in this widget"""
        if index:
            item = index.internalPointer()

            # top level group
            if item:
                node_name = index.internalPointer().columnData()["name"]
                node = NodegraphAPI.GetNode(node_name)
            # top level, NOT group
            else:
                node = self.node
        else:
            node = self.node

        return node

    def getNodeListFromItem(self, item):
        """
        Gets all of the node children from the specified item

        Returns (list) of nodes
        """
        # get node list
        children = item.children()
        node_name_list = [child.columnData()['name'] for child in children]
        node_list = [NodegraphAPI.GetNode(node) for node in node_name_list]

        return node_list

    """ EVENTS """
    def createNewNode(self, widget, value):
        """ User creating new node """
        # get node
        parent_index = self.getParentIndex()
        parent_node = self.getParentNodeFromIndex(parent_index)

        # get node type to create
        node_type = value

        # create node
        # # check if node type in nodes list...
        all_nodes = NodegraphAPI.GetNodeTypes()

        if node_type in all_nodes:
            # # create node
            new_node = NodegraphAPI.CreateNode(str(node_type), parent_node)

            name = str(new_node.getName())
            node_type = new_node.getType()

            # create new item
            new_index = self.insertTansuWidget(0, column_data={'name': name, 'type': node_type}, parent=parent_index)
            new_item = new_index.internalPointer()
            if not hasattr(new_node, 'getChildren'):
                new_item.setIsDropEnabled(False)
            # wire node
            nodeutils.createIOPorts(new_node, force_create=False, connect=False)

            # get children / parent_node
            if parent_index:
                item = parent_index.internalPointer()
                # if index exists
                if item:
                    group_item = parent_index.internalPointer()
                # special case for root
                else:
                    group_item = parent_index.internalPointer()

            else:
                group_item = self.model().getRootItem()
                parent_node = self.node

            # get node list
            node_list = self.getNodeListFromItem(group_item)

            nodeutils.connectInsideGroup(node_list, parent_node)

            # reset widget
            widget.setText('')
            widget.hide()

            # TODO Set focus back on header?
            self.headerViewWidget().setFocus()
        else:
            return

    def nodeMovedEvent(self, row, items_dropped, parent):
        """
        Run when the user does a drop.  This is triggered on the dropMimeData funciton
        in the model.

        Args:
            indexes (list): of TansuModelItems
            parent (TansuModelItem): parent item that was dropped on

        """
        # disconnect... not working... input ports not reconnect to group send?

        # get parent node
        parent_node = NodegraphAPI.GetNode(parent.columnData()['name'])
        # if root
        if parent.columnData()["name"] == 'root':
            parent_node = self.node

        # drop items
        for item in items_dropped:
            # get node
            node = NodegraphAPI.GetNode(item.columnData()['name'])

            # disconnect node
            nodeutils.disconnectNode(node, input=True, output=True, reconnect=True)

            # reparent
            node.setParent(parent_node)

        # reconnect node to new parent
        node_list = self.getNodeListFromItem(parent)
        nodeutils.connectInsideGroup(node_list, parent_node)

        # reconnect old parent
        # node dropped?

    def nodeNameChangedEvent(self, item, old_value, new_value):
        node = NodegraphAPI.GetNode(old_value)
        node.setName(new_value)
        Utils.EventModule.ProcessAllEvents()
        new_name = node.getName()
        item.columnData()['name'] = new_name


class NodeTreeHeaderDelegate(NodeTypeListWidget):
    def __init__(self, parent=None):
        super(NodeTreeHeaderDelegate, self).__init__(parent)


class NodeTreeViewWidget(TansuHeaderTreeView):
    def __init__(self, parent=None):
        super(NodeTreeViewWidget, self).__init__(parent)


class NodeTreeDynamicWidget(QWidget):
    """
    Simple example of overloaded class to be used as a dynamic widget for
    the TansuModelViewWidget.
    """
    def __init__(self, parent=None):
        super(NodeTreeDynamicWidget, self).__init__(parent)
        QVBoxLayout(self)
        self.label = QLabel('init')
        self.layout().addWidget(self.label)

    @staticmethod
    def updateGUI(parent, widget, item):
        """
        widget (TansuModelDelegateWidget)
        item (TansuModelItem)
        """
        # ToDo Update node selected display
        #
        if item:
            print ('----------------------------')
            #print(parent, widget, item)
            print(item.columnData())
            name = parent.model().getItemName(item)
            widget.setName(name)
            widget.getMainWidget().label.setText(name)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout
    from qtpy.QtGui import QCursor
    from cgwidgets.widgets import TansuModelViewWidget
    app = QApplication(sys.argv)

    w = NodeTreeEditor(None, None)
    w.resize(500, 500)

    w.show()
    w.move(QCursor.pos())
    sys.exit(app.exec_())


# import sys
# from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout
# from qtpy.QtGui import QCursor
# from cgwidgets.widgets import TansuModelViewWidget
# w = NodeTreeEditor(None, None)
# w.resize(500, 500)
#
# w.show()
# w.move(QCursor.pos())