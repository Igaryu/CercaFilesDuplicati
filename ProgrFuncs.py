#!/usr/bin/env python3
import sqlite3, fnmatch, sys, os

from pathlib import Path
from hashlib import md5



def cls():
	if os.name == 'posix':
		os.system('clear')
	else:
		os.system('cls')#!/usr/bin/env python3


def is_numeric(i):
	''' Ritorna True se il parametro è numerico '''
	try:
		float(i)
		return True
	except ValueError:
		return False

def find_files(directory, pattern):
	for root, dirs, files in os.walk(directory):
		for basename in files:
			if fnmatch.fnmatch(basename, pattern):
				filename = os.path.join(root, basename)
				yield filename


def check_DirToScan(HomeDir,DirToScan):
	''' 
	Se il parametro esistee, come percorso assoluto, lo restituisce; 
	altrimenti verifica se esiste come percorso relativo alla $HOME e, se si,
	resistuisce il paramentro anteposto dal contenuto di $HOME.

	Se non sono vere nessuna delle due situazioni, segnala l'inesitenza della
	directory ed esce con un error code -9
	
	:param HomeDir Cartella home dell'utente
	:param DirToScan Cartella segnalata dall'utente come oggetto della scansione

	:return percorso assoluto se lo è altrimenti restituisce la somma dei due paramentri 
	'''	

	if (os.path.exists(DirToScan) is True):
		return(DirToScan)
	
	
	if (os.path.exists(HomeDir+'/'+DirToScan) is True):
		return(HomeDir+'/'+DirToScan)
	else:
		print("Directory inesistente !!!")
		exit(-9)



def LetturaNodo():

	if os.path.exists("/tmp/cfd.sqlite3") is False:
		print("\n\nDatabase cdf.sqlite3 inesistente: lo creo...")
		db=sqlite3.connect("/tmp/cfd.sqlite3")
		db.execute('''CREATE TABLE Sorgente (indice INTEGER PRIMARY KEY, md5 TEXT, percorso TEST)''')
		db.execute('''CREATE INDEX indSrcIndice on Sorgente(indice ASC)''')
		db.execute('''CREATE INDEX indMd5 on Sorgente(md5 ASC)''')	

		db.execute('''CREATE TABLE Duplicati (md5 TEXT, indiceSrc NUMERIC, indiceDest NUMERIC,percorsoSrc TEXT, percorsoDest TEXT)''')
		db.execute('''CREATE INDEX indiceMd5 on Duplicati(md5 ASC)''')	
		db.execute('''CREATE INDEX indiceSrc on Duplicati(indiceSrc ASC)''')	
		db.execute('''CREATE INDEX indiceDest on Duplicati(indiceDest ASC)''')	
		db.commit()
		print("\n\nDatabase cdf.sqlite3 creato!\n\n")
	else:
		print("\n\nDatabase cdf.sqlite3 esistente: lo apro...")
		db=sqlite3.connect("/tmp/cfd.sqlite3")
		db.execute("delete from Sorgente;")
		db.execute("delete from Duplicati;")
		db.commit()
		print("Database cdf.sqlite3 aperto e pulito!\n\n")


	CurDir=os.getcwd()	
	HomeDir= os.environ['HOME']
	DirToScan = ''
	DirExists = 0
	SN = ''

	SN = input(f"\n\nDevo usare {CurDir} come directory da scansionare? [s/N] ")
	if SN=='n' or SN=='N' or SN=='':
		DirToScan=input("Digita percorso da scansionare: (è ammesso il path assoluto o relativo rispetto alla propria $HOME)  ")
		DefDirToScan = check_DirToScan(HomeDir,DirToScan)
	else:
		DefDirToScan = check_DirToScan(HomeDir,CurDir)

	curs=db.cursor()

	NumFiles=os.popen(f'find {DefDirToScan} -type f | wc -l').read()

	print(f'\n\nA seconda del numero di files da elaborare può volerci diverso tempo: nel tuo caso i files sono:{NumFiles}') 
	print('Per ogni file va calcolato il rispettivo hash md5!')
	print('\nOgni trattino corrisponde a 50 files elaborati...\n\n')

	wIndice = 0
	for filename in find_files(DefDirToScan, '*'):
#		wPercorso=filename
		wMd5 = md5(Path(filename).read_bytes()).hexdigest()
		wIndice += 1
		if (( wIndice % 50 ) == 0 ):
			sys.stdout.write('-')
			sys.stdout.flush()
		curs.execute(f'INSERT INTO Sorgente VALUES ({wIndice},"{wMd5}","{filename}");')
		db.commit()

	db.close()
	print()

	print("\nIl file cfd.sqlite3 è presente nella cartella /tmp; puoi usarlo da li o copiarlo dove ti fa più comodo.\n\n")



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
	print(f"\nNumero di record presenti nella tabella Sorgente: {nrec}.")
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
		if ((NumRead % 50) == 0):
			sys.stdout.write('-')
			sys.stdout.flush()

	print('\n\nNomralizzo tavola Duplicati...')
	NumRead=0
	for i in db.execute("select indiceSrc, indiceDest, md5 from Duplicati;"):
		NumRead += 1
		for k in db.execute("select indiceSrc, indiceDest, md5 from Duplicati;"):
			db.execute(f'delete from Duplicati where indiceSrc!={i[0]} and md5="{k[2]}";')
		
		if (( NumRead % 50 ) == 0 ):
			sys.stdout.write('-')
			sys.stdout.flush()	
 
	db.commit()	


	db.close()
	print(f'\n\nRecord totali: {k[0]}, normalizzati: {i[0]}, duplicati rimasti: {NumRead}')

def ReportDati():
	'''
	Apre il file cdf.sqlite3
	Verifica se esistono dati nella tabella Duplicati.
	'''

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
	for i in db.execute("select * from Duplicati order by indiceSrc;"): 
		i1 = i[1]
		print(f'Il file {i[3]} è duplicato in:')
		logFile.write(f'Il file {i[3]} è duplicato in:\n')
		for k in db.execute(f"select * from Duplicati where indiceSrc={i1} order by percorsoSrc;"): 
			print(f'\t\t --> {k[4]} ')
			logFile.write(f'\t\t --> {k[4]} \n')
		
		print('\n')
		logFile.write('\n')	

	db.close()
	logFile.close()
