import sys
import os

from Katana import UI4, Callbacks, KatanaResources

from cgwidgets.widgets.AbstractWidgets.AbstractScriptEditor.AbstractScriptEditorEventFilter import AbstractEventFilter

SCRIPTS_VARIABLE = "KATANABEBOPSCRIPTS"


class scriptEditorEventFilter(AbstractEventFilter):
    def __init__(self, parent=None):
        main_window = UI4.App.MainWindow.GetMainWindow()
        super(scriptEditorEventFilter, self).__init__(
            parent, main_window=main_window, scripts_variable=SCRIPTS_VARIABLE)


def installPopupHotkeysEventFilter(**kwargs):
    # setup scripts directories
    katana_bebop_scripts_dir = os.environ["KATANABEBOP"] + "/Scripts"
    sandbox_directory = KatanaResources.GetUserKatanaPath() + "/Sandbox"
    try:
        script_directories = os.environ[SCRIPTS_VARIABLE].split(":") + [katana_bebop_scripts_dir, sandbox_directory]
    except KeyError:
        script_directories = [katana_bebop_scripts_dir, sandbox_directory]

    os.environ[SCRIPTS_VARIABLE] = ":".join(script_directories)

    katana_main = UI4.App.MainWindow.GetMainWindow()
    katana_main.event_filter_widget = scriptEditorEventFilter(katana_main)
    katana_main.installEventFilter(katana_main.event_filter_widget)

