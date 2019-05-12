#!/usr/bin/env python3

import os
import re
import argparse
import time
import json

def set_output_color(color, bold=False):
    colormap = {
            "black": "30",
            "red": "31",
            "green": "32",
            "yellow": "33",
            "blue": "34",
            "magenta": "35",
            "cyan": "36",
            "white": "37"
        }

    if color == "default":
        print("\033[0m", end='')
    else:
        bstr = "1" if bold else "0"
        cstr = colormap[color]
        print(f"\033[{bstr};{cstr}m", end='')


class QSO:
    NAME_MAP = {
            'timestamp': "Zeitstempel",
            'tx_rst': "Gesendetes RST",
            'tx_num': "Gesendete Nummer",
            'rx_rst': "Empfangenes RST",
            'rx_call': "Empfangenes Rufzeichen",
            'rx_num': "Empfangene Nummer",
            'rx_loc': "Empfangener Locator",
            'rx_dok': "Empfangener DOK"
        }

    def __init__(self, **kwargs):
        self.data = {}

        self.data['timestamp'] = str(int(time.time()))

        self.data['tx_rst'] = "59"
        self.data['tx_num'] = None

        self.data['rx_rst'] = "59"
        self.data['rx_call'] = None
        self.data['rx_num'] = None
        self.data['rx_loc'] = None
        self.data['rx_dok'] = None

        self.data.update(kwargs)

        self.normalize_format()

    def normalize_format(self):
        if self.data['tx_num']:
            self.data['tx_num'] = "{:03d}".format(int(self.data['tx_num']))
        if self.data['rx_num']:
            self.data['rx_num'] = "{:03d}".format(int(self.data['rx_num']))

        for k in ['rx_call', 'rx_loc', 'rx_dok']:
            if self.data[k]:
                self.data[k] = self.data[k].upper()

    def serialize(self):
        return json.dumps(self.data)

    def deserialize(self, string):
        self.data = json.loads(string)

    def edit(self):
        cmd = 'x'

        while cmd != 'q':
            edit_order = []

            for k, v in self.NAME_MAP.items():
                if k[0] == 'r':
                    set_output_color("green")
                else:
                    set_output_color("yellow")

                data = self.data[k]

                print(f"[{len(edit_order)}] {v:22s} - {data}")
                edit_order.append(k)

            set_output_color("default")

            cmd = input("\nEintragsnummer ('q' zum Beenden)> ")

            try:
                idx = int(cmd)
            except:
                continue

            if idx >= len(edit_order):
                continue

            edit_key = edit_order[idx]

            new_val = input(f"{self.NAME_MAP[edit_key]}> ")
            if new_val:
                self.data[edit_key] = new_val
            else:
                set_output_color("red")
                print("Leere Eingabe -> QSO nicht verändert.")

        self.normalize_format()

    def print_table_header(self):
        print("QSO# ", end='')
        print("Zeit              ", end='')
        print("TX RST/Nr.   ", end='')
        print("RX Rufz.     ", end='')
        print("RX RST/Nr.   ", end='')
        print("RX DOK  ", end='')
        print("RX Loc. ")

    def print_table_data(self, idx):
        gmt = time.gmtime(int(self.data['timestamp']))
        timestr = time.strftime('%Y-%m-%d %H:%M', gmt)

        print("{:4d} ".format(idx), end='')
        print("{:18s}".format(timestr), end='')
        print("{} {:10s}".format(self.data['tx_rst'], self.data['tx_num'] or '-'), end='')
        print("{:13s}".format(self.data['rx_call'] or '-'), end='')
        print("{} {:10s}".format(self.data['rx_rst'], self.data['rx_num'] or '-'), end='')
        print("{:8s}".format(self.data['rx_dok'] or '-'), end='')
        print("{:8s}".format(self.data['rx_loc'] or '-'))


class QSOManager:
    def __init__(self, my_call, my_loc, my_dok, log_file):
        self.my_call = my_call
        self.my_loc = my_loc
        self.my_dok = my_dok

        self.log_file = log_file

        self.qsos = []

        if os.path.exists(log_file):
            self.load(log_file)

            set_output_color("blue")
            print(f"{len(self.qsos)} QSOs geladen.")

        self.next_number = len(self.qsos) + 1

    def load(self, log_file):
        with open(log_file, 'r') as f:
            for line in f:
                q = QSO()
                q.deserialize(line)
                self.qsos.append(q)

    def save(self, log_file=None):
        if not log_file:
            log_file = self.log_file

        if os.path.exists(log_file):
            os.rename(log_file, log_file + "~")

        with open(log_file, 'w') as f:
            for qso in self.qsos:
                f.write(qso.serialize() + "\n")

    def add_qso_from_string(self, text):
        parts = text.split(' ')
        parts.reverse() # search backwards

        # regular expressions for different parts
        callregex = re.compile('([a-z0-9]+/)?[a-z]{1,2}[0-9]+[a-z]+(/p|/m|/mm|/am)?', re.IGNORECASE)
        dokregex = re.compile('([0-9]+)?[a-z][0-9]{2}', re.IGNORECASE)
        rstnumregex = re.compile('[0-9]+', re.IGNORECASE)
        locregex = re.compile('[a-z]{2}[0-9]{2}[a-z]{2}', re.IGNORECASE)

        callfound = dokfound = rstnumfound = locfound = False

        call = dok = rst = num = loc = None

        for part in parts:
            part = part.strip()

            if not dokfound:
                mo = dokregex.match(part)
                if mo:
                    dok = mo.group(0)
                    dokfound = True
                    continue

            if not rstnumfound:
                mo = rstnumregex.match(part)
                if mo:
                    rstnum = mo.group(0)

                    rst = rstnum[:2]
                    num = rstnum[2:]
                    rstnumfound = True
                    continue

            if not locfound:
                mo = locregex.match(part)
                if mo:
                    loc = mo.group(0)
                    locfound = True
                    continue

            if not callfound:
                locmo = locregex.match(part)
                if locmo:
                    set_output_color("yellow")
                    print(f"ACHTUNG: {part} sieht wie ein Locator aus und wurde als Rufzeichen ignoriert.")
                else:
                    mo = callregex.match(part)
                    if mo:
                        call = mo.group(0)
                        callfound = True

        q = QSO(tx_num=str(self.next_number),
                tx_rst='59', # FIXME
                rx_call=call,
                rx_dok=dok,
                rx_loc=loc,
                rx_rst=rst,
                rx_num=num)

        qsoidx = len(self.qsos)
        self.qsos.append(q)

        return q, qsoidx

    def edit_last_qso(self):
        if not self.qsos:
            set_output_color("yellow")
            print("Keine QSOs im Log.")
            return

        self.qsos[-1].edit()

    def print_qso_table(self):
        if not self.qsos:
            set_output_color("yellow")
            print("Keine QSOs im Log.")
            return

        self.qsos[0].print_table_header()

        for i in range(len(self.qsos)):
            self.qsos[i].print_table_data(i)

    def loop(self):
        """Main loop."""

        while True:
            set_output_color("magenta")
            print(f"\n<<< 59 {self.next_number:03d} {self.my_dok} {self.my_loc}")
            set_output_color("default")
            cmd = input('> ')

            if cmd == 'h':
                set_output_color("green")
                print("Gültige Befehle:\n")
                print("h - Diese Hilfe anzeigen")
                print("q - Programm beenden")
                print("n - Nächste ausgehende Nummer setzen")
                print("e - Das letzte QSO bearbeiten")
                print("b - QSO nach Nummer bearbeiten")
                print("l - QSOs auflisten")
                print("")
                print("Jede andere Eingabe wird als neues QSO interpretiert und eingelesen")
                print("")
            elif cmd == 'q':
                self.save()
                break
            elif cmd == 'n':
                nstr = input('Nächste ausgehende Nummer> ')

                set_output_color("red")
                if not nstr:
                    print("Leere Eingabe -> Nummer nicht verändert.")
                else:
                    try:
                        self.next_number = int(nstr)
                    except:
                        print(f"{nstr} ist keine Zahl")
            elif cmd == 'e':
                self.edit_last_qso()
                self.save()
            elif cmd == 'b':
                nstr = input('QSO-Nummer> ')
                set_output_color("red")

                if not nstr:
                    print("Leere Eingabe -> Abbruch.")
                else:
                    try:
                        qsoidx = int(nstr)
                        self.qsos[qsoidx].edit()
                        self.save()
                    except Exception as e:
                        print(f"Fehler bei der QSO-Bearbeitung: {str(e)}")

            elif cmd == 'l':
                self.print_qso_table()
            elif len(cmd) > 1:
                q, qsoidx = self.add_qso_from_string(cmd)
                self.save()

                self.next_number += 1

                set_output_color("cyan")

                print("")
                q.print_table_header()
                q.print_table_data(qsoidx)
                print("")
            else:
                set_output_color("red")
                print("Eingabe nicht erkannt.")


parser = argparse.ArgumentParser(description='Logprogramm für die Frankenaktivität.')
parser.add_argument('-c', '--call', dest='call', type=str, required=True, help='Eigenes Rufzeichen')
parser.add_argument('-l', '--locator', dest='locator', type=str, required=True, help='Eigener Locator')
parser.add_argument('-d', '--dok', dest='dok', type=str, required=True, help='Eigener DOK')
parser.add_argument('-o', '--output-file', dest='output_file', type=str, required=True, help='File where the QSOs will be saved. Will be loaded if it exists.')

args = parser.parse_args()

my_call = args.call
my_loc  = args.locator
my_dok  = args.dok

set_output_color("green")
print(f"""
Eigene Info:

    Rufzeichen: {my_call}
    Locator:    {my_loc}
    DOK:        {my_dok}

Gib 'h' für eine Befehlsliste ein.
""")

set_output_color("default")

qsomgr = QSOManager(args.call, args.locator, args.dok, args.output_file)

qsomgr.loop()
