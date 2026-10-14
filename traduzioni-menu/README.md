# Menù Marechiaro — 19 lingue

Pacchetto completo redatto e revisionato in chat, senza API esterne.

- [Pacchetto completo ZIP](Marechiaro-menu.zip): CSV unico, cinque CSV tabellari, SQL, glossario, registro di revisione, controlli e fonti.
- [CSV unico](Marechiaro-menu.csv): 13.737 campi testuali, 723 per lingua.
- [SQL di importazione](Marechiaro-importazione.sql): importazione delle cinque tabelle di traduzione.

## Scaricare

Aprire il file ZIP su GitHub e premere **Download raw file** (icona di download).
In alternativa, dal menu **Code** del ramo `traduzioni-menu`, scegliere **Download ZIP** e aprire la cartella `traduzioni-menu` nell’archivio.

## Controlli e limiti

ID e riferimenti italiani conservati; 456 traduzioni approvate invariate; nessun duplicato e nessuna traduzione inventata per campi vuoti o null.
Nomi commerciali, produttori e denominazioni preservati. Le anomalie della fonte italiana sono documentate nel pacchetto.

La revisione è assistita AI e non è una certificazione di un traduttore madrelingua.
La sintassi PostgreSQL e PL/pgSQL è stata controllata, ma l’SQL non è stato eseguito su un database.
Supabase non è stato modificato. Prima dell’esecuzione, leggere `LEGGIMI.txt` nel pacchetto e confermare l’importazione.
