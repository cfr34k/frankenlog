#!/usr/bin/env python3

#    FrankenLog - a logging program for ham radio contests
#    Copyright (C) 2019  Thomas Kolb (DL5TKL)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import re
import argparse
import time
import json
import readline

import helper
from helper import set_output_color

from templates import *

# regular expressions for different parts of a QSO
callregex = re.compile('([a-z0-9]+/)?[a-z]{1,2}[0-9]+[a-z]+(/p|/m|/mm|/am)?', re.IGNORECASE)
dokregex = re.compile('([0-9]+)?[a-z][0-9]{2}', re.IGNORECASE)
rstnumregex = re.compile('[0-9]+', re.IGNORECASE)
locregex = re.compile('[a-z]{2}[0-9]{2}[a-z]{2}', re.IGNORECASE)

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

    def __init__(self, my_info, **kwargs):
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

        self.my_info = my_info

        self.normalize_format()

        self.update_stats()

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
        self.update_stats()

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
        self.update_stats()

    def update_stats(self):
        tx_loc = self.my_info['loc']
        rx_loc = self.data['rx_loc']

        if not tx_loc or not rx_loc:
            self.stats = None
            return

        self.stats = {}
        self.stats['distance'] = helper.DistanceBetweenLocs(tx_loc, rx_loc)
        self.stats['dok']    = self.data['rx_dok']
        self.stats['field']  = rx_loc[:4]

    def print_table_header(self, term=True):
        print("QSO# ", end='')
        print("Zeit              ", end='')
        print("TX RST/Nr.   ", end='')
        print("RX Rufz.     ", end='')
        print("RX RST/Nr.   ", end='')
        print("RX DOK  ", end='')
        print("RX Loc. ", end='')
        print("Distanz ", end='')
        if term:
            print()

    def print_table_data(self, idx, term=True):
        gmt = time.gmtime(int(self.data['timestamp']))
        timestr = time.strftime('%Y-%m-%d %H:%M', gmt)

        print("{:4d} ".format(idx), end='')
        print("{:18s}".format(timestr), end='')
        print("{} {:10s}".format(self.data['tx_rst'], self.data['tx_num'] or '-'), end='')
        print("{:13s}".format(self.data['rx_call'] or '-'), end='')
        print("{} {:10s}".format(self.data['rx_rst'], self.data['rx_num'] or '-'), end='')
        print("{:8s}".format(self.data['rx_dok'] or '-'), end='')
        print("{:8s}".format(self.data['rx_loc'] or '-'), end='')
        if self.stats:
            print("{:7.1f} ".format(self.stats['distance']), end='')
        else:
            print("{:>7s} ".format('-'), end='')
        if term:
            print()


class QSOManager:
    def __init__(self, my_info, log_file):
        self.my_info = my_info

        self.log_file = log_file

        self.qsos = []
        self.compo = None

        if os.path.exists(log_file):
            self.load(log_file)

            set_output_color("blue")
            print(f"{len(self.qsos)} QSOs geladen.")

        self.next_number = len(self.qsos) + 1

    def load(self, log_file):
        with open(log_file, 'r') as f:
            firstLine = True
            for line in f:
                if firstLine:
                    firstLine = False

                    obj = json.loads(line)
                    if 'class' in obj:
                        self.compo = obj['class']
                        continue # successfully parsed, so this line is not a QSO
                    else:
                        self.compo = None

                q = QSO(self.my_info)
                q.deserialize(line)
                self.qsos.append(q)

    def save(self, log_file=None):
        if not log_file:
            log_file = self.log_file

        if os.path.exists(log_file):
            os.rename(log_file, log_file + "~")

        with open(log_file, 'w') as f:
            meta = {'class': self.compo}
            f.write(json.dumps(meta) + "\n")

            for qso in self.qsos:
                f.write(qso.serialize() + "\n")

    def add_qso_from_string(self, text):
        parts = text.split(' ')
        parts.reverse() # search backwards

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

        q = QSO(self.my_info,
                tx_num=str(self.next_number),
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

    def print_evaluation(self):
        if not self.qsos:
            set_output_color("yellow")
            print("Keine QSOs im Log.")
            return

        total_points = 0
        multi = 0

        seen_doks = set()
        seen_fields = set()

        self.qsos[0].print_table_header(term=False)
        print("Punkte ", end='')
        print("DOK-Multi ", end='')
        print("Loc-Multi ", end='')
        print()

        for i in range(len(self.qsos)):
            q = self.qsos[i]

            points = 0
            if self.my_info['dok'] != q.data['rx_dok']:
                points = round(q.stats['distance'])

            total_points += points

            dok_multi = q.stats['dok'] not in seen_doks and helper.DOKCountsAsMulti(q.stats['dok'])
            field_multi = q.stats['field'] not in seen_fields

            if dok_multi:
                seen_doks.add(q.stats['dok'])
                multi += 1

            if field_multi:
                seen_fields.add(q.stats['field'])
                multi += 1

            if points > 1000:
                set_output_color("red")
            elif points > 300:
                set_output_color("yellow")

            self.qsos[i].print_table_data(i, term=False)
            print(f"{points:6d} ", end='')
            print(f"{dok_multi:9} ", end='')
            print(f"{field_multi:9} ", end='')
            print()

            set_output_color("default")

        score = multi * total_points
        print(f"\nGesamtpunktzahl = Multi × Punkte = {multi} × {total_points} = {score}\n")

        print("QSOs \033[0;33m>300km\033[0m oder \033[0;31m>1000km\033[0m sollten besonders auf Fehler geprüft werden!\n")

    def adif_export(self, filename):
        if not self.qsos:
            set_output_color("yellow")
            print("Keine QSOs im Log.")
            return

        with open(filename, 'w') as adifile:
            # write header
            adifile.write(f"Generated for {self.my_info['call']} in {self.my_info['dok']} - Loc: {self.my_info['loc']}\n\n")
            adifile.write(f"<adif_ver:5>3.0.9\n")
            adifile.write(f"<programid:10>FrankenLog\n")
            adifile.write(f"<USERDEF2:2:N>Nr\n")
            adifile.write(f"<EOH>\n\n")

            for q in self.qsos:
                gmt = time.gmtime(int(q.data['timestamp']))

                d = time.strftime('%Y%m%d', gmt)
                t = time.strftime('%H%M', gmt)

                call = q.data['rx_call']
                dok = q.data['rx_dok']
                loc = q.data['rx_loc']
                nr = q.data['rx_num']

                adifile.write(f"<QSO_DATE:8>{d}\n")
                adifile.write(f"<TIME_ON:4>{t}\n")
                adifile.write(f"<CALL:{len(call)}>{call}\n")
                adifile.write(f"<RST_SENT:2>{q.data['tx_rst']}\n")
                adifile.write(f"<RST_RCVD:2>{q.data['rx_rst']}\n")
                adifile.write(f"<DARC_DOK:{len(dok)}>{dok}\n")
                adifile.write(f"<GRIDSQUARE:{len(loc)}>{loc}\n")
                adifile.write(f"<Nr:{len(nr)}>{nr}\n")
                adifile.write(f"<EOR>\n\n")

    def txt_export(self, filename):
        if not self.qsos:
            set_output_color("yellow")
            print("Keine QSOs im Log.")
            return

        # gather information
        template_info = {}
        template_info['my_call'] = self.my_info['call']
        template_info['my_loc'] = self.my_info['loc']
        template_info['my_dok'] = self.my_info['dok']
        template_info['qth'] = self.my_info['qth']
        template_info['addr'] = self.my_info['addr']
        template_info['name'] = self.my_info['name']
        template_info['nqsos'] = len(self.qsos)
        template_info['today_de'] = time.strftime('%d.%m.%Y')

        # choose strings based on selected competition class
        if self.compo == 'C':
            template_info['compo'] = 'C - 2m (alle Betriebsarten)'
            template_info['band'] = '2 m'
            band = '2'
        elif self.compo == 'D':
            template_info['compo'] = 'D - 70cm (alle Betriebsarten)'
            template_info['band'] = '70 cm'
            band = '70'
        else:
            template_info['compo'] = 'INVALID'
            template_info['band'] = 'INVALID'
            band = '???'

        mode = 'SSB' # FIXME?

        total_points = 0
        dok_multi = 0
        field_multi = 0

        seen_doks = set()
        seen_fields = set()

        template_info['qsotable'] = ""

        for i, q in enumerate(self.qsos):
            q = self.qsos[i]

            points = 0
            if self.my_info['dok'] != q.data['rx_dok']:
                points = round(q.stats['distance'])

            total_points += points

            is_dok_multi = q.stats['dok'] not in seen_doks and helper.DOKCountsAsMulti(q.stats['dok'])
            is_field_multi = q.stats['field'] not in seen_fields

            if is_dok_multi:
                seen_doks.add(q.stats['dok'])
                dok_multi += 1

            if is_field_multi:
                seen_fields.add(q.stats['field'])
                field_multi += 1

            sent = TXT_SENT_TEMPLATE.format(
                    tx_dok = self.my_info['dok'],
                    tx_loc = self.my_info['loc'],
                    tx_rst = q.data['tx_rst'],
                    tx_num = q.data['tx_num'],
                )
            rcvd = TXT_RCVD_TEMPLATE.format(**(q.data))

            gmt = time.gmtime(int(q.data['timestamp']))

            template_info['qsotable'] += TXT_QSO_TEMPLATE.format(
                        nr = i + 1,
                        date = time.strftime('%d%m%y', gmt),
                        utc = time.strftime('%H%M', gmt),
                        call = q.data['rx_call'],
                        band = band,
                        mode = mode,
                        sent = sent,
                        rcvd = rcvd,
                        new_dok = q.stats['dok'] if is_dok_multi else '',
                        new_loc = q.stats['field'] if is_field_multi else '',
                        points = points
                    ) + "\n"

        multi = dok_multi + field_multi
        score = multi * total_points

        template_info['dok_multi'] = dok_multi
        template_info['field_multi'] = field_multi
        template_info['total_multi'] = multi
        template_info['total_points'] = total_points
        template_info['final_score'] = score

        with open(filename, 'w') as txtfile:
            txtfile.write(TXT_TEMPLATE.format(**template_info))

    def loop(self):
        """Main loop."""

        while True:
            set_output_color("magenta")
            print(f"\n<<< 59 {self.next_number:03d} {self.my_info['dok']} {self.my_info['loc']}")
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
                print("w - Auswertung anzeigen")
                print("a - ADIF-Datei exportieren")
                print("t - TXT-Datei exportieren")
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
            elif cmd == 'w':
                self.print_evaluation()
            elif cmd == 'a':
                filename = self.log_file + ".adi"
                self.adif_export(filename)
                set_output_color("green")
                print(f"Exported to: {filename}")
            elif cmd == 't':
                while not self.compo:
                    set_output_color("yellow")
                    print("Teilnahmeklasse nicht gesetzt!")
                    set_output_color("default")
                    compo = input("Wähle die Klasse aus (C = 2m, D = 70cm): ").upper()
                    if compo not in ['C', 'D']:
                        print("Eingabe nicht erkannt. Nur 1 Buchstabe darf eingegeben werden")
                        continue
                    else:
                        self.compo = compo

                filename = self.log_file + ".txt"
                self.txt_export(filename)
                set_output_color("green")
                print(f"Exported to: {filename}")
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

def get_user_info(info_file_name):
    keys = ['call', 'loc', 'dok', 'name', 'addr', 'qth']
    names = ['Rufzeichen', 'Locator', 'DOK', 'Name', 'Straße und Hausnummer', 'PLZ/Ort']
    query_tpl = ['dein {}', 'deinen {}', 'deinen {}', 'deinen {}n', 'deine {}', 'deine PLZ/deinen Ort']
    check_regex = [None, locregex, None, None, None, None]

    my_info = {}

    try:
        with open(info_file_name, 'r') as info_file:
            my_info = json.load(info_file)
    except FileNotFoundError:
        pass
    except Exception as e:
        set_output_color("red")
        print(f"Kann Benutzerinfo nicht aus '{args.info_file}' laden: {str(e)}. Ende.")
        exit(1)

    for idx, k in enumerate(keys):
        while not my_info.get(k):
            set_output_color("yellow")
            print(f"{names[idx]} nicht gesetzt!")
            set_output_color("default")
            inp = input("Gib {} ein: ".format(query_tpl[idx].format(names[idx])))

            if k in ['call', 'loc', 'dok']:
                inp = inp.upper()

            if check_regex[idx]:
                if not check_regex[idx].match(inp):
                    set_output_color("red")
                    print(f"Ungültige Eingabe!")
                    continue

            my_info[k] = inp

    with open(info_file_name, 'w') as info_file:
        try:
            json.dump(my_info, info_file)
        except Exception as e:
            set_output_color("yellow")
            print(f"Kann Benutzerinfo nicht in '{args.info_file}' speichern: {str(e)}.")

    return my_info

parser = argparse.ArgumentParser(description='Logprogramm für die Frankenaktivität.')
parser.add_argument('-o', '--output-file', dest='output_file', type=str, required=True, help='In dieser Datei werden die QSOs gespeichert. Wird beim Start eingelesen.')
parser.add_argument('-i', '--info-file', dest='info_file', type=str, required=True, help='Datei mit Benutzerinformationen. Wird angelegt, wenn sie nicht existiert. Fehlende Infos werden abgefragt.')

args = parser.parse_args()

my_info = get_user_info(args.info_file)

set_output_color("green")
print(f"""
Eigene Info:

    Rufzeichen: {my_info['call']}
    Locator:    {my_info['loc']}
    DOK:        {my_info['dok']}

Gib 'h' für eine Befehlsliste ein.
""")

set_output_color("default")

qsomgr = QSOManager(my_info, args.output_file)

qsomgr.loop()
