#! /usr/bin/env python3
#
#  ChanView v1.05
#
#  LG-TV UM7100PLA
#
###############################################################################################################

import tkinter as tk
import tkinter.messagebox as message
import tkinter.filedialog as fdialog
import os

###############################################################################################################

# Channel-Listen
prNum, minorNum, original_network_id, transport_id, service_id, serviceType = [], [], [], [], [], []
frequency, mapAttr, favoriteIdxA, favoriteIdxB, favoriteIdxC, favoriteIdxD = [], [], [], [], [], [] 
favoriteIdxE, favoriteIdxF, favoriteIdxG, favoriteIdxH, isInvisable, isBlocked  = [], [], [], [], [], []
isSkipped, isDeleted, isScrambled, vchName, isUserSelCHNo, videoStreamType = [], [], [], [], [], []

# Service-Info
aucSvcName, usServiceID, bVisibilityFlag, bIsScramble, usLCNValue, ucServiceType, usTPIndex = [],[],[],[],[],[],[]

# Tuning-Info
unFrequency, unTSID, unONID, abwSymbolRate, abwPolarization, abwCodeRate, bwDVBS2 = [],[],[],[],[],[],[] 
abwModulationType, bwDirection, abwAnglePrec, ucAngle, ucNoOfServices, usTPHandle = [],[],[],[],[],[] 

# Satelliten-Info
SatelliteNameHex, Angle, AnglePrec, DirEastWest = [],[],[],[]

# Transponder-Info
TransponderId, Frequency, Polarisation, SymbolRate, TransmissionSystem, HomeTp = [],[],[],[],[],[]

# Transponder-Parameter
uwServiceStartIndex, uwServiceEndIndex, uwServiceCount, nitVersion = [],[],[],[]
channelIndex, frequency2, original_network_id2, transport_id2 = [],[],[],[]


Puffer = []           # alle Dateizeilen
idxITEM = []          # Zeiger auf <ITEM>'s
Aktuelle = []         # Zeiger auf aktuell angezeigte idxITEM[]
idxSID = []           # Zeiger auf <ServCount..>'s
aktSID = []           # Zeiger auf aktuell angezeigte idxSID[]

TLLDatei = ""
servTypText = []      # serviceType in Klartext
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

def Datei_Oeffnen(event=None):

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

def Datei_Speichern(event=None):

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

    with open(TLLDatei, "w", encoding="utf-8") as Datei:    # TLLDatei schreiben (überschreiben)
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

def servTypText_Laden(typ):

    if   typ == "1":    return "SD-TV"
    elif typ == "2":    return "Radio"
    elif typ == "3":    return "VText"
    elif typ == "7":    return "FM-Radio"
    elif typ == "10":   return "AAC-Radio"
    elif typ == "12":   return "Data/Test"
    elif typ == "17":   return "HD-TV"
    elif typ == "22":   return "SD-TV"
    elif typ == "25":   return "HD-TV"
    elif typ == "31":   return "UHD-TV"
    elif typ == "159":  return "UHD-TV"
    else:               return "unbekannt"

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
    n = Puffer[i+34].find("</", 9)
    vchName.append(Puffer[i+34][9:n])
    n = Puffer[i+38].find("</", 15)
    isUserSelCHNo.append(Puffer[i+38][15:n])
    n = Puffer[i+39].find("</", 17)
    videoStreamType.append(Puffer[i+39][17:n])

###############################################################################################################

def Listen_in_Puffer(nr):

    global Puffer

    # nur die Veränderbaren aktuallisieren
    Puffer[idxITEM[Aktuelle[nr]]+1]  = "<prNum>"         + prNum[nr]         + "</prNum>\n"
    Puffer[idxITEM[Aktuelle[nr]]+2]  = "<minorNum>"      + minorNum[nr]      + "</minorNum>\n"
    Puffer[idxITEM[Aktuelle[nr]]+34] = "<vchName>"       + vchName[nr]       + "</vchName>\n"
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
    # Sendername in Hex und Länge ändern
    Puffer[idxITEM[Aktuelle[nr]]+32] = "<hexVchName>" + vchName[nr].encode("utf-8").hex() + "</hexVchName>\n"
    Puffer[idxITEM[Aktuelle[nr]]+33] = "<notConvertedLengthOfVchName>" + str(len(vchName[nr])) + "</notConvertedLengthOfVchName>\n"
    Puffer[idxITEM[Aktuelle[nr]]+35] = "<lengthOfVchName>" + str(len(vchName[nr])) + "</lengthOfVchName>\n"

###############################################################################################################

def Sender_Zeile_Anzeigen(pos, i):

    Listen_Box.insert(pos, "  {:6s} {:5s} {:30.30s} {:10s} {:7s} {:6s} {:6s} {:5s} {:3s} │  {:2s} {:2s} {:2s} {:2s} {:2s} │  {:4s} {:4s} {:4s} {:4s} {:4s} {:4s} {:4s} {:4s}"\
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
        Sender_Zeile_Anzeigen(tk.END, i)
    StatusAnzahl.set(len(Aktuelle))
    Cursor_Anzeigen()

###############################################################################################################

def Alle_Anzeigen(event=None):

    global Aktuelle

    Puffer_in_Listen()
    Aktuelle.clear()
    for i in range(len(idxITEM)):
        Aktuelle.append(i)
    Aktuelle_Anzeigen()
    StatusText.set("Chronologisch")

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

def Filter_sTyp(typ):

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

def Filter_PayTV():

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

def Sortieren(gruppe):

    global Aktuelle

    # Bubble Sort
    for j in range(len(Aktuelle)):
        for i in range(0, len(Aktuelle)-1, 1):
            if gruppe == "Nummer": 
                if int(prNum[i]) > int(prNum[i+1]):
                    Aktuelle[i], Aktuelle[i+1] = Aktuelle[i+1], Aktuelle[i]
                    Listen_Tauschen(i)
            if gruppe == "Name": 
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

def Sender_Suchen(event=None):

    def Suche_Anzeigen(event=None):

        global Aktuelle

        Suchbegriff = Eingabefeld.get()
        Fenster.destroy()

        Aktuelle.clear()
        Listen_Loeschen()

        for i in range(len(idxITEM)):
            if Puffer[idxITEM[i]+34].lower().find(Suchbegriff.lower()) != -1:
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

###############################################################################################################

def Sender_Ueberspringen(event=None):        # Doppelklick Rechts

    global GEAENDERT, Puffer

    if Listen_Box.curselection() and len(Aktuelle) > 0:

        nr = Listen_Box.curselection()[0]

        if isSkipped[nr] == "0":
            Puffer[idxITEM[Aktuelle[nr]]+26] = "<isSkipped>1</isSkipped>\n"    # on
            isSkipped[nr] = "1"
        else:
            Puffer[idxITEM[Aktuelle[nr]]+26] = "<isSkipped>0</isSkipped>\n"    # off
            isSkipped[nr] = "0"

        Listen_Box.delete(nr)
        Sender_Zeile_Anzeigen(nr, nr)
        GEAENDERT = True

        Listen_Box.selection_set(nr+1)       # Markierung auf nächste Zeile
        Listen_Box.focus_set()

###############################################################################################################

markierte = 0    # global!!

###############################################################################################################

def Markieren(a,i):

    global GEAENDERT, Puffer, markierte

    if a == 1:   # überspringen
        if isSkipped[i] == "0":
            Puffer[idxITEM[Aktuelle[i]]+26] = "<isSkipped>1</isSkipped>\n"
            isSkipped[i] = "1"
            markierte += 1
    if a == 2:   # verstecken
        if isInvisable[i] == "0":
            Puffer[idxITEM[Aktuelle[i]]+24] = "<isInvisible>1</isInvisible>\n"
            isInvisable[i] = "1"
            markierte += 1
    if a == 3:   # sperren
        if isBlocked[i] == "0":
            Puffer[idxITEM[Aktuelle[i]]+25] = "<isBlocked>1</isBlocked>\n"
            isBlocked[i] = "1"
            markierte += 1
    if a == 4:   # löschen
        if isDeleted[i] == "0":
            Puffer[idxITEM[Aktuelle[i]]+28] = "<isDeleted>1</isDeleted>\n"
            isDeleted[i] = "1"
            markierte += 1

    GEAENDERT = True

###############################################################################################################

def Sender_Markieren(a,b):

    global markierte

    insgesamt = 0
    markierte = 0

    if b == 1:   # Radio
        for i in range(len(Aktuelle)):
            if serviceType[i] == "2" or serviceType[i] == "7" or serviceType[i] == "10":
                Markieren(a,i)
                insgesamt += 1

    if b == 2:   # Pay-TV
        for i in range(len(Aktuelle)):
            if isScrambled[i] == "1":
                Markieren(a,i)
                insgesamt += 1

    if b == 3:   # Doppelte
        for j in range(0, len(Aktuelle), 1):
            for i in range(j+1, len(Aktuelle), 1):
                if frequency[j] == frequency[i] and service_id[j] == service_id[i] and transport_id[j] == transport_id[i]: 
                    insgesamt += 1
                    # nur wenn beide noch nicht markiert
                    if (a == 1 and isSkipped[j] == "0" and isSkipped[i] == "0") or \
                       (a == 2 and isInvisable[j] == "0" and isInvisable[i] == "0") or \
                       (a == 3 and isBlocked[j] == "0" and isBlocked[i] == "0") or \
                       (a == 4 and isDeleted[j] == "0" and isDeleted[i] == "0"):
                        Markieren(a,i)

    if b == 4:   # Unbekannte
        for i in range(len(Aktuelle)):
            if (serviceType[i] !=  "1" and serviceType[i] !=  "2" and serviceType[i] !=  "7" and serviceType[i] != "10" and \
                serviceType[i] != "17" and serviceType[i] != "22" and serviceType[i] != "25" and serviceType[i] != "31") or \
                (prNum[i] ==  "0" and minorNum[i] == "0"):
                Markieren(a,i)
                insgesamt += 1

    Listen_Box.delete(0, tk.END) 
    Aktuelle_Anzeigen()
    message.showinfo("Channel View", "\nEs wurden " + str(markierte) + " von " + str(insgesamt) + " Sendern markiert.  ")

###############################################################################################################

###############################################################################################################

def Sender_Bearbeiten(event=None):

    def Eintrag_Aendern(event=None):

        global GEAENDERT

        if EingabeNr.get().isnumeric() and EingabemNr.get().isnumeric() and \
           EingabeFav1.get().isnumeric() and EingabeFav2.get().isnumeric() and EingabeFav3.get().isnumeric():

            vchName[nr] = EingabeName.get()
            prNum[nr] = EingabeNr.get()
            minorNum[nr] = EingabemNr.get()
            isUserSelCHNo[nr] = "1"           # immer!! ?? 
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

            Listen_Box.delete(nr)
            Sender_Zeile_Anzeigen(nr, nr)
            Listen_in_Puffer(nr)
            GEAENDERT = True

            Listen_Box.selection_set(nr+1)       # Markierung auf nächste Zeile
            Listen_Box.focus_set()
            Fenster.destroy()

#--------------------------------------------

    if Listen_Box.curselection() and len(Aktuelle) > 0:    # wenn Zeile markiert und mind. ein Listenelement

        Fenster = tk.Toplevel(Master)
        Fenster.title("Kanal bearbeiten")
        Fenster.geometry("+" + str(Master.winfo_x()+270) + "+" + str(Master.winfo_y()+300)) 
        Fenster.resizable(False, False)
        Fenster.wm_attributes("-topmost", True)

        nr = Listen_Box.curselection()[0]

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
        tk.Label(Fenster).grid(row=0, column=0, padx=30, pady=5)
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
        EingabeName.grid(row=1, column=2, columnspan=8, pady=10)
        # 3. Zeile = Nummern & Favoriten
        TextNr.grid(row=2, column=1, sticky="w", pady=20)
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
        CheckAttrP.grid(row=3, column=1, columnspan=2, sticky="w", pady=5)
        CheckAttrU.grid(row=3, column=2, columnspan=4)
        CheckAttrV.grid(row=3, column=5, columnspan=2, sticky="w")
        CheckAttrS.grid(row=3, column=7, columnspan=2, sticky="w")
        CheckAttrL.grid(row=3, column=8, columnspan=3)
        # 5. Zeile
        ButtonSpeichern.grid(row=4, column=1, columnspan=5, padx=50, pady=18, ipadx=25, sticky="e")
        ButtonAbbrechen.grid(row=4, column=6, columnspan=5, padx=50, pady=18, ipadx=23, sticky="w")
        tk.Label(Fenster).grid(row=5, column=0, pady=1)

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

def Sender_Entfernen(event=None):

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

    if Listen_Box.curselection():

        nr = Listen_Box.curselection()[0]

        for i in range(42):
            Puffer.pop(idxITEM[Aktuelle[nr]])    # <ITEM> bis </ITEM> aus Puffer löschen
        idxITEM.pop(-1)                          # immer letzten Zeiger löschen, Puffer ist unsortiert!!

        for i in range(len(Aktuelle)):           # nur nachfolgende Aktuelle -1
            if Aktuelle[i] > Aktuelle[nr]:   Aktuelle[i] -= 1
        Aktuelle.pop(nr)

        Listenelement_Loeschen()                 # 25 Listen
        GEAENDERT = True

        StatusAnzahl.set(len(Aktuelle))
        Listen_Box.delete(nr)
        Listen_Box.selection_set(nr)             # Markierung auf neue Zeile
        Listen_Box.focus_set()

###############################################################################################################

###############################################################################################################

def Service_Info(event=None):

    def SID_Listen_Loeschen():

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
                i += 1
                while Puffer[i] != "</astServiceInfo>\n":
                    idxSID.append(i)               # Zeiger auf <ServCount..>'s
                    aktSID.append(len(aktSID))     # Zeiger auf Aktuellen
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
            Listen_Box.insert(tk.END, " {:>5s}   {:30.30s} {:6s} {:2s} {:2s} {:3s} {:3s}".format(usLCNValue[i], aucSvcName[i],\
                                         usServiceID[i], bIsScramble[i], bVisibilityFlag[i], ucServiceType[i], usTPIndex[i]))
        Listen_Box.selection_set(0)
        Listen_Box.focus_set()


    def Eintrag_Entfernen(event=None):

        global GEAENDERT, Puffer

        if Listen_Box.curselection():

            nr = Listen_Box.curselection()[0]

            aucSvcName[nr] = " "
            usServiceID[nr] = "0"
            bVisibilityFlag[nr] = "0"
            bIsScramble[nr] = "0"
            usLCNValue[nr] = "0"
            ucServiceType[nr] = "0"
            usTPIndex[nr] = "0"

            Puffer[idxSID[aktSID[nr]]+1] = '<hexAucSvcName type="0"> </hexAucSvcName>\n'
            Puffer[idxSID[aktSID[nr]]+2] = '<aucSvcName type="0"> </aucSvcName>\n'
            Puffer[idxSID[aktSID[nr]]+3] = '<usServiceID type="0">0</usServiceID>\n'
            Puffer[idxSID[aktSID[nr]]+4] = '<bVisibilityFlag type="0">0</bVisibilityFlag>\n'
            Puffer[idxSID[aktSID[nr]]+5] = '<bIsScramble type="0">0</bIsScramble>\n'
            Puffer[idxSID[aktSID[nr]]+6] = '<usLCNValue type="0">0</usLCNValue>\n'
            Puffer[idxSID[aktSID[nr]]+7] = '<ucServiceType type="0">0</ucServiceType>\n'
            Puffer[idxSID[aktSID[nr]]+8] = '<ucSvcNameLength type="0">0</ucSvcNameLength>\n'
            Puffer[idxSID[aktSID[nr]]+9] = '<usTPIndex type="0">0</usTPIndex>\n'

            Listen_Box.delete(nr)
            Listen_Box.insert(nr, " {:>5s}   {:30.30s} {:6s} {:2s} {:2s} {:3s} {:3s}".format(usLCNValue[nr], aucSvcName[nr],\
                                      usServiceID[nr], bIsScramble[nr], bVisibilityFlag[nr], ucServiceType[nr], usTPIndex[nr]))
            Listen_Box.selection_set(nr+1)      # Markierung auf nächste Zeile
            Listen_Box.focus_set()
            GEAENDERT = True

    def Eintrag_Bearbeiten(event=None):

        def Eintrag_Aendern(event=None):

            global GEAENDERT

            if EingabeLCN.get().isnumeric():

                usLCNValue[nr] = EingabeLCN.get()
                aucSvcName[nr] = EingabeName.get()
                Puffer[idxSID[aktSID[nr]]+6] = '<usLCNValue type="0">' + usLCNValue[nr] + '</usLCNValue>\n'
                Puffer[idxSID[aktSID[nr]]+2] = '<aucSvcName type="0">' + aucSvcName[nr] + '</aucSvcName>\n'
                Puffer[idxSID[aktSID[nr]]+1] = '<hexAucSvcName type="0">' + aucSvcName[nr].encode("utf-8").hex() + '</hexAucSvcName>\n'
                Puffer[idxSID[aktSID[nr]]+8] = '<ucSvcNameLength type="0">' + str(len(aucSvcName[nr])) + '</ucSvcNameLength>\n'
                GEAENDERT = True

                Listen_Box.delete(nr)
                Listen_Box.insert(nr, " {:>5s}   {:30.30s} {:6s} {:2s} {:2s} {:3s} {:3s}".format(usLCNValue[nr], aucSvcName[nr],\
                                          usServiceID[nr], bIsScramble[nr], bVisibilityFlag[nr], ucServiceType[nr], usTPIndex[nr]))
                Listen_Box.selection_set(nr+1)
                Listen_Box.focus_set()
                Fenster2.destroy()

        if Listen_Box.curselection():

            Fenster2 = tk.Toplevel(Fenster)
            Fenster2.title("Logische Kanalnummer bearbeiten")
            Fenster2.geometry("+" + str(Fenster.winfo_x()+20) + "+" + str(Fenster.winfo_y()+308)) 
            Fenster2.resizable(False, False)
            Fenster2.wm_attributes("-topmost", True)

            nr = Listen_Box.curselection()[0]

            EingabeLCN =   tk.Entry(Fenster2, bd=3, width=5, font="Helvetica 11")
            EingabeName =  tk.Entry(Fenster2, bd=3, width=30, font="Helvetica 11")
            EingabeLCN.pack(padx=40, pady=25, side="left")
            EingabeName.pack(side="left")            
            tk.Label(Fenster2).pack(padx=15, side="left")
        
            EingabeLCN.insert(0, usLCNValue[nr])
            EingabeName.insert(0, aucSvcName[nr])
            EingabeLCN.select_range(0, tk.END)
            EingabeLCN.focus_set()

            EingabeLCN.bind("<Return>", Eintrag_Aendern)
            EingabeName.bind("<Return>", Eintrag_Aendern)
            Fenster2.bind("<Escape>", lambda event: Fenster2.destroy())

#--------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title("Service Info")
    Fenster.geometry("+" + str(Master.winfo_x()+713) + "+" + str(Master.winfo_y()+7)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Scroll_Vertikal = tk.Scrollbar(Fenster, width=15)
    Listen_Box = tk.Listbox(Fenster, width=61, height=41, yscrollcommand=Scroll_Vertikal.set)
    Titelleiste = tk.Label(Fenster, text="   LCN   Sendername                     SID    P  V STyp TPI", relief="sunken", anchor="w", font=Schrift)
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
            Listen_Box.insert(tk.END, " {:>5s}   {:30.30s} {:6s} {:2s} {:2s} {:3s} {:3s}".format(usLCNValue[i], aucSvcName[i],\
                                         usServiceID[i], bIsScramble[i], bVisibilityFlag[i], ucServiceType[i], usTPIndex[i]))
        Listen_Box.selection_set(0)
        Listen_Box.focus_set()
    Statuszeile.config(text = "   {:5d}    |    Sortieren:   LCN = <F9>    Name = <F10>    SID = <F11>".format(i+1))

    Listen_Box.bind("<Double-Button-1>", Eintrag_Bearbeiten)
    Listen_Box.bind("<Return>", Eintrag_Bearbeiten)
    Listen_Box.bind("<Control-Key-d>", Eintrag_Entfernen)
    Listen_Box.bind("<F9>", lambda event: SID_Sortieren("LCN"))
    Listen_Box.bind("<F10>", lambda event: SID_Sortieren("Name"))
    Listen_Box.bind("<F11>", lambda event: SID_Sortieren("SID"))
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

###############################################################################################################

def Satelliten_Info(event=None):

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

#--------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title("Satelliten Info")
    Fenster.geometry("+" + str(Master.winfo_x()+420) + "+" + str(Master.winfo_y()+6)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)   # Fenster immer im Vordergrund halten

    Scroll_Vertikal = tk.Scrollbar(Fenster, width=15)
    Listen_Box = tk.Listbox(Fenster, width=46, height=42, yscrollcommand=Scroll_Vertikal.set)
    Titelleiste = tk.Label(Fenster, text="  Pos  Satellit                    Angel Dir", relief="sunken", anchor="w", font=Schrift)
    Statuszeile = tk.Label(Fenster, text="", relief="sunken", anchor="w", font="Consolas 1")
    Scroll_Vertikal.config(command=Listen_Box.yview)
    Listen_Box.config(bg=Hintergrund, fg=Vordergrund, font=Schrift)
    Titelleiste.pack(side="top", fill="x", padx=2, pady=1)
    Statuszeile.pack(side="bottom", fill="x", padx=2, pady=1)
    Scroll_Vertikal.pack(side="right", fill="y", padx=1, pady=1)
    Listen_Box.pack(fill="both", padx=2, pady=1, expand=True)

    SatellitenInfo_Loeschen()
    SatellitenInfo_Laden()
    if len(SatelliteNameHex) == 0:
        Listen_Box.insert(tk.END, "  Keine Satelliten Informationen!")
    else:
        for i in range(len(SatelliteNameHex)):
            Listen_Box.insert(tk.END, "{:5d}  {:27.27s} {:>3s},{:2s} {:2s}"\
                .format(i+1, bytearray.fromhex(SatelliteNameHex[i]).decode(), Angle[i], AnglePrec[i], DirEastWest[i]))
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

#--------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title("Transponder Info")
    Fenster.geometry("+" + str(Master.winfo_x()+490) + "+" + str(Master.winfo_y()+6)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Scroll_Vertikal = tk.Scrollbar(Fenster, width=15)
    Listen_Box = tk.Listbox(Fenster, width=36, height=42, yscrollcommand=Scroll_Vertikal.set)
    Titelleiste = tk.Label(Fenster, text="  Pos  TPI  Freq  Pol SymRt  TS HTp", relief="sunken", anchor="w", font=Schrift)
    Statuszeile = tk.Label(Fenster, text="", relief="sunken", anchor="w", font="Consolas 1")
    Scroll_Vertikal.config(command=Listen_Box.yview)
    Listen_Box.config(bg=Hintergrund, fg=Vordergrund, font=Schrift)
    Titelleiste.pack(side="top", fill="x", padx=2, pady=1)
    Statuszeile.pack(side="bottom", fill="x", padx=2, pady=1)
    Scroll_Vertikal.pack(side="right", fill="y", padx=1, pady=1)
    Listen_Box.pack(fill="both", padx=2, pady=1, expand=True)

    TransponderInfo_Loeschen()
    TransponderInfo_Laden()
    if len(TransponderId) == 0:
        Listen_Box.insert(tk.END, "  Keine Transponder Informationen!")
    else:
        for i in range(len(TransponderId)):
            Listen_Box.insert(tk.END, "{:5d}  {:4s} {:6s} {:2s} {:6s} {:2s} {:2s}"\
                .format(i+1, TransponderId[i], Frequency[i], Polarisation[i], SymbolRate[i], TransmissionSystem[i], HomeTp[i]))
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

#--------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title("Transponder Parameter")
    Fenster.geometry("+" + str(Master.winfo_x()+420) + "+" + str(Master.winfo_y()+6)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Scroll_Vertikal = tk.Scrollbar(Fenster, width=15)
    Listen_Box = tk.Listbox(Fenster, width=52, height=42, yscrollcommand=Scroll_Vertikal.set)
    Titelleiste = tk.Label(Fenster, text="  Pos  TPI  Freq   sStart sEnde  SCt oNID TrID  NIT", relief="sunken", anchor="w", font=Schrift)
    Statuszeile = tk.Label(Fenster, text="", relief="sunken", anchor="w", font="Consolas 1")
    Scroll_Vertikal.config(command=Listen_Box.yview)
    Listen_Box.config(bg=Hintergrund, fg=Vordergrund, font=Schrift)
    Titelleiste.pack(side="top", fill="x", padx=2, pady=1)
    Statuszeile.pack(side="bottom", fill="x", padx=2, pady=1)
    Scroll_Vertikal.pack(side="right", fill="y", padx=1, pady=1)
    Listen_Box.pack(fill="both", padx=2, pady=1, expand=True)

    TransponderParameter_Loeschen()
    TransponderParameter_Laden()
    if len(channelIndex) == 0:
        Listen_Box.insert(tk.END, "  Keine Transponder Parameter!")
    else:
        for i in range(len(channelIndex)):
            Listen_Box.insert(tk.END, "{:5d}  {:4s} {:6s} {:6s} {:6s} {:3s} {:4s} {:5s} {:3s}"\
                .format(i+1, channelIndex[i], frequency2[i], uwServiceStartIndex[i], uwServiceEndIndex[i],\
                uwServiceCount[i], original_network_id2[i], transport_id2[i], nitVersion[i]))
        Listen_Box.selection_set(0)
        Listen_Box.focus_set()

    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

###############################################################################################################

def Tuning_Info(event=None):

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

#--------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title("Tuning Info")
    Fenster.geometry("+" + str(Master.winfo_x()+370) + "+" + str(Master.winfo_y()+6)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Scroll_Vertikal = tk.Scrollbar(Fenster, width=15)
    Listen_Box = tk.Listbox(Fenster, width=64, height=42, yscrollcommand=Scroll_Vertikal.set)
    Titelleiste = tk.Label(Fenster, text="  Pos  Freq   TSID  oNID SymRt Pol CR S2 Mod Dir Angel NOS TPH", relief="sunken", anchor="w", font=Schrift)
    Statuszeile = tk.Label(Fenster, text="", relief="sunken", anchor="w", font="Consolas 1")
    Scroll_Vertikal.config(command=Listen_Box.yview)
    Listen_Box.config(bg=Hintergrund, fg=Vordergrund, font=Schrift)
    Titelleiste.pack(side="top", fill="x", padx=2, pady=1)
    Statuszeile.pack(side="bottom", fill="x", padx=2, pady=1)
    Scroll_Vertikal.pack(side="right", fill="y", padx=1, pady=1)
    Listen_Box.pack(fill="both", padx=2, pady=1, expand=True)

    TuningInfo_Loeschen()
    TuningInfo_Laden()
    if len(unFrequency) == 0:
        Listen_Box.insert(tk.END, "  Keine Tuning Informationen!")
    else:
        for i in range(len(unFrequency)):
            Listen_Box.insert(tk.END, "{:5d}  {:6s} {:5s} {:4s} {:6s}  {:2s} {:2s} {:2s} {:2s} {:2s} {:>3s},{:2s} {:3} {:4s}"\
                .format(i+1, unFrequency[i], unTSID[i], unONID[i], abwSymbolRate[i], abwPolarization[i], abwCodeRate[i], bwDVBS2[i],\
                abwModulationType[i], bwDirection[i], ucAngle[i], abwAnglePrec[i], ucNoOfServices[i], usTPHandle[i]))
        Listen_Box.selection_set(0)
        Listen_Box.focus_set()

    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

###############################################################################################################

def Hilfe_Abkuerzungen(event=None):

    Fenster = tk.Toplevel(Master)
    Fenster.title("Abkürzungen")
    Fenster.geometry("+" + str(Master.winfo_x()+520) + "+" + str(Master.winfo_y()+80)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)

    Text_Fenster = tk.Text(Fenster, width=35, height=33, pady=10, padx=10)
    Text_Fenster.config(fg=Vordergrund, bg=Hintergrund, font="Consolas 10", wrap="none")
    Text_Fenster.pack(fill="both", padx=3, pady=3, expand=True)

    Text_Fenster.configure(state="normal")
    Text_Fenster.delete("1.0", tk.END)
    Text_Fenster.insert(tk.END, "\n   Angel =  Winkel\n")
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
    Text_Fenster.insert(tk.END, "   oNID  =  Originale Netzwerk-ID\n")
    Text_Fenster.insert(tk.END, "   P     =  Pay-TV\n")
    Text_Fenster.insert(tk.END, "   Pol   =  Polarisation\n")
    Text_Fenster.insert(tk.END, "   Pos   =  Position\n")
    Text_Fenster.insert(tk.END, "   S     =  Sperren\n")
    Text_Fenster.insert(tk.END, "   S2    =  DVBS2\n")
    Text_Fenster.insert(tk.END, "   SCt   =  Service-Count\n")
    Text_Fenster.insert(tk.END, "   SID   =  Service-ID\n")
    Text_Fenster.insert(tk.END, "   STyp  =  Service-Typ\n")
    Text_Fenster.insert(tk.END, "   SymRt =  Symbolrate\n")
    Text_Fenster.insert(tk.END, "   TPH   =  TP-Handle\n")
    Text_Fenster.insert(tk.END, "   TPI   =  Transponder-Index\n")
    Text_Fenster.insert(tk.END, "   TrID  =  Transport-ID\n")
    Text_Fenster.insert(tk.END, "   TS    =  Transmission-System\n")
    Text_Fenster.insert(tk.END, "   TSID  =  Transponder-ID\n")
    Text_Fenster.insert(tk.END, "   Ü     =  Überspringen\n")
    Text_Fenster.insert(tk.END, "   V     =  Verstecken\n")
    Text_Fenster.insert(tk.END, "   VST   =  Videostream-Typ\n")
    Text_Fenster.configure(state="disabled")

    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###############################################################################################################

def Hilfe_Ueber():

    Fenster = tk.Toplevel(Master)
    Fenster.title("Über")
    Fenster.geometry("+" + str(Master.winfo_x()+480) + "+" + str(Master.winfo_y()+350)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", True)
    tk.Label(Fenster).pack()
    Zeile1 = tk.Label(Fenster, text="Channel View", font="Helvetica 20 bold")
    Zeile2 = tk.Label(Fenster, text="Version 1.05", font="Helvetica 14")
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

def Programm_Beenden(event=None):

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
Menu_Sortieren.add_command(label="  nach Nummer",    command=lambda: Sortieren("Nummer"))
Menu_Sortieren.add_command(label="  nach Namen",     command=lambda: Sortieren("Name"))
Menu_Sortieren.add_command(label="  nach Frequenz",  command=lambda: Sortieren("Frequenz"))
Menu_Sortieren.add_command(label="  nach ServiceID", command=lambda: Sortieren("ServiceID"))

Menu_Filter = tk.Menu(Menu_Bearbeiten, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Bearbeiten.add_cascade(label="  Filter ", menu=Menu_Filter, underline=2)
Menu_Filter.add_command(label="  SD-TV",  command=lambda: Filter_sTyp("SD-TV"))
Menu_Filter.add_command(label="  HD-TV",  command=lambda: Filter_sTyp("HD-TV"))
Menu_Filter.add_command(label="  UHD-TV", command=lambda: Filter_sTyp("UHD-TV"))
Menu_Filter.add_command(label="  Radio",  command=lambda: Filter_sTyp("Radio"))
Menu_Filter.add_command(label="  Pay-TV", command=Filter_PayTV)

Menu_Markieren = tk.Menu(Menu_Bearbeiten, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Bearbeiten.add_cascade(label="  Markieren", menu=Menu_Markieren, underline=2)
Menu_Ueberspringen = tk.Menu(Menu_Markieren, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Markieren.add_cascade(label="  Überspringen", menu=Menu_Ueberspringen)
Menu_Ueberspringen.add_command(label="  Radiosender", command=lambda: Sender_Markieren(1,1))
Menu_Ueberspringen.add_command(label="  Pay-TV",      command=lambda: Sender_Markieren(1,2))
Menu_Ueberspringen.add_command(label="  Doppelte",    command=lambda: Sender_Markieren(1,3))
Menu_Ueberspringen.add_command(label="  Unbekannte",  command=lambda: Sender_Markieren(1,4))
Menu_Verstecken = tk.Menu(Menu_Markieren, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Markieren.add_cascade(label="  Verstecken", menu=Menu_Verstecken)
Menu_Verstecken.add_command(label="  Radiosender", command=lambda: Sender_Markieren(2,1))
Menu_Verstecken.add_command(label="  Pay-TV",      command=lambda: Sender_Markieren(2,2))
Menu_Verstecken.add_command(label="  Doppelte",    command=lambda: Sender_Markieren(2,3))
Menu_Verstecken.add_command(label="  Unbekannte",  command=lambda: Sender_Markieren(2,4))
Menu_Sperren = tk.Menu(Menu_Markieren, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Markieren.add_cascade(label="  Sperren", menu=Menu_Sperren)
Menu_Sperren.add_command(label="  Radiosender", command=lambda: Sender_Markieren(3,1))
Menu_Sperren.add_command(label="  Pay-TV",      command=lambda: Sender_Markieren(3,2))
Menu_Sperren.add_command(label="  Doppelte",    command=lambda: Sender_Markieren(3,3))
Menu_Sperren.add_command(label="  Unbekannte",  command=lambda: Sender_Markieren(3,4))
Menu_Loeschen = tk.Menu(Menu_Markieren, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Markieren.add_cascade(label="  Löschen", menu=Menu_Loeschen)
Menu_Loeschen.add_command(label="  Radiosender", command=lambda: Sender_Markieren(4,1))
Menu_Loeschen.add_command(label="  Pay-TV",      command=lambda: Sender_Markieren(4,2))
Menu_Loeschen.add_command(label="  Doppelte",    command=lambda: Sender_Markieren(4,3))
Menu_Loeschen.add_command(label="  Unbekannte",  command=lambda: Sender_Markieren(4,4))

Menu_Bearbeiten.add_separator()
Menu_Bearbeiten.add_command(label="  Suchen", command=Sender_Suchen, accelerator=" <F3> ")
Menu_Bearbeiten.add_command(label="  Alle anzeigen", command=Alle_Anzeigen, accelerator=" <F5> ")
Menu_Bearbeiten.add_separator()
Menu_Bearbeiten.add_command(label="  Service Info", command=Service_Info, accelerator=" <F7> ")

Menuleiste.add_cascade(label=" Tuning ", menu=Menu_Information, underline=1)
Menu_Information.add_command(label="  Satelliten ", command=Satelliten_Info, underline=2)
Menu_Information.add_command(label="  Transponder ", command=Transponder_Info, underline=2)
Menu_Information.add_command(label="  TP-Parameter ", command=Transponder_Parameter, underline=3)
Menu_Information.add_command(label="  Tuning Info ", command=Tuning_Info, underline=3)

Menuleiste.add_cascade(label=" Hilfe ", menu=Menu_Hilfe, underline=1)
Menu_Hilfe.add_command(label="  Abkürzungen", command=Hilfe_Abkuerzungen)
Menu_Hilfe.add_separator()
Menu_Hilfe.add_command(label="  Über", command=Hilfe_Ueber)

Scroll_Vertikal = tk.Scrollbar(Master, width=15)
Listen_Box = tk.Listbox(Master, width=150, height=45, yscrollcommand=Scroll_Vertikal.set)
Titelleiste = tk.Label(Master, text="", relief="sunken", anchor="w", font=Schrift)
Titelleiste.config(text="  Nr     mNr   Sendername                     STyp       Freq    SID    TSID   oNID  VST    P  Ü  V  S  L     Fav1 Fav2 Fav3 Fav4 Fav5 Fav6 Fav7 Fav8")
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
Listen_Box.bind("<Return>", Sender_Bearbeiten)
Listen_Box.bind("<BackSpace>", Alle_Anzeigen)
Listen_Box.bind("<Control-Key-o>", Datei_Oeffnen)
Listen_Box.bind("<Control-Key-s>", Datei_Speichern)
Listen_Box.bind("<Control-Key-q>", Programm_Beenden)
Listen_Box.bind("<Control-Key-d>", Sender_Entfernen)
Listen_Box.bind("<F1>", Hilfe_Abkuerzungen)
Listen_Box.bind("<F3>", Sender_Suchen)
Listen_Box.bind("<F5>", Alle_Anzeigen)
Listen_Box.bind("<F7>", Service_Info)

#----------------------------------------------------------------------

StatusAnzahl.trace_add("write", Statuszeile_Anzeigen)
StatusText.trace_add("write", Statuszeile_Anzeigen)

Statuszeile_Anzeigen()
Datei_Oeffnen()

Master.protocol("WM_DELETE_WINDOW", Programm_Beenden)

Master.mainloop()

###############################################################################################################
