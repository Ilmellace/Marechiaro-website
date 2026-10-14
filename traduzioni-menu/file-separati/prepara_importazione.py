#!/usr/bin/env python3
"""Validazione e generazione offline. Non apre connessioni al database."""
import argparse, csv, json
from collections import Counter, defaultdict
from pathlib import Path

MAPPING = {
 'CATEGORIA': ('menu_category_translations', 'category_id', ['nome']),
 'SOTTOCATEGORIA': ('menu_subcategory_translations', 'subcategory_id', ['nome']),
 'INTRODUZIONE': ('menu_intro_translations', 'intro_id', ['titolo', 'testo']),
 'IMPOSTAZIONE': ('menu_setting_translations', 'setting_id', ['valore']),
 'PRODOTTO': ('menu_item_translations', 'item_id', ['nome','descrizione','vitigni','produttore','origine','regione']),
}
LANGUAGES = set('en fr de es pt nl pl ro cs el hu sv da no fi uk ru tr ar'.split())
FINAL = {'APPROVATA', 'REVISIONATA', 'PRESERVATO_VERIFICATO'}

def read(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:
  r=csv.DictReader(f)
  data=list(r)
  if any(None in x or any(v is None for v in x.values()) for x in data):
   raise ValueError('Numero di colonne non valido nel CSV')
  return data

def key(r): return (r['tipologia'],r['id'],r['campo'])
def quote(value): return "'"+value.replace("'", "''")+"'"
def write_csv(path,headers,rows):
 with path.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=headers,quoting=csv.QUOTE_NOTNULL);w.writeheader();w.writerows(rows)

def generate(args):
 sources=read(args.fonte); rows=read(args.traduzioni)
 source={key(r):r['testo_italiano'] for r in sources}
 if len(source)!=len(sources): raise ValueError('Chiavi duplicate nella fonte italiana')
 if any(n>1 for n in Counter((*key(r),r['language_code']) for r in rows).values()):
  raise ValueError('Chiavi duplicate nelle traduzioni')
 if {r['language_code'] for r in rows}!=LANGUAGES: raise ValueError('Lingue diverse dalle 19 previste')
 for r in rows:
  k=key(r)
  if k not in source or r['testo_italiano']!=source[k]: raise ValueError(f'Fonte italiana discordante: {k}')
  typ,ident,field=k
  if typ not in MAPPING or field not in MAPPING[typ][2]: raise ValueError(f'Campo sconosciuto: {k}')
  if not ident.isdecimal(): raise ValueError(f'ID non numerico: {ident}')
 translatable={k for k,v in source.items() if v.strip() and v.strip().lower()!='null'}
 expected={(t,i,f,l) for t,i,f in translatable for l in LANGUAGES}
 actual={(*key(r),r['language_code']) for r in rows}
 if actual!=expected: raise ValueError(f'Copertura errata: mancanti {len(expected-actual)}, extra {len(actual-expected)}')
 selected=[]
 if args.solo_approvate:
  selected=[r for r in rows if r['tipologia'] in ('CATEGORIA','SOTTOCATEGORIA') and r['stato_qualita']=='APPROVATA']
 else:
  unresolved=[r for r in rows if r['stato_qualita'] not in FINAL or not r['traduzione'].strip()]
  if unresolved: raise ValueError(f'Importazione definitiva bloccata: {len(unresolved)} righe non revisionate o vuote')
  if not args.null_come_sql_null: raise ValueError('Confermare che il valore letterale null della fonte rappresenti SQL NULL con --null-come-sql-null')
  selected=rows
 for r in selected:
  if not r['traduzione'].strip(): raise ValueError('Traduzione finale vuota')
  if r['stato_qualita']=='PRESERVATO_VERIFICATO' and r['traduzione']!=r['testo_italiano']:
   raise ValueError('Nome preservato modificato')
 # Le categorie già approvate vanno confrontate con il file originale.
 if not args.solo_approvate:
  if not args.approvazioni_originali: raise ValueError('Serve --approvazioni-originali per proteggere le traduzioni approvate')
  originals=read(args.approvazioni_originali)
  lookup={(*key(r),r['language_code']):r for r in rows}
  for r in originals:
   if r['tipologia'] in ('CATEGORIA','SOTTOCATEGORIA') and r['stato_qualita']=='APPROVATA':
    new=lookup[(*key(r),r['language_code'])]
    if new['traduzione']!=r['traduzione']: raise ValueError('Traduzione approvata modificata')
 out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
 groups=defaultdict(dict)
 for r in selected:
  groups[(r['tipologia'],r['id'],r['language_code'])][r['campo']]=r['traduzione']
 sql=['-- Generato offline; nessuna connessione al database.',
      '-- SOLO CATEGORIE APPROVATE; NON è il menù definitivo.' if args.solo_approvate else '-- Importazione completa delle traduzioni revisionate.',
      '-- Eseguire soltanto dopo revisione e conferma. Transazione atomica.',
      'BEGIN;', "SET LOCAL client_encoding = 'UTF8';",
      'LOCK TABLE '+', '.join('public.'+MAPPING[t][0] for t in MAPPING)+' IN SHARE ROW EXCLUSIVE MODE;']
 counts={}
 for typ,(table,fk,fields) in MAPPING.items():
  grouped=[(ident,lang,values) for (t,ident,lang),values in groups.items() if t==typ]
  if not grouped: continue
  grouped.sort(key=lambda x:(x[1],int(x[0])))
  payload=[]
  for ident,lang,values in grouped:
   record={fk:ident,'language_code':lang}
   for field in fields:
    if field in values: record[field]=values[field]
    else:
     original=source.get((typ,ident,field))
     if original=='': record[field]=''
     elif original is not None and original.strip().lower()=='null': record[field]=None
     else: raise ValueError(f'Campo mancante: {typ}/{ident}/{field}')
   payload.append(record)
  write_csv(out/(table+'.csv'),[fk,'language_code']+fields,payload)
  # SQL incorpora i valori; non dipende dall'importazione CSV o dal filesystem Supabase.
  cols=[fk,'language_code']+fields
  temp='stage_'+table
  base_table={'CATEGORIA':'menu_categories','SOTTOCATEGORIA':'menu_subcategories','INTRODUZIONE':'menu_intro','IMPOSTAZIONE':'menu_settings','PRODOTTO':'menu_items'}[typ]
  snapshot='source_'+table
  sql.append(f'CREATE TEMP TABLE {snapshot} ON COMMIT DROP AS SELECT id, '+', '.join(fields)+f' FROM public.{base_table} WITH NO DATA;')
  snapshots=[]
  for ident in sorted({x[0] for x in grouped},key=int):
   vals=[ident]
   for field in fields:
    original=source[(typ,ident,field)]
    vals.append('NULL' if original.strip().lower()=='null' else quote(original))
   snapshots.append('('+', '.join(vals)+')')
  sql.append(f'INSERT INTO {snapshot} (id, '+', '.join(fields)+') VALUES\n'+',\n'.join(snapshots)+';')
  comparisons=' OR '.join(f'b.{f} IS DISTINCT FROM s.{f}' for f in fields)
  sql.append(f'''DO $source$
BEGIN
 IF EXISTS (SELECT 1 FROM {snapshot} s LEFT JOIN public.{base_table} b ON b.id=s.id WHERE b.id IS NULL OR {comparisons}) THEN
  RAISE EXCEPTION 'Fonte italiana non corrispondente per {base_table}: transazione annullata. Verificare ID, testi e NULL';
 END IF;
END $source$;''')
  sql.append(f'CREATE TEMP TABLE {temp} ON COMMIT DROP AS SELECT {", ".join(cols)} FROM public.{table} WITH NO DATA;')
  value_lines=[]
  for r in payload:
   value_lines.append('('+', '.join(str(r[c]) if c==fk else ('NULL' if r[c] is None else quote(r[c])) for c in cols)+')')
  sql.append(f'INSERT INTO {temp} ({", ".join(cols)}) VALUES\n'+',\n'.join(value_lines)+';')
  sql.append(f'''DO $check$
BEGIN
 IF EXISTS (SELECT 1 FROM {temp} s LEFT JOIN public.{table} t USING ({fk}, language_code) WHERE t.id IS NULL)
 AND NOT EXISTS (
  SELECT 1 FROM information_schema.columns
  WHERE table_schema='public' AND table_name={quote(table)} AND column_name='id'
    AND (is_identity='YES' OR column_default IS NOT NULL)
 ) THEN
  RAISE EXCEPTION 'La tabella {table} richiede nuovi ID ma non ha generazione automatica: nessun dato importato';
 END IF;
END $check$;''')
  update=', '.join(f'{f}=EXCLUDED.{f}' for f in fields)+', updated_at=now()'
  assignments=', '.join(f'{f}=s.{f}' for f in fields)+', updated_at=now()'
  sql.append(f'UPDATE public.{table} t SET {assignments} FROM {temp} s WHERE t.{fk}=s.{fk} AND t.language_code=s.language_code;')
  sql.append(f'INSERT INTO public.{table} ({", ".join(cols)}) SELECT '+', '.join('s.'+c for c in cols)+f' FROM {temp} s WHERE NOT EXISTS (SELECT 1 FROM public.{table} t WHERE t.{fk}=s.{fk} AND t.language_code=s.language_code)\nON CONFLICT ({fk}, language_code) DO UPDATE SET {update};')
  counts[table]=len(payload)
 sql.append('COMMIT;')
 (out/'importazione.sql').write_text('\n\n'.join(sql)+'\n',encoding='utf-8')
 (out/'riepilogo.json').write_text(json.dumps({'modalita':'solo_approvate' if args.solo_approvate else 'revisionate','righe_per_tabella':counts,'campi':len(selected),'database_modificato':False},indent=2)+'\n',encoding='utf-8')
 print(json.dumps(counts,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--fonte',required=True);p.add_argument('--traduzioni',required=True)
 p.add_argument('--output',required=True);p.add_argument('--solo-approvate',action='store_true')
 p.add_argument('--null-come-sql-null',action='store_true');p.add_argument('--approvazioni-originali')
 try: generate(p.parse_args())
 except (ValueError,KeyError) as e: p.exit(1,f'ERRORE: {e}\n')
