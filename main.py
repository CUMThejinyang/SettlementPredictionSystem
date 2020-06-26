
import sys
from PyQt5.QtWidgets import QApplication
from PyLogicFile.MainForm import MainWin
from PyQt5.QtCore import QTranslator, QCoreApplication, Qt

if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = QTranslator()
    translator.load('./config/qt_zh_CN.qm')
    app.installTranslator(translator)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    win = MainWin()
    win.show()
    sys.exit(app.exec_())


