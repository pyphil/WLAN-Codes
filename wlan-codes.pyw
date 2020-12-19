from PyQt5 import QtCore, QtGui, QtWidgets        
from ui.mainwindow import Ui_MainWindow
from ui.codeabruf import Ui_CodeAbrufen
from ui.fullscreen import Ui_Fullscreen
from os import getlogin
from datetime import datetime
import sqlite3
import pdfexport


class Database():
    def __init__(self):
        self.verbindung = sqlite3.connect("wlan-code.db")
        self.c = self.verbindung.cursor()
        self.username = getlogin()
        # zu Beginn alte Codes zu löschen
        self.deleteOldCodes()

    def count(self):
        """ Zählt die Anzahl Codes für die Laufzeiten
        zwischen 1 und 12 Stunden und gibt nur die vorhandenen
        Laufzeiten zurück
        """
        count = []
        for i in range(1,13):
            item = list(self.c.execute("""SELECT count(*) FROM codes 
                                          WHERE runtime = ? AND
                                          used = 0
                                       """,
                                       (i,)))
            if item[0][0] != 0:
                count.append((i,item[0][0]))

        return count

    def getCodelist(self, h):
        """ erstellt eine Liste aller unverbrauchten Codes """
        codes = list(self.c.execute("""SELECT code FROM codes
                                    WHERE used = 0 AND runtime = ?
                                    """,
                                    (h,)))
        return codes
    
    def getCode(self, h):
        """ Holt einen neuen Code aus der db und markiert
        diesen direkt als 'used' und setzt time und username
        """
        codes = self.getCodelist(h)
        
        time = datetime.now()
        self.c.execute(""" UPDATE codes SET used=1, username=?, time=?
                           WHERE code=?
                       """,
                       (self.username, time, codes[0][0]))
        self.verbindung.commit()

        return codes[0][0]

    def getRunningCodes(self):
        """ Filtert die laufenden Codes (60 Minuten) und 
        erstellt eine Liste. Führt die Methode zum 
        Löschen aller abgelaufenen Codes aus.
        """
        codes = list(self.c.execute("""SELECT code, time, runtime FROM codes
                                       WHERE used = 1 AND username = ?
                                       ORDER BY time ASC
                                    """,
                                   (self.username,)))
        liste = []
        time = datetime.now()
        for i in range(len(codes)):
            # Zeit aus db in datetime konvertieren
            time2 = datetime.strptime(codes[i][1], "%Y-%m-%d %H:%M:%S.%f")
            # Restzeit berechnen
            diff = time - time2
            runtimeToMin = codes[i][2]*60
            restzeit = runtimeToMin-int(diff.total_seconds()/60)
            if restzeit > 0:
                liste.append([codes[i][0],str(restzeit)+" Minuten",codes[i][2]])
        
        self.deleteOldCodes()
        
        return liste

    def deleteOldCodes(self):
        """ löscht abgelaufene Codes aller Nutzer """
        # Gesamtliste holen
        usedcodes = list(self.c.execute("""SELECT code, time from codes
                                       WHERE used = 1 
                                    """,
                                   ))
        # Liste der zu löschenden Codes erstellen
        liste_del = []
        time = datetime.now()
        for i in range(len(usedcodes)):
            # Zeit aus db in datetime konvertieren
            time2 = datetime.strptime(usedcodes[i][1], "%Y-%m-%d %H:%M:%S.%f")
            # Restzeit berechnen
            diff = time - time2
            restzeit = 60-int(diff.total_seconds()/60)
            if restzeit <= 0:
                liste_del.append([usedcodes[i][0]])
        
        # abgelaufene Codes löschen
        for i in range(len(liste_del)):
            self.c.execute(""" DELETE FROM codes
                            WHERE code=?
                        """,
                        (liste_del[i][0],))
            self.verbindung.commit()
        

class CodeAbruf(Ui_CodeAbrufen):
    hours = []
    
    def __init__(self, generator, db):
        self.generator = generator
        self.db = db
        
        self.CodeAbrufen = QtWidgets.QWidget()
        self.setupUi(self.CodeAbrufen)
        self.CodeAbrufen.show()

        self.count = self.db.count()

        for i in self.count:
            if i[0] == 1:
                self.comboBoxLaufzeit.addItem(str(i[0])+" Stunde")
            else:
                self.comboBoxLaufzeit.addItem(str(i[0])+" Stunden")


        self.pushButtonOK.clicked.connect(self.ok)
        self.pushButtonAbbrechen.clicked.connect(self.abbrechen)

    def ok(self):
        """ Fragt die Laufzeit ab und holt einen Code aus der DB """
        # Auswahl aus der Combobox in Variable speichern 
        hours = self.count[self.comboBoxLaufzeit.currentIndex()][0]
        CodeAbruf.hours = hours

        if self.comboBoxLaufzeit.currentIndex() == -1:
            self.message = QtWidgets.QMessageBox()
            self.message.setIcon(QtWidgets.QMessageBox.Warning)
            self.message.setWindowTitle("Laufzeit")
            self.message.setText("Bitte eine Laufzeit angeben.")
            self.message.exec_()
        else:
            # Code aus db holen und anzeigen
            self.generator.label.setText(self.db.getCode(hours))
            self.generator.pushButton_2.setEnabled(True)
            self.generator.pushButton_3.setEnabled(True)
            self.generator.updateStatusbar()
            self.CodeAbrufen.close()
    
    def abbrechen(self):
        self.CodeAbrufen.close()

class Fullscreen(Ui_Fullscreen):
    def __init__(self, code):
        self.Fullscreen = QtWidgets.QWidget()
        self.setupUi(self.Fullscreen)
        self.Fullscreen.showFullScreen()

        self.code = code

        self.labelCode.setText(code)
        self.pushButtonClose.clicked.connect(self.close)

    def close(self):
        self.Fullscreen.close()

class Generator(Ui_MainWindow):
    def __init__(self):
        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)
        self.MainWindow.show()
        
        # Kopfzeile der Tabelle festlegen
        headers = ["Code","Restzeit mind."]
        self.tableWidget.setHorizontalHeaderLabels(headers)

        # Signals and Slots
        self.pushButton.clicked.connect(self.newcode)
        self.tabWidget.tabBarClicked.connect(self.updateTab)
        self.pushButton_2.clicked.connect(self.fullscreen)
        self.tableWidget.clicked.connect(self.enableButton)
        self.pushButton_4.clicked.connect(self.fullscreen)
        self.pushButton_3.clicked.connect(self.export)
        self.pushButton_5.clicked.connect(self.exportRunningCode)

        # Datenbankobjekt instanziieren
        self.db = Database()
        
        # Statusbar bei Start füllen
        self.updateStatusbar()

    def updateStatusbar(self):
        """ Holt im Datenankobjekt die verfübaren Anzahlen der Codes
        und baut einen String für die Statuszeile
        """
        statustext = " verfügbar: "
        count = self.db.count()
        for i in range(len(count)):
            statustext += str(count[i][0])+"h: "+str(count[i][1])+" Stk.  "
        self.statusbar.showMessage(statustext)

    def newcode(self):
        """ instanziiert de Dialog zum Codeabruf und übergibt db und
        sich selbst
        """
        self.abrufDialog = CodeAbruf(self, self.db)

    def updateTab(self):
        """ wird ausgeführt, wenn der zweite Tab 'Laufende
        Codes' angelickt wird und erstellt dabei die Tabelle und
        aktualisiert die Statuszeile
        """
        self.rcodes = self.db.getRunningCodes()
        self.tableWidget.setRowCount(len(self.rcodes))
        
        for i in range(len(self.rcodes)):
            self.tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(self.rcodes[i][0]))
            self.tableWidget.setItem(i,1,QtWidgets.QTableWidgetItem(self.rcodes[i][1]))

        self.updateStatusbar()

    def fullscreen(self):
        if self.pushButton.sender().objectName() == "pushButton_2":
            self.full = Fullscreen(self.label.text())
        if self.pushButton.sender().objectName() == "pushButton_4":
            self.full = Fullscreen(self.rcodes[self.tableWidget.currentRow()][0])
            
    def enableButton(self):
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
    def export(self):
        pdfexport.makepdf(self.label.text(),CodeAbruf.hours)

    def exportRunningCode(self):
        pdfexport.makepdf(self.rcodes[self.tableWidget.currentRow()][0],self.rcodes[self.tableWidget.currentRow()][2])

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    # app.setAttribute(QtCore.Qt.AA_Use96Dpi)
    # app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    ui = Generator()
    sys.exit(app.exec_())
