

a = """
import sys
from qtpy.QtWidgets import QLabel, QApplication
from qtpy.QtCore import Qt

from cgwidgets.utils import centerWidgetOnCursor

#app = QApplication(sys.argv)

class Tester(QLabel):
    def __init__(self):
        #QComboBox.__init__(self, parent)
        super(Tester, self).__init__()
        self.setText("ffffff")

a = Tester()
a.show()
print(a)
"""
exec(a)



