# --coding: utf8--
# @Time  : 2020/6/12 13:09
# @author: hejinyang
# @File  : ExtendedTableWidget.py

from PyQt5.Qt import *
from PyUiFile.rowdialog import Ui_rowDialog
from PyUiFile.coldialog import Ui_coldialog
from PyUiFile.propertywin import Ui_Dialog
from typing import *

import cgitb
cgitb.enable(format="text")

class propertyDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        super(propertyDialog, self).__init__(parent)
        self.setupUi(self)
        self.tableWidget.verticalHeader().hide()
        self.pushButtonOk.clicked.connect(self.confirm)
        self.pushButton_reset.clicked.connect(self.reset)
        self.tableWidget.setRowCount(self.parent().columnCount())

    def confirm(self):
        try:
            lst = []
            for i in range(self.tableWidget.rowCount()):
                lst.append(self.tableWidget.item(i, 1).text())
            self.parent().setHorizontalHeaderLabels(lst)
            col_num = self.spinBox_colnum.value()
            row_num = self.spinBox_rownum.value()
            self.parent().setColumnCount(col_num)
            self.parent().setRowCount(row_num)
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def reset(self):
        try:
            self.tableWidget.clear()
            self.tableWidget.setHorizontalHeaderLabels(['列号', '列标题'])
            for i in range(self.parent().columnCount()):
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                item = self.tableWidget.item(i, 0)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if self.parent().horizontalHeaderItem(i) is not None:
                    self.tableWidget.setItem(i, 1, QTableWidgetItem(self.parent().horizontalHeaderItem(i).text()))
                else:
                    self.tableWidget.setItem(i, 1, QTableWidgetItem("untitled"+str(i + 1)))
            self.spinBox_colnum.setValue(self.parent().columnCount())
            self.spinBox_rownum.setValue(self.parent().rowCount())
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')


class ColDialog(QDialog, Ui_coldialog):

    def __init__(self, parent=None):
        super(ColDialog, self).__init__(parent)
        self.setupUi(self)
        self.radioButton_beforecol.setChecked(True)
        self.checknum = 1
        self.radioButton_beforecol.toggled[bool].connect(self.changeState1)
        self.radioButton_aftercol.toggled[bool].connect(self.changeState2)

    def changeState1(self, val):
        if val:
            self.checknum = 1

    def changeState2(self, val):
        if val:
            self.checknum = 2


class RowDialog(QDialog, Ui_rowDialog):

    def __init__(self, parent=None):
        super(RowDialog, self).__init__(parent)
        self.setupUi(self)
        self.radioButton_beforerow.setChecked(True)
        self.checknum = 1
        self.radioButton_beforerow.toggled[bool].connect(self.changeState1)
        self.radioButton_afterrow.toggled[bool].connect(self.changeState2)

    def changeState1(self, val):
        if val:
            self.checknum = 1

    def changeState2(self, val):
        if val:
            self.checknum = 2


class ExtendedTableWidget(QTableWidget):

    Signal_CalculateSettlement = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.popmenu = QMenu(self)
        self.cnt = 0

        self.action_copy = QAction("复制", self.popmenu)
        self.action_copy.triggered.connect(self.copy)

        self.action_CalculateSettlement = QAction("沉降值计算", self.popmenu)
        self.action_CalculateSettlement.triggered.connect(self.emitSignal_CalculateSettlement)

        self.action_paste = QAction("粘贴", self.popmenu)
        self.action_paste.triggered.connect(self.paste)

        self.action_shear = QAction("剪切", self.popmenu)
        self.action_shear.triggered.connect(self.shear)

        self.action_selectAll = QAction("全选", self.popmenu)
        self.action_selectAll.triggered.connect(self.selectAll)

        self.action_delete = QAction("清空", self.popmenu)
        self.action_delete.triggered.connect(self.deleteContent)

        self.action_removerow = QAction("删除选中行", self.popmenu)
        self.action_removerow.triggered.connect(self.removeSelectedRow)

        self.action_removecol = QAction("删除选中列", self.popmenu)
        self.action_removecol.triggered.connect(self.removeSelectedCol)

        self.action_insertrow = QAction("插入行", self.popmenu)
        self.action_insertrow.triggered.connect(self.InsertRow)

        self.action_insertcol = QAction("插入列", self.popmenu)
        self.action_insertcol.triggered.connect(self.InsertCol)

        self.action_modifyColumnTitle = QAction("修改列标题", self.popmenu)
        self.action_modifyColumnTitle.triggered.connect(self.modifyColumnTitle)

        self.action_propertySet = QAction("表格属性设置", self.popmenu)
        self.action_propertySet.triggered.connect(self.setTableProperty)

        self.propertyWin = propertyDialog(self)
        self.propertyWin.hide()

        self.action_drawFigure = QAction("绘图", self.popmenu)
        self.action_drawFigure.triggered.connect(self.drawFigure)
        self.popmenu.addAction(self.action_drawFigure)
        self.popmenu.addAction(self.action_CalculateSettlement)


        self.popmenu.addSeparator()

        lst = [
            self.action_copy,
            self.action_shear,
            self.action_paste,

            self.action_selectAll,
            self.action_delete,
            self.action_insertrow,
            self.action_insertcol,

            self.action_removerow,
            self.action_removecol,
            self.action_modifyColumnTitle,
            self.action_propertySet

        ]
        self.popmenu.addActions(lst[:3])
        self.popmenu.addSeparator()
        self.popmenu.addActions(lst[3:7])
        self.popmenu.addSeparator()
        self.popmenu.addActions(lst[7:])
        self.customContextMenuRequested.connect(self.showPopMenu)


    def emitSignal_CalculateSettlement(self):
        self.Signal_CalculateSettlement.emit()


    def drawFigure(self):
        mainWin = self.parent().parent().parent()
        mainWin.dockWidget_2.raise_()
        mainWin.drawOriginData()



    def modifyColumnTitle(self):
        try:
            selection = self.selectedRanges()[0]
            labels = [self.horizontalHeaderItem(i).text() for i in range(self.columnCount())]
            ret, ok = QInputDialog.getText(self, "列标题设置", "请输入列标题", text="列标题{}".format(self.cnt))
            if ok:
                labels[selection.leftColumn()] = ret
                self.cnt += 1
                self.setHorizontalHeaderLabels(labels)
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')



    def setTableProperty(self):
        try:
            self.propertyWin.tableWidget.setRowCount(self.columnCount())
            for i in range(self.columnCount()):
                self.propertyWin.tableWidget.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                item = self.propertyWin.tableWidget.item(i, 0)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if self.horizontalHeaderItem(i) is not None:
                    self.propertyWin.tableWidget.setItem(i, 1, QTableWidgetItem(self.horizontalHeaderItem(i).text()))
                else:
                    self.propertyWin.tableWidget.setItem(i, 1, QTableWidgetItem(str(i + 1)))

            self.propertyWin.spinBox_colnum.setValue(self.columnCount())
            self.propertyWin.spinBox_rownum.setValue(self.rowCount())
            self.propertyWin.show()
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def InsertRow(self):
        try:
            rowdialog = RowDialog(self)
            if rowdialog.exec_() == QDialog.Accepted:
                if rowdialog.checknum == 1:  # 选中行之前插入
                    selecedrange = self.selectedRanges()[0]
                    toprow = selecedrange.topRow()
                    num, ok = QInputDialog.getInt(self, "插入行", "请输入要插入的行数:", 0, 0, 100, 1)
                    if ok:
                        for i in range(num):
                            self.insertRow(toprow)
                elif rowdialog.checknum == 2:
                    selecedrange = self.selectedRanges()[0]
                    bottom_row = selecedrange.bottomRow()
                    num, ok = QInputDialog.getInt(self, "插入行", "请输入要插入的行数:", 0, 0, 100, 1)
                    if ok:
                        for i in range(num):
                            self.insertRow(bottom_row + 1)
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def InsertCol(self):
        try:
            coldialog = ColDialog(self)
            if coldialog.exec_() == QDialog.Accepted:
                if coldialog.checknum == 1:  # 选中行之前插入
                    selecedrange = self.selectedRanges()[0]
                    leftcol = selecedrange.leftColumn()
                    num, ok = QInputDialog.getInt(self, "插入行", "请输入要插入的列数:", 1, 0, 100, 1)
                    if ok:
                        for i in range(num):
                            self.insertColumn(leftcol)
                elif coldialog.checknum == 2:
                    selecedrange = self.selectedRanges()[0]
                    rightcol = selecedrange.rightColumn()
                    num, ok = QInputDialog.getInt(self, "插入行", "请输入要插入的列数:", 1, 0, 100, 1)
                    if ok:
                        for i in range(num):
                            self.insertColumn(rightcol + 1)
        except Exception as e:

            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def removeSelectedRow(self):
        try:
            cols = self.columnCount()
            selectedranges = self.selectedRanges()
            for selectedrange in selectedranges[::-1]:
                col_begin = selectedrange.leftColumn()
                col_end = selectedrange.rightColumn()
                if col_end - col_begin + 1 == cols:  # 选中行
                    top_row = selectedrange.topRow()
                    print(top_row)
                    for i in range(selectedrange.rowCount()):
                        self.removeRow(top_row)
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def removeSelectedCol(self):
        try:
            rows = self.rowCount()
            selectedranges = self.selectedRanges()
            for selectedrange in selectedranges[::-1]:
                row_begin = selectedrange.topRow()
                row_end = selectedrange.bottomRow()
                if row_end - row_begin + 1 == rows:  # 选中行
                    left_col = selectedrange.leftColumn()
                    for i in range(selectedrange.columnCount()):
                        self.removeColumn(left_col)
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def deleteContent(self):
        try:
            selectedRanges: List[QTableWidgetSelectionRange] = self.selectedRanges()
            for selectedRange in selectedRanges:
                for i in range(selectedRange.topRow(), selectedRange.bottomRow() + 1):
                    for j in range(selectedRange.leftColumn(), selectedRange.rightColumn() + 1):
                        item = self.takeItem(i, j)
                        del item
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def copy(self):
        try:
            selectedRanges: List[QTableWidgetSelectionRange] = self.selectedRanges()
            if len(selectedRanges) > 1:
                QMessageBox.warning(self, "错误操作", "您不能对多重区域进行复制操作", QMessageBox.Yes)
                return
            selectedRange = selectedRanges[0]
            s = ""
            for i in range(selectedRange.topRow(), selectedRange.bottomRow() + 1):
                rowS = ""
                for j in range(selectedRange.leftColumn(), selectedRange.rightColumn() + 1):
                    item = self.item(i, j)
                    if j == selectedRange.rightColumn():
                        if item is None:
                            rowS += '' + "\n"
                        else:
                            rowS += item.text() + "\n"
                    else:
                        if item is None:
                            rowS += '' + "\t"
                        else:
                            rowS += item.text() + "\t"
                s += rowS
            QApplication.clipboard().setText(s)
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def paste(self):
        try:
            selectedRange: QTableWidgetSelectionRange = self.selectedRanges()[0]
            row = selectedRange.topRow()
            col = selectedRange.leftColumn()
            DList: List[List[str]] = []
            s = QApplication.clipboard().text()
            lst = s.split('\n')[:-1]
            for rowStr in lst:
                DList.append(rowStr.split('\t'))
            for i in range(row, row + len(DList)):
                for j in range(col, col + len(DList[0])):
                    if self.item(i, j) is None:
                        self.setItem(i, j, QTableWidgetItem(DList[i - row][j - col]))
                    else:
                        self.item(i, j).setText(DList[i - row][j - col])
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def shear(self):
        try:
            selectedRanges: List[QTableWidgetSelectionRange] = self.selectedRanges()
            if len(selectedRanges) > 1:
                QMessageBox.warning(self, "错误操作", "您不能对多重区域进行剪切操作", QMessageBox.Yes)
                return
            selectedRange = selectedRanges[0]
            s = ""
            for i in range(selectedRange.topRow(), selectedRange.bottomRow() + 1):
                rowS = ""
                for j in range(selectedRange.leftColumn(), selectedRange.rightColumn() + 1):
                    item = self.item(i, j)
                    if j == selectedRange.rightColumn():
                        if item is None:
                            rowS += '' + "\n"
                        else:
                            rowS += item.text() + "\n"
                    else:
                        if item is None:
                            rowS += '' + "\t"
                        else:
                            rowS += item.text() + "\t"
                    item = self.takeItem(i, j)
                    del item
                s += rowS
            QApplication.clipboard().setText(s)
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')

    def showPopMenu(self):
        self.popmenu.exec_(QCursor.pos())




