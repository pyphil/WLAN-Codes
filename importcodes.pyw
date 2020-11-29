from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
from ui.importWindow import Ui_ImportWindow


class Import(Ui_ImportWindow):
    def __init__(self):
        self.ImportWindow = QtWidgets.QWidget()
        self.setupUi(self.ImportWindow)
        self.ImportWindow.show()

        self.ButtonDateiname.clicked.connect(self.getFilename)
        self.ButtonImport.clicked.connect(self.importcodes)
        self.ButtonClose.clicked.connect(self.close)

    def getFilename(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()
        self.lineEditDateiname.setText(filename[0])


    def importcodes(self):
        try:
            # Exportdatei öffnen, Datenbank öffnen
            f = open(self.lineEditDateiname.text(),'r',encoding="utf-8")
            verbindung = sqlite3.connect("wlan-code.db")
            c = verbindung.cursor()

            for zeile in f:
                # Zeilenumbruch entfernen
                zeile = zeile.rstrip()
                #  Wenn code nicht in db -> [], dann anlegen, sonst nichts tun
                db = list(c.execute(""" SELECT code FROM codes
                                WHERE code = ?
                            """,
                            (zeile,)))
                if db == []:
                    # anlegen
                    c.execute(""" INSERT INTO codes
                                ("code", "used", "runtime")
                                VALUES (?,0,?); """, 
                                (zeile,int(self.spinBoxRuntime.text())))
                    verbindung.commit()           
                else:
                    pass

            f.close()
            c.close()
            verbindung.close()
            self.message = QtWidgets.QMessageBox()
            self.message.setIcon(QtWidgets. QMessageBox.Information)
            self.message.setWindowTitle("Import")
            self.message.setText("Codes wurden importiert.")
            self.message.exec_()
        except:
            f.close()
            c.close()
            verbindung.close()
            self.message = QtWidgets.QMessageBox()
            self.message.setIcon(QtWidgets. QMessageBox.Warning)
            self.message.setWindowTitle("Import")
            self.message.setText("Datei nicht kompatibel.")
            self.message.exec_()

    def close(self):
        self.ImportWindow.close()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Import()
    sys.exit(app.exec_())