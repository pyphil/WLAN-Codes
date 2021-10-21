from PyQt6 import QtGui, QtWidgets
from ui.mainwindow import Ui_MainWindow
from ui.codeabruf import Ui_CodeAbrufen
from ui.fullscreen import Ui_Fullscreen
from ui.authDialog import Ui_Login
from os import getlogin, urandom, path
from datetime import datetime
import sqlite3
import pdfexport
import hashlib
# finding regular expressions
import re
from ui.importWindowPaste import Ui_ImportWindow
from ui.Einstellungen import Ui_Einstellungen
from ui.firstpasswd import Ui_PasswortEinrichtung


class Database():
    def __init__(self):
        self.verbindung = sqlite3.connect("wlan-code.db")
        self.c = self.verbindung.cursor()
        self.username = getlogin()
        # zu Beginn alte Codes löschen
        # TODO erst beim Abrufen löschen
        self.deleteOldCodes()

    def count(self):
        """ Zählt die Anzahl Codes für die Laufzeiten
        zwischen 1 und 12 Stunden und gibt nur die vorhandenen
        Laufzeiten zurück
        """
        count = []
        for i in range(1, 13):
            item = list(self.c.execute("""SELECT count(*) FROM codes
                                          WHERE runtime = ? AND
                                          used = 0
                                       """,
                                       (i,)))
            if item[0][0] != 0:
                count.append((i, item[0][0]))

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
                liste.append(
                    [codes[i][0], str(restzeit)+" Minuten", codes[i][2]])

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


class Authentication():
    def __init__(self, db):
        self.db = db

    def newPW(self, password):
        user = "admin"

        # Salt generieren und hash zu Passwort erzeugen
        salt = urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt, 100000)

        # User, salt und hash in Datenbank speichern
        verbindung = sqlite3.connect("wlan-code.db")
        c = verbindung.cursor()
        c.execute(""" CREATE TABLE account(user VARCHAR(20), salt BINARY(128),
                    key BINARY(128))
                    """)

        c.execute(""" INSERT INTO account (user, salt, key) VALUES (?, ?, ?)
                """,
                  (user, salt, key))
        verbindung.commit()
        c.close()
        verbindung.close()

    def updatePW(self, password):
        # Salt generieren und hash zu Passwort erzeugen
        salt = urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt, 100000)

        # User, salt und hash in Datenbank speichern
        verbindung = sqlite3.connect("wlan-code.db")
        c = verbindung.cursor()

        c.execute(""" UPDATE account
                    SET salt = ?, key = ?
                    WHERE user = "admin"
                """,
                  (salt, key))

        verbindung.commit()
        c.close()
        verbindung.close()

    def login(self, pw):
        # get salt and key (hash) from database
        salt_key = list(self.db.c.execute(""" SELECT salt, key FROM account
                                WHERE user = "admin"
                            """,
                                          ))

        salt = salt_key[0][0]
        key = salt_key[0][1]

        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            # Convert the password to bytes
            pw.encode('utf-8'),
            salt,
            100000
        )

        if new_key == key:
            return True


class CodeAbruf(Ui_CodeAbrufen, QtWidgets.QDialog):
    hours = []

    def __init__(self, generator, db):
        super(CodeAbruf, self).__init__(generator.MainWindow)
        self.generator = generator
        self.db = db

        self.setupUi(self)
        self.show()

        # Stylesheet non-editable Combobox ändern
        self.comboBoxLaufzeit.setStyleSheet("combobox-popup: 0;")

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
            self.message.setIcon(QtWidgets.QMessageBox().icon().Warning)
            self.message.setWindowTitle("Laufzeit")
            self.message.setWindowIcon(QtGui.QIcon("images/icon.ico"))
            self.message.setText("Bitte eine Laufzeit angeben.")
            self.message.exec()
        else:
            # Code aus db holen und anzeigen
            self.generator.label.setText(self.db.getCode(hours))
            self.generator.pushButton_2.setEnabled(True)
            self.generator.pushButton_3.setEnabled(True)
            self.generator.updateStatusbar()
            self.close()

    def abbrechen(self):
        self.close()


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


class FirstPassword(Ui_PasswortEinrichtung, QtWidgets.QDialog):
    def __init__(self, main):
        super(FirstPassword, self).__init__(main.MainWindow)
        self.setupUi(self)
        self.show()
        self.main = main

        self.pushButtonOK.clicked.connect(self.setPW)
        self.pushButtonAbbrechen.clicked.connect(self.abbrechen)
        self.lineEditNeuPW.setFocus()

    def setPW(self):
        self.newPW = self.lineEditNeuPW.text()
        self.newPW_2 = self.lineEditWdhNeuPW.text()
        # check new Password
        if len(self.newPW) < 8:
            # Password check dialogues
            msg = QtWidgets.QMessageBox(self.main.MainWindow)
            msg.setIcon(QtWidgets.QMessageBox().icon().Warning)
            msg.setWindowTitle("Fehler")
            msg.setWindowIcon(QtGui.QIcon("images/icon.ico"))
            msg.setText("Das gewählte Passwort ist nicht lang genug.\n" +
                        "Es muss mindestens 8 Zeichen enthalten.")
            msg.exec()
        elif self.newPW != self.newPW_2:
            msg = QtWidgets.QMessageBox(self.main.MainWindow)
            msg.setIcon(QtWidgets.QMessageBox().icon().Warning)
            msg.setWindowTitle("Fehler")
            msg.setWindowIcon(QtGui.QIcon("images/icon.ico"))
            msg.setText("Die beiden Passwörter sind nicht identisch.")
            msg.exec()
        else:
            # db zunächst erstellen
            verbindung = sqlite3.connect("wlan-code.db")
            c = verbindung.cursor()
            c.execute(""" CREATE TABLE "codes" (
                        "code"	TEXT,
                        "used"	INTEGER,
                        "username"	TEXT,
                        "time"	TEXT,
                        "runtime"	INTEGER
                    ) 
                    """,
                      )
            verbindung.commit()
            c.close()
            verbindung.close()

            self.main.loadDB()
            self.auth = Authentication(self.main.db)
            self.auth.newPW(self.newPW)
            self.close()

    def abbrechen(self):
        self.close()
        sys.exit(app.exit())


class Einstellungen(Ui_Einstellungen, QtWidgets.QDialog):
    def __init__(self, main):
        super(Einstellungen, self).__init__(main.MainWindow)
        self.setupUi(self)
        self.show()
        self.main = main

        self.pushButtonOK.clicked.connect(self.ok)
        self.pushButtonAbbrechen.clicked.connect(self.abbrechen)
        self.lineEditAktPW.setFocus()

    def ok(self):
        oldPW = self.lineEditAktPW.text()
        self.newPW = self.lineEditNeuPW.text()
        self.newPW_2 = self.lineEditWdhNeuPW.text()

        self.auth = Authentication(self.main.db)
        result = self.auth.login(oldPW)

        if result:
            self.changePW()
        else:
            msg = QtWidgets.QMessageBox(self.main.MainWindow)
            msg.setIcon(QtWidgets.QMessageBox().icon().Warning)
            msg.setWindowTitle("Fehler")
            msg.setWindowIcon(QtGui.QIcon("images/icon.ico"))
            msg.setText("Das aktuelle Passwort ist nicht korrekt.")
            msg.exec()

    def changePW(self):
        # check new Password
        if len(self.newPW) < 8:
            msg = QtWidgets.QMessageBox(self.main.MainWindow)
            msg.setIcon(QtWidgets.QMessageBox().icon().Warning)
            msg.setWindowTitle("Fehler")
            msg.setWindowIcon(QtGui.QIcon("images/icon.ico"))
            msg.setText("Das gewählte Passwort ist nicht lang genug.\n" +
                        "Es muss mindestens 8 Zeichen enthalten.")
            msg.exec()
        elif self.newPW != self.newPW_2:
            msg = QtWidgets.QMessageBox(self.main.MainWindow)
            msg.setIcon(QtWidgets.QMessageBox().icon().Warning)
            msg.setWindowTitle("Fehler")
            msg.setWindowIcon(QtGui.QIcon("images/icon.ico"))
            msg.setText("Die beiden Passwörter sind nicht identisch.")
            msg.exec()
        else:
            self.auth.updatePW(self.newPW)
            self.close()

    def abbrechen(self):
        self.close()


class Login(Ui_Login, QtWidgets.QDialog):
    def __init__(self, main, target):
        super(Login, self).__init__(main.MainWindow)
        self.setupUi(self)
        self.show()

        self.main = main
        self.target = target

        self.pushButtonOK.clicked.connect(self.ok)
        self.pushButtonAbbrechen.clicked.connect(self.abbrechen)

        self.lineEditPW.setFocus()

    def ok(self):
        password = self.lineEditPW.text()

        auth = Authentication(self.main.db)
        result = auth.login(password)

        if result:
            # Gewünschtes Objekt instanziieren
            if self.target == "codeimport":
                self.codeimportdial = Import(self.main)
                self.close()
            elif self.target == "einstellungen":
                self.close()
                self.einstellungen = Einstellungen(self.main)
        else:
            msg = QtWidgets.QMessageBox(self.main.MainWindow)
            msg.setIcon(QtWidgets.QMessageBox().icon().Warning)
            msg.setWindowTitle("Fehler")
            msg.setWindowIcon(QtGui.QIcon("images/icon.ico"))
            msg.setText("Das Passwort ist nicht korrekt.")
            msg.exec()

    def abbrechen(self):
        self.close()


class Import(Ui_ImportWindow, QtWidgets.QDialog):
    def __init__(self, main):
        super(Import, self).__init__(main.MainWindow)
        self.setupUi(self)
        self.show()

        # self.ButtonImport.clicked.connect(self.importcodes)
        self.ButtonImport.clicked.connect(self.importcodes)
        self.ButtonClose.clicked.connect(self.closeWindow)

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
            self.message.setIcon(QtWidgets.QMessageBox().icon().Information)
            self.message.setWindowTitle("Import")
            self.message.setWindowIcon(QtGui.QIcon("images/icon.ico"))
            self.message.setText(str(len(codes)-duplicates) +
                                 " Codes wurden importiert. " +
                                 str(duplicates) + " Duplikat(e).")
            self.message.exec()
        else:
            c.close()
            verbindung.close()
            self.message = QtWidgets.QMessageBox()
            self.message.setIcon(QtWidgets.QMessageBox().icon().Warning)
            self.message.setWindowTitle("Import")
            self.message.setWindowIcon(QtGui.QIcon("images/icon.ico"))
            self.message.setText("Es sind keine Codes im Format XXXXX-XXXXX " +
                                 "vorhanden.")
            self.message.exec()

    def closeWindow(self):
        self.close()


class Generator(Ui_MainWindow):
    def __init__(self):
        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)
        self.MainWindow.show()

        # Kopfzeile der Tabelle festlegen
        headers = ["Code", "Restzeit mind."]
        self.tableWidget.setHorizontalHeaderLabels(headers)

        # Signals and Slots
        self.pushButton.clicked.connect(self.newcode)
        self.tabWidget.tabBarClicked.connect(self.updateTab)
        self.pushButton_2.clicked.connect(self.fullscreen)
        self.tableWidget.clicked.connect(self.enableButton)
        self.pushButton_4.clicked.connect(self.fullscreen)
        self.pushButton_3.clicked.connect(self.export)
        self.pushButton_5.clicked.connect(self.exportRunningCode)

        # Menu
        self.actionCodes_importieren.triggered.connect(self.codeimport)
        self.actionBeenden.triggered.connect(lambda x: self.MainWindow.close())
        self.actionEinstellungen.triggered.connect(self.einstellungen)
        self.actionInfo.triggered.connect(self.showInfo)

        # Datenbankobjekt instanziieren
        # TODO Wenn db nicht vorhanden, erstellen und Passworteinrichtung
        if path.exists("wlan-code.db"):
            self.loadDB()
        else:
            self.passwortEinrichtung = FirstPassword(self)

    def loadDB(self):
        print("go")
        self.db = Database()
        # Statusbar bei Start füllen
        self.updateStatusbar()

    def codeimport(self):
        # Login vorgeschaltet, Übergabe des Zieldialogs durch "codeimport"
        self.logindialog = Login(self, "codeimport")

    def einstellungen(self):
        self.logindialog = Login(self, "einstellungen")

    def updateStatusbar(self):
        """ Holt im Datenankobjekt die verfügbaren Anzahlen der Codes
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
            self.tableWidget.setItem(
                i, 0, QtWidgets.QTableWidgetItem(self.rcodes[i][0]))
            self.tableWidget.setItem(
                i, 1, QtWidgets.QTableWidgetItem(self.rcodes[i][1]))

        self.updateStatusbar()

    def fullscreen(self):
        if self.pushButton.sender().objectName() == "pushButton_2":
            self.full = Fullscreen(self.label.text())
        if self.pushButton.sender().objectName() == "pushButton_4":
            self.full = Fullscreen(
                self.rcodes[self.tableWidget.currentRow()][0])

    def enableButton(self):
        self.pushButton_4.setEnabled(True)
        self.pushButton_5.setEnabled(True)

    def export(self):
        pdfexport.makepdf(self.label.text(), CodeAbruf.hours)

    def exportRunningCode(self):
        pdfexport.makepdf(self.rcodes[self.tableWidget.currentRow(
        )][0], self.rcodes[self.tableWidget.currentRow()][2])

    def showInfo(self):
        info = QtWidgets.QMessageBox(self.MainWindow)
        info.setWindowTitle("Über")
        info.setWindowIcon(QtGui.QIcon("images/icon.ico"))
        info.setText("WLAN-Codes 0.9.6 \n\n" +
                     "released under GNU Public License Version 3 \n" +
                     "(https://www.gnu.org/licenses/gpl-3.0.en.html)" + "\n" +
                     "by Philipp Lobe")
        info.exec()


if __name__ == "__main__":
    import sys
    # Scale Factor Rounding Policy
    # default is PassThrough in Qt6 (Round in Qt 5)
    # environ['QT_SCALE_FACTOR_ROUNDING_POLICY'] = 'Round'
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    ui = Generator()
    sys.exit(app.exec())
