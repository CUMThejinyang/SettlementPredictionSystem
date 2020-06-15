from PyQt5.Qt import *
from PyUiFile.mainform import Ui_MainWindow
import numpy as np
import pandas as pd
from pyqtgraph.widgets import PlotWidget


class MainWin(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        centerWidget = self.takeCentralWidget()
        del centerWidget
        self.setDockNestingEnabled(True)
        self.dockWidget_4.setMaximumWidth(150)
        self.splitDockWidget(self.dockWidget, self.dockWidget_4, Qt.Horizontal)
        self.df_oriData: pd.DataFrame = None
        self.df_processData: pd.DataFrame = None
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.propertyWin.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.radioButtonOriData.setChecked(True)


        self.action_exit.triggered.connect(self.deleteLater)
        self.action_newTable.triggered.connect(self.newTable)
        self.action_datafromExcel.triggered.connect(self.inputData)
        self.radioButton_ProcessData.toggled[bool].connect(self.changeData1)
        self.radioButtonOriData.toggled[bool].connect(self.changeData2)


    def changeData1(self, val:bool):
        try:
            if val:
                self.tableWidget.clear()
                df = self.df_processData
                col_num = len(df.columns)
                row_num = len(df.index)
                self.tableWidget.setRowCount(row_num)
                self.tableWidget.setColumnCount(col_num)
                labels = list(df.columns)
                labels = map(str, labels)
                self.tableWidget.setHorizontalHeaderLabels(labels)
                for i in range(row_num):
                    for j in range(col_num):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))

        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')


    def changeData2(self, val:bool):
        try:
            if val:
                self.tableWidget.clear()
                df = self.df_oriData
                col_num = len(df.columns)
                row_num = len(df.index)
                self.tableWidget.setRowCount(row_num)
                self.tableWidget.setColumnCount(col_num)
                labels = list(df.columns)
                labels = map(str, labels)
                self.tableWidget.setHorizontalHeaderLabels(labels)
                for i in range(row_num):
                    for j in range(col_num):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def inputData(self):
        filename, ok = QFileDialog.getOpenFileName(self, "数据导入", ".", "Excel Files(*.xlsx *.xls)")
        try:

            if ok:
                df = pd.read_excel(filename)
                col_num = len(df.columns)
                row_num = len(df.index)
                self.tableWidget.setRowCount(row_num)
                self.tableWidget.setColumnCount(col_num)
                labels = list(df.columns)
                labels = map(str, labels)
                self.tableWidget.setHorizontalHeaderLabels(labels)
                self.df_oriData = df
                data = {}
                data[df.columns[0]] = df[df.columns[0]]
                data[df.columns[1]] = df[df.columns[1]]
                for i in range(2, col_num):
                    series = df[df.columns[i]] - df[df.columns[1]]
                    data[df.columns[i]] = list(map(lambda x:round(x, 5), series.tolist()))
                self.df_processData = pd.DataFrame(data)
                if self.radioButtonOriData.isChecked():
                    for i in range(row_num):
                        for j in range(col_num):
                            self.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
                elif self.radioButton_ProcessData.isChecked():
                    new_df = self.df_processData
                    for i in range(row_num):
                        for j in range(col_num):
                            self.tableWidget.setItem(i, j, QTableWidgetItem(str(new_df.iloc[i, j])))


        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def newTable(self):
        self.tableWidget.setColumnCount(50)
        self.tableWidget.setRowCount(100)
