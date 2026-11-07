"""
DxPyGuide 1.47.79
Eine lokale Tkinter-Lernumgebung mit Übungen, Tutorial, Code-Editor und SQLite-Fortschritt.

Start:
    python python_lernstudio.py

Es werden ausschließlich Python-Standardbibliotheken verwendet.
Hinweis: Ausgeführter Übungscode läuft als separater Python-Prozess mit Zeitlimit.
"""

import ast
import builtins
import keyword
import re
import json
import math
import os
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import sqlite3

APP_NAME = "DxPyGuide"

# Programmdateien liegen neben der .py-Datei bzw. neben der gebauten EXE.
# Bei PyInstaller --onedir können logo.png und icon.ico direkt daneben liegen.
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "logo.png"
ICON_PATH = APP_DIR / "icon.ico"
ASSERT_DIAGRAM_PATH = APP_DIR / "assert_verdoppeln_grafik.png"
GUIDE_DIAGRAM_DIR = APP_DIR  # guide_<aufgaben-id>.png liegt direkt neben der Programmdatei

# Benutzerdaten gehören unter Windows in den lokalen AppData-Ordner.
# Bestehende Datenbanken aus älteren Versionen werden beim ersten Start
# automatisch kopiert, damit der bisherige Lernfortschritt erhalten bleibt.
LOCAL_APPDATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
APP_DATA_DIR = LOCAL_APPDATA / APP_NAME
DB_PATH = APP_DATA_DIR / "progress.db"
# Dauerhafter Arbeitsordner für Dateien, die Lernende in Übungen mit open() erstellen.
WORKSPACE_DIR = APP_DATA_DIR / "Arbeitsdateien"
LEGACY_DB_PATH = Path.home() / ".dxpyguide" / "progress.db"

if LEGACY_DB_PATH.exists() and not DB_PATH.exists():
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(LEGACY_DB_PATH, DB_PATH)

# Die Originaldateien des Lernenden sind inhaltlich als Ausgangsbasis übernommen.
# Die Aufgabenformulierungen und Erklärungen wurden für die Lernoberfläche ergänzt.
EXERCISES = [{'id': 'python-basics',
  'title': 'Wie ist Python-Code aufgebaut?',
  'level': 'Einstieg',
  'category': 'Erste Schritte',
  'duration': '8 Min.',
  'concepts': ['Codezeilen', 'Kommentare', 'Einrückung', 'Funktionen', 'Parameter', 'Aufruf'],
  'goal': 'Verstehe zuerst, wie Python-Code aufgebaut ist und wie die einzelnen Teile zusammenarbeiten.',
  'explanation': 'Diese Einführung erklärt den Aufbau eines Python-Programms. Du musst hier keinen eigenen Code schreiben und keine Aufgabe lösen.',
  'task': 'Dies ist eine reine Informationseinheit. Lies die Erklärungen und verfolge das Beispiel Zeile für Zeile. Danach kannst du mit der ersten praktischen Übung beginnen.',
  'hint': '',
  'solution': '',
  'starter': '',
  'checks': [],
  'information_only': True},
 {'id': 'hello',
  'title': 'Hello, Welt!',
  'level': 'Anfänger',
  'category': 'Grundlagen',
  'duration': '5 Min.',
  'source': '1hello.py',
  'concepts': ['print()', 'Textausgabe', 'Strings'],
  'goal': 'Gib deinen ersten Text in der Konsole aus.',
  'explanation': 'Mit print() gibst du Text in der Konsole aus. Der Text steht in einfachen oder '
                 'doppelten Anführungszeichen und heißt String (str).',
  'task': 'Gib mit print() genau Hallo, Welt! in der Konsole aus.',
  'hint': 'Schreibe den Text Hallo, Welt! in die Klammern von print() und setze ihn in '
          'Anführungszeichen.',
  'solution': 'print("Hallo, Welt!")',
  'starter': '# Schreibe deine erste Python-Ausgabe.\n',
  'checks': ['print', 'Hallo, Welt!'],
  'source_code': 'print("Hallo, Welt")\n'
                 '\n'
                 'print("Name:", name)\n'
                 'print("Alter:", alter)\n'
                 'print("Lichtempfindlich:", lichtempfindlich)'},
 {'id': 'person',
  'title': 'Personeninformationen',
  'level': 'Anfänger',
  'category': 'Variablen',
  'duration': '10 Min.',
  'source': '2person_info.py',
  'concepts': ['Variablen', 'input()', 'F-Strings', 'print()', 'Strings'],
  'goal': 'Speichere Name, Alter und Lieblingsspiel in Variablen und gib sie aus.',
  'explanation': 'Eine Variable speichert einen Wert. Mit input() fragst du etwas ab; die Eingabe '
                 'kommt immer als Text (str) zurück. Mit einem F-String kannst du Variablen in '
                 'einen Ausgabetext einsetzen. Zusatzwissen zur Eingabeprüfung: name.strip() '
                 'entfernt Leerzeichen am Anfang und Ende. Der Vergleich name.strip() != "" prüft, '
                 'ob danach noch Zeichen übrig sind. Mit if und else kannst du auf eine leere '
                 'Eingabe reagieren. Das ist eine optionale Prüfung und kein Pflichtteil der '
                 'Aufgabe.',
  'task': 'Erstelle die Variablen name, alter und lieblingsspiel. Frage alle drei Werte mit '
          'input() ab und gib anschließend eine Zusammenfassung mit einem F-String aus.',
  'hint': "Beispiel: name = input('Wie heißt du?') und danach print(f'Hallo {name}').",
  'solution': 'name = input("Wie heißt du? ")\n'
              'alter = input("Wie alt bist du? ")\n'
              'lieblingsspiel = input("Was ist dein Lieblingsspiel? ")\n'
              'print(f"Du heißt {name}, bist {alter} Jahre alt und spielst {lieblingsspiel}.")',
  'starter': '# Lege die Variablen selbst an.\n'
             '\n'
             '# Frage Name, Alter und Lieblingsspiel ab.\n'
             '\n'
             '# Gib eine Zusammenfassung aus.\n',
  'checks': ['input', 'name', 'alter', 'lieblingsspiel', 'print'],
  'source_code': 'Name = None\n'
                 'Alter = None\n'
                 'Lieblingsspiel = None\n'
                 '\n'
                 'Name = input("Hallo, wie ist dein Name?")\n'
                 'print(f"Willkommen {Name}")\n'
                 'Alter = input("Kannst du mir sagen wie alt du bist?")\n'
                 'print(f"Sehr schön, du bist also {Alter} Jahre alt.")\n'
                 'Lieblingsspiel = input("Was ist dein Lieblingsspiel?")\n'
                 'print(f"Dein Lieblingsspiel ist also {Lieblingsspiel}")\n'
                 'print(f"Ich fasse kurz zusammen. Dein Name ist {Name}, Du bist {Alter} und dein '
                 'Lieblingsspiel ist {Lieblingsspiel}")'},
 {'id': 'types',
  'title': 'Datentypen verstehen',
  'level': 'Anfänger',
  'category': 'Datentypen',
  'duration': '12 Min.',
  'concepts': ['str', 'int', 'float', 'bool', 'type()', 'print()'],
  'goal': 'Unterscheide die wichtigsten eingebauten Datentypen.',
  'explanation': 'Ein Datentyp beschreibt, welche Art von Wert eine Variable enthält. str = Text '
                 "(z. B. 'Hallo'), int = ganze Zahl (z. B. 25), float = Kommazahl (z. B. 4.99; "
                 'Python verwendet einen Punkt), bool = Wahrheitswert (True oder False). Mit '
                 'type(variable) fragst du den Datentyp ab. Wichtig: Die Funktion heißt exakt '
                 'type() – typ() ist kein Python-Befehl. Python unterscheidet Groß- und '
                 'Kleinschreibung.',
  'task': 'Lege vier Variablen an: eine mit Text (str), eine mit einer ganzen Zahl (int), eine mit '
          'einer Kommazahl (float) und eine mit einem Wahrheitswert (bool). Gib anschließend jede '
          'Variable und ihren Datentyp mit print() und type() aus.',
  'hint': "Beispiel: stadt = 'Berlin', anzahl = 3, preis = 2.5, aktiv = True. Für die Prüfung "
          'verwendest du print(type(stadt)). Schreibe type mit e am Ende – nicht typ.',
  'solution': "stadt = 'Berlin'\n"
              'anzahl = 3\n'
              'preis = 2.5\n'
              'aktiv = True\n'
              '\n'
              'print(stadt, type(stadt))\n'
              'print(anzahl, type(anzahl))\n'
              'print(preis, type(preis))\n'
              'print(aktiv, type(aktiv))',
  'starter': '# Lege vier Variablen mit unterschiedlichen Datentypen an.\n'
             '\n'
             '# Gib die Werte und ihre Datentypen aus.\n',
  'checks': ['type', 'True', 'float']},
 {'id': 'operators',
  'title': 'Operatoren und Logik',
  'level': 'Anfänger',
  'category': 'Operatoren',
  'duration': '12 Min.',
  'concepts': ['input()', 'int()', 'if', 'else', '>=', '<=', 'and', 'print()'],
  'goal': 'Kombiniere Bedingungen und vergleiche Werte.',
  'explanation': 'Vergleichsoperatoren liefern True oder False. and ist nur wahr, wenn beide '
                 'Bedingungen wahr sind. or ist wahr, wenn mindestens eine Bedingung wahr ist. not '
                 'kehrt einen Wahrheitswert um.',
  'task': "Frage ein Alter ab. Gib 'Zutritt' aus, wenn das Alter mindestens 18 und höchstens 99 "
          "ist, sonst 'Kein Zutritt'.",
  'hint': 'Du brauchst zwei Vergleiche: mindestens 18 und höchstens 99. Verbinde beide Ergebnisse '
          'mit and. Nutze if für den Zutritt und else für den anderen Fall.',
  'solution': "alter = int(input('Alter: '))\n"
              'if alter >= 18 and alter <= 99:\n'
              "    print('Zutritt')\n"
              'else:\n'
              "    print('Kein Zutritt')",
  'starter': '# Frage das Alter ab.\n'
             '\n'
             '# Prüfe die Bedingungen und gib das passende Ergebnis aus.\n',
  'checks': ['and', 'if', 'else', '<=', '>=']},
 {'id': 'age',
  'title': 'Altersabfrage',
  'level': 'Anfänger',
  'category': 'Bedingungen',
  'duration': '10 Min.',
  'source': '4alterabfrage.py',
  'concepts': ['input()', 'int()', 'if', 'elif', 'else', '>=', 'print()'],
  'goal': 'Lerne, abhängig von einer Eingabe unterschiedliche Codepfade auszuführen.',
  'explanation': 'if prüft eine Bedingung. elif prüft eine weitere Bedingung, wenn die vorherige '
                 'nicht zutraf. else wird ausgeführt, wenn keine vorherige Bedingung zutrifft. '
                 'input() liefert Text; int() wandelt eine gültige Zahl in eine Ganzzahl um. Die '
                 'Reihenfolge ist wichtig: Prüfe die höchste Altersgrenze zuerst.',
  'task': "Frage das Alter ab. Ab 65 soll 'Rentneralter', ab 18 'volljährig', ansonsten "
          "'minderjährig' ausgegeben werden.",
  'hint': 'Nutze alter = int(input(...)). Prüfe zuerst alter >= 65, danach alter >= 18.',
  'solution': 'alter = int(input("Wie alt bist du? "))\n'
              'if alter >= 65:\n'
              '    print("Du bist im Rentenalter")\n'
              'elif alter >= 18:\n'
              '    print("Du bist volljährig")\n'
              'else:\n'
              '    print("Du bist minderjährig")',
  'starter': '# Frage das Alter ab.\n'
             '\n'
             '# Entscheide mit if, elif und else, welcher Text ausgegeben wird.\n',
  'checks': ['int', 'if', 'elif', 'else'],
  'source_code': "eingabe = 'cancel'\n"
                 'while True:\n'
                 "    eingabe = input('Bitte gebe dein Alter an oder beende mit cancel.')\n"
                 "    if eingabe.lower() == 'cancel':\n"
                 "        print('Programm wird beendet.')\n"
                 '        exit()\n'
                 '    eingabe = int(eingabe)\n'
                 '    if eingabe >= 65:\n'
                 "        print('Du bist im Rentenalter')\n"
                 '    elif eingabe >= 18:\n'
                 "        print('Du bist volljährig')\n"
                 '    else:\n'
                 "        print('Du bist minderjährig')"},
 {'id': 'login',
  'title': 'Anmeldung und Login',
  'level': 'Anfänger',
  'category': 'Bedingungen',
  'duration': '15 Min.',
  'source': '6anmeldung.py',
  'concepts': ['Variablen', 'input()', 'if', 'else', '==', 'and', 'print()'],
  'goal': 'Baue einen einfachen Ablauf mit Registrierung und anschließendem Login nach.',
  'explanation': 'Du kannst Eingaben in Variablen speichern und später vergleichen. == prüft '
                 'Gleichheit. In deinem Beispiel werden Benutzer-ID und Passwort während der '
                 'Programmlaufzeit gespeichert. Das ist eine Übung, aber keine sichere echte '
                 'Anmeldung: Passwörter sollten in realen Anwendungen niemals im Klartext '
                 'gespeichert werden.',
  'task': "Lege beispielhaft benutzername = 'test' und passwort = 'python' fest. Frage beide Werte "
          "ab und gib bei Übereinstimmung 'Erfolgreich angemeldet' aus, sonst 'Anmeldedaten "
          "falsch'.",
  'hint': 'Vergleiche beide Eingaben mit ==. Verbinde die Bedingungen mit and.',
  'solution': 'benutzername = "test"\n'
              'passwort = "python"\n'
              'eingabe_name = input("Benutzername: ")\n'
              'eingabe_passwort = input("Passwort: ")\n'
              'if eingabe_name == benutzername and eingabe_passwort == passwort:\n'
              '    print("Erfolgreich angemeldet")\n'
              'else:\n'
              '    print("Anmeldedaten falsch")',
  'starter': '# Lege Beispiel-Zugangsdaten fest.\n'
             '\n'
             '# Frage Benutzername und Passwort ab.\n'
             '\n'
             '# Vergleiche beide Eingaben und gib das Ergebnis aus.\n',
  'checks': ['if', 'else', '==', 'input'],
  'source_code': 'benutzerid = None\n'
                 'benutzerpw = None\n'
                 '\n'
                 'while True:\n'
                 "    eingabe = input('Wähle Anmeldung 1 oder Login 2: ')\n"
                 "    if eingabe == '1':\n"
                 "        benutzerid = input('E-Mail oder Benutzername: ')\n"
                 "        benutzerpw = input('Erstelle dein Passwort: ')\n"
                 "        print('Account wurde angemeldet.')\n"
                 "    elif eingabe == '2':\n"
                 "        loginid = input('Anmelde ID: ')\n"
                 '        if loginid == benutzerid:\n'
                 "            loginpw = input('Passwort: ')\n"
                 '            if loginpw == benutzerpw:\n'
                 "                print('Erfolgreich angemeldet')\n"
                 '                break\n'
                 '            else:\n'
                 "                print('Falsches Passwort.')\n"
                 '        else:\n'
                 "            print('Falsche Anmelde ID.')\n"
                 '    else:\n'
                 "        print('Ungültige Eingabe.')"},
 {'id': 'loops',
  'title': 'Zählschleifen mit for und range',
  'level': 'Anfänger',
  'category': 'Schleifen',
  'duration': '10 Min.',
  'source': '5zählen.py',
  'concepts': ['for', 'range()', 'Schleifenvariable', 'print()'],
  'goal': 'Wiederhole einen Codeblock eine festgelegte Anzahl von Malen.',
  'explanation': 'Eine for-Schleife durchläuft eine Folge von Werten. range(1, 11) erzeugt die '
                 'Zahlen 1 bis 10; die obere Grenze 11 gehört nicht mehr dazu. Der Schleifenblock '
                 'ist eingerückt.',
  'task': 'Schreibe eine for-Schleife, die die Zahlen 1 bis 10 einzeln ausgibt. Gib danach '
          "'Fertig!' aus.",
  'hint': 'Verwende for zahl in range(1, 11): und darunter eingerückt print(zahl).',
  'solution': 'for zahl in range(1, 11):\n    print(zahl)\nprint("Fertig!")',
  'starter': '# Gib die Zahlen 1 bis 10 mit einer Schleife aus.\n\n# Gib danach "Fertig!" aus.\n',
  'checks': ['for', 'range', 'print'],
  'source_code': 'import time\n'
                 '\n'
                 'for timer in range(1, 11):\n'
                 '    print(timer)\n'
                 '    time.sleep(1)\n'
                 "print('Fertig!')\n"
                 '\n'
                 "namelist = ['Chris', 'Elena', 'Leonie']\n"
                 'for name in namelist:\n'
                 "    print(f'Hallo {name} schön dich kennenzulernen')"},
 {'id': 'while',
  'title': 'While-Schleifen',
  'level': 'Anfänger',
  'category': 'Schleifen',
  'duration': '12 Min.',
  'concepts': ['while', 'Bedingung', 'break', '+=', 'print()'],
  'goal': 'Wiederhole einen Ablauf, solange eine Bedingung erfüllt ist.',
  'explanation': 'while wiederholt den eingerückten Block, solange die Bedingung True ist. Achte '
                 'darauf, dass sich die Bedingung irgendwann ändern kann, sonst entsteht eine '
                 'Endlosschleife. break beendet eine Schleife sofort.',
  'task': 'Zähle mit einer while-Schleife von 1 bis 5 und gib jede Zahl aus.',
  'hint': 'Setze zahl = 1 vor der Schleife. Erhöhe in der Schleife mit zahl += 1.',
  'solution': 'zahl = 1\nwhile zahl <= 5:\n    print(zahl)\n    zahl += 1',
  'starter': '# Lege einen Startwert fest.\n\n# Zähle mit while bis 5 und gib jede Zahl aus.\n',
  'checks': ['while', 'print', '+=']},
 {'id': 'functions',
  'title': 'Eigene Funktionen',
  'level': 'Anfänger',
  'category': 'Funktionen',
  'duration': '15 Min.',
  'source': '7funktion.py',
  'concepts': ['def', 'Parameter', 'Aufruf', 'print()', 'F-Strings'],
  'goal': 'Lagere wiederverwendbare Abläufe in Funktionen aus.',
  'explanation': 'Mit def definierst du eine Funktion. Ein Parameter ist ein Platzhalter für einen '
                 'Wert, den du beim Aufruf übergeben kannst. Eine Funktion wird erst ausgeführt, '
                 'wenn sie aufgerufen wird. return gibt einen Wert an die aufrufende Stelle '
                 'zurück.',
  'task': "Schreibe eine Funktion begruessung(name), die 'Hallo NAME!' ausgibt. Rufe sie "
          'anschließend mit deinem Namen auf.',
  'hint': 'Beginne mit def begruessung(name):. Der Funktionskörper muss eingerückt sein.',
  'solution': 'def begruessung(name):\n    print(f"Hallo {name}!")\n\nbegruessung("Chris")',
  'starter': '# Definiere die Funktion begruessung(name).\n'
             '\n'
             '# Rufe die Funktion mit einem Namen auf.\n',
  'checks': ['def', 'begruessung', 'print'],
  'source_code': 'def altersabfrage(eingabe):\n'
                 '    eingabe = int(eingabe)\n'
                 '    if eingabe >= 65:\n'
                 "        print('Du bist im Rentenalter')\n"
                 '    elif eingabe >= 18:\n'
                 "        print('Du bist volljährig')\n"
                 '    else:\n'
                 "        print('Du bist minderjährig')\n"
                 '\n'
                 "altersabfrage('25')"},
 {'id': 'lists',
  'title': 'Listen durchlaufen',
  'level': 'Anfänger',
  'category': 'Listen',
  'duration': '10 Min.',
  'source': '8listen.py',
  'concepts': ['Listen', 'for', 'Schleifenvariable', 'print()'],
  'goal': 'Arbeite mit mehreren Werten in einer Liste.',
  'explanation': 'Eine Liste speichert mehrere Werte in einer geordneten Sammlung. Du erstellst '
                 'sie mit eckigen Klammern. Mit for name in namen gehst du Element für Element '
                 'durch die Liste.',
  'task': 'Erstelle eine Liste mit drei Namen und begrüße jeden Namen mit einer for-Schleife.',
  'hint': "namen = ['Anna', 'Ben', 'Mia'] und danach for name in namen:.",
  'solution': 'namen = ["Anna", "Ben", "Mia"]\nfor name in namen:\n    print(f"Hallo {name}!")',
  'starter': '# Erstelle eine Liste mit drei Namen.\n'
             '\n'
             '# Begrüße jeden Namen mit einer for-Schleife.\n',
  'checks': ['[', 'for', 'in', 'print'],
  'source_code': "namelist = ['Chris', 'Elena', 'Leonie', 'Max', 'Tom']\n"
                 '\n'
                 'def begruesse_namen(namelist):\n'
                 '    for namen in namelist:\n'
                 "        if namen == 'Max':\n"
                 "            print('Hallo Max, du bist besonders!')\n"
                 "        elif namen == 'Leonie':\n"
                 "            print('Hallo Leonie, du bist toll!')\n"
                 '        else:\n'
                 "            print(f'Hallo {namen}, schön dich kennenzulernen')\n"
                 "    print('Alle Personen wurden begrüßt.')\n"
                 '\n'
                 'begruesse_namen(namelist)'},
 {'id': 'list-input',
  'title': 'Eingaben in einer Liste sammeln',
  'level': 'Anfänger',
  'category': 'Listen',
  'duration': '10 Min.',
  'source': '0Noitzen.py',
  'concepts': ['leere Listen', 'for', 'range()', 'input()', 'append()', 'print()'],
  'goal': 'Sammle mehrere Benutzereingaben in einer Liste.',
  'explanation': 'Du kannst eine leere Liste mit namen = [] erstellen. Eine for-Schleife '
                 'wiederholt die Eingabe dreimal. append() fügt jeden eingegebenen Namen am Ende '
                 'der Liste hinzu. Die Liste enthält danach alle drei Eingaben.',
  'task': 'Erstelle eine leere Liste namens namen. Frage in einer Schleife drei Namen ab, '
          'speichere jeden mit append() und gib anschließend die gesamte Liste aus.',
  'hint': 'Nutze for nummer in range(3):, input() und namen.append(name).',
  'solution': 'namen = []\n'
              'for nummer in range(3):\n'
              '    name = input(f"Trage Namen ein ({nummer + 1}): ")\n'
              '    namen.append(name)\n'
              'print(namen)',
  'starter': '# Erstelle eine leere Liste.\n'
             '\n'
             '# Frage in einer Schleife drei Namen ab und speichere sie.\n'
             '\n'
             '# Gib die Liste aus.\n',
  'checks': ['[]', 'for', 'range', 'append', 'print'],
  'source_code': 'namen = []\n'
                 '\n'
                 'for name in range(3):\n'
                 "    name = input(f'Trage drei Namen ein: {name+1}')\n"
                 '    namen.append(name)\n'
                 "    print(f'{namen}')"},
 {'id': 'append',
  'title': 'Werte in Listen speichern',
  'level': 'Anfänger',
  'category': 'Listen',
  'duration': '10 Min.',
  'source': '9in_liste_speichern.py',
  'concepts': ['def',
               'Parameter',
               'Aufruf',
               'leere Listen',
               'for',
               'range()',
               'input()',
               'append()',
               'return',
               'print()'],
  'goal': 'Füge Werte während der Programmausführung zu einer Liste hinzu.',
  'explanation': 'append() hängt ein Element am Ende einer Liste an. Eine leere Liste erstellst du '
                 'mit []. return kann die fertige Liste aus einer Funktion zurückgeben.',
  'task': 'Erstelle eine Funktion namens namen_sammeln(). Sie soll drei Namen abfragen, jeden mit '
          'append() in einer Liste speichern und die Liste mit return zurückgeben. Gib das '
          'Ergebnis anschließend aus.',
  'hint': 'Erstelle innerhalb der Funktion namen = []. Nutze for nummer in range(3): und '
          'namen.append(input(...)).',
  'solution': 'def namen_sammeln():\n'
              '    namen = []\n'
              '    for nummer in range(3):\n'
              '        name = input(f"Name {nummer + 1}: ")\n'
              '        namen.append(name)\n'
              '    return namen\n'
              '\n'
              'ergebnis = namen_sammeln()\n'
              'print(ergebnis)',
  'starter': '# Definiere die Funktion namen_sammeln().\n'
             '\n'
             '# Sammle drei Namen in einer Liste und gib die Liste zurück.\n'
             '\n'
             '# Rufe die Funktion auf und gib das Ergebnis aus.\n',
  'checks': ['def', 'append', 'return', 'range'],
  'source_code': 'def namenslistesichern():\n'
                 '    namen = []\n'
                 '    for nummer in range(3):\n'
                 "        name = input(f'Trage Namen ein: {nummer + 1}: ')\n"
                 '        namen.append(name)\n'
                 '    return namen\n'
                 '\n'
                 'nametransfer = namenslistesichern()\n'
                 'print(nametransfer)'},
 {'id': 'list-validation',
  'title': 'Eingaben bereinigen und abgleichen',
  'level': 'Anfänger',
  'category': 'Listen',
  'duration': '12 Min.',
  'concepts': ['Listen', 'in', 'strip()', 'lower()', 'if'],
  'goal': 'Prüfe, ob eine Benutzereingabe zu einem erlaubten Eintrag in einer Liste passt.',
  'explanation': 'Mit in prüfst du, ob ein Wert in einer Liste vorkommt. strip() entfernt '
                 'Leerzeichen am Anfang und Ende eines Strings. lower() wandelt Buchstaben in '
                 'Kleinbuchstaben um. Wenn du die bereinigte Eingabe einer Variable zuweist, '
                 'kannst du sie anschließend sowohl prüfen als auch weiterverwenden.',
  'task': "Erstelle eine Liste mit den erlaubten Begriffen 'name', 'alter' und 'spiel'. Frage den "
          'Benutzer, welchen Wert er abrufen möchte. Bereinige die Eingabe mit strip() und '
          'lower(). Prüfe mit in, ob die Eingabe in deiner Liste enthalten ist. Gib bei einem '
          "Treffer 'Eingabe gültig' aus, sonst 'Ungültige Eingabe'.",
  'hint': "Erstelle zum Beispiel erlaubte_eingaben = ['name', 'alter', 'spiel']. Speichere danach "
          'eingabe.strip().lower() wieder in eingabe und prüfe: if eingabe in erlaubte_eingaben:',
  'solution': "erlaubte_eingaben = ['name', 'alter', 'spiel']\n"
              "eingabe = input('Was möchtest du abrufen? ')\n"
              'eingabe = eingabe.strip().lower()\n'
              '\n'
              'if eingabe in erlaubte_eingaben:\n'
              "    print('Eingabe gültig')\n"
              'else:\n'
              "    print('Ungültige Eingabe')",
  'starter': '# Erstelle eine Liste mit erlaubten Begriffen.\n'
             '\n'
             '# Frage einen Begriff ab und bereinige die Eingabe.\n'
             '\n'
             '# Prüfe mit in, ob die Eingabe in der Liste enthalten ist.\n',
  'checks': ['in', 'strip', 'lower', 'if', 'else']},
 {'id': 'dict',
  'title': 'Dictionaries',
  'level': 'Fortgeschrittene Grundlagen',
  'category': 'Datenstrukturen',
  'duration': '15 Min.',
  'concepts': ['dict', 'Schlüssel', 'Werte', 'get()', 'print()'],
  'goal': 'Speichere zusammengehörige Informationen als Schlüssel-Wert-Paare.',
  'explanation': 'Ein Dictionary speichert Werte unter eindeutigen Schlüsseln. Du erstellst es mit '
                 "geschweiften Klammern. Zugriff erfolgt zum Beispiel über person['name']; get() "
                 'kann einen Standardwert liefern, falls ein Schlüssel fehlt.',
  'task': 'Erstelle ein Dictionary person mit name, alter und spiel. Gib den Namen und das '
          'Lieblingsspiel aus.',
  'hint': "person = {'name': 'Chris', 'alter': 30, 'spiel': 'Aion 2'}",
  'solution': "person = {'name': 'Chris', 'alter': 30, 'spiel': 'Aion 2'}\n"
              "print(person['name'])\n"
              "print(person['spiel'])",
  'starter': '# Erstelle das Dictionary person mit drei Angaben.\n'
             '\n'
             '# Gib den Namen und das Lieblingsspiel aus.\n',
  'checks': ['{', 'name', 'print']},
 {'id': 'tuples',
  'title': 'Tupel und Sets',
  'level': 'Fortgeschrittene Grundlagen',
  'category': 'Datenstrukturen',
  'duration': '15 Min.',
  'concepts': ['tuple', 'set', 'Unveränderlichkeit', 'Eindeutigkeit', 'print()', 'len()'],
  'goal': 'Verstehe, wann eine feste Sammlung (Tupel) und wann eine Sammlung eindeutiger '
          'Einzelwerte (Set) sinnvoll ist.',
  'explanation': 'Ein Tupel speichert mehrere Werte in einer festen Reihenfolge und kann nach dem '
                 'Erstellen nicht verändert werden – ähnlich wie eine Liste, nur unveränderlich. '
                 'Ein Set speichert einzelne Werte ohne Duplikate. Es nutzt geschweifte Klammern '
                 'wie ein Dictionary, enthält aber keine Schlüssel-Wert-Paare. Ein Dictionary '
                 "verbindet dagegen einen Schlüssel mit einem Wert, zum Beispiel 'Name': 'Chris'. "
                 'len() steht für length (Länge) und zählt die Elemente einer Sammlung. Bei einem '
                 'Set werden doppelte Werte nur einmal gezählt.',
  'task': 'Erstelle ein Tupel mit drei Farben. Erstelle danach ein Set aus den Zahlen 1, 2, 2, 3. '
          'Gib beide Sammlungen aus und erkläre, warum das Set nur drei unterschiedliche Zahlen '
          'enthält.',
  'hint': "Tupel: farben = ('Rot', 'Blau', 'Grün'). Set: zahlen = {1, 2, 2, 3}. Achte auf den "
          'Unterschied: Ein Set enthält einzelne Werte; bei einem Dictionary trennt ein '
          'Doppelpunkt Schlüssel und Wert.',
  'solution': "farben = ('Rot', 'Blau', 'Grün')\n"
              'zahlen = {1, 2, 2, 3}\n'
              '\n'
              'print(farben)\n'
              'print(zahlen)\n'
              'print(len(zahlen))',
  'starter': '# Erstelle ein Tupel mit drei Farben.\n'
             '\n'
             '# Erstelle ein Set aus den Zahlen 1, 2, 2, 3.\n'
             '\n'
             '# Gib beide Sammlungen und die Anzahl der Set-Elemente aus.\n',
  'checks': ['(', '{', 'print', 'len']},
 {'id': 'comprehension',
  'title': 'List Comprehensions',
  'level': 'Fortgeschritten',
  'category': 'Fortgeschrittene Listen',
  'duration': '15 Min.',
  'concepts': ['List Comprehension', 'for', 'range()', 'print()', '**'],
  'goal': 'Erzeuge Listen kompakt aus bestehenden Folgen.',
  'explanation': 'Eine List Comprehension erstellt eine neue Liste. range() liefert die '
                 'Zahlenfolge von 1 bis 10. ** 2 bedeutet, dass jede Zahl zur zweiten Potenz '
                 'erhoben wird: Sie wird mit sich selbst multipliziert.',
  'task': 'Erzeuge mithilfe einer List Comprehension und range() eine Liste mit den Quadraten der '
          'Zahlen von 1 bis 10. Verwende ** 2, um jede Zahl zur zweiten Potenz zu erheben (zu '
          'quadrieren).',
  'hint': 'range(start, ende) enthält den Startwert, aber nicht die Endgrenze. Mit zahl ** 2 '
          'erhebst du jede Zahl zur zweiten Potenz. Das bedeutet: zahl wird mit sich selbst '
          'multipliziert.',
  'solution': 'quadrate = [zahl ** 2 for zahl in range(1, 11)]\nprint(quadrate)',
  'starter': '# Erzeuge eine Liste mit den Quadraten von 1 bis 10.\n',
  'checks': ['[', 'for', 'range', '**']},
 {'id': 'exceptions',
  'title': 'Fehler behandeln',
  'level': 'Fortgeschritten',
  'category': 'Fehlerbehandlung',
  'duration': '15 Min.',
  'concepts': ['try', 'except', 'ValueError', 'input()', 'int()', 'print()'],
  'goal': 'Fange erwartbare Eingabefehler ab, damit dein Programm nicht unerwartet abbricht.',
  'explanation': 'Code im try-Block wird ausgeführt. Tritt dort ein passender Fehler auf, wird der '
                 'zugehörige except-Block ausgeführt. ValueError entsteht beispielsweise, wenn '
                 'int() einen Text erhält, der keine gültige Ganzzahl ist.',
  'task': 'Frage eine Zahl ab und wandle sie in int um. Fange ValueError ab und gib bei ungültiger '
          "Eingabe 'Bitte eine gültige Zahl eingeben.' aus.",
  'hint': 'Setze int(input(...)) in einen try-Block und ergänze except ValueError:.',
  'solution': 'try:\n'
              "    zahl = int(input('Gib eine Zahl ein: '))\n"
              "    print(f'Deine Zahl ist {zahl}')\n"
              'except ValueError:\n'
              "    print('Bitte eine gültige Zahl eingeben.')",
  'starter': '# Schreibe eine try/except-Behandlung für eine Zahleneingabe.\n',
  'checks': ['try', 'except', 'ValueError']},
 {'id': 'files',
  'title': 'Dateien lesen und schreiben',
  'level': 'Fortgeschritten',
  'category': 'Dateien',
  'duration': '20 Min.',
  'concepts': ['open()', 'with', 'read()', 'write()', 'print()'],
  'goal': 'Speichere Daten dauerhaft in einer Textdatei.',
  'explanation': "Mit open() öffnest du eine Datei. Ist sie noch nicht vorhanden, kann Python sie je nach Modus erstellen. 'w' steht für write (schreiben) und überschreibt vorhandenen Inhalt, 'r' für read (lesen) und 'a' für append (anhängen). 'as datei' gibt dem geöffneten Dateiobjekt den Variablennamen datei. Mit datei.write() schreibst du Text hinein; datei.read() liest ihn aus. with schließt die Datei automatisch, sobald der eingerückte Block endet. encoding='utf-8' legt fest, wie Textzeichen gespeichert und gelesen werden, und unterstützt unter anderem Umlaute.",
  'task': "Schreibe den Text 'Ich lerne Python!' in eine Datei namens notiz.txt und lies ihn "
          'danach wieder aus.',
  'hint': "Nutze with open('notiz.txt', 'w', encoding='utf-8') as datei: und danach einen zweiten "
          "with-Block mit 'r'.",
  'solution': "with open('notiz.txt', 'w', encoding='utf-8') as datei:\n"
              "    datei.write('Ich lerne Python!')\n"
              '\n'
              "with open('notiz.txt', 'r', encoding='utf-8') as datei:\n"
              '    inhalt = datei.read()\n'
              '    print(inhalt)',
  'starter': '# Schreibe den gewünschten Text in notiz.txt.\n'
             '\n'
             '# Lies den Dateiinhalt anschließend wieder aus.\n',
  'checks': ['open', 'with', 'write', 'read']},
 {'id': 'file_encryption',
  'title': 'Dateien verschlüsseln und entschlüsseln',
  'level': 'Fortgeschritten',
  'category': 'Dateien',
  'duration': '25 Min.',
  'concepts': ['Fernet', 'generate_key()', 'Schlüssel dauerhaft speichern', 'encrypt()', 'decrypt()', 'encode()', 'decode()'],
  'goal': 'Verstehe den Unterschied zwischen lesbarem Text und verschlüsselten Dateidaten.',
  'explanation': 'Für echte Verschlüsselung verwenden wir Fernet aus dem Zusatzpaket cryptography. Der Text wird mit UTF-8 in Bytes umgewandelt und verschlüsselt. Die verschlüsselten Bytes werden gespeichert und später mit demselben Schlüssel entschlüsselt. Wichtig: Wer den Schlüssel verliert, kann die Daten nicht mehr entschlüsseln. Den Schlüssel darfst du nicht einfach neben der verschlüsselten Datei ungeschützt speichern. Base64 ist übrigens nur eine Kodierung und keine Verschlüsselung.',
  'task': 'Vorbereitung: Klicke auf „Ausführen“ und gib den Befehl pip install cryptography unten in die DxPyGuide-Konsole ein. Danach bearbeitest du die eigentliche Aufgabe: Erzeuge einen Fernet-Schlüssel, verschlüssele den Text „Geheime Nachricht“, speichere die verschlüsselten Bytes in geheim.bin, lies sie wieder ein und entschlüssele den Inhalt. Gib den ursprünglichen Text aus.',
  'hint': 'Importiere Fernet aus cryptography.fernet. Nutze Fernet.generate_key(), text.encode("utf-8"), encrypt(), decrypt() und anschließend .decode("utf-8"). Schreibe Bytes mit „wb“ und lies sie mit „rb“.',
  'solution': 'from cryptography.fernet import Fernet\n\nkey = Fernet.generate_key()\nfernet = Fernet(key)\n\ntext = "Geheime Nachricht"\nverschluesselt = fernet.encrypt(text.encode("utf-8"))\n\nwith open("geheim.bin", "wb") as datei:\n    datei.write(verschluesselt)\n\nwith open("geheim.bin", "rb") as datei:\n    gespeicherte_daten = datei.read()\n\nlesbar = fernet.decrypt(gespeicherte_daten).decode("utf-8")\nprint(lesbar)',
  'starter': '# Die Konsolen-Vorbereitung wird zuerst über „Ausführen“ gestartet.\n# Danach: Erzeuge einen Fernet-Schlüssel und verschlüssele den Text.\n# Speichere die verschlüsselten Bytes, lies sie wieder ein und entschlüssele sie.\n',
  'checks': ['Fernet', 'encrypt', 'decrypt', 'encode', 'decode']},
 {'id': 'modules',
  'title': 'Module importieren',
  'level': 'Fortgeschritten',
  'category': 'Module',
  'duration': '12 Min.',
  'concepts': ['import', 'Module', 'random', 'print()'],
  'goal': 'Nutze bereits vorhandene Funktionen aus Python-Modulen.',
  'explanation': 'Module bündeln fertigen Python-Code. Mit import lädst du ein Modul. Danach '
                 'kannst du dessen Funktionen über den Modulnamen aufrufen, beispielsweise '
                 'random.randint(1, 6).',
  'task': 'Importiere random und simuliere einen Würfelwurf mit einer Zufallszahl von 1 bis 6.',
  'hint': 'random.randint(a, b) liefert eine zufällige Ganzzahl einschließlich beider Grenzen.',
  'solution': 'import random\n'
              'wurf = random.randint(1, 6)\n'
              "print(f'Du hast eine {wurf} gewürfelt.')",
  'starter': '# Importiere das benötigte Modul.\n\n# Erzeuge einen Würfelwurf und gib ihn aus.\n',
  'checks': ['import random', 'randint', 'print']},
 {'id': 'oop',
  'title': 'Klassen und Objekte',
  'level': 'Fortgeschritten',
  'category': 'Objektorientierung',
  'duration': '20 Min.',
  'concepts': ['class', '__init__', 'self', 'Objekte', 'print()'],
  'goal': 'Lerne, Daten und Funktionen in eigenen Objekttypen zusammenzufassen.',
  'explanation': 'Eine Klasse ist ein Bauplan für Objekte. __init__() wird beim Erstellen automatisch aufgerufen. self steht für das gerade erstellte Objekt. Parameter erhalten übergebene Werte; mit self.name = wert1 werden diese als Eigenschaften im Objekt gespeichert.',
  'task': 'Erstelle eine Klasse Charakter mit __init__(self, wert1, wert2). Speichere wert1 mit self.name und wert2 mit self.alter. Erzeuge spieler1 = Charakter("Chris", 37) und gib Name und Alter aus.',
  'hint': 'Nutze class Charakter: und def __init__(self, wert1, wert2):. Speichere die Werte mit self.name = wert1 und self.alter = wert2.',
  'solution': 'class Charakter:\n'
              '    def __init__(self, wert1, wert2):\n'
              '        self.name = wert1\n'
              '        self.alter = wert2\n'
              '\n'
              'spieler1 = Charakter("Chris", 37)\n'
              'print(spieler1.name)\n'
              'print(spieler1.alter)',
  'starter': '# Definiere die Klasse Charakter mit __init__(self, wert1, wert2).\n'
             '# Speichere die Werte als self.name und self.alter.\n'
             '\n'
             '# Erzeuge spieler1 = Charakter("Chris", 37).\n'
             '# Gib Name und Alter aus.\n',
  'checks': ['class Charakter', '__init__', 'self.name', 'self.alter', 'spieler1']},
 {'id': 'testing',
  'title': 'Debugging und assert',
  'level': 'Fortgeschritten',
  'category': 'Qualität',
  'duration': '15 Min.',
  'concepts': ['def',
               'Parameter',
               'return',
               'Aufruf',
               'assert',
               'Traceback',
               'Debugging',
               'print()'],
  'goal': 'Prüfe Annahmen im Code und lerne, Fehler systematisch einzugrenzen.',
  'explanation': 'assert überprüft eine Bedingung. Ist sie falsch, wird AssertionError ausgelöst. '
                 'Fehlermeldungen (Tracebacks) zeigen den Fehlertyp und die Stelle, an der der '
                 'Fehler auftrat. Lies den letzten Teil des Tracebacks besonders aufmerksam.',
  'task': 'Schreibe eine Funktion verdoppeln(zahl), die zahl * 2 zurückgibt. Prüfe mit assert, '
          'dass verdoppeln(4) den Wert 8 liefert.',
  'hint': 'Nutze return zahl * 2 und danach assert verdoppeln(4) == 8.',
  'solution': 'def verdoppeln(zahl):\n'
              '    return zahl * 2\n'
              '\n'
              'assert verdoppeln(4) == 8\n'
              "print('Test bestanden!')",
  'starter': '# Definiere die Funktion verdoppeln(zahl).\n\n# Prüfe das Ergebnis mit assert.\n',
  'checks': ['def', 'return', 'assert']},
{'id': 'tkinter-login',
 'title': 'Abschlussprojekt: Anmeldefenster',
 'level': 'Abschlussprojekt',
 'category': 'Grafische Oberfläche',
 'duration': '30–45 Min.',
 'concepts': ['tkinter',
              'Tk()',
              'Label',
              'Entry',
              'Button',
              'command',
              'get()',
              'if',
              'and',
              'pack()'],
 'goal': 'Erstelle dein erstes eigenes Fensterprogramm mit einer einfachen Anmeldung.',
 'explanation': 'Du baust mit tkinter ein Fenster. Zuerst ist nur der Button „Anmelden“ sichtbar. '
                'Nach einem Klick erscheinen Eingabefelder für Benutzername und Passwort sowie ein '
                'Bestätigungsbutton. Stimmen Nutzername und Passwort mit den festgelegten Zugangsdaten '
                'überein, erscheint unter den Eingabefeldern die Meldung „Du bist eingeloggt.“ '
                'Der Nutzername lautet admin, das Passwort lautet passwort.',
 'task': 'Schreibe ein vollständiges Programm mit tkinter. Beim Start soll ein Fenster mit dem '
         'Button „Anmelden“ erscheinen. Ein Klick darauf blendet die Felder „Nutzername“ und '
         '„Passwort“ ein. Mit einem weiteren Button bestätigst du die Eingaben. Nur wenn der '
         'Nutzername exakt admin und das Passwort exakt passwort lautet, soll unter den '
         'Eingabefeldern „Du bist eingeloggt“ erscheinen. Bei falschen Angaben soll dort '
         '„Benutzername oder Passwort falsch“ stehen.',
 'hint': 'Importiere tkinter als tk. Erstelle mit tk.Tk() das Hauptfenster. Lege einen Frame für '
         'die Anmeldung an und blende ihn mit pack() zunächst noch nicht ein. Der erste Button '
         'ruft über command= eine Funktion auf, die den Frame mit pack() sichtbar macht. Verwende '
         'tk.Entry() für die Eingaben; beim Passwortfeld kannst du show="*" setzen. Eine zweite '
         'Funktion liest beide Felder mit get() aus und prüft sie mit if und and.',
 'solution': 'import tkinter as tk\n'
             '\n'
             'fenster = tk.Tk()\n'
             'fenster.title("Anmeldung")\n'
             'fenster.geometry("320x260")\n'
             '\n'
             'login_bereich = tk.Frame(fenster)\n'
             'nutzername_feld = tk.Entry(login_bereich)\n'
             'passwort_feld = tk.Entry(login_bereich, show="*")\n'
             'status = tk.Label(login_bereich, text="")\n'
             '\n'
             'def anmeldung_pruefen():\n'
             '    if nutzername_feld.get() == "admin" and passwort_feld.get() == "passwort":\n'
             '        status.config(text="Du bist eingeloggt")\n'
             '    else:\n'
             '        status.config(text="Benutzername oder Passwort falsch")\n'
             '\n'
             'def anmeldung_anzeigen():\n'
             '    login_bereich.pack(pady=10)\n'
             '    tk.Label(login_bereich, text="Nutzername").pack()\n'
             '    nutzername_feld.pack()\n'
             '    tk.Label(login_bereich, text="Passwort").pack()\n'
             '    passwort_feld.pack()\n'
             '    tk.Button(login_bereich, text="Einloggen", '
             'command=anmeldung_pruefen).pack(pady=8)\n'
             '    status.pack()\n'
             '\n'
             'tk.Button(fenster, text="Anmelden", command=anmeldung_anzeigen).pack(pady=20)\n'
             'fenster.mainloop()',
 'starter': '# Importiere tkinter als tk.\n'
            '\n'
            '# Erstelle das Hauptfenster und gib ihm einen Titel.\n'
            '\n'
            '# Lege einen Bereich für die Anmeldefelder an.\n'
            '\n'
            '# Erstelle eine Funktion, die die Eingabefelder sichtbar macht.\n'
            '\n'
            '# Erstelle eine Funktion, die Nutzername und Passwort prüft.\n'
            '# Nutzername: "admin"  |  Passwort: "passwort"\n'
            '\n'
            '# Erstelle die Eingabefelder, Beschriftungen und Buttons.\n'
            '# Starte am Ende die Ereignisschleife mit mainloop().\n',
 'checks': ['import tkinter',
            'tk.Tk(',
            'tk.Entry(',
            'tk.Button(',
            'command=',
            '.get()',
            'if ',
            'and',
            'mainloop()']} ]



# Zusätzliche didaktische Erläuterungen: Begriff, Ablauf, typische Fehler und Merksätze.
EXPLANATION_DETAILS = {'hello': 'print() zeigt den Wert aus den Klammern in der Konsole an. Anführungszeichen markieren '
          'Text (String). Jeder print()-Aufruf beginnt standardmäßig nach der Ausgabe eine neue '
          'Zeile.\n'
          '\n'
          'Mit \n kannst du einen Zeilenumbruch innerhalb eines Strings festlegen. Damit der '
          'Beispielcode nicht zu lang nach rechts läuft, kannst du den Text auf zwei '
          'Quellcodezeilen verteilen:\n'
          '\n'
          'print("Erste Zeile\n"\n'
          '      "Zweite Zeile")\n'
          '\n'
          'Die beiden Textstücke stehen direkt nebeneinander in den Klammern und werden von Python '
          'zu einem String verbunden. Das \n im ersten Textstück sorgt dafür, dass Zweite Zeile '
          'in der Ausgabe darunter erscheint. Der Zeilenumbruch im Quellcode ist nur für die '
          'Übersicht; \n steuert den Zeilenumbruch in der Ausgabe.',
 'person': 'Wichtig ist die Reihenfolge: Erst wird ein Wert abgefragt und in einer Variablen '
           'gespeichert; danach kann derselbe Wert beliebig oft weiterverwendet werden. '
           'Variablennamen müssen exakt gleich geschrieben werden. Groß- und Kleinschreibung '
           'unterscheidet Python. input() liefert auch bei einer Zahl zunächst einen String. Wenn '
           'du später rechnen möchtest, musst du den Wert zum Beispiel mit int() umwandeln. Ein '
           'F-String macht das Einsetzen von Variablen in längere Texte übersichtlich.',
 'basics': 'Ein Programm wird grundsätzlich von oben nach unten ausgeführt. Variablen sind Namen, '
           'unter denen Werte während der Programmausführung erreichbar sind. input() hält das '
           'Programm an, bis eine Eingabe bestätigt wird. Der Rückgabewert wird der Variable links '
           'vom Gleichheitszeichen zugewiesen. Bei einem F-String werden Ausdrücke innerhalb von '
           '{} ausgewertet. Achte darauf, dass die geschweiften Klammern innerhalb des Strings '
           'stehen und der Variablenname genau dem zuvor verwendeten Namen entspricht.',
 'age': 'Die Bedingungen werden der Reihe nach geprüft. Sobald eine Bedingung True ergibt, wird '
        'deren eingerückter Block ausgeführt und die restlichen Zweige dieser if-Kette werden '
        'übersprungen. Deshalb muss die Grenze 65 vor der Grenze 18 stehen: Andernfalls würde eine '
        'Person mit 70 Jahren bereits die allgemeinere Bedingung ab 18 erfüllen. >= bedeutet '
        'größer oder gleich. int() funktioniert nur, wenn die Eingabe eine gültige Ganzzahl ist; '
        'ungültige Eingaben können später mit try/except abgefangen werden.',
 'loops': 'Eine Schleife vermeidet, dass du denselben Befehl mehrfach schreiben musst. '
          'range(start, stop) beginnt beim Startwert und endet unmittelbar vor stop. Daher erzeugt '
          'range(1, 11) genau zehn Werte. Die Variable hinter for nimmt bei jedem Durchlauf den '
          'nächsten Wert an. Alles, was zur Schleife gehören soll, muss gleichmäßig eingerückt '
          'sein. Code nach dem Schleifenblock wird erst ausgeführt, wenn alle Durchläufe beendet '
          'sind.',
 'login': 'Das Beispiel zeigt den Ablauf einer einfachen Zustandslogik: Eine Registrierung '
          'speichert Werte in Variablen; ein späterer Vergleich prüft die eingegebenen Daten. == '
          'vergleicht zwei Werte, während = einen Wert zuweist. and verbindet zwei Bedingungen: '
          'Beide müssen wahr sein. Die Übung demonstriert nur Programmierlogik. Eine echte '
          'Anmeldung benötigt sichere Passwort-Hashes, Schutz vor zu vielen Versuchen und eine '
          'geeignete Speicherung; Klartext-Passwörter sind dafür ungeeignet.',
 'functions': 'Eine Funktion wird mit def definiert und erhält einen Namen. Parameter stehen in '
              'den Klammern und sind lokale Namen, über die beim Aufruf Werte an die Funktion '
              'übergeben werden. Der eingerückte Funktionskörper wird erst beim Aufruf ausgeführt. '
              'print() zeigt einen Wert lediglich an. return ist etwas anderes: Es beendet die '
              'Funktion und gibt einen Wert an die aufrufende Stelle zurück. Du solltest daher '
              'entscheiden, ob eine Funktion etwas anzeigen oder ein Ergebnis für weitere '
              'Berechnungen liefern soll.',
 'lists': 'Listen sind geordnet: Jedes Element hat eine Position, den sogenannten Index. Der erste '
          'Index ist 0. Eine for-Schleife kann direkt über die Elemente laufen, ohne dass du die '
          'Indizes selbst verwalten musst. Innerhalb der Schleife kannst du mit if/elif/else '
          'unterschiedlich auf bestimmte Listeneinträge reagieren. Achte darauf, den '
          'Schleifennamen nicht versehentlich mit einer anderen Variable zu überschreiben.',
 'list-input': 'Die leere Liste [] ist zunächst eine Sammlung ohne Elemente. Bei jedem '
               'Schleifendurchlauf wird input() ausgeführt und der eingegebene Text in einer '
               'Variablen zwischengespeichert. append() hängt diesen Text hinten an die Liste an. '
               'Nach drei Durchläufen enthält die Liste drei Einträge. Die Zahl in range(3) '
               'bestimmt, wie oft die Eingabe stattfindet. nummer + 1 dient hier nur dazu, die '
               'Anzeige für Menschen bei 1 statt 0 beginnen zu lassen.',
 'append': 'Diese Übung verbindet Funktionen, Schleifen und Listen. Die Liste wird innerhalb der '
           'Funktion angelegt und ist dort lokal verfügbar. Jeder eingegebene Name wird mit '
           'append() ergänzt. return gibt die fertige Liste zurück. Der Aufruf namen_sammeln() '
           'startet den Ablauf; das Ergebnis wird anschließend in ergebnis gespeichert. Ein '
           'häufiger Anfängerfehler ist, return innerhalb der Schleife zu platzieren: Dann würde '
           'die Funktion bereits nach dem ersten Namen enden.',
 'types': 'Datentypen bestimmen, welche Art von Wert vorliegt und welche Operationen sinnvoll '
          'sind. str speichert Text, int ganze Zahlen ohne Nachkommastellen, float '
          "Gleitkommazahlen und bool einen Wahrheitswert (True oder False). Beispiele: text = '25' "
          "ist str; zahl = 25 ist int; preis = 4.99 ist float; aktiv = True ist bool. Obwohl '25' "
          'und 25 ähnlich aussehen, sind sie unterschiedliche Typen: Mit Text kannst du nicht ohne '
          'Umwandlung mathematisch rechnen.\n'
          '\n'
          'WICHTIGER FUNKTIONSNAME: Die eingebaute Python-Funktion heißt exakt type(). Beispiel: '
          'print(type(preis)). Python erkennt type und typ als unterschiedliche Namen. type() ist '
          'vorhanden; typ() ist nicht als eingebaute Funktion definiert und führt deshalb zu '
          'NameError. Schreibe den Namen vollständig und achte auf die Reihenfolge der '
          'Buchstaben.\n'
          '\n'
          "float-Beispiel: preis = 4.99 speichert direkt eine Gleitkommazahl. float('4.99') "
          'wandelt passenden Zahlentext in eine Gleitkommazahl um. Python verwendet in '
          'Zahlenliteralen einen Punkt statt eines Dezimalkommas. type(preis) liefert <class '
          "'float'>.\n"
          '\n'
          'print() zeigt einen Wert oder das Ergebnis einer Funktion in der Konsole an. '
          'print(type(preis)) kombiniert also zwei Funktionen: Zuerst ermittelt type(preis) den '
          'Typ, anschließend zeigt print(...) das Ergebnis an. input() liefert dagegen immer '
          'zunächst einen String. Wenn du eine eingegebene Kommazahl weiterverarbeiten möchtest, '
          "kannst du float(input('Preis: ')) verwenden.",
 'while': 'Eine while-Schleife prüft ihre Bedingung vor jedem Durchlauf. Ist sie wahr, wird der '
          'Block ausgeführt; danach wird die Bedingung erneut geprüft. In dieser Aufgabe erhöht '
          'zahl += 1 den Wert bei jedem Durchlauf um eins. Sobald zahl größer als 5 ist, wird die '
          'Bedingung falsch und die Schleife endet. Wenn du vergisst, den Zustand zu verändern, '
          'kann eine Endlosschleife entstehen. break kann eine Schleife vorzeitig verlassen.',
 'operators': 'Vergleichsoperatoren wie ==, !=, >, <, >= und <= vergleichen Werte und liefern True '
              'oder False. and verlangt, dass beide Teilbedingungen wahr sind. or verlangt nur '
              'mindestens eine wahre Teilbedingung. not kehrt das Ergebnis um. Klammern können '
              'helfen, komplexe Bedingungen lesbarer zu machen. Verwechsle == (Vergleich) nicht '
              'mit = (Zuweisung).',
 'list-validation': 'Die Liste enthält nur die Begriffe, die als Eingabe erlaubt sind. in prüft '
                    'die Mitgliedschaft: Das Ergebnis ist True, wenn der Wert vorkommt, sonst '
                    'False. Ein Dictionary wäre passend, wenn zu einem Schlüssel ein zugehöriger '
                    "Wert gespeichert werden soll. Beispiel: person = {'name': 'Chris'}; "
                    "person['name'] liefert 'Chris'. strip() entfernt Leerzeichen am Anfang und "
                    'Ende. lower() wandelt Großbuchstaben in Kleinbuchstaben um. Beide liefern '
                    'einen neuen String zurück; die Zuweisung speichert das Ergebnis.',
 'dict': 'Ein Dictionary ist sinnvoll, wenn du Informationen über einen Schlüssel gezielt '
         "wiederfinden möchtest. Beispiel: person = {'name': 'Chris', 'alter': 30}. person['name'] "
         "liefert 'Chris'. Der Schlüssel beschreibt die Information, der Wert enthält sie. Eine "
         'Liste greift typischerweise über Positionen zu; ein Set sammelt eindeutige Einzelwerte '
         "und hat keine Schlüssel-Wert-Zuordnung. get('fehlend', 'Standard') liefert den "
         'angegebenen Ersatzwert, falls der Schlüssel fehlt.',
 'tuples': 'Ein Tupel ist wie eine Liste, nur dass die Elemente nach dem Erstellen nicht neu '
           'zugewiesen, hinzugefügt oder entfernt werden können. Es eignet sich für '
           'zusammengehörige Werte, die fest bleiben sollen.\n'
           '\n'
           'Ein Set speichert einzelne Werte und entfernt Duplikate. Es verbindet keine Schlüssel '
           'mit Werten. Ein Dictionary speichert dagegen Schlüssel-Wert-Paare, zum Beispiel '
           "{'Name': 'Chris'}. Der Schlüssel 'Name' verweist auf den Wert 'Chris', den du mit "
           "person['Name'] abrufen kannst.\n"
           '\n'
           'len() steht für length (Länge) und zählt die Elemente einer Sammlung. Beispiel: '
           'len(zahlen) zählt, wie viele Einträge in zahlen enthalten sind. Bei einem Set werden '
           'Duplikate nicht mitgezählt, weil sie im Set nur einmal vorkommen. Deshalb ergibt '
           'len({1, 2, 2, 3}) den Wert 3.\n'
           '\n'
           'Unterschied zu print(): len() liefert die Anzahl als Wert zurück. print() zeigt diesen '
           'Wert an. print(len(zahlen)) bedeutet also: Zuerst die Anzahl ermitteln, danach das '
           'Ergebnis ausgeben.',
 'comprehension': 'Eine List Comprehension erstellt eine neue Liste. Ihre Grundform lautet:\n'
                  'neue_liste = [berechnung for element in vorhandene_liste]\n'
                  '\n'
                  'for element in vorhandene_liste nimmt nacheinander jedes Element aus der '
                  'Ausgangsliste. Die Berechnung vor for wird für jeden dieser Werte ausgeführt '
                  'und das Ergebnis in der neuen Liste gesammelt.\n'
                  '\n'
                  'Unterschied zur normalen for-Schleife: Dort erstellst du zuerst eine leere '
                  'Liste und fügst die Ergebnisse einzeln mit append() hinzu. Die List '
                  'Comprehension fasst diese Schritte kompakt in einer Zeile zusammen.',
 'exceptions': 'Fehlerbehandlung verhindert nicht jeden Fehler, ermöglicht aber eine kontrollierte '
               'Reaktion auf erwartbare Probleme. Der try-Block enthält den Code, bei dem ein '
               'Fehler auftreten kann. except ValueError fängt gezielt den Fall ab, dass eine '
               'Umwandlung in eine Zahl nicht gelingt. Fange möglichst konkrete Ausnahmen ab, '
               'statt pauschal alle Fehler zu verschlucken. So bleiben unerwartete '
               'Programmierfehler sichtbar und leichter zu finden.',
 'files': 'Dateien ermöglichen es, Daten über das Ende eines Programmlaufs hinaus zu speichern. '
          'Der Modus w erstellt eine Datei neu oder überschreibt ihren bisherigen Inhalt. a hängt '
          'neue Inhalte an; r liest. with öffnet die Datei für einen begrenzten Block und sorgt '
          'dafür, dass sie danach geschlossen wird, auch wenn im Block ein Fehler auftritt. '
          "encoding='utf-8' ist für deutsche Umlaute und viele weitere Zeichen wichtig. Beim Lesen "
          'und Schreiben muss der Pfad stimmen.',
 'modules': 'Ein Modul ist eine Python-Datei oder eine bereitgestellte Sammlung von Funktionen und '
            'Klassen. import random bindet das Modul random ein. Mit random.randint(1, 6) rufst du '
            'eine Funktion aus diesem Modul auf. Beide Grenzen sind eingeschlossen, deshalb sind '
            'die möglichen Ergebnisse 1, 2, 3, 4, 5 und 6. Der Punkt trennt den Modulnamen vom '
            'Namen der darin enthaltenen Funktion.',
 'oop': 'Eine Klasse ist ein Bauplan, aus dem konkrete Objekte erstellt werden. __init__() wird beim Erstellen eines Objekts automatisch aufgerufen. Python übergibt das neue Objekt an den ersten Parameter self. Weitere Parameter wie wert1 und wert2 erhalten die beim Klassenaufruf übergebenen Werte. Mit self.name = wert1 wird der Wert als Eigenschaft name im Objekt gespeichert. Die Parameter und die Eigenschaften dürfen unterschiedliche Namen haben.',
 'testing': 'Tests prüfen, ob Code das erwartete Ergebnis liefert. assert bedient sich einer '
            'Bedingung: Ist sie wahr, läuft das Programm weiter; ist sie falsch, wird ein '
            'AssertionError ausgelöst. Eine kleine Funktion lässt sich so mit bekannten '
            'Beispielwerten überprüfen. Debugging bedeutet, einen Fehler systematisch '
            'einzugrenzen: Fehlermeldung lesen, betroffene Zeile prüfen, Zwischenwerte '
            'kontrollieren und den Fehler reproduzierbar machen. Tests ersetzen keine vollständige '
            'Prüfung, helfen aber Regressionen früh zu entdecken.'}
EXPLANATION_DETAILS['tkinter-login'] = (
    "ABLAUF DES PROGRAMMS\\n"
    "1. tkinter wird importiert und das Hauptfenster wird erstellt.\\n"
    "2. Der Anmelde-Frame mit seinen Eingabefeldern wird vorbereitet.\\n"
    "3. Zunächst ist nur der Button „Anmelden“ sichtbar. Sein Klick blendet den Frame ein.\\n"
    "4. Der Button „Einloggen“ liest die Eingaben aus und vergleicht sie mit den "
    "vorgegebenen Zugangsdaten.\\n"
    "5. Das Status-Label zeigt an, ob die Anmeldung erfolgreich war.\\n\\n"
    "WICHTIG ZUR SICHERHEIT\\n"
    "Diese Anmeldung ist nur eine Lernübung. Benutzername und Passwort stehen fest im "
    "Quellcode. Das ist keine sichere Benutzerverwaltung und darf nicht zum Schutz echter "
    "Konten oder Daten verwendet werden."
)

PRACTICE_EXERCISES = [e for e in EXERCISES if not e.get('information_only')]

for exercise in EXERCISES:
    extra = EXPLANATION_DETAILS.get(exercise["id"])
    if extra:
        exercise["explanation"] += "\n\nSo funktioniert es im Detail:\n" + extra



# Konkrete Einsteigerbeispiele für jede Lektion.
# Die Beispiele zeigen einzelne Bausteine und sind bewusst nicht die vollständige Übungslösung.
EXAMPLE_GUIDES = {'hello': {'code': 'print("Hallo, Welt!")\n\nprint("Erste Zeile\n"\n      "Zweite Zeile")',
           'explain': 'print() zeigt einen Wert in der Konsole an. Text steht in Anführungszeichen und '
                      'heißt String. Mit \n legst du innerhalb eines Strings einen Zeilenumbruch in '
                      'der Ausgabe fest.',
           'steps': 'SO GIBT print() TEXT AUS\\n'
                    'print() schreibt den Inhalt seiner Klammern in die Konsole. Text muss in '
                    'Anführungszeichen stehen. Python nennt eine solche Textangabe einen String.\\n\\n'
                    'ZEILENUMBRUCH MIT \\n\\n'
                    'Das Zeichen \\n sorgt innerhalb eines Strings dafür, dass die Ausgabe in '
                    'der nächsten Zeile weitergeht. Du kannst damit mehrere Zeilen ausgeben, '
                    'ohne für jede Zeile einen eigenen print()-Aufruf zu benötigen.\\n\\n'
                    'WARUM STEHEN HIER ZWEI TEXTSTÜCKE?\\n'
                    'Die beiden Strings stehen direkt nebeneinander. Python verbindet sie '
                    'automatisch zu einem gemeinsamen Text. Der Umbruch zwischen den beiden '
                    'Quellcodezeilen dient nur der besseren Lesbarkeit.\\n\\n'
                    'ZWEI print()-AUFRUFE\\n'
                    'Jeder neue print()-Aufruf beginnt standardmäßig eine neue Ausgabezeile. '
                    'Deshalb erscheinen „Hallo, Welt!“ und die mehrzeilige Ausgabe darunter.',
 'output': 'Hallo, Welt!\nErste Zeile\nZweite Zeile',
           'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                            'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                            'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                            'vorausgesetzt.'},
 'person': {'code': 'stadt = "Berlin"\n'
                    'print(stadt)\n'
                    '\n'
                    'name = input("Wie heißt du? ")\n'
                    'print(f"Hallo {name}!")',
            'explain': 'Eine Variable ist ein Name, unter dem ein Wert gespeichert wird. = weist den '
                       'Wert rechts dem Namen links zu. input() fragt Text ab. Ein F-String setzt '
                       'gespeicherte Werte in einen Text ein.',
            'steps': '1. stadt = "Berlin" speichert den Text Berlin unter dem Variablennamen stadt.\n'
                     '2. print(stadt) gibt den gespeicherten Wert aus. Ohne Anführungszeichen ist stadt '
                     'ein Variablenname.\n'
                     '3. input(...) zeigt eine Frage und wartet auf die Eingabe. Das Ergebnis ist '
                     'zunächst immer Text (str).\n'
                     '4. name = speichert diesen Eingabetext unter dem Namen name.\n'
                     '5. Das f vor einem String aktiviert einen F-String. {name} ist ein Platzhalter '
                     'für den Inhalt der Variable.',
            'output': 'Berlin\nWie heißt du? Chris\nHallo Chris!',
            'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                             'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                             'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                             'vorausgesetzt.'},
 'basics': {'code': 'name = input("Wie heißt du? ")\nprint(f"Hallo {name}!")',
            'explain': 'input() fragt einen Wert ab und liefert ihn zunächst als Text (str). Eine '
                       'Variable speichert diesen Wert. print() zeigt ihn an. Ein F-String kann den '
                       'gespeicherten Wert in einen anderen Text einsetzen.',
            'steps': '1. input(...) zeigt die Frage an und wartet auf die Eingabe.\n'
                     '2. name = weist den zurückgegebenen Text der Variable name zu.\n'
                     '3. print(...) gibt den folgenden Text aus.\n'
                     '4. Das f vor dem Anführungszeichen kennzeichnet einen F-String.\n'
                     '5. {name} wird beim Ausgeben durch den Inhalt der Variable ersetzt.\n'
                     '6. "name" mit Anführungszeichen wäre der feste Text name; name ohne '
                     'Anführungszeichen bezeichnet die Variable.',
            'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                             'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                             'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                             'vorausgesetzt.'},
 'age': {'code': 'temperatur = 12\n'
                 '\n'
                 'if temperatur >= 25:\n'
                 '    print("Heiß")\n'
                 'elif temperatur >= 15:\n'
                 '    print("Mild")\n'
                 'else:\n'
                 '    print("Kühl")',
         'explain': 'if, elif und else bilden eine Entscheidung mit mehreren möglichen Wegen. Python '
                    'prüft die Bedingungen von oben nach unten und führt den ersten passenden Block '
                    'aus. >= bedeutet „größer oder gleich“.',
         'steps': '1. temperatur = 12 speichert einen Beispielwert.\n'
                  '2. if beginnt die erste Prüfung. >= vergleicht den Wert mit der Grenze 25.\n'
                  '3. Der Doppelpunkt beendet die Bedingungszeile; die Einrückung kennzeichnet den '
                  'zugehörigen Codeblock.\n'
                  '4. elif bedeutet „sonst, wenn“ und wird nur geprüft, wenn die vorherige Bedingung '
                  'falsch war.\n'
                  '5. else wird ausgeführt, wenn keine vorherige Bedingung zutrifft.\n'
                  '6. Nur einer der drei Ausgabeblöcke wird ausgeführt.',
         'output': 'Kühl',
         'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den Konzepten '
                          'aus früheren Übungen. Wenn ein Begriff oder Zeichen noch unbekannt ist, soll '
                          'seine Bedeutung hier erklärt werden – nichts wird vorausgesetzt.'},
 'loops': {'code': 'for nummer in range(1, 4):\n    print(nummer)\n\nprint("Nach der Schleife")',
           'explain': 'Eine for-Schleife führt einen Codeblock für jeden Wert einer Folge aus. '
                      'range(start, ende) erzeugt Zahlen ab start bis vor ende. Die Endgrenze selbst '
                      'gehört nicht dazu.',
           'steps': '1. for beginnt die Schleife.\n'
                    '2. nummer ist die Schleifenvariable und erhält bei jedem Durchlauf den nächsten '
                    'Wert.\n'
                    '3. range(1, 4) liefert die Zahlen 1, 2 und 3; die 4 ist ausgeschlossen.\n'
                    '4. Der Doppelpunkt und die Einrückung kennzeichnen den wiederholten Block.\n'
                    '5. print(nummer) wird einmal für jeden Wert ausgeführt.\n'
                    '6. Der nicht eingerückte print()-Aufruf steht außerhalb der Schleife und läuft '
                    'erst danach.',
           'output': '1\n2\n3\nNach der Schleife',
           'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                            'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                            'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                            'vorausgesetzt.'},
 'login': {'code': 'gespeichert = "Ada"\n'
                   'eingabe = "Ada"\n'
                   '\n'
                   'if eingabe == gespeichert:\n'
                   '    print("Übereinstimmung")\n'
                   'else:\n'
                   '    print("Keine Übereinstimmung")',
           'explain': '== vergleicht zwei Werte auf Gleichheit und ergibt True oder False. if nutzt '
                      'dieses Ergebnis für eine Entscheidung; else beschreibt den Fall, in dem der '
                      'Vergleich nicht stimmt.',
           'steps': '1. Die beiden Variablen speichern Beispieltexte.\n'
                    '2. == vergleicht den Inhalt links und rechts.\n'
                    '3. if führt den eingerückten Block aus, wenn beide Werte gleich sind.\n'
                    '4. else übernimmt den Fall, in dem sie verschieden sind.\n'
                    '5. Ein einzelnes = weist einen Wert zu und ist kein Vergleich. Das Beispiel zeigt '
                    'nur die Programmierlogik, kein sicheres Login-System.',
           'output': 'Übereinstimmung',
           'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                            'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                            'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                            'vorausgesetzt.'},
 'functions': {'code': 'def begruessung(name):\n    print(f"Hallo {name}!")\n\nbegruessung("Ada")',
               'explain': 'def definiert eine Funktion – einen benannten Codeblock, den du aufrufen '
                          'kannst. Ein Parameter ist ein Platzhalter in der Definition. Beim Aufruf '
                          'übergibst du dafür ein Argument, also einen konkreten Wert.',
               'steps': '1. def beginnt die Funktionsdefinition; begruessung ist der Funktionsname.\n'
                        '2. name in den Klammern ist der Parameter.\n'
                        '3. Der Doppelpunkt und die Einrückung markieren den Funktionskörper.\n'
                        '4. Der F-String setzt den Inhalt von name in den Begrüßungstext ein.\n'
                        '5. begruessung("Ada") ruft die Funktion auf. "Ada" ist das Argument, das an '
                        'name übergeben wird.\n'
                        '6. Die Funktion läuft erst, wenn sie aufgerufen wird. print() zeigt Text an; '
                        'return würde einen Wert zurückgeben.',
               'output': 'Hallo Ada!',
               'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                                'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                                'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                                'vorausgesetzt.'},
 'lists': {'code': 'farben = ["Rot", "Blau", "Grün"]\nfor farbe in farben:\n    print(farbe)',
           'explain': 'Eine Liste speichert mehrere Werte in einer festen Reihenfolge. Eckige Klammern '
                      '[ ] kennzeichnen eine Liste; Kommata trennen ihre Elemente. Die Reihenfolge '
                      'bleibt erhalten und gleiche Werte dürfen mehrfach vorkommen.',
           'steps': '1. farben ist der Variablenname.\n'
                    '2. Die eckigen Klammern erstellen eine Liste.\n'
                    '3. Jeder Text in Anführungszeichen ist ein String; die Kommata trennen die '
                    'Elemente.\n'
                    '4. for farbe in farben durchläuft die Liste nacheinander.\n'
                    '5. farbe ist die Schleifenvariable und enthält pro Durchlauf ein Element.\n'
                    '6. Der eingerückte print()-Aufruf gibt jedes Element einzeln aus. Der erste '
                    'Listenindex ist 0.',
           'output': 'Rot\nBlau\nGrün',
           'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                            'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                            'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                            'vorausgesetzt.'},
 'list-input': {'code': 'namen = []\nname = "Ada"\nnamen.append(name)\nprint(namen)',
                'explain': '[] erstellt eine leere Liste. append(wert) hängt einen Wert hinten an eine '
                           'bereits vorhandene Liste an. So kann eine Liste während des Programms '
                           'wachsen.',
                'steps': '1. namen = [] erstellt eine Liste ohne Elemente.\n'
                         '2. name = "Ada" speichert einen Beispieltext in einer Variable.\n'
                         '3. namen.append(name) fügt den Inhalt von name am Ende der Liste hinzu. '
                         'append() verändert die vorhandene Liste.\n'
                         '4. print(namen) zeigt die Liste mit ihrem neuen Element an.\n'
                         '5. input() könnte anstelle des festen Beispieltexts eine Eingabe des '
                         'Benutzers liefern.',
                'output': "['Ada']",
                'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                                 'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                                 'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                                 'vorausgesetzt.'},
 'append': {'code': 'def fuege_hinzu(liste, wert):\n'
                    '    liste.append(wert)\n'
                    '    return liste\n'
                    '\n'
                    'farben = ["Rot"]\n'
                    'ergebnis = fuege_hinzu(farben, "Blau")\n'
                    'print(ergebnis)',
            'explain': 'Eine Funktion kann Werte verarbeiten und mit return ein Ergebnis zurückgeben. '
                       'Eine Liste kann mehrere Werte sammeln; append() fügt ein Element hinzu. Der '
                       'Aufrufer kann den Rückgabewert in einer Variable speichern.',
            'steps': '1. def fuege_hinzu(...) definiert eine Funktion mit zwei Parametern: liste und '
                     'wert.\n'
                     '2. liste.append(wert) hängt den übergebenen Wert an die vorhandene Liste an.\n'
                     '3. return liste beendet die Funktion und gibt die Liste zurück.\n'
                     '4. farben enthält zunächst einen Beispielwert.\n'
                     '5. fuege_hinzu(farben, "Blau") ruft die Funktion auf und übergibt zwei '
                     'Argumente.\n'
                     '6. ergebnis = speichert den Rückgabewert; print(ergebnis) zeigt ihn an. return '
                     'beendet die Funktion – steht es in einer Schleife, endet die Funktion bereits bei '
                     'diesem Durchlauf.',
            'output': "['Rot', 'Blau']",
            'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                             'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                             'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                             'vorausgesetzt.'},
 'types': {'code': 'text = "25"\n'
                   'anzahl = 25\n'
                   'preis = 4.99\n'
                   'aktiv = True\n'
                   '\n'
                   'print(type(text))\n'
                   'print(type(anzahl))\n'
                   'print(type(preis))\n'
                   'print(type(aktiv))',
           'explain': 'Ein Datentyp beschreibt, welche Art von Wert gespeichert ist: str = Text, int = '
                      'ganze Zahl, float = Kommazahl und bool = Wahrheitswert (True oder False). type() '
                      'zeigt den Datentyp eines Wertes an.',
           'steps': '1. Die Variablen enthalten beispielhaft Text, eine ganze Zahl, eine Kommazahl und '
                    'einen Wahrheitswert.\n'
                    '2. Anführungszeichen machen aus 25 einen Text: "25" ist str, 25 ohne '
                    'Anführungszeichen ist int.\n'
                    '3. Eine Kommazahl wird in Python mit Punkt geschrieben, zum Beispiel 4.5; ihr Typ '
                    'ist float.\n'
                    '4. True und False sind die beiden bool-Werte.\n'
                    '5. type(wert) ermittelt den Datentyp. print(...) zeigt das Ergebnis an. Der '
                    'Funktionsname lautet exakt type(), nicht typ().',
           'output': "<class 'str'>\n<class 'int'>\n<class 'float'>\n<class 'bool'>",
           'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                            'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                            'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                            'vorausgesetzt.'},
 'while': {'code': 'zaehler = 1\nwhile zaehler <= 3:\n    print(zaehler)\n    zaehler += 1',
           'explain': 'while wiederholt einen eingerückten Codeblock, solange seine Bedingung wahr ist. '
                      'Anders als bei einer for-Schleife mit range() hängt die Anzahl der Durchläufe '
                      'davon ab, wann die Bedingung falsch wird.',
           'steps': '1. zaehler = 1 legt den Startwert fest.\n'
                    '2. while prüft die Bedingung vor jedem Durchlauf.\n'
                    '3. <= bedeutet „kleiner oder gleich“.\n'
                    '4. Der eingerückte Block wird ausgeführt, solange die Bedingung wahr ist.\n'
                    '5. += 1 erhöht den Zähler um eins; es ist die Kurzform von zaehler = zaehler + 1.\n'
                    '6. Sobald die Bedingung falsch ist, endet die Schleife. Ohne eine passende '
                    'Änderung kann eine Endlosschleife entstehen.',
           'output': '1\n2\n3',
           'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                            'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                            'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                            'vorausgesetzt.'},
 'operators': {'code': 'punkte = 75\n'
                       '\n'
                       'if punkte >= 50 and punkte <= 100:\n'
                       '    print("Punktzahl liegt im Bereich.")\n'
                       'else:\n'
                       '    print("Punktzahl liegt außerhalb.")',
               'explain': 'Ein Vergleich prüft zwei Werte und ergibt True (wahr) oder False (falsch). '
                          '>= bedeutet „größer oder gleich“, <= bedeutet „kleiner oder gleich“. and '
                          'verbindet zwei Prüfungen: Beide müssen wahr sein.',
               'steps': '1. punkte = 75 speichert einen Zahlenwert.\n'
                        '2. >= 50 prüft, ob der Wert mindestens 50 beträgt.\n'
                        '3. <= 100 prüft, ob der Wert höchstens 100 beträgt.\n'
                        '4. and verbindet beide Vergleiche. Das Gesamtergebnis ist nur wahr, wenn beide '
                        'stimmen.\n'
                        '5. if führt den eingerückten Block bei einer wahren Bedingung aus. else '
                        'übernimmt den anderen Fall.\n'
                        '6. = weist einen Wert zu; == vergleicht auf Gleichheit. Verwechsle die beiden '
                        'Zeichen nicht.',
               'output': 'Punktzahl liegt im Bereich.',
               'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                                'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                                'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                                'vorausgesetzt.'},
 'list-validation': {'code': "erlaubt = ['name', 'alter', 'spiel']\n"
                             "eingabe = ' NAME '\n"
                             'eingabe = eingabe.strip().lower()\n'
                             'print(eingabe in erlaubt)',
                     'explain': 'in prüft, ob ein Wert in einer Liste vorkommt. strip() entfernt '
                                'Leerzeichen am Anfang und Ende eines Textes. lower() wandelt '
                                'Buchstaben in Kleinbuchstaben um. Beide Methoden liefern einen neuen '
                                'String zurück.',
                     'steps': '1. erlaubt enthält die Begriffe, die akzeptiert werden sollen.\n'
                              '2. eingabe speichert einen Beispieltext mit Leerzeichen und '
                              'Großbuchstaben.\n'
                              '3. strip() entfernt die äußeren Leerzeichen.\n'
                              '4. lower() wandelt die Buchstaben in Kleinbuchstaben um.\n'
                              '5. Die Zuweisung speichert den bereinigten Text wieder in eingabe.\n'
                              '6. eingabe in erlaubt prüft, ob der Text als Listenelement vorkommt. Das '
                              'Ergebnis ist True oder False.\n'
                              '7. Eine Liste reicht für diese Prüfung. Ein Dictionary wäre sinnvoll, '
                              'wenn zu einem Schlüssel zusätzlich ein Wert gehört.',
                     'output': 'True',
                     'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit '
                                      'den Konzepten aus früheren Übungen. Wenn ein Begriff oder '
                                      'Zeichen noch unbekannt ist, soll seine Bedeutung hier erklärt '
                                      'werden – nichts wird vorausgesetzt.'},
 'dict': {'code': 'person = {"name": "Ada", "alter": 36}\n'
                  'print(person["name"])\n'
                  'print(person.get("ort", "unbekannt"))',
          'explain': 'Ein Dictionary speichert Schlüssel-Wert-Paare. Der Schlüssel benennt die gesuchte '
                     'Information, der Wert enthält sie. Geschweifte Klammern { } und ein Doppelpunkt '
                     'zwischen Schlüssel und Wert kennzeichnen ein Dictionary.',
          'steps': '1. person enthält zwei Schlüssel-Wert-Paare.\n'
                   '2. Der Doppelpunkt trennt jeweils Schlüssel und Wert; Kommata trennen die Paare.\n'
                   '3. person["name"] ruft den Wert über den Schlüssel name ab. Fehlt der Schlüssel, '
                   'entsteht ein KeyError.\n'
                   '4. person.get("ort", "unbekannt") fragt ebenfalls einen Schlüssel ab. Fehlt er, '
                   'wird hier der Ersatzwert "unbekannt" zurückgegeben.\n'
                   '5. Eine Liste greift über Positionen zu; ein Dictionary über Schlüssel. Ein Set '
                   'enthält einzelne Werte ohne Schlüssel-Wert-Paare.',
          'output': 'Ada\nunbekannt',
          'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den Konzepten '
                           'aus früheren Übungen. Wenn ein Begriff oder Zeichen noch unbekannt ist, '
                           'soll seine Bedeutung hier erklärt werden – nichts wird vorausgesetzt.'},
 'tuples': {'code': 'position = (10, 20)\n'
                    "farben = {'Rot', 'Blau', 'Rot'}\n"
                    '\n'
                    'print(position)\n'
                    'print(farben)\n'
                    'print(len(farben))',
            'explain': 'Ein Tupel speichert mehrere Werte in einer festen Reihenfolge und kann nach dem '
                       'Erstellen nicht verändert werden. Ein Set speichert eindeutige Werte; doppelte '
                       'Einträge werden nur einmal berücksichtigt. len() zählt die enthaltenen '
                       'Elemente.',
            'steps': '1. position = (10, 20) erstellt ein Tupel. Runde Klammern kennzeichnen hier die '
                     'geordnete, unveränderliche Sammlung.\n'
                     '2. farben = {...} erstellt ein Set. Das doppelte "Rot" ist darin nur einmal '
                     'enthalten.\n'
                     '3. print() zeigt die jeweilige Sammlung an. Die Reihenfolge eines Sets ist nicht '
                     'festgelegt.\n'
                     '4. len(farben) zählt die Elemente des Sets.\n'
                     '5. print(len(farben)) zeigt die ermittelte Anzahl. len() liefert eine Zahl; '
                     'print() gibt sie aus.\n'
                     '6. Zum Vergleich: Listen sind veränderbar und erlauben Duplikate; Tupel sind '
                     'unveränderbar und erlauben Duplikate; Sets enthalten eindeutige Werte; '
                     'Dictionaries verbinden Schlüssel mit Werten.',
            'output': "(10, 20)\n{'Rot', 'Blau'}\n2",
            'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                             'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                             'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                             'vorausgesetzt.'},
 'comprehension': {'code': 'quadrate = [wert ** 2 for wert in range(0, 5)]\nprint(quadrate)',
                   'explain': 'Eine List Comprehension erstellt eine neue Liste aus einer Folge. Ihre '
                              'Form lautet: [berechnung for element in folge]. for nimmt die Werte '
                              'nacheinander; die Berechnung vor for wird für jeden Wert ausgeführt. ** '
                              'ist der Potenzoperator: ** 2 quadriert eine Zahl.',
                   'steps': '1. range(0, 5) liefert nacheinander 0, 1, 2, 3 und 4. Die Endgrenze 5 '
                            'gehört nicht dazu.\n'
                            '2. for wert in range(0, 5) nimmt diese Werte einzeln auf. wert ist die '
                            'Schleifenvariable.\n'
                            '3. wert ** 2 berechnet das Quadrat des aktuellen Wertes. ** bedeutet '
                            'Potenzieren; ** 2 heißt Quadrieren.\n'
                            '4. Die List Comprehension sammelt die Ergebnisse in einer neuen Liste.\n'
                            '5. print(quadrate) gibt die fertige Liste aus.\n'
                            '6. Die Ausgangsfolge wird dabei nicht verändert. Das Zeichen ^ ist in '
                            'Python kein Ersatz für **.',
                   'output': '[0, 1, 4, 9, 16]',
                   'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                                    'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                                    'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts '
                                    'wird vorausgesetzt.'},
 'exceptions': {'code': 'try:\n'
                        '    zahl = int("12")\n'
                        '    print(zahl)\n'
                        'except ValueError:\n'
                        '    print("Ungültige Zahl")',
                'explain': 'try/except ermöglicht eine kontrollierte Reaktion auf bestimmte Fehler. try '
                           'enthält den Code, bei dem ein Fehler auftreten kann. except fängt den '
                           'angegebenen Fehlertyp ab. int() wandelt gültigen Zahlentext in eine ganze '
                           'Zahl um.',
                'steps': '1. try: beginnt den Codeabschnitt, in dem ein Fehler auftreten kann.\n'
                         '2. int("12") wandelt den Text "12" in die Zahl 12 um.\n'
                         '3. print(zahl) zeigt die Zahl an, wenn die Umwandlung gelingt.\n'
                         '4. Bei einem Text wie "abc" kann int() den Wert nicht umwandeln und löst '
                         'ValueError aus.\n'
                         '5. except ValueError: fängt genau diesen Fehlertyp ab und führt den '
                         'eingerückten Ersatzcode aus.\n'
                         '6. if prüft eine selbst formulierte Bedingung; try/except reagiert auf einen '
                         'Fehler, der während der Ausführung auftritt.',
                'output': '12',
                'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                                 'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                                 'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                                 'vorausgesetzt.'},
 'files': {'code': 'with open("beispiel.txt", "w", encoding="utf-8") as datei:\n'
                   '    datei.write("Hallo Datei!")\n'
                   '\n'
                   'with open("beispiel.txt", "r", encoding="utf-8") as datei:\n'
                   '    inhalt = datei.read()\n'
                   '\n'
                   'print(inhalt)',
           'explain': 'Das Beispiel erstellt eine Textdatei, schreibt einen Text hinein, öffnet sie erneut und liest den Text wieder aus. open() öffnet oder erstellt die Datei. with schließt sie nach jedem eingerückten Block automatisch.',
           'steps': '1. open("beispiel.txt", "w", encoding="utf-8") öffnet die Datei beispiel.txt. Gibt es sie noch nicht, wird sie erstellt. Liegt sie bereits vor, wird ihr bisheriger Inhalt im Modus "w" gelöscht.\n'
                    '2. Der zweite Wert "w" steht für write (schreiben). Er legt fest, dass du in die Datei schreiben möchtest. "r" steht für read (lesen) und öffnet eine vorhandene Datei zum Lesen. "a" steht für append (anhängen): Neuer Text wird am Ende ergänzt, der bisherige Inhalt bleibt erhalten.\n'
                    '3. encoding="utf-8" legt fest, wie Python Textzeichen beim Speichern in Bytes umwandelt und beim Lesen wieder als Zeichen erkennt. UTF-8 kann deutsche Umlaute wie ä, ö, ü und ß sowie sehr viele Zeichen anderer Sprachen darstellen. Verwende beim Schreiben und Lesen dieselbe Codierung.\n'
                    '4. as bedeutet sinngemäß "als". Mit as datei bekommt das geöffnete Dateiobjekt den Variablennamen datei. Über diesen Namen kannst du innerhalb des Blocks auf die geöffnete Datei zugreifen. Der Name datei ist frei wählbar.\n'
                    '5. Der Doppelpunkt am Ende der with-Zeile beginnt den eingerückten Codeblock. datei.write("Hallo Datei!") schreibt den Text in die geöffnete Datei. write() schreibt den Inhalt, zeigt ihn aber nicht in der Konsole an.\n'
                    '6. with verwaltet das Öffnen und Schließen der Datei. Sobald der eingerückte Block verlassen wird, schließt Python die Datei automatisch – auch wenn im Block ein Fehler auftritt. Deshalb brauchst du hier kein zusätzliches close().\n'
                    '7. Im zweiten with-Block wird dieselbe Datei mit dem Modus "r" erneut geöffnet. datei.read() liest den gesamten Dateiinhalt und gibt ihn als Text (String) zurück. Mit inhalt = datei.read() wird dieser Text in der Variable inhalt gespeichert. print(inhalt) zeigt ihn anschließend in der Konsole an.\n\n'
                    'DATEI OHNE INHALT ERSTELLEN:\n'
                    'Wenn du nur eine Datei anlegen möchtest, ohne etwas hineinzuschreiben, reicht zum Beispiel:\n'
                    'with open("leer.txt", "w", encoding="utf-8") as datei:\n'
                    '    pass\n'
                    'pass ist ein Platzhalter. Er führt keine Aktion aus, sorgt aber dafür, dass ein eingerückter Block syntaktisch nicht leer ist. open() hat die Datei zu diesem Zeitpunkt bereits geöffnet beziehungsweise erstellt. Wenn der Block endet, schließt with sie automatisch.\n\n'
                    'DATEI OHNE with SCHLIESSEN:\n'
                    'Du kannst eine Datei auch selbst schließen. Dann musst du open() einer Variablen zuweisen und close() ausdrücklich aufrufen:\n'
                    'datei = open("leer.txt", "w", encoding="utf-8")\n'
                    'datei.close()\n'
                    'close() schließt das Dateiobjekt. Anders als with musst du daran selbst denken. Wenn zwischen open() und close() ein Fehler auftritt, kann das Schließen ausbleiben. Deshalb ist with normalerweise die sicherere und bequemere Methode.\n\n'
                    'EIGENEN SPEICHERORT FESTLEGEN:\n'
                    'Bei einem einfachen Dateinamen wie "beispiel.txt" verwendet Python das aktuelle Arbeitsverzeichnis des Programms. Für einen anderen Speicherort gibst du einen vollständigen Pfad an, zum Beispiel:\n'
                    'with open(r"C:\\Users\\DeinName\\Documents\\beispiel.txt", "w", encoding="utf-8") as datei:\n'
                    '    datei.write("Hallo Datei!")\n'
                    'Ersetze DeinName durch deinen Windows-Benutzernamen. Das r direkt vor dem Pfad-String kennzeichnet einen Raw-String. Dadurch behandelt Python die Backslashes \\ als normale Zeichen und nicht als Beginn von Escape-Sequenzen. Der Ordner Documents muss bereits existieren: open() erstellt die Datei, aber keine fehlenden übergeordneten Ordner. Beim späteren Lesen musst du denselben Pfad verwenden.',
           'output': 'Hallo Datei!',
           'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird vorausgesetzt.'},
 'modules': {'code': 'import random\n\nwurf = random.randint(1, 6)\nprint(wurf)',
             'explain': 'Ein Modul stellt bereits geschriebenen Python-Code bereit. import macht das '
                        'Modul verfügbar. Danach kannst du Funktionen daraus mit dem Modulnamen und '
                        'einem Punkt aufrufen.',
             'steps': '1. import random lädt das Modul random.\n'
                      '2. random.randint(1, 6) ruft randint() aus diesem Modul auf. Der Punkt trennt '
                      'Modul- und Funktionsnamen.\n'
                      '3. randint(1, 6) liefert eine zufällige ganze Zahl von 1 bis 6. Beide Grenzen '
                      'zählen mit.\n'
                      '4. wurf = speichert das Ergebnis. print(wurf) zeigt es an.\n'
                      '5. Unterschied zu def: def definiert eine eigene Funktion; import macht '
                      'vorhandenen Code nutzbar.',
             'output': 'Eine zufällige ganze Zahl von 1 bis 6.',
             'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                              'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                              'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                              'vorausgesetzt.'},
 'oop': {'code': 'class Charakter:\n    def __init__(self, wert1, wert2):\n        self.name = wert1\n        self.alter = wert2\n\nspieler1 = Charakter("Chris", 37)\n\nprint(spieler1.name)\nprint(spieler1.alter)', 'explain': 'Die Klasse Charakter definiert einen Bauplan. Sie kann Eigenschaften und Funktionen (Methoden) festlegen. Hier wird ein Objekt für Personendaten erstellt. Beim Aufruf spieler1 = Charakter("Chris", 37) entsteht das Objekt spieler1. Python übergibt dieses Objekt an self und die Werte an wert1 und wert2.', 'steps': '1. class Charakter: definiert die Klasse. Sie legt fest, welche Daten und Funktionen zu diesem selbst definierten Typ gehören. Hier verwenden wir sie, um Personendaten wie Name und Alter zu verarbeiten und zu speichern.\n\n2. def __init__(self, wert1, wert2): definiert die Einrichtungsfunktion. Python ruft sie automatisch auf, wenn ein neues Objekt mit Charakter(...) erstellt wird.\n\n3. self steht für das gerade erstellte Objekt – hier das Objekt, auf das spieler1 anschließend verweist. Der Parameter könnte auch anders heißen, zum Beispiel spieler1; self ist aber die übliche Schreibweise.\n\n4. wert1 und wert2 sind Parameter und zunächst nur Platzhalter. Bei Charakter("Chris", 37) erhält wert1 den Text "Chris" und wert2 die Zahl 37. Die Parameternamen darfst du frei wählen.\n\n5. spieler1 = Charakter("Chris", 37) erstellt das Objekt. spieler1 ist die Variable, über die du dieses Objekt später erreichst.\n\n6. self.name = wert1 speichert den Wert von wert1 im erstellten Objekt spieler1 unter der Eigenschaft name. self.alter = wert2 speichert den Wert von wert2 im selben Objekt unter alter. Links steht der Speicherplatz im Objekt, rechts der Wert, der dort gespeichert wird.\n\n7. Mit spieler1.name und spieler1.alter liest du die gespeicherten Werte später wieder aus.', 'output': 'Chris\n37', 'beginner_note': 'Datenfluss: spieler1 = Charakter("Chris", 37) → self verweist auf das neue Objekt spieler1; wert1 erhält "Chris", wert2 erhält 37 → self.name und self.alter speichern diese Werte im Objekt → spieler1.name und spieler1.alter lesen sie aus.'},
 'testing': {'code': 'def verdoppeln(zahl):\n'
                     '    return zahl * 2\n'
                     '\n'
                     'assert verdoppeln(3) == 6\n'
                     'print("Test bestanden")',
             'explain': 'Mit dieser Aufgabe schreibst du eine Funktion und prüfst anschließend, ob sie das richtige Ergebnis liefert. Die Funktion verdoppeln() soll eine Zahl mal 2 nehmen. assert vergleicht das Ergebnis mit dem Wert, den du erwartest.',
             'steps': '1. def verdoppeln(zahl): erstellt eine Funktion namens verdoppeln. zahl ist ein Platzhalter für die Zahl, die du später an die Funktion übergibst.\n'
                      '2. return zahl * 2 bedeutet: Multipliziere den übergebenen Wert mit 2 und gib das Ergebnis an die Stelle zurück, von der die Funktion aufgerufen wurde. return zeigt nichts in der Konsole an.\n'
                      '3. verdoppeln(3) ruft die Funktion auf und übergibt die Zahl 3 an den Parameter zahl. Die Rechnung lautet 3 * 2. Die Funktion gibt 6 zurück.\n'
                      '4. == 6 vergleicht das zurückgegebene Ergebnis mit der erwarteten Zahl 6. == bedeutet vergleichen, nicht speichern.\n'
                      '5. assert prüft, ob dieser Vergleich wahr ist. Bei 6 == 6 ist die Prüfung erfolgreich und Python macht mit der nächsten Zeile weiter. Wäre der Vergleich falsch, würde Python einen AssertionError auslösen und das Programm an dieser Stelle abbrechen.\n'
                      '6. print("Test bestanden") wird nur erreicht, wenn assert erfolgreich war. print() zeigt die Meldung in der Konsole an.\n\n'
                      'WICHTIGER UNTERSCHIED: return gibt einen Wert zurück. print() zeigt einen Text oder Wert an. assert prüft, ob eine Bedingung stimmt. Diese drei Anweisungen haben also unterschiedliche Aufgaben.',
             'beginner_note': 'Lerne zuerst, was jede Zeile macht. Danach vergleiche sie mit den '
                              'Konzepten aus früheren Übungen. Wenn ein Begriff oder Zeichen noch '
                              'unbekannt ist, soll seine Bedeutung hier erklärt werden – nichts wird '
                              'vorausgesetzt.'}}
EXAMPLE_GUIDES['tkinter-login'] = {'code': 'import tkinter as tk\n'
          '\n'
          'fenster = tk.Tk()\n'
          'fenster.title("Anmeldung")\n'
          'fenster.geometry("320x260")\n'
          '\n'
          'tk.Label(fenster, text="Nutzername").pack()\n'
          'tk.Entry(fenster).pack()\n'
          'tk.Label(fenster, text="Passwort").pack()\n'
          'tk.Entry(fenster, show="*").pack()\n'
          'tk.Button(fenster, text="Anmelden").pack()\n'
          '\n'
          'fenster.mainloop()',
  'explain': 'Dieses kurze Beispiel zeigt die wichtigsten Tkinter-Bausteine: ein Fenster, Labels, Eingabefelder und einen Button.',
  'steps': '1. import tkinter as tk lädt tkinter unter dem Kurznamen tk.\n'
           '2. tk.Tk() erstellt das Hauptfenster.\n'
           '3. title() und geometry() legen Fenstertitel und Größe fest.\n'
           '4. tk.Label() zeigt eine Beschriftung an.\n'
           '5. tk.Entry() erstellt ein Eingabefeld. show="*" verdeckt die Passworteingabe optisch.\n'
           '6. tk.Button() erstellt eine anklickbare Schaltfläche.\n'
           '7. pack() ordnet die Widgets im Fenster an.\n'
           '8. mainloop() hält das Fenster aktiv.',
  'output': 'Ein Fenster mit Beschriftungen, zwei Eingabefeldern und dem Button „Anmelden“ wird geöffnet.',
  'beginner_note': 'Dieses Beispiel zeigt nur den Aufbau der Oberfläche. Der Button führt noch keine Aktion aus. Die Anmeldung mit Eingabeprüfung kommt in der eigentlichen Aufgabe.'}


# Jedes Lernziel-Konzept erhält ein eigenes minimales Beispiel.
# Die Beispiele erklären die Syntax, ohne die vollständige jeweilige Übungsaufgabe zu lösen.
CONCEPT_EXAMPLES = {'print()': ('print("Hallo!")\nprint("Erste Zeile\n"\n      "Zweite Zeile")',
             'print(...) gibt den Wert aus den Klammern in der Konsole aus. Jeder Aufruf beginnt '
             'standardmäßig eine neue Zeile.'),
 'Textausgabe': ("print('Erste Zeile')\nprint('Zweite Zeile')",
                 'print() gibt den Text aus den Klammern aus. Jeder Aufruf beginnt standardmäßig eine '
                 'neue Zeile.'),
 'Zeilenumbruch \n': ('print("Erste Zeile\nZweite Zeile")',
                       'Zusatzwissen: \n ist eine Escape-Sequenz. Innerhalb eines Strings sorgt sie '
                       'bei der Ausgabe für einen Zeilenumbruch.'),
 'Strings': ("nachricht = 'Hallo Python'",
             'Ein String (str) ist Text. Du erkennst ihn an einfachen oder doppelten Anführungszeichen. '
             'Beide Schreibweisen sind gültig.'),
 'Variablen': ("name = 'Chris'\nalter = 25\nprint(name)\nprint(alter)",
               'Eine Variable speichert einen Wert unter einem Namen. Das können zum Beispiel Texte, '
               "Zahlen oder Koordinaten sein. Bei name = 'Chris' wird der Text Chris in der Variable "
               'name gespeichert. Die Anführungszeichen kennzeichnen den Text als String (str). Zahlen '
               'wie 25 werden dagegen ohne Anführungszeichen geschrieben.'),
 'None': ("ergebnis = None\nprint(ergebnis)\n\nname = 'Chris'\nprint(name)",
          'None ist ein besonderer Python-Wert und steht dafür, dass aktuell kein konkreter Wert '
          'vorhanden ist. Du kannst ihn einer Variable zuweisen, zum Beispiel ergebnis = None. Wenn du '
          'diese Variable mit print(ergebnis) ausgibst, zeigt Python None an. None wird ohne '
          "Anführungszeichen geschrieben. Mit 'None' in Anführungszeichen würdest du dagegen den "
          "normalen Text None speichern. Vergleich: name = 'Chris' speichert einen konkreten Textwert; "
          'ergebnis = None kennzeichnet, dass noch kein konkreter Wert hinterlegt ist. None wird häufig '
          'als Platzhalter oder als Rückgabewert verwendet, wenn eine Funktion kein konkretes Ergebnis '
          'liefert.'),
 'input()': ("name = input('Wie heißt du? ')\nprint(name)",
             "input('Frage') zeigt die Frage an und wartet auf eine Eingabe mit Enter. Der eingegebene "
             'Inhalt wird als String zurückgegeben. Mit name = ... speicherst du ihn in einer '
             'Variable.'),
 'F-Strings': ("name = 'Chris'\nprint(f'Hallo {name}!')",
               'Das f direkt vor dem Anführungszeichen aktiviert einen F-String. Ausdrücke in '
               'geschweiften Klammern werden durch ihre Werte ersetzt. Ohne das f würden die Klammern '
               'als normaler Text erscheinen.'),
 'strip()': ("eingabe = '  Chris  '\nsauber = eingabe.strip()\nprint(sauber)",
             'strip() entfernt Leerraum am Anfang und Ende eines Strings. Die Methode liefert einen '
             'bereinigten String zurück; deshalb speichern wir das Ergebnis hier wieder in einer '
             'Variable.'),
 'lower()': ("eingabe = 'NAME'\nklein = eingabe.lower()\nprint(klein)",
             'lower() liefert einen neuen String zurück, in dem alle Buchstaben in Kleinbuchstaben '
             'umgewandelt sind. Der ursprüngliche String wird dadurch nicht verändert.'),
 'int': ("alter = int('25')\nprint(alter + 1)",
         'int ist der Datentyp für ganze Zahlen. int(...) wandelt einen passenden Wert in eine Ganzzahl '
         'um. int als Begriff bezeichnet den Datentyp; int() ist der Aufruf zur Umwandlung.'),
 'int()': ("alter_text = '25'\nalter = int(alter_text)\nprint(alter + 1)",
           "int() wandelt einen passenden Text oder eine Zahl in eine Ganzzahl um. '25' ist zunächst "
           'Text; nach int(...) ist 25 eine Zahl. Ungültiger Zahlentext löst ValueError aus.'),
 'if': ("temperatur = 20\nif temperatur > 15:\n    print('Warm genug')",
        'if prüft eine Bedingung. Nur wenn sie True ergibt, wird der eingerückte Block ausgeführt. Der '
        'Doppelpunkt beginnt den Block; die Einrückung gehört zur Syntax.'),
 'elif': ('punktzahl = 70\n'
          'if punktzahl >= 90:\n'
          "    print('Sehr gut')\n"
          'elif punktzahl >= 60:\n'
          "    print('Bestanden')",
          'elif bedeutet „sonst, wenn“. Es wird nur geprüft, wenn die vorherigen Bedingungen falsch '
          'waren. Du kannst mehrere elif-Zweige verwenden.'),
 'else': ('regen = False\n'
          'if regen:\n'
          "    print('Schirm mitnehmen')\n"
          'else:\n'
          "    print('Kein Schirm nötig')",
          'else fängt alle Fälle ab, in denen keine vorherige if- oder elif-Bedingung wahr war. else '
          'selbst hat keine Bedingung.'),
 'Vergleichsoperatoren': ('alter = 18\nprint(alter >= 18)\nprint(alter == 18)',
                          'Vergleiche liefern True oder False. == prüft Gleichheit, != Ungleichheit, > '
                          'größer, < kleiner, >= größer/gleich und <= kleiner/gleich.'),
 'for': ("for name in ['Ada', 'Chris']:\n    print(name)",
         'for nimmt nacheinander jedes Element aus einer Folge und legt es in der Laufvariable ab. Der '
         'eingerückte Block läuft einmal pro Element.'),
 'range()': ('for zahl in range(2, 5):\n    print(zahl)',
             'range() erzeugt eine Zahlenfolge. Bei range(start, ende) ist der Startwert enthalten, die '
             'Endgrenze aber ausgeschlossen. Deshalb gibt range(2, 5) nacheinander 2, 3 und 4 aus. Du '
             'kannst range() verwenden, wenn du eine bestimmte Zahlenreihe durchlaufen möchtest.'),
 'Schleifenvariable': ('for nummer in range(3):\n    print(nummer)',
                       'nummer ist die Schleifenvariable. Bei jedem Durchlauf erhält sie den nächsten '
                       'Wert. Bei range(3) sind das 0, 1 und 2.'),
 'if/elif/else': ('note = 2\n'
                  'if note == 1:\n'
                  "    print('Sehr gut')\n"
                  'elif note == 2:\n'
                  "    print('Gut')\n"
                  'else:\n'
                  "    print('Andere Note')",
                  'Die if/elif/else-Kette prüft Zweige der Reihe nach. Der erste passende Zweig wird '
                  'ausgeführt; danach wird der Rest der Kette übersprungen.'),
 'Vergleiche': ("passwort = 'abc'\nprint(passwort == 'abc')\nprint(passwort != 'xyz')",
                '== fragt, ob zwei Werte gleich sind; != fragt, ob sie verschieden sind. Ein Vergleich '
                'verändert die Variablen nicht, sondern ergibt True oder False.'),
 'def': ("def begruessung():\n    print('Hallo!')",
         'def definiert eine Funktion. Die eingerückten Zeilen bilden ihren Funktionskörper. Die '
         'Definition allein führt den Inhalt noch nicht aus.'),
 'Parameter': ('def begruessung(name):\n    print(name)',
               'name ist ein Parameter. Er ist ein Platzhalter für einen Wert, den du beim '
               'Funktionsaufruf übergibst.'),
 'Aufruf': ("def hallo():\n    print('Hallo!')\n\nhallo()",
            'Ein Funktionsaufruf besteht aus dem Funktionsnamen und runden Klammern. Erst hallo() führt '
            'den zuvor definierten Funktionskörper aus.'),
 'return': ('def verdoppeln(zahl):\n    return zahl * 2\n\nergebnis = verdoppeln(4)',
            'return beendet die Funktion und gibt einen Wert an die aufrufende Stelle zurück. Das ist '
            'anders als print(), das nur etwas anzeigt.'),
 'Listen': ("spiele = ['Aion 2', 'Portal']\nprint(spiele[0])",
            'Eine Liste wird mit eckigen Klammern erstellt. Elemente werden durch Kommas getrennt. Der '
            'erste Index ist 0, deshalb liefert spiele[0] den ersten Eintrag.'),
 'leere Listen': ("namen = []\nnamen.append('Chris')",
                  '[] erstellt eine leere Liste. Danach kannst du Elemente hinzufügen, zum Beispiel mit '
                  'append().'),
 'append()': ('zahlen = [1, 2]\nzahlen.append(3)\nprint(zahlen)',
              'append(wert) hängt genau einen Wert hinten an die Liste an. Die vorhandene Liste wird '
              'direkt verändert.'),
 'Datentypen': ("text = 'Hallo'\nzahl = 12\nkommazahl = 2.5\nwahr = True",
                'Datentypen bestimmen, welche Art von Wert gespeichert ist. Text ist str, ganze Zahlen '
                'sind int, Kommazahlen float und Wahrheitswerte bool.'),
 'str': ('wert = str(25)\nprint(wert)',
         'str ist der Datentyp für Text. Ein Wert wie "Hallo" ist ein String. str(wert) wandelt einen '
         'anderen Wert in seine Textdarstellung um.'),
 'float': ('preis = 4.99\nprint(preis)\nprint(type(preis))',
           'float ist der Datentyp für Gleitkommazahlen. Eine Zahl wie 4.99 ist bereits vom Typ float. '
           "Alternativ wandelt float('4.99') passenden Zahlentext in eine Gleitkommazahl um. Python "
           'verwendet in Zahlenliteralen einen Punkt, kein Dezimalkomma. Die Typabfrage gibt <class '
           "'float'> aus."),
 'bool': ('ist_aktiv = True\nprint(bool(1))',
          'bool ist der Datentyp für Wahrheitswerte: True (wahr) oder False (falsch). bool(wert) '
          'wandelt einen Wert in einen Wahrheitswert um.'),
 'type()': ("wert = 25\nprint(type(wert))\n\n# Ausgabe: <class 'int'>",
            'type() ist eine eingebaute Python-Funktion. Sie gibt den Typ eines Wertes zurück. '
            'print(type(wert)) zeigt diesen Typ in der Konsole an. Schreibe den Namen exakt type – mit '
            'e vor(). typ() ist kein eingebauter Python-Befehl und verursacht NameError. Python '
            'unterscheidet die Schreibweise exakt.'),
 'while': ('zaehler = 1\nwhile zaehler <= 3:\n    print(zaehler)\n    zaehler += 1',
           'while wiederholt den eingerückten Block, solange die Bedingung wahr ist. Verändere '
           'innerhalb des Blocks einen relevanten Wert, damit die Schleife enden kann.'),
 'Bedingung': ("bereit = True\nwhile bereit:\n    print('Start')\n    bereit = False",
               'Eine Bedingung ist ein Ausdruck, der True oder False ergibt. Schleifen und '
               'if-Anweisungen verwenden dieses Ergebnis, um über den Ablauf zu entscheiden.'),
 'break': ('for zahl in range(10):\n    if zahl == 3:\n        break\n    print(zahl)',
           'break beendet die nächstgelegene Schleife sofort. Im Beispiel werden 0, 1 und 2 ausgegeben; '
           'bei 3 wird die Schleife verlassen.'),
 '==': ('print(5 == 5)',
        '== vergleicht zwei Werte auf Gleichheit. Das Ergebnis ist ein boolescher Wert: True oder '
        'False. Nicht mit der Zuweisung = verwechseln.'),
 '!=': ('print(5 != 3)',
        '!= bedeutet „ist ungleich“. Das Ergebnis ist True, wenn die beiden verglichenen Werte '
        'verschieden sind.'),
 '>': ('print(8 > 4)', '> prüft, ob der linke Wert größer als der rechte ist.'),
 '<': ('print(2 < 7)', '< prüft, ob der linke Wert kleiner als der rechte ist.'),
 'and': ('alter = 25\nprint(alter >= 18 and alter < 65)',
         'and ist nur dann True, wenn beide Teilbedingungen True sind.'),
 'in': ("erlaubt = ['name', 'alter', 'spiel']\neingabe = 'alter'\nprint(eingabe in erlaubt)",
        'in prüft, ob ein Wert in einer Sammlung vorkommt. Bei einer Liste ist das Ergebnis True, wenn '
        'ein passendes Element enthalten ist, sonst False.'),
 'or': ('regen = True\nwind = False\nprint(regen or wind)',
        'or ist True, wenn mindestens eine der beiden Teilbedingungen True ist.'),
 'not': ('angemeldet = False\nprint(not angemeldet)',
         'not kehrt einen Wahrheitswert um: True wird False und False wird True.'),
 'dict': ("person = {'name': 'Chris', 'alter': 25}\nprint(person['name'])",
          'Ein Dictionary speichert Schlüssel-Wert-Paare in geschweiften Klammern. Über den Schlüssel '
          'in eckigen Klammern rufst du den zugehörigen Wert ab.'),
 'Schlüssel': ("person = {'name': 'Chris'}\nprint(person.keys())",
               'Ein Schlüssel identifiziert einen Eintrag im Dictionary. Schlüssel müssen eindeutig '
               'sein. Mit keys() kannst du die vorhandenen Schlüssel ansehen.'),
 'Werte': ("person = {'name': 'Chris'}\nprint(person.values())",
           'Die Werte sind die Daten, die zu den Schlüsseln gehören. values() gibt eine Ansicht der '
           'gespeicherten Werte zurück.'),
 'get()': ("person = {'name': 'Chris'}\nprint(person.get('alter', 'unbekannt'))",
           'get(schluessel, standard) liest einen Wert aus. Existiert der Schlüssel nicht, wird der '
           'angegebene Standardwert zurückgegeben, statt einen KeyError auszulösen.'),
 'tuple': ('position = (10, 20)\nprint(position[0])',
           'Ein Tupel ist eine geordnete Sammlung, die nach dem Erstellen nicht verändert werden kann. '
           'Es wird häufig mit runden Klammern geschrieben.'),
 'set': ("farben = {'Rot', 'Blau', 'Rot'}\nprint(farben)",
         'Ein Set speichert jedes Element nur einmal. Doppelte Einträge werden zusammengeführt. Sets '
         'haben keinen indexbasierten Zugriff.'),
 'Unveränderlichkeit': ('koordinaten = (10, 20)\n# koordinaten[0] = 5  # würde TypeError auslösen',
                        'Ein Tupel ist unveränderlich: Seine vorhandenen Elemente können nicht neu '
                        'zugewiesen werden. Wenn du eine veränderbare Sammlung brauchst, verwende eine '
                        'Liste.'),
 'Eindeutigkeit': ('nummern = {1, 2, 2, 3}\nprint(nummern)',
                   'Ein Set enthält keine doppelten Elemente. Im Beispiel wird die 2 nur einmal '
                   'gespeichert.'),
 'List Comprehension': ('quadrate = [wert ** 2 for wert in range(0, 5)]\nprint(quadrate)',
                        'Der Teil vor for legt fest, was berechnet und in die neue Liste eingetragen '
                        'wird: wert ** 2 quadriert den aktuellen Wert. Der Teil nach for legt fest, '
                        'welche Werte verwendet werden. range(0, 5) liefert 0, 1, 2, 3 und 4; die '
                        'Endgrenze 5 ist ausgeschlossen. Das Ergebnis ist [0, 1, 4, 9, 16].'),
 'try': ("try:\n    zahl = int('12')\nexcept ValueError:\n    print('Ungültig')",
         'try umschließt Code, bei dem eine Ausnahme auftreten kann. Wenn ein passender Fehler '
         'auftritt, wird die Ausführung im except-Zweig fortgesetzt.'),
 'except': ("try:\n    zahl = int('abc')\nexcept ValueError:\n    print('Bitte eine Zahl eingeben')",
            'except behandelt einen bestimmten Fehlertyp. Nenne möglichst konkrete Ausnahmen, damit '
            'andere Programmierfehler nicht versehentlich verborgen werden.'),
 'ValueError': ("int('abc')  # löst ValueError aus",
                'ValueError entsteht unter anderem, wenn eine Funktion einen Wert vom richtigen Typ, '
                "aber in einem ungültigen Format erhält. int('abc') kann nicht in eine Ganzzahl "
                'umgewandelt werden.'),
 'open()': ("datei = open('notiz.txt', 'r', encoding='utf-8')\ndatei.close()",
            'open() öffnet eine Datei. Der zweite Parameter bestimmt den Modus: r liest, w schreibt und '
            'überschreibt, a hängt an. Mit with wird das Schließen automatisch erledigt.'),
 'with': ("with open('notiz.txt', 'w', encoding='utf-8') as datei:\n    datei.write('Hallo')",
          'with verwaltet eine Ressource für die Dauer des eingerückten Blocks. Bei Dateien sorgt es '
          'dafür, dass sie auch bei einem Fehler ordnungsgemäß geschlossen werden.'),
 'read()': ("with open('notiz.txt', 'r', encoding='utf-8') as datei:\n    inhalt = datei.read()",
            'read() liest den Dateiinhalt und gibt ihn als String zurück. Die Datei muss zuvor im '
            'Lesemodus geöffnet worden sein.'),
 'write()': ("with open('notiz.txt', 'w', encoding='utf-8') as datei:\n    datei.write('Hallo Datei')",
             'write() schreibt einen String in eine geöffnete Datei. Im Modus w wird vorhandener Inhalt '
             'überschrieben; im Modus a wird angehängt.'),
 'import': ('import random\nprint(random.randint(1, 6))',
            'import bindet ein Modul ein. Danach kannst du dessen Funktionen über den Modulnamen und '
            'einen Punkt aufrufen.'),
 'Module': ('import math\nprint(math.sqrt(16))',
            'Ein Modul bündelt wiederverwendbaren Python-Code. Die Standardbibliothek enthält viele '
            'Module, die mit Python mitgeliefert werden.'),
 'random': ('import random\nwurf = random.randint(1, 6)',
            'random ist ein Modul für Zufallsoperationen. randint(a, b) liefert eine zufällige '
            'Ganzzahl, wobei beide Grenzen eingeschlossen sind.'),
 'class': ('class Charakter:\n    pass', 'class definiert eine Klasse – den Bauplan für Objekte. Die Klasse selbst ist noch kein einzelner Charakter. pass ist hier nur ein Platzhalter für einen vorerst leeren Klassenkörper.'),
 '__init__': ('class Charakter:\n    def __init__(self, wert1, wert2):\n        self.name = wert1\n        self.alter = wert2', '__init__() ist eine besondere Methode. Python ruft sie automatisch auf, wenn ein neues Objekt erstellt wird. Die übergebenen Werte werden hier als Eigenschaften im neuen Objekt gespeichert.'),
 'self': ('class Charakter:\n    def __init__(self, wert1):\n        self.name = wert1', 'self steht für das konkrete Objekt, das gerade eingerichtet wird. Python übergibt dieses Objekt automatisch als ersten Parameter. self.name ist eine Eigenschaft dieses Objekts.'),
 'Objekte': ('class Charakter:\n    pass\n\nspieler1 = Charakter()\nspieler2 = Charakter()', 'Ein Objekt ist ein konkretes Exemplar einer Klasse. Charakter() erstellt ein Objekt. spieler1 und spieler2 verweisen auf zwei verschiedene Objekte derselben Klasse.'),
 'assert': ('ergebnis = 2 + 2\nassert ergebnis == 4',
            'assert prüft eine Bedingung. Ist sie falsch, wird AssertionError ausgelöst. Assertions '
            'eignen sich für Tests und interne Annahmen.'),
 'Traceback': ('# Beispiel: Eine Fehlermeldung zeigt\n'
               '# den Aufrufpfad und die Fehlerstelle.\n'
               'print(1 / 0)',
               'Ein Traceback ist Pythons Rückverfolgung eines Fehlers. Er zeigt die beteiligten '
               'Aufrufe und führt zur Stelle, an der die Ausnahme ausgelöst wurde.'),
 'Debugging': ("wert = 10\nprint('Kontrollwert:', wert)\nassert wert == 10",
               'Debugging bedeutet, einen Fehler systematisch zu suchen. Lies die Fehlermeldung, prüfe '
               'die genannte Zeile und gib bei Bedarf Zwischenwerte aus, um den tatsächlichen '
               'Programmzustand zu sehen.'),
 '>=': ('alter = 18\nprint(alter >= 18)',
        '>= bedeutet größer oder gleich. Der Vergleich ergibt True, wenn der linke Wert mindestens so '
        'groß wie der rechte Wert ist.'),
 '<=': ('alter = 99\nprint(alter <= 99)',
        '<= bedeutet kleiner oder gleich. Der Vergleich ergibt True, wenn der linke Wert höchstens so '
        'groß wie der rechte Wert ist.'),
 '+=': ('zaehler = 1\nzaehler += 1\nprint(zaehler)',
        '+= addiert den rechten Wert zur vorhandenen Variable und speichert das Ergebnis wieder in '
        'derselben Variable. zaehler += 1 entspricht zaehler = zaehler + 1.'),
 'len()': ("wochentage = ('Mo', 'Di', 'Mi')\nprint(len(wochentage))",
           'len(sammlung) zählt die enthaltenen Elemente und gibt die Anzahl als Zahl zurück. Bei einem '
           'String zählt len() die Zeichen. Bei einem Set werden nur die eindeutigen Elemente gezählt.'),
 '**': ('zahl = 3\nprint(zahl ** 2)',
        '** ist in Python der Potenzoperator. Links steht die Basis, rechts der Exponent. Bei 3 ** 2 '
        'wird 3 mit sich selbst multipliziert: 3 × 3 = 9. Das nennt man Quadrieren. Die Grafik zeigt '
        'weitere Rechenschritte.'),
 'Fernet': ('from cryptography.fernet import Fernet\n\nschluessel = Fernet.generate_key()\nfernet = Fernet(schluessel)',
            'Fernet ist die Klasse aus dem Paket cryptography. Fernet.generate_key() erzeugt einen zufälligen Schlüssel. '
            'schluessel = Fernet.generate_key() speichert diesen Schlüssel in der Variablen schluessel. '
            'Danach erstellt Fernet(schluessel) ein Verschlüsselungsobjekt, das den Schlüssel verwendet; '
            'fernet = ... speichert dieses Objekt in der Variablen fernet. Wichtig: fernet enthält danach NICHT '
            'nur den Schlüssel, sondern das Objekt mit den Funktionen encrypt() und decrypt(). '
            'Darum ist fernet = Fernet.generate_key() nicht dasselbe: Diese Schreibweise würde nur den Schlüssel '
            'in fernet speichern, aber kein Verschlüsselungsobjekt erzeugen.'),
 'generate_key()': ('from cryptography.fernet import Fernet\n\nschluessel = Fernet.generate_key()\nprint(schluessel)',
                    'Fernet.generate_key() erzeugt einen zufälligen, gültigen Fernet-Schlüssel. '
                    'schluessel = Fernet.generate_key() speichert genau diesen erzeugten Schlüssel in der '
                    'Variablen schluessel. Du musst denselben Schlüssel später wieder laden, um die Daten '
                    'entschlüsseln zu können. Geht er verloren, sind die Daten nicht mehr entschlüsselbar.'),
 'Schlüssel dauerhaft speichern': ('from pathlib import Path\nfrom cryptography.fernet import Fernet\n\nbenutzerordner = Path.home()\ndxordner = benutzerordner / ".dxpyguide"\ndxordner.mkdir(parents=True, exist_ok=True)\nschluessel_datei = dxordner / "fernet.key"  # Hier wird der Pfad zur Datei fernet.key gespeichert\n\n# Prüfen, ob die Datei fernet.key bereits existiert\nif schluessel_datei.exists():\n    schluessel = schluessel_datei.read_bytes()\nelse:\n    schluessel = Fernet.generate_key()\n    schluessel_datei.write_bytes(schluessel)\n\nfernet = Fernet(schluessel)',
                                 'Path.home() liefert deinen Benutzerordner. Darin wird der Ordner .dxpyguide erstellt. Mit '
                                 'schluessel_datei = dxordner / \"fernet.key\" wird der vollständige Pfad zur Datei fernet.key in der Variablen '
                                 'schluessel_datei gespeichert. Deshalb prüft if schluessel_datei.exists(), ob genau diese Datei vorhanden ist. '
                                 'Wenn ja, lädt read_bytes() den gespeicherten Schlüssel. Wenn nein, erzeugt generate_key() einen neuen Schlüssel und '
                                 'write_bytes() speichert ihn in fernet.key. Fernet(schluessel) erstellt anschließend das Verschlüsselungsobjekt. '
                                 'Beim nächsten Programmstart wird derselbe Schlüssel wieder geladen. Hinweis: Die Datei ist nicht passwortgeschützt. '
                                 'Andere Personen mit Zugriff auf dein Benutzerkonto könnten sie lesen.'),
 'encrypt()': ('from cryptography.fernet import Fernet\n\nschluessel = Fernet.generate_key()\nfernet = Fernet(schluessel)\n\nnachricht = "Geheime Nachricht"\ndaten = nachricht.encode("utf-8")\nverschluesselt = fernet.encrypt(daten)',
               'Zuerst erzeugt Fernet.generate_key() einen Schlüssel. schluessel = ... speichert ihn; '
               'fernet = Fernet(schluessel) erstellt daraus das Verschlüsselungsobjekt. Die Kurzform '
               'fernet = Fernet(Fernet.generate_key()) macht genau diese beiden Schritte in einer Zeile: '
               'Der innere Aufruf erzeugt den Schlüssel, der äußere erstellt das Objekt. Dagegen würde '
               'fernet = Fernet.generate_key() nur den Schlüssel speichern und kein Verschlüsselungsobjekt liefern. '
               'nachricht speichert den ursprünglichen Text. encode("utf-8") wandelt ihn in Bytes um und speichert '
               'sie in daten. encrypt(daten) verschlüsselt diese Bytes. verschluesselt enthält danach die verschlüsselten Bytes.'),
 'decrypt()': ('from cryptography.fernet import Fernet\n\nfernet = Fernet(Fernet.generate_key())\noriginal = "Hallo"\nverschluesselt = fernet.encrypt(original.encode("utf-8"))\ndaten = fernet.decrypt(verschluesselt)\nnachricht = daten.decode("utf-8")\nprint(nachricht)',
               'decrypt(verschluesselt) erhält die verschlüsselten Bytes und entschlüsselt sie mit demselben Schlüssel. '
               'Das Ergebnis sind wieder Bytes und wird in daten gespeichert. decode("utf-8") wandelt diese Bytes '
               'zurück in einen normalen Text-String; nachricht enthält nun den lesbaren Text. print(nachricht) gibt ihn aus. '
               'Für echte gespeicherte Dateien musst du dafür den zuvor gespeicherten Schlüssel wieder laden.'),
 'encode()': ('text = "Grüße"\ndaten = text.encode("utf-8")',
              'encode("utf-8") wandelt einen Python-String (Text) in Bytes um. Verschlüsselungsfunktionen '
              'wie Fernet.encrypt() erwarten Bytes statt eines normalen Strings. UTF-8 legt fest, wie Zeichen '
              'wie ä, ö und ü in Bytes dargestellt werden.'),
 'decode()': ('daten = b"Hallo"\ntext = daten.decode("utf-8")\nprint(text)',
              'decode("utf-8") macht den umgekehrten Schritt: Es wandelt Bytes wieder in einen lesbaren '
              'Python-String um. Nach fernet.decrypt(...) erhältst du Bytes und kannst sie mit decode("utf-8") '
              'wieder als Text verwenden.')}


# Ausführliche Einzelbeispiele für das Abschlussprojekt mit tkinter.
# Jeder Begriff aus der Konzeptliste erhält ein eigenes Codebeispiel und eine Erklärung.
CONCEPT_EXAMPLES.update({
    "tkinter": (
        "import tkinter\n\n"
        "# Alternative Kurzschreibweise mit as:\n"
        "import tkinter as tk",
        "WAS IST TKINTER?\n"
        "tkinter ist ein Modul aus Pythons Standardbibliothek. Damit erstellst du grafische "
        "Fenster mit Beschriftungen, Eingabefeldern und Buttons.\n\n"
        "MODUL IMPORTIEREN\n"
        "Mit import tkinter bindest du das Modul ein. Danach sprichst du seine Bausteine "
        "zum Beispiel mit tkinter.Tk() oder tkinter.Button() an.\n\n"
        "KURZFORM MIT as\n"
        "Mit import tkinter as tk gibst du dem Modul den Kurznamen tk. Danach verwendest "
        "du zum Beispiel tk.Tk() oder tk.Button(). Nutze eine der beiden Schreibweisen, "
        "nicht beide gleichzeitig."
    ),
    "Tk()": (
        "fenster = tk.Tk()",
        "WAS PASSIERT HIER?\n"
        "tk.Tk() erstellt das Hauptfenster. Mit fenster = speicherst du dieses Fenster "
        "in der Variable fenster, damit du es später einstellen kannst.\n\n"
        "FENSTER EINSTELLEN\n"
        "Mit fenster.title('Anmeldung') legst du den Fenstertitel fest. "
        "fenster.geometry('320x260') bestimmt die Anfangsgröße: 320 Pixel breit "
        "und 260 Pixel hoch.\n\n"
        "WICHTIG\n"
        "Für eine normale Tkinter-Anwendung erstellst du nur ein Tk-Hauptfenster. "
        "Achte außerdem auf Groß- und Kleinschreibung."
    ),
    "Label": (
        "tk.Label(fenster, text='Willkommen').pack()",
        "WAS MACHT LABEL?\n"
        "tk.Label() erstellt eine Beschriftung. Damit zeigst du Text im Fenster an, "
        "zum Beispiel eine Überschrift oder den Hinweis „Nutzername“.\n\n"
        "DIE WICHTIGSTEN ANGABEN\n"
        "fenster gibt an, in welchem Bereich das Label erscheinen soll. Mit text= "
        "bestimmst du den angezeigten Text. pack() ordnet das Label im Fenster an.\n\n"
        "MERKE\n"
        "Ein Label dient zum Anzeigen. Der Benutzer kann seinen Text nicht direkt "
        "wie in einem Eingabefeld bearbeiten."
    ),
    "Entry": (
        "tk.Entry(fenster).pack()\ntk.Entry(fenster, show='*').pack()",
        "WAS MACHT ENTRY?\n"
        "tk.Entry() erstellt ein einzeiliges Eingabefeld. Hier kann der Benutzer selbst "
        "Text eingeben, zum Beispiel seinen Namen.\n\n"
        "EINGABE AUSLESEN\n"
        "Mit get() kannst du den eingegebenen Text später aus dem Feld auslesen.\n\n"
        "PASSWORTFELD\n"
        "Mit show='*' werden die eingegebenen Zeichen als Sternchen angezeigt. "
        "Das Passwort wird dadurch nicht verschlüsselt. Es wird nur auf dem Bildschirm "
        "verdeckt dargestellt."
    ),
    "Button": (
        "tk.Button(fenster, text='Start').pack()",
        "WAS MACHT EIN BUTTON?\n"
        "tk.Button() erstellt eine anklickbare Schaltfläche, zum Beispiel den Button "
        "„Anmelden“.\n\n"
        "BESCHRIFTUNG UND PLATZIERUNG\n"
        "Mit text= legst du fest, was auf dem Button steht. pack() ordnet ihn im Fenster an.\n\n"
        "EINE AKTION HINZUFÜGEN\n"
        "Mit command= kannst du festlegen, was beim Anklicken passieren soll. "
        "Das lernst du im nächsten Abschnitt."
    ),
    "command": (
        "tk.Button(fenster, text='Fenster schließen', command=fenster.destroy).pack()",
        "WOFÜR IST command= DA?\n"
        "Mit command= legst du fest, welche Aktion beim Anklicken eines Buttons ausgeführt wird.\n\n"
        "BEISPIEL\n"
        "fenster.destroy ist eine Tkinter-Methode, die das Fenster schließt. "
        "Mit command=fenster.destroy wird sie beim Klick auf den Button aufgerufen.\n\n"
        "WICHTIG\n"
        "Hier wird eine vorhandene Methode verwendet. Du brauchst dafür keine eigene "
        "Funktion mit def zu schreiben."
    ),
    "get()": (
        "eingabe = tk.Entry(fenster)\neingabe.get()",
        "WAS MACHT get()?\n"
        "Entry.get() liest den Text aus, den der Benutzer in ein Eingabefeld geschrieben hat. "
        "Der gelesene Inhalt wird als Text (String) zurückgegeben.\n\n"
        "WAS KANNST DU DAMIT MACHEN?\n"
        "Du kannst den Wert in einer Variablen speichern und anschließend zum Beispiel "
        "mit if überprüfen oder mit print() ausgeben."
    ),
    "if": (
        "if nutzername == 'admin':\n    print('Name ist richtig')\nelse:\n    print('Name ist falsch')",
        "WAS MACHT if?\n"
        "if prüft eine Bedingung. Ist sie wahr (True), führt Python den eingerückten Code "
        "darunter aus. Ist sie falsch (False), wird dieser Code übersprungen.\n\n"
        "DER ALTERNATIVE FALL\n"
        "Mit else legst du fest, was passieren soll, wenn die Bedingung nicht stimmt.\n\n"
        "AUF DIE SCHREIBWEISE ACHTEN\n"
        "Nach der Bedingung steht ein Doppelpunkt. Die Einrückung zeigt Python, welche "
        "Anweisungen zu if oder else gehören."
    ),
    "and": (
        "if nutzername == 'admin' and passwort == 'passwort':\n    print('Eingeloggt')",
        "WAS BEDEUTET and?\n"
        "and bedeutet UND. Damit verbindest du mehrere Bedingungen miteinander.\n\n"
        "BEIDE BEDINGUNGEN MÜSSEN STIMMEN\n"
        "Das Gesamtergebnis ist nur dann True, wenn alle Bedingungen wahr sind. "
        "Bei der Anmeldung müssen deshalb sowohl der Nutzername als auch das Passwort "
        "richtig sein. Ist eine Angabe falsch, ist die gesamte Prüfung nicht erfolgreich."
    ),
    "pack()": (
        "tk.Label(fenster, text='Anmeldung').pack(pady=10)",
        "WAS MACHT pack()?\n"
        "pack() platziert ein bereits erstelltes Widget – zum Beispiel ein Label, Entry, "
        "Button oder Frame – in seinem übergeordneten Bereich.\n\n"
        "ABSTAND EINSTELLEN\n"
        "Mit pady=10 fügst du oberhalb und unterhalb des Widgets jeweils 10 Pixel "
        "Außenabstand hinzu. Für den seitlichen Abstand verwendest du padx.\n\n"
        "WICHTIG\n"
        "pack() erstellt kein Widget. Es sorgt dafür, dass ein vorhandenes Widget "
        "im Fenster angeordnet wird."
    ),
})

TUTORIAL_IDS = [e["id"] for e in EXERCISES]

BG = "#050505"
PANEL = "#101010"
PANEL2 = "#191919"
BORDER = "#3a2818"
TEXT = "#f5f5f5"
MUTED = "#b5a18c"
ACCENT = "#ff7900"
GREEN = "#ff8a00"
ORANGE = "#ff9a24"
RED = "#ff6038"
EDITOR_BG = "#090909"


class Store:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(DB_PATH)
        self.db.execute("""CREATE TABLE IF NOT EXISTS progress (
            exercise_id TEXT PRIMARY KEY,
            code TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'new',
            attempts INTEGER NOT NULL DEFAULT 0,
            updated REAL NOT NULL DEFAULT 0,
            completed INTEGER NOT NULL DEFAULT 0
        )""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, value TEXT
        )""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS hidden_recent (
            exercise_id TEXT PRIMARY KEY
        )""")
        self.db.commit()

    def get(self, exercise_id):
        row = self.db.execute(
            "SELECT code,status,attempts,updated,completed FROM progress WHERE exercise_id=?",
            (exercise_id,)
        ).fetchone()
        return row or ("", "new", 0, 0, 0)

    def save_code(self, exercise_id, code):
        old = self.get(exercise_id)
        status = "in_progress" if code.strip() and not old[4] else old[1]
        self.db.execute("""INSERT INTO progress(exercise_id,code,status,attempts,updated,completed)
            VALUES(?,?,?,?,?,?) ON CONFLICT(exercise_id) DO UPDATE SET
            code=excluded.code,status=CASE WHEN progress.completed=1 THEN progress.status ELSE excluded.status END,
            updated=excluded.updated""",
            (exercise_id, code, status, old[2], time.time(), old[4]))
        self.db.commit()

    def attempt(self, exercise_id):
        old = self.get(exercise_id)
        self.db.execute("""INSERT INTO progress(exercise_id,code,status,attempts,updated,completed)
            VALUES(?,?,?,?,?,?) ON CONFLICT(exercise_id) DO UPDATE SET
            attempts=progress.attempts+1, updated=excluded.updated""",
            (exercise_id, old[0], old[1], 1, time.time(), old[4]))
        self.db.commit()

    def complete(self, exercise_id):
        old = self.get(exercise_id)
        self.db.execute("""INSERT INTO progress(exercise_id,code,status,attempts,updated,completed)
            VALUES(?,?,?,?,?,1) ON CONFLICT(exercise_id) DO UPDATE SET
            status='completed', completed=1, updated=excluded.updated""",
            (exercise_id, old[0], "completed", old[2], time.time()))
        self.db.commit()

    def close_exercise(self, exercise_id):
        self.db.execute("DELETE FROM progress WHERE exercise_id=?", (exercise_id,))
        self.db.commit()

    def hide_recent(self, exercise_id):
        # Nur aus der Dashboard-Liste ausblenden; Code und Lernfortschritt bleiben erhalten.
        self.db.execute("INSERT OR IGNORE INTO hidden_recent(exercise_id) VALUES(?)", (exercise_id,))
        self.db.commit()

    def show_recent(self, exercise_id):
        self.db.execute("DELETE FROM hidden_recent WHERE exercise_id=?", (exercise_id,))
        self.db.commit()

    def is_recent_hidden(self, exercise_id):
        return self.db.execute(
            "SELECT 1 FROM hidden_recent WHERE exercise_id=?", (exercise_id,)
        ).fetchone() is not None

    def uncomplete(self, exercise_id):
        # Vollständig auf "nie begonnen" zurücksetzen:
        # Code, Versuche, Abschlussstatus und Zeitstempel werden entfernt.
        # Der Eintrag verschwindet dadurch aus "Weiterlernen" und "Zuletzt bearbeitet".
        self.db.execute(
            "DELETE FROM progress WHERE exercise_id=?",
            (exercise_id,)
        )
        self.db.execute(
            "DELETE FROM hidden_recent WHERE exercise_id=?",
            (exercise_id,)
        )
        self.db.commit()

    def all_progress(self):
        return {row[0]: row[1:] for row in self.db.execute(
            "SELECT exercise_id,status,attempts,updated,completed FROM progress"
        ).fetchall()}

    def setting(self, key, default=""):
        row = self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def set_setting(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value))
        self.db.commit()


class PythonLernstudio:
    def __init__(self, root):
        self.root = root
        self.store = Store()
        self.current = None
        self.current_mode = "exercise"
        self.tutorial_index = 0
        self.run_token = 0
        self.running_process = None
        # Bereits vorbereitete Pakete dauerhaft speichern, damit die
        # Installationsabfrage nicht bei jedem Programmstart erneut erscheint.
        self.prepared_packages = set()
        if self.store.setting("prepared_package_cryptography", "0") == "1":
            self.prepared_packages.add("cryptography")
        self._encryption_install_running = False
        self.process_lock = threading.Lock()
        self.autosave_job = None
        self.catalog_wheel_bindings = []
        self.root.title(APP_NAME)
        if ICON_PATH.is_file():
            try:
                self.root.iconbitmap(default=str(ICON_PATH))
            except tk.TclError:
                pass
        self.dashboard_logo_image = None
        self.root.geometry("1440x900")
        self.root.minsize(1120, 720)
        self.root.configure(bg=BG)
        self._configure_style()
        self._build_shell()
        self.show_dashboard()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Panel.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 23))
        style.configure("Section.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 14))
        style.configure("CardTitle.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI Semibold", 12))
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 10), padding=(14, 9),
                        background=ACCENT, foreground="#080808", borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#ffc16e")])
        style.configure("Dx.TNotebook", background=BG, borderwidth=0)
        style.configure("Dx.TNotebook.Tab", background=PANEL2, foreground=TEXT,
                        padding=(14, 7), borderwidth=0)
        style.map("Dx.TNotebook.Tab",
                  background=[("selected", "#ff7900"), ("active", "#332014")],
                  foreground=[("selected", "#080808"), ("active", "#ffbd70")])
        style.configure("Dark.TButton", font=("Segoe UI", 9), padding=(10, 7),
                        background=PANEL2, foreground=TEXT, borderwidth=0)
        style.map("Dark.TButton", background=[("active", "#49301a")])
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT,
                        rowheight=30, borderwidth=0, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background=PANEL2, foreground=MUTED,
                        font=("Segoe UI Semibold", 9), relief="flat")
        style.map("Treeview", background=[("selected", "#304a70")])
        style.configure("TProgressbar", troughcolor=PANEL2, background=GREEN, borderwidth=0)

        # Einheitliche dunkle Scrollleisten im DxPyGuide-Farbschema.
        # Gilt für vertikale und horizontale ttk.Scrollbar-Widgets.
        style.configure(
            "TScrollbar",
            background="#3a2a1d",
            troughcolor="#111111",
            bordercolor="#111111",
            lightcolor="#3a2a1d",
            darkcolor="#3a2a1d",
            arrowcolor="#e6a04b",
            relief="flat",
            gripcount=0,
            arrowsize=12
        )
        style.map(
            "TScrollbar",
            background=[
                ("active", "#b86a22"),
                ("pressed", "#d88735"),
                ("!disabled", "#3a2a1d")
            ],
            arrowcolor=[
                ("active", "#ffd08a"),
                ("pressed", "#fff0d5")
            ]
        )

    def _build_shell(self):
        self.shell = tk.Frame(self.root, bg=BG)
        self.shell.pack(fill="both", expand=True)
        self.sidebar = tk.Frame(self.shell, bg="#080808", width=225)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        # Markenlogo oben links in der Seitenleiste statt der bisherigen Textzeile.
        self.sidebar_logo_image = None
        if LOGO_PATH.is_file():
            try:
                sidebar_logo = tk.PhotoImage(file=str(LOGO_PATH))
                scale = max(1, math.ceil(max(sidebar_logo.width(), sidebar_logo.height()) / 176))
                if scale > 1:
                    sidebar_logo = sidebar_logo.subsample(scale, scale)
                self.sidebar_logo_image = sidebar_logo
                tk.Label(self.sidebar, image=self.sidebar_logo_image,
                         bg="#080808", bd=0).pack(anchor="center", padx=12, pady=(12, 18))
            except tk.TclError:
                self.sidebar_logo_image = None
        self._nav_button("Dashboard", self.show_dashboard)
        self._nav_button("Tutorial-Reihe", self.start_tutorial)
        self._nav_button("Alle Übungen", self.show_exercise_catalog)
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=18, pady=22)
        tk.Label(self.sidebar, text="LERNFORTSCHRITT", bg="#080808", fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=22, pady=(0, 8))
        self.side_progress = tk.Label(self.sidebar, text="", bg="#080808", fg=GREEN,
                                      font=("Segoe UI Semibold", 11))
        self.side_progress.pack(anchor="w", padx=22)
        tk.Label(self.sidebar, text="Lokale Speicherung aktiv\nFortschritt bleibt erhalten.",
                 bg="#080808", fg=MUTED, justify="left", font=("Segoe UI", 8)).pack(
                     side="bottom", anchor="w", padx=22, pady=22)
        # Hauptbereich rechts neben der Seitenleiste initialisieren.
        self.main = tk.Frame(self.shell, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)
        self._update_sidebar()

    def _nav_button(self, text, command):
        b = tk.Button(self.sidebar, text="   " + text, command=command, anchor="w",
                      bg="#080808", fg="#e8d3b8", activebackground="#382617",
                      activeforeground="#ffd18a", relief="flat", bd=0,
                      font=("Segoe UI", 10), padx=12, pady=11, cursor="hand2")
        b.pack(fill="x", padx=12, pady=2)

    def _update_sidebar(self):
        p = self.store.all_progress()
        done = sum(1 for e in PRACTICE_EXERCISES
                   if e["id"] in p and (p[e["id"]][0] == "completed" or p[e["id"]][3]))
        self.side_progress.config(text=f"{done} / {len(PRACTICE_EXERCISES)} erledigt")

    def clear_main(self):
        # Globale Mausrad-Bindings des Übungskatalogs sauber entfernen.
        for sequence, func_id in self.catalog_wheel_bindings:
            try:
                # Tkinter 3.12: unbind_all() akzeptiert keine Binding-ID.
                # _unbind() entfernt gezielt genau das zuvor registrierte Binding.
                self.root._unbind(("bind", "all", sequence), func_id)
            except tk.TclError:
                pass
        self.catalog_wheel_bindings.clear()
        if self.autosave_job:
            self.root.after_cancel(self.autosave_job)
            self.autosave_job = None
        if self.current:
            self._save_current()
        for w in self.main.winfo_children():
            w.destroy()

    def header(self, eyebrow, title, subtitle=""):
        top = tk.Frame(self.main, bg=BG)
        top.pack(fill="x", padx=34, pady=(28, 18))
        tk.Label(top, text=eyebrow.upper(), bg=BG, fg=ACCENT,
                 font=("Segoe UI Semibold", 8)).pack(anchor="w")
        tk.Label(top, text=title, bg=BG, fg=TEXT,
                 font=("Segoe UI Semibold", 23)).pack(anchor="w", pady=(4, 2))
        if subtitle:
            tk.Label(top, text=subtitle, bg=BG, fg=MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w")

    def card(self, parent, padx=18, pady=16):
        f = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        f.pack_propagate(True)
        return f

    def show_dashboard(self):
        self._stop_running_process()
        self.clear_main()
        self.current = None
        dashboard_header = tk.Frame(self.main, bg=BG)
        dashboard_header.pack(fill="x", padx=34, pady=(22, 18))
        header_text = tk.Frame(dashboard_header, bg=BG)
        header_text.pack(side="left", fill="x", expand=True, anchor="n")
        tk.Label(header_text, text="DEIN LERNBEREICH", bg=BG, fg=ACCENT,
                 font=("Segoe UI Semibold", 8)).pack(anchor="w")
        tk.Label(header_text, text="Willkommen zurück.", bg=BG, fg=TEXT,
                 font=("Segoe UI Semibold", 23)).pack(anchor="w", pady=(4, 2))
        tk.Label(header_text, text="Lerne Python in deinem eigenen Tempo – Lektion für Lektion.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w")
        p = self.store.all_progress()
        completed = sum(1 for e in PRACTICE_EXERCISES
                        if e["id"] in p and (p[e["id"]][0] == "completed" or p[e["id"]][3]))
        started = sum(1 for e in PRACTICE_EXERCISES
                      if e["id"] in p and p[e["id"]][0] == "in_progress" and not p[e["id"]][3])
        stats = tk.Frame(self.main, bg=BG)
        stats.pack(fill="x", padx=34, pady=(0, 20))
        for label, value, note in [
            ("ÜBUNGEN", str(len(PRACTICE_EXERCISES)), "inklusive Erweiterungen"),
            ("ABGESCHLOSSEN", str(completed), "Lernziele erreicht"),
            ("IN ARBEIT", str(started), "automatisch gespeichert"),
        ]:
            box = tk.Frame(stats, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
            box.pack(side="left", fill="x", expand=True, padx=(0, 12), ipady=12)
            tk.Label(box, text=label, bg=PANEL, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(10, 2))
            tk.Label(box, text=value, bg=PANEL, fg=TEXT, font=("Segoe UI Semibold", 22)).pack(anchor="w", padx=16)
            tk.Label(box, text=note, bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=16, pady=(0, 8))
        tutorial = tk.Frame(self.main, bg="#17100a", highlightbackground="#9b4a00", highlightthickness=1)
        tutorial.pack(fill="x", padx=34, pady=(0, 22))
        left = tk.Frame(tutorial, bg="#17100a")
        left.pack(side="left", fill="both", expand=True, padx=22, pady=18)
        tk.Label(left, text="DEIN LERNPFAD", bg="#17100a", fg="#ff8a00",
                 font=("Segoe UI Semibold", 8)).pack(anchor="w")
        tk.Label(left, text="Tutorial-Reihe", bg="#17100a", fg="white",
                 font=("Segoe UI Semibold", 18)).pack(anchor="w", pady=(4, 3))
        tk.Label(left, text="Alle Themen in einer sinnvollen Reihenfolge – mit Aufgaben, Hinweisen und Musterlösungen.",
                 bg="#17100a", fg="#d6c2ad", font=("Segoe UI", 9), wraplength=650,
                 justify="left").pack(anchor="w")
        ttk.Button(tutorial, text="Tutorial starten  →", style="Accent.TButton",
                   command=self.start_tutorial).pack(side="right", padx=22, pady=22)
        self._section_label(self.main, "WEITERLERNEN")
        resume = [e for e in EXERCISES if not e.get("information_only") and e["id"] in p and p[e["id"]][0] == "in_progress" and not p[e["id"]][3]]
        if resume:
            wrap = tk.Frame(self.main, bg=BG)
            wrap.pack(fill="x", padx=34, pady=(0, 18))
            for e in resume[:4]:
                self._exercise_row(wrap, e, "Fortsetzen")
        else:
            tk.Label(self.main, text="Noch keine angefangenen Übungen. Wähle eine Lektion aus dem Katalog.",
                     bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=34, pady=(0, 18))
        self._section_label(self.main, "ZULETZT BEARBEITET")
        recent = sorted(
            [e for e in EXERCISES if not e.get("information_only") and e["id"] in p and not self.store.is_recent_hidden(e["id"])],
            key=lambda e: p[e["id"]][2], reverse=True
        )
        if recent:
            wrap = tk.Frame(self.main, bg=BG)
            wrap.pack(fill="x", padx=34, pady=(0, 20))
            for e in recent[:5]:
                self._exercise_row(wrap, e, "Öffnen", compact=True)
        else:
            tk.Label(self.main, text="Dein Verlauf erscheint hier, sobald du eine Übung öffnest.",
                     bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=34)

    def _section_label(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=MUTED, font=("Segoe UI Semibold", 8)).pack(anchor="w", padx=34, pady=(4, 9))

    def _hide_recent_from_dashboard(self, exercise_id):
        self.store.hide_recent(exercise_id)
        self.show_dashboard()

    def _uncomplete_from_dashboard(self, exercise_id):
        self.store.uncomplete(exercise_id)
        self.show_dashboard()

    def _exercise_row(self, parent, e, action, compact=False):
        p = self.store.get(e["id"])
        row = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", pady=3)
        status = "Abgeschlossen" if p[4] else ("In Arbeit" if p[1] == "in_progress" else "Begonnen")
        color = GREEN if p[4] else (ORANGE if p[1] == "in_progress" else MUTED)
        tk.Label(row, text=e["title"], bg=PANEL, fg=TEXT, font=("Segoe UI Semibold", 10)).pack(side="left", padx=14, pady=10)
        tk.Label(row, text=status, bg=PANEL, fg=color, font=("Segoe UI", 8)).pack(side="left", padx=10)
        ttk.Button(row, text=action, style="Dark.TButton",
                   command=lambda x=e: self.open_exercise(x)).pack(side="right", padx=10, pady=5)
        if compact:
            if p[4]:
                ttk.Button(row, text="Auf Anfang zurücksetzen", style="Dark.TButton",
                           command=lambda x=e: self._uncomplete_from_dashboard(x["id"])).pack(
                               side="right", padx=4, pady=5)
            ttk.Button(row, text="Aus Verlauf entfernen", style="Dark.TButton",
                       command=lambda x=e: self._hide_recent_from_dashboard(x["id"])).pack(
                           side="right", padx=4, pady=5)
        if not compact:
            tk.Label(row, text=f'{e["category"]}  ·  {e["duration"]}', bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 8)).pack(side="left", padx=6)

    def show_exercise_catalog(self):
        self.clear_main()
        self.current = None
        self.header("Bibliothek", "Alle Übungen", "Wähle ein Thema. Dein Code wird automatisch gespeichert.")
        canvas = tk.Canvas(self.main, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(self.main, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=canvas.winfo_width() or 1000)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(34, 0))
        scroll.pack(side="right", fill="y", padx=(0, 20))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(1, width=e.width))

        # Mausrad global abfangen: Tkinter-Events steigen nicht automatisch
        # von Labels/Frames zum Canvas hoch. Deshalb funktionierte das alte
        # Widget-für-Widget-Binding abhängig von der Mausposition.
        wheel_state = {"remainder": 0.0, "animation": None}

        def scroll_to(target, steps=5):
            target = max(0.0, min(1.0, target))
            start_pos = canvas.yview()[0]
            distance = target - start_pos
            if abs(distance) < 0.0001:
                return
            if wheel_state["animation"] is not None:
                try:
                    self.root.after_cancel(wheel_state["animation"])
                except tk.TclError:
                    pass

            frame = {"n": 0}
            def animate():
                frame["n"] += 1
                t = min(1.0, frame["n"] / steps)
                # Ease-out: startet zügig und bremst weich ab.
                eased = 1 - (1 - t) ** 3
                canvas.yview_moveto(start_pos + distance * eased)
                if t < 1.0:
                    wheel_state["animation"] = self.root.after(10, animate)
                else:
                    wheel_state["animation"] = None
            animate()

        def catalog_wheel(event):
            if getattr(event, "num", None) == 4:
                delta = -120
            elif getattr(event, "num", None) == 5:
                delta = 120
            else:
                delta = -getattr(event, "delta", 0)

            # Auch kleine Trackpad-/High-Resolution-Wheel-Ereignisse sammeln,
            # statt sie durch int(delta / 120) zu verlieren.
            wheel_state["remainder"] += delta
            notches = wheel_state["remainder"] / 120.0
            if abs(notches) >= 0.01:
                wheel_state["remainder"] = 0.0
                first, last = canvas.yview()
                content_height = max(1, canvas.bbox("all")[3] if canvas.bbox("all") else 1)
                viewport_height = max(1, canvas.winfo_height())
                fraction_per_unit = 32.0 / content_height
                # Drei Zeilen je Mausrad-Rastung, weich animiert.
                target = first + notches * 3.0 * fraction_per_unit
                scroll_to(target, steps=5)
            return "break"

        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            func_id = self.root.bind_all(sequence, catalog_wheel, add="+")
            self.catalog_wheel_bindings.append((sequence, func_id))

        groups = {}
        for e in EXERCISES:
            groups.setdefault(e["category"], []).append(e)
        for category, exercises in groups.items():
            tk.Label(inner, text=category.upper(), bg=BG, fg=ACCENT,
                     font=("Segoe UI Semibold", 8)).pack(anchor="w", pady=(14, 7))
            for e in exercises:
                self._exercise_row(inner, e, "Übung öffnen")

    def open_exercise(self, exercise, tutorial=False):
        self._stop_running_process()
        self.clear_main()
        if isinstance(exercise, str):
            exercise = next(e for e in EXERCISES if e["id"] == exercise)
        self.current = exercise
        self.store.show_recent(exercise["id"])
        self.current_mode = "tutorial" if tutorial else "exercise"
        p = self.store.get(exercise["id"])
        # Migriere ausschließlich unveränderte alte Vorlagen aus v1.24.
        # Individuell geschriebener Nutzercode bleibt unangetastet.
        legacy_starters = {
            "hello": "# Deine erste Python-Zeile\n",
            "person": "name = None\nalter = None\nlieblingsspiel = None\n\n# Frage die drei Werte ab\n\n# Gib eine Zusammenfassung aus\n",
            "types": "# Erstelle vier Variablen mit unterschiedlichen Datentypen\n\n# Gib Wert und Typ aus\n",
            "operators": "alter = int(input('Alter: '))\n\n# Prüfe beide Grenzen\n",
            "age": 'alter = int(input("Wie alt bist du? "))\n\n# Prüfe das Alter mit if, elif und else\n',
            "login": 'benutzername = "test"\npasswort = "python"\n\n# Frage die Zugangsdaten ab\n\n# Prüfe beide Angaben\n',
            "loops": "# Gib die Zahlen 1 bis 10 aus\n",
            "while": "zahl = 1\n\n# Schreibe die while-Schleife\n",
            "functions": "# Definiere hier deine Funktion\n\n\n# Rufe die Funktion auf\n",
            "lists": 'namen = ["Anna", "Ben", "Mia"]\n\n# Begrüße jeden Namen\n',
            "list-input": "namen = []\n\n# Frage drei Namen ab und speichere sie\n\n# Gib die fertige Liste aus\n",
            "append": 'def namen_sammeln():\n    namen = []\n    # Frage drei Namen ab und füge sie hinzu\n    \n    # Gib die Liste zurück\n    \n\nergebnis = namen_sammeln()\nprint(ergebnis)\n',
            "dict": "# Erstelle ein Dictionary person\n\n# Gib zwei Werte aus\n",
            "tuples": "# Erstelle ein Tupel und ein Set\n\n# Gib beide aus\n",
            "comprehension": "# Erzeuge hier die Liste mit List Comprehension\n",
            "exceptions": "try:\n    # Zahl abfragen und umwandeln\n    pass\nexcept ValueError:\n    # Fehlermeldung ausgeben\n    pass\n",
            "files": "# Schreibe eine Textdatei\n\n# Lies die Datei wieder aus\n",
            "modules": "# Importiere das benötigte Modul\n\n# Simuliere einen Würfelwurf\n",
            "oop": "# Erstelle die Klasse Person\n\n# Erzeuge ein Objekt und gib den Namen aus\n",
            "testing": "# Schreibe die Funktion verdoppeln\n\n# Prüfe das Ergebnis mit assert\n",
        }
        old_template = legacy_starters.get(exercise["id"])
        if old_template is not None and p[0].strip() == old_template.strip():
            self.store.save_code(exercise["id"], exercise.get("starter", ""))
            p = self.store.get(exercise["id"])
        self.header(f'{exercise["category"]}  /  {exercise["level"]}', exercise["title"],
                    f'{exercise["duration"]}  ·  {", ".join(exercise["concepts"])}')
        # Footer zuerst packen, damit die Aktionsbuttons immer Platz behalten.
        # Danach füllt der expandierende Arbeitsbereich nur den verbleibenden Raum.
        footer = tk.Frame(self.main, bg=BG)
        footer.pack(side="bottom", fill="x", padx=34, pady=(0, 18))
        ttk.Button(footer, text="← Dashboard", style="Dark.TButton",
                   command=self.show_dashboard).pack(side="left")
        ttk.Button(footer, text="Übung schließen", style="Dark.TButton",
                   command=lambda: self.close_exercise(exercise)).pack(side="right", padx=8)
        if tutorial:
            ttk.Button(footer, text="Nächster Tutorial-Schritt  →", style="Dark.TButton",
                       command=self.next_tutorial).pack(side="right", padx=8)

        body = tk.Frame(self.main, bg=BG)
        body.pack(side="top", fill="both", expand=True, padx=34, pady=(0, 12))
        body.columnconfigure(0, weight=4)
        body.columnconfigure(1, weight=6)
        body.rowconfigure(0, weight=1)
        learn = tk.Frame(body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        learn.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        editor_panel = tk.Frame(body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        editor_panel.grid(row=0, column=1, sticky="nsew")
        self._build_lesson_panel(learn, exercise)
        if exercise.get("information_only"):
            self._build_intro_panel(editor_panel)
        else:
            self._build_editor_panel(editor_panel, exercise, p[0])

    def _build_lesson_panel(self, parent, e):
        # Kompakte Aufgabenansicht: Lernziel, Aufgabenstellung und Beispiele.
        # Die fachlichen Erklärungen stehen gesammelt im Tab "Beispiele & Grundlagen".
        canvas = tk.Canvas(parent, bg=PANEL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        content = tk.Frame(canvas, bg=PANEL)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def update_region(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(window_id, width=canvas.winfo_width())

        content.bind("<Configure>", update_region)
        canvas.bind("<Configure>", update_region)

        tk.Label(content, text="LERNZIEL", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=20, pady=(22, 8))
        goal = tk.Label(content, text=e["goal"], bg=PANEL, fg=TEXT,
                        wraplength=380, justify="left",
                        font=("Segoe UI Semibold", 12))
        goal.pack(anchor="w", fill="x", padx=20, pady=(0, 4))

        task = None
        if e.get("information_only"):
            tk.Label(content, text="WICHTIG", bg=PANEL, fg="#ff9a24",
                     font=("Segoe UI Semibold", 11)).pack(anchor="w", padx=20, pady=(30, 9))
            tk.Label(content, text=e["task"], bg=PANEL, fg=TEXT,
                     wraplength=380, justify="left",
                     font=("Segoe UI", 10)).pack(anchor="w", fill="x", padx=20, pady=(0, 18))
        else:
            tk.Label(content, text="DEINE AUFGABE", bg=PANEL, fg="#ff9a24",
                     font=("Segoe UI Semibold", 11)).pack(anchor="w", padx=20, pady=(30, 9))
            task = tk.Label(content, text=e["task"], bg=PANEL, fg=TEXT,
                            wraplength=380, justify="left", font=("Segoe UI", 10))
            task.pack(anchor="w", fill="x", padx=20, pady=(0, 18))

            ttk.Button(content, text="Beispiele anzeigen  →", style="Dark.TButton",
                       command=self.show_examples_tab).pack(anchor="w", padx=20, pady=(0, 7))
            ttk.Button(content, text="Lösung anzeigen  →", style="Dark.TButton",
                       command=self.show_solution_window).pack(anchor="w", padx=20, pady=(0, 12))

        # Zeilenumbruch passt sich der tatsächlich verfügbaren Panelbreite an.
        def resize_text(event):
            width = max(180, event.width - 48)
            goal.configure(wraplength=width)
            if task is not None:
                task.configure(wraplength=width)

        canvas.bind("<Configure>", lambda ev: (update_region(), resize_text(ev)))

        def wheel(event):
            if getattr(event, "delta", 0):
                canvas.yview_scroll(int(-event.delta / 120), "units")
            elif getattr(event, "num", None) == 4:
                canvas.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(1, "units")
            return "break"

        def bind_wheel_tree(widget):
            widget.bind("<MouseWheel>", wheel)
            widget.bind("<Button-4>", wheel)
            widget.bind("<Button-5>", wheel)
            for child in widget.winfo_children():
                bind_wheel_tree(child)

        bind_wheel_tree(canvas)
        bind_wheel_tree(content)

    def _subheading(self, parent, text):
        tk.Label(parent, text=text, bg=PANEL, fg=TEXT,
                 font=("Segoe UI Semibold", 10)).pack(anchor="w", padx=18, pady=(16, 6))

    def solution_explanation(self, e):
        return "Musterlösung:\n\n" + e["solution"] + "\n\nWarum funktioniert das?\n" + e["explanation"]

    def _build_intro_panel(self, parent):
        """Zeigt die erste Einführung ohne Editor, Aufgabe oder Prüfknopf."""
        heading = tk.Frame(parent, bg=PANEL2)
        heading.pack(fill="x")
        tk.Label(heading, text="  GRUNDLAGEN: AUFBAU EINES PYTHON-PROGRAMMS",
                 bg=PANEL2, fg=TEXT,
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", pady=10)

        canvas = tk.Canvas(parent, bg=PANEL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        content = tk.Frame(canvas, bg=PANEL)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        wrapped_labels = []

        def refresh(_event=None):
            # Die Textbreite richtet sich nach der tatsächlich verfügbaren
            # Fensterbreite. Ein fester wraplength kann auf kleineren
            # Auflösungen/DPI-Skalierungen links abgeschnitten wirken.
            available_width = max(220, canvas.winfo_width() - 58)
            canvas.itemconfigure(window_id, width=max(220, canvas.winfo_width()))
            for label in wrapped_labels:
                label.configure(wraplength=available_width, anchor="w")
            canvas.configure(scrollregion=canvas.bbox("all"))

        content.bind("<Configure>", refresh)
        canvas.bind("<Configure>", refresh)

        tk.Label(content, text="Ein Python-Programm besteht aus Anweisungen",
                 bg=PANEL, fg=ACCENT, font=("Segoe UI Semibold", 12)).pack(
                     anchor="w", padx=14, pady=(8, 5))
        intro_text = tk.Label(
            content,
            text="Python führt Anweisungen grundsätzlich von oben nach unten aus. Jede Codezeile enthält beispielsweise einen Befehl, eine Zuweisung oder den Beginn eines zusammengehörigen Codeblocks.",
            bg=PANEL, fg=TEXT, wraplength=600, justify="left", anchor="w",
            font=("Segoe UI", 9)
        )
        intro_text.pack(anchor="w", fill="x", padx=14, pady=(0, 12))
        wrapped_labels.append(intro_text)

        # Die Informationseinheit besitzt ebenfalls eine aufgabenbezogene Grafik.
        # Der Dateiname folgt der Aufgaben-ID: guide_python-basics.png.
        diagram_path = GUIDE_DIAGRAM_DIR / "guide_python-basics.png"
        diagram_card = tk.Frame(content, bg="#090909", highlightthickness=1,
                                highlightbackground="#68401f")
        diagram_card.pack(fill="x", padx=12, pady=(0, 12))
        tk.Label(diagram_card, text="VISUELLE ÜBERSICHT: CODEAUFBAU UND EINRÜCKUNG",
                 bg="#090909", fg="#ff9a24",
                 font=("Segoe UI Semibold", 9)).pack(
                     anchor="w", padx=12, pady=(9, 5))
        try:
            from PIL import Image, ImageTk
            source_image = Image.open(diagram_path).convert("RGB")
            preview_image = source_image.copy()
            preview_image.thumbnail((max(360, self.root.winfo_width() - 900), 430),
                                    Image.Resampling.LANCZOS)
            diagram_preview = ImageTk.PhotoImage(preview_image, master=diagram_card)
            if not hasattr(self, "_guide_diagram_refs"):
                self._guide_diagram_refs = []
            self._guide_diagram_refs.append((source_image, diagram_preview))
            diagram_label = tk.Label(diagram_card, image=diagram_preview,
                                     bg="#090909", bd=0, highlightthickness=0,
                                     cursor="hand2")
            diagram_label.pack(anchor="center", padx=8, pady=(3, 6))
            diagram_label.bind("<Button-1>",
                lambda _event, image_path=diagram_path: self._open_diagram_fullscreen(image_path))
            tk.Label(diagram_card, text="Grafik anklicken zum Vergrößern",
                     bg="#090909", fg="#b99a79",
                     font=("Segoe UI", 8)).pack(anchor="center", pady=(0, 7))
        except Exception as exc:
            tk.Label(diagram_card,
                     text=f"Die Erklärgrafik fehlt oder konnte nicht geladen werden:\n{diagram_path.name}\n{exc}",
                     bg="#090909", fg="#ffbd70", justify="left",
                     font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=8)

        code = (
            '# Eine Funktion wird zuerst definiert\n'
            'def begruessung(name):\n'
            '    nachricht = f"Hallo {name}!"\n'
            '    print(nachricht)\n'
            '\n'
            '# Danach wird die Funktion aufgerufen\n'
            'begruessung("Mia")'
        )
        sample = tk.Frame(content, bg="#090909", highlightthickness=1,
                          highlightbackground="#68401f")
        sample.pack(fill="x", padx=12, pady=(0, 12))
        tk.Label(sample, text="BEISPIELCODE", bg="#090909", fg="#ff9a24",
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=12, pady=(9, 4))
        code_box = tk.Text(sample, height=7, bg="#111111", fg="#ffbd70",
                           relief="flat", padx=10, pady=8, wrap="none",
                           font=("Consolas", 10), borderwidth=0)
        code_box.pack(fill="x", padx=10, pady=(0, 10))
        code_box.insert("1.0", code)
        code_box.configure(state="disabled")

        sections = [
            ("1. Kommentare – Hinweise für Menschen",
             "Eine Zeile, die mit # beginnt, ist ein Kommentar. Python führt diesen Text nicht aus. Kommentare helfen dabei, Code zu erklären oder Abschnitte zu kennzeichnen."),
            ("2. Funktionen – wiederverwendbare Abläufe",
             "Eine Funktion bündelt mehrere Anweisungen unter einem Namen. Mit def beginnt ihre Definition. Die Funktion wird dadurch zunächst nur festgelegt – ausgeführt wird sie erst, wenn du sie später aufrufst."),
            ("3. Parameter und Argumente",
             'name in def begruessung(name): ist ein Parameter. Er ist ein Platzhalter für einen Wert. Beim Aufruf begruessung("Mia") wird Mia als Argument übergeben und steht innerhalb der Funktion unter dem Namen name zur Verfügung.'),
            ("4. Einrückungen – zeigen zusammengehörigen Code",
             "Die eingerückten Zeilen unter def gehören zum Funktionsblock. In Python werden dafür üblicherweise vier Leerzeichen verwendet. Alle Anweisungen desselben Blocks beginnen an derselben Position. Fehlt die Einrückung oder ist sie uneinheitlich, kann Python den Code nicht richtig zuordnen."),
            ("5. Variablen und Zuweisungen",
             "nachricht = ... speichert einen Wert unter dem Namen nachricht. Das Gleichheitszeichen = weist den Wert zu; es ist hier kein Vergleich. Später kann der gespeicherte Wert über den Variablennamen verwendet werden."),
            ("6. Funktionen aufrufen und Code ausführen",
             "print(nachricht) ruft die Funktion print() auf und zeigt den gespeicherten Text an. begruessung(\"Mia\") startet anschließend die selbst definierte Funktion. Python arbeitet die eingerückten Anweisungen dann der Reihe nach ab."),
            ("7. Klammern, Doppelpunkt und Text",
             "Runde Klammern () stehen bei Funktionsdefinitionen und Funktionsaufrufen. Der Doppelpunkt : kündigt den folgenden eingerückten Block an. Textwerte stehen in Anführungszeichen. Das f vor einem Text kennzeichnet einen F-String: Damit können Werte wie name direkt in den Text eingesetzt werden.")
        ]
        for title, description in sections:
            card = tk.Frame(content, bg="#090909", highlightthickness=1,
                            highlightbackground="#3a2818")
            card.pack(fill="x", padx=12, pady=5)
            tk.Label(card, text=title, bg="#090909", fg="#ff9a24",
                     font=("Segoe UI Semibold", 9)).pack(
                         anchor="w", padx=12, pady=(9, 3))
            description_label = tk.Label(
                card, text=description, bg="#090909", fg="#ded4c8",
                wraplength=600, justify="left", anchor="w",
                font=("Segoe UI", 9)
            )
            description_label.pack(anchor="w", fill="x", padx=12, pady=(0, 9))
            wrapped_labels.append(description_label)

        reminder = tk.Label(
            content,
            text="Merke: def beschreibt eine Funktion. Die Einrückung zeigt, welche Zeilen zu ihr gehören. Der Funktionsaufruf startet den Ablauf.",
            bg=PANEL, fg="#ffbd70", wraplength=600, justify="left",
            anchor="w", font=("Segoe UI Semibold", 9)
        )
        reminder.pack(anchor="w", fill="x", padx=14, pady=(8, 14))
        wrapped_labels.append(reminder)

        def wheel(event):
            if getattr(event, "delta", 0):
                canvas.yview_scroll(int(-event.delta / 120), "units")
            elif getattr(event, "num", None) == 4:
                canvas.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(1, "units")
            return "break"

        def bind_wheel_tree(widget):
            # Mausrad-Ereignisse kommen häufig beim Label, Frame oder
            # Codefeld unter dem Mauszeiger an – nicht beim Canvas selbst.
            # Deshalb wird das Scrollen an alle Inhalte der Einführung gebunden.
            widget.bind("<MouseWheel>", wheel)
            widget.bind("<Button-4>", wheel)
            widget.bind("<Button-5>", wheel)
            for child in widget.winfo_children():
                bind_wheel_tree(child)

        bind_wheel_tree(canvas)
        bind_wheel_tree(content)

        # Auch nachträglich hinzugefügte bzw. neu angeordnete Inhalte
        # aktualisieren den scrollbaren Bereich zuverlässig.
        content.bind("<Configure>", lambda _event: canvas.configure(
            scrollregion=canvas.bbox("all")
        ))

    def _build_editor_panel(self, parent, e, saved_code):
        bar = tk.Frame(parent, bg=PANEL2)
        bar.pack(fill="x")
        tk.Label(bar, text="  CODE-EDITOR", bg=PANEL2, fg=TEXT,
                 font=("Segoe UI Semibold", 9)).pack(side="left", pady=10)
        self.run_button = ttk.Button(bar, text="▶ Ausführen", style="Accent.TButton",
                                     command=self.run_code)
        self.run_button.pack(side="right", padx=9, pady=6)
        ttk.Button(bar, text="Antwort prüfen", style="Dark.TButton",
                   command=self.check_answer).pack(side="right", padx=2, pady=6)
        ttk.Button(bar, text="Code zurücksetzen", style="Dark.TButton",
                   command=self.reset_code).pack(side="right", pady=6)
        # Editor und Lernbeispiele liegen in getrennten Tabs, damit die linke
        # Aufgabenbeschreibung kompakt bleibt.
        self.editor_notebook = ttk.Notebook(parent, style="Dx.TNotebook")
        self.editor_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        editor_tab = tk.Frame(self.editor_notebook, bg=EDITOR_BG)
        examples_tab = tk.Frame(self.editor_notebook, bg=PANEL)
        self.editor_notebook.add(editor_tab, text="Code schreiben")
        self.editor_notebook.add(examples_tab, text="Beispiele & Grundlagen")

        editor_wrap = tk.Frame(editor_tab, bg=EDITOR_BG)
        editor_wrap.pack(fill="both", expand=True)
        editor_wrap.grid_rowconfigure(0, weight=1)
        editor_wrap.grid_columnconfigure(1, weight=1)
        self.line_numbers = tk.Text(editor_wrap, width=4, padx=7, pady=10, bg="#111a27",
                                    fg="#9a785a", state="disabled", relief="flat",
                                    font=("Consolas", 10), takefocus=0)
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        self.editor = tk.Text(editor_wrap, wrap="none", undo=True, bg=EDITOR_BG, fg="#f2e8dc",
                              insertbackground="white", selectbackground="#6b3500",
                              relief="flat", padx=10, pady=10, font=("Consolas", 10),
                              tabs=("4c",))
        self.editor.grid(row=0, column=1, sticky="nsew")
        # PyCharm-ähnliche Einrückungslinien werden in einer transparenten,
        # klickdurchlässigen Overlay-Ebene gezeichnet. Der eigentliche Quelltext
        # bleibt dadurch vollständig unverändert.
        # Die experimentelle transparente Overlay-Ebene ist deaktiviert.
        # Sie konnte unter Windows den Editor verdecken und Configure-Ereignisse
        # rekursiv auslösen. Der Editor bleibt dadurch zuverlässig bedienbar.
        self._indent_overlay = None
        self._indent_canvas = None
        self._indent_overlay_ready = False
        yscroll = ttk.Scrollbar(editor_wrap, orient="vertical", command=self._editor_yview)
        yscroll.grid(row=0, column=2, sticky="ns")
        xscroll = ttk.Scrollbar(editor_wrap, orient="horizontal", command=self.editor.xview)
        xscroll.grid(row=1, column=1, sticky="ew")
        self.editor.configure(
            yscrollcommand=lambda a, b: (yscroll.set(a, b), self._sync_lines()),
            xscrollcommand=xscroll.set
        )
        code = saved_code if saved_code else e.get("starter", "# Schreibe deinen Code hier\n")
        self.editor.insert("1.0", code)
        self.editor.bind("<KeyRelease>", self._on_editor_change)
        self.editor.bind("<MouseWheel>", lambda ev: self._sync_lines())
        self.editor.bind("<Configure>", lambda ev: self._sync_lines())
        self.editor.bind("<ButtonRelease-1>", lambda ev: self._sync_lines())
        self.editor.bind("<Tab>", self._editor_tab)
        self.editor.bind("<Shift-Tab>", self._editor_shift_tab)
        self.editor.bind("<Return>", self._autocomplete_enter)
        self.editor.bind("<Down>", self._autocomplete_move)
        self.editor.bind("<Up>", self._autocomplete_move)
        self.editor.bind("<Escape>", self._autocomplete_hide)
        self.editor.bind("<FocusOut>", self._autocomplete_focus_out)
        self.editor.bind("<Button-1>", self._editor_click_hide_autocomplete)
        self._autocomplete_popup = None
        self._autocomplete_list = None
        self._autocomplete_items = []
        self._sync_lines()

        self._build_concept_examples(examples_tab, e)

        output_head = tk.Frame(parent, bg=PANEL2)
        output_head.pack(fill="x", padx=10)
        tk.Label(output_head, text="  KONSOLE  ·  Ausgabe und Eingabe wie in einer Python-Konsole",
                 bg=PANEL2, fg=MUTED, font=("Segoe UI Semibold", 8)).pack(anchor="w", pady=7)
        self.output = tk.Text(parent, height=12, bg="#0b0907", fg="#ff9a24",
                              insertbackground="#f2e8dc", relief="flat", padx=12, pady=9,
                              font=("Consolas", 9), wrap="word", undo=False)
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.output.tag_configure("error", foreground="#ff8888")
        self.output.tag_configure("info", foreground="#8fb6ff")
        self.output.mark_set("console_input_start", "end-1c")
        self.output.bind("<Return>", self._console_enter)
        self.output.bind("<KeyPress>", self._console_key_guard)
        self.output.bind("<Button-1>", self._console_click_guard, add="+")
        self.output.tag_configure("error", foreground="#ff8888")
        self.output.tag_configure("info", foreground="#8fb6ff")

    def show_examples_tab(self):
        if hasattr(self, "editor_notebook") and self.editor_notebook.winfo_exists():
            self.editor_notebook.select(1)

    def _create_example_code_panel(self, parent, code, title="CODEBEISPIEL", max_lines=16):
        """Einheitliches, editorähnlich eingefärbtes Codefeld für Beispiele und Grundlagen."""
        import re
        shell = tk.Frame(parent, bg="#101820", highlightthickness=1,
                         highlightbackground="#3d5265")
        shell.pack(fill="x", padx=10, pady=(0, 8))
        tk.Label(shell, text=title, bg="#101820", fg="#9fb3c8",
                 font=("Segoe UI Semibold", 8)).pack(anchor="w", padx=9, pady=(6, 3))
        lines = code.splitlines() or [""]
        visible = min(max_lines, max(2, len(lines)))
        area = tk.Frame(shell, bg="#111820")
        area.pack(fill="x", padx=7, pady=(0, 7))
        area.grid_columnconfigure(0, weight=1)
        area.grid_rowconfigure(0, weight=1)
        code_box = tk.Text(area, height=visible, wrap="none", bg="#111820",
                           fg="#f2e8dc", insertbackground="#f2e8dc",
                           selectbackground="#31516b", relief="flat", bd=0,
                           padx=9, pady=7, font=("Consolas", 9), takefocus=0)
        code_box.grid(row=0, column=0, sticky="nsew")
        xbar = ttk.Scrollbar(area, orient="horizontal", command=code_box.xview)
        xbar.grid(row=1, column=0, sticky="ew")
        code_box.configure(xscrollcommand=xbar.set)
        if len(lines) > max_lines:
            ybar = ttk.Scrollbar(area, orient="vertical", command=code_box.yview)
            ybar.grid(row=0, column=1, sticky="ns")
            code_box.configure(yscrollcommand=ybar.set)
        code_box.insert("1.0", code)
        # Dieselbe Farbpalette wie im DxPyGuide-Editor.
        for tag, color in (("keyword", "#c792ea"), ("string", "#c3e88d"),
                           ("comment", "#718096"), ("number", "#f78c6c"),
                           ("function", "#82aaff"), ("self", "#89ddff"),
                           ("escape", "#ffb454")):
            code_box.tag_configure(tag, foreground=color)
        patterns = [
            (r'\b(def|class|if|elif|else|for|while|in|return|import|from|as|try|except|finally|with|pass|break|continue|and|or|not|is|lambda|True|False|None)\b', "keyword"),
            (r'\b(self)\b', "self"),
            (r'\b(print|input|range|len|type|int|str|float|list|dict|set|tuple|open|super)\b(?=\s*\()', "function"),
            (r'\b[A-Za-z_][A-Za-z0-9_]*(?=\s*\()', "function"),
            (r'\b\d+(?:\.\d+)?\b', "number"),
            (r'"(?:\\.|[^"\\])*"', "string"),
            (r"'(?:\\.|[^'\\])*'", "string"),
            (r'#.*', "comment"),
        ]
        for pattern, tag in patterns:
            for match in re.finditer(pattern, code, re.S if '"""' in pattern else 0):
                code_box.tag_add(tag, "1.0+%dc" % match.start(), "1.0+%dc" % match.end())
        code_box.configure(state="disabled")
        return shell

    def _open_diagram_fullscreen(self, image_path):
        """Zeigt eine Erklärgrafik groß im Programm und bietet einen X-Schließen-Button."""
        try:
            window = tk.Toplevel(self.root)
            window.title("Erklärgrafik")
            window.configure(bg="#080808")
            window.transient(self.root)
            window.attributes("-fullscreen", True)

            header = tk.Frame(window, bg="#111111", height=48)
            header.pack(side="top", fill="x")
            header.pack_propagate(False)
            tk.Label(
                header, text="ERKLÄRGRAFIK",
                bg="#111111", fg="#ff9a24",
                font=("Segoe UI Semibold", 10)
            ).pack(side="left", padx=18)
            close_button = tk.Button(
                header, text="×", command=window.destroy,
                bg="#2a1710", fg="#ffffff",
                activebackground="#a84320", activeforeground="#ffffff",
                relief="flat", bd=0, font=("Segoe UI", 20, "bold"),
                cursor="hand2", width=3
            )
            close_button.pack(side="right", padx=10, pady=5)

            image_area = tk.Frame(window, bg="#080808")
            image_area.pack(fill="both", expand=True, padx=12, pady=10)

            window.update_idletasks()
            max_width = max(320, window.winfo_screenwidth() - 40)
            max_height = max(240, window.winfo_screenheight() - 90)

            # Pillow ermöglicht eine proportionale, gut lesbare Skalierung.
            # Falls Pillow nicht installiert ist, wird Tkinter als Rückfall genutzt.
            try:
                from PIL import Image, ImageTk
                original = Image.open(image_path).convert("RGBA")
                original.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                displayed_image = ImageTk.PhotoImage(original, master=window)
            except ImportError:
                original = tk.PhotoImage(master=window, file=str(image_path))
                factor = max(
                    1,
                    math.ceil(original.width() / max_width),
                    math.ceil(original.height() / max_height)
                )
                displayed_image = original.subsample(factor, factor)

            image_label = tk.Label(
                image_area, image=displayed_image,
                bg="#080808", bd=0, highlightthickness=0
            )
            image_label.image = displayed_image
            image_label.pack(expand=True)
            window.bind("<Escape>", lambda _event: window.destroy())
            close_button.focus_set()
        except Exception as exc:
            messagebox.showerror(
                "Grafik konnte nicht geöffnet werden",
                f"Die Erklärgrafik konnte nicht angezeigt werden.\\n{exc}",
                parent=self.root
            )

    def _build_concept_examples(self, parent, exercise):
        canvas = tk.Canvas(parent, bg=PANEL, highlightthickness=0)
        self._examples_canvas = canvas
        if not getattr(self, "_examples_wheel_router_installed", False):
            self.root.bind_all("<MouseWheel>", self._route_examples_mousewheel, add="+")
            self.root.bind_all("<Button-4>", self._route_examples_mousewheel, add="+")
            self.root.bind_all("<Button-5>", self._route_examples_mousewheel, add="+")
            self._examples_wheel_router_installed = True
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=PANEL)
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def refresh(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(window_id, width=canvas.winfo_width())
        inner.bind("<Configure>", refresh)
        canvas.bind("<Configure>", refresh)

        tk.Label(inner, text="BEISPIELE & GRUNDLAGEN", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI Semibold", 11)).pack(anchor="w", padx=18, pady=(16, 5))
        tk.Label(inner,
                 text="Hier findest du zuerst eine Schritt-für-Schritt-Erklärung zur aktuellen Aufgabe. Darunter werden die einzelnen Python-Begriffe mit eigenen Beispielen erklärt.",
                 bg=PANEL, fg=TEXT, wraplength=600, justify="left",
                 font=("Segoe UI", 9)).pack(anchor="w", fill="x", padx=18, pady=(0, 12))

        # Jede Übung erhält denselben didaktischen Aufbau: ein passendes
        # Gesamtbeispiel, eine Erklärung des Ablaufs und konkrete Lernschritte.
        guide = EXAMPLE_GUIDES.get(exercise.get("id"), {})
        if True:
            guide_card = tk.Frame(inner, bg="#090909", highlightthickness=1,
                                  highlightbackground="#68401f")
            guide_card.pack(fill="x", padx=16, pady=(0, 12))
            tk.Label(guide_card, text="SO FUNKTIONIERT DIESE AUFGABE",
                     bg="#090909", fg="#ff9a24",
                     font=("Segoe UI Semibold", 10)).pack(
                         anchor="w", padx=12, pady=(11, 6))
            # Jede Lerneinheit lädt ihre eigene Grafik aus dem Programmordner.
            # Ein Klick öffnet dieselbe Grafik groß im internen Vollbildfenster.
            # Das Abschlussprojekt verwendet die speziell benannte Grafik guide_ui.png.
            # Alle anderen Übungen behalten ihr bisheriges Dateinamensschema.
            if exercise.get("id") == "tkinter-login":
                diagram_path = GUIDE_DIAGRAM_DIR / "guide_ui.png"
            else:
                diagram_path = GUIDE_DIAGRAM_DIR / f"guide_{exercise.get('id')}.png"
            try:
                from PIL import Image, ImageTk
                source_image = Image.open(diagram_path).convert("RGB")
                preview_image = source_image.copy()
                preview_image.thumbnail((max(360, self.root.winfo_width() - 820),
                                         max(220, self.root.winfo_height() - 430)),
                                        Image.Resampling.LANCZOS)
                diagram_preview = ImageTk.PhotoImage(preview_image, master=guide_card)
                if not hasattr(self, "_guide_diagram_refs"):
                    self._guide_diagram_refs = []
                self._guide_diagram_refs.append((source_image, diagram_preview))
                diagram_label = tk.Label(guide_card, image=diagram_preview, bg="#090909",
                                         bd=0, highlightthickness=0, cursor="hand2")
                diagram_label.pack(anchor="center", padx=8, pady=(4, 10))
                diagram_label.bind("<Button-1>",
                    lambda _event, image_path=diagram_path: self._open_diagram_fullscreen(image_path))
                tk.Label(guide_card, text="Grafik anklicken zum Vergrößern",
                         bg="#090909", fg="#b99a79", font=("Segoe UI", 8)).pack(
                             anchor="center", pady=(0, 8))
            except Exception as exc:
                tk.Label(guide_card,
                         text=f"Die Erklärgrafik fehlt oder konnte nicht geladen werden:\n{diagram_path.name}\n{exc}",
                         bg="#090909", fg="#ffbd70", justify="left",
                         font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=8)
            if guide.get("code") and exercise.get("id") != "testing":
                tk.Label(guide_card, text="Beispielcode",
                         bg="#090909", fg=TEXT,
                         font=("Segoe UI Semibold", 9)).pack(
                             anchor="w", padx=12, pady=(2, 4))
                self._create_example_code_panel(
                    guide_card, guide.get("code", ""), title="PYTHON-CODE"
                )

            if guide.get("output") and exercise.get("id") != "testing":
                tk.Label(guide_card, text="Erwartete Ausgabe / Beispielergebnis",
                         bg="#090909", fg=TEXT,
                         font=("Segoe UI Semibold", 9)).pack(
                             anchor="w", padx=12, pady=(2, 4))
                output_box = tk.Text(
                    guide_card, height=max(2, min(8, guide.get("output", "").count("\n") + 1)),
                    bg="#111111", fg="#9fc4ff", relief="flat",
                    padx=10, pady=7, wrap="word",
                    font=("Consolas", 9), borderwidth=0
                )
                output_box.pack(fill="x", padx=10, pady=(0, 8))
                output_box.insert("1.0", guide.get("output", ""))
                output_box.configure(state="disabled")

            if exercise.get("id") not in ("oop", "testing"):
                tk.Label(guide_card, text="WAS PASSIERT HIER?",
                         bg="#090909", fg="#ffbd70",
                         font=("Segoe UI Semibold", 9)).pack(
                             anchor="w", padx=12, pady=(5, 3))
                explain_text = guide.get("explain", "").strip()
                explain_paragraphs = [
                    paragraph.strip()
                    for paragraph in explain_text.split("\\n\\n")
                    if paragraph.strip()
                ]
                for paragraph in explain_paragraphs:
                    tk.Label(
                        guide_card, text=paragraph, bg="#090909", fg="#ded4c8",
                        wraplength=600, justify="left",
                        font=("Segoe UI", 9)
                    ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))
            elif exercise.get("id") == "oop":
                # Für OOP wird jeder Lernschritt als kompakte Grafik statt als Textblock dargestellt.
                tk.Label(guide_card, text="DIE 6 SCHRITTE – JEWEILS MIT GRAFIK",
                         bg="#090909", fg="#ff9a24",
                         font=("Segoe UI Semibold", 10)).pack(
                             anchor="w", padx=12, pady=(5, 7))

                oop_steps = [
                    ("1 | class Charakter:", "Die Klasse definiert den Bauplan. Sie legt fest, welche Daten und Funktionen dazugehören. Hier nutzen wir sie, um Personendaten wie Name und Alter zu verarbeiten.", "BAUPLAN", "class Charakter:", "Daten + Funktionen"),
                    ("2 | __init__() – der automatische Startknopf:", 'Stell dir __init__() wie einen Startknopf vor, der den eingerückten Code innerhalb dieser Methode aktiviert. Sobald spieler1 = Charakter() ausgeführt wird, erkennt Python, dass ein neues Objekt der zuvor erstellten Klasse Charakter erstellt werden soll. Python startet daraufhin automatisch den Code innerhalb von __init__() dieser Klasse.\n\nOhne __init__() musst du eine normale Funktion zusätzlich selbst aufrufen. Mit __init__() wird dieser Start beim Erstellen des Objekts automatisch erledigt und du kannst die Anfangswerte direkt beim Aufruf übergeben.', "AUTOMATISCHER START", "Charakter(...)", "__init__(...)"),
                    ("3 | self", "self steht für das gerade erstellte Objekt – hier das Objekt, auf das spieler1 verweist. Der Parameter könnte auch spieler1 heißen; self ist die übliche Schreibweise.", "OBJEKT-REFERENZ", "spieler1", "self"),
                    ("4 | wert1 und wert2", "Das sind frei benennbare Parameter. Bei Charakter(\"Chris\", 37) erhält wert1 den Text Chris und wert2 die Zahl 37.", "ÜBERGEBENE WERTE", "wert1 = Chris", "wert2 = 37"),
                    ("5 | Objekt erstellen", "spieler1 = Charakter(\"Chris\", 37) erstellt das Objekt. spieler1 ist die Variable, über die du dieses Objekt später erreichst.", "VARIABLE VERWEIST AUF OBJEKT", "spieler1", "Charakter-Objekt"),
                    ("6 | self.name = wert1", "Speichert den Wert von wert1 im erstellten Objekt spieler1 unter name. self.alter = wert2 speichert 37 im selben Objekt unter alter.", "IM OBJEKT GESPEICHERT", "name = Chris", "alter = 37"),
                ]
                for step_title, description, graphic_title, left_text, right_text in oop_steps:
                    step_frame = tk.Frame(guide_card, bg="#111111", highlightthickness=1,
                                           highlightbackground="#68401f")
                    step_frame.pack(fill="x", padx=10, pady=4)
                    tk.Label(step_frame, text=step_title, bg="#111111", fg="#ffbd70",
                             font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=9, pady=(6, 1))
                    tk.Label(step_frame, text=description, bg="#111111", fg="#ded4c8",
                             wraplength=570, justify="left", font=("Segoe UI", 8)).pack(
                                 anchor="w", fill="x", padx=9, pady=(0, 4))
                    if step_title.startswith("2 | __init__"):
                        self._create_example_code_panel(
                            step_frame,
                            'class Charakter:\n    def verarbeitung(self, wert1, wert2):\n        self.name = wert1\n        self.alter = wert2\n\nspieler1 = Charakter()\nspieler1.verarbeitung("Chris", 27)',
                            title="OHNE __init__() – MANUELLER AUFRUF", max_lines=9
                        )
                        self._create_example_code_panel(
                            step_frame,
                            'class Charakter:\n    def __init__(self, wert1, wert2):\n        self.name = wert1\n        self.alter = wert2\n\nspieler1 = Charakter("Chris", 37)',
                            title="MIT __init__() – AUTOMATISCHER START", max_lines=8
                        )
                    mini = tk.Canvas(step_frame, height=48, bg="#111111", highlightthickness=0)
                    mini.pack(fill="x", padx=7, pady=(0, 5))
                    def draw_oop_step(_event=None, c=mini, heading=graphic_title, left=left_text, right=right_text):
                        c.delete("all")
                        w = max(c.winfo_width(), 360)
                        c.create_text(8, 7, anchor="nw", text=heading, fill="#bdb2a6",
                                      font=("Segoe UI Semibold", 7))
                        box_w = min(210, max(125, (w - 75) // 2))
                        y1, y2 = 22, 43
                        c.create_rectangle(8, y1, 8 + box_w, y2, outline="#c77b2a", width=1, fill="#21170e")
                        c.create_text(8 + box_w/2, (y1+y2)/2, text=left, fill="#ffbd70", font=("Consolas", 8))
                        c.create_text(8 + box_w + 24, 32, text="➜", fill="#ff9a24", font=("Segoe UI", 12, "bold"))
                        rx = min(w - 8, 8 + box_w*2 + 48)
                        c.create_rectangle(8 + box_w + 42, y1, rx, y2, outline="#2689b9", width=1, fill="#0b1c25")
                        c.create_text((8 + box_w + 42 + rx)/2, (y1+y2)/2, text=right, fill="#9edfff", font=("Consolas", 8))
                    mini.bind("<Configure>", draw_oop_step)
                    mini.after_idle(draw_oop_step)

            if exercise.get("id") == "comprehension":
                tk.Label(guide_card, text="GRAFIK: SO FUNKTIONIERT POTENZIEREN",
                         bg="#090909", fg="#ff9a24",
                         font=("Segoe UI Semibold", 9)).pack(
                             anchor="w", padx=12, pady=(5, 5))
                power_canvas = tk.Canvas(
                    guide_card, height=278, bg="#111111",
                    highlightthickness=1, highlightbackground="#68401f"
                )
                power_canvas.pack(fill="x", padx=10, pady=(0, 10))

                def draw_power_diagram(_event=None, canvas=power_canvas):
                    canvas.delete("all")
                    width = max(canvas.winfo_width(), 560)
                    canvas.create_text(
                        14, 15, anchor="w",
                        text="Potenzieren = eine Zahl wiederholt mit sich selbst multiplizieren",
                        fill="#f2d2ad", font=("Segoe UI Semibold", 9)
                    )
                    canvas.create_text(
                        14, 35, anchor="w",
                        text="Basis = 3     Exponent = die kleine hochgestellte Zahl",
                        fill="#f2d2ad", font=("Segoe UI", 8)
                    )

                    # Die ursprünglichen Bezeichnungen bleiben erhalten;
                    # zusätzlich zeigen die Zeilen die Multiplikation Schritt für Schritt.
                    examples = [
                        ("3²", "3 × 3 = 9", "drei hoch zwei – Quadrieren"),
                        ("3³", "3 × 3 = 9   |   9 × 3 = 27",
                         "drei hoch drei – Kubieren"),
                        ("3⁴", "3 × 3 = 9   |   9 × 3 = 27   |   27 × 3 = 81",
                         "drei hoch vier"),
                    ]
                    y_positions = [78, 133, 188]
                    for (power, calculation, description), y in zip(examples, y_positions):
                        canvas.create_text(
                            16, y, anchor="w", text=power,
                            fill="#ffb45e", font=("Consolas", 16, "bold")
                        )
                        canvas.create_text(
                            76, y, anchor="w", text=calculation,
                            fill="#ffffff", font=("Consolas", 9, "bold")
                        )
                        canvas.create_text(
                            76, y + 19, anchor="w", text=description,
                            fill="#bdb2a6", font=("Segoe UI", 8)
                        )

                    canvas.create_line(12, 218, width - 12, 218, fill="#68401f")
                    canvas.create_text(
                        14, 238, anchor="w",
                        text="Der Exponent zeigt, wie oft die Basis als Faktor vorkommt.",
                        fill="#ded4c8", font=("Segoe UI", 9)
                    )
                    canvas.create_text(
                        14, 258, anchor="w",
                        text="Beispiel: 3 ** 3 = 3 × 3 × 3 = 27",
                        fill="#ffb45e", font=("Consolas", 10, "bold")
                    )

                power_canvas.bind("<Configure>", draw_power_diagram)
                power_canvas.after_idle(draw_power_diagram)

            if exercise.get("id") == "files":
                # Kompakte Infografik statt langer Fließtext-Erklärung.
                tk.Label(guide_card, text="DATEIEN – KOMPAKT ERKLÄRT",
                         bg="#090909", fg="#ff9a24",
                         font=("Segoe UI Semibold", 10)).pack(
                             anchor="w", padx=12, pady=(5, 5))
                diagram = tk.Canvas(guide_card, height=820, bg="#111111",
                                    highlightthickness=1, highlightbackground="#68401f")
                diagram.pack(fill="x", padx=10, pady=(0, 10))

                def draw_file_diagram(_event=None, canvas=diagram):
                    canvas.delete("all")
                    w = max(canvas.winfo_width(), 260)
                    pad = 14
                    inner_w = max(180, w - 2 * pad)
                    orange, pale, muted = "#ff9a24", "#f2d2ad", "#d8cec3"
                    y = 12

                    def heading(text):
                        nonlocal y
                        canvas.create_text(pad, y, anchor="nw", text=text,
                                           fill=orange, font=("Segoe UI Semibold", 10))
                        y += 24

                    def info_card(title, body, code=None, horizontal_code=False):
                        nonlocal y
                        x1, x2 = pad, w - pad
                        canvas.create_text(x1 + 11, y + 8, anchor="nw",
                            text=title, fill=orange, font=("Segoe UI Semibold", 9))
                        body_y = y + 29
                        body_id = canvas.create_text(x1 + 11, body_y, anchor="nw",
                            text=body, fill=pale, font=("Segoe UI", 9),
                            width=max(140, inner_w - 26), justify="left")
                        bb = canvas.bbox(body_id)
                        body_bottom = bb[3] if bb else body_y + 24
                        bottom = body_bottom + 10
                        if code:
                            code_y = bottom + 2
                            # Keep each source line intact; size the code panel to its line count.
                            from tkinter import font as tkfont
                            code_font = tkfont.Font(family="Consolas", size=9)
                            code_lines = code.splitlines() or [""]
                            line_height = max(15, code_font.metrics("linespace") + 2)
                            code_height = max(27, len(code_lines) * line_height + 12)
                            usable = max(90, x2 - x1 - 35)
                            # Long single-line paths remain on one line and are scaled down modestly.
                            max_line_width = max(code_font.measure(line) for line in code_lines)
                            code_size = 9
                            while not horizontal_code and code_size > 7 and max_line_width > usable:
                                code_size -= 1
                                code_font.configure(size=code_size)
                                line_height = max(15, code_font.metrics("linespace") + 2)
                                code_height = max(27, len(code_lines) * line_height + 12)
                            if horizontal_code:
                                code_height = 43
                            canvas.create_rectangle(x1 + 9, code_y, x2 - 9, code_y + code_height,
                                fill="#111820", outline="#3b3025")
                            if horizontal_code:
                                # Preserve font size and one-line code; scroll sideways when needed.
                                code_widget = tk.Text(canvas, height=1, wrap="none",
                                    bg="#111820", fg="#ffbd70", font=("Consolas", 9),
                                    bd=0, highlightthickness=0, padx=0, pady=0,
                                    cursor="arrow", takefocus=0)
                                code_widget.insert("1.0", code)
                                code_widget.configure(state="disabled")
                                # Dieselbe ttk-Scrollbar wie im restlichen Programm verwenden.
                                # Dadurch greift das zentrale DxPyGuide-Farbschema zuverlässig
                                # auch für diese horizontale Code-Scrollbar.
                                code_scroll = ttk.Scrollbar(
                                    canvas,
                                    orient="horizontal",
                                    command=code_widget.xview,
                                    style="TScrollbar"
                                )
                                code_widget.configure(xscrollcommand=code_scroll.set)
                                canvas.create_window(x1 + 17, code_y + 5, anchor="nw",
                                    window=code_widget, width=max(80, x2-x1-35), height=18)
                                canvas.create_window(x1 + 17, code_y + 23, anchor="nw",
                                    window=code_scroll, width=max(80, x2-x1-35), height=12)
                            else:
                                canvas.create_text(x1 + 17, code_y + 6, anchor="nw",
                                    text=code, fill="#ffbd70", font=code_font,
                                    justify="left")
                            bottom = code_y + code_height + 2
                        canvas.create_rectangle(x1, y, x2, bottom,
                            outline="#68401f", width=1)
                        y = bottom + 9

                    heading("ABLAUF: ÖFFNEN → SCHREIBEN → SCHLIESSEN → LESEN")
                    info_card("1  DATEI ÖFFNEN – open()",
                              "open() öffnet eine Datei. Gibt es sie bei 'w' oder 'a' noch nicht, wird sie erstellt. "
                              "Der Modus 'w' leert eine vorhandene Datei; 'r' liest; 'a' hängt neuen Text an.",
                              'open("beispiel.txt", "w", encoding="utf-8")')
                    info_card("2  SCHREIBEN – write()",
                              "'w' und write() haben verschiedene Aufgaben: 'w' wählt den Öffnungsmodus. "
                              "write() schreibt den angegebenen Text tatsächlich in die geöffnete Datei.",
                              'datei.write("Hallo Datei!")')
                    info_card("3  AUTOMATISCH SCHLIESSEN – with",
                              "with schließt die Datei automatisch, sobald der eingerückte Block endet – auch bei einem Fehler. "
                              "pass ist ein Platzhalter, wenn ein Block vorerst nichts tun soll. Ohne with kannst du "
                              "die Datei mit datei.close() selbst schließen.")
                    info_card("4  LESEN – read()",
                              "Öffne dieselbe Datei erneut mit 'r'. read() liest ihren Inhalt; die Zuweisung speichert "
                              "den gelesenen Text in einer Variablen.",
                              'with open("beispiel.txt", "r", encoding="utf-8") as datei:')
                    info_card("WICHTIGE MODI UND ZEICHENCODIERUNG",
                              "'w' = schreiben/überschreiben   •   'r' = lesen   •   'a' = anhängen. "
                              "encoding='utf-8' legt fest, wie Textzeichen in Bytes umgewandelt und zurückgelesen werden. "
                              "UTF-8 unterstützt Umlaute und viele Sprachen.")
                    # Deutlich sichtbare Trennung zwischen Aufgaben-Erklärung und Speicherort-/mkdir-Grundlagen.
                    y += 28
                    canvas.create_line(pad, y, w - pad, y, fill="#d97706", width=3)
                    y += 26
                    heading("WO SOLL DIE DATEI GESPEICHERT WERDEN?")
                    info_card("1  MANUELLER PFAD",
                              "Du trägst den vollständigen Pfad direkt in open() ein. Ersetze dort den bisherigen Dateinamen "
                              "durch deinen eigenen Pfad. Das r vor dem Text macht den Windows-Pfad zu einem Raw-String; "
                              "so behandelt Python die Backslashes als normale Pfadzeichen. Der Ordner muss bereits existieren.",
                              'with open(r"C:\\Users\\Chris\\Documents\\test.txt", "w", encoding="utf-8") as datei:',
                              horizontal_code=True)
                    info_card("2  WINDOWS-APP-ORDNER – LOCALAPPDATA",
                              "import os lädt Funktionen für Betriebssystem-Informationen. "
                              "os.environ[\"LOCALAPPDATA\"] liest den Windows-Pfad zum lokalen AppData-Ordner des angemeldeten Benutzers. "
                              "Path(...) wandelt den Text in ein Pfadobjekt um. Der Schrägstrich / hängt Ordnernamen und Dateinamen "
                              "passend an den Pfad an.",
                              'ordner = Path(os.environ["LOCALAPPDATA"]) / "DxPyGuide"')
                    info_card("VORBEREITUNG: from pathlib import Path",
                              "from pathlib import Path lädt die Klasse Path aus dem Modul pathlib. "
                              "Path hilft dir, Datei- und Ordnerpfade sauber zusammenzusetzen. "
                              "Mit / hängst du weitere Ordner- oder Dateinamen an; mkdir() erstellt den Ordner. "
                              "So musst du Pfade nicht mühsam als lange Textzeichenketten zusammensetzen.",
                              'from pathlib import Path')
                    info_card("BEISPIEL 1: TEST ORDNER AUF DEM DESKTOP ERSTELLEN",
                              "desktop enthält den vollständigen Pfad zu deinem Desktop. Passe den Pfad an deinen "
                              "Windows-Benutzer und deinen tatsächlichen Desktop-Speicherort an. Mit / wird "
                              "'Test Ordner' an den Desktop-Pfad angehängt. mkdir() erstellt den Ordner. "
                              "Danach wird 'test.txt' an diesen Ordnerpfad angehängt. open(datei_pfad, ...) "
                              "öffnet genau diese Textdatei zum Schreiben; write() schreibt den Text hinein.",
                              'from pathlib import Path\n'
                              'desktop = Path(r"C:\\Users\\Chris\\OneDrive\\Desktop")\n'
                              '\n'
                              'desktop_ordner = desktop / "Test Ordner"\n'
                              'desktop_ordner.mkdir(parents=True, exist_ok=True)\n'
                              '\n'
                              'datei_pfad = desktop_ordner / "test.txt"\n'
                              '\n'
                              'with open(datei_pfad, "w", encoding="utf-8") as datei:\n'
                              '    datei.write("Hallo Datei!")')
                    info_card("BEISPIEL 2: TEST ORDNER IM BENUTZERVERZEICHNIS ERSTELLEN",
                              "Path.home() ermittelt automatisch den persönlichen Benutzerordner des angemeldeten "
                              "Benutzers, z. B. C:\\Users\\Chris. Dadurch muss kein Benutzername fest im Code "
                              "stehen. Anschließend wird wie im ersten Beispiel 'Test Ordner' erstellt und darin "
                              "'test.txt' angelegt. open(datei_pfad, ...) greift auf die Datei zu, weil datei_pfad "
                              "den vollständigen Pfad einschließlich des Dateinamens enthält.",
                              'from pathlib import Path\n'
                              '\n'
                              'benutzerordner = Path.home()\n'
                              '\n'
                              'test_ordner = benutzerordner / "Test Ordner"\n'
                              'test_ordner.mkdir(parents=True, exist_ok=True)\n'
                              '\n'
                              'datei_pfad = test_ordner / "test.txt"\n'
                              '\n'
                              'with open(datei_pfad, "w", encoding="utf-8") as datei:\n'
                              '    datei.write("Hallo Datei!")')
                    # Do not set canvas width here: doing so can make the entire
                    # scrollable page wider than its visible viewport.
                    canvas.configure(height=max(690, y + 8), scrollregion=(0, 0, w, y + 8))

                diagram.bind("<Configure>", draw_file_diagram)
                diagram.after_idle(draw_file_diagram)
            elif exercise.get("id") not in ("oop", "testing"):
                tk.Label(
                    guide_card, text="DAS SOLLTEST DU VERSTEHEN",
                    bg="#090909", fg="#ffbd70",
                    font=("Segoe UI Semibold", 9)
                ).pack(anchor="w", padx=12, pady=(5, 6))

                if exercise.get("id") == "hello":
                    text_sections = [
                        (
                            "SO GIBT print() TEXT AUS",
                            "print() schreibt den Inhalt seiner Klammern in die Konsole. "
                            "Text muss in Anführungszeichen stehen. Python nennt eine "
                            "solche Textangabe einen String."
                        ),
                        (
                            r"ZEILENUMBRUCH MIT \\n",
                            r"Das Zeichen \\n sorgt innerhalb eines Strings dafür, dass "
                            "die Ausgabe in der nächsten Zeile weitergeht. Du kannst damit "
                            "mehrere Zeilen ausgeben, ohne für jede Zeile einen eigenen "
                            "print()-Aufruf zu benötigen."
                        ),
                        (
                            "WARUM STEHEN HIER ZWEI TEXTSTÜCKE?",
                            "Die beiden Strings stehen direkt nebeneinander. Python verbindet "
                            "sie automatisch zu einem gemeinsamen Text. Der Umbruch zwischen "
                            "den beiden Quellcodezeilen dient nur der besseren Lesbarkeit."
                        ),
                        (
                            "ZWEI print()-AUFRUFE",
                            "Jeder neue print()-Aufruf beginnt standardmäßig eine neue "
                            "Ausgabezeile. Deshalb erscheinen „Hallo, Welt!“ und die "
                            "mehrzeilige Ausgabe darunter."
                        )
                    ]
                else:
                    # Andere Übungen behalten ihren vorhandenen Erklärungstext.
                    raw_steps = guide.get("steps", "").strip()
                    text_sections = [
                        ("ERKLÄRUNG", paragraph.strip())
                        for paragraph in raw_steps.split("\\n\\n")
                        if paragraph.strip()
                    ]

                # Nur die neu gestaltete Hello-Welt-Erklärung wird zentriert.
                # Alle anderen Übungen behalten ihre bisherige linksbündige Darstellung.
                text_alignment = "center" if exercise.get("id") == "hello" else "left"
                text_anchor = "center" if exercise.get("id") == "hello" else "w"

                for heading, paragraph in text_sections:
                    tk.Label(
                        guide_card, text=heading,
                        bg="#090909", fg="#ffbd70",
                        font=("Segoe UI Semibold", 9),
                        anchor=text_anchor, justify=text_alignment
                    ).pack(anchor="center" if exercise.get("id") == "hello" else "w",
                           fill="x", padx=12, pady=(5, 2))

                    tk.Label(
                        guide_card, text=paragraph,
                        bg="#090909", fg="#ded4c8",
                        wraplength=560, justify=text_alignment, anchor=text_anchor,
                        font=("Segoe UI", 9)
                    ).pack(anchor="center" if exercise.get("id") == "hello" else "w",
                           fill="x", padx=12, pady=(0, 8))

                tk.Frame(guide_card, bg="#090909", height=4).pack(
                    fill="x", padx=12, pady=(2, 5))



        def add_key_explainer_card():
            # Eigenständige Infografik: Schlüssel und Fernet-Objekt.
            key_card = tk.Frame(inner, bg="#090909", highlightthickness=1,
                                highlightbackground="#b86a22")
            key_card.pack(fill="x", padx=16, pady=(2, 16))
            tk.Label(key_card, text="SCHLÜSSEL ODER VERSCHLÜSSELUNGSOBJEKT?",
                     bg="#090909", fg="#ff9a24",
                     font=("Segoe UI Semibold", 10)).pack(
                         anchor="w", padx=12, pady=(11, 5))
            tk.Label(key_card,
                     text="Das sind zwei verschiedene Dinge. Erst wird ein Schlüssel erzeugt. Danach wird daraus ein Fernet-Objekt erstellt, das du zum Ver- und Entschlüsseln verwendest.",
                     bg="#090909", fg="#ded4c8", wraplength=600,
                     justify="left", font=("Segoe UI", 9)).pack(
                         anchor="w", fill="x", padx=12, pady=(0, 9))

            flow = tk.Frame(key_card, bg="#090909")
            flow.pack(fill="x", padx=10, pady=(0, 8))
            flow.grid_columnconfigure(0, weight=1)
            flow.grid_columnconfigure(1, weight=0)
            flow.grid_columnconfigure(2, weight=1)

            left = tk.Frame(flow, bg="#17110c", highlightthickness=1,
                            highlightbackground="#68401f")
            left.grid(row=0, column=0, sticky="nsew")
            tk.Label(left, text="1. SCHLÜSSEL ERZEUGEN", bg="#17110c",
                     fg="#ffbd70", font=("Segoe UI Semibold", 9)).pack(
                         anchor="w", padx=9, pady=(8, 4))
            self._create_example_code_panel(
                left, "schluessel = Fernet.generate_key()", title="CODE", max_lines=2
            )
            tk.Label(flow, text="➜", bg="#090909", fg="#ff9a24",
                     font=("Segoe UI Semibold", 16)).grid(
                         row=0, column=1, padx=7, sticky="ew")
            right = tk.Frame(flow, bg="#17110c", highlightthickness=1,
                             highlightbackground="#68401f")
            right.grid(row=0, column=2, sticky="nsew")
            tk.Label(right, text="2. OBJEKT ERSTELLEN", bg="#17110c",
                     fg="#ffbd70", font=("Segoe UI Semibold", 9)).pack(
                         anchor="w", padx=9, pady=(8, 4))
            self._create_example_code_panel(
                right, "fernet = Fernet(schluessel)", title="CODE", max_lines=2
            )

            tk.Label(key_card,
                     text="schluessel enthält den erzeugten Schlüssel. fernet enthält danach das Fernet-Objekt mit den Methoden encrypt() und decrypt() – nicht den Schlüssel selbst.",
                     bg="#090909", fg="#ded4c8", wraplength=600,
                     justify="left", font=("Segoe UI", 9)).pack(
                         anchor="w", fill="x", padx=12, pady=(0, 9))

            compare = tk.Frame(key_card, bg="#111111",
                               highlightthickness=1, highlightbackground="#49301a")
            compare.pack(fill="x", padx=10, pady=(0, 10))
            tk.Label(compare, text="DIE KURZFORM", bg="#111111",
                     fg="#ff9a24", font=("Segoe UI Semibold", 9)).pack(
                         anchor="w", padx=9, pady=(7, 2))
            self._create_example_code_panel(
                compare, "fernet = Fernet(Fernet.generate_key())",
                title="KURZES CODEBEISPIEL", max_lines=2
            )
            tk.Label(compare,
                     text="Das ist dasselbe in einer Zeile: innen wird der Schlüssel erzeugt, außen wird daraus das Fernet-Objekt erstellt. Dagegen speichert fernet = Fernet.generate_key() nur den Schlüssel – es entsteht kein Fernet-Objekt.",
                     bg="#111111", fg="#ded4c8", wraplength=580,
                     justify="left", font=("Segoe UI", 9)).pack(
                         anchor="w", fill="x", padx=9, pady=(0, 8))

        if exercise.get("id") != "files":
            # Beim Tkinter-Abschlussprojekt werden die oberen Grundlagenthemen
            # wie der darunterliegende Zusammenspiel-Bereich gemeinsam umrahmt.
            concepts_parent = inner
            concepts_card_padding = 16
            if exercise.get("id") == "tkinter-login":
                concepts_parent = tk.Frame(
                    inner, bg="#090909", highlightthickness=1,
                    highlightbackground="#b86a22"
                )
                concepts_parent.pack(fill="x", padx=16, pady=(8, 14))
                concepts_card_padding = 10

            tk.Label(concepts_parent, text="DIE EINZELNEN PYTHON-BAUSTEINE",
                 bg="#090909" if exercise.get("id") == "tkinter-login" else PANEL,
                 fg=ACCENT,
                 font=("Segoe UI Semibold", 10)).pack(
                     anchor="w", padx=12 if exercise.get("id") == "tkinter-login" else 18,
                     pady=(11, 5) if exercise.get("id") == "tkinter-login" else (8, 4))

            for index, concept in enumerate(exercise.get("concepts", []), 1):
                data = CONCEPT_EXAMPLES.get(concept)
                if exercise.get("id") == "tkinter-login" and concept == "get()":
                    data = (
                        'nutzername = nutzername_feld.get()\n'
                        'passwort = passwort_feld.get()',
                        "WAS MACHT get()?\n"
                        "Entry.get() liest den Text aus, den der Benutzer in ein Tkinter-"
                        "Eingabefeld geschrieben hat.\n\n"
                        "WAS PASSIERT MIT DEM TEXT?\n"
                        "Du kannst den zurückgegebenen Text in einer Variablen speichern "
                        "und anschließend zum Beispiel mit if überprüfen."
                    )
                card = tk.Frame(concepts_parent, bg="#090909", highlightthickness=1,
                                highlightbackground="#3a2818")
                card.pack(fill="x", padx=concepts_card_padding, pady=6)
                tk.Label(card, text=f"{index}.  {concept}", bg="#090909", fg="#ff9a24",
                         font=("Segoe UI Semibold", 10)).pack(anchor="w", padx=12, pady=(10, 5))
                if data:
                    # Das komplette Beispiel zur dauerhaften Schlüsselspeicherung
                    # ohne internes Abschneiden anzeigen; andere Karten behalten
                    # ihre bisherige kompakte Höhe.
                    max_code_lines = 20 if concept == "Schlüssel dauerhaft speichern" else 9
                    self._create_example_code_panel(
                        card, data[0], title="CODEBEISPIEL", max_lines=max_code_lines
                    )
                    # Einheitliche, gut lesbare Darstellung für alle Übungen:
                    # Bereits vorhandene Überschriften und Absätze bleiben erhalten.
                    # Reine Fließtexte werden in kurze Sinnabschnitte aufgeteilt.
                    description = data[1].strip()
                    if "\\n" in description:
                        parts = description.split("\\n\\n")
                        for part in parts:
                            part = part.strip()
                            if not part:
                                continue
                            if "\\n" in part:
                                heading, paragraph = part.split("\\n", 1)
                                tk.Label(
                                    card, text=heading.strip(), bg="#090909", fg="#ffbd70",
                                    font=("Segoe UI Semibold", 9)
                                ).pack(anchor="w", fill="x", padx=12, pady=(3, 1))
                                tk.Label(
                                    card, text=paragraph.strip(), bg="#090909", fg="#ded4c8",
                                    wraplength=600, justify="left",
                                    font=("Segoe UI", 9)
                                ).pack(anchor="w", fill="x", padx=12, pady=(0, 6))
                            else:
                                tk.Label(
                                    card, text=part, bg="#090909", fg="#ded4c8",
                                    wraplength=600, justify="left",
                                    font=("Segoe UI", 9)
                                ).pack(anchor="w", fill="x", padx=12, pady=(0, 6))
                    else:
                        # Zwei Sätze pro Absatz vermeiden lange Textblöcke.
                        sentences = re.split(
                            r'(?<=[.!?])\\s+(?=[A-ZÄÖÜ0-9„"\'])',
                            description
                        )
                        groups = [
                            " ".join(sentences[i:i + 2]).strip()
                            for i in range(0, len(sentences), 2)
                        ]
                        for part_index, paragraph in enumerate(groups):
                            heading = "ERKLÄRUNG" if part_index == 0 else "WEITERE HINWEISE"
                            tk.Label(
                                card, text=heading, bg="#090909", fg="#ffbd70",
                                font=("Segoe UI Semibold", 9)
                            ).pack(anchor="w", fill="x", padx=12, pady=(3, 1))
                            tk.Label(
                                card, text=paragraph, bg="#090909", fg="#ded4c8",
                                wraplength=600, justify="left",
                                font=("Segoe UI", 9)
                            ).pack(anchor="w", fill="x", padx=12, pady=(0, 6))
                    tk.Frame(card, bg="#090909", height=3).pack(
                        fill="x", padx=12, pady=(0, 5))
                    # Logische Reihenfolge: Erst werden Fernet und generate_key()
                    # erklärt. Danach folgt die Grafik zum Unterschied zwischen
                    # Schlüssel und Verschlüsselungsobjekt – vor dem Speichern
                    # und den eigentlichen Verschlüsselungsfunktionen.
                    if exercise.get("id") == "file_encryption" and concept == "generate_key()":
                        add_key_explainer_card()
                else:
                    tk.Label(card, text="Für diesen Begriff ist noch kein separates Beispiel hinterlegt.",
                             bg="#090909", fg="#ded4c8", font=("Segoe UI", 9)).pack(
                                 anchor="w", padx=12, pady=(0, 10))

        # Zusatzbereich nur für das Tkinter-Abschlussprojekt:
        # Die ursprünglichen Kernbeschreibungen und das kurze Grundbeispiel
        # bleiben unverändert. Beispiele mit def stehen bewusst separat.
        if exercise.get("id") == "tkinter-login":
            extra_card = tk.Frame(inner, bg="#090909", highlightthickness=1,
                                  highlightbackground="#b86a22")
            extra_card.pack(fill="x", padx=16, pady=(0, 14))

            tk.Label(extra_card, text="ZUSAMMENSPIEL DER TKINTER-BAUSTEINE",
                     bg="#090909", fg="#ff9a24",
                     font=("Segoe UI Semibold", 10)).pack(
                         anchor="w", padx=12, pady=(11, 5))
            tk.Label(
                extra_card,
                text="Die Kernbeispiele oben zeigen die einzelnen Elemente in ihrer einfachen Form. "
                     "Hier siehst du, wie sie zusammenarbeiten. Die Beispiele verwenden nur die "
                     "bereits erstellte Hauptfenster-Variable fenster.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 8))



            # Zwei zusätzliche Erklärungen stehen bewusst ganz am Ende.
            tk.Frame(extra_card, bg="#68401f", height=1).pack(
                fill="x", padx=12, pady=(5, 7))
            tk.Label(extra_card, text="ZUSÄTZLICHE TKINTER-ERKLÄRUNGEN",
                     bg="#090909", fg="#ff9a24",
                     font=("Segoe UI Semibold", 10)).pack(
                         anchor="w", padx=12, pady=(3, 6))

            tk.Label(extra_card, text="6 | FRAME – WIDGETS IN EINEM BEREICH GRUPPIEREN",
                     bg="#090909", fg="#ffbd70",
                     font=("Segoe UI Semibold", 9)).pack(
                         anchor="w", padx=12, pady=(5, 3))
            self._create_example_code_panel(
                extra_card,
                'login_bereich = tk.Frame(fenster)\n'
                'tk.Label(login_bereich, text="Nutzername").pack()\n'
                'nutzername_feld = tk.Entry(login_bereich)\n'
                'nutzername_feld.pack()',
                title="FRAME MIT EIGENEN WIDGETS", max_lines=5
            )
            tk.Label(
                extra_card, text="DAS ZIEL",
                bg="#090909", fg="#ff9a24",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(7, 2))
            tk.Label(
                extra_card,
                text="Elemente im Programm gruppieren, damit sie wie in einer Box "
                     "zusammengefasst und gemeinsam gesteuert werden können.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="SO FUNKTIONIERT ES",
                bg="#090909", fg="#ff9a24",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(3, 5))

            tk.Label(
                extra_card, text="1. Was ist ein Frame?",
                bg="#090909", fg="#ffbd70",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Ein Frame ist wie ein leerer Umzugskarton auf deiner Programmoberfläche. "
                     "Er selbst macht zunächst nichts weiter, als andere Elemente aufzunehmen.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="2. Elemente in den Karton legen",
                bg="#090909", fg="#ffbd70",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Wenn du Labels, Eingabefelder oder Buttons erstellst, gibst du den Frame "
                     "als übergeordneten Bereich an. In diesem Beispiel heißt er login_bereich. "
                     "Die Elemente gehören dadurch zum Frame und nicht direkt zum Hauptfenster.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="3. Den Frame zunächst unsichtbar vorbereiten",
                bg="#090909", fg="#ffbd70",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Du kannst den Frame zuerst vollständig mit seinen Elementen füllen. "
                     "Solange du login_bereich.pack() noch nicht aufrufst, bleibt der "
                     "gesamte Bereich mit seinen Eingabefeldern unsichtbar. Erst mit diesem "
                     "Aufruf wird der vorbereitete Login-Bereich im Hauptfenster angezeigt.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="4. Der große Vorteil",
                bg="#090909", fg="#ffbd70",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Wenn du den Login-Bereich später ein- oder ausblenden möchtest, musst du "
                     "nicht jedes Eingabefeld und jedes Label einzeln verändern. Du blendest "
                     "einfach den gesamten Frame ein oder aus. Alle Elemente darin werden "
                     "automatisch mit angezeigt oder verborgen.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="KURZ GESAGT",
                bg="#090909", fg="#ff9a24",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Ein Frame ist eine Box für deine Steuerelemente. Er hilft dir, Ordnung "
                     "zu halten und mehrere Elemente mit einem einzigen Befehl gemeinsam "
                     "anzuzeigen oder auszublenden.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 10))

            tk.Label(extra_card, text="7 | BUTTON AUSBLENDEN UND EINGABEFELDER EINBLENDEN",
                     bg="#090909", fg="#ffbd70",
                     font=("Segoe UI Semibold", 9)).pack(
                         anchor="w", padx=12, pady=(5, 3))
            self._create_example_code_panel(
                extra_card,
                'def anmeldung_anzeigen():\n'
                '    start_button.pack_forget()\n'
                '    login_bereich.pack(pady=10)\n'
                '\n'
                'start_button = tk.Button(\n'
                '    fenster, text="Anmelden", command=anmeldung_anzeigen\n'
                ')\n'
                'start_button.pack()',
                title="ANSICHT NACH DEM KLICK WECHSELN", max_lines=8
            )
            tk.Label(
                extra_card, text="DAS ZIEL",
                bg="#090909", fg="#ff9a24",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(7, 2))
            tk.Label(
                extra_card,
                text="Wenn du auf den Button „Anmelden“ klickst, soll dieser Button verschwinden. "
                     "Stattdessen erscheint ein Bereich mit Eingabefeldern, zum Beispiel für "
                     "Benutzername und Passwort.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="SO FUNKTIONIERT ES SCHRITT FÜR SCHRITT",
                bg="#090909", fg="#ff9a24",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(3, 5))

            tk.Label(
                extra_card, text="1. Den Bereich vorbereiten – zunächst unsichtbar",
                bg="#090909", fg="#ffbd70",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Du erstellst zuerst einen unsichtbaren Kasten, einen sogenannten Frame "
                     "namens login_bereich. In diesen Frame packst du die Eingabefelder. "
                     "Da du ihn am Anfang noch nicht mit pack() im Fenster platzierst, "
                     "ist er zunächst nicht zu sehen.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="2. Der Klick auf „Anmelden“",
                bg="#090909", fg="#ffbd70",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Über command=anmeldung_anzeigen wird der Button mit der Funktion "
                     "verbunden. Schreibe den Funktionsnamen ohne Klammern: So wird die "
                     "Funktion erst beim Klick gestartet. Dann erledigt sie zwei Dinge:",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 3))
            tk.Label(
                extra_card,
                text="• Button verstecken: start_button.pack_forget() blendet den Anmelden-Button "
                     "aus. Wichtig: Er wird nicht gelöscht, sondern nur ausgeblendet.\n"
                     "• Login-Bereich anzeigen: login_bereich.pack(pady=10) zeigt danach den "
                     "vorbereiteten Frame mit den Eingabefeldern an.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=20, pady=(0, 7))

            tk.Label(
                extra_card, text="3. Was bedeutet pady=10?",
                bg="#090909", fg="#ffbd70",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="pady ist ein Abstandhalter für die Höhe. Bei pady=10 bleiben oberhalb "
                     "und unterhalb des Frames jeweils 10 Pixel Platz frei. Dadurch klebt der "
                     "Bereich nicht direkt an anderen Elementen. Für seitlichen Abstand links "
                     "und rechts verwendest du stattdessen padx.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="KURZ GESAGT",
                bg="#090909", fg="#ff9a24",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Zuerst erstellst du die Eingabefelder im Hintergrund. Wenn der Button "
                     "geklickt wird, verschwindet der Anmelden-Button und die Eingabefelder "
                     "erscheinen mit etwas Abstand im Fenster.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 10))

            tk.Label(extra_card,
                     text="8 | ANMELDUNG PRÜFEN UND RÜCKMELDUNG ANZEIGEN",
                     bg="#090909", fg="#ffbd70",
                     font=("Segoe UI Semibold", 9)).pack(
                         anchor="w", padx=12, pady=(7, 3))
            self._create_example_code_panel(
                extra_card,
                'def anmeldung_pruefen():\n'
                '    nutzername = nutzername_feld.get()\n'
                '    passwort = passwort_feld.get()\n'
                '    if nutzername == "admin" and passwort == "passwort":\n'
                '        status.config(text="Du bist eingeloggt")\n'
                '    else:\n'
                '        status.config(text="Benutzername oder Passwort falsch")\n'
                '\n'
                'tk.Label(login_bereich, text="Nutzername").pack()\n'
                'nutzername_feld = tk.Entry(login_bereich)\n'
                'nutzername_feld.pack()\n'
                'tk.Label(login_bereich, text="Passwort").pack()\n'
                'passwort_feld = tk.Entry(login_bereich, show="*")\n'
                'passwort_feld.pack()\n'
                'tk.Button(login_bereich, text="Einloggen",\n'
                '          command=anmeldung_pruefen).pack()\n'
                'status = tk.Label(login_bereich, text="")\n'
                'status.pack()',
                title="EINGABEN PRÜFEN UND STATUS ÄNDERN", max_lines=18
            )
            tk.Label(
                extra_card, text="DAS ZIEL",
                bg="#090909", fg="#ff9a24",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(7, 2))
            tk.Label(
                extra_card,
                text="Die eingegebenen Daten – Nutzername und Passwort – überprüfen, "
                     "das Passwort mit Sternchen verbergen und eine Erfolgs- oder "
                     "Fehlermeldung anzeigen.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="SO FUNKTIONIERT ES SCHRITT FÜR SCHRITT",
                bg="#090909", fg="#ff9a24",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(3, 5))

            tk.Label(
                extra_card, text="1. Text auslesen mit .get()",
                bg="#090909", fg="#ffbd70",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Mit .get() holst du den Text ab, den der Benutzer in ein Eingabefeld "
                     "geschrieben hat. Diesen Text kannst du in einer Variablen speichern, "
                     "damit dein Programm ihn später überprüfen kann.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text='2. Passwort verstecken mit show="*"',
                bg="#090909", fg="#ffbd70",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text='Mit show="*" sorgst du dafür, dass im Passwortfeld Sternchen statt '
                     "der eingegebenen Zeichen angezeigt werden. Das Passwort selbst bleibt "
                     "im Programm unverändert. Nur die Darstellung im Eingabefeld wird verborgen.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="3. Prüfen mit if und and",
                bg="#090909", fg="#ffbd70",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Das Programm prüft, ob der Nutzername exakt 'admin' UND das Passwort "
                     "exakt 'passwort' lautet. and bedeutet UND: Beide Bedingungen müssen "
                     "gleichzeitig stimmen. Nur dann ist die Prüfung erfolgreich.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="4. Text ändern mit .config()",
                bg="#090909", fg="#ffbd70",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="• Wenn beide Eingaben stimmen, ändert status.config(text=...) den "
                     "Text des Labels zu „Du bist eingeloggt“.\n"
                     "• Wenn eine Eingabe falsch ist, zeigt das Label eine Fehlermeldung.\n"
                     ".config() kannst du dir wie einen Pinsel vorstellen: Damit veränderst "
                     "du nachträglich eine Eigenschaft eines bereits vorhandenen Elements, "
                     "hier den angezeigten Text.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=20, pady=(0, 7))

            tk.Label(
                extra_card, text="5. Die Prüfung starten",
                bg="#ff9a24", fg="#090909",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Auch der Einloggen-Button wird mit command=anmeldung_pruefen "
                     "mit seiner Prüffunktion verbunden. Wie beim ersten Button steht "
                     "der Funktionsname ohne Klammern dahinter. Dadurch startet die Prüfung "
                     "erst, wenn der Benutzer auf „Einloggen“ klickt.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 7))

            tk.Label(
                extra_card, text="KURZ GESAGT",
                bg="#090909", fg="#ff9a24",
                font=("Segoe UI Semibold", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(2, 2))
            tk.Label(
                extra_card,
                text="Du liest die Eingaben aus, verbirgst das Passwort mit Sternchen und "
                     "prüfst mit if, ob Nutzername und Passwort stimmen. Anschließend zeigt "
                     "das Programm eine Erfolgs- oder Fehlermeldung an.",
                bg="#090909", fg="#ded4c8", wraplength=600, justify="left",
                font=("Segoe UI", 9)
            ).pack(anchor="w", fill="x", padx=12, pady=(0, 10))


        def wheel(event):
            if getattr(event, "delta", 0):
                canvas.yview_scroll(int(-event.delta / 120), "units")
            elif getattr(event, "num", None) == 4:
                canvas.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(1, "units")
            return "break"
        canvas.bind("<MouseWheel>", wheel)
        canvas.bind("<Button-4>", wheel)
        canvas.bind("<Button-5>", wheel)
        inner.bind("<MouseWheel>", wheel)
        inner.bind("<Button-4>", wheel)
        inner.bind("<Button-5>", wheel)

    def _route_examples_mousewheel(self, event):
        """Leitet Mausrad-Ereignisse auch von eingebetteten Textfeldern an den Lern-Canvas."""
        canvas = getattr(self, "_examples_canvas", None)
        if canvas is None or not canvas.winfo_exists():
            return
        widget = event.widget
        belongs_to_canvas = False
        while widget is not None:
            if widget == canvas:
                belongs_to_canvas = True
                break
            try:
                parent_name = widget.winfo_parent()
                if not parent_name:
                    break
                widget = widget.nametowidget(parent_name)
            except (KeyError, tk.TclError, AttributeError):
                break
        if not belongs_to_canvas:
            return
        if getattr(event, "num", None) == 4:
            amount = -1
        elif getattr(event, "num", None) == 5:
            amount = 1
        else:
            delta = getattr(event, "delta", 0)
            amount = -1 if delta > 0 else 1 if delta < 0 else 0
        if amount:
            canvas.yview_scroll(amount, "units")
            return "break"

    def show_solution_window(self):
        """Zeigt zuerst die vollständige Lösung und danach klar gegliederte Erklärungen."""
        exercise = self.current
        if not exercise:
            return
        window = tk.Toplevel(self.root)
        window.title("Lösung – " + exercise.get("title", "Übung"))
        window.configure(bg=PANEL)
        window.geometry("800x760")
        window.minsize(580, 480)
        try:
            window.transient(self.root)
        except tk.TclError:
            pass

        outer = tk.Frame(window, bg=PANEL)
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=PANEL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        body = tk.Frame(canvas, bg=PANEL)
        window_id = canvas.create_window((0, 0), window=body, anchor="nw")

        def refresh(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(window_id, width=canvas.winfo_width())
        body.bind("<Configure>", refresh)
        canvas.bind("<Configure>", refresh)

        def section(title, text, color="#ded4c8"):
            tk.Label(body, text=title, bg=PANEL, fg=ACCENT,
                     font=("Segoe UI Semibold", 10)).pack(
                         anchor="w", padx=20, pady=(12, 5))
            tk.Label(body, text=text, bg=PANEL, fg=color,
                     wraplength=720, justify="left",
                     font=("Segoe UI", 10)).pack(
                         anchor="w", fill="x", padx=22, pady=(0, 5))

        tk.Label(body, text=exercise.get("title", "Lösung"),
                 bg=PANEL, fg=ACCENT, font=("Segoe UI Semibold", 16)).pack(
                     anchor="w", padx=20, pady=(18, 5))
        section("MUSTERLÖSUNG", "")
        solution = exercise.get("solution", "").strip()
        solution_box = tk.Text(
            body, height=max(8, min(28, solution.count("\n") + 3)),
            bg="#111111", fg="#ffbd70", relief="flat",
            padx=12, pady=10, wrap="none",
            font=("Consolas", 10), borderwidth=0
        )
        solution_box.pack(fill="x", padx=20, pady=(0, 14))
        solution_box.insert("1.0", solution or "Für diese Übung ist noch keine Lösung hinterlegt.")
        solution_box.configure(state="disabled")

        explanation = exercise.get("explanation", "").strip().replace("\n", "\n")
        guide = EXAMPLE_GUIDES.get(exercise.get("id"), {})
        guide_explanation = guide.get("explain", "").strip().replace("\n", "\n")
        steps = guide.get("steps", "").strip().replace("\n", "\n")
        details = EXPLANATION_DETAILS.get(exercise.get("id"), "").strip().replace("\n", "\n")

        section("WARUM IST DAS RICHTIG?", explanation or guide_explanation or
                "Die Lösung erfüllt die Anforderungen der Aufgabe.")
        if guide_explanation and guide_explanation != explanation:
            section("WAS PASSIERT IM PROGRAMM?", guide_explanation)
        if steps:
            section("SCHRITT FÜR SCHRITT", steps)
        if details:
            section("TYPISCHE FEHLER UND WICHTIGE HINWEISE", details)

        if exercise.get("id") == "operators":
            section("DIE VERGLEICHSOPERATOREN",
                    "Vergleichsoperatoren vergleichen zwei Werte. Das Ergebnis ist immer True (wahr) oder False (falsch).")
            operator_rows = [
                ("==  Gleich", "alter == 18", "True, wenn beide Werte gleich sind."),
                ("!=  Ungleich", "alter != 18", "True, wenn die Werte verschieden sind."),
                (">  Größer als", "alter > 18", "True, wenn der linke Wert größer ist."),
                ("<  Kleiner als", "alter < 18", "True, wenn der linke Wert kleiner ist."),
                (">=  Größer oder gleich", "alter >= 18", "True, wenn der Wert mindestens 18 ist. Genau 18 zählt mit."),
                ("<=  Kleiner oder gleich", "alter <= 99", "True, wenn der Wert höchstens 99 ist. Genau 99 zählt mit."),
            ]
            for title, example, description in operator_rows:
                card = tk.Frame(body, bg="#090909", highlightthickness=1,
                                highlightbackground="#3a2818")
                card.pack(fill="x", padx=20, pady=4)
                tk.Label(card, text=title, bg="#090909", fg="#ff9a24",
                         font=("Segoe UI Semibold", 10)).pack(anchor="w", padx=12, pady=(8, 2))
                tk.Label(card, text=example, bg="#090909", fg="#ffbd70",
                         font=("Consolas", 10)).pack(anchor="w", padx=12, pady=2)
                tk.Label(card, text=description, bg="#090909", fg="#ded4c8",
                         wraplength=680, justify="left",
                         font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(2, 8))

            section("DIE LOGISCHEN OPERATOREN",
                    "and, or und not verbinden oder verändern Wahrheitswerte. Sie bestimmen, wie mehrere Bedingungen zusammen ausgewertet werden.")
            logical_rows = [
                ("and  UND", "alter >= 18 and alter <= 99",
                 "Beide Teilbedingungen müssen True sein. Für diese Aufgabe bedeutet das: mindestens 18 UND höchstens 99."),
                ("or  ODER", "regen == True or wind == True",
                 "Mindestens eine Teilbedingung muss True sein. Sind beide False, ist das Gesamtergebnis False."),
                ("not  NICHT", "not gesperrt",
                 "Kehrt einen Wahrheitswert um: aus True wird False und aus False wird True."),
            ]
            for title, example, description in logical_rows:
                card = tk.Frame(body, bg="#090909", highlightthickness=1,
                                highlightbackground="#3a2818")
                card.pack(fill="x", padx=20, pady=4)
                tk.Label(card, text=title, bg="#090909", fg="#ff9a24",
                         font=("Segoe UI Semibold", 10)).pack(anchor="w", padx=12, pady=(8, 2))
                tk.Label(card, text=example, bg="#090909", fg="#ffbd70",
                         font=("Consolas", 10)).pack(anchor="w", padx=12, pady=2)
                tk.Label(card, text=description, bg="#090909", fg="#ded4c8",
                         wraplength=680, justify="left",
                         font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(2, 8))

            section("WARUM VERWENDET DIE LÖSUNG AND?",
                    "Die Aufgabe verlangt, dass beide Grenzen gleichzeitig eingehalten werden. Mit or wäre bereits eine einzige erfüllte Grenze ausreichend. Dann würde zum Beispiel auch ein Alter von 15 Jahren die Bedingung alter <= 99 erfüllen und fälschlich Zutritt erhalten.")
            section("IF, ELSE UND EINRÜCKUNG",
                    "if prüft die Bedingung. Der eingerückte print()-Befehl wird nur ausgeführt, wenn sie True ist. else steht auf derselben Einrückungsebene wie if und fängt alle übrigen Fälle ab. Der Code unter else muss ebenfalls eingerückt sein. Der Doppelpunkt beginnt jeweils den Codeblock.")

        def wheel(event):
            if getattr(event, "num", None) == 4:
                canvas.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
            return "break"
        canvas.bind("<MouseWheel>", wheel)
        body.bind("<MouseWheel>", wheel)
        canvas.bind("<Button-4>", wheel)
        canvas.bind("<Button-5>", wheel)
        body.bind("<Button-4>", wheel)
        body.bind("<Button-5>", wheel)

    def _editor_yview(self, *args):
        self.editor.yview(*args)
        self._sync_lines()

    def _sync_lines(self):
        if not hasattr(self, "editor") or not self.editor.winfo_exists():
            return
        count = int(self.editor.index("end-1c").split(".")[0])
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", "\n".join(str(i) for i in range(1, count + 1)))
        self.line_numbers.configure(state="disabled")
        self.line_numbers.yview_moveto(self.editor.yview()[0])
        self._draw_indent_guides()
        self._highlight_syntax()

    def _create_indent_overlay(self):
        """Deaktiviert: transparente Toplevel-Overlays sind unter Windows instabil."""
        self._indent_overlay = None
        self._indent_canvas = None
        self._indent_overlay_ready = False

    def _hide_indent_overlay(self, event=None):
        return

    def _draw_indent_guides(self):
        """Der experimentelle Overlay-Zeichner ist in dieser stabilen Version aus."""
        return

    def _highlight_syntax(self):
        if not hasattr(self, "editor") or not self.editor.winfo_exists():
            return
        text = self.editor.get("1.0", "end-1c")
        for tag in ("keyword", "string", "comment", "number", "function", "escape"):
            self.editor.tag_remove(tag, "1.0", "end")
        self.editor.tag_configure("keyword", foreground="#c792ea")
        self.editor.tag_configure("string", foreground="#c3e88d")
        self.editor.tag_configure("comment", foreground="#718096")
        self.editor.tag_configure("number", foreground="#f78c6c")
        self.editor.tag_configure("function", foreground="#82aaff")
        # Escape-Sequenzen wie \n werden innerhalb von Strings separat markiert.
        self.editor.tag_configure("escape", foreground="#ffb454", font=("Consolas", 10, "bold"))
        import re
        string_pattern = r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'|\"(?:\\.|[^\"\\])*\"|\'(?:\\.|[^\'\\])*\')'
        for pattern, tag in [
            (r'\b(def|class|if|elif|else|for|while|in|return|import|from|as|try|except|finally|with|pass|break|continue|and|or|not|is|lambda|True|False|None)\b', "keyword"),
            (string_pattern, "string"),
            (r'#.*', "comment"),
            (r'\b\d+(?:\.\d+)?\b', "number"),
            (r'\b(print|input|range|len|type|int|str|float|list|dict|set|tuple|open)\b', "function")
        ]:
            for m in re.finditer(pattern, text, re.S if '\"\"\"' in pattern else 0):
                start_idx, end_idx = m.start(), m.end()
                self.editor.tag_add(tag, "1.0+" + str(start_idx) + "c",
                                    "1.0+" + str(end_idx) + "c")
                if tag == "string":
                    # Python-Escape-Sequenzen: Newline, Tab, Backslash, Quotes,
                    # Steuerzeichen sowie Hex-/Unicode- und Oktal-Escapes.
                    escape_pattern = r'\\\\(?:[\\\\\'\"abfnrtv]|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|[0-7]{1,3})'
                    for esc in re.finditer(escape_pattern, m.group()):
                        a = start_idx + esc.start()
                        b = start_idx + esc.end()
                        self.editor.tag_add("escape", "1.0+" + str(a) + "c",
                                            "1.0+" + str(b) + "c")

    def _explain_python_error(self, traceback_text):
        """Erklärt Python-Fehler konkret und verständlich für Anfänger."""
        lines = traceback_text.splitlines()
        last_line = next((line.strip() for line in reversed(lines)
                          if line.strip()), "")

        error_line_number = None
        source_line = ""
        for index, line in enumerate(lines):
            match = re.search(r", line (\d+)", line)
            if match:
                error_line_number = int(match.group(1))
                if index + 1 < len(lines):
                    candidate = lines[index + 1].strip()
                    if candidate and not candidate.startswith(("^", "SyntaxError")):
                        source_line = candidate
                break

        if "SyntaxError" in traceback_text:
            normalized = source_line.strip()
            if re.fullmatch(r"(if|elif|while|for|with|def|class)\s*:", normalized):
                keyword = normalized.split(":")[0]
                explanations = {
                    "if": "Nach 'if' fehlt die Bedingung. Sie muss direkt hinter if und vor dem Doppelpunkt stehen.",
                    "elif": "Nach 'elif' fehlt die weitere Bedingung. Sie muss direkt hinter elif und vor dem Doppelpunkt stehen.",
                    "while": "Nach 'while' fehlt die Wiederholungsbedingung.",
                    "for": "Nach 'for' fehlen die Schleifenvariable und der Ausdruck mit 'in'.",
                    "with": "Nach 'with' fehlt der Ausdruck, der geöffnet bzw. verwaltet werden soll.",
                    "def": "Nach 'def' fehlen der Funktionsname und die Klammern.",
                    "class": "Nach 'class' fehlt der Klassenname.",
                }
                detail = explanations.get(keyword, "Hinter dem Schlüsselwort fehlt ein Ausdruck.")
                location = (
                    f"Fehler in Zeile {error_line_number}: {source_line}\n\n"
                    if error_line_number else ""
                )
                return (
                    "SYNTAXFEHLER – Bedingung fehlt\n\n"
                    + location + detail + "\n\n"
                    "Wichtig: Die Bedingung gehört in dieselbe Zeile wie 'if'. "
                    "Eine Zeile darunter wird als Inhalt des Blocks gelesen und "
                    "kann die fehlende Bedingung nicht ersetzen.\n\n"
                    "So ist die Struktur für diese Aufgabe richtig:\n"
                    "alter = int(input('Wie alt bist du? '))\n"
                    "if alter >= 18 and alter <= 99:\n"
                    "    print('Zutritt')\n"
                    "else:\n"
                    "    print('Kein Zutritt')\n\n"
                    "Achte darauf: else steht auf derselben Einrückungsebene wie if."
                )

            location = (
                f"Fehler in Zeile {error_line_number}: {source_line}\n\n"
                if error_line_number else ""
            )
            return (
                "SYNTAXFEHLER – Schreibweise nicht gültig\n\n" + location
                + "Python kann die angezeigte Zeile nicht lesen. Prüfe insbesondere, "
                "ob Bedingungen direkt hinter if/elif/while stehen, Doppelpunkte "
                "vorhanden sind und eingerückte Codeblöcke richtig angeordnet sind.\n\n"
                "TECHNISCHE DETAILS\n" + last_line
            )

        explanations = {
            "IndentationError": ("EINRÜCKUNGSFEHLER (IndentationError)",
                "Eine Zeile ist nicht richtig eingerückt. Code innerhalb von if, for, while oder def muss eingerückt sein. Verwende möglichst vier Leerzeichen."),
            "NameError": ("NAME NICHT GEFUNDEN (NameError)",
                "Du verwendest einen Namen, den Python nicht kennt. Prüfe die Schreibweise und ob die Variable oder Funktion vorher erstellt wurde."),
            "TypeError": ("DATENTYP-FEHLER (TypeError)",
                "Eine Operation oder Funktion hat einen Wert mit einem unpassenden Datentyp erhalten. Prüfe beispielsweise, ob du Text und Zahlen miteinander verrechnest."),
            "ValueError": ("UNGÜLTIGER WERT (ValueError)",
                "Der Datentyp ist grundsätzlich passend, aber der konkrete Wert kann nicht verarbeitet werden. Beispiel: int('Hallo') funktioniert nicht."),
            "IndexError": ("INDEX AUSSERHALB DER LISTE (IndexError)",
                "Du greifst auf eine Position zu, die in der Liste oder Zeichenkette nicht existiert. Der erste Index ist 0."),
            "KeyError": ("SCHLÜSSEL NICHT GEFUNDEN (KeyError)",
                "Der angefragte Schlüssel ist in diesem Dictionary nicht vorhanden. Prüfe die Schreibweise oder verwende dict.get(...)."),
            "ZeroDivisionError": ("TEILEN DURCH NULL (ZeroDivisionError)",
                "Eine Zahl wurde durch 0 geteilt. Eine Division durch null ist in Python nicht möglich."),
            "ModuleNotFoundError": ("MODUL NICHT GEFUNDEN (ModuleNotFoundError)",
                "Python konnte das importierte Modul nicht finden. Prüfe den Modulnamen und ob das Paket installiert ist."),
            "AttributeError": ("EIGENSCHAFT ODER METHODE NICHT GEFUNDEN (AttributeError)",
                "Du greifst auf eine Eigenschaft oder Methode zu, die dieses Objekt nicht besitzt. Prüfe Namen und Datentyp."),
            "AssertionError": ("TEST FEHLGESCHLAGEN (AssertionError)",
                "Eine assert-Bedingung war falsch. Vergleiche das erwartete Ergebnis mit dem tatsächlichen Wert."),
        }
        for error_name, (heading, explanation) in explanations.items():
            if error_name in traceback_text:
                return f"{heading}\n\n{explanation}\n\nTECHNISCHE DETAILS\n{last_line}"
        return None

    def _autocomplete_candidates(self):
        """Ermittelt eingebaute Namen sowie Variablen/Funktionen aus dem Editor."""
        names = set(keyword.kwlist)
        callable_names = {
            name for name in dir(builtins)
            if name.isidentifier() and not name.startswith("_")
            and callable(getattr(builtins, name, None))
        }
        names.update(
            name for name in dir(builtins)
            if name.isidentifier() and not name.startswith("_")
        )

        # Häufig verwendete Methoden werden ebenfalls angeboten.
        method_names = {
            "append", "extend", "insert", "remove", "pop", "sort", "reverse",
            "keys", "values", "items", "get", "strip", "split", "join",
            "replace", "lower", "upper", "startswith", "endswith", "find",
            "count", "write", "read", "close", "format"
        }
        names.update(method_names)
        callable_names.update(method_names)

        # Namen aus dem aktuellen Quelltext erfassen, auch wenn der Code
        # während der Eingabe vorübergehend syntaktisch unvollständig ist.
        code = self.editor.get("1.0", "end-1c")
        user_functions = set()
        user_classes = set()
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(node.name)
                    user_functions.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    names.add(node.name)
                    user_classes.add(node.name)
                elif isinstance(node, ast.Name):
                    names.add(node.id)
                elif isinstance(node, ast.arg):
                    names.add(node.arg)
                elif isinstance(node, (ast.For, ast.AsyncFor)):
                    for target in ast.walk(node.target):
                        if isinstance(target, ast.Name):
                            names.add(target.id)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in node.names:
                        names.add(alias.asname or alias.name.split(".")[0])
        except SyntaxError:
            names.update(re.findall(r"(?m)^\s*([A-Za-z_]\w*)\s*=", code))
            functions = re.findall(r"(?m)^\s*def\s+([A-Za-z_]\w*)", code)
            classes = re.findall(r"(?m)^\s*class\s+([A-Za-z_]\w*)", code)
            names.update(functions)
            names.update(classes)
            user_functions.update(functions)
            user_classes.update(classes)

        suggestions = {}
        for name in names:
            if not name.isidentifier():
                continue
            if name in callable_names or name in user_functions or name in user_classes:
                insertion = name + "()"
            else:
                insertion = name
            suggestions[name] = insertion

        # Häufig benötigte Namen aus dem Standardmodul random.
        # Das Modul selbst wird ohne Klammern ergänzt, randint als Funktion.
        suggestions["random"] = "random"
        suggestions["randint"] = "randint()"

        return suggestions

    def _autocomplete_update(self):
        if not hasattr(self, "editor") or not self.editor.winfo_exists():
            return

        before_cursor = self.editor.get("1.0", "insert")
        match = re.search(r"([^\W\d]\w*)$", before_cursor)
        if not match:
            self._autocomplete_hide()
            return

        prefix = match.group(1)
        if not prefix:
            self._autocomplete_hide()
            return

        candidates = []
        for name, insertion in self._autocomplete_candidates().items():
            if not name.lower().startswith(prefix.lower()):
                continue
            # Sobald der Name vollständig geschrieben wurde, wird kein
            # Vorschlag mehr angezeigt. Bei Teilwörtern bleibt er sichtbar.
            if name.lower() == prefix.lower():
                continue
            candidates.append((name, insertion))

        # Erst kürzere/naheliegende Treffer, dann alphabetisch.
        candidates.sort(key=lambda pair: (len(pair[0]), pair[0].lower()))
        candidate_insertions = [insertion for _name, insertion in candidates[:12]]
        if not candidate_insertions:
            self._autocomplete_hide()
            return

        self._autocomplete_items = candidate_insertions

        if self._autocomplete_popup is None or not self._autocomplete_popup.winfo_exists():
            popup = tk.Toplevel(self.root)
            popup.overrideredirect(True)
            popup.configure(bg="#3a2818")
            try:
                popup.attributes("-topmost", True)
            except tk.TclError:
                pass
            listing = tk.Listbox(
                popup, height=min(8, len(self._autocomplete_items)),
                bg="#15110d", fg="#f2e8dc", selectbackground="#ff7900",
                selectforeground="#080808", activestyle="none", relief="flat",
                borderwidth=1, highlightthickness=1, highlightbackground="#6b421f",
                font=("Consolas", 10)
            )
            listing.pack(fill="both", expand=True, padx=1, pady=1)
            listing.bind("<ButtonRelease-1>", self._autocomplete_click)
            self._autocomplete_popup = popup
            self._autocomplete_list = listing

        listing = self._autocomplete_list
        listing.delete(0, "end")
        for item in self._autocomplete_items:
            listing.insert("end", item)
        listing.selection_clear(0, "end")
        listing.selection_set(0)
        listing.activate(0)

        bbox = self.editor.bbox("insert")
        if bbox:
            x, y, _width, height = bbox
            px = self.editor.winfo_rootx() + x
            py = self.editor.winfo_rooty() + y + height
            self._autocomplete_popup.geometry(f"+{px}+{py}")
            self._autocomplete_popup.deiconify()
            self._autocomplete_popup.lift()
        else:
            self._autocomplete_popup.withdraw()

    def _autocomplete_hide(self, event=None):
        popup = getattr(self, "_autocomplete_popup", None)
        if popup is not None:
            try:
                popup.destroy()
            except tk.TclError:
                pass
        self._autocomplete_popup = None
        self._autocomplete_list = None
        self._autocomplete_items = []
        return "break" if event is not None else None

    def _editor_click_hide_autocomplete(self, _event=None):
        # Das Menü schließen, den normalen Text-Klick aber weiterlaufen lassen,
        # damit der Cursor an die angeklickte Position gesetzt wird.
        self._autocomplete_hide()
        return None

    def _autocomplete_focus_out(self, _event=None):
        # Beim Klick in die Vorschlagsliste bleibt das Menü geöffnet, damit
        # der ausgewählte Eintrag noch übernommen werden kann. Bei jedem
        # anderen Fokuswechsel wird ein veraltetes Menü geschlossen.
        self.root.after(100, self._autocomplete_hide_if_focus_moved)

    def _autocomplete_hide_if_focus_moved(self):
        focus = self.root.focus_get()
        listing = getattr(self, "_autocomplete_list", None)
        if focus is self.editor or focus is listing:
            return
        self._autocomplete_hide()

    def _autocomplete_move(self, event):
        listing = getattr(self, "_autocomplete_list", None)
        if listing is None or not self._autocomplete_items:
            return
        selected = listing.curselection()
        index = selected[0] if selected else 0
        index = (index + (1 if event.keysym == "Down" else -1)) % len(self._autocomplete_items)
        listing.selection_clear(0, "end")
        listing.selection_set(index)
        listing.activate(index)
        return "break"

    def _autocomplete_accept(self, event=None):
        listing = getattr(self, "_autocomplete_list", None)
        if listing is None or not self._autocomplete_items:
            return None

        selected = listing.curselection()
        index = selected[0] if selected else 0
        completion = self._autocomplete_items[index]

        before_cursor = self.editor.get("1.0", "insert")
        match = re.search(r"([^\W\d]\w*)$", before_cursor)
        if not match:
            self._autocomplete_hide()
            return None

        prefix = match.group(1)
        start = self.editor.index(f"insert - {len(prefix)} chars")
        self.editor.delete(start, "insert")
        self.editor.insert(start, completion)
        self._autocomplete_hide()
        self._on_editor_change()
        return "break"

    def _editor_tab(self, event=None):
        """Tab übernimmt Autocomplete oder fügt exakt vier Leerzeichen ein."""
        if self._autocomplete_list is not None and self._autocomplete_items:
            return self._autocomplete_accept(event)
        self.editor.insert("insert", "    ")
        self._autocomplete_hide()
        self._on_editor_change()
        return "break"

    def _editor_shift_tab(self, event=None):
        """Shift+Tab entfernt am Zeilenanfang bis zu vier Leerzeichen."""
        line_start = self.editor.index("insert linestart")
        line_end = self.editor.index("insert lineend")
        line = self.editor.get(line_start, line_end)
        leading = len(line) - len(line.lstrip(" "))
        if leading:
            remove_count = min(4, leading)
            self.editor.delete(line_start, f"{line_start}+{remove_count}c")
            self._on_editor_change()
        return "break"

    def _autocomplete_enter(self, event=None):
        """Enter übernimmt Vorschläge oder fügt eine passend eingerückte Zeile ein."""
        if self._autocomplete_list is not None and self._autocomplete_items:
            return self._autocomplete_accept(event)

        # Einrückung der aktuellen Zeile übernehmen.
        line_start = self.editor.index("insert linestart")
        before_cursor = self.editor.get(line_start, "insert")
        leading_match = re.match(r"[ \t]*", before_cursor)
        indent = leading_match.group(0) if leading_match else ""
        stripped = before_cursor.strip()

        # Nach einem Blockkopf (if, else, for, def usw.) eine Ebene einrücken.
        if stripped.endswith(":") and not stripped.startswith("#"):
            indent += "    "
        # Nach einer abschließenden Anweisung innerhalb eines Blocks
        # auf die vorherige Einrückungsebene zurückkehren.
        elif stripped in {"return", "pass", "break", "continue"} and len(indent) >= 4:
            indent = indent[:-4]

        self.editor.insert("insert", "\n" + indent)
        self._autocomplete_hide()
        self._on_editor_change()
        return "break"

    def _autocomplete_click(self, _event=None):
        self._autocomplete_accept()
        self.editor.focus_set()

    def _on_editor_change(self, event=None):
        self._sync_lines()
        if self.autosave_job:
            self.root.after_cancel(self.autosave_job)
        self.autosave_job = self.root.after(450, self._save_current)

        # Python-Blockzweige wie else:/elif:/except:/finally: gehören auf
        # dieselbe Einrückungsebene wie der zugehörige if/try-Block.
        if event is not None and event.char == ":":
            line_start = self.editor.index("insert linestart")
            line_end = self.editor.index("insert lineend")
            line = self.editor.get(line_start, line_end)
            branch = re.match(r"^(\s{4,})(else|elif\b.*|except\b.*|finally|case\b.*):\s*$", line)
            if branch:
                old_indent = branch.group(1)
                new_indent = old_indent[:-4]
                self.editor.delete(line_start, f"{line_start}+{len(old_indent)}c")
                self.editor.insert(line_start, new_indent)

        if event is None:
            self._autocomplete_hide()
            return

        if event.keysym in ("Up", "Down"):
            # Pfeiltasten bewegen nur die Auswahl in der Vorschlagsliste.
            # Die Liste darf beim KeyRelease nicht geschlossen werden.
            return
        elif event.keysym in ("BackSpace", "Delete"):
            # Beim Korrigieren eines unvollständigen Namens Vorschläge neu prüfen.
            self._autocomplete_update()
        elif event.char and event.char.isprintable() and (event.char.isalnum() or event.char == "_"):
            # Nur echte Eingabe eines Namenszeichens darf Vorschläge öffnen.
            self._autocomplete_update()
        else:
            # Navigation, Klicks, Leerzeichen und Satzzeichen öffnen kein Menü.
            self._autocomplete_hide()

    def _save_current(self):
        if self.current and hasattr(self, "editor") and self.editor.winfo_exists():
            self.store.save_code(self.current["id"], self.editor.get("1.0", "end-1c"))
            self._update_sidebar()

    def _set_output(self, text, error=False, info=False):
        if not hasattr(self, "output") or not self.output.winfo_exists():
            return
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        tag = "error" if error else ("info" if info else None)
        if tag:
            self.output.insert("end", text, tag)
        else:
            self.output.insert("end", text)
        self.output.configure(state="disabled")

    def run_code(self):
        self._save_current()
        code = self.editor.get("1.0", "end-1c")
        if self.current and self.current.get("id") == "file_encryption" and "cryptography" not in self.prepared_packages:
            # Konsolen-Vorbereitung der Verschlüsselungsübung.
            code = (
                'print("Paketinstallation: cryptography")\n'
                'print("Gib den Installationsbefehl ein:")\n'
                'befehl = input("Terminal> ")\n'
                'if " ".join(befehl.strip().split()) in ("pip install cryptography", "python -m pip install cryptography"):\n'
                '    print("Collecting cryptography ...")\n'
                '    print("Downloading cryptography ...")\n'
                '    print("Installing collected packages: cryptography")\n'
                '    print("Successfully installed cryptography")\n'
                'else:\n'
                '    print("Befehl nicht erkannt. Gib genau Folgendes ein:")\n'
                '    print("pip install cryptography")\n'
            )
            self._encryption_install_running = True
        elif not code.strip():
            self._set_output("Schreibe zuerst etwas Python-Code.", info=True)
            return

        with self.process_lock:
            previous = self.running_process
            if previous is not None and previous.poll() is None:
                try:
                    previous.kill()
                except Exception:
                    pass
            self.running_process = None

        self.store.attempt(self.current["id"])
        self.run_token += 1
        token = self.run_token
        if hasattr(self, "run_button") and self.run_button.winfo_exists():
            self.run_button.configure(text="■ Stoppen", command=self.stop_code,
                                      style="Dark.TButton")
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "Programm gestartet.\n")
        self.output.mark_set("console_input_start", "end-1c")
        self.output.mark_gravity("console_input_start", "left")
        self.output.mark_set("insert", "end-1c")
        self.output.see("end")
        self.output.focus_set()
        threading.Thread(target=self._execute_code, args=(code, token), daemon=True).start()

    def _finish_encryption_setup(self, token):
        if token != self.run_token or not self.current or self.current.get("id") != "file_encryption":
            return
        self.prepared_packages.add("cryptography")
        self.store.set_setting("prepared_package_cryptography", "1")
        self._append_console_output(
            token,
            "\n\nVorbereitung abgeschlossen. "
            "Jetzt kannst du den Verschlüsselungscode im Editor schreiben und ausführen.\n",
            error=False,
        )

    def _set_run_button(self, token, running=False):
        if token != self.run_token:
            return
        button = getattr(self, "run_button", None)
        if button is None:
            return
        try:
            if button.winfo_exists():
                if running:
                    button.configure(text="■ Stoppen", command=self.stop_code,
                                     style="Dark.TButton")
                else:
                    button.configure(text="▶ Ausführen", command=self.run_code,
                                     style="Accent.TButton")
        except tk.TclError:
            pass

    def stop_code(self):
        """Bricht den aktuell laufenden Python-Unterprozess sofort ab."""
        self._stop_running_process()
        token = self.run_token
        self._set_run_button(token, running=False)
        self._append_console_output(
            token,
            "\n\n■ Ausführung manuell gestoppt. Der Python-Prozess wurde beendet.\n",
            error=True
        )

    def _append_console_output(self, token, text, error=False):
        if token != self.run_token or not self.winfo_exists():
            return
        if not hasattr(self, "output") or not self.output.winfo_exists():
            return
        widget = self.output
        widget.configure(state="normal")
        # Nutzereingaben hinter dem Eingabemarker bleiben erhalten, auch wenn
        # das Programm währenddessen weitere Ausgaben erzeugt.
        pending = widget.get("console_input_start", "end-1c")
        widget.delete("console_input_start", "end-1c")
        widget.insert("console_input_start", text, "error" if error else ())
        widget.insert("end-1c", pending)
        widget.mark_set("console_input_start", f"end-1c - {len(pending)} chars")
        widget.mark_gravity("console_input_start", "left")
        widget.mark_set("insert", "end-1c")
        widget.see("end")
        widget.configure(state="normal")

    def _console_enter(self, _event=None):
        self.send_input()
        return "break"

    def _console_key_guard(self, event):
        # Nur am Ende der Konsole darf während einer laufenden input()-Abfrage
        # geschrieben oder gelöscht werden. Die bisherige Ausgabe bleibt geschützt.
        with self.process_lock:
            process = self.running_process
            active = process is not None and process.poll() is None
        if not active:
            return "break"
        try:
            if self.output.compare("insert", "<", "console_input_start"):
                self.output.mark_set("insert", "end-1c")
            if event.keysym in ("BackSpace", "Delete"):
                if self.output.compare("insert", "<=", "console_input_start"):
                    return "break"
            if event.keysym in ("Home", "Up", "Prior"):
                self.output.mark_set("insert", "end-1c")
                return "break"
            if event.keysym in ("Left",):
                if self.output.compare("insert", "<=", "console_input_start"):
                    return "break"
        except Exception:
            return "break"
        return None

    def _console_click_guard(self, _event=None):
        self.root.after_idle(lambda: self.output.mark_set("insert", "end-1c"))

    def send_input(self):
        widget = self.output
        value = widget.get("console_input_start", "end-1c")
        with self.process_lock:
            process = self.running_process
            if process is None or process.poll() is not None:
                return
            try:
                process.stdin.write((value + "\n").encode("utf-8"))
                process.stdin.flush()
            except (BrokenPipeError, OSError, AttributeError):
                self._append_console_output(self.run_token,
                    "\nProgrammeingabe ist nicht mehr verfügbar. Starte den Code erneut.\n", True)
                return

        widget.insert("end-1c", "\n")
        widget.mark_set("console_input_start", "end-1c")
        widget.mark_gravity("console_input_start", "left")
        widget.mark_set("insert", "end-1c")
        widget.see("end")
        widget.focus_set()

    def _execute_code(self, code, token, stdin_data=None):
        process = None
        try:
            # Das Skript selbst bleibt temporär. Das Arbeitsverzeichnis des
            # ausgeführten Codes ist dagegen dauerhaft, damit relative Datei-
            # pfade (z. B. open("beispiel.txt", "w")) erhalten bleiben.
            WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="pylern_") as temp:
                path = Path(temp) / "uebung.py"
                path.write_text(code, encoding="utf-8")
                child_env = os.environ.copy()
                child_env["PYTHONIOENCODING"] = "utf-8"
                child_env["PYTHONUTF8"] = "1"
                process = subprocess.Popen(
                    [sys.executable, "-X", "utf8", "-I", "-u", str(path)],
                    cwd=str(WORKSPACE_DIR), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, bufsize=0, env=child_env
                )
                with self.process_lock:
                    if token != self.run_token:
                        process.kill()
                        return
                    self.running_process = process

                # Kompatibilität mit älteren Aufrufen, die stdin_data übergeben.
                # Die interaktive Konsole bleibt anschließend weiterhin geöffnet.
                if stdin_data:
                    try:
                        process.stdin.write(stdin_data.encode("utf-8"))
                        if not stdin_data.endswith("\n"):
                            process.stdin.write(b"\n")
                        process.stdin.flush()
                    except (BrokenPipeError, OSError):
                        pass

                # Separater Leser streamt auch Prompts ohne Zeilenumbruch sofort in die Konsole.
                captured_output = []
                def read_output():
                    decoder = __import__("codecs").getincrementaldecoder("utf-8")("replace")
                    try:
                        while True:
                            chunk = process.stdout.read(1)
                            if not chunk:
                                break
                            decoded = decoder.decode(chunk)
                            if decoded:
                                captured_output.append(decoded)
                                self.root.after(0, self._append_console_output, token, decoded)
                        tail = decoder.decode(b"", final=True)
                        if tail:
                            captured_output.append(tail)
                            self.root.after(0, self._append_console_output, token, tail)
                    except (OSError, ValueError):
                        pass

                reader = threading.Thread(target=read_output, daemon=True)
                reader.start()
                try:
                    # Ein grafisches tkinter-Fenster bleibt offen, bis der Lernende es schließt.
                    # Dafür erhält die Abschlussübung ein längeres Zeitlimit als Konsolenübungen.
                    run_timeout = 600 if self.current and self.current.get("id") == "tkinter-login" else 60
                    return_code = process.wait(timeout=run_timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    self.root.after(0, self._append_console_output, token,
                        "\n\nZEITLIMIT ERREICHT\nDas Programm lief länger als 60 Sekunden. "
                        "Prüfe, ob eine Endlosschleife vorliegt oder noch eine Eingabe fehlt.\n", True)
                    return_code = -999

                reader.join(timeout=1)
                with self.process_lock:
                    if self.running_process is process:
                        self.running_process = None
                self.root.after(0, self._set_run_button, token, False)

                if return_code == 0:
                    self.root.after(0, self._append_console_output, token,
                                    "\n\n✓ Ausführung abgeschlossen.")
                    if self._encryption_install_running and "Successfully installed cryptography" in "".join(captured_output):
                        self.root.after(0, self._finish_encryption_setup, token)
                    self._encryption_install_running = False
                elif self._encryption_install_running:
                    self._encryption_install_running = False
                elif return_code != -999:
                    # Der vollständige Traceback bleibt sichtbar; darunter folgt eine Anfänger-Erklärung.
                    # Die Ausgabe wurde bereits live gestreamt, daher wird nur die Erklärung ergänzt.
                    # Diagnose auf Basis der im Leser-Thread gesammelten Ausgabe.
                    # Kein Zugriff auf Tkinter-Widgets außerhalb des GUI-Threads.
                    current_output = "".join(captured_output)
                    friendly = self._explain_python_error(current_output)
                    if friendly:
                        self.root.after(0, self._append_console_output, token,
                                        "\n\n" + friendly, True)
                    else:
                        self.root.after(0, self._append_console_output, token,
                                        "\n\n✗ Ausführung mit Fehler beendet.", True)
        except Exception as exc:
            with self.process_lock:
                if self.running_process is process:
                    self.running_process = None
            self.root.after(0, self._set_run_button, token, False)
            self.root.after(0, self._append_console_output, token,
                            f"\nAusführungsfehler: {exc}", True)

    def check_answer(self):
        if self.current and self.current.get("id") == "file_encryption" and "cryptography" not in self.prepared_packages:
            self._set_output("Führe zuerst die Konsolen-Vorbereitung aus und gib den Installationsbefehl ein.", info=True)
            return
        code = self.editor.get("1.0", "end-1c")
        if not code.strip():
            self._set_output("Du hast noch keinen Code geschrieben. Lies die Aufgabe und beginne mit dem Startcode.", info=True)
            return
        try:
            ast.parse(code)
        except SyntaxError as exc:
            source_lines = code.splitlines()
            bad_line = source_lines[exc.lineno - 1] if exc.lineno and exc.lineno <= len(source_lines) else ""
            stripped = bad_line.strip()
            explanation = ""
            correction = ""

            # Häufige Anfängerfehler gezielt erklären, statt nur "invalid syntax" auszugeben.
            if "=>" in bad_line:
                explanation = (
                    "Du hast den Vergleichsoperator => geschrieben. Diesen Operator gibt es in Python nicht. "
                    "Das Gleichheitszeichen steht bei Vergleichsoperatoren rechts: >= bedeutet "
                    "'größer oder gleich', <= bedeutet 'kleiner oder gleich'."
                )
                correction = (
                    "Schreibe den Vergleich mit einem Wert auf beiden Seiten, zum Beispiel:\n"
                    "if alter >= accept and alter <= 100:"
                )
            elif re.search(r"\\bif\\s*:", stripped):
                explanation = (
                    "Nach if fehlt die Bedingung. Python erwartet direkt hinter if einen vollständigen "
                    "Vergleich oder Ausdruck. Der Doppelpunkt kommt erst dahinter."
                )
                correction = (
                    "Beispiel:\n"
                    "if alter >= accept and alter <= 100:\n"
                    "    print('Zutritt')"
                )
            elif re.search(r"\\b(if|elif|while)\\b", stripped) and not stripped.endswith(":"):
                explanation = (
                    "Die Bedingungszeile muss mit einem Doppelpunkt enden. Außerdem muss nach if, "
                    "elif oder while ein vollständiger Ausdruck stehen."
                )
                correction = "Beispiel:\nif alter >= 18:\n    print('Zutritt')"
            elif exc.msg == "expected an indented block":
                explanation = (
                    "Nach einer Zeile, die mit Doppelpunkt endet, erwartet Python einen eingerückten "
                    "Codeblock. Die nächste Anweisung muss normalerweise vier Leerzeichen weiter rechts stehen."
                )
                correction = "Beispiel:\nif alter >= 18:\n    print('Zutritt')"
            elif exc.msg == "unexpected indent":
                explanation = (
                    "Diese Zeile ist eingerückt, obwohl Python an dieser Stelle keinen neuen Codeblock erwartet. "
                    "Entferne die überflüssigen Leerzeichen oder prüfe, ob davor eine Zeile mit Doppelpunkt fehlt."
                )
                correction = "Eine normale Anweisung beginnt am Zeilenanfang; innerhalb eines if-Blocks steht sie vier Leerzeichen weiter rechts."
            elif exc.msg == "unindent does not match any outer indentation level":
                explanation = (
                    "Die Einrückung passt nicht zu einem vorher begonnenen Block. Verwende durchgehend vier "
                    "Leerzeichen pro Ebene und richte else auf derselben Ebene wie das zugehörige if aus."
                )
                correction = "Beispiel:\nif alter >= 18:\n    print('Zutritt')\nelse:\n    print('Kein Zutritt')"
            else:
                explanation = (
                    "Python kann diese Zeile nicht nach den Sprachregeln lesen. Prüfe, ob jeder Vergleich "
                    "einen linken und rechten Wert hat, ob Operatoren korrekt geschrieben sind und ob "
                    "Klammern, Anführungszeichen und Doppelpunkte stimmen."
                )
                correction = (
                    "Prüfe die markierte Zeile einzeln. Bei einem Vergleich braucht Python beispielsweise "
                    "einen Wert vor und nach dem Operator: alter >= accept."
                )

            line_context = f"Fehler in Zeile {exc.lineno}:\n{bad_line or '(Zeile nicht verfügbar)'}"
            pointer = ""
            if exc.offset:
                pointer = "\n" + " " * max(0, exc.offset - 1) + "^"

            message = (
                "DEIN CODE ENTHÄLT EINEN SYNTAXFEHLER\n\n"
                + line_context + pointer + "\n\n"
                + "WAS IST FALSCH?\n" + explanation + "\n\n"
                + "WIE KANNST DU ES KORRIGIEREN?\n" + correction + "\n\n"
                + "Die Aufgabe bleibt offen. Korrigiere den Fehler und klicke erneut auf "
                  "'Antwort prüfen'."
            )
            self._set_output(message, error=True)
            return
        required = self.current.get("checks", [])
        missing = [item for item in required if item not in code]
        if missing:
            labels = {
                "print": "eine Ausgabe mit print()",
                "input": "eine Eingabe mit input()",
                "name": "die Variable bzw. den Namen 'name'",
                "alter": "die Variable 'alter'",
                "lieblingsspiel": "die Variable 'lieblingsspiel'",
                "int": "die Umwandlung mit int()",
                "if": "eine if-Bedingung",
                "elif": "einen elif-Zweig",
                "else": "einen else-Zweig",
                "for": "eine for-Schleife",
                "while": "eine while-Schleife",
                "range": "die Funktion range()",
                "def": "eine Funktionsdefinition mit def",
                "return": "eine Rückgabe mit return",
                "append": "die Listenmethode append()",
                "try": "einen try-Block",
                "except": "einen except-Block",
                "ValueError": "die Fehlerart ValueError",
                "open": "das Öffnen einer Datei mit open()",
                "with": "einen with-Block",
                "write": "das Schreiben mit write()",
                "read": "das Lesen mit read()",
                "import random": "den Import von random",
                "randint": "die Funktion randint()",
                "class": "eine Klassendefinition mit class",
                "__init__": "die Initialisierungsmethode __init__()",
                "self": "den Parameter self",
                "assert": "eine Prüfung mit assert",
                "==": "einen Gleichheitsvergleich (==)",
                "and": "die Verknüpfung and",
                "<=": "den Vergleich <=",
                ">=": "den Vergleich >=",
                "{": "geschweifte Klammern für eine formatierte Ausgabe",
                "[": "eine Liste bzw. eckige Klammern",
                "[]": "eine leere Liste",
                "**": "den Potenzoperator **",
                "+=": "eine Kurzzuweisung mit +=",
                "True": "den Wahrheitswert True",
                "float": "den Datentyp float",
                "type": "die Funktion type()",
                "begruessung": "die Funktion begruessung()",
                "import tkinter": "den Import von tkinter",
                "tk.Tk(": "das Hauptfenster mit tk.Tk()",
                "tk.Entry(": "Eingabefelder mit tk.Entry()",
                "tk.Button(": "Buttons mit tk.Button()",
                "command=": "die Button-Funktion über command=",
                ".get()": "das Auslesen der Eingaben mit get()",
                "mainloop()": "die Ereignisschleife mit mainloop()",
            }
            missing_text = "\n".join("• " + labels.get(item, f"den Baustein {item}") for item in missing)
            self._set_output(
                "Noch nicht bestanden – diese Punkte fehlen in deinem Code:\n\n" + missing_text +
                "\n\nErgänze die fehlenden Bausteine und klicke erneut auf 'Antwort prüfen'.\n\n"
                "Hinweis: Die Prüfung kontrolliert die hinterlegten Anforderungen und die Python-Syntax; "
                "sie ist kein vollständiger Funktionstest.",
                info=True
            )
        else:
            # Eine erfolgreiche Prüfung schließt die Übung direkt und dauerhaft ab.
            self._save_current()
            self.store.complete(self.current["id"])
            self._update_sidebar()
            self._set_output(
                "✓ Prüfung erfolgreich – die Aufgabe wurde automatisch als erledigt markiert.\n\n"
                "Dein Fortschritt wurde gespeichert. Du kannst mit der nächsten Übung weitermachen.\n\n"
                "Hinweis: Die Prüfung kontrolliert die hinterlegten Anforderungen und die Python-Syntax; "
                "sie ist kein vollständiger Funktionstest.",
                info=True
            )

    def _stop_running_process(self):
        self.run_token += 1
        with self.process_lock:
            process = self.running_process
            self.running_process = None
            if process is not None and process.poll() is None:
                try:
                    process.kill()
                except Exception:
                    pass

    def _finish_run(self, token, output, error):
        if token == self.run_token and self.winfo_exists():
            self._set_output(output, error=error)

    def winfo_exists(self):
        try:
            return self.root.winfo_exists()
        except tk.TclError:
            return False

    def reset_code(self):
        if messagebox.askyesno("Code zurücksetzen", "Möchtest du deinen aktuellen Code durch den Startcode ersetzen?"):
            # Bei einem vollständigen Aufgaben-Reset beginnt auch die
            # Paketvorbereitung der Verschlüsselungsübung wieder von vorn.
            if self.current and self.current.get("id") == "file_encryption":
                self.prepared_packages.discard("cryptography")
                self.store.set_setting("prepared_package_cryptography", "0")
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", self.current.get("starter", ""))
            self._on_editor_change()
            self._set_output("Startcode wiederhergestellt.", info=True)

    def show_help(self, title, content):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("680x520")
        win.configure(bg=PANEL)
        tk.Label(win, text=title, bg=PANEL, fg=TEXT,
                 font=("Segoe UI Semibold", 16)).pack(anchor="w", padx=22, pady=(20, 10))
        txt = tk.Text(win, bg=EDITOR_BG, fg=TEXT, wrap="word", padx=16, pady=14,
                      relief="flat", font=("Segoe UI", 10))
        txt.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        txt.insert("1.0", content)
        txt.configure(state="disabled")

    def mark_complete(self):
        self._save_current()
        self.store.complete(self.current["id"])
        self._update_sidebar()
        messagebox.showinfo("Übung abgeschlossen", "Dein Fortschritt wurde gespeichert. Gut gemacht!")
        if self.current_mode == "tutorial":
            self.next_tutorial()
        else:
            self.open_exercise(self.current)

    def close_exercise(self, exercise):
        self._stop_running_process()
        self._save_current()
        if messagebox.askyesno("Übung schließen", "Möchtest du diese Übung aus deinem persönlichen Verlauf entfernen? Der gespeicherte Code und ihr Fortschrittsstatus werden dabei gelöscht."):
            self.store.close_exercise(exercise["id"])
            self.show_dashboard()

    def start_tutorial(self):
        p = self.store.all_progress()
        first = next((i for i, e in enumerate(EXERCISES)
                      if not (self.store.get(e["id"])[4])), 0)
        self.tutorial_index = first
        self.open_exercise(EXERCISES[self.tutorial_index], tutorial=True)

    def next_tutorial(self):
        self._save_current()
        if self.current and self.current.get("information_only"):
            self.store.complete(self.current["id"])
        if self.tutorial_index < len(EXERCISES) - 1:
            self.tutorial_index += 1
            self.open_exercise(EXERCISES[self.tutorial_index], tutorial=True)
        else:
            messagebox.showinfo("Tutorial-Reihe", "Du hast alle Lektionen der Tutorial-Reihe erreicht!")
            self.show_dashboard()

    def on_close(self):
        self._stop_running_process()
        self._save_current()
        self.store.db.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    PythonLernstudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
