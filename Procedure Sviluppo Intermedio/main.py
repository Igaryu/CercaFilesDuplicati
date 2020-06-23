#!/usr/bin/env python3
import os

from ProgrFuncs import lettura_Nodo, normalizzazione_dati, report_dati, cls

cls()

#input("Premi [INVIO] per avviare la procedura di scansione della cartella... ")
lettura_nodo()
print("Scansione cartella eseguita!!\n")
input("Premi [INVIO] per avviare la procedura di Normalizazione dei dati... ")
normalizzazione_dati()
print("\nNormalizzazione dati eseguita!!\n")
input("Premi [INVIO] per avviare la procedura Rapporto dati in CercaFilesDuplicati.log...")
report_dati()
si_no = input("Il file cfd.sqlite3 è presente nella cartella /tmp vuoi cancellarlo? [s/N]: ").upper()

if si_no == "S":
	os.popen("rm /tmp/cfd.sqlite3")
	print("\nFile database /tmp/sqlite3 cancellato!!\n\n")
else:
	print("\nIl file cfd.sqlite3 è presente nella cartella /tmp; puoi usarlo da li o copiarlo dove ti fa più comodo.\n\n")



