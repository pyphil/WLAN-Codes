from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak
import subprocess
from os import environ

def makepdf(code, time):
    if time == 1:
        time = str(time)+" Stunde"
    else:
        time = str(time)+" Stunden"
    
    # Definieren der Styles
    style = getSampleStyleSheet()

    # Anlegen einer Liste, welche den Seiteninhalt enthält
    story = []

    # Generieren von Inhalt
    story.append(Paragraph('WLAN-Code: '+code,style['Heading1']))
    story.append(Paragraph('Laufzeit des Codes: '+time,style['Heading2']))
    story.append(Paragraph('Netzwerk-Name (SSID): Schueler',style['Heading2']))
    story.append(Paragraph('Die Laufzeit des Codes beginnt mit der ersten Einwahl eines Gerätes.',style['BodyText']))

    # Anlegen des PDFs
    home = environ['HOMEDRIVE']+environ['HOMEPATH']
    filename = home + '\\Downloads\\Code.pdf'
    pdf = SimpleDocTemplate(filename,pagesize=A4)
    pdf.build(story)

    # PDF anzeigen
    subprocess.call("C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe "+filename)
    #system("del "+filename)

if __name__ == "__main__":
    makepdf("012345",2)