#!/usr/bin/env python3
'''
Apre il file cdf.sqlite3
Svuota la tabella Duplicati
Calcola quanti record sono presenti nella tabella Sorgente
Esegue un ciclo nidficato confrtontando l'hash del record attuale con quello successivo 
Se l'hash è duplicato crea un record e lo carica in tabella Duplicati
Durante l'elaborazione viene emesso un carattere - ogni 250 record elaborati.
A termine ciclo chiude il database e restituisce le statistiche 
su record lavorati e duplicati trovati.
'''

import os, sqlite3, fnmatch, sys
from pathlib import Path
from hashlib import md5

if os.path.exists("/tmp/cfd.sqlite3") is False:
	print("\n\nDatabase cdf.sqlite3 inesistente: deve essere stato creato e scansionato prima di eseguire una visualizzazione!")
	input("Premi [INVIO] per terminare.")
	sys.exit(-9)

dataBase=sqlite3.connect("/tmp/cfd.sqlite3")
dataBase.execute("delete from Duplicati;")
dataBase.commit()

for numeroRecord in  dataBase.execute("select count(*) from Sorgente;"): 
	pass 

numeroRecord=numeroRecord[0]
contatore=0
print(f"Numero di record presenti nella tabella Sorgente: {numeroRecord}.")
NumeroLetture=0
for elementoSelezionatoEsterno in dataBase.execute("select * from Sorgente;"): 
	NumeroLetture += 1
	for elementoSelezionatoInterno in dataBase.execute("select * from Sorgente;"): 
		#print(i[0],i[1],"\t\t",k[0],k[1])
		if (elementoSelezionatoEsterno[1] == elementoSelezionatoInterno[1]) and (elementoSelezionatoEsterno[0] != elementoSelezionatoInterno[0]):
			contatore += 1
			#print(f'insert into Duplicati values ("{i[1]}", {i[0]}, {k[0]}, "{i[2]}","{k[2]}");') 
			dataBase.execute(f'insert into Duplicati values ("{elementoSelezionatoEsterno[1]}", {elementoSelezionatoEsterno[0]}, {elementoSelezionatoInterno[0]}, "{elementoSelezionatoEsterno[2]}","{elementoSelezionatoInterno[2]}");') 
	dataBase.commit()
	if ((NumeroLetture % 100) == 0):
		sys.stdout.write('-')
		sys.stdout.flush()

print('\n\nNomralizzo tavola Duplicati...')
rigaAttuale=0
for elementoSelezionato in dataBase.execute("select indiceSrc, indiceDest, md5 from Duplicati;"):
	rigaAttuale += 1
	dataBase.execute(f'delete from Duplicati where indiceSrc!={elementoSelezionato[0]} and md5="{elementoSelezionato[2]}";')
	if (( NumeroLetture % 50 ) == 0 ):
		sys.stdout.write('-')
		sys.stdout.flush()	

dataBase.commit()	


dataBase.close()
print(f"\n\nI = {elementoSelezionatoEsterno[0]} e K = {elementoSelezionatoInterno[0]} e totali duplicati = {rigaAttuale}.")



