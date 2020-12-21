#!/usr/bin/env python3
'''
    docstring  da scrivere
'''

import sqlite3
import fnmatch
import sys
import os

from pathlib import Path
from hashlib import md5
from progress.bar import Bar
from pyfiglet import Figlet



def cls():
    '''
        Definisce come pulire lo scermo in base all'ambiente operativo.
    '''
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')


def is_numeric(i):
    '''
        Ritorna True se il parametro è numerico
    '''
    try:
        float(i)
        return True
    except ValueError:
        return False

def find_files(directory: str, pattern: str):
    '''
        Trova tutti i files corrispondenti a PATTERN scandendo la
        struttura DIRECTORY
    '''
    for root, _, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def check_dir_to_scan(home_dir: str, dir_to_scan: str):
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

    if os.path.exists(dir_to_scan) is True:
        return dir_to_scan

    if os.path.exists(home_dir+'/'+dir_to_scan) is True:
        return home_dir+'/'+dir_to_scan
    
    print("Directory inesistente !!!")
    sys.exit(-9)


def lettura_nodo():
    '''
        Verfica la presenza di un vecchio database in /tmp
        se non esiste
            crea il database con le tavole e relativi indici
        altrimenti
            apre il database e svuota le tabelle presenti

        Chiede se usare la cartella corrente per la scansione
        se no input per la cartella da scansionare
        Esegue la sconsione e popola la tavola Sorgenti con i relativi dati
    '''

    global FIGLET
    print(FIGLET.renderText('C.F.D.\nScansione Cartella'))

    if os.path.exists("/tmp/cfd.sqlite3") is False:
        print("\n\nDatabase cdf.sqlite3 inesistente: lo creo...")
        data_base = sqlite3.connect("/tmp/cfd.sqlite3")
        data_base.execute('''CREATE TABLE Sorgente (indice INTEGER NOT NULL, md5 TEXT NOT NULL, percorso TEXT NOT NULL, PRIMARY KEY(indice ASC))''')
        data_base.execute('''CREATE INDEX indSrcIndice on Sorgente(indice ASC)''')
        data_base.execute('''CREATE INDEX indMd5 on Sorgente(md5 ASC)''')

        data_base.execute('''CREATE TABLE Duplicati (md5 TEXT NOT NULL, indiceSrc NUMERIC NOT NULL, indiceDest NUMERIC NOT NULL, percorsoSrc TEXT NOT NULL, percorsoDest TEXT NOT NULL)''')
        data_base.execute('''CREATE INDEX indiceMd5 on Duplicati(md5 ASC)''')
        data_base.execute('''CREATE INDEX indiceSrc on Duplicati(indiceSrc ASC)''')
        data_base.execute('''CREATE INDEX indiceDest on Duplicati(indiceDest ASC)''')
        data_base.commit()
        print("\n\nDatabase cdf.sqlite3 creato!\n\n")
    else:
        print("\n\nDatabase cdf.sqlite3 esistente: lo apro...")
        data_base = sqlite3.connect("/tmp/cfd.sqlite3")
        data_base.execute("delete from Sorgente;")
        data_base.execute("delete from Duplicati;")
        data_base.commit()
        print("Database cdf.sqlite3 aperto e pulito!\n\n")


    cur_dir = os.getcwd()
    home_dir = os.environ['HOME']
    dir_to_scan = ''
    dir_exists = 0

    si_no = input(f"\n\nDevo usare {cur_dir} come directory da scansionare? [s/N] ").upper()
    if si_no in 'SN' or si_no == '':
        dir_to_scan = input("Digita percorso da scansionare: (è ammesso il path assoluto o relativo rispetto alla propria $HOME)  ")
        def_dir_to_scan = check_dir_to_scan(home_dir, dir_to_scan)
    else:
        def_dir_to_scan = check_dir_to_scan(home_dir, cur_dir)

    cursore = data_base.cursor()
    numero_files = os.popen(f'find {def_dir_to_scan} -type f | wc -l').read()

    print(f'\n\nA seconda del numero di files da elaborare può volerci diverso tempo: nel tuo caso i files sono:{numero_files}')
    print('Per ogni file va calcolato il rispettivo hash md5!')

    tmp_indice = 0
    bar = Bar('Scansione in corso', max=int(numero_files))

    for filename in find_files(def_dir_to_scan, '*'):

        tmp_md5 = md5(Path(filename).read_bytes()).hexdigest()
        tmp_indice += 1

        if (tmp_indice%50) == 0:
            sys.stdout.write('-')
            sys.stdout.flush()
        cursore.execute(f'INSERT INTO Sorgente VALUES ({tmp_indice},"{tmp_md5}","{filename}");')
        data_base.commit()
        bar.next()

    bar.finish()
    data_base.close()
    print()

def normalizzazione_dati():
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
    global FIGLET
    print(FIGLET.renderText('C.F.D.\nNormalizazione dati...'))

    if os.path.exists("/tmp/cfd.sqlite3") is False:
        print("\n\nDatabase cdf.sqlite3 inesistente: deve essere stato creato e scansionato prima di eseguire una visualizzazione!")
        input("Premi [INVIO] per terminare.")
        sys.exit(-9)

    data_base = sqlite3.connect("/tmp/cfd.sqlite3")
    data_base.execute("delete from Duplicati;")
    data_base.commit()

    for numero_record in  data_base.execute("select count(*) from Sorgente;"):
        pass
    numero_record = numero_record[0]

    numero_di_record = 0
    numero_letture = 0

    print("Avvio procedura di verifica dei duplicati...\n")
    print(f"\nNumero di record presenti nella tabella Sorgente: {numero_record}.\n")

    barra = Bar('Scansione in corso:', max=numero_record)
    for elemento_selezionato_esterno in data_base.execute("select * from Sorgente;"):
        numero_letture += 1
        for elemento_selezionato_interno in data_base.execute("select * from Sorgente;"):
        #    print(f"MD5SUM[1] est+int: \n\t {elemento_selezionato_esterno[1]} \
        #           \n\t {elemento_selezionato_interno[1]}")
        #    print(f"Indice[0] est+int: \n\t {elemento_selezionato_esterno[0]} \
        #           \n\t {elemento_selezionato_interno[0]}")
            if (elemento_selezionato_esterno[1] == elemento_selezionato_interno[1]) and (elemento_selezionato_esterno[0] != elemento_selezionato_interno[0]):
        #        print(f"MD5SUM[1] est+int: \n\t {elemento_selezionato_esterno[1]} \
        #           \n\t {elemento_selezionato_interno[1]}")
        #        print(f"Indice[0] est+int: \n\t {elemento_selezionato_esterno[0]} \
        #           \n\t {elemento_selezionato_interno[0]}")
        #        input("premi un tasto per contniuare")
                numero_di_record += 1
                data_base.execute(f'insert into Duplicati values ("{elemento_selezionato_esterno[1]}", {elemento_selezionato_esterno[0]}, {elemento_selezionato_interno[0]}, "{elemento_selezionato_esterno[2]}","{elemento_selezionato_interno[2]}");')
                data_base.commit()
        barra.next()
    barra.finish()

    print('\n\nNomralizzo tavola Duplicati...')
    numero_letture = 0
    for elemento_selezionato_esterno in data_base.execute("select indiceSrc, indiceDest, md5 from Duplicati;"):
        numero_letture = numero_letture + 1
        for elemento_selezionato_interno in data_base.execute("select indiceSrc, indiceDest, md5 from Duplicati;"):
        #    data_base.execute(f'delete from Duplicati where indiceSrc!={elemento_selezionato_esterno[0]} and md5="{elemento_selezionato_interno[2]}";')
            pass
        if (numero_letture%50) == 0:
            sys.stdout.write('-')
            sys.stdout.flush()

    data_base.commit()

    for numero_record in data_base.execute("select count(*) from Duplicati;"):
        pass

    data_base.close()

    print(f'\n\nNumeroRecordord totali: {elemento_selezionato_interno[0]}, normalizzati: {elemento_selezionato_esterno[0]}, duplicati rimasti: {numero_record[0]}')
    if numero_record[0] == 0:
        print("\nNessun duplicato presente!! Termine elaborazione.\n")
        data_base.close()
        sys.exit(-3)

def report_dati():
    '''
        Apre il file cdf.sqlite3
        Verifica se esistono dati nella tabella Duplicati.
        Se si chiede all'utente se vuole ANCHE il reporto a video, altrimenti
        lo riporta solo nel file CercaFileDuplicati.log
    '''

    cls()
    global FIGLET
    print(FIGLET.renderText('C.F.D.\nReport Dati...'))

    if os.path.exists("/tmp/cfd.sqlite3") is False:
        print("\n\nDatabase cdf.sqlite3 inesistente: deve essere stato creato e scansionato prima di eseguire una visualizzazione!")
        input("Premi [INVIO] per terminare.")
        sys.exit(-9)

    data_base = sqlite3.connect("/tmp/cfd.sqlite3")
    for numero_record in  data_base.execute("select count(*) from Duplicati;"):
        pass

    if numero_record[0] == 0:
        print('\nTavola Duplicati vuota: Non risultano file duplicati in seguito alla scansione!!\n')
        data_base.close()
        sys.exit(-1)

    print(f'\nCi sono {numero_record[0]} elementi nella tavola Duplicati...\n')
    si_no = input('Il report verrà prodotto nel file CercaFileDuplicati.log; vuoi anche il reporto a video? [s/N]').upper()
    log_file = open('CercaFileDuplicati.log', 'w')

    riga_attuale = 0
    for elemento_selezionato_esterno in data_base.execute("select * from Duplicati order by indiceSrc;"):
        riga_attuale = elemento_selezionato_esterno[1]
        if si_no == 'S':
            print(f'Il file {elemento_selezionato_esterno[3]} è duplicato in:')
        log_file.write(f'Il file {elemento_selezionato_esterno[3]} è duplicato in:\n')

        for elemento_selezionato_interno in data_base.execute(f"select * from Duplicati where indiceSrc={riga_attuale} order by percorsoSrc;"):
            if si_no == 'S':
                print(f'\t\t --> {elemento_selezionato_interno[4]} ')
            log_file.write(f'\t\t --> {elemento_selezionato_interno[4]} \n')

        if si_no == 'S':
            print('\n')

        log_file.write('\n')

    data_base.close()
    log_file.close()

    print("\nProcedura di report dati eseguita!! Il rapporto sitrova nel file CercaFileDuplicati.log nella cartella da cui hai lanciato lo script.\n")

####################################################################
#
# Fine Area Funzioni
#
####################################################################
cls()
si_no = ''
FIGLET = Figlet(font='slant')

lettura_nodo()
print("Scansione cartella eseguita!!\n")
input("Premi [INVIO] per avviare la procedura di Normalizazione dei dati... ")

normalizzazione_dati()
print("\nNormalizzazione dati eseguita!!\n")
input("Premi [INVIO] per avviare la procedura Rapporto dati in CercaFilesDuplicati.log...")

report_dati()

si_no = input("Il file cfd.sqlite3 è presente nella cartella /tmp vuoi cancellarlo? [s/N]: ").upper()

if si_no == "S":
    os.popen("rm /tmp/cfd.sqlite3")
    print("\nFile database /tmp/sqlite3 cancellato!!\n\n")
else:
    print("\nIl file cfd.sqlite3 è presente nella cartella /tmp; puoi usarlo da li o copiarlo dove ti fa più comodo.\n\n")
