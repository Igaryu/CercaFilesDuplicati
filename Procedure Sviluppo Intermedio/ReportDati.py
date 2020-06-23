#!/usr/bin/env python3
'''
Apre il file cdf.sqlite3
Verifica se esistono dati nella tabella Duplicati.
'''

import os, sqlite3, fnmatch, sys
from pathlib import Path
from hashlib import md5

if os.path.exists("/tmp/cfd.sqlite3") is False:
	print("\n\ndata_base cdf.sqlite3 inesistente: deve essere stato creato e scansionato prima di eseguire una visualizzazione!")
	input("Premi [INVIO] per terminare.")
	sys.exit(-9)

data_base=sqlite3.connect("/tmp/cfd.sqlite3")
for numero_record in data_base.execute("select count(*) from Duplicati;"): 
	pass 

if (numero_record[0] ==0 ):
	print('Tavola Duplicati vuota: devi esegure una scansione prima!!')
	data_base.close()
	sys.exit(-1)

print(f'\nCi sono {numero_record[0]} elementi nella tavola Duplicati...\n')

log_file = open('CercaFileDuplicati.log', 'w') 
duplicato=0
for elemento_selezionato_esterno in db.execute("select * from Duplicati;"): 
	duplicato = elemento_selezionato_esterno[1]
	print(f'Il file {elemento_selezionato_esterno[4]} è duplicato in:')
	log_file.write(f'Il file {elemento_selezionato_esterno[4]} è duplicato in:\n')
	for elemento_selezionato_interno in db.execute(f"select * from Duplicati where indiceSrc={duplicato};"): 
		print(f'\t\t --> {elemento_selezionato_interno[4]} ')
		log_file.write(f'\t\t --> {elemento_selezionato_interno[4]} \n')
		
	print('\n')
	log_file.write('\n')	

data_base.close()
log_file.close()
