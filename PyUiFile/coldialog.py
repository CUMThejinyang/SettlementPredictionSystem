# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'coldialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_coldialog(object):
    def setupUi(self, coldialog):
        coldialog.setObjectName("coldialog")
        coldialog.resize(217, 110)
        coldialog.setMinimumSize(QtCore.QSize(217, 110))
        coldialog.setMaximumSize(QtCore.QSize(217, 110))
        self.gridLayout_2 = QtWidgets.QGridLayout(coldialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.radioButton_beforecol = QtWidgets.QRadioButton(coldialog)
        self.radioButton_beforecol.setObjectName("radioButton_beforecol")
        self.gridLayout.addWidget(self.radioButton_beforecol, 0, 0, 1, 2)
        self.radioButton_aftercol = QtWidgets.QRadioButton(coldialog)
        self.radioButton_aftercol.setObjectName("radioButton_aftercol")
        self.gridLayout.addWidget(self.radioButton_aftercol, 1, 0, 1, 2)
        self.pushButton_ok = QtWidgets.QPushButton(coldialog)
        self.pushButton_ok.setObjectName("pushButton_ok")
        self.gridLayout.addWidget(self.pushButton_ok, 2, 0, 1, 1)
        self.pushButton_cancel = QtWidgets.QPushButton(coldialog)
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.gridLayout.addWidget(self.pushButton_cancel, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(coldialog)
        self.pushButton_ok.clicked.connect(coldialog.accept)
        self.pushButton_cancel.clicked.connect(coldialog.reject)
        QtCore.QMetaObject.connectSlotsByName(coldialog)

    def retranslateUi(self, coldialog):
        _translate = QtCore.QCoreApplication.translate
        coldialog.setWindowTitle(_translate("coldialog", "添加方式选择"))
        self.radioButton_beforecol.setText(_translate("coldialog", "选中列之前"))
        self.radioButton_aftercol.setText(_translate("coldialog", "选中列之后"))
        self.pushButton_ok.setText(_translate("coldialog", "确定"))
        self.pushButton_cancel.setText(_translate("coldialog", "取消"))
