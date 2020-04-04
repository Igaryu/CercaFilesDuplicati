#!/usr/bin/env python3

from ProgrFuncs import LetturaNodo, NormalizzazioneDati, ReportDati, cls

cls()

input("Premi [INVIO] per avviare la procedura di scansione della cartella... ")
LetturaNodo()
print("Scansione cartella eseguita!!\n")
input("Premi [INVIO] per avviare la procedura di Normalizazione dei dati... ")
NormalizzazioneDati()
print("\nNormalizzazione dati eseguita!!\n")
input("Premi [INVIO] per avviare la procedura di Visualizazione dei dati\n\
Verra creato inoltre un file id log con gli stessi dati del video che\n\
si chiama: CercaFilesDuplicati.log... ")
ReportDati()

