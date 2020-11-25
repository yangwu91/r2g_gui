#!/usr/bin/env python3
# Before run it on macOS Big Sur, export QT_MAC_WANTS_LAYER=1

import sys
from PyQt5.QtWidgets import QApplication

from r2g_gui.main.operations import R2gMainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    _ = R2gMainWindow()
    sys.exit(app.exec_())
