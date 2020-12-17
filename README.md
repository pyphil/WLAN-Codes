[wlan-codes0.9.4](https://github.com/pyphil/WLAN-Codes/releases/download/v0.9.4/wlan-codes0.9.4.zip)
[![paypal](https://www.paypalobjects.com/de_DE/DE/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=8KZ7YQRXBLJD8)
# WLAN-Codes 
*Einfache Ausgabe von WLAN-Codes an Lernende in Bildungseinrichtungen*

**Screenshots**
  
![Image](./images/mainwindow.PNG)
![Image](./images/code_abrufen.PNG)  
![Image](./images/laufende_codes.PNG)

![Image](./images/vollbild.PNG)

**Funktionen**
- Gibt WLAN-Codes aus, die aus einem WLAN-Controller mit verschiedenen Laufzeiten als als multi-use keys für die mehrfache Verwendung durch eine Lerngruppe exportiert worden sind
- Lehrer oder Dozenten können Vollbildmodus den Code für BYOD Geräte am Interactive Whiteboard anzeigen
- Codes können während ihrer Mindestlaufzeit (Laufzeit ab dem Abruf) im Tab "Laufende Codes" erneut angezeigt werden

**Hinzufügen von Codes durch Administratoren**
- Administratoren fügen der Datenbank Codes über ein grafisches Importskript hinzu
- Das Skript erwartet eine Textdatei mit einem Importcode pro Zeile
- Die Codes werden in einer sqlite-DB verwaltet und beim Abruf mit einem Zeitstempel und Benutzername versehen

**BUGS**
- momentan fest eingestellter Export-Ordner für PDF
- vorbereitete DB muss momentan vorhanden sein, sollte aber vom Programm generiert werden

**Geplante Features**
- Import direkt aus PDF Dateien, die sich z.B. aus UniFi Contoller exportieren lassen
