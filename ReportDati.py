#!/usr/bin/env python3
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

Database=sqlite3.connect("/tmp/cfd.sqlite3")
for numeroRecord in dataBase.execute("select count(*) from Duplicati;"): 
	pass 

if (numeroRecord[0] ==0 ):
	print('Tavola Duplicati vuota: devi esegure una scansione prima!!')
	dataBase.close()
	sys.exit(-1)

print(f'\nCi sono {numeroRecord[0]} elementi nella tavola Duplicati...\n')

logFile = open('CercaFileDuplicati.log', 'w') 
duplicato=0
for elementoSelezionatoEsterno in db.execute("select * from Duplicati;"): 
	duplicato = elementoSelezionatoEsterno[1]
	print(f'Il file {elementoSelezionatoEsterno[4]} è duplicato in:')
	logFile.write(f'Il file {elementoSelezionatoEsterno[4]} è duplicato in:\n')
	for elementoSelezionatoInterno in db.execute(f"select * from Duplicati where indiceSrc={duplicato};"): 
		print(f'\t\t --> {elementoSelezionatoInterno[4]} ')
		logFile.write(f'\t\t --> {elementoSelezionatoInterno[4]} \n')
		
	print('\n')
	logFile.write('\n')	

db.close()
logFile.close()