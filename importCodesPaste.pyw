# from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtWidgets
import sqlite3
import re
from ui.importWindowPaste import Ui_ImportWindow


class Import(Ui_ImportWindow):
    def __init__(self):
        self.ImportWindow = QtWidgets.QWidget()
        self.setupUi(self.ImportWindow)
        self.ImportWindow.show()

        # self.ButtonImport.clicked.connect(self.importcodes)
        self.ButtonImport.clicked.connect(self.importcodes)
        self.ButtonClose.clicked.connect(self.close)

    def getCodes(self):
        text = self.plainTextEditCodes.toPlainText()
        # codeRegex = re.compile(r'\d\d\d-\d\d\d')
        codes = re.findall(r'\d\d\d\d\d-\d\d\d\d\d', text)
        return codes

    def importcodes(self):
        codes = self.getCodes()
        # Datenbank öffnen
        verbindung = sqlite3.connect("wlan-code.db")
        c = verbindung.cursor()
        duplicates = 0
        if codes != []:
            for i in codes:
                #  Wenn code nicht in db -> [], dann anlegen, sonst nichts tun
                db = list(c.execute(""" SELECT code FROM codes
                                WHERE code = ?
                            """,
                                    (i,)))
                if db == []:
                    # anlegen
                    c.execute(""" INSERT INTO codes
                                ("code", "used", "runtime")
                                VALUES (?,0,?); """,
                              (i, int(self.spinBoxRuntime.text())))
                    verbindung.commit()
                else:
                    duplicates += 1

            c.close()
            verbindung.close()
            self.message = QtWidgets.QMessageBox()
            self.message.setIcon(QtWidgets.QMessageBox.Information)
            self.message.setWindowTitle("Import")
            self.message.setText(str(len(codes)-duplicates) +
                                 " Codes wurden importiert. " + 
                                 str(duplicates) + " Duplikat(e).")
            self.message.exec_()
        else:
            c.close()
            verbindung.close()
            self.message = QtWidgets.QMessageBox()
            self.message.setIcon(QtWidgets. QMessageBox.Warning)
            self.message.setWindowTitle("Import")
            self.message.setText("Es sind keine Codes im Format XXXXX-XXXXX " +
                                 "vorhanden.")
            self.message.exec_()

    def close(self):
        self.ImportWindow.close()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Import()
    sys.exit(app.exec_())
