from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin
from PyQt5.QtGui import QIcon

import resources_rc
from ledbuttonwidget import LedButton


class LedButtonPlugin(QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        super(LedButtonPlugin, self).__init__(parent)
        self._initialized = False

        resources_rc

    def initialize(self, editor):
        self._initialized = True

    def isInitialized(self):
        return self._initialized

    def createWidget(self, parent):
        return LedButton(parent)

    def name(self):
        return 'LedButton'

    def group(self):
        return 'PyQt'

    def icon(self):
        return QIcon(":/res/ledbutton.png")

    def toolTip(self):
        return ''

    def whatsThis(self):
        return ''

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="LedButton" name="ledbutton">\n' \
               '</widget>\n'

    def includeFile(self):
        return 'ledbuttonwidget'
