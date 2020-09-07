################################
#########    COLORS    ###########
################################

""" BLOCK / PATTERN """
# item bg color
# push button hover color
""" ACCEPTS / DECLINE / MAYBE"""
def convertToHoverColor(rgba, hover_mult=1.5):
    """
    """
    new_color = []
    for value in rgba:
        value *= hover_mult
        if 255 < value:
            value = 255
        new_color.append(int(value))

    return tuple(new_color)


ACCEPT_COLOR_RGBA = (64, 128, 64, 255)
CANCEL_COLOR_RGBA = (128, 64, 64, 255)
MAYBE_COLOR_RGBA = (64, 64, 128, 255)
ERROR_COLOR_RGBA = (192, 0, 0, 255)

ACCEPT_HOVER_COLOR_RGBA = convertToHoverColor(ACCEPT_COLOR_RGBA)
CANCEL_HOVER_COLOR_RGBA = convertToHoverColor(CANCEL_COLOR_RGBA)
MAYBE_HOVER_COLOR_RGBA = convertToHoverColor(MAYBE_COLOR_RGBA)
ERROR_HOVER_COLOR_RGBA = convertToHoverColor(ERROR_COLOR_RGBA)

GRID_COLOR = (10, 95, 20, 255)
GRID_HOVER_COLOR = convertToHoverColor(GRID_COLOR)
# hacky color resets
TEXT_COLOR = (192, 192, 192, 255)
KATANA_YELLOW = (255, 200, 0, 255)
