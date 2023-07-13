import PySimpleGUI as sg
import serial
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
import tomli_w

from os import path
config_path = path.join(path.dirname(__file__), 'config.toml')
ser = serial.Serial('/dev/ttyACM0', 9600)

# Charger fichier de config
with open(config_path, mode="rb") as fp:
    config = tomllib.load(fp)
font = (config["font"]["font"],config["font"]["size"])
listeFiltre = config["filtres"]["filtres"]

#sg.theme('DarkAmber')   # Add a touch of color

# Onglet Réseau
tabReseau = [  [sg.Text('Initialiser sur (nm)'),sg.InputText(config["reseau"]["posActuel"],key="-posActuel-"),sg.Button('Initialiser',key="initPos")],
            [sg.Text('Centrer sur (nm)'), sg.InputText(config["reseau"]["posCibleDefaut"],key="-posCible-"),sg.Button('Go',key="goToLambda")],
            [sg.Button("<"),sg.InputText(config["reseau"]["nbPas"],key="-nbPasReseau-"),sg.Button(">")] ]

# Onglet Filtres
tabFiltres = [ [sg.Text("Initialiser sur un filtre")],
                [sg.Combo(listeFiltre,default_value=config["filtres"]["filtreActuel"],key="-filtreActuel-"),sg.Button("Init",key="initFiltre")],
                [sg.Text("Choisir un filtre")],
                [sg.Listbox(listeFiltre,size=(40, 10),default_values=(config["filtres"]["filtreActuel"],),key="-filtreCible-"), sg.Button("Go",key="goToFilter")],
                [sg.Button("<",key='-filtreGauche-'),sg.InputText(config["filtres"]["nbPas"],key="-nbPasFiltre-"),sg.Button(">",key='-filtreDroite-')] ]

tabgrp = [[sg.TabGroup([[sg.Tab('Réseau', tabReseau, title_color='Red',border_width =10, background_color='Green',
                                tooltip='Centrage du réseau', element_justification= 'center'),
                    sg.Tab('Filtres', tabFiltres,title_color='Blue',background_color='Yellow')
                    ]], tab_location='centertop',
                       title_color='White', tab_background_color='Black',selected_title_color='Black',
                       selected_background_color='Gray', border_width=5)],[sg.Button('Quitter')]]  
# Creation de la fenetre
window = sg.Window('SuperSpectro', tabgrp,font=font)



#############

def goToLambda(posActuel,posCible,config):
    print(posActuel,posCible)
    rate = config["reseau"]["ratioLambdaStep"]
    steps = (int(posCible) - int(posActuel))*rate
    if steps>0:
        move="FORWARD"
    else:
        move="BACKWARD"
    cmd = move + str(steps)

    config["reseau"]["posActuel"] = int(posCible)
    with open(config_path, mode="wb") as fp:
        config = tomli_w.dump(config,fp)
    window["-posActuel-"].update(posCible)

def goToFilter(filtreActuel,filtreCible,config,window):
    
    rate = config["filtres"]["ratioFiltreStep"]
    steps = (filtreActuel - filtreCible)*rate
    if steps>0:
        move="FORWARD"
    else:
        move="BACKWARD"
    cmd = move + str(steps)

    newFiltre = listeFiltre[filtreCible]
    config["filtres"]["filtreActuel"] = newFiltre
    with open(config_path, mode="wb") as fp:
        config = tomli_w.dump(config,fp)
    window["-filtreActuel-"].update(newFiltre)

def initFiltre(config):
    config["filtres"]["filtreActuel"] = values["-filtreActuel-"]
    with open(config_path, mode="wb") as fp:
        config = tomli_w.dump(config,fp)

def initPos(config):
    config["reseau"]["posActuel"] = values["-posActuel-"]
    with open(config_path, mode="wb") as fp:
        config = tomli_w.dump(config,fp)

def deplacementFleche(config,sens,moteur):
    if moteur == "reseau":
        m = "R"
    else:
        m = "F"
    if sens == "gauche":
        s="-"
    else:
        s=""
    
    cmd = m + s + str(config[moteur]["nbPas"])
    ser.write(cmd)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Quitter': # if user closes window or clicks quit
        with open(config_path, mode="wb") as fp:
            config = tomli_w.dump(config,fp)
        break
    elif (event == "<") :
        deplacementFleche(config,"gauche","reseau")
    elif (event == "-filtreGauche-"):
        deplacementFleche(config,"gauche","filtre")
    elif (event == ">"):
        deplacementFleche(config,"droite","reseau")
    elif (event == "-filtreDroite-"):
        deplacementFleche(config,"droite","filtres")
    elif event == "initPos":
        initPos(config)
    elif event == "initFiltre":
        initFiltre(config)
    elif event == "goToLambda":
        goToLambda(values["-posActuel-"],values["-posCible-"],config)
    elif event == "goToFilter":
        #listbox renvoie une liste de sélection donc on garde que le premier
        goToFilter(listeFiltre.index(values["-filtreActuel-"]),listeFiltre.index(values["-filtreCible-"][0]),config,window)

window.close()