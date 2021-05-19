#!/usr/bin/env python3
import sqlite3, fnmatch, sys, os

from pathlib import Path
from hashlib import md5



def cls():
	if os.name == 'posix':
		os.system('clear')
	else:
		os.system('cls')#!/usr/bin/env python3


def e_un_numero(i):
	''' Ritorna True se il parametro è numerico '''
	try:
		float(i)
		return True
	except ValueError:
		return False

def trova_files(directory, pattern):
	for root, dirs, files in os.walk(directory):
		for basename in files:
			if fnmatch.fnmatch(basename, pattern):
				filename = os.path.join(root, basename)
				yield filename


def check_dir_to_scan(home_dir,dir_to_scan):
	''' 
	Se il parametro esistee, come percorso assoluto, lo restituisce; 
	altrimenti verifica se esiste come percorso relativo alla $HOME e, se si,
	resistuisce il paramentro anteposto dal contenuto di $HOME.

	Se non sono vere nessuna delle due situazioni, segnala l'inesitenza della
	directory ed esce con un error code -9
	
	:param home_dir Cartella home dell'utente
	:param dir_to_scan Cartella segnalata dall'utente come oggetto della scansione

	:return percorso assoluto se lo è altrimenti restituisce la somma dei due paramentri 
	'''	

	if (os.path.exists(dir_to_scan) is True):
		return(dir_to_scan)
	
	
	if (os.path.exists(home_dir+'/'+dir_to_scan) is True):
		return(home_dir+'/'+dir_to_scan)
	else:
		print("Directory inesistente !!!")
		exit(-9)



def lettura_nodo():

	if os.path.exists("/tmp/cfd.sqlite3") is False:
		print("\n\nDatabase cdf.sqlite3 inesistente: lo creo...")
		data_base=sqlite3.connect("/tmp/cfd.sqlite3")
		data_base.execute('''CREATE TABLE Sorgente (indice INTEGER PRIMARY KEY, md5 TEXT, percorso TEST)''')
		data_base.execute('''CREATE INDEX indSrcIndice on Sorgente(indice ASC)''')
		data_base.execute('''CREATE INDEX indMd5 on Sorgente(md5 ASC)''')	

		data_base.execute('''CREATE TABLE Duplicati (md5 TEXT, indiceSrc NUMERIC, indiceDest NUMERIC,percorsoSrc TEXT, percorsoDest TEXT)''')
		data_base.execute('''CREATE INDEX indiceMd5 on Duplicati(md5 ASC)''')	
		data_base.execute('''CREATE INDEX indiceSrc on Duplicati(indiceSrc ASC)''')	
		data_base.execute('''CREATE INDEX indiceDest on Duplicati(indiceDest ASC)''')	
		data_base.commit()
		print("\n\nDatabase cdf.sqlite3 creato!\n\n")
	else:
		print("\n\nDatabase cdf.sqlite3 esistente: lo apro...")
		data_base=sqlite3.connect("/tmp/cfd.sqlite3")
		data_base.execute("delete from Sorgente;")
		data_base.execute("delete from Duplicati;")
		data_base.commit()
		print("Database cdf.sqlite3 aperto e pulito!\n\n")


	cur_dir = os.getcwd()	
	home_dir = os.environ['HOME']
	dir_to_scan = ''
	dir_exists = 0
	si_no = ''

	si_no = input(f"\n\nDevo usare {cur_dir} come directory da scansionare? [s/N] ")
	if si_no in 'SsNn ':
		dir_to_scan=input("Digita percorso da scansionare: (è ammesso il path assoluto o relativo rispetto alla propria $HOME)  ")
		dir_to_scan = check_dir_to_scan(home_dir,dir_to_scan)
	else:
		dir_to_scan = check_dir_to_scan(home_dir,cur_dir)

	cursore=data_base.cursoreor()

	numero_files=os.popen(f'find {dir_to_scan} -type f | wc -l').read()

	print(f'\n\nA seconda del numero di files da elaborare può volerci diverso tempo: nel tuo caso i files sono:{numero_files}') 
	print('Per ogni file va calcolato il rispettivo hash md5!')
	print('\nOgni trattino corrisponde a 50 files elaborati...\n\n')

	tmp_indice = 0
	for filename in trova_files(dir_to_scan, '*'):
		tmp_md5 = md5(Path(filename).read_bytes()).hexdigest()
		tmp_indice += 1
		if (( tmp_indice % 50 ) == 0 ):
			sys.stdout.write('-')
			sys.stdout.flush()
		cursore.execute(f'INSERT INTO Sorgente VALUES ({tmp_indice},"{tmoMd5}","{filename}");')
		data_base.commit()

	data_base.close()
	print()


def normalizzazione_dati():
	'''
	Apre il file cdf.sqlite3
	Svuota la ta/elemento_selezionato_esternobella Duplicati
	Calcola quanti record sono presenti nella tabella Sorgente
	Esegue un ciclo nidficato confrtontando l'hash del record attuale con quello successivo 
	Se l'hash è duplicato crea un record e lo carica in tabella Duplicati
	Durante l'elaborazione viene emesso un carattere - ogni 250 record elaborati.
	A termine ciclo chiude il database e restituisce le statistiche 
	su record lavorati e duplicati trovati.
	'''

	cls()
	if os.path.exists("/tmp/cfd.sqlite3") is False:
		print("\n\nDatabase cdf.sqlite3 inesistente: deve essere stato creato e scansionato prima di eseguire una visualizzazione!")
		input("Premi [INVIO] per terminare.")
		sys.exit(-9)

	data_base = sqlite3.connect("/tmp/cfd.sqlite3")
	data_base.execute("delete from Duplicati;")
	data_base.commit()

	for numero_record in  data_base.execute("select count(*) from Sorgente;"): 
		pass 

	numero_record = numero_record[0]
	riga_attuale = 0
	print("Avvio procedura di verifica dei duplicati...\n")
	print(f"\nNumero di record presenti nella tabella Sorgente: {numero_record}.\n")
	numero_letto = 0
	for elemento_selezionato_esterno in data_base.execute("select * from Sorgente;"): 
		numero_letto += 1
		for elemento_selezionato_interno in data_base.execute("select * from Sorgente;"): 
			#print(i[0],i[1],"\t\t",k[0],k[1])
			if (elemento_selezionato_esterno[1] == elemento_selezionato_interno[1]) and (elemento_selezionato_esterno[0] != elemento_selezionato_interno[0]):
				riga_attuale += 1
				#print(f'insert into Duplicati values ("{i[1]}", {i[0]}, {k[0]}, "{i[2]}","{k[2]}");') 
				data_base.execute(f'insert into Duplicati values ("{elemento_selezionato_esterno[1]}", {elemento_selezionato_esterno[0]}, {elemento_selezionato_interno[0]}, "{elemento_selezionato_esterno[2]}","{elemento_selezionato_interno[2]}");') 
		data_base.commit()
		if ((numero_letto % 50) == 0):
			sys.stdout.write('-')
			sys.stdout.flush()

	print('\n\nNomralizzo tavola Duplicati...')
	numero_letto = 0
	for elemento_selezionato_esterno in data_base.execute("select indiceSrc, indiceDest, md5 from Duplicati;"):
		numero_letto = numero_letto + 1
		for elemento_selezionato_interno in data_base.execute("select indiceSrc, indiceDest, md5 from Duplicati;"):
			data_base.execute(f'delete from Duplicati where indiceSrc!={elemento_selezionato_esterno[0]} and md5="{elemento_selezionato_interno[2]}";')
		
		if (( numero_letto % 50 ) == 0 ):
			sys.stdout.write('-')
			sys.stdout.flush()	
 
	data_base.commit()	
	
	for numero_righe in data_base.execute("select count(*) from Duplicati;"):
		pass
	

	data_base.close()
	print(f'\n\numero_recordord totali: {elemento_selezionato_interno[0]}, normalizzati: {elemento_selezionato_esterno[0]}, duplicati rimasti: {numero_righe[0]}')
	if numero_righe[0] == 0:
		print("\nNessun duplicato presente!! Termine elaborazione.\n")
		data_base.close()
		sys.exit(-3)

def report_dati():
	'''
	Apre il file cdf.sqlite3
	Verifica se esistono dati nella tabella Duplicati.
	'''

	cls()

	if os.path.exists("/tmp/cfd.sqlite3") is False:
		print("\n\nDatabase cdf.sqlite3 inesistente: deve essere stato creato e scansionato prima di eseguire una visualizzazione!")
		input("Premi [INVIO] per terminare.")
		sys.exit(-9)

	data_base = sqlite3.connect("/tmp/cfd.sqlite3")
	for numero_record in  data_base.execute("select count(*) from Duplicati;"): 
		pass 

	if (numero_record[0] == 0 ):
		print('\nTavola Duplicati vuota: Non risultano file duplicati in seguito alla scansione!!\n')
		data_base.close()
		sys.exit(-1)

	print(f'\nCi sono {numero_record[0]} elementi nella tavola Duplicati...\n')
	si_no = input('Il report verrà prodotto nel file CercaFileDuplicati.log; vuoi anche il reporto a video? [s/N]').upper()
	log_file = open('CercaFileDuplicati.log', 'w') 
	tmp_contatore = 0
	for elemento_selezionato_esterno in data_base.execute("select * from Duplicati order by indiceSrc;"): 
		tmp_contatore = elemento_selezionato_esterno[1]
		if si_no == 'S':
			print(f'Il file {elemento_selezionato_esterno[3]} è duplicato in:')
		log_file.write(f'Il file {i[3]} è duplicato in:\n')
		for elemento_selezionato_interno in data_base.execute(f"select * from Duplicati where indiceSrc={tmp_contatore} order by percorsoSrc;"):
			if si_no == 'S': 
				print(f'\t\t --> {elemento_selezionato_interno[4]} ')
				log_file.write(f'\t\t --> {elemento_selezionato_interno[4]} \n')
			else:
				log_file.write(f'\t\t --> {elemento_selezionato_interno[4]} \n')
		
		if si_no == 'S':
			print('\n')

		log_file.write('\n')	

	data_base.close()
	log_file.close()

	print("\nProcedura di report dati eseguita!! Il rapporto sitrova nel file CercaFileDuplicati.log nella cartella da cui hai lanciato lo script.\n")
