# Form implementation generated from reading ui file '.\ui\Einstellungen.ui'
#
# Created by: PyQt6 UI code generator 6.1.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Einstellungen(object):
    def setupUi(self, Einstellungen):
        Einstellungen.setObjectName("Einstellungen")
        Einstellungen.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        Einstellungen.resize(276, 229)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui\\../images/icon.ico"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        Einstellungen.setWindowIcon(icon)
        self.gridLayout_2 = QtWidgets.QGridLayout(Einstellungen)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.pushButtonOK = QtWidgets.QPushButton(Einstellungen)
        self.pushButtonOK.setDefault(True)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.gridLayout.addWidget(self.pushButtonOK, 0, 0, 1, 1)
        self.pushButtonAbbrechen = QtWidgets.QPushButton(Einstellungen)
        self.pushButtonAbbrechen.setObjectName("pushButtonAbbrechen")
        self.gridLayout.addWidget(self.pushButtonAbbrechen, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 8, 0, 1, 1)
        self.label = QtWidgets.QLabel(Einstellungen)
        font = QtGui.QFont()
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Einstellungen)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEditAktPW = QtWidgets.QLineEdit(Einstellungen)
        self.lineEditAktPW.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEditAktPW.setClearButtonEnabled(True)
        self.lineEditAktPW.setObjectName("lineEditAktPW")
        self.gridLayout_2.addWidget(self.lineEditAktPW, 2, 0, 1, 1)
        self.lineEditNeuPW = QtWidgets.QLineEdit(Einstellungen)
        self.lineEditNeuPW.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEditNeuPW.setClearButtonEnabled(True)
        self.lineEditNeuPW.setObjectName("lineEditNeuPW")
        self.gridLayout_2.addWidget(self.lineEditNeuPW, 4, 0, 1, 1)
        self.lineEditWdhNeuPW = QtWidgets.QLineEdit(Einstellungen)
        self.lineEditWdhNeuPW.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEditWdhNeuPW.setClearButtonEnabled(True)
        self.lineEditWdhNeuPW.setObjectName("lineEditWdhNeuPW")
        self.gridLayout_2.addWidget(self.lineEditWdhNeuPW, 6, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(Einstellungen)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 5, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(Einstellungen)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 7, 0, 1, 1)

        self.retranslateUi(Einstellungen)
        QtCore.QMetaObject.connectSlotsByName(Einstellungen)
        Einstellungen.setTabOrder(self.lineEditAktPW, self.lineEditNeuPW)
        Einstellungen.setTabOrder(self.lineEditNeuPW, self.lineEditWdhNeuPW)
        Einstellungen.setTabOrder(self.lineEditWdhNeuPW, self.pushButtonOK)
        Einstellungen.setTabOrder(self.pushButtonOK, self.pushButtonAbbrechen)

    def retranslateUi(self, Einstellungen):
        _translate = QtCore.QCoreApplication.translate
        Einstellungen.setWindowTitle(_translate("Einstellungen", "Einstellungen"))
        self.pushButtonOK.setText(_translate("Einstellungen", "OK"))
        self.pushButtonAbbrechen.setText(_translate("Einstellungen", "Abbrechen"))
        self.label.setText(_translate("Einstellungen", "Administrator-Passwort ändern"))
        self.label_2.setText(_translate("Einstellungen", "Aktuelles Passwort:"))
        self.label_4.setText(_translate("Einstellungen", "Wiederholung neues Passwort:"))
        self.label_3.setText(_translate("Einstellungen", "Neues Passwort:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Einstellungen = QtWidgets.QDialog()
    ui = Ui_Einstellungen()
    ui.setupUi(Einstellungen)
    Einstellungen.show()
    sys.exit(app.exec())
