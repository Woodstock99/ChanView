#! /usr/bin/env python3
#
#  ChanView v1.07
#
#  LG-TV UM7100PLA (webOS)
#
###############################################################################################################

import tkinter as tk
import tkinter.messagebox as message
import tkinter.filedialog as fdialog
import os

###############################################################################################################

# Senderlisten:  <CHANNEL> / <DTV> / <ITEM>
minorNum, original_network_id, transport_id, service_id, serviceType, servTypText = [], [], [], [], [], []
prNum, frequency, mapAttr, favoriteIdxA, favoriteIdxB, favoriteIdxC, favoriteIdxD = [], [], [], [], [], [], [] 
favoriteIdxE, favoriteIdxF, favoriteIdxG, favoriteIdxH, isInvisable, isBlocked  = [], [], [], [], [], []
isSkipped, isDeleted, isScrambled, vchName, isUserSelCHNo, videoStreamType = [], [], [], [], [], []

# Service-Info:  <astServiceInfo> / <ServCount..>
servCountNr, aucSvcName, usServiceID, bVisibilityFlag, bIsScramble, usLCNValue, ucServiceType, usTPIndex = [],[],[],[],[],[],[],[]

# Satelliten-Info:  <SatRecordInfo>
SatelliteNameHex, Angle, AnglePrec, DirEastWest = [],[],[],[]

# Transponder-Info:  <TPList> / <Record..>
TransponderId, Frequency, Polarisation, SymbolRate, TransmissionSystem, HomeTp = [],[],[],[],[],[]

# Transponder-Parameter:  <stTPRecParams> / <Record..>
uwServiceStartIndex, uwServiceEndIndex, uwServiceCount, nitVersion = [],[],[],[]
channelIndex, frequency2, original_network_id2, transport_id2 = [],[],[],[]

# Tuning-Info:  <astTuningInfo> / <TPCount..>
unFrequency, unTSID, unONID, abwSymbolRate, abwPolarization, abwCodeRate, bwDVBS2 = [],[],[],[],[],[],[] 
abwModulationType, bwDirection, abwAnglePrec, ucAngle, ucNoOfServices, usTPHandle = [],[],[],[],[],[] 


Puffer = []           # alle Dateizeilen
idxITEM = []          # Zeiger auf <ITEM>'s
Aktuelle = []         # Zeiger auf aktuell angezeigte idxITEM[]
idxSID = []           # Zeiger auf <ServCount..>'s
aktSID = []           # Zeiger auf aktuell angezeigte idxSID[]

TLLDatei = ""
GEAENDERT = False

Schrift = "Consolas 9"
Vordergrund = "#ffffcc"
Hintergrund = "#000066"

###############################################################################################################

Master = tk.Tk()
Master.title("LG Channel View")
Master.geometry("+300+0")                                    # Fensterposition
Master.option_add("*Dialog.msg.font", "Helvetica 11")        # Messagebox Schriftart
Master.option_add("*Dialog.msg.wrapLength", "50i")           # Messagebox Zeilenumbruch

AttributP = tk.IntVar()             # verschlüsselt
AttributV = tk.IntVar()             # versteckt
AttributU = tk.IntVar()             # überspringen
AttributS = tk.IntVar()             # gesperrt
AttributL = tk.IntVar()             # löschen

Statusleiste = tk.StringVar()       # Statuszeile
StatusAnzahl = tk.IntVar()          # Statuszeile Anzahl Aktuelle
StatusText = tk.StringVar()         # Stauszeile Text

###############################################################################################################

def Datei_Oeffnen(event=None):    # <Strg+O>

    global TLLDatei

    if GEAENDERT:
        if message.askyesno("Channel View", "\nEs wurden Änderungen vorgenommen. Sollen die gespeichert werden?  "):
            Datei_Speichern()

    Dateipfad = fdialog.askopenfilename(initialdir=".", filetypes=[("LG-Dateien","*.TLL*"),("Alle Dateien","*")])

    if Dateipfad and os.path.isfile(Dateipfad):
        TLLDatei = Dateipfad
        Puffer.clear() 
        with open(Dateipfad, "r") as Datei:
            for Zeile in Datei:
                Puffer.append(Zeile)
        Alle_Anzeigen()

###############################################################################################################

def Datei_Speichern(event=None):    # <Strg+S>

    global TLLDatei

    if GEAENDERT:
        if not os.path.isfile(os.path.splitext(TLLDatei)[0] + ".BAK"):
            os.rename(TLLDatei, os.path.splitext(TLLDatei)[0] + ".BAK")
        else:
            for n in range(2, 100, 1):      # neuer BAK-Dateiname 2-99
                if not os.path.isfile(os.path.splitext(TLLDatei)[0] + ".BAK" + str(n)):    break
            os.rename(TLLDatei, os.path.splitext(TLLDatei)[0] + ".BAK" + str(n))

        TLLDatei_Speichern()
        message.showinfo("Channel View", "\nAlle Änderungen wurden gespeichert.  ")

###############################################################################################################

def Datei_Speichern_Unter():

    global TLLDatei

    Dateipfad = fdialog.asksaveasfilename(initialfile=os.path.basename(TLLDatei), filetypes=[("LG-Dateien","*.TLL*"),("Alle Dateien","*")])

    if Dateipfad:
        TLLDatei = Dateipfad
        TLLDatei_Speichern()
        message.showinfo("Channel View", "\nDie Datei " + os.path.basename(TLLDatei) + " wurde gespeichert.  ")

###############################################################################################################

def TLLDatei_Speichern():

    global GEAENDERT

    with open(TLLDatei, "w") as Datei:
        for i in range(0, len(Puffer)):
            if os.name == "posix":
                Datei.write(Puffer[i].replace('\n', '\r\n'))    # LF -> CR LF 
            else:
                Datei.write(Puffer[i])    # Windows
    GEAENDERT = False

###############################################################################################################

def TLLDatei_in_Puffer():

    global Puffer

    Puffer.clear() 
    with open(TLLDatei, "r") as Datei:
        for Zeile in Datei:
            Puffer.append(Zeile)
    Alle_Anzeigen()

###############################################################################################################

###############################################################################################################

def servTypText_Laden(typ):

    if   typ == "1":    return "SD-TV"
    elif typ == "2":    return "Radio"
    elif typ == "7":    return "Radio"
    elif typ == "10":   return "Radio"
    elif typ == "17":   return "HD-TV"
    elif typ == "22":   return "SD-TV"
    elif typ == "25":   return "HD-TV"
    elif typ == "31":   return "UHD-TV"
    elif typ == "159":  return "UHD-TV"
    else:               return " --- "

###############################################################################################################

def Listen_Loeschen():

    servTypText.clear()
    prNum.clear()
    minorNum.clear()
    original_network_id.clear()
    transport_id.clear()
    service_id.clear()
    serviceType.clear()
    frequency.clear()
    mapAttr.clear()
    favoriteIdxA.clear()
    favoriteIdxB.clear()
    favoriteIdxC.clear()
    favoriteIdxD.clear()
    favoriteIdxE.clear()
    favoriteIdxF.clear()
    favoriteIdxG.clear()
    favoriteIdxH.clear()
    isInvisable.clear()
    isBlocked.clear()
    isSkipped.clear()
    isDeleted.clear()
    isScrambled.clear()
    vchName.clear()
    isUserSelCHNo.clear()
    videoStreamType.clear()

###############################################################################################################

def Listen_Tauschen(i):

    servTypText[i], servTypText[i+1] = servTypText[i+1], servTypText[i]
    prNum[i], prNum[i+1] = prNum[i+1], prNum[i]
    minorNum[i], minorNum[i+1] = minorNum[i+1], minorNum[i]
    original_network_id[i], original_network_id[i+1] = original_network_id[i+1], original_network_id[i]
    transport_id[i], transport_id[i+1] = transport_id[i+1], transport_id[i]
    service_id[i], service_id[i+1] = service_id[i+1], service_id[i]
    serviceType[i], serviceType[i+1] = serviceType[i+1], serviceType[i]
    frequency[i], frequency[i+1] = frequency[i+1], frequency[i]
    mapAttr[i], mapAttr[i+1] = mapAttr[i+1], mapAttr[i]
    favoriteIdxA[i], favoriteIdxA[i+1] = favoriteIdxA[i+1], favoriteIdxA[i]
    favoriteIdxB[i], favoriteIdxB[i+1] = favoriteIdxB[i+1], favoriteIdxB[i]
    favoriteIdxC[i], favoriteIdxC[i+1] = favoriteIdxC[i+1], favoriteIdxC[i]
    favoriteIdxD[i], favoriteIdxD[i+1] = favoriteIdxD[i+1], favoriteIdxD[i]
    favoriteIdxE[i], favoriteIdxE[i+1] = favoriteIdxE[i+1], favoriteIdxE[i]
    favoriteIdxF[i], favoriteIdxF[i+1] = favoriteIdxF[i+1], favoriteIdxF[i]
    favoriteIdxG[i], favoriteIdxG[i+1] = favoriteIdxG[i+1], favoriteIdxG[i]
    favoriteIdxH[i], favoriteIdxH[i+1] = favoriteIdxH[i+1], favoriteIdxH[i]
    isInvisable[i], isInvisable[i+1] = isInvisable[i+1], isInvisable[i]
    isBlocked[i], isBlocked[i+1] = isBlocked[i+1], isBlocked[i]
    isSkipped[i], isSkipped[i+1] = isSkipped[i+1], isSkipped[i]
    isDeleted[i], isDeleted[i+1] = isDeleted[i+1], isDeleted[i]
    isScrambled[i], isScrambled[i+1] = isScrambled[i+1], isScrambled[i]
    vchName[i], vchName[i+1] = vchName[i+1], vchName[i]
    isUserSelCHNo[i], isUserSelCHNo[i+1] = isUserSelCHNo[i+1], isUserSelCHNo[i]
    videoStreamType[i], videoStreamType[i+1] = videoStreamType[i+1], videoStreamType[i]

###############################################################################################################

def Puffer_in_Listen():

    global idxITEM

    for i in range(len(Puffer)):             # erst nach <CHANNEL> suchen
        if Puffer[i] == "<CHANNEL>\n":
            for i in range(len(Puffer)):     # dann nach <DTV> weitersuchen
                if Puffer[i] == "<DTV>\n":
                    i += 1                           # Zeiger auf Ersten <ITEM>
                    idxITEM.clear()
                    Listen_Loeschen()
                    while Puffer[i] != "</DTV>\n":
                        idxITEM.append(i)            # Zeiger-Liste auf <ITEM>'s
                        ITEM_in_Listen(idxITEM[-1])  # Puffer-ITEM in Listen
                        i += 42                      # nächster <ITEM>

###############################################################################################################

def ITEM_in_Listen(i):

    n = Puffer[i+1].find("</", 7)         # Ende suchen -> .find(string, start) 
    prNum.append(Puffer[i+1][7:n])        # <prNum>Wert</prNum>
    n = Puffer[i+2].find("</", 10)
    minorNum.append(Puffer[i+2][10:n])    # <minorNum>Wert</minorNum>
    n = Puffer[i+3].find("</", 21)
    original_network_id.append(Puffer[i+3][21:n])
    n = Puffer[i+4].find("</", 14)
    transport_id.append(Puffer[i+4][14:n])
    n = Puffer[i+6].find("</", 12)
    service_id.append(Puffer[i+6][12:n])
    n = Puffer[i+9].find("</", 13)
    serviceType.append(Puffer[i+9][13:n])
    servTypText.append(servTypText_Laden(serviceType[-1]))   # Klartext: SD, HD, Radio usw.
    n = Puffer[i+11].find("</", 11)
    frequency.append(Puffer[i+11][11:n])
    n = Puffer[i+14].find("</", 9)
    mapAttr.append(Puffer[i+14][9:n])
    n = Puffer[i+16].find("</", 14)
    favoriteIdxA.append(Puffer[i+16][14:n])
    n = Puffer[i+17].find("</", 14)
    favoriteIdxB.append(Puffer[i+17][14:n])
    n = Puffer[i+18].find("</", 14)
    favoriteIdxC.append(Puffer[i+18][14:n])
    n = Puffer[i+19].find("</", 14)
    favoriteIdxD.append(Puffer[i+19][14:n])
    n = Puffer[i+20].find("</", 14)
    favoriteIdxE.append(Puffer[i+20][14:n])
    n = Puffer[i+21].find("</", 14)
    favoriteIdxF.append(Puffer[i+21][14:n])
    n = Puffer[i+22].find("</", 14)
    favoriteIdxG.append(Puffer[i+22][14:n])
    n = Puffer[i+23].find("</", 14)
    favoriteIdxH.append(Puffer[i+23][14:n])
    n = Puffer[i+24].find("</", 13)
    isInvisable.append(Puffer[i+24][13:n])
    n = Puffer[i+25].find("</", 11)
    isBlocked.append(Puffer[i+25][11:n])
    n = Puffer[i+26].find("</", 11)
    isSkipped.append(Puffer[i+26][11:n])
    n = Puffer[i+28].find("</", 11)
    isDeleted.append(Puffer[i+28][11:n])
    n = Puffer[i+31].find("</", 13)
    isScrambled.append(Puffer[i+31][13:n])
    n = Puffer[i+38].find("</", 15)
    isUserSelCHNo.append(Puffer[i+38][15:n])
    n = Puffer[i+39].find("</", 17)
    videoStreamType.append(Puffer[i+39][17:n])

    # Sendername: wenn <vchName> leer oder nur ein Zeichen, dann <hexVchName> laden
    n = Puffer[i+34].find("</", 9)
    if (n-9) < 2:
        n = Puffer[i+32].find("</", 12)
        vchName.append('"' + bytearray.fromhex(Puffer[i+32][12:n]).decode("cp1252") + '"')
    else:
        vchName.append(Puffer[i+34][9:n])

###############################################################################################################

def Listen_in_Puffer(nr):

    global Puffer

    tabelle = str.maketrans({ 'ä':'a','Ä':'A','ö':'o','Ö':'O','ü':'u','Ü':'U','ß':' ',0x05:'' })

    # Hex-Name und Länge ändern
    Puffer[idxITEM[Aktuelle[nr]]+32] = "<hexVchName>" + vchName[nr].encode("cp1252").hex() + "</hexVchName>\n"
    Puffer[idxITEM[Aktuelle[nr]]+33] = "<notConvertedLengthOfVchName>" + str(len(vchName[nr])) + "</notConvertedLengthOfVchName>\n"

    vchName[nr] = vchName[nr].translate(tabelle)    # dann Umlaute konvertieren

    Puffer[idxITEM[Aktuelle[nr]]+34] = "<vchName>"       + vchName[nr]       + "</vchName>\n"
    Puffer[idxITEM[Aktuelle[nr]]+35] = "<lengthOfVchName>" + str(len(vchName[nr])) + "</lengthOfVchName>\n"

    # nur die Veränderbaren aktuallisieren
    Puffer[idxITEM[Aktuelle[nr]]+1]  = "<prNum>"         + prNum[nr]         + "</prNum>\n"
    Puffer[idxITEM[Aktuelle[nr]]+2]  = "<minorNum>"      + minorNum[nr]      + "</minorNum>\n"
    Puffer[idxITEM[Aktuelle[nr]]+31] = "<isScrambled>"   + isScrambled[nr]   + "</isScrambled>\n"
    Puffer[idxITEM[Aktuelle[nr]]+26] = "<isSkipped>"     + isSkipped[nr]     + "</isSkipped>\n"
    Puffer[idxITEM[Aktuelle[nr]]+24] = "<isInvisable>"   + isInvisable[nr]   + "</isInvisable>\n"
    Puffer[idxITEM[Aktuelle[nr]]+25] = "<isBlocked>"     + isBlocked[nr]     + "</isBlocked>\n"
    Puffer[idxITEM[Aktuelle[nr]]+28] = "<isDeleted>"     + isDeleted[nr]     + "</isDeleted>\n"
    Puffer[idxITEM[Aktuelle[nr]]+16] = "<favoriteIdxA>"  + favoriteIdxA[nr]  + "</favoriteIdxA>\n"
    Puffer[idxITEM[Aktuelle[nr]]+17] = "<favoriteIdxB>"  + favoriteIdxB[nr]  + "</favoriteIdxB>\n"
    Puffer[idxITEM[Aktuelle[nr]]+18] = "<favoriteIdxC>"  + favoriteIdxC[nr]  + "</favoriteIdxC>\n"
    Puffer[idxITEM[Aktuelle[nr]]+14] = "<mapAttr>"       + mapAttr[nr]       + "</mapAttr>\n"
    Puffer[idxITEM[Aktuelle[nr]]+38] = "<isUserSelCHNo>" + isUserSelCHNo[nr] + "</isUserSelCHNo>\n"

###############################################################################################################

def Listen_Box_Zeile_Anzeigen(pos, i):

    Listen_Box.insert(pos, "  {:6s} {:5s} {:28.28s}  {:7s} {:7s} {:7s} {:6s} {:4s} {:3s} │  {:2s} {:2s} {:2s} {:2s} {:2s} │  {:4s} {:4s} {:4s} {:4s} {:4s} {:4s} {:4s} {:4s}"\
        .format(prNum[i], minorNum[i], vchName[i], servTypText[i], frequency[i], service_id[i], transport_id[i], original_network_id[i],\
        videoStreamType[i], isScrambled[i], isSkipped[i], isInvisable[i], isBlocked[i], isDeleted[i],\
        favoriteIdxA[i], favoriteIdxB[i], favoriteIdxC[i], favoriteIdxD[i], favoriteIdxE[i], favoriteIdxF[i], favoriteIdxG[i], favoriteIdxH[i]))

###############################################################################################################

def Cursor_Anzeigen():

    if len(Aktuelle) == 0:
        Listen_Box.insert(tk.END, "  Keine Sender gefunden!")
    else:
        Listen_Box.selection_set(0)
        Listen_Box.focus_set()


###############################################################################################################

def Aktuelle_Anzeigen(event=None):

    Listen_Box.delete(0, tk.END) 
    for i in range(len(Aktuelle)):
        Listen_Box_Zeile_Anzeigen(tk.END, i)
    StatusAnzahl.set(len(Aktuelle))
    Cursor_Anzeigen()

###############################################################################################################

def Alle_Anzeigen(event=None):    # <F3>

    global Aktuelle

    Puffer_in_Listen()
    Aktuelle.clear()
    for i in range(len(idxITEM)):
        Aktuelle.append(i)
    Aktuelle_Anzeigen()
    StatusText.set("Chronologisch")

###############################################################################################################

def Sender_Suchen(event=None):    # <F7>

    def Suche_Anzeigen(event=None):

        global Aktuelle

        Suchbegriff = Eingabefeld.get()
        Fenster.destroy()

        Aktuelle.clear()
        Listen_Loeschen()

        for i in range(len(idxITEM)):
            if Puffer[idxITEM[i]+34].lower().find(Suchbegriff.lower()) != -1 or \
               Puffer[idxITEM[i]+32].find(Suchbegriff.encode("cp1252").hex()) != -1 or \
               Puffer[idxITEM[i]+32].find(Suchbegriff.lower().encode("cp1252").hex()) != -1 or \
               Puffer[idxITEM[i]+32].find(Suchbegriff.upper().encode("cp1252").hex()) != -1:
                Aktuelle.append(i)
                ITEM_in_Listen(idxITEM[i])

        Listen_Box.delete(0, tk.END) 
        Aktuelle_Anzeigen()
        StatusText.set("Suche nach \"{:s}\"".format(Suchbegriff))

    Fenster = tk.Toplevel(Master)
    Fenster.title("Sendernamen suchen")
    Fenster.geometry("+" + str(Master.winfo_x()+450) + "+" + str(Master.winfo_y()+250)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Eingabefeld = tk.Entry(Fenster, bd=4, width=30, font="Helvetica 12")
    ButtonSuchen = tk.Button(Fenster, bd=3, text="Suchen", font="Helvetica 11", command=Suche_Anzeigen)
    tk.Label(Fenster).pack(pady=1)
    Eingabefeld.pack(padx=50)
    ButtonSuchen.pack(pady=17, ipadx=10)

    Eingabefeld.insert(0, "RTL")
    Eingabefeld.select_range(0, tk.END)
    Eingabefeld.focus_set()
    Eingabefeld.bind("<Return>", Suche_Anzeigen)
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

def Senderliste_Drucken(event=None):

    Liste = Listen_Box.get(0, tk.END)

    with open("Senderliste.txt", "w") as Datei:
        for i in Liste:
            Datei.write(i[0:111] + "\n")    # nur bis Fav1

    message.showinfo("Channel View", "\nDie Datei Senderliste.txt wurde erstellt.  ")

###############################################################################################################

###############################################################################################################

def Favoriten_Anzeigen(fav):

    global Aktuelle

    Aktuelle.clear()
    Listen_Loeschen()

    for i in range(len(idxITEM)):
        if Puffer[idxITEM[i]+15+fav] != "<favoriteIdx" + chr(64+fav) + ">250</favoriteIdx" + chr(64+fav) + ">\n":   # chr(65=A, 66=B, 67=C)
            Aktuelle.append(i)
            ITEM_in_Listen(idxITEM[i])

    #  Bubble Sort
    for x in range(len(Aktuelle)):
        for i in range(0, len(Aktuelle)-1, 1):
            if (fav == 1 and int(favoriteIdxA[i]) > int(favoriteIdxA[i+1])) or \
               (fav == 2 and int(favoriteIdxB[i]) > int(favoriteIdxB[i+1])) or \
               (fav == 3 and int(favoriteIdxC[i]) > int(favoriteIdxC[i+1])) or \
               (fav == 4 and int(favoriteIdxD[i]) > int(favoriteIdxD[i+1])):
                Aktuelle[i], Aktuelle[i+1] = Aktuelle[i+1], Aktuelle[i]
                Listen_Tauschen(i)
    
    Listen_Box.delete(0, tk.END) 
    Aktuelle_Anzeigen()
    StatusText.set("Favoriten " + str(fav) + " sortiert")

###############################################################################################################

def Filtern_serviceType(typ):

    global Aktuelle

    Aktuelle.clear()
    Listen_Loeschen()

    for i in range(len(idxITEM)):
        if typ == "SD-TV":
            if Puffer[idxITEM[i]+9] == "<serviceType>1</serviceType>\n" or \
               Puffer[idxITEM[i]+9] == "<serviceType>22</serviceType>\n":
                Aktuelle.append(i)
                ITEM_in_Listen(idxITEM[i])
        if typ == "HD-TV":
            if Puffer[idxITEM[i]+9] == "<serviceType>17/serviceType>\n" or \
               Puffer[idxITEM[i]+9] == "<serviceType>25</serviceType>\n":
                Aktuelle.append(i)
                ITEM_in_Listen(idxITEM[i])
        if typ == "UHD-TV":
            if Puffer[idxITEM[i]+9] == "<serviceType>31</serviceType>\n" or \
               Puffer[idxITEM[i]+9] == "<serviceType>159</serviceType>\n":
                Aktuelle.append(i)
                ITEM_in_Listen(idxITEM[i])
        if typ == "Radio":
            if Puffer[idxITEM[i]+9] == "<serviceType>2</serviceType>\n" or \
               Puffer[idxITEM[i]+9] == "<serviceType>10</serviceType>\n":
                Aktuelle.append(i)
                ITEM_in_Listen(idxITEM[i])

    Listen_Box.delete(0, tk.END) 
    Aktuelle_Anzeigen()
    StatusText.set("Nur " + typ + " Sender")

###############################################################################################################

def Filtern_PayTV():

    global Aktuelle

    Aktuelle.clear()
    Listen_Loeschen()

    for i in range(len(idxITEM)):
        if Puffer[idxITEM[i]+31] == "<isScrambled>1</isScrambled>\n":
            Aktuelle.append(i)
            ITEM_in_Listen(idxITEM[i])

    Listen_Box.delete(0, tk.END) 
    Aktuelle_Anzeigen()
    StatusText.set("Nur Pay-TV Sender")

###############################################################################################################

def Sender_Sortieren(gruppe, event=None):

    global Aktuelle

    # Bubble Sort
    for j in range(len(Aktuelle)):
        for i in range(0, len(Aktuelle)-1, 1):
            if gruppe == "Nummer":     # <F4> 
                if int(prNum[i]) > int(prNum[i+1]):
                    Aktuelle[i], Aktuelle[i+1] = Aktuelle[i+1], Aktuelle[i]
                    Listen_Tauschen(i)
            if gruppe == "Name":       # <F5>
                if vchName[i].lower() > vchName[i+1].lower():
                    Aktuelle[i], Aktuelle[i+1] = Aktuelle[i+1], Aktuelle[i]
                    Listen_Tauschen(i)
            if gruppe == "Frequenz": 
                if int(frequency[i]) > int(frequency[i+1]):
                    Aktuelle[i], Aktuelle[i+1] = Aktuelle[i+1], Aktuelle[i]
                    Listen_Tauschen(i)
            if gruppe == "ServiceID": 
                if int(service_id[i]) > int(service_id[i+1]):
                    Aktuelle[i], Aktuelle[i+1] = Aktuelle[i+1], Aktuelle[i]
                    Listen_Tauschen(i)
   
    Listen_Box.delete(0, tk.END) 
    Aktuelle_Anzeigen()
    StatusText.set("Sortiert nach " + gruppe)

###############################################################################################################

def Sender_Markieren(a,b):

    insgesamt = 0
    markierte = 0

    def Markieren(a,i):

        global GEAENDERT, Puffer

        if a == 1:   # überspringen
            if isSkipped[i] == "0":
                Puffer[idxITEM[Aktuelle[i]]+26] = "<isSkipped>1</isSkipped>\n"
                isSkipped[i] = "1"
                GEAENDERT = True
                return(True)
        if a == 2:   # verstecken
            if isInvisable[i] == "0":
                Puffer[idxITEM[Aktuelle[i]]+24] = "<isInvisible>1</isInvisible>\n"
                isInvisable[i] = "1"
                GEAENDERT = True
                return(True)
        if a == 3:   # sperren
            if isBlocked[i] == "0":
                Puffer[idxITEM[Aktuelle[i]]+25] = "<isBlocked>1</isBlocked>\n"
                isBlocked[i] = "1"
                GEAENDERT = True
                return(True)
        if a == 4:   # löschen
            if isDeleted[i] == "0":
                Puffer[idxITEM[Aktuelle[i]]+28] = "<isDeleted>1</isDeleted>\n"
                isDeleted[i] = "1"
                GEAENDERT = True
                return(True)
    
        return(False)
 
#--------------------------------------------

    if b == 1:   # UHD-TV
        for i in range(len(Aktuelle)):
            if serviceType[i] == "31" or serviceType[i] == "159":
                if Markieren(a,i):
                    markierte += 1
                insgesamt += 1

    if b == 2:   # Radio
        for i in range(len(Aktuelle)):
            if serviceType[i] == "2" or serviceType[i] == "7" or serviceType[i] == "10":
                if Markieren(a,i):
                    markierte += 1
                insgesamt += 1

    if b == 3:   # Pay-TV
        for i in range(len(Aktuelle)):
            if isScrambled[i] == "1":
                if Markieren(a,i):
                    markierte += 1
                insgesamt += 1

    if b == 4:   # Unbekannte    (SD-TV = 1+22 / HD-TV = 17+25 / UHD-TV = 31+159 / Radio = 2+7+10 / VText = 3 / Data/Test = 12)
        for i in range(len(Aktuelle)):
            if (serviceType[i] !=  "1" and serviceType[i] !=  "2" and serviceType[i] !=  "7" and serviceType[i] != "10" and \
                serviceType[i] != "17" and serviceType[i] != "22" and serviceType[i] != "25" and serviceType[i] != "31"):
                if Markieren(a,i):
                    markierte += 1
                insgesamt += 1

#    if b == 5:   # Doppelte
#        for j in range(0, len(Aktuelle), 1):
#            for i in range(j+1, len(Aktuelle), 1):
#                if frequency[j] == frequency[i] and service_id[j] == service_id[i] and transport_id[j] == transport_id[i]: 
#                    insgesamt += 1
#                    # nur wenn beide noch nicht markiert
#                    if (a == 1 and isSkipped[j] == "0" and isSkipped[i] == "0") or \
#                       (a == 2 and isInvisable[j] == "0" and isInvisable[i] == "0") or \
#                       (a == 3 and isBlocked[j] == "0" and isBlocked[i] == "0") or \
#                       (a == 4 and isDeleted[j] == "0" and isDeleted[i] == "0"):
#                       Markieren(a,i)
#                       markierte += 1

    Listen_Box.delete(0, tk.END) 
    Aktuelle_Anzeigen()
    message.showinfo("Channel View", "\nEs wurden " + str(markierte) + " von " + str(insgesamt) + " Sendern markiert.  ")

###############################################################################################################

def Sender_Ueberspringen(event=None):    # <Doppelklick Rechts>

    global GEAENDERT, Puffer

    if Listen_Box.curselection() and len(Aktuelle) > 0:
        nr = Listen_Box.curselection()[0]

        if isSkipped[nr] == "0":
            Puffer[idxITEM[Aktuelle[nr]]+26] = "<isSkipped>1</isSkipped>\n"    # on
            isSkipped[nr] = "1"
        else:
            Puffer[idxITEM[Aktuelle[nr]]+26] = "<isSkipped>0</isSkipped>\n"    # off
            isSkipped[nr] = "0"#

        GEAENDERT = True

        Listen_Box.delete(nr)
        Listen_Box_Zeile_Anzeigen(nr, nr)
        Listen_Box.selection_set(nr+1)
        Listen_Box.focus_set()

###############################################################################################################

###############################################################################################################

def Sender_Bearbeiten(event=None):    # <Return> oder <Doppelklick Links>

    def Eintrag_Aendern(event=None):

        global GEAENDERT

        if EingabeNr.get().isnumeric() and EingabemNr.get().isnumeric() and \
           EingabeFav1.get().isnumeric() and EingabeFav2.get().isnumeric() and EingabeFav3.get().isnumeric():

            vchName[nr] = EingabeName.get()
            if vchName[nr][0] == '"' and vchName[nr][-1] == '"':
                vchName[nr] = vchName[nr].replace('"','')        # ohne "
 
            prNum[nr] = EingabeNr.get()
            minorNum[nr] = EingabemNr.get()
            isUserSelCHNo[nr] = "1"           # immer!! 
            # Favoritenliste schreiben
            favoriteIdxA[nr] = EingabeFav1.get()
            favoriteIdxB[nr] = EingabeFav2.get()
            favoriteIdxC[nr] = EingabeFav3.get()
            # Favoriten mapAttribute setzen
            mapA = 0
            if int(EingabeFav1.get()) < 250:    mapA += 1
            if int(EingabeFav2.get()) < 250:    mapA += 2
            if int(EingabeFav3.get()) < 250:    mapA += 4
            #if int(EingabeFav4.get()) < 250:    mapA += 8
            mapAttr[nr] = str(mapA)
            # Kanal-Attribute setzen
            if AttributP.get():   isScrambled[nr] = "1"
            else:                 isScrambled[nr] = "0"
            if AttributU.get():   isSkipped[nr] = "1"
            else:                 isSkipped[nr] = "0"
            if AttributV.get():   isInvisable[nr] = "1"
            else:                 isInvisable[nr] = "0"
            if AttributS.get():   isBlocked[nr] = "1"
            else:                 isBlocked[nr] = "0"
            if AttributL.get():   isDeleted[nr] = "1"
            else:                 isDeleted[nr] = "0"

            Listen_in_Puffer(nr)
            GEAENDERT = True

            Listen_Box.delete(nr)
            Listen_Box_Zeile_Anzeigen(nr, nr)
            Listen_Box.selection_set(nr+1)
            Listen_Box.focus_set()
            Fenster.destroy()

#--------------------------------------------

    if Listen_Box.curselection() and len(Aktuelle) > 0:
        nr = Listen_Box.curselection()[0]

        Fenster = tk.Toplevel(Master)
        Fenster.title("Sender bearbeiten")
        Fenster.geometry("+" + str(Master.winfo_x()+310) + "+" + str(Master.winfo_y()+300)) 
        Fenster.resizable(False, False)
        Fenster.wm_attributes("-topmost", True)

        EingabeName =  tk.Entry(Fenster, bd=3, width=40, font="Helvetica 11")
        TextNr = tk.Label(Fenster, text="Nr: ", font="Helvetica 11")
        TextmNr = tk.Label(Fenster, text="mNr: ", font="Helvetica 11")
        TextFav1 = tk.Label(Fenster, text="Fav 1: ", font="Helvetica 11")
        TextFav2 = tk.Label(Fenster, text="Fav 2: ", font="Helvetica 11")
        TextFav3 = tk.Label(Fenster, text="Fav 3: ", font="Helvetica 11")
        # Nummer + Favoriten
        EingabeNr =    tk.Entry(Fenster, bd=3, width=5, font="Helvetica 11")
        EingabemNr =   tk.Entry(Fenster, bd=3, width=5, font="Helvetica 11")
        EingabeFav1 =  tk.Entry(Fenster, bd=3, width=4, font="Helvetica 11")
        EingabeFav2 =  tk.Entry(Fenster, bd=3, width=4, font="Helvetica 11")
        EingabeFav3 =  tk.Entry(Fenster, bd=3, width=4, font="Helvetica 11")
       # Attribute
        AttributP.set(int(isScrambled[nr]))
        AttributU.set(int(isSkipped[nr]))
        AttributV.set(int(isInvisable[nr]))
        AttributS.set(int(isBlocked[nr]))
        AttributL.set(int(isDeleted[nr]))
        CheckAttrP = tk.Checkbutton(Fenster, text=" Pay-TV", font="Helvetica 11", variable=AttributP)
        CheckAttrU = tk.Checkbutton(Fenster, text=" Überspringen", font="Helvetica 11", variable=AttributU)
        CheckAttrV = tk.Checkbutton(Fenster, text=" Verstecken", font="Helvetica 11", variable=AttributV)
        CheckAttrS = tk.Checkbutton(Fenster, text=" Sperren", font="Helvetica 11", variable=AttributS)
        CheckAttrL = tk.Checkbutton(Fenster, text=" Löschen", font="Helvetica 11", variable=AttributL)
        # Button's
        ButtonSpeichern = tk.Button(Fenster, bd=3, text="Speichern", font="Helvetica 11", command=Eintrag_Aendern)
        ButtonAbbrechen = tk.Button(Fenster, bd=3, text="Abbrechen", font="Helvetica 11", command=Fenster.destroy)

        # 1. Zeile mit 12 Spalten
        tk.Label(Fenster).grid(row=0, column=0, padx=30)
        tk.Label(Fenster).grid(row=0, column=1, padx=16)
        tk.Label(Fenster).grid(row=0, column=2, padx=40)
        tk.Label(Fenster).grid(row=0, column=3, padx=20)
        tk.Label(Fenster).grid(row=0, column=4, padx=40)
        tk.Label(Fenster).grid(row=0, column=5, padx=30)
        tk.Label(Fenster).grid(row=0, column=6, padx=35)
        tk.Label(Fenster).grid(row=0, column=7, padx=30)
        tk.Label(Fenster).grid(row=0, column=8, padx=35)
        tk.Label(Fenster).grid(row=0, column=9, padx=30)
        tk.Label(Fenster).grid(row=0, column=10, padx=35)
        tk.Label(Fenster).grid(row=0, column=11, padx=20)
        # 2. Zeile = SenderName
        EingabeName.grid(row=1, column=2, columnspan=8, pady=8)
        # 3. Zeile = Nummern & Favoriten
        TextNr.grid(row=2, column=1, sticky="w", pady=22)
        TextmNr.grid(row=2, column=3, sticky="w")
        TextFav1.grid(row=2, column=5, sticky="w")
        TextFav2.grid(row=2, column=7, sticky="w")
        TextFav3.grid(row=2, column=9, sticky="w")
        EingabeNr.grid(row=2, column=2, sticky="w")
        EingabemNr.grid(row=2, column=4, sticky="w")
        EingabeFav1.grid(row=2, column=6, sticky="w")
        EingabeFav2.grid(row=2, column=8, sticky="w")
        EingabeFav3.grid(row=2, column=10, sticky="w")
        # 4. Zeile = Attribute
        CheckAttrP.grid(row=3, column=1, columnspan=2, sticky="w")
        CheckAttrU.grid(row=3, column=2, columnspan=4)
        CheckAttrV.grid(row=3, column=5, columnspan=2, sticky="w")
        CheckAttrS.grid(row=3, column=7, columnspan=2, sticky="w")
        CheckAttrL.grid(row=3, column=8, columnspan=3)
        # 5. Zeile
        ButtonSpeichern.grid(row=4, column=1, columnspan=5, padx=50, pady=22, ipadx=25, sticky="e")
        ButtonAbbrechen.grid(row=4, column=6, columnspan=5, padx=50, pady=22, ipadx=23, sticky="w")

        EingabeNr.insert(0, prNum[nr])
        EingabeNr.select_range(0, tk.END)
        EingabeNr.focus_set()
        EingabeName.insert(0, vchName[nr])
        EingabemNr.insert(0, minorNum[nr])
        EingabeFav1.insert(0, favoriteIdxA[nr])
        EingabeFav2.insert(0, favoriteIdxB[nr])
        EingabeFav3.insert(0, favoriteIdxC[nr])

        EingabeName.bind("<Return>", Eintrag_Aendern)
        EingabeNr.bind("<Return>", Eintrag_Aendern)
        EingabemNr.bind("<Return>", Eintrag_Aendern)
        EingabeFav1.bind("<Return>", Eintrag_Aendern)
        ButtonSpeichern.bind("<Return>", Eintrag_Aendern)
        ButtonAbbrechen.bind("<Return>", lambda event: Fenster.destroy())
        Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

###############################################################################################################

def Sender_Kopieren(event=None):    # <F8> 

    def Listen_Kopieren(nummer, name):

        prNum.insert(nr+1,nummer)    # neue Nummer
        minorNum.insert(nr+1,nummer)
        original_network_id.insert(nr+1,original_network_id[nr])
        transport_id.insert(nr+1,transport_id[nr])
        service_id.insert(nr+1,service_id[nr])
        serviceType.insert(nr+1,serviceType[nr])
        servTypText.insert(nr+1,servTypText_Laden(serviceType[nr]))
        frequency.insert(nr+1,frequency[nr])
        mapAttr.insert(nr+1,mapAttr[nr])
        favoriteIdxA.insert(nr+1,favoriteIdxA[nr])
        favoriteIdxB.insert(nr+1,favoriteIdxB[nr])
        favoriteIdxC.insert(nr+1,favoriteIdxC[nr])
        favoriteIdxD.insert(nr+1,favoriteIdxD[nr])
        favoriteIdxE.insert(nr+1,favoriteIdxE[nr])
        favoriteIdxF.insert(nr+1,favoriteIdxF[nr])
        favoriteIdxG.insert(nr+1,favoriteIdxG[nr])
        favoriteIdxH.insert(nr+1,favoriteIdxH[nr])
        isInvisable.insert(nr+1,isInvisable[nr])
        isBlocked.insert(nr+1,isBlocked[nr])
        isSkipped.insert(nr+1,isSkipped[nr])
        isDeleted.insert(nr+1,isDeleted[nr])
        isScrambled.insert(nr+1,isScrambled[nr])
        vchName.insert(nr+1,name)    # neuer Name
        isUserSelCHNo.insert(nr+1,"1")
        videoStreamType.insert(nr+1,videoStreamType[nr])

    def Eintrag_Aendern(event=None):

        global GEAENDERT, Puffer

        idxITEM.append(idxITEM[-1]+42)        # Zeiger auf neuen letzten Senderblock (vorher = </DTV>)
        for i in range(42):                   # Neuen Senderblock ans Pufferende kopieren
            Puffer.insert(idxITEM[-1]+i, Puffer[idxITEM[Aktuelle[nr]]+i])

        PrgNum = EingabeNummer.get()
        PrgName = EingabeName.get()

        Puffer[idxITEM[-1]+1]  = "<prNum>"    + PrgNum + "</prNum>\n"
        Puffer[idxITEM[-1]+2]  = "<minorNum>" + PrgNum + "</minorNum>\n"
        Puffer[idxITEM[-1]+34] = "<vchName>"    + PrgName + "</vchName>\n"
        Puffer[idxITEM[-1]+32] = "<hexVchName>" + PrgName.encode("cp1252").hex() + "</hexVchName>\n"
        Puffer[idxITEM[-1]+35] = "<lengthOfVchName>"             + str(len(PrgName)) + "</lengthOfVchName>\n"
        Puffer[idxITEM[-1]+33] = "<notConvertedLengthOfVchName>" + str(len(PrgName)) + "</notConvertedLengthOfVchName>\n"
        Puffer[idxITEM[-1]+38] = "<isUserSelCHNo>1</isUserSelCHNo>\n"

        Listen_Kopieren(PrgNum, PrgName)
        Aktuelle.insert(nr+1,nr+1)
        GEAENDERT = True

        Listen_Box_Zeile_Anzeigen(nr+1, nr+1)
        StatusAnzahl.set(len(Aktuelle))
        Fenster.destroy()

#--------------------------------------------

    if Listen_Box.curselection() and len(Aktuelle) > 0:
        nr = Listen_Box.curselection()[0]

        Fenster = tk.Toplevel(Master)
        Fenster.title("Sender kopieren nach:")
        Fenster.geometry("+" + str(Master.winfo_x()+450) + "+" + str(Master.winfo_y()+350)) 
        Fenster.resizable(False, False)
        Fenster.wm_attributes("-topmost", True)

        EingabeNummer = tk.Entry(Fenster, bd=4, width=3, font="Helvetica 12")
        EingabeName = tk.Entry(Fenster, bd=4, width=26, font="Helvetica 12")
        tk.Label(Fenster).pack(side="left", padx=20, pady=40)
        EingabeNummer.pack(side="left", padx=10)
        EingabeName.pack(side="left", padx=10)            
        tk.Label(Fenster).pack(side="left", padx=20)

        for num in range(1, len(prNum), 1):      # freie Nummer suchen
            gefunden = False
            for i in range(0, len(prNum), 1):
                if str(num) == prNum[i]:
                    gefunden = True
                    break
            if not gefunden:   break

        EingabeName.insert(0, vchName[nr])
        EingabeNummer.insert(0, str(num))
        EingabeNummer.select_range(0, tk.END)
        EingabeNummer.focus_set()
        EingabeNummer.bind("<Return>", Eintrag_Aendern)
        EingabeName.bind("<Return>", Eintrag_Aendern)
        Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

###############################################################################################################

def Sender_Entfernen(event=None):    # <Strg+D>

    global GEAENDERT, Puffer, Aktuelle


    def Listenelement_Loeschen():

        servTypText.pop(nr)
        prNum.pop(nr)
        minorNum.pop(nr)
        original_network_id.pop(nr)
        transport_id.pop(nr)
        service_id.pop(nr)
        serviceType.pop(nr)
        frequency.pop(nr)
        mapAttr.pop(nr)
        favoriteIdxA.pop(nr)
        favoriteIdxB.pop(nr)
        favoriteIdxC.pop(nr)
        favoriteIdxD.pop(nr)
        favoriteIdxE.pop(nr)
        favoriteIdxF.pop(nr)
        favoriteIdxG.pop(nr)
        favoriteIdxH.pop(nr)
        isInvisable.pop(nr)
        isBlocked.pop(nr)
        isSkipped.pop(nr)
        isDeleted.pop(nr)
        isScrambled.pop(nr)
        vchName.pop(nr)
        isUserSelCHNo.pop(nr)
        videoStreamType.pop(nr)

#--------------------------------------------

    if Listen_Box.curselection() and len(Aktuelle) > 0:
        nr = Listen_Box.curselection()[0]

        for i in range(42):                      # 42x letztes Element löschen
            Puffer.pop(idxITEM[Aktuelle[nr]])    # <ITEM> bis </ITEM> aus Puffer löschen
        idxITEM.pop(-1)

        for i in range(len(Aktuelle)):           # nur nachfolgende Aktuelle -1
            if Aktuelle[i] > Aktuelle[nr]:   Aktuelle[i] -= 1
        Aktuelle.pop(nr)

        Listenelement_Loeschen()                 # 25 Listen
        GEAENDERT = True

        Listen_Box.delete(nr)
        StatusAnzahl.set(len(Aktuelle))
        Listen_Box.selection_set(nr)
        Listen_Box.focus_set()

###############################################################################################################

###############################################################################################################

def Service_Info(event=None):    # <F9>

    def SID_Listen_Loeschen():

        servCountNr.clear()
        aucSvcName.clear()
        usServiceID.clear()
        bVisibilityFlag.clear()
        bIsScramble.clear()
        usLCNValue.clear()
        ucServiceType.clear()
        usTPIndex.clear()

    def SID_Listen_Laden():

        global idxSID, aktSID

        idxSID.clear()
        aktSID.clear()
        for i in range(len(Puffer)):
            if Puffer[i] == "<astServiceInfo>\n":
                i += 1     # erster <ServCount..>
                while Puffer[i] != "</astServiceInfo>\n":
                    idxSID.append(i)               # Zeiger auf <ServCount..>'s
                    aktSID.append(len(aktSID))     # Zeiger auf Aktuellen
                    n = Puffer[idxSID[-1]].find('>\n', 10)
                    servCountNr.append(Puffer[i][10:n])
                    n = Puffer[idxSID[-1]+2].find('</', 21)
                    aucSvcName.append(Puffer[idxSID[-1]+2][21:n])
                    n = Puffer[idxSID[-1]+3].find('</', 22)
                    usServiceID.append(Puffer[idxSID[-1]+3][22:n])
                    n = Puffer[idxSID[-1]+4].find('</', 26)
                    bVisibilityFlag.append(Puffer[idxSID[-1]+4][26:n])
                    n = Puffer[idxSID[-1]+5].find('</', 22)
                    bIsScramble.append(Puffer[idxSID[-1]+5][22:n])
                    n = Puffer[idxSID[-1]+6].find('</', 21)
                    usLCNValue.append(Puffer[idxSID[-1]+6][21:n])
                    n = Puffer[idxSID[-1]+7].find('</', 24)
                    ucServiceType.append(Puffer[idxSID[-1]+7][24:n])
                    n = Puffer[idxSID[-1]+9].find('</', 20)
                    usTPIndex.append(Puffer[idxSID[-1]+9][20:n])
                    i += 14             # nächster <ServCount..>

    def SID_Tauschen(i):

        servCountNr[i], servCountNr[i+1] = servCountNr[i+1], servCountNr[i]
        aucSvcName[i], aucSvcName[i+1] = aucSvcName[i+1], aucSvcName[i]
        usServiceID[i], usServiceID[i+1] = usServiceID[i+1], usServiceID[i]
        bVisibilityFlag[i], bVisibilityFlag[i+1] = bVisibilityFlag[i+1], bVisibilityFlag[i]
        bIsScramble[i], bIsScramble[i+1] = bIsScramble[i+1], bIsScramble[i]
        usLCNValue[i], usLCNValue[i+1] = usLCNValue[i+1], usLCNValue[i]
        ucServiceType[i], ucServiceType[i+1] = ucServiceType[i+1], ucServiceType[i]
        usTPIndex[i], usTPIndex[i+1] = usTPIndex[i+1], usTPIndex[i]

    def SID_Sortieren(gruppe):

        global aktSID
    
        # Bubble Sort
        for j in range(len(aktSID)):
            for i in range(0, len(aktSID)-1, 1):
                if gruppe == "Pos": 
                    if int(servCountNr[i]) > int(servCountNr[i+1]):
                        aktSID[i], aktSID[i+1] = aktSID[i+1], aktSID[i]
                        SID_Tauschen(i)
                if gruppe == "LCN": 
                    if int(usLCNValue[i]) > int(usLCNValue[i+1]):
                        aktSID[i], aktSID[i+1] = aktSID[i+1], aktSID[i]
                        SID_Tauschen(i)
                if gruppe == "SID": 
                    if int(usServiceID[i]) > int(usServiceID[i+1]):
                        aktSID[i], aktSID[i+1] = aktSID[i+1], aktSID[i]
                        SID_Tauschen(i)
                if gruppe == "Name": 
                    if aucSvcName[i].lower() > aucSvcName[i+1].lower():
                        aktSID[i], aktSID[i+1] = aktSID[i+1], aktSID[i]
                        SID_Tauschen(i)
       
        Listen_Box.delete(0, tk.END) 
        for i in range(len(aktSID)):
            styp = ucServiceType[i]
            styp = styp.replace("1","SD-TV").replace("22","SD-TV").replace("17","HD-TV").replace("25","HD-TV").replace("2","Radio")
            Listen_Box.insert(tk.END, " {:>5s} {:>5s}   {:30.30s} {:7s} {:6s} {:2s} {:2s} {:3s}".format(servCountNr[i], usLCNValue[i], \
                                         aucSvcName[i], styp, usServiceID[i], bVisibilityFlag[i], bIsScramble[i], usTPIndex[i]))
        Listen_Box.selection_set(0)
        Listen_Box.focus_set()

    def Eintrag_Entfernen(event=None):

        global GEAENDERT, Puffer, aktSID

        if Listen_Box.curselection():
            nr = Listen_Box.curselection()[0]

            aucSvcName.pop(nr)
            usServiceID.pop(nr)
            bVisibilityFlag.pop(nr)
            bIsScramble.pop(nr)
            usLCNValue.pop(nr)
            ucServiceType.pop(nr)
            usTPIndex.pop(nr)

            for i in range(14):
                Puffer.pop(idxSID[aktSID[nr]])      # <ServCount..> bis </ServCount..> aus Puffer löschen
            idxSID.pop(-1)                          # 14x letztes Element löschen (ganzen Eintrag)

            for i in range(len(aktSID)):            # nur nachfolgende aktSID -1
                if aktSID[i] > aktSID[nr]:   aktSID[i] -= 1
            aktSID.pop(nr)
            GEAENDERT = True

            Listen_Box.delete(nr)
            Statuszeile.config(text = "  {:7d}   |   Sortieren nach:   LCN = <F10>,   Name = <F11>,   SID = <F12>".format(len(aktSID)))
            Listen_Box.selection_set(nr)
            Listen_Box.focus_set()

    def Eintrag_Bearbeiten(event=None):

        def Eintrag_Aendern(event=None):

            global GEAENDERT, Puffer

            if EingabeLCN.get().isnumeric():

                usLCNValue[nr] = EingabeLCN.get()
                aucSvcName[nr] = EingabeName.get()
                usTPIndex[nr] = EingabeTPI.get()
                Puffer[idxSID[aktSID[nr]]+6] = '<usLCNValue type="0">' + usLCNValue[nr] + '</usLCNValue>\n'
                Puffer[idxSID[aktSID[nr]]+2] = '<aucSvcName type="0">' + aucSvcName[nr] + '</aucSvcName>\n'
                Puffer[idxSID[aktSID[nr]]+1] = '<hexAucSvcName type="0">' + aucSvcName[nr].encode("cp1252").hex() + '</hexAucSvcName>\n'
                Puffer[idxSID[aktSID[nr]]+8] = '<ucSvcNameLength type="0">' + str(len(aucSvcName[nr])) + '</ucSvcNameLength>\n'
                Puffer[idxSID[aktSID[nr]]+9] = '<usTPIndex type="0">' + usTPIndex[nr] + '</usTPIndex>\n'
                GEAENDERT = True

                Listen_Box.delete(nr)
                styp = ucServiceType[i]
                styp = styp.replace("1","SD-TV").replace("22","SD-TV").replace("17","HD-TV").replace("25","HD-TV").replace("2","Radio")
                Listen_Box.insert(tk.END, " {:>5s} {:>5s}   {:30.30s} {:7s} {:6s} {:2s} {:2s} {:3s}".format(servCountNr[i], usLCNValue[i], \
                                             aucSvcName[i], styp, usServiceID[i], bVisibilityFlag[i], bIsScramble[i], usTPIndex[i]))
                Listen_Box.selection_set(nr+1)
                Listen_Box.focus_set()
                Fenster2.destroy()

        if Listen_Box.curselection():
            nr = Listen_Box.curselection()[0]

            Fenster2 = tk.Toplevel(Fenster)
            Fenster2.title("Logische Kanalnummer bearbeiten")
            Fenster2.geometry("+" + str(Fenster.winfo_x()+28) + "+" + str(Fenster.winfo_y()+330)) 
            Fenster2.resizable(False, False)
            Fenster2.wm_attributes("-topmost", True)

            EingabeName =  tk.Entry(Fenster2, bd=3, width=27, font="Helvetica 11")
            EingabeLCN =   tk.Entry(Fenster2, bd=3, width=4, font="Helvetica 11")
            EingabeTPI =   tk.Entry(Fenster2, bd=3, width=4, font="Helvetica 11")
            TextLCN = tk.Label(Fenster2, text=" LCN:", font="Helvetica 8")
            TextTPI = tk.Label(Fenster2, text="  TPI:", font="Helvetica 8")
            tk.Label(Fenster2).pack(padx=15, pady=27, side="left")
            EingabeName.pack(padx=10, side="left")            
            TextLCN.pack(side="left")            
            EingabeLCN.pack(padx=5, side="left")
            TextTPI.pack(side="left")            
            EingabeTPI.pack(padx=5, side="left")            
            tk.Label(Fenster2).pack(padx=15, side="left")
        
            EingabeName.insert(0, aucSvcName[nr])
            EingabeLCN.insert(0, usLCNValue[nr])
            EingabeTPI.insert(0, usTPIndex[nr])
            EingabeLCN.select_range(0, tk.END)
            EingabeLCN.focus_set()

            EingabeLCN.bind("<Return>", Eintrag_Aendern)
            EingabeName.bind("<Return>", Eintrag_Aendern)
            EingabeTPI.bind("<Return>", Eintrag_Aendern)
            Fenster2.bind("<Escape>", lambda event: Fenster2.destroy())

    def ServiceInfo_Drucken(event=None):

        Liste = Listen_Box.get(0, tk.END)

        with open("ServiceInfo.txt", "w") as Datei:
            for i in Liste:
                if i[7:12] != "    0":    # wenn LCN nicht 0
                    Datei.write(i + "\n")

        message.showinfo("Service Info", "\nDie Datei ServiceInfo.txt wurde erstellt.  ", parent=Fenster)

#--------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title("Service Info")
    Fenster.geometry("+" + str(Master.winfo_x()+625) + "+" + str(Master.winfo_y()+7)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Scroll_Vertikal = tk.Scrollbar(Fenster, width=15)
    Listen_Box = tk.Listbox(Fenster, width=72, height=41, yscrollcommand=Scroll_Vertikal.set)
    Titelleiste = tk.Label(Fenster, text="   Pos   LCN   Sendername                     STyp    SID    S  P  TPI", relief="sunken", anchor="w", font=Schrift)
    Statuszeile = tk.Label(Fenster, text="", relief="sunken", anchor="w", font="Helvetica 10")
    Scroll_Vertikal.config(command=Listen_Box.yview)
    Listen_Box.config(bg=Hintergrund, fg=Vordergrund, font=Schrift)
    Titelleiste.pack(side="top", fill="x", padx=2, pady=1)
    Statuszeile.pack(side="bottom", fill="x", padx=2, pady=1)
    Scroll_Vertikal.pack(side="right", fill="y", padx=1, pady=1)
    Listen_Box.pack(fill="both", padx=2, pady=1, expand=True)

    SID_Listen_Loeschen()
    SID_Listen_Laden()
    if len(aktSID) == 0:
        Listen_Box.insert(tk.END, "  Keine Service Informationen!")
    else:
        for i in range(len(aktSID)):
            styp = ucServiceType[i]
            styp = styp.replace("1","SD-TV").replace("22","SD-TV").replace("17","HD-TV").replace("25","HD-TV").replace("2","Radio")
            Listen_Box.insert(tk.END, " {:>5s} {:>5s}   {:30.30s} {:7s} {:6s} {:2s} {:2s} {:3s}".format(servCountNr[i], usLCNValue[i], \
                                         aucSvcName[i], styp, usServiceID[i], bVisibilityFlag[i], bIsScramble[i], usTPIndex[i]))
        Listen_Box.selection_set(0)
        Listen_Box.focus_set()
    Statuszeile.config(text = "  {:7d}   |   Sortieren nach:   LCN = <F10>,   Name = <F11>,   SID = <F12>".format(len(aktSID)))

    Listen_Box.bind("<Double-Button-1>", Eintrag_Bearbeiten)
    Listen_Box.bind("<Return>", Eintrag_Bearbeiten)
    Listen_Box.bind("<Control-Key-d>", Eintrag_Entfernen)
    Listen_Box.bind("<Control-Key-p>", ServiceInfo_Drucken)
    Listen_Box.bind("<F9>", lambda event: SID_Sortieren("Pos"))
    Listen_Box.bind("<F10>", lambda event: SID_Sortieren("LCN"))
    Listen_Box.bind("<F11>", lambda event: SID_Sortieren("Name"))
    Listen_Box.bind("<F12>", lambda event: SID_Sortieren("SID"))
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

def ServInfo_Neu_Nummerieren(event=None):

    global GEAENDERT, Puffer

    for i in range(len(Puffer)):
        if Puffer[i] == "<astServiceInfo>\n":
            i += 1     # erster <ServCount..>
            z = 0
            while Puffer[i] != "</astServiceInfo>\n":
                Puffer[i] = "<ServCount" + str(z) + ">\n"
                Puffer[i+13] = "</ServCount" + str(z) + ">\n"
                z += 1
                i += 14             # nächster <ServCount..>
            GEAENDERT = True
    message.showinfo("Service Info", "\nDie Service Info wurde neu durchnummeriert.  ")

###############################################################################################################

def ServInfo_Erstellen(event=None):

    global GEAENDERT, Puffer

    if Listen_Box.curselection():
        nr = Listen_Box.curselection()[0]

        if message.askyesno("Channel View", '\nSoll eine Service-Info für "' + vchName[nr] + '" erstellt werden?  '):

            for i in range(len(Puffer)):
                if Puffer[i] == "</astServiceInfo>\n":    # Ende <ServCount..> suchen
    
                    n = Puffer[i-1].find('>\n', 11)    # </ServCount..>
                    z = int(Puffer[i-1][11:n]) + 1     # nächste Nummer
                    Puffer.insert(i,"<ServCount" + str(z) + ">\n")

                    Puffer.insert(i+1,'<hexAucSvcName type="0">'+vchName[nr].encode("cp1252").hex()+'</hexAucSvcName>\n')
                    Puffer.insert(i+2,'<aucSvcName type="0">'+vchName[nr]+'</aucSvcName>\n')
                    Puffer.insert(i+3,'<usServiceID type="0">'+service_id[nr]+'</usServiceID>\n')
                    Puffer.insert(i+4,'<bVisibilityFlag type="0">'+str(1-int(isInvisable[nr]))+'</bVisibilityFlag>\n')
                    Puffer.insert(i+5,'<bIsScramble type="0">'+isScrambled[nr]+'</bIsScramble>\n')
                    Puffer.insert(i+6,'<usLCNValue type="0">'+prNum[nr]+'</usLCNValue>\n')
                    Puffer.insert(i+7,'<ucServiceType type="0">'+serviceType[nr]+'</ucServiceType>\n')
                    Puffer.insert(i+8,'<ucSvcNameLength type="0">'+str(len(vchName[nr]))+'</ucSvcNameLength>\n')
                    Puffer.insert(i+9,'<usTPIndex type="0">0</usTPIndex>\n')      # ???
                    Puffer.insert(i+10,'<usHDLcn type="0">0</usHDLcn>\n')
                    Puffer.insert(i+11,'<bIsOptrChBlocked type="0">0</bIsOptrChBlocked>\n')
                    Puffer.insert(i+12,'<usReservedForFuture type="0">0</usReservedForFuture>\n')

                    Puffer.insert(i+13,"</ServCount" + str(z) + ">\n")

                    #for i in range(len(idxITEM)):      # nach ServInfo einfügen ist idxITEM[] verschoben !?!
                    #    idxITEM[i] += 14

                    #n = Puffer[idxITEM[Aktuelle[nr]]+32+1].find("</", 12)    # <hexVchName>
                    #Puffer.insert(i+1,'<hexAucSvcName type="0">'+Puffer[idxITEM[Aktuelle[nr]]+32][12:n]+'</hexAucSvcName>\n')
                    #n = Puffer[idxITEM[Aktuelle[nr]]+34+2].find("</", 9)     # <vchName>
                    #Puffer.insert(i+2,'<aucSvcName type="0">'+Puffer[idxITEM[Aktuelle[nr]]+34][9:n]+'</aucSvcName>\n')
                    #n = Puffer[idxITEM[Aktuelle[nr]]+1+3].find("</", 12)     # <service_id>
                    #Puffer.insert(i+3,'<usServiceID type="0">'+Puffer[idxITEM[Aktuelle[nr]]+6][12:n]+'</usServiceID>\n')
                    #n = Puffer[idxITEM[Aktuelle[nr]]+24+4].find("</", 13)    # <isInvisable>
                    #Puffer.insert(i+4,'<bVisibilityFlag type="0">'+Puffer[idxITEM[Aktuelle[nr]]+24][13:n]+'</bVisibilityFlag>\n')
                    #n = Puffer[idxITEM[Aktuelle[nr]]+31+5].find("</", 13)    # <isScrambled>
                    #Puffer.insert(i+5,'<bIsScramble type="0">'+Puffer[idxITEM[Aktuelle[nr]]+31][13:n]+'</bIsScramble>\n')
                    #n = Puffer[idxITEM[Aktuelle[nr]]+1+6].find("</", 7)      # <prNum>
                    #Puffer.insert(i+6,'<usLCNValue type="0">'+Puffer[idxITEM[Aktuelle[nr]]+1][7:n]+'</usLCNValue>\n')
                    #n = Puffer[idxITEM[Aktuelle[nr]]+1+7].find("</", 13)     # <serviceType>
                    #Puffer.insert(i+7,'<ucServiceType type="0">'+Puffer[idxITEM[Aktuelle[nr]]+9][13:n]+'</ucServiceType>\n')
                    #n = Puffer[idxITEM[Aktuelle[nr]]+35+8].find("</", 17)    # <lengthOfVchName>
                    #Puffer.insert(i+8,'<ucSvcNameLength type="0">'+Puffer[idxITEM[Aktuelle[nr]]+35][17:n]+'</ucSvcNameLength>\n')
                    #n = Puffer[idxITEM[Aktuelle[nr]]+1+9].find("</", 7)      # <???>
                    #Puffer.insert(i+9,'<usTPIndex type="0">0</usTPIndex>\n')
                    #n = Puffer[idxITEM[Aktuelle[nr]]+1+10].find("</", 7)     # "0"
                    #Puffer.insert(i+10,'<usHDLcn type="0">0</usHDLcn>\n')
                    #n = Puffer[idxITEM[Aktuelle[nr]]+1+11].find("</", 7)     # "0"
                    #Puffer.insert(i+11,'<bIsOptrChBlocked type="0">0</bIsOptrChBlocked>\n')
                    #n = Puffer[idxITEM[Aktuelle[nr]]+1+12].find("</", 7)     # "0"
                    #Puffer.insert(i+12,'<usReservedForFuture type="0">0</usReservedForFuture>\n')

                    GEAENDERT = True
                    break

###############################################################################################################

###############################################################################################################

def Satelliten_Info():

    def SatellitenInfo_Loeschen():

        SatelliteNameHex.clear()
        Angle.clear()
        AnglePrec.clear()
        DirEastWest.clear()

    def SatellitenInfo_Laden():

        for z in range(len(Puffer)):
            if Puffer[z] == "<SatRecordInfo>\n":
                while Puffer[z] != "</SatRecordInfo>\n":
                    z += 1
                    if Puffer[z].find("<SatelliteNameHex") == 0:     # wenn gefunden
                        n = Puffer[z].find('</', 27)
                        SatelliteNameHex.append(Puffer[z][27:n])
                        n = Puffer[z+1].find('</', 16)
                        Angle.append(Puffer[z+1][16:n])
                        n = Puffer[z+2].find('</', 20)
                        AnglePrec.append(Puffer[z+2][20:n])
                        n = Puffer[z+3].find('</', 22)
                        DirEastWest.append(Puffer[z+3][22:n])

    def SatellitenInfo_Sortieren():

        for j in range(len(SatelliteNameHex)):
            for i in range(0, len(SatelliteNameHex)-1, 1):
                if SatelliteNameHex[i] > SatelliteNameHex[i+1]:
                    SatelliteNameHex[i], SatelliteNameHex[i+1] = SatelliteNameHex[i+1], SatelliteNameHex[i]
                    Angle[i], Angle[i+1] = Angle[i+1], Angle[i]
                    AnglePrec[i], AnglePrec[i+1] = AnglePrec[i+1], AnglePrec[i]
                    DirEastWest[i], DirEastWest[i+1] = DirEastWest[i+1], DirEastWest[i]

#--------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title("Satelliten Info")
    Fenster.geometry("+" + str(Master.winfo_x()+473) + "+" + str(Master.winfo_y()+3)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Scroll_Vertikal = tk.Scrollbar(Fenster, width=15)
    Listen_Box = tk.Listbox(Fenster, width=44, height=44, yscrollcommand=Scroll_Vertikal.set)
    Scroll_Vertikal.config(command=Listen_Box.yview)
    Listen_Box.config(bg=Hintergrund, fg=Vordergrund, font=Schrift)
    Titelleiste.pack(side="top", fill="x", padx=2, pady=1)
    Scroll_Vertikal.pack(side="right", fill="y", padx=1, pady=1)
    Listen_Box.pack(fill="both", padx=2, pady=1, expand=True)

    SatellitenInfo_Loeschen()
    SatellitenInfo_Laden()
    SatellitenInfo_Sortieren()
    if len(SatelliteNameHex) == 0:
        Listen_Box.insert(tk.END, "  Keine Satelliten Informationen!")
    else:
        for i in range(len(SatelliteNameHex)):
            dirEW = DirEastWest[i].replace("1","Ost").replace("0","West")
            Listen_Box.insert(tk.END, "    {:25.25s} {:>3s},{:2s} {:2s}"\
                .format(bytearray.fromhex(SatelliteNameHex[i]).decode(), Angle[i], AnglePrec[i], dirEW))
        Listen_Box.selection_set(0)
        Listen_Box.focus_set()

    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

###############################################################################################################

def Transponder_Info():

    def TransponderInfo_Loeschen():

        TransponderId.clear()
        Frequency.clear()
        Polarisation.clear()
        SymbolRate.clear()
        TransmissionSystem.clear()
        HomeTp.clear()

    def TransponderInfo_Laden():

        for a in range(len(Puffer)):
            if Puffer[a] == "<TPList>\n":
                a += 2            # Zeiger auf "<TPRecord0>"
                i = 0
                while Puffer[a+i*8] != "</TPList>\n":
                    i += 1
                    n = Puffer[a+(i*8-7)].find('</', 24)
                    TransponderId.append(Puffer[a+(i*8-7)][24:n])
                    n = Puffer[a+(i*8-6)].find('</', 20)
                    Frequency.append(Puffer[a+(i*8-6)][20:n])
                    n = Puffer[a+(i*8-5)].find('</', 23)
                    Polarisation.append(Puffer[a+(i*8-5)][23:n])
                    n = Puffer[a+(i*8-4)].find('</', 21)
                    SymbolRate.append(Puffer[a+(i*8-4)][21:n])
                    n = Puffer[a+(i*8-3)].find('</', 29)
                    TransmissionSystem.append(Puffer[a+(i*8-3)][29:n])
                    n = Puffer[a+(i*8-2)].find('</', 17)
                    HomeTp.append(Puffer[a+(i*8-2)][17:n])

    def TransponderInfo_Sortieren():

        for j in range(len(TransponderId)):
            for i in range(0, len(TransponderId)-1, 1):
                if int(Frequency[i]) > int(Frequency[i+1]):
                    TransponderId[i], TransponderId[i+1] = TransponderId[i+1], TransponderId[i]
                    Frequency[i], Frequency[i+1] = Frequency[i+1], Frequency[i]
                    Polarisation[i], Polarisation[i+1] = Polarisation[i+1], Polarisation[i]
                    SymbolRate[i], SymbolRate[i+1] = SymbolRate[i+1], SymbolRate[i]
                    TransmissionSystem[i], TransmissionSystem[i+1] = TransmissionSystem[i+1], TransmissionSystem[i]
                    HomeTp[i], HomeTp[i+1] = HomeTp[i+1], HomeTp[i]

#--------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title("Transponder Info")
    Fenster.geometry("+" + str(Master.winfo_x()+530) + "+" + str(Master.winfo_y()+6)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Scroll_Vertikal = tk.Scrollbar(Fenster, width=15)
    Listen_Box = tk.Listbox(Fenster, width=32, height=42, yscrollcommand=Scroll_Vertikal.set)
    Titelleiste = tk.Label(Fenster, text="   TID  Freq  Pol SymRt TS HTp", relief="sunken", anchor="w", font=Schrift)
    Statuszeile = tk.Label(Fenster, text="", relief="sunken", anchor="w", font="Consolas 1")
    Scroll_Vertikal.config(command=Listen_Box.yview)
    Listen_Box.config(bg=Hintergrund, fg=Vordergrund, font=Schrift)
    Titelleiste.pack(side="top", fill="x", padx=2, pady=1)
    Statuszeile.pack(side="bottom", fill="x", padx=2, pady=1)
    Scroll_Vertikal.pack(side="right", fill="y", padx=1, pady=1)
    Listen_Box.pack(fill="both", padx=2, pady=1, expand=True)

    TransponderInfo_Loeschen()
    TransponderInfo_Laden()
    TransponderInfo_Sortieren()
    if len(TransponderId) == 0:
        Listen_Box.insert(tk.END, "  Keine Transponder Informationen!")
    else:
        for i in range(len(TransponderId)):
            pol = Polarisation[i].replace("1","H").replace("0","V")
            Listen_Box.insert(tk.END, "{:>6s}  {:6s} {:2s} {:6s} {:2s} {:2s}"\
                .format(TransponderId[i], Frequency[i], pol, SymbolRate[i], TransmissionSystem[i], HomeTp[i]))
        Listen_Box.selection_set(0)
        Listen_Box.focus_set()

    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

###############################################################################################################

def Transponder_Parameter():

    def TransponderParameter_Loeschen():

        uwServiceStartIndex.clear()
        uwServiceEndIndex.clear()
        uwServiceCount.clear()
        nitVersion.clear()
        channelIndex.clear()
        frequency2.clear()
        original_network_id2.clear()
        transport_id2.clear()

    def TransponderParameter_Laden():

        for a in range(len(Puffer)):
            if Puffer[a] == "<stTPRecParams>\n":
                a += 1            # Zeiger auf "<Record0>"
                i = 0
                while Puffer[a+i*34] != "</stTPRecParams>\n":
                    i += 1
                    n = Puffer[a+(i*34-33)].find('</', 30)
                    uwServiceStartIndex.append(Puffer[a+(i*34-33)][30:n])
                    n = Puffer[a+(i*34-32)].find('</', 28)
                    uwServiceEndIndex.append(Puffer[a+(i*34-32)][28:n])
                    n = Puffer[a+(i*34-31)].find('</', 25)
                    uwServiceCount.append(Puffer[a+(i*34-31)][25:n])
                    n = Puffer[a+(i*34-24)].find('</', 21)
                    nitVersion.append(Puffer[a+(i*34-24)][21:n])
                    n = Puffer[a+(i*34-23)].find('</', 23)
                    channelIndex.append(Puffer[a+(i*34-23)][23:n])
                    n = Puffer[a+(i*34-22)].find('</', 20)
                    frequency2.append(Puffer[a+(i*34-22)][20:n])
                    n = Puffer[a+(i*34-19)].find('</', 30)
                    original_network_id2.append(Puffer[a+(i*34-19)][30:n])
                    n = Puffer[a+(i*34-18)].find('</', 23)
                    transport_id2.append(Puffer[a+(i*34-18)][23:n])

    def TransponderParameter_Sortieren():

        for j in range(len(frequency2)):
            for i in range(0, len(frequency2)-1, 1):
                if int(frequency2[i]) > int(frequency2[i+1]):
                    frequency2[i], frequency2[i+1] = frequency2[i+1], frequency2[i]
                    uwServiceStartIndex[i], uwServiceStartIndex[i+1] = uwServiceStartIndex[i+1], uwServiceStartIndex[i]
                    uwServiceEndIndex[i], uwServiceEndIndex[i+1] = uwServiceEndIndex[i+1], uwServiceEndIndex[i]
                    uwServiceCount[i], uwServiceCount[i+1] = uwServiceCount[i+1], uwServiceCount[i]
                    nitVersion[i], nitVersion[i+1] = nitVersion[i+1], nitVersion[i]
                    channelIndex[i], channelIndex[i+1] = channelIndex[i+1], channelIndex[i]
                    original_network_id2[i], original_network_id2[i+1] = original_network_id2[i+1], original_network_id2[i]
                    transport_id2[i], transport_id2[i+1] = transport_id2[i+1], transport_id2[i]

#--------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title("Transponder Parameter")
    Fenster.geometry("+" + str(Master.winfo_x()+410) + "+" + str(Master.winfo_y()+6)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Scroll_Vertikal = tk.Scrollbar(Fenster, width=15)
    Listen_Box = tk.Listbox(Fenster, width=50, height=42, yscrollcommand=Scroll_Vertikal.set)
    Titelleiste = tk.Label(Fenster, text="   TID  Freq   sStart sEnde  SCt oNID TrID  NIT", relief="sunken", anchor="w", font=Schrift)
    Statuszeile = tk.Label(Fenster, text="", relief="sunken", anchor="w", font="Consolas 1")
    Scroll_Vertikal.config(command=Listen_Box.yview)
    Listen_Box.config(bg=Hintergrund, fg=Vordergrund, font=Schrift)
    Titelleiste.pack(side="top", fill="x", padx=2, pady=1)
    Statuszeile.pack(side="bottom", fill="x", padx=2, pady=1)
    Scroll_Vertikal.pack(side="right", fill="y", padx=1, pady=1)
    Listen_Box.pack(fill="both", padx=2, pady=1, expand=True)

    TransponderParameter_Loeschen()
    TransponderParameter_Laden()
    TransponderParameter_Sortieren()
    if len(channelIndex) == 0:
        Listen_Box.insert(tk.END, "  Keine Transponder Parameter!")
    else:
        for i in range(len(channelIndex)):
            Listen_Box.insert(tk.END, "{:>6s}  {:6s} {:6s} {:6s} {:3s} {:4s} {:5s} {:3s}"\
                .format(channelIndex[i], frequency2[i], uwServiceStartIndex[i], uwServiceEndIndex[i],\
                uwServiceCount[i], original_network_id2[i], transport_id2[i], nitVersion[i]))
        Listen_Box.selection_set(0)
        Listen_Box.focus_set()

    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

###############################################################################################################

def Tuning_Info():

    def TuningInfo_Loeschen():

        unFrequency.clear()
        unTSID.clear()
        unONID.clear()
        abwSymbolRate.clear()
        abwPolarization.clear() 
        abwCodeRate.clear()
        bwDVBS2.clear()
        abwModulationType.clear()
        bwDirection.clear()
        abwAnglePrec.clear()
        ucAngle.clear()
        ucNoOfServices.clear()
        usTPHandle.clear()

    def TuningInfo_Laden():

        for a in range(len(Puffer)):
            if Puffer[a] == "<astTuningInfo>\n":
                a += 1           # Zeiger auf "<TPCount0>"
                i = 0
                while Puffer[a+i*17] != "</astTuningInfo>\n":
                    i += 1
                    n = Puffer[a+(i*17-16)].find('</', 22)
                    unFrequency.append(Puffer[a+(i*17-16)][22:n])
                    n = Puffer[a+(i*17-15)].find('</', 17)
                    unTSID.append(Puffer[a+(i*17-15)][17:n])
                    n = Puffer[a+(i*17-14)].find('</', 17)
                    unONID.append(Puffer[a+(i*17-14)][17:n])
                    n = Puffer[a+(i*17-13)].find('</', 24)
                    abwSymbolRate.append(Puffer[a+(i*17-13)][24:n])
                    n = Puffer[a+(i*17-12)].find('</', 26)
                    abwPolarization.append(Puffer[a+(i*17-12)][26:n])
                    n = Puffer[a+(i*17-11)].find('</', 22)
                    abwCodeRate.append(Puffer[a+(i*17-11)][22:n])
                    n = Puffer[a+(i*17-10)].find('</', 18)
                    bwDVBS2.append(Puffer[a+(i*17-10)][18:n])
                    n = Puffer[a+(i*17-9)].find('</', 28)
                    abwModulationType.append(Puffer[a+(i*17-9)][28:n])
                    n = Puffer[a+(i*17-7)].find('</', 22)
                    bwDirection.append(Puffer[a+(i*17-7)][22:n])
                    n = Puffer[a+(i*17-6)].find('</', 23)
                    abwAnglePrec.append(Puffer[a+(i*17-6)][23:n])
                    n = Puffer[a+(i*17-5)].find('</', 18)
                    ucAngle.append(Puffer[a+(i*17-5)][18:n])
                    n = Puffer[a+(i*17-4)].find('</', 25)
                    ucNoOfServices.append(Puffer[a+(i*17-4)][25:n])
                    n = Puffer[a+(i*17-3)].find('</', 21)
                    usTPHandle.append(Puffer[a+(i*17-3)][21:n])

    def TuningInfo_Sortieren():

        for j in range(len(unFrequency)):
            for i in range(0, len(unFrequency)-1, 1):
                if int(unFrequency[i]) > int(unFrequency[i+1]):
                    unFrequency[i], unFrequency[i+1] = unFrequency[i+1], unFrequency[i]
                    unTSID[i], unTSID[i+1] = unTSID[i+1], unTSID[i]
                    unONID[i], unONID[i+1] = unONID[i+1], unONID[i]
                    abwSymbolRate[i], abwSymbolRate[i+1] = abwSymbolRate[i+1], abwSymbolRate[i]
                    abwPolarization[i], abwPolarization[i+1] = abwPolarization[i+1], abwPolarization[i]
                    abwCodeRate[i], abwCodeRate[i+1] = abwCodeRate[i+1], abwCodeRate[i]
                    bwDVBS2[i], bwDVBS2[i+1] = bwDVBS2[i+1], bwDVBS2[i]
                    abwModulationType[i], abwModulationType[i+1] = abwModulationType[i+1], abwModulationType[i]
                    bwDirection[i], bwDirection[i+1] = bwDirection[i+1], bwDirection[i]
                    abwAnglePrec[i], abwAnglePrec[i+1] = abwAnglePrec[i+1], abwAnglePrec[i]
                    ucAngle[i], ucAngle[i+1] = ucAngle[i+1], ucAngle[i]
                    ucNoOfServices[i], ucNoOfServices[i+1] = ucNoOfServices[i+1], ucNoOfServices[i]
                    usTPHandle[i], usTPHandle[i+1] = usTPHandle[i+1], usTPHandle[i]

#--------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title("Tuning Info")
    Fenster.geometry("+" + str(Master.winfo_x()+410) + "+" + str(Master.winfo_y()+6)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Scroll_Vertikal = tk.Scrollbar(Fenster, width=15)
    Listen_Box = tk.Listbox(Fenster, width=61, height=42, yscrollcommand=Scroll_Vertikal.set)
    Titelleiste = tk.Label(Fenster, text="    Freq  Pol SymRt  TSID oNID CR S2 Mod Dir Angel NOS TPH", relief="sunken", anchor="w", font=Schrift)
    Statuszeile = tk.Label(Fenster, text="", relief="sunken", anchor="w", font="Consolas 1")
    Scroll_Vertikal.config(command=Listen_Box.yview)
    Listen_Box.config(bg=Hintergrund, fg=Vordergrund, font=Schrift)
    Titelleiste.pack(side="top", fill="x", padx=2, pady=1)
    Statuszeile.pack(side="bottom", fill="x", padx=2, pady=1)
    Scroll_Vertikal.pack(side="right", fill="y", padx=1, pady=1)
    Listen_Box.pack(fill="both", padx=2, pady=1, expand=True)

    TuningInfo_Loeschen()
    TuningInfo_Laden()
    TuningInfo_Sortieren()
    if len(unFrequency) == 0:
        Listen_Box.insert(tk.END, "  Keine Tuning Informationen!")
    else:
        for i in range(len(unFrequency)):
            pol = abwPolarization[i].replace("1","H").replace("0","V")
            Listen_Box.insert(tk.END, "    {:5s}  {:2s} {:6s} {:5s} {:4s} {:2s} {:2s} {:2s} {:2s} {:>3s},{:2s} {:3} {:4s}"\
                .format(unFrequency[i], pol, abwSymbolRate[i], unTSID[i], unONID[i], abwCodeRate[i], bwDVBS2[i],\
                abwModulationType[i], bwDirection[i], ucAngle[i], abwAnglePrec[i], ucNoOfServices[i], usTPHandle[i]))
        Listen_Box.selection_set(0)
        Listen_Box.focus_set()

    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

###############################################################################################################

def Hilfe_Abkuerzungen(event=None):    # <F1>

    Fenster = tk.Toplevel(Master)
    Fenster.title("Abkürzungen")
    Fenster.geometry("+" + str(Master.winfo_x()+480) + "+" + str(Master.winfo_y()+48)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Text_Fenster = tk.Text(Fenster, width=35, height=35, pady=10, padx=10)
    Text_Fenster.config(fg=Vordergrund, bg=Hintergrund, font="Consolas 10", wrap="none")
    Text_Fenster.pack(fill="both", padx=3, pady=3, expand=True)

    Text_Fenster.configure(state="normal")
    Text_Fenster.delete("1.0", tk.END)
    Text_Fenster.insert(tk.END, "\n   Angel =  Winkel\n")
    Text_Fenster.insert(tk.END, "   B     =  Blockieren, Sperren\n")
    Text_Fenster.insert(tk.END, "   CR    =  Code-Rate\n")
    Text_Fenster.insert(tk.END, "   Dir   =  Ausrichtung (West/Ost)\n")
    Text_Fenster.insert(tk.END, "   Fav   =  Favoriten\n")
    Text_Fenster.insert(tk.END, "   Freq  =  Frequenz\n")
    Text_Fenster.insert(tk.END, "   HTp   =  Home-Tp\n")
    Text_Fenster.insert(tk.END, "   L     =  Löschen\n")
    Text_Fenster.insert(tk.END, "   LCN   =  Logische Kanalnummer\n")
    Text_Fenster.insert(tk.END, "   mNr   =  minor Nummer\n")
    Text_Fenster.insert(tk.END, "   Mod   =  Modulation\n")
    Text_Fenster.insert(tk.END, "   NID   =  Netzwerk-ID\n")
    Text_Fenster.insert(tk.END, "   NIT   =  NIT-Version\n")
    Text_Fenster.insert(tk.END, "   NOS   =  Anzahl Services\n")
    Text_Fenster.insert(tk.END, "   oNID  =  originale Netzwerk-ID\n")
    Text_Fenster.insert(tk.END, "   P     =  Pay-TV\n")
    Text_Fenster.insert(tk.END, "   Pol   =  Polarisation\n")
    Text_Fenster.insert(tk.END, "   Pos   =  Position\n")
    Text_Fenster.insert(tk.END, "   S     =  Sichtbarkeit\n")
    Text_Fenster.insert(tk.END, "   S2    =  DVBS2\n")
    Text_Fenster.insert(tk.END, "   SCt   =  Service-Count\n")
    Text_Fenster.insert(tk.END, "   SID   =  Service-ID\n")
    Text_Fenster.insert(tk.END, "   STyp  =  Service-Typ\n")
    Text_Fenster.insert(tk.END, "   SymRt =  Symbolrate\n")
    Text_Fenster.insert(tk.END, "   TID   =  Transponder-ID\n")
    Text_Fenster.insert(tk.END, "   TPH   =  TP-Handle\n")
    Text_Fenster.insert(tk.END, "   TPI   =  Transponder-Index\n")
    Text_Fenster.insert(tk.END, "   TrID  =  Transport-ID\n")
    Text_Fenster.insert(tk.END, "   TS    =  Transmission-System\n")
    Text_Fenster.insert(tk.END, "   TSID  =  Transponder-Service-ID\n")
    Text_Fenster.insert(tk.END, "   Ü     =  Überspringen\n")
    Text_Fenster.insert(tk.END, "   V     =  Verstecken\n")
    Text_Fenster.insert(tk.END, "   VST   =  Videostream-Typ\n")
    Text_Fenster.configure(state="disabled")

    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

def Hilfe_Tastatur(event=None):    # <F2>

    Fenster = tk.Toplevel(Master)
    Fenster.title("Tastaturbedienung")
    Fenster.geometry("+" + str(Master.winfo_x()+473) + "+" + str(Master.winfo_y()+172)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Text_Fenster = tk.Text(Fenster, width=39, height=22, pady=10, padx=10)
    Text_Fenster.config(fg=Vordergrund, bg=Hintergrund, font="Consolas 10", wrap="none")
    Text_Fenster.pack(fill="both", padx=3, pady=3, expand=True)

    Text_Fenster.configure(state="normal")
    Text_Fenster.delete("1.0", tk.END)
    Text_Fenster.insert(tk.END, "\n   Datei öffnen:          <Strg+O>\n")
    Text_Fenster.insert(tk.END, "   Datei speichern:       <Strg+S>\n")
    Text_Fenster.insert(tk.END, "   Alle Sender anzeigen:  <F3>\n")
    Text_Fenster.insert(tk.END, "   nach Nummer sortieren: <F4>\n")
    Text_Fenster.insert(tk.END, "   nach Namen sortieren:  <F5>\n")
    Text_Fenster.insert(tk.END, "   Sender suchen:         <F7>\n")
    Text_Fenster.insert(tk.END, "   Sender kopieren:       <F8>\n")
    Text_Fenster.insert(tk.END, "   Sender bearbeiten:     <Return>\n")
    Text_Fenster.insert(tk.END, "   Sender entfernen:      <Strg+D>>\n")
    Text_Fenster.insert(tk.END, "   Senderliste drucken:   <Strg+P>>\n\n")

    Text_Fenster.insert(tk.END, "   Service Info:          <F9>\n")
    Text_Fenster.insert(tk.END, "   nach LCN sortieren:    <F10>\n")
    Text_Fenster.insert(tk.END, "   nach Namen sortieren:  <F11>\n")
    Text_Fenster.insert(tk.END, "   nach SID sortieren:    <F12>\n")
    Text_Fenster.insert(tk.END, "   ServInfo bearbeiten:   <Return>\n")
    Text_Fenster.insert(tk.END, "   ServInfo erstellen:    <Strg+I>\n")
    Text_Fenster.insert(tk.END, "   ServInfo entfernen:    <Strg+D>\n")
    Text_Fenster.insert(tk.END, "   SInfo neu nummerieren: <Strg+N>\n")
    Text_Fenster.insert(tk.END, "   SInfoliste drucken:    <Strg+P>\n")

    Text_Fenster.configure(state="disabled")

    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

def Hilfe_Ueber():

    Fenster = tk.Toplevel(Master)
    Fenster.title("Über")
    Fenster.geometry("+" + str(Master.winfo_x()+473) + "+" + str(Master.winfo_y()+350)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)
    tk.Label(Fenster).pack()
    Zeile1 = tk.Label(Fenster, text="Channel View", font="Helvetica 20 bold")
    Zeile2 = tk.Label(Fenster, text="Version 1.07", font="Helvetica 14")
    Zeile3 = tk.Label(Fenster, text="Woodstock (C) 2026", font="Helvetica 12")
    Zeile1.pack(padx=110, pady=10) 
    Zeile2.pack(pady=10) 
    Zeile3.pack(pady=10)
    tk.Label(Fenster).pack()
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

###############################################################################################################

def Statuszeile_Anzeigen(*args):

    Statusleiste.set(" {:6d} Sender   |   {:s}   |   {:s}".format(StatusAnzahl.get(), StatusText.get(), TLLDatei))

###############################################################################################################

def Programm_Beenden(event=None):    # <Strg+Q>

    if GEAENDERT:
        if message.askyesno("Channel View", "\nEs wurden Änderungen vorgenommen. Sollen die gespeichert werden?  "):
            Datei_Speichern()

    Master.destroy()

###############################################################################################################

Menuleiste = tk.Menu(Master, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Datei = tk.Menu(Menuleiste, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Bearbeiten = tk.Menu(Menuleiste, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Information = tk.Menu(Menuleiste, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Hilfe = tk.Menu(Menuleiste, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")

Menuleiste.add_cascade(label=" Datei ", menu=Menu_Datei, underline=1)
Menu_Datei.add_command(label="  Öffnen", command=Datei_Oeffnen, accelerator=" <Strg+O> ")
Menu_Datei.add_command(label="  Speichern", command=Datei_Speichern, accelerator=" <Strg+S> ")
Menu_Datei.add_command(label="  Speichern unter", command=Datei_Speichern_Unter)
Menu_Datei.add_separator()
Menu_Datei.add_command(label="  Beenden", command=Programm_Beenden, accelerator=" <Strg+Q> ")

Menuleiste.add_cascade(label=" Bearbeiten ", menu=Menu_Bearbeiten, underline=1)

Menu_Favoriten = tk.Menu(Menu_Bearbeiten, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Bearbeiten.add_cascade(label="  Favoriten ", menu=Menu_Favoriten, underline=3)
Menu_Favoriten.add_command(label="  Favoriten 1", command=lambda: Favoriten_Anzeigen(1))
Menu_Favoriten.add_command(label="  Favoriten 2", command=lambda: Favoriten_Anzeigen(2))
Menu_Favoriten.add_command(label="  Favoriten 3", command=lambda: Favoriten_Anzeigen(3))
Menu_Favoriten.add_command(label="  Favoriten 4", command=lambda: Favoriten_Anzeigen(4))

Menu_Sortieren = tk.Menu(Menu_Bearbeiten, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Bearbeiten.add_cascade(label="  Sortieren", menu=Menu_Sortieren, underline=2)
Menu_Sortieren.add_command(label="  Nummer",    command=lambda: Sender_Sortieren("Nummer"), accelerator=" <F4> ")
Menu_Sortieren.add_command(label="  Namen",     command=lambda: Sender_Sortieren("Name"), accelerator=" <F5> ")
Menu_Sortieren.add_command(label="  Frequenz",  command=lambda: Sender_Sortieren("Frequenz"))
Menu_Sortieren.add_command(label="  ServiceID", command=lambda: Sender_Sortieren("ServiceID"))

Menu_Filtern = tk.Menu(Menu_Bearbeiten, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Bearbeiten.add_cascade(label="  Filtern ", menu=Menu_Filtern, underline=2)
Menu_Filtern.add_command(label="  SD-TV ",  command=lambda: Filtern_serviceType("SD-TV"))
Menu_Filtern.add_command(label="  HD-TV ",  command=lambda: Filtern_serviceType("HD-TV"))
Menu_Filtern.add_command(label="  UHD-TV ", command=lambda: Filtern_serviceType("UHD-TV"))
Menu_Filtern.add_command(label="  Radio ",  command=lambda: Filtern_serviceType("Radio"))
Menu_Filtern.add_command(label="  Pay-TV ", command=Filtern_PayTV)

Menu_Markieren = tk.Menu(Menu_Bearbeiten, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Bearbeiten.add_cascade(label="  Markieren", menu=Menu_Markieren, underline=2)
Menu_Ueberspringen = tk.Menu(Menu_Markieren, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Markieren.add_cascade(label="  Überspringen", menu=Menu_Ueberspringen)
Menu_Ueberspringen.add_command(label="  UHD-TV",    command=lambda: Sender_Markieren(1,1))
Menu_Ueberspringen.add_command(label="  Radio",     command=lambda: Sender_Markieren(1,2))
Menu_Ueberspringen.add_command(label="  Pay-TV",    command=lambda: Sender_Markieren(1,3))
Menu_Ueberspringen.add_command(label="  Unbekannte",command=lambda: Sender_Markieren(1,4))
Menu_Verstecken = tk.Menu(Menu_Markieren, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Markieren.add_cascade(label="  Verstecken", menu=Menu_Verstecken)
Menu_Verstecken.add_command(label="  UHD-TV",    command=lambda: Sender_Markieren(2,1))
Menu_Verstecken.add_command(label="  Radio",     command=lambda: Sender_Markieren(2,2))
Menu_Verstecken.add_command(label="  Pay-TV",    command=lambda: Sender_Markieren(2,3))
Menu_Verstecken.add_command(label="  Unbekannte",command=lambda: Sender_Markieren(2,4))
Menu_Sperren = tk.Menu(Menu_Markieren, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Markieren.add_cascade(label="  Sperren", menu=Menu_Sperren)
Menu_Sperren.add_command(label="  UHD-TV",    command=lambda: Sender_Markieren(3,1))
Menu_Sperren.add_command(label="  Radio",     command=lambda: Sender_Markieren(3,2))
Menu_Sperren.add_command(label="  Pay-TV",    command=lambda: Sender_Markieren(3,3))
Menu_Sperren.add_command(label="  Unbekannte",command=lambda: Sender_Markieren(3,4))
Menu_Loeschen = tk.Menu(Menu_Markieren, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Markieren.add_cascade(label="  Löschen", menu=Menu_Loeschen)
Menu_Loeschen.add_command(label="  UHD-TV",    command=lambda: Sender_Markieren(4,1))
Menu_Loeschen.add_command(label="  Radio",     command=lambda: Sender_Markieren(4,2))
Menu_Loeschen.add_command(label="  Pay-TV",    command=lambda: Sender_Markieren(4,3))
Menu_Loeschen.add_command(label="  Unbekannte",command=lambda: Sender_Markieren(4,4))

Menu_Bearbeiten.add_separator()
Menu_Bearbeiten.add_command(label="  Suchen", command=Sender_Suchen, accelerator=" <F7> ")
Menu_Bearbeiten.add_command(label="  Alle anzeigen", command=Alle_Anzeigen, accelerator=" <F3> ")
Menu_Bearbeiten.add_separator()
Menu_Bearbeiten.add_command(label="  Service Info", command=Service_Info, accelerator=" <F9> ")

Menuleiste.add_cascade(label=" Tuning ", menu=Menu_Information, underline=1)
Menu_Information.add_command(label="  Satelliten ", command=Satelliten_Info)
Menu_Information.add_command(label="  Transponder ", command=Transponder_Info)
Menu_Information.add_command(label="  Tuning Info ", command=Tuning_Info)
Menu_Information.add_command(label="  TP-Parameter ", command=Transponder_Parameter)

Menuleiste.add_cascade(label=" Hilfe ", menu=Menu_Hilfe, underline=1)
Menu_Hilfe.add_command(label="  Abkürzungen", command=Hilfe_Abkuerzungen, accelerator=" <F1> ")
Menu_Hilfe.add_command(label="  Tastatur", command=Hilfe_Tastatur, accelerator=" <F2> ")
Menu_Hilfe.add_separator()
Menu_Hilfe.add_command(label="  Über", command=Hilfe_Ueber)

Scroll_Vertikal = tk.Scrollbar(Master, width=15)
Listen_Box = tk.Listbox(Master, width=146, height=45, yscrollcommand=Scroll_Vertikal.set)
Titelleiste = tk.Label(Master, text="", relief="sunken", anchor="w", font=Schrift)
Titelleiste.config(text="  Nr     mNr   Sendername                    STyp    Freq     SID    TSID  oNID  VST    P  Ü  V  B  L     Fav1 Fav2 Fav3 Fav4 Fav5 Fav6 Fav7 Fav8")
Statuszeile = tk.Label(Master, textvariable=Statusleiste, relief="sunken", anchor="w", font="Helvetica 11")
Master.config(menu=Menuleiste)
Scroll_Vertikal.config(command=Listen_Box.yview)
Listen_Box.config(bg=Hintergrund, fg=Vordergrund, font=Schrift)
Titelleiste.pack(side="top", fill="x", padx=2, pady=1)
Statuszeile.pack(side="bottom", fill="x", padx=2, pady=1)
Scroll_Vertikal.pack(side="right", fill="y", padx=1, pady=1)
Listen_Box.pack(fill="both", padx=2, pady=1, expand=True)

Listen_Box.bind("<Double-Button-1>", Sender_Bearbeiten)
Listen_Box.bind("<Double-Button-3>", Sender_Ueberspringen)
Listen_Box.bind("<Button-3>", ServInfo_Erstellen)
Listen_Box.bind("<Return>", Sender_Bearbeiten)
Listen_Box.bind("<BackSpace>", Alle_Anzeigen)
Listen_Box.bind("<Control-Key-o>", Datei_Oeffnen)
Listen_Box.bind("<Control-Key-s>", Datei_Speichern)
Listen_Box.bind("<Control-Key-q>", Programm_Beenden)
Listen_Box.bind("<Control-Key-i>", ServInfo_Erstellen)
Listen_Box.bind("<Control-Key-d>", Sender_Entfernen)
Listen_Box.bind("<Control-Key-p>", Senderliste_Drucken)
Listen_Box.bind("<Control-Key-n>", ServInfo_Neu_Nummerieren)
Listen_Box.bind("<F1>", Hilfe_Abkuerzungen)
Listen_Box.bind("<F2>", Hilfe_Tastatur)
Listen_Box.bind("<F3>", Alle_Anzeigen)
Listen_Box.bind("<F4>", lambda event: Sender_Sortieren("Nummer", event))
Listen_Box.bind("<F5>", lambda event: Sender_Sortieren("Name", event))
Listen_Box.bind("<F7>", Sender_Suchen)
Listen_Box.bind("<F8>", Sender_Kopieren)
Listen_Box.bind("<F9>", Service_Info)

#----------------------------------------------------------------------

StatusAnzahl.trace_add("write", Statuszeile_Anzeigen)
StatusText.trace_add("write", Statuszeile_Anzeigen)

Statuszeile_Anzeigen()
Datei_Oeffnen()

Master.protocol("WM_DELETE_WINDOW", Programm_Beenden)

Master.mainloop()

###############################################################################################################
