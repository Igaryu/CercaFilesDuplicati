#!/usr/bin/env python3
import os

from ProgrFuncs import LetturaNodo, NormalizzazioneDati, ReportDati, cls

cls()

#input("Premi [INVIO] per avviare la procedura di scansione della cartella... ")
LetturaNodo()
print("Scansione cartella eseguita!!\n")
input("Premi [INVIO] per avviare la procedura di Normalizazione dei dati... ")
NormalizzazioneDati()
print("\nNormalizzazione dati eseguita!!\n")
input("Premi [INVIO] per avviare la procedura Rapporto dati in CercaFilesDuplicati.log...")
ReportDati()
SiNo = input("Il file cfd.sqlite3 è presente nella cartella /tmp vuoi cancellarlo? [s/N]: ").upper()

if SiNo == "S":
	os.popen("rm /tmp/cfd.sqlite3")
	print("\nFile database /tmp/sqlite3 cancellato!!\n\n")
else:
	print("\nIl file cfd.sqlite3 è presente nella cartella /tmp; puoi usarlo da li o copiarlo dove ti fa più comodo.\n\n")



