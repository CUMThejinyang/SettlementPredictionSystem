from PyQt5.Qt import *
from PyUiFile.mainform import Ui_MainWindow
import pandas as pd
import pyqtgraph as pg
from random import randint
from numpy import trapz, array
from PyLogicFile.GrayModel import GrayModel
import cgitb
from typing import *
from prettytable import PrettyTable
from numba import jit

cgitb.enable(format="text")

pg.setConfigOptions(antialias=True)
s = """
<style type="text/css">
table.gridtable {
	font-family: verdana,arial,sans-serif;
	font-size:13px;
	color:#333333;
	border-width: 1px;
	border-color: #666666;
	border-collapse: collapse;

}
table.gridtable th {
	border-width: 1px;
	padding: 8px;
	border-style: solid;
	border-color: #666666;
	background-color: #dedede;
}
table.gridtable td {
	border-width: 1px;
	padding: 8px;
	border-style: solid;
	border-color: #666666;
	background-color: #ffffff;
    text-align: center;
}
</style>
<body>
<table class="gridtable">
"""


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
        self.textBrowser.setContextMenuPolicy(Qt.CustomContextMenu)


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

        # 基础设置
        self.action_clear_output = QAction( "clear", self.textBrowser)
        self.action_clear_output.triggered.connect(self.clearOutput)
        self.textBrowser.addAction(self.action_clear_output)




        # 测试
        self.test()

    def clearOutput(self):
        self.textBrowser.clear()

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
        self.action_RunGrayTheory.triggered.connect(self.getGrayPredictionResult)

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
                                              pen=(randint(0, 255), randint(0, 255), randint(0, 255)),
                                              symbolBrush=(randint(0, 255), randint(0, 255), randint(0, 255)),
                                              symbolPen='w', symbol='o', symbolSize=7)

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

        for i in range(leftcolumn + 1, rightcolumn + 1):
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
            self.tableWidget_SettlementDisplay.setItem(j, 0, QTableWidgetItem(str(datas[j][0])))
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
        self.tableWidget.setHorizontalHeaderLabels(["untitled" + str(i) for i in range(20)])

    def getGrayPredictionResult(self):
        # 1. 获取预测参数
        train_data_length = self.SpinBoxTrainCount.value()
        predict_length = self.SpinBoxPredictCount.value()
        if predict_length == 0:
            self.outputToUser('预测次数为0', 1)
            return
            # 2. 获取数据
        selections = self.tableWidget_SettlementDisplay.selectedRanges()
        if len(selections) == 0:
            self.outputToUser('您没有选择任何数据, 请重新选择后再试', 1)
            return

        if len(selections) >= 2:
            QMessageBox.critical(self, "出现错误", "您不能对多重区域进行此操作", QMessageBox.Yes)
            return

        data = []
        selection = selections[0]
        toprow = selection.topRow()
        bottomrow = selection.bottomRow()
        leftcolumn = selection.leftColumn()
        rightcolumn = selection.rightColumn()
        for col in range(leftcolumn, rightcolumn + 1, 1):
            lst = []
            for row in range(toprow, bottomrow + 1, 1):
                try:
                    lst.append(float(self.tableWidget_SettlementDisplay.item(row, col).text()))
                except Exception:
                    break
            data.append(lst)

        if len(data) == 1:
            predict_data = data[0]
        elif len(data) == 2:
            predict_discription = data[0]
            predict_data = data[1]
        else:
            self.outputToUser('预测数据选择错误, 请重新选择', 1)
            return

        if train_data_length < 3:
            self.outputToUser('模型训练集数据至少三个, 您的输入有误, 已经使用默认值3', 2)
            self.SpinBoxTrainCount.setValue(3)
            train_data_length = 3


        if not any([self.checkBox_CommonGrayModel.isChecked(), self.checkBox_SupplementModel.isChecked(), self.checkBox_MetabolismModel.isChecked()]):
            self.outputToUser('您还未选择灰色理论预测模型, 请选择后再试!', 1)
            return
        # 建模
        graymodel = GrayModel(array(predict_data[:train_data_length]),
                              array(predict_data[train_data_length:train_data_length + predict_length]),
                              predict_length)
        self.outputToUser(
            f'本次预测使用的训练集数据为{predict_data[:train_data_length]};<br> 测试集数据为{predict_data[train_data_length:train_data_length + predict_length]};<br> 预测次数为{predict_length}:',
            level=4)
        labels = [self.tableWidget_SettlementDisplay.horizontalHeaderItem(i).text() for i in range(self.tableWidget_SettlementDisplay.columnCount())]

        if self.checkBox_CommonGrayModel.isChecked():
            ret = graymodel.ordinaryGMPredict()




            content: str = self.DataFrameToHtml(ret, graymodel.train_length)
            self.outputToUser('采用普通GM(1,1)模型预测结果如下:', level=2)
            self.textBrowser.append(content)
        if self.checkBox_SupplementModel.isChecked():
            ret = graymodel.getGrayNumberFillModelResult()
            content: str = self.DataFrameToHtml(ret, -1)
            self.outputToUser('采用灰数递补模型预测结果如下:', level=2)
            self.textBrowser.append(content)
        if self.checkBox_MetabolismModel.isChecked():
            if predict_length > len(predict_data) - train_data_length:
                self.outputToUser('您选择了新陈代谢模型, 该模型需要实测得数据进行迭代计算, 您提供的数据不足, 无法计算!', level=1)
            else:
                ret = graymodel.getMetabolicModelResult()
                content: str = self.DataFrameToHtml(ret, -1)
                self.outputToUser('采用新陈代谢模型预测结果如下:', level=2)
                self.textBrowser.append(content)



















    @staticmethod
    def DataFrameToPrettyTable(df: pd.DataFrame):
        columns = df.columns
        tb = PrettyTable()
        for title in columns:
            tb.add_column(title, df[title].tolist(), valign='m')
        return tb

    def outputToUser(self, text: str, level: int = 4, bold: bool = True):
        """
        :param text: 输出的内容
        :param level:
        `1`: red
        `2`: blue
        `3`: green
        `4` : black
        :return:
        """
        if level == 4:
            color = 'black'
        elif level == 3:
            color = 'green'
        elif level == 2:
            color = 'blue'
        elif level == 1:
            color = 'red'
        else:
            color = 'black'
        if bold:
            s = f'<font color={color} size="3"><b>{text}</b></font>'
        else:
            s = f'<font color={color} size="3">{text}</font>'
        self.textBrowser.append(s)

    def test(self):
        self.tableWidget_SettlementDisplay.setRowCount(10)
        self.tableWidget_SettlementDisplay.setColumnCount(2)
        self.tableWidget_SettlementDisplay.setHorizontalHeaderLabels(['开挖范围', '沉降值'])
        self.tableWidget_SettlementDisplay.setItem(0, 0, QTableWidgetItem(str(30)))
        self.tableWidget_SettlementDisplay.setItem(1, 0, QTableWidgetItem(str(40)))
        self.tableWidget_SettlementDisplay.setItem(2, 0, QTableWidgetItem(str(50)))
        self.tableWidget_SettlementDisplay.setItem(3, 0, QTableWidgetItem(str(60)))
        self.tableWidget_SettlementDisplay.setItem(4, 0, QTableWidgetItem(str(70)))
        self.tableWidget_SettlementDisplay.setItem(5, 0, QTableWidgetItem(str(80)))
        self.tableWidget_SettlementDisplay.setItem(6, 0, QTableWidgetItem(str(90)))
        self.tableWidget_SettlementDisplay.setItem(7, 0, QTableWidgetItem(str(100)))
        self.tableWidget_SettlementDisplay.setItem(8, 0, QTableWidgetItem(str(110)))
        self.tableWidget_SettlementDisplay.setItem(9, 0, QTableWidgetItem(str(120)))

        self.tableWidget_SettlementDisplay.setItem(0, 1, QTableWidgetItem(str(1.6053)))
        self.tableWidget_SettlementDisplay.setItem(1, 1, QTableWidgetItem(str(2.776)))
        self.tableWidget_SettlementDisplay.setItem(2, 1, QTableWidgetItem(str(3.9751)))
        self.tableWidget_SettlementDisplay.setItem(3, 1, QTableWidgetItem(str(4.4792)))
        self.tableWidget_SettlementDisplay.setItem(4, 1, QTableWidgetItem(str(5.5745)))
        self.tableWidget_SettlementDisplay.setItem(5, 1, QTableWidgetItem(str(7.1783)))
        self.tableWidget_SettlementDisplay.setItem(6, 1, QTableWidgetItem(str(8.889)))
        self.tableWidget_SettlementDisplay.setItem(7, 1, QTableWidgetItem(str(10.9843)))
        self.tableWidget_SettlementDisplay.setItem(8, 1, QTableWidgetItem(str(12.7529)))
        self.tableWidget_SettlementDisplay.setItem(9, 1, QTableWidgetItem(str(13.1359)))
        self.SpinBoxPredictCount.setValue(5)
        self.SpinBoxTrainCount.setValue(6)
        self.checkBox_CommonGrayModel.setChecked(True)

    @staticmethod
    def DataFrameToHtml(df: pd.DataFrame, fit_num: int):
        content = """"""
        columns = df.columns
        content += "<tr>"
        for title in columns:
            content += "<th>{}</th>".format(title)
        content += "</tr>"
        cnt = 0
        for i in range(len(df.index)):
            content += "<tr>"
            for j in range(len(columns)):
                if cnt < fit_num:
                    content += '<td><b>{}</b></td>'.format(df.iloc[i, j])
                else:
                    if isinstance(df.loc[i, '相对误差(%)'], str):
                        content += '<td><b><i><font color="#aaa6ad">{}</font></i></b></td>'.format(df.iloc[i, j])
                    else:
                        if round(df.loc[i, '相对误差(%)'], 3) > 20:
                            content += '<td><font color="red"><b>{}</b></font></td>'.format(df.iloc[i, j])
                        else:
                            content += '<td><font color="green"><b>{}</b></font></td>'.format(df.iloc[i, j])

            cnt += 1
            content += "</tr>"
        content += "</table></body>"
        return s + content
