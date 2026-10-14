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

## Tutti i file separati

[Apri la cartella con tutti i file](file-separati). Ogni file è disponibile singolarmente senza estrarre lo ZIP.

- [Categorie](file-separati/tabelle_supabase/menu_category_translations.csv)
- [Sottocategorie](file-separati/tabelle_supabase/menu_subcategory_translations.csv)
- [Introduzioni](file-separati/tabelle_supabase/menu_intro_translations.csv)
- [Note e impostazioni](file-separati/tabelle_supabase/menu_setting_translations.csv)
- [Prodotti](file-separati/tabelle_supabase/menu_item_translations.csv)
- [SQL per tutte le cinque tabelle](file-separati/Marechiaro_importazione_19_lingue.sql)
- [CSV unico del menù nelle 19 lingue](file-separati/Marechiaro_menu_19_lingue.csv)
- [Istruzioni](file-separati/LEGGIMI.txt)

Sono presenti anche glossario, registro di revisione, rapporti dei controlli, anomalie della fonte italiana, script di rigenerazione e fonti originali. Per scaricare un singolo file, aprirlo e premere l’icona **Download raw file**.
