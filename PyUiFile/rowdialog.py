# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rowdialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_rowDialog(object):
    def setupUi(self, rowDialog):
        rowDialog.setObjectName("rowDialog")
        rowDialog.resize(217, 104)
        rowDialog.setMinimumSize(QtCore.QSize(217, 104))
        rowDialog.setMaximumSize(QtCore.QSize(217, 104))
        self.gridLayout_2 = QtWidgets.QGridLayout(rowDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.radioButton_beforerow = QtWidgets.QRadioButton(rowDialog)
        self.radioButton_beforerow.setObjectName("radioButton_beforerow")
        self.gridLayout.addWidget(self.radioButton_beforerow, 0, 0, 1, 2)
        self.radioButton_afterrow = QtWidgets.QRadioButton(rowDialog)
        self.radioButton_afterrow.setObjectName("radioButton_afterrow")
        self.gridLayout.addWidget(self.radioButton_afterrow, 1, 0, 1, 2)
        self.pushButton_ok = QtWidgets.QPushButton(rowDialog)
        self.pushButton_ok.setObjectName("pushButton_ok")
        self.gridLayout.addWidget(self.pushButton_ok, 2, 0, 1, 1)
        self.pushButton_cancel = QtWidgets.QPushButton(rowDialog)
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.gridLayout.addWidget(self.pushButton_cancel, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(rowDialog)
        self.pushButton_ok.clicked.connect(rowDialog.accept)
        self.pushButton_cancel.clicked.connect(rowDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(rowDialog)

    def retranslateUi(self, rowDialog):
        _translate = QtCore.QCoreApplication.translate
        rowDialog.setWindowTitle(_translate("rowDialog", "添加方式选择"))
        self.radioButton_beforerow.setText(_translate("rowDialog", "选中行之前"))
        self.radioButton_afterrow.setText(_translate("rowDialog", "选中行之后"))
        self.pushButton_ok.setText(_translate("rowDialog", "确定"))
        self.pushButton_cancel.setText(_translate("rowDialog", "取消"))
