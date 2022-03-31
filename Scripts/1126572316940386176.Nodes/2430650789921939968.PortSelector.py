""" This is an evolution of the "~" key connection in Katana.
This is actived with the Alt+~ and will do a few things:
    No active port selection:
        1 ) Find the nearest node
        2a) If there is only one output port, select it
        2b) If there are multiple output ports, popup a display to the user to select an output port
    If there is an active port selection:
        1 ) Find nearest node
        2a) If there is only one input port, unconnected, connect it
        2b) If there is only one input port, and it is connected, prompt the user to override the connection
        2c) If there are multiple input ports, prompt the user to select an input port to connect to.  If the user
                selects a port that has a connection, prompt the user to override the connection.
TODO
    *   Case for 0 ports
            Selecting ports
    *   Prompt color nodes
            For when an override is active
    *   Connecting to/found the current node

"""
from qtpy.QtWidgets import QFrame, QVBoxLayout, QLabel
from qtpy.QtCore import Qt

from Katana import Utils, QT4Widgets, QT4GLLayerStack, NodegraphAPI, DrawingModule, ResourceFiles, KatanaPrefs, logging, PrefNames, UI4
from UI4.Tabs.NodeGraphTab.Layers.LinkConnectionLayer import LinkConnectionLayer

from cgwidgets.widgets import ButtonInputWidgetContainer, ButtonInputWidget, FrameInputWidgetContainer
from cgwidgets.utils import centerWidgetOnCursor, setAsBorderless, setAsTransparent, setAsTool
from Utils2 import nodeutils, portutils, getFontSize

main_window = UI4.App.MainWindow.CurrentMainWindow()

INPUT_PORT = 0
OUTPUT_PORT = 1


class OverridePortWarningButtonPopupWidget(QFrame):
    def __init__(self, node, input_port, output_port, parent=None):
        super(OverridePortWarningButtonPopupWidget, self).__init__(parent)
        # setup attrs
        #self._show_noodle = False
        self._output_port = output_port
        # setup layout
        QVBoxLayout(self)
        self._button_widget = OverridePortWarningButtonWidget(node, input_port, output_port)
        self.layout().addWidget(self._button_widget)

        # setup display
        setAsBorderless(self)
        self.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet("""QFrame{border: 1px solid rgba(128,128,255,255); margin: 2px}""")
        if not PortConnector.isSelectionActive():
            PortConnector.showNoodle(output_port)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            # PortConnector.showNoodle(self._output_port)
            self.close()
        ButtonInputWidget.keyPressEvent(self, event)

    def closeEvent(self, event):
        main_window.activateWindow()
        ButtonInputWidget.closeEvent(self, event)

    def leaveEvent(self, event):
        # if self._show_noodle:
        #     PortConnector.showNoodle(self._output_port)
        self.close()
        return ButtonInputWidget.leaveEvent(self, event)


class OverridePortWarningButtonWidget(ButtonInputWidget):
    """ Popup displayed to the user when they attempt to connect a port that already has a connection

    Args:
        node (node):
        input_port (port):
        output_port (port):

    Attributes:
        show_noodle (bool): determines if the noodle should be shown on exit
        input_port (port):
        output_port (port)
    """
    def __init__(self, node, input_port, output_port, parent=None):
        super(OverridePortWarningButtonWidget, self).__init__(parent=parent)

        # setup attrs
        self._input_port = input_port
        self._output_port = output_port
        self._show_noodle = False
        self.setIsToggleable(False)

        # setup display
        self.setText("-- OVERRIDE CONNECTION -- \n {node} | {port}".format(node=node.getName(), port=self._input_port.getName()))
        self.setFixedHeight(getFontSize() * 5)
        setAsBorderless(self)

        # setup events
        self.setUserClickedEvent(self.connectPortsEvent)

    def connectPortsEvent(self, widget):
        self._input_port.connect(self._output_port)
        PortConnector.hideNoodle()
        self.parent().close()


class MultiPortPopupMenuWidget(FrameInputWidgetContainer):
    def __init__(self, node, port_type=OUTPUT_PORT, selected_port=None,  parent=None):
        super(MultiPortPopupMenuWidget, self).__init__(parent)
        # setup attrs
        self._node = node
        #self._show_noodle = False
        self._selected_port = selected_port
        self.setTitle(node.getName())
        self.setIsHeaderEditable(False)
        self.setDirection(Qt.Vertical)

        # create widgets
        self._title_widget = QLabel(node.getName())
        self._title_widget.setAlignment(Qt.AlignCenter)
        self._ports_widget = MultiPortPopupMenu(node, port_type=port_type, selected_port=selected_port,  parent=self)
        self.addInputWidget(self._ports_widget)

        # setup display
        nodeutils.setGlowColor(node, (0.5, 0.5, 1))
        setAsBorderless(self)
        setAsTransparent(self._ports_widget)
        self.setStyleSheet("""QFrame{border: 1px solid rgba(128,128,255,255); margin: 2px}""")
        self.setContentsMargins(2, 2, 2, 2)

        # show noodle
        if port_type == INPUT_PORT:
            if not PortConnector.isSelectionActive():
                PortConnector.showNoodle(selected_port)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._show_noodle = True
            self.close()

        QFrame.keyPressEvent(self, event)

    def closeEvent(self, event):
        main_window.activateWindow()
        # if self._show_noodle:
        #     PortConnector.showNoodle(self._selected_port)

        nodeutils.setGlowColor(self._node, None)

        QFrame.closeEvent(self, event)

    def leaveEvent(self, event):
        QFrame.leaveEvent(self, event)
        self.close()

    def showEvent(self, event):
        return_val = QFrame.showEvent(self, event)
        if self.width() < 200:
            self.setFixedWidth(200)

        return return_val


class MultiPortPopupMenu(ButtonInputWidgetContainer):
    """ Popup widget displayed when the user queries a node with multiple inputs

    This will show the user a list of all of the available ports to be selected.
    If no port is currently selected, this will activate a port selection, if one is
    currently selected, then this will connect the ports.

    Args:
        node (node): node
        ports (list): of ports
        port_type (PORT_TYPE): the type of ports that will be displayed to the user
        selected_port (port): port currently selected

    """
    def __init__(self, node, port_type=OUTPUT_PORT, selected_port=None,  parent=None):
        super(MultiPortPopupMenu, self).__init__(parent, Qt.Vertical)

        # setup attrs
        self._selected_port = selected_port
        self._node = node
        self._port_type = port_type
        self.setIsToggleable(False)

        for port in self.getDisplayPorts():
            self.addButton(port.getName(), port.getName(), self.portSelectedEvent)

    """ EVENTS """
    def portSelectedEvent(self, widget):
        """ Event run when the user selects a port"""
        port = self.getSelectedPort(widget.flag())

        # connect selected ports
        if self._port_type == INPUT_PORT:
            is_connected = portutils.isPortConnected(port)

            # port selected is connected, display warning
            if is_connected:
                main_window._warning_widget = OverridePortWarningButtonPopupWidget(self._node, port, self._selected_port)
                main_window._warning_widget.show()
                centerWidgetOnCursor(main_window._warning_widget, raise_=True)

            # port selected has no connections, connect port
            else:
                self._selected_port.connect(port)
                PortConnector.hideNoodle()

        # show noodle
        elif self._port_type == OUTPUT_PORT:
            PortConnector.showNoodle(port)

        # self.parent()._show_noodle = False
        self.parent().close()

    """ UTILS """
    def getDisplayPorts(self):
        if self._port_type == INPUT_PORT:
            ports = self._node.getInputPorts()
        elif self._port_type == OUTPUT_PORT:
            ports = self._node.getOutputPorts()

        return ports

    def getSelectedPort(self, port_name):
        """ Gets the port from the port name provided

        Args:
            port_name (str): """
        if self._port_type == INPUT_PORT:
            port = self._node.getInputPort(port_name)
        elif self._port_type == OUTPUT_PORT:
            port = self._node.getOutputPort(port_name)

        return port


class PortConnector():
    """ Main function for the port connector display """
    def __init__(self):
        self.output_port = None
        self.main()

    def main(self):
        """ Run when the node is initialized.

        This is the main switch that will determine what should be done.

        1.) This will detect the nearest node to the cursor when the hotkey is pressed.
        2a.) If no port is selected, select a port.  If there are multiple ports on the node,
            then show the user a GUI to select a port
        2b.) If a port is selected, then connect the port.  If multiple ports are available to be
            connected, then show the user a GUI to select a port.
        """
        node = nodeutils.getClosestNode()
        selection_active = PortConnector.isSelectionActive()

        # PORT SELECTED
        if selection_active:
            link_connection_layer = PortConnector.getLinkConnectionLayer()
            if link_connection_layer:
                base_ports = link_connection_layer.getBasePorts()

                # SINGULAR INPUT PORT
                if len(node.getInputPorts()) == 1:
                    input_port = node.getInputPortByIndex(0)
                    is_connected = portutils.isPortConnected(input_port)

                    # prompt user to connect
                    if is_connected:
                        main_window._warning_widget = OverridePortWarningButtonPopupWidget(node, input_port, base_ports[0])
                        main_window._warning_widget.show()
                        centerWidgetOnCursor(main_window._warning_widget)

                    # automagically connect
                    else:
                        for base_port in base_ports:
                            input_port.connect(base_port)
                        PortConnector.hideNoodle()
                # MULTIPLE INPUT PORTS
                elif 1 < len(node.getInputPorts()):
                    main_window._port_popup_menu = MultiPortPopupMenuWidget(node, port_type=INPUT_PORT, selected_port=base_ports[0])
                    main_window._port_popup_menu.show()
                    centerWidgetOnCursor(main_window._port_popup_menu)

        # NOT SELECTED
        else:
            # NO OUTPUT PORTS
            if 0 == len(node.getOutputPorts()):
                return

            # SINGULAR OUTPUT PORT
            if 1 == len(node.getOutputPorts()):
                self.output_port = node.getOutputPorts()[0]
                self.showNoodle(self.output_port)

            # MULTIPLE OUTPUT PORTS
            elif 1 < len(node.getOutputPorts()):
                main_window._port_popup_menu = MultiPortPopupMenuWidget(node)
                main_window._port_popup_menu.show()
                centerWidgetOnCursor(main_window._port_popup_menu)


    @staticmethod
    def getLinkConnectionLayer():
        """ Returns the link interaction layer.

        If it is not the last in the stack, this will return None"""
        nodegraph_tab = UI4.App.Tabs.FindTopTab('Node Graph')
        nodegraph_widget = nodegraph_tab.getNodeGraphWidget()
        last_layer = nodegraph_widget.getLayers()[-1]
        if isinstance(last_layer, LinkConnectionLayer):
            return last_layer

        return None

    @staticmethod
    def isSelectionActive():
        """ Determines if a port selection is active"""
        nodegraph_tab = UI4.App.Tabs.FindTopTab('Node Graph')
        nodegraph_widget = nodegraph_tab.getNodeGraphWidget()
        graph_interaction = nodegraph_widget.getGraphInteraction()
        return not graph_interaction

    @staticmethod
    def hideNoodle():
        """ Hides the noodle, or multiple noodles..."""
        nodegraph_tab = UI4.App.Tabs.FindTopTab('Node Graph')
        nodegraph_widget = nodegraph_tab.getNodeGraphWidget()
        last_layer = nodegraph_widget.getLayers()[-1]
        while isinstance(last_layer, LinkConnectionLayer):
            nodegraph_widget.idleUpdate()
            nodegraph_widget.removeLayer(last_layer)
            nodegraph_tab = UI4.App.Tabs.FindTopTab('Node Graph')
            nodegraph_widget = nodegraph_tab.getNodeGraphWidget()
            last_layer = nodegraph_widget.getLayers()[-1]

    @staticmethod
    def showNoodle(port):
        """ Shows the noodle from the port provided

        Args:
            port (Port): """

        nodegraph_tab = UI4.App.Tabs.FindTopTab('Node Graph')
        nodegraph_widget = nodegraph_tab.getNodeGraphWidget()
        port_layer = nodegraph_widget.getLayerByName("PortInteractions")

        ls = port_layer.layerStack()
        layer = LinkConnectionLayer([port], None, enabled=True)
        ls.appendLayer(layer, stealFocus=True)


PortConnector()