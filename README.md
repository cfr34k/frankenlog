# FrankenLog

Ein Logprogramm für den Aktivitätswettbewerb Franken (oder andere Conteste, wo
laufende Nummern und DOKs ausgetauscht werden).

## Motivation

Wer kennt das nicht: die Gegenstation gibt ihre Daten in einer Reihenfolge, die
nicht zum eigenen Log-Programm passt oder korrigiert nochmal nach, wenn
eigentlich schon alles eingetragen ist. In beiden Fällen muss man erstmal das
richtige Feld in der GUI suchen und überschreiben, was im Contest unnötigen
Stress bedeutet.

Mit diesem simplen, textbasieren Logprogramm können die ausgetauschten Infos in
beliebiger Reihenfolge einfach hintereinander geschrieben werden. Das Programm
sucht sich anhand bestimmter Muster heraus, was ein Rufzeichen, ein Rapport,
ein Locator oder eine laufende Nummer ist. Der jeweils zuletzt gefundene
Eintrag zählt.

Ein Beispiel:

DA0XX gibt _59007 B99 JN59mo_, korrigiert nachträglich aber die Nummer nochmal auf _008_. Im Tool sieht das beispielsweise so aus:

```
<<< 59 021 B26 JN59gb
> da0xx 59007 b99 jn59mo 59008


QSO# Zeit              TX RST/Nr.   RX Rufz.     RX RST/Nr.   RX DOK  RX Loc. 
  20 2019-05-12 13:46  59 021       DA0XX        59 008       B99     JN59MO  
```

Sollte einmal eine Zeile fehlerhaft zerlegt werden, kann das QSO nachträglich korrigiert werden. Dabei wird auch die ursprüngliche Eingabezeile als Referenz angezeigt.

## Einrichtung und Verwendung

Frankenlog ist ein Skript, das in jeder Python-3-Umgebung ausgeführt werden
kann. Es werden keine externen Abhängigkeiten verwendet.

Das Skript kann wie folgt gestartet werden:

```sh
./frankenlog.py -i meine.info -o klasse_c.log
```

In der Datei `meine.info` wird anschließend die Information über die eigene
Station gespeichert, in `klasse_c.log` landen die Logeinträge. Beide Dateien
können natürlich beliebig benannt werden.

Nach dem Start fragt das Programm die für den Log-Export erforderlichen
Informationen zur Station ab. Sobald alles eingetragen wurde, kann direkt mit
dem Loggen begonnen werden.

## Features

- Automatisches Zerlegen der Eingabe nach
  - Rufzeichen
  - Eingehendes RST
  - Eingehende Nummer
  - DOK
  - Locator
- Kurzbefehl (e) zur Korrektur des letzten QSOs
- Nachträgliche Korrektur beliebiger QSOs (b)
- Auswertung mit Punktzahl- und Multiplikator-Berechnung
- ADIF-Export (kann im HamFranken eingelesen werden)
- Cabrillo-Export (einzusendendes Format seit 2022)

Bei der Korrektur gibt es keine Einschränkungen durch die Mustererkennung. Das
ist nützlich, wenn z.B. ein Sonder-DOK nicht automatisch erkannt wurde.

## Lizenz

Dieses Programm ist freie Software unter der GPL v3 (siehe LICENSE).
