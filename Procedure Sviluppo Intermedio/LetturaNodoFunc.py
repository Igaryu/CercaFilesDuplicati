#!/usr/bin/env python3
import os, sqlite3, fnmatch, sys
from pathlib import Path
from hashlib import md5

def cls():
	if name == 'posix':
		system('clear')
	else:
		system('cls')

def LetturaNodo():
	
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


	def check_DirToScan(HomeDir,DirToScan):
		''' 
		Se il parametro esistee, come percorso assoluto, lo restituisce; 

		altrimenti verifica se esiste come percorso relativo alla $HOME e, se si,
		resistuisce il paramentro anteposto dal contenuto di $HOME.

		Se non sono vere nessuna delle due situazioni, segnala l'inesitenza della
		directory ed esce con un error code -9
	
		:param HomeDir Cartella home dell'utente
		:param DirToScan Cartella segnalata dall'utente come oggetto della scansione

		:return percorso assoluto se lo è, altrimenti restituisce la somma dei due paramentri 
		'''	

		if os.path.exists(DirToScan) is True:
			return(DirToScan)
	
	
		if os.path.exists(HomeDir+'/'+DirToScan) is True:
			return(HomeDir+'/'+DirToScan)
		else:
			print("Directory inesistente !!!")
			exit(-9)
	


#######################################
## Fine area funzioni
#######################################

	if os.path.exists("/tmp/cfd.sqlite3") is False:
		print("\n\nDatabase cdf.sqlite3 inesistente: lo creo...")
		dataBase = sqlite3.connect("/tmp/cfd.sqlite3")
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
		dataBase = sqlite3.connect("/tmp/cfd.sqlite3")
		dataBase.execute("delete from Sorgente;")
		dataBase.execute("delete from Duplicati;")
		dataBase.commit()
		print("Database cdf.sqlite3 aperto e pulito!\n\n")


	CurDir = os.getcwd()	
	HomeDir = os.environ['HOME']
	DirToScan = ''
	SiNo = ''

	SiNo = input(f"\n\nDevo usare {CurDir} come directory da scansionare? [s/n] ")
	if SiNo in 'nN':
		DirToScan = input("Digita percorso da scansionare: (è ammesso il path assoluto o relativo rispetto alla propria $HOME)  ")
		DefDirToScan = check_DirToScan(HomeDir,DirToScan)
	else:
		DefDirToScan = check_DirToScan(HomeDir,CurDir)

	cursore = dataBase.cursor()

	number_of_files = os.popen(f'find {DefDirToScan} -type f | wc -l').read()

	print(f'\n\nA seconda del numero di files da elaborare può volerci diverso tempo: nel tuo caso i files sono:{number_of_files}') 
	print('Per ogni file va calcolato il rispettivo hash md5!')
	print('\nOgni trattino corrisponde a 100 files elaborati...\n\n')

	tmpIndice = 0
	for filename in trova_files(DefDirToScan, '*'):
#		wPercorso=filename
		tmpMd5 = md5(Path(filename).read_bytes()).hexdigest()
		tmpIndice += 1
		if ( tmpIndice % 50 ) == 0 :
			sys.stdout.write('-')
			sys.stdout.flush()
		cursore.execute(f'INSERT INTO Sorgente VALUES ({tmpIndice},"{tmpMd5}","{filename}");')
		dataBase.commit()

	dataBase.close()
	print()

	print("\nIl file cfd.sqlite3 è presente nella cartella /tmp; puoi usarlo da li o copiarlo dove ti fa più comodo.\n\n")

