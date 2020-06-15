
from PyQt5.Qt import *
from typing import *

class CpPasteTable(QTableWidget):

    def __init__(self, parent=None):
        super(CpPasteTable, self).__init__(parent)
        self.popmenu = QMenu(self)

        self.action_copy = QAction("复制", self.popmenu)
        self.action_copy.triggered.connect(self.copy)

        self.action_paste = QAction("粘贴", self.popmenu)
        self.action_paste.triggered.connect(self.paste)

        self.action_shear = QAction("剪切", self.popmenu)
        self.action_shear.triggered.connect(self.shear)

        self.action_delete = QAction("清空", self.popmenu)
        self.action_delete.triggered.connect(self.deleteContent)

        lst = [
            self.action_copy,
            self.action_shear,
            self.action_paste,

            self.action_delete,

        ]
        self.popmenu.addActions(lst)
        self.customContextMenuRequested.connect(self.showPopMenu)

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

    def deleteContent(self):
        try:
            selectedRanges: List[QTableWidgetSelectionRange] = self.selectedRanges()
            for selectedRange in selectedRanges:
                for i in range(selectedRange.topRow(), selectedRange.bottomRow() + 1):
                    for j in range(selectedRange.leftColumn(), selectedRange.rightColumn() + 1):
                        self.item(i, j).setText("")
        except Exception as e:
            print(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno, sep='\t\t\t')
