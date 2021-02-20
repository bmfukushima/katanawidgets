import math
#from cgwidgets.interface.AbstractUtilsInterfaceAPI import disconnectNode, connectInsideGroup
try:
    import NodegraphAPI
except ModuleNotFoundError:
    pass


def disconnectNode(node, input=False, output=False, reconnect=False):
    """
    Disconnects the node provide from all other nodes.  The same
    as hitting 'x' on the keyboard... or "Extract Nodes" except this
    is in the NodegraphWidget, not the NodegraphAPI. so kinda hard
    to call... so I made my own...

    Args:
        node (node): Node to be extracted
        input (bool): If true disconnect all input ports
        output (bool): If true disconnect all output ports
        reconnect (bool): If true, will rewire the node graphs input/output ports
            will only work if input and output are true
    """
    if reconnect is True:
        if input is True and output is True:
            input_port = node.getInputPortByIndex(0)
            upstream_port = input_port.getConnectedPorts()[0]
            output_port = node.getOutputPortByIndex(0)
            downstream_port = output_port.getConnectedPorts()[0]

            if upstream_port and downstream_port:
                # reconnect wire
                upstream_port.connect(downstream_port)

    if input is True:
        for input_port in node.getInputPorts():
            output_ports = input_port.getConnectedPorts()
            for port in output_ports:
                port.disconnect(input_port)

    if output is True:
        for output in node.getOutputPorts():
            input_ports = output.getConnectedPorts()
            for port in input_ports:
                port.disconnect(output)


def connectInsideGroup(node_list, parent_node):
    """
    Connects all of the nodes inside of a specific node in a linear fashion

    Args:
        node_list (list): list of nodes to be connected together, the order
            of the nodes in this list, will be the order that they are connected in
        parent_node (node): node have the nodes from the node_list
            wired into.
    """
    import NodegraphAPI
    send_port = parent_node.getSendPort('in')
    return_port = parent_node.getReturnPort('out')
    if len(node_list) == 0:
        send_port.connect(return_port)
    elif len(node_list) == 1:
        node_list[0].getOutputPortByIndex(0).connect(return_port)
        node_list[0].getInputPortByIndex(0).connect(send_port)
    elif len(node_list) == 2:
        node_list[0].getInputPortByIndex(0).connect(send_port)
        node_list[1].getOutputPortByIndex(0).connect(return_port)
        node_list[0].getOutputPortByIndex(0).connect(node_list[1].getInputPortByIndex(0))
        NodegraphAPI.SetNodePosition(node_list[0], (0, 100))
    elif len(node_list) > 2:
        for index, node in enumerate(node_list[:-1]):
            node.getOutputPortByIndex(0).connect(node_list[index+1].getInputPortByIndex(0))
            NodegraphAPI.SetNodePosition(node, (0, index * -100))
        node_list[0].getInputPortByIndex(0).connect(send_port)
        node_list[-1].getOutputPortByIndex(0).connect(return_port)
        NodegraphAPI.SetNodePosition(node_list[-1], (0, len(node_list) * -100))


def toggleTwoFacedNodeAppearance(node):
    display_mode_param = node.getParameter('display_mode')
    display_mode = display_mode_param.getValue(0)
    display_mode_param.setValue(math.fabs(display_mode - 1))


def insertNode(node, parent_node):
    """
    Inserts the node in the correct position in the Nodegraph, and then
    wires the node into that position.

    Note:
        When this happens, the node has already been connected..
        Thus the awesome -2

    Args:
        node (node): Current node to be inserted
        parent_node (node): The current nodes parent
    """
    # get previous port / position

    if len(parent_node.getChildren()) == 1:
        # previous port
        previous_port = parent_node.getSendPort('in')

        # position
        pos = (0, 0)
    else:
        # get previous node
        node_references = parent_node.getParameter('nodeReference')
        previous_node_name = node_references.getChildByIndex(node_references.getNumChildren() - 2)
        previous_node = NodegraphAPI.GetNode(previous_node_name.getValue(0))

        # previous port
        previous_port = previous_node.getOutputPortByIndex(0)

        # setup pos
        current_pos = NodegraphAPI.GetNodePosition(previous_node)
        xpos = current_pos[0]
        ypos = current_pos[1] - 100
        pos = (xpos, ypos)

    # wire node
    previous_port.connect(node.getInputPortByIndex(0))
    node.getOutputPortByIndex(0).connect(parent_node.getReturnPort('out'))

    # position node
    NodegraphAPI.SetNodePosition(node, pos)


def createIOPorts(node, in_port=True, out_port=True, connect=True, force_create=True):

    if in_port is True:
        if force_create:
            node.addInputPort('in')
        else:
            if len(node.getInputPorts()) == 0:
                node.addInputPort('in')

    if out_port is True:
        if force_create:
            node.addOutputPort('out')
        else:
            if len(node.getOutputPorts()) == 0:
                node.addOutputPort('out')
    if connect is True:
        if in_port is True and out_port is True:
            node.getSendPort('in').connect(node.getReturnPort('out'))