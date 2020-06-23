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

	data_base=sqlite3.connect("/tmp/cfd.sqlite3")
	data_base.execute("delete from Duplicati;")
	data_base.commit()

	for numero_record in  data_base.execute("select count(*) from Sorgente;"): 
		pass 

	numero_record=numero_record[0]
	riga_attuale=0
	print(f"Numero di record presenti nella tabella Sorgente: {numero_record}.")
	for elemento_selezionato_esterno in data_base.execute("select * from Sorgente;"): 
		riga_attuale += 1
		for elemento_selezionato_interno in data_base.execute("select * from Sorgente;"): 
			#print(i[0],i[1],"\t\t",k[0],k[1])
			if (elemento_selezionato_esterno[1] == elemento_selezionato_interno[1]) and (elemento_selezionato_esterno[0] != elemento_selezionato_interno[0]):
				riga_corrente += 1
				#print(f'insert into Duplicati values ("{i[1]}", {i[0]}, {k[0]}, "{i[2]}","{k[2]}");') 
				data_base.execute(f'insert into Duplicati values ("{elemento_selezionato_esterno[1]}", {elemento_selezionato_esterno[0]}, {elemento_selezionato_interno[0]}, "{elemento_selezionato_esterno[2]}","{elemento_selezionato_interno[2]}");') 
		data_base.commit()
		if ((riga_attuale % 100) == 0):
			sys.stdout.write('-')
			sys.stdout.flush()

	print('\n\nNomralizzo tavola Duplicati...')
	riga_attuale=0
	for elemento_selezionato in data_base.execute("select indiceSrc, indiceDest, md5 from Duplicati;"):
		riga_attuale += 1
		data_base.execute(f'delete from Duplicati where indiceSrc!={elemento_selezionato[0]} and md5="{elemento_selezionato[2]}";')
		if (( riga_attuale % 50 ) == 0 ):
			sys.stdout.write('-')
			sys.stdout.flush()	

	data_base.commit()	


	data_base.close()
	print(f"\n\nI = {elemento_selezionato_esterno[0]} e K = {elemento_selezionato_interno[0]} e totali duplicati = {riga_attuale}.")



