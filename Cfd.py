#!/usr/bin/env python3
import sqlite3, fnmatch, sys, os

from pathlib import Path
from hashlib import md5
from progress.bar import Bar
from pyfiglet import Figlet



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
	global figLet
	print( figLet.renderText('Cerca file Diplicati...'))

	if os.path.exists("/tmp/cfd.sqlite3") is False:
		print("\n\nDatabase cdf.sqlite3 inesistente: lo creo...")
		dataBase=sqlite3.connect("/tmp/cfd.sqlite3")
		dataBase.execute('''CREATE TABLE Sorgente (indice INTEGER PRIMARY KEY, md5 TEXT, percorso TEST)''')
		dataBase.execute('''CREATE INDEX indSrcIndice on Sorgente(indice ASC)''')
		dataBase.execute('''CREATE INDEX indMd5 on Sorgente(md5 ASC)''')	

		dataBase.execute('''CREATE TABLE Duplicati (md5 TEXT, indiceSrc NUMERIC, indiceDest NUMERIC,percorsoSrc TEXT, percorsoDest TEXT)''')
		dataBase.execute('''CREATE INDEX indiceMd5 on Duplicati(md5 ASC)''')	
		dataBase.execute('''CREATE INDEX indiceSrc on Duplicati(indiceSrc ASC)''')	
		dataBase.execute('''CREATE INDEX indiceDest on Duplicati(indiceDest ASC)''')	
		dataBase.commit()
		print("\n\nDatabase cdf.sqlite3 creato!\n\n")
	else:
		print("\n\nDatabase cdf.sqlite3 esistente: lo apro...")
		dataBase=sqlite3.connect("/tmp/cfd.sqlite3")
		dataBase.execute("delete from Sorgente;")
		dataBase.execute("delete from Duplicati;")
		dataBase.commit()
		print("Database cdf.sqlite3 aperto e pulito!\n\n")


	CurDir=os.getcwd()	
	HomeDir= os.environ['HOME']
	DirToScan = ''
	DirExists = 0
	SiNo = ''

	SiNo = input(f"\n\nDevo usare {CurDir} come directory da scansionare? [s/N] ")
	if SiNo in 'SnNn' or SiNo == '':
		DirToScan=input("Digita percorso da scansionare: (è ammesso il path assoluto o relativo rispetto alla propria $HOME)  ")
		DefDirToScan = check_DirToScan(HomeDir,DirToScan)
	else:
		DefDirToScan = check_DirToScan(HomeDir,CurDir)

	cursore=dataBase.cursor()

	numeroFiles=os.popen(f'find {DefDirToScan} -type f | wc -l').read()

	print(f'\n\nA seconda del numero di files da elaborare può volerci diverso tempo: nel tuo caso i files sono:{numeroFiles}') 
	print('Per ogni file va calcolato il rispettivo hash md5!')
	
	tmpIndice = 0
	bar = Bar('Scansione in corso', max=int(numeroFiles))
	for filename in find_files(DefDirToScan, '*'):
#		wPercorso=filename
		tmpMd5 = md5(Path(filename).read_bytes()).hexdigest()
		tmpIndice += 1
		if (( tmpIndice % 50 ) == 0 ):
			sys.stdout.write('-')
			sys.stdout.flush()
		cursore.execute(f'INSERT INTO Sorgente VALUES ({tmpIndice},"{tmpMd5}","{filename}");')
		dataBase.commit()
		bar.next()
	bar.finish()
	dataBase.close()
	print()


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

	cls()
	global figLet
	print( figLet.renderText('Cerca file Diplicati...'))
	
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
	numeroDiRecord=0
	print("Avvio procedura di verifica dei duplicati...\n")
	print(f"\nNumero di record presenti nella tabella Sorgente: {numeroRecord}.\n")
	numeroLetto=0
	bar = Bar('Scansione in corso:', max=numeroRecord)
	for elementoSelezionatoEsterno in dataBase.execute("select * from Sorgente;"): 
		numeroLetto += 1
		for elementoSelezionatoInterno in dataBase.execute("select * from Sorgente;"): 
			#print(i[0],i[1],"\t\t",k[0],k[1])
			if (elementoSelezionatoEsterno[1] == elementoSelezionatoInterno[1]) and (elementoSelezionatoEsterno[0] != elementoSelezionatoInterno[0]):
				numeroDiRecord += 1
				#print(f'insert into Duplicati values ("{i[1]}", {i[0]}, {k[0]}, "{i[2]}","{k[2]}");') 
				dataBase.execute(f'insert into Duplicati values ("{elementoSelezionatoEsterno[1]}", {elementoSelezionatoEsterno[0]}, {elementoSelezionatoInterno[0]}, "{elementoSelezionatoEsterno[2]}","{elementoSelezionatoInterno[2]}");')	
		dataBase.commit()
		bar.next()
	bar.finish()
#		if ((numeroLetto % 50) == 0):
#			sys.stdout.write('-')
#			sys.stdout.flush()

	print('\n\nNomralizzo tavola Duplicati...')
	numeroLetto=0
	for elementoSelezionatoEsterno in dataBase.execute("select indiceSrc, indiceDest, md5 from Duplicati;"):
		numeroLetto = numeroLetto + 1
		for elementoSelezionatoInterno in dataBase.execute("select indiceSrc, indiceDest, md5 from Duplicati;"):
			dataBase.execute(f'delete from Duplicati where indiceSrc!={elementoSelezionatoEsterno[0]} and md5="{elementoSelezionatoInterno[2]}";')
		
		if (( numeroLetto % 50 ) == 0 ):
			sys.stdout.write('-')
			sys.stdout.flush()	
 
	dataBase.commit()	
	
	for numeroRecord in dataBase.execute("select count(*) from Duplicati;"):
		pass
	
	dataBase.close()

	print(f'\n\numeroRecordord totali: {elementoSelezionatoInterno[0]}, normalizzati: {elementoSelezionatoEsterno[0]}, duplicati rimasti: {numeroRecord[0]}')
	if numeroRecord[0] == 0:
		print("\nNessun duplicato presente!! Termine elaborazione.\n")
		dataBase.close()
		sys.exit(-3)

def ReportDati():
	'''
	Apre il file cdf.sqlite3
	Verifica se esistono dati nella tabella Duplicati.
	'''

	cls()

	if os.path.exists("/tmp/cfd.sqlite3") is False:
		print("\n\nDatabase cdf.sqlite3 inesistente: deve essere stato creato e scansionato prima di eseguire una visualizzazione!")
		input("Premi [INVIO] per terminare.")
		sys.exit(-9)

	dataBase=sqlite3.connect("/tmp/cfd.sqlite3")
	for numeroRecord in  dataBase.execute("select count(*) from Duplicati;"): 
		pass 

	if (numeroRecord[0] == 0 ):
		print('\nTavola Duplicati vuota: Non risultano file duplicati in seguito alla scansione!!\n')
		dataBase.close()
		sys.exit(-1)

	print(f'\nCi sono {numeroRecord[0]} elementi nella tavola Duplicati...\n')
	SiNo=input('Il report verrà prodotto nel file CercaFileDuplicati.log; vuoi anche il reporto a video? [s/N]').upper()
	logFile = open('CercaFileDuplicati.log', 'w') 
	rigaAttuale=0
	for elementoSelezionatoEsterno in dataBase.execute("select * from Duplicati order by indiceSrc;"): 
		rigaAttuale = elementoSelezionatoEsterno[1]
		if SiNo == 'S':
			print(f'Il file {elementoSelezionatoEsterno[3]} è duplicato in:')
		logFile.write(f'Il file {elementoSelezionatoEsterno[3]} è duplicato in:\n')
		for elementoSelezionatoInterno in dataBase.execute(f"select * from Duplicati where indiceSrc={rigaAttuale} order by percorsoSrc;"):
			if SiNo == 'S': 
				print(f'\t\t --> {elementoSelezionatoInterno[4]} ')
				logFile.write(f'\t\t --> {elementoSelezionatoInterno[4]} \n')
			else:
				logFile.write(f'\t\t --> {elementoSelezionatoInterno[4]} \n')
		
		if SiNo == 'S':
			print('\n')

		logFile.write('\n')	

	dataBase.close()
	logFile.close()

	print("\nProcedura di report dati eseguita!! Il rapporto sitrova nel file CercaFileDuplicati.log nella cartella da cui hai lanciato lo script.\n")

####################################################################
#
# Fine Area Funzioni
#
####################################################################




#!/usr/bin/env python3

cls()

#input("Premi [INVIO] per avviare la procedura di scansione della cartella... ")
figLet = Figlet(font='slant')
#print (figLet.renderText('Cerca file Diplicati...'))

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



