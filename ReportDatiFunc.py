#!/usr/bin/env python3
def ReportDati():
	'''
	Apre il file cdf.sqlite3
	Verifica se esistono dati nella tabella Duplicati.
	'''

	import os, sqlite3, fnmatch, sys
	from pathlib import Path
	from hashlib import md5

	if os.path.exists("/tmp/cfd.sqlite3") is False:
		print("\n\nDatabase cdf.sqlite3 inesistente: deve essere stato creato e scansionato prima di eseguire una visualizzazione!")
		input("Premi [INVIO] per terminare.")
		sys.exit(-9)

	db=sqlite3.connect("/tmp/cfd.sqlite3")
	for nrec in  db.execute("select count(*) from Duplicati;"): 
		pass 

	if (nrec[0] ==0 ):
		print('Tavola Duplicati vuota: devi esegure una scansione prima!!')
		db.close()
		sys.exit(-1)

	print(f'\nCi sono {nrec[0]} elementi nella tavola Duplicati...\n')

	logFile = open('CercaFileDuplicati.log', 'w') 
	i1=0
	for i in db.execute("select * from Duplicati;"): 
		i1 = i[1]
		print(f'Il file {i[4]} è duplicato in:')
		logFile.write(f'Il file {i[4]} è duplicato in:\n')
		for k in db.execute(f"select * from Duplicati where indiceSrc={i1};"): 
			print(f'\t\t --> {k[4]} ')
			logFile.write(f'\t\t --> {k[4]} \n')
		
		print('\n')
		logFile.write('\n')	

	db.close()
	logFile.close()