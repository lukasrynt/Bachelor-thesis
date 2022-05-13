# Prototyp webového vyhledávače
Tato aplikace funguje jako prototyp dvojjazyčného webového vyhledávače, který je postavený nad naučenými vektorovými reprezentace z kolekce EUR-Lex. Umožňuje vyhledávat v jednotlivých dokumentech v obou jazycích a řadí výsledky na základě definované relevance. 

## Prerekvizity

Pro spuštění aplikace je potřeba mít nainstalované následující (spouštění předpokládá systém Linux)

- Ruby 3.0.3
- Bundler
- Yarn
- PostgreSQL

## Inicializace aplikace

Pro spuštění a zprovoznění aplikace je potřeba mít nainstalovaný software zmíněný v prerekvizitách a následně v hlavní složce projektu spustit následující příkazy:

- `bundle install`
- `yarn install`
- `rails db:create db:migrate db:seed`
- `bin/dev`

Příkaz `rails db:seed` předpokládá adresářovou strukturu, která byla popsána v rámci bakalářské práce (obsah přiloženého média). Konkrétně jde o to, aby složka `../word2vec/corpus/eurlex/` obsahoval adresářovou strukturu vygenerovanou z jupyter notebooku `eurlex_corpus.ipynb` a pro ÚFAL kolekci aby byl přítomný soubor `../word2vec/corpus/ufal/ufal_with_tokens.csv`.  

Pro samotné vyhledávání je potřeba mít aktivované conda prostředí specifikované v ../word2vec/README.md, neboť aplikace využívá Python skript pro vyhledávání.

Navíc je nutné přidat natrénovaný Word2Vec model aby bylo možné hledat nejbližší překlady. Model je potřeba přidat do složky `python_search` a pojmenovat ho jako `model`. 

Webová aplikace po spuštění běží na adrese [localhost:3000](http://localhost:3000/).

Při spuštění aplikace je pod EUR-Lex corpem možnost vygenerovat invertovaný index. Tato akce je nutná pro potřeby vyhledávání. Samotné vyhledávání je pak možné provádět z detailu kolekce.
