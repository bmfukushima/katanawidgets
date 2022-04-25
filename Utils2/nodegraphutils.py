from qtpy.QtCore import QPoint

from Katana import NodegraphAPI, DrawingModule, Utils, KatanaPrefs

# backdrop_nodes = NodegraphAPI.GetAllNodesByType("Backdrop")
#
# pos, root_node = getNodegraphCursorPos()
# active_backdrop_nodes = [backdrop_node for backdrop_node in backdrop_nodes if backdrop_node.getParent() == root_node]
CENTER = 0
TOPRIGHT = 1
TOP = 2
TOPLEFT = 3
LEFT = 4
BOTLEFT = 5
BOT = 6
BOTRIGHT = 7
RIGHT = 8


def getBackdropNodeUnderCursor():
    """ Returns the backdrop node under the cursor"""
    cursor_pos, root_node = getNodegraphCursorPos()
    if not cursor_pos: return None
    backdrop_nodes = NodegraphAPI.GetAllNodesByType("Backdrop")
    active_backdrop_nodes = [backdrop_node for backdrop_node in backdrop_nodes if backdrop_node.getParent() == root_node]

    depth = -10000
    active_backdrop_node = None
    for backdrop_node in active_backdrop_nodes:
        attrs = backdrop_node.getAttributes()
        # position test
        node_pos = NodegraphAPI.GetNodePosition(backdrop_node)

        """ Need to duck type this as the ns_sizeXY is not created until the user
        has resized the backdrop node"""
        try:
            width = attrs["ns_sizeX"]
            height = attrs["ns_sizeY"]
        except KeyError:
            width = 128
            height = 64
        left = node_pos[0] - (width * 0.5)
        top = node_pos[1] + (height * 0.5)
        right = node_pos[0] + (width * 0.5)
        bottom = node_pos[1] - (height * 0.5)

        # position test
        if left < cursor_pos.x() and cursor_pos.x() < right and bottom < cursor_pos.y() and cursor_pos.y() < top:
            # depth test
            if "ns_zDepth" in attrs:
                if depth < attrs["ns_zDepth"]:
                    active_backdrop_node = backdrop_node
                    depth = attrs["ns_zDepth"]

    return active_backdrop_node


def getBackdropQuadrantSelected(backdrop_node):
    """ Takes a backdrop, and returns the quadrant that the user has clicked under

    Assumes a standard cartesian coordinate plane where 1 is in the upper right (+, +)
    then rotates counter clockwise to put 4 in the bottom right (+, -)
    1 = + +
    2 = - +
    3 = - -
    4 = + -

    Returns (Quadrant): TOPLEFT | TOPRIGHT | BOTLEFT | BOTRIGHT """
    cursor_pos, root_node = getNodegraphCursorPos()
    node_pos = NodegraphAPI.GetNodePosition(backdrop_node)
    attrs = backdrop_node.getAttributes()

    # Calculate boundaries
    """ Need to duck type this as the ns_sizeXY is not created until the user
    has resized the backdrop node
    """
    try:
        width = attrs["ns_sizeX"]
        height = attrs["ns_sizeY"]
    except KeyError:
        width = 128
        height = 64

    """ Calculate positions, the points are based off the standard cartesian
    system, where 0 is in the upper right, and 3 is in the bottom right"""
    left = node_pos[0] - (width * 0.5)
    top = node_pos[1] + (height * 0.5)
    right = node_pos[0] + (width * 0.5)
    bottom = node_pos[1] - (height * 0.5)
    width_offset = width / 3
    height_offset = height / 3
    point_00 = QPoint(right - width_offset, top - height_offset)
    point_01 = QPoint(left + width_offset, top - height_offset)
    point_02 = QPoint(left + width_offset, bottom + height_offset)
    point_03 = QPoint(right - width_offset, bottom + height_offset)
    # check if cursor in backdrop
    if left < cursor_pos.x() and cursor_pos.x() < right and bottom < cursor_pos.y() and cursor_pos.y() < top:

        # Top Right
        if point_00.x() < cursor_pos.x() and point_00.y() < cursor_pos.y():
            return TOPRIGHT

        # Top
        elif point_01.x() < cursor_pos.x() and cursor_pos.x() < point_00.x() and point_00.y() < cursor_pos.y():
            return TOP

        # Top Left
        elif cursor_pos.x() < point_01.x() and point_00.y() < cursor_pos.y():
            return TOPLEFT

        # Left
        elif cursor_pos.x() < point_01.x() and cursor_pos.y() < point_00.y() and point_02.y() < cursor_pos.y():
            return LEFT

        # Bottom Left
        elif cursor_pos.x() < point_02.x() and cursor_pos.y() < point_02.y():
            return BOTLEFT

        # Bottom
        elif point_02.x() < cursor_pos.x() and cursor_pos.x() < point_03.x() and cursor_pos.y() < point_02.y():
            return BOT

        # Bottom Right
        elif point_03.x() < cursor_pos.x() and cursor_pos.y() < point_02.y():
            return BOTRIGHT

        # Right
        elif point_00.x() < cursor_pos.x() and cursor_pos.y() < point_00.y() and point_02.y() < cursor_pos.y():
            return RIGHT

        else:
            return CENTER


    return None


def getBackdropChildren(backdrop_node):
    from .widgetutils import getActiveNodegraphWidget
    nodegraph_widget = getActiveNodegraphWidget()

    l, b, r, t = DrawingModule.nodeWorld_getBoundsOfListOfNodes([backdrop_node])
    children = nodegraph_widget.hitTestBox(
        (l, b),
        (r, t),
        viewNode=backdrop_node.getParent()
    )

    selected_nodes = [node for node in children if node is not None]

    return selected_nodes


def getNearestGridPoint(x, y):
    """
    @return: returns an offset of grid units (x, y)
    @x: <float> or <int>
    @y: <float> or <int>

    This should be in the Nodegraph Coordinate System,
    use self.mapToNodegraph() to convert to this sytem
    """
    # pos = NodegraphAPI.GetNodePosition(node)
    from MonkeyPatches.Nodegraph.gridLayer import GRID_SIZE_X_PREF_NAME, GRID_SIZE_Y_PREF_NAME
    grid_x_size = KatanaPrefs[GRID_SIZE_X_PREF_NAME]
    grid_y_size = KatanaPrefs[GRID_SIZE_Y_PREF_NAME]
    x = int(x)
    y = int(y)
    if x % grid_x_size > (grid_x_size * .5):
        x_offset = (x // grid_x_size) + 1
    else:
        x_offset = (x // grid_x_size)
    if y % grid_y_size > (grid_y_size * .5):
        y_offset = (y // grid_y_size) + 1
    else:
        y_offset = (y // grid_y_size)
    return QPoint(x_offset * grid_x_size, y_offset * grid_y_size)


def getNodegraphCursorPos():
    """ Gets the position of the cursor relative to the current cartesian system the mouse is over

    Returns (QPoint, Node)"""
    from .widgetutils import getActiveNodegraphWidget
    nodegraph_widget = getActiveNodegraphWidget()
    # get cursor position
    if not hasattr(nodegraph_widget, "getMousePos"): return
    cursor_pos = nodegraph_widget.getMousePos()
    group_node = nodegraph_widget.getGroupNodeUnderMouse()
    if not cursor_pos: return QPoint(0, 0), group_node

    world_pos = nodegraph_widget.mapFromQTLocalToWorld(cursor_pos.x(), cursor_pos.y())
    cursor_pos = QPoint(*nodegraph_widget.getPointAdjustedToGroupNodeSpace(group_node, world_pos))

    return cursor_pos, group_node


def updateBackdropDisplay(node, attrs=None):
    """ Hacky method to refresh a backdrop nodes by selecting/unselecting it

    Args:
        attrs (dict): of ns attrs for the backdrop, if none are provided,
            this will merely do an update
        node (node):

    """
    if node.getType() == "Backdrop":
        if attrs:
            NodegraphAPI.SetNodeShapeNodeAttrs(node, attrs)

        Utils.EventModule.QueueEvent('node_setShapeAttributes', hash(node), node=node)


        NodegraphAPI.SetNodeSelected(node, True)
        NodegraphAPI.SetNodeSelected(node, False)