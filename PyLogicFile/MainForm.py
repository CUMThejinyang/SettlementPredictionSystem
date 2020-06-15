from PyQt5.Qt import *
from PyUiFile.mainform import Ui_MainWindow


class MainWin(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        centerWidget = self.takeCentralWidget()
        del centerWidget
        self.setDockNestingEnabled(True)
        self.dockWidget_4.setMaximumWidth(150)
        self.splitDockWidget(self.dockWidget, self.dockWidget_4, Qt.Horizontal)

        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.propertyWin.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)

        self.action_exit.triggered.connect(self.deleteLater)
        self.tableWidget.setColumnCount(100)
        self.tableWidget.setRowCount(100)
        for i in range(100):
            for j in range(100):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(i * j)))
