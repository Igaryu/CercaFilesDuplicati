#!/usr/bin/env python3
def NormalizzazioneDati():
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

	db=sqlite3.connect("/tmp/cfd.sqlite3")
	db.execute("delete from Duplicati;")
	db.commit()

	for nrec in  db.execute("select count(*) from Sorgente;"): 
		pass 

	nrec=nrec[0]
	dd=0
	print(f"Numero di record presenti nella tabella Sorgente: {nrec}.")
	NumRead=0
	for i in db.execute("select * from Sorgente;"): 
		NumRead += 1
		for k in db.execute("select * from Sorgente;"): 
			#print(i[0],i[1],"\t\t",k[0],k[1])
			if (i[1] == k[1]) and (i[0] != k[0]):
				dd += 1
				#print(f'insert into Duplicati values ("{i[1]}", {i[0]}, {k[0]}, "{i[2]}","{k[2]}");') 
				db.execute(f'insert into Duplicati values ("{i[1]}", {i[0]}, {k[0]}, "{i[2]}","{k[2]}");') 
		db.commit()
		if ((NumRead % 100) == 0):
			sys.stdout.write('-')
			sys.stdout.flush()

	print('\n\nNomralizzo tavola Duplicati...')
	NumRead=0
	for i in db.execute("select indiceSrc, indiceDest, md5 from Duplicati;"):
		NumRead += 1
		db.execute(f'delete from Duplicati where indiceSrc!={i[0]} and md5="{i[2]}";')
		if (( NumRead % 50 ) == 0 ):
			sys.stdout.write('-')
			sys.stdout.flush()	

	db.commit()	


	db.close()
	print(f"\n\nI = {i[0]} e K = {k[0]} e totali duplicati = {NumRead}.")



