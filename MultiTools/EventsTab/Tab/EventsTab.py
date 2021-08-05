from Widgets2 import EventWidget
'''
To Do 

    - Drag/Drop move nodes via Node List
    - option for syncing the state
    - option for viewing super tool children
    - sometimes super tool children not sorting correctly inside of supertools?
    - rename nodes
    - sort by node type
'''
from qtpy.QtWidgets import QVBoxLayout
from Katana import UI4 , NodegraphAPI, Utils

class EventsTab(UI4.Tabs.BaseTab):
    NAME = 'Global Events'
    def __init__(self, parent=None):
        super(EventsTab, self).__init__(parent)
        self._param_location = "KatanaBebop.GlobalEventsData.data"

        QVBoxLayout(self)
        # setup main widget

        self.node = NodegraphAPI.GetRootNode()
        katana_main = UI4.App.MainWindow.GetMainWindow()

        node = NodegraphAPI.GetRootNode()
        if not hasattr(katana_main, "global_events_widget"):
            katana_main.global_events_widget = EventWidget(
                katana_main, node=node, param=self.paramLocation())

        self.main_widget = katana_main.global_events_widget
        self.layout().addWidget(self.main_widget)

    def paramLocation(self):
        return self._param_location

    def showEvent(self, event):
        self.layout().addWidget(self.main_widget)
        node = NodegraphAPI.GetRootNode()
        if not node.getParameter(self.paramLocation()):
            node.getParameters().createChildString(self.paramLocation(), "")

        self.main_widget.main_node = node
        self.main_widget.eventsWidget().clearModel()
        self.main_widget.loadEventsDataFromJSON()
        self.main_widget.show()

    def closeEvent(self, event):
        katana_main = UI4.App.MainWindow.GetMainWindow()
        self.main_widget.setParent(katana_main)
        self.main_widget.hide()

#PluginRegistry = [("KatanaPanel", 2, "Events", EventsTab)]