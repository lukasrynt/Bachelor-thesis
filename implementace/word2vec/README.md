# Word2Vec model
Součástí této složky jsou jupyter notebook a pomocné modely sloužící k výstavbě EUR-Lex a ÚFAL corpu a k následnému trénování, měření úspěšnosti a vizualizaci dvojjazyčného Word2Vec modelu.

## Prerekvizity

Pro spuštění Python notebooků je potřeba mít nainstalované následující

- Python 3
- Pip

## Inicializace aplikace

Pro spuštění a zprovoznění Python prostředí je potřeba mít nainstalovaný software zmíněný v prerekvizitách a následně v hlavní složce projektu spustit následující příkazy:

- `pip install -r requirements.txt`
- `jupyter notebook`

## Notebooky

Hlavní jupyter notebooky obsahují skripty pro tvorbu kolekcí a dále pro trénování, vizualizace a hodnocení jednotlivých word2vec modelů.

Notebook eurlex_corpus.ipynb obsahuje buňky pro stažení kolekce ze stránek eurlex a následné vytvoření corpu. Tento corpus je v přiloženém médiu přítomné pod složkou corpus/eurlex. Struktura odpovídá té, kterou vygeneruje daný notebook. Dále jsou v této části přítomné možnosti, jak napojovat odstavce obou jazyků na sebe. Tyto jsou opět předvygenerované.

Druhý hlavní notebook eurlex_w2v.ipynb obsahuje možnosti jak dávkově trénovat modely a dále jak je vizualizovat pomocí t-SNE a PCA technik redukce dimenzionality. V poslední části je pak přítomné samotné ohodnocení modelů pomocí jednotlivých metrik P@k a `distance_sum`, které byly používány v rámci práce.

Obdobně je zpracován i UFAL corpus, kde ale nejsou řešeny metriky hodnocení, neboť nedávalo příliš smysl je řešit vzhledem k objemu kolekce.
