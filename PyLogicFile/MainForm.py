from PyQt5.Qt import *
from PyUiFile.mainform import Ui_MainWindow
import pandas as pd
import pyqtgraph as pg
from random import randint
from numpy import trapz
import cgitb

cgitb.enable(format="text")

pg.setConfigOptions(antialias=True)


class MainWin(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        centerWidget = self.takeCentralWidget()
        del centerWidget
        self.setDockNestingEnabled(True)
        self.checkBox_reverseAxis.setChecked(True)
        self.df_oriData: pd.DataFrame = None
        self.df_processData: pd.DataFrame = None

        # 单独设置沉降值计算窗口
        # self.tableWidget_SettlementDisplay.action_drawFigure.setVisible(False)
        self.tableWidget_SettlementDisplay.action_CalculateSettlement.setVisible(False)
        self.tableWidget_SettlementDisplay.action_insertcol.setVisible(False)
        self.tableWidget_SettlementDisplay.action_insertrow.setVisible(False)

        # 右键菜单设置
        self.tableWidget_SettlementDisplay.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.propertyWin.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)

        self.dockWidget_4.setFixedWidth(386)
        self.radioButtonOriData.setChecked(True)

        # 菜单项图片设置
        self.action_datafromExcel.setIcon(QIcon("Images/导入数据.png"))
        self.action_outputGrayModelData.setIcon(QIcon("Images/导出数据.png"))
        self.action_newTable.setIcon(QIcon("Images/新建表格.png"))

        self.connectSlotFunction()

        # 工具栏设置
        self.toolBar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)
        self.toolBar.addAction(self.action_newTable)
        self.toolBar.addAction(self.action_datafromExcel)
        self.action_datafromExcel.setToolTip("从Excel文件导入数据")
        self.toolBar.addAction(self.action_outputGrayModelData)
        self.action_outputGrayModelData.setToolTip("灰色理论预测数据导出")

        # 布局
        self.customLayout()

    def connectSlotFunction(self):
        self.action_exit.triggered.connect(self.deleteLater)
        self.action_newTable.triggered.connect(self.newTable)
        self.action_datafromExcel.triggered.connect(self.inputData)
        self.radioButton_ProcessData.toggled[bool].connect(self.changeData1)
        self.radioButtonOriData.toggled[bool].connect(self.changeData2)
        self.pushButton_draw.clicked.connect(self.drawOriginData)
        self.pushButton_reset.clicked.connect(self.ori_reset)
        self.pushButton_clearPicture.clicked.connect(self.ori_plot_win.plotItem.clear)
        self.tableWidget.Signal_CalculateSettlement.connect(self.calculateSettlement)
        self.tableWidget_SettlementDisplay.action_drawFigure.disconnect()
        self.tableWidget_SettlementDisplay.action_drawFigure.triggered.connect(self.drawSettlementFigure)


    def drawSettlementFigure(self):
        selections = self.tableWidget_SettlementDisplay.selectedRanges()
        if len(selections) == 0:
            return
        self.predictPlotWin.addLegend(offset=(50, 50))
        # self.ori_plot_win.plotItem.showGrid(x=True, y=True, alpha = 0.4)  # 设置绘图部件显示网格线
        self.predictPlotWin.plotItem.clear()
        labels = [self.tableWidget_SettlementDisplay.horizontalHeaderItem(i).text() for i in
                  range(self.tableWidget_SettlementDisplay.columnCount())]
        data = []
        for selection in selections:
            toprow = selection.topRow()
            bottomrow = selection.bottomRow()
            leftcolumn = selection.leftColumn()
            rightcolumn = selection.rightColumn()
            for col in range(leftcolumn, rightcolumn + 1, 1):
                lst = []
                for row in range(toprow, bottomrow + 1, 1):
                    lst.append(float(self.tableWidget_SettlementDisplay.item(row, col).text()))
                data.append((labels[col], lst))

        for index in range(1, len(data)):
            self.predictPlotWin.plotItem.plot(x=data[0][1], y=data[index][1],
                                            pen=(randint(0, 255), randint(0, 255), randint(0, 255)),symbolBrush=(randint(0, 255), randint(0, 255), randint(0, 255)), symbolPen='w', symbol='o', symbolSize=7)

        self.predictPlotWin.setLabel('left', self.tableWidget_SettlementDisplay.horizontalHeaderItem(1).text())
        self.predictPlotWin.setLabel('bottom', self.tableWidget_SettlementDisplay.horizontalHeaderItem(0).text())

    def calculateSettlement(self):
        selections = self.tableWidget.selectedRanges()
        if len(selections) == 0:
            return

        if len(selections) >= 2:
            QMessageBox.warning(self, "错误提示", "您不能对多重选择区域进行此操作")
            return
        selection = selections[0]
        toprow = selection.topRow()
        bottomrow = selection.bottomRow()
        leftcolumn = selection.leftColumn()
        rightcolumn = selection.rightColumn()
        labels = [self.tableWidget.horizontalHeaderItem(i).text() for i in range(self.tableWidget.columnCount())]
        datas = []

        x_lst = []
        for j in range(toprow, bottomrow + 1):
            x_lst.append(self.tableWidget.item(j, leftcolumn).text())
        x_lst = list(map(float, x_lst))

        for i in range(leftcolumn+1, rightcolumn + 1):
            lst = []
            title = labels[i]
            for j in range(toprow, bottomrow + 1):
                lst.append(self.tableWidget.item(j, i).text())
            lst = list(map(float, lst))
            ret = abs(trapz(lst, x_lst, dx=0.01) / 1000)
            datas.append((title, round(ret, 4)))

        self.tableWidget_SettlementDisplay.setColumnCount(2)
        self.tableWidget_SettlementDisplay.setRowCount(len(datas))
        self.tableWidget_SettlementDisplay.setHorizontalHeaderLabels(['开采范围(cm)', '沉降值(mm)'])

        for j in range(len(datas)):
            self.tableWidget_SettlementDisplay.setItem(j ,0, QTableWidgetItem(str(datas[j][0])))
            self.tableWidget_SettlementDisplay.setItem(j, 1, QTableWidgetItem(str(datas[j][1])))
        self.dockWidget_3.raise_()


    def customLayout(self):
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_4)
        self.setLayoutDirection(Qt.LeftToRight)
        self.dockWidget_2.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.dockWidget_3.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.tabifyDockWidget(self.dockWidget, self.dockWidget_2)
        self.tabifyDockWidget(self.dockWidget, self.dockWidget_3)
        # self.setTabPosition(Qt.LeftDockWidgetArea, QTabWidget.West)
        self.dockWidget.raise_()
        self.splitter_2.setStretchFactor(0, 3.5)
        self.splitter_2.setStretchFactor(1, 6.5)
        self.splitter_3.setStretchFactor(0, 7)
        self.splitter_3.setStretchFactor(1, 3)

    def ori_reset(self):
        self.lineEdit_horizontalAxisTitle.clear()
        self.lineEdit_verticalAxisTitle.clear()
        self.lineEdit_verticalAxisUnits.clear()
        self.lineEdit_horizontalAxisUnits.clear()
        self.checkBox_reverseAxis.setChecked(True)

    def drawOriginData(self):

        selections = self.tableWidget.selectedRanges()
        self.ori_plot_win.addLegend(offset=(50, 50))
        # self.ori_plot_win.plotItem.showGrid(x=True, y=True, alpha = 0.4)  # 设置绘图部件显示网格线
        self.ori_plot_win.plotItem.clear()
        labels = [self.tableWidget.horizontalHeaderItem(i).text() for i in
                  range(self.tableWidget.columnCount())]
        data = []
        for selection in selections:
            toprow = selection.topRow()
            bottomrow = selection.bottomRow()
            leftcolumn = selection.leftColumn()
            rightcolumn = selection.rightColumn()
            for col in range(leftcolumn, rightcolumn + 1, 1):
                lst = []
                for row in range(toprow, bottomrow + 1, 1):
                    lst.append(float(self.tableWidget.item(row, col).text()))
                data.append((labels[col], lst))
        # 设置坐标轴信息
        xtitle = self.lineEdit_horizontalAxisTitle.text()
        xunits = self.lineEdit_horizontalAxisUnits.text()
        ytitle = self.lineEdit_verticalAxisTitle.text()
        yunits = self.lineEdit_verticalAxisUnits.text()
        if xtitle == "":
            x = ""
        else:
            if xunits == "":
                x = xtitle
            else:
                x = "{}({})".format(xtitle, xunits)

        if ytitle == "":
            y = ""
        else:
            if yunits == "":
                y = ytitle
            else:
                y = "{}({})".format(ytitle, yunits)
        if self.checkBox_reverseAxis.isChecked():
            self.ori_plot_win.setLabel('left', y)
            self.ori_plot_win.setLabel('bottom', x)
            # 绘图
            for index in range(1, len(data)):
                self.ori_plot_win.plotItem.plot(y=data[0][1], x=data[index][1], name=data[index][0],
                                                pen=(randint(0, 255), randint(0, 255), randint(0, 255)))
        else:
            self.ori_plot_win.setLabel('left', y)
            self.ori_plot_win.setLabel('bottom', x)
            # 绘图
            for index in range(1, len(data)):
                self.ori_plot_win.plotItem.plot(x=data[0][1], y=data[index][1], name=data[index][0],
                                                pen=(randint(0, 255), randint(0, 255), randint(0, 255)))

    def changeData1(self, val: bool):
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

    def changeData2(self, val: bool):
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
        # filename, ok = QFileDialog.getOpenFileName(self, "数据导入", ".", "Excel Files(*.xlsx *.xls)")
        filename = r"C:\Users\hejinyang\Desktop\V1.xlsx"
        ok = True
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
                    data[df.columns[i]] = list(map(lambda x: round(x, 5), series.tolist()))
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
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(20)
        self.tableWidget.setRowCount(100)
        self.tableWidget.setHorizontalHeaderLabels(["untitled"+str(i) for i in range(20)])
