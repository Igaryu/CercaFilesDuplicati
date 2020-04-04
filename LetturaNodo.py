#!/usr/bin/env python3
import os, sqlite3, fnmatch, sys
from pathlib import Path
from hashlib import md5

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
	


#######################################
## Fine area funzioni
#######################################

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

SN = input(f"\n\nDevo usare {CurDir} come directory da scansionare? [s/n] ")
if SN in 'nN':
	DirToScan=input("Digita percorso da scansionare: (è ammesso il path assoluto o relativo rispetto alla propria $HOME)  ")
	DefDirToScan = check_DirToScan(HomeDir,DirToScan)
else:
	DefDirToScan = check_DirToScan(HomeDir,CurDir)

curs=db.cursor()

NumFiles=os.popen(f'find {DefDirToScan} -type f | wc -l').read()

print(f'\n\nA seconda del numero di files da elaborare può volerci diverso tempo: nel tuo caso i files sono:{NumFiles}') 
print('Per ogni file va calcolato il rispettivo hash md5!')
print('\nOgni trattino corrisponde a 100 files elaborati...\n\n')

wIndice = 0
for filename in find_files(DefDirToScan, '*'):
#	wPercorso=filename
	wMd5 = md5(Path(filename).read_bytes()).hexdigest()
	wIndice += 1
	if (( wIndice % 50 ) == 0 ):
		sys.stdout.write('-')
		sys.stdout.flush()
	curs.execute(f'INSERT INTO Sorgente VALUES ({wIndice},"{wMd5}","{filename}");')
	db.commit()

db.close()
print()

SN = input("\n\nCancello il file database di lavoro da /tmp? [s/n]")
if SN in 'sS':
	os.remove("/tmp/cfd.sqlite3")
	print("\nIl file cfd.sqlite3 è stato cancellato dalla cartella /tmp.\n")
else:
	print("\nIl file cfd.sqlite3 è presente nella cartella /tmp; puoi usarlo da li o copiarlo dove ti fa più comodo.\n\n")


