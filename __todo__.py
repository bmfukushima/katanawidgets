"""
TODO: BUGS
    QBasicTimer::start: QBasicTimer can only be used with threads started with QThread
        Seems to be associated with the shoji model view widget???
        https://stackoverflow.com/questions/27131294/error-qobjectstarttimer-qtimer-can-only-be-used-with-threads-started-with-qt
            Bascially... delete on close has an unpredictable order... so pooooooooooooooooooooo
    AbstractParametersDisplayWidget --> populateParameters
        - Certain image nodes (ImageIn) give this error
        - HideTitle Error
        - See below for error log
    Shoji... you mean SLOWJI!! =\

TODO: WISHLIST
    Shoji
        - Hotkeys | Don't seem to register correctly with Katana...
            might need wrapper for delegates?
    GSV / IRFs
        - GSV Utils
    Variable Manager New?
        Move this over to Shoji API
    Popup Hotkey Editor
        Move this over to Shoji API
        Beginning of TansuAPI

"""

# AbstractParametersDisplayWidget | Error Log
"""
[ERROR python.root]: An AttributeError occurred in "Node2DGroup.py": 'Node2DGroupFormWidget' object has no attribute '_Node2DGroupFormWidget__originalPopdownIndent'
    Traceback (most recent call last):
      File "software_python/QT4FormWidgets/v0/ValuePolicy.py", line 401, in _HandleQueuedChanges
      File "Utils/v5/WeakMethod.py", line 37, in __call__
      File "FormMaster/Editors/Teleparam.py", line 135, in valueChangedEvent
      File "FormMaster/Editors/Teleparam.py", line 101, in __buildHostedWidget
      File "FormMaster/KatanaFactory.py", line 341, in buildWidget
      File "software_python/QT4FormWidgets/v0/WidgetFactory.py", line 107, in buildWidget
      File "FormMaster/Editors/Node2DGroup.py", line 30, in __init__
      File "FormMaster/Editors/NodeGroup.py", line 104, in __init__
      File "FormMaster/Editors/HideTitleGroup.py", line 35, in __init__
      File "/media/ssd01/dev/katana/KatanaWidgets/ParameterMenu/CreateParametersMenu.py", line 29, in showPopdownWithCustomMenu
        QT4FormWidgets.GroupFormWidget.originalShowPopdown(self, value)
      File "software_python/QT4FormWidgets/v0/GroupFormWidget.py", line 109, in showPopdown
      File "software_python/QT4FormWidgets/v0/FormWidget.py", line 830, in showPopdown
      File "software_python/QT4FormWidgets/v0/FormWidget.py", line 792, in __buildPopdownArea
      File "FormMaster/Editors/Node2DGroup.py", line 76, in _popdownCreated
    AttributeError: 'Node2DGroupFormWidget' object has no attribute '_Node2DGroupFormWidget__originalPopdownIndent'
"""