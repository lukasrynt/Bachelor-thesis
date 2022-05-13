from gensim.models import Word2Vec

from helpers.word2vec import get_vector_representations, get_single_representation, cosine_distance
from helpers.text_preprocessing import cz_tokenize, en_tokenize
import pandas as pd
import sys


def search_nearest_translations(model, word: str, lang: str, en_freqs, cz_freqs):
    if lang == 'en':
        freqs = en_freqs
        token = en_tokenize(word)[0]
    else:
        freqs = cz_freqs
        token = cz_tokenize(word)[0]
    if token not in model.wv:
        return [token]
    df = get_vector_representations(model)
    all_for_lang = freqs['Unnamed: 0'].values.tolist()
    representations = df.loc[df['token'].isin(all_for_lang)]
    cz_repr = get_single_representation(model, token)
    distances = representations.apply(lambda x: cosine_distance(x[list(range(1, model.vector_size + 1))].tolist(), cz_repr), axis=1)
    distances.rename('distances', inplace=True)
    merged = pd.concat([distances, representations], axis=1)
    return [token] + merged.nsmallest(5, 'distances')['token'].tolist()


if len(sys.argv) < 3:
    sys.exit(1)

lang = sys.argv[1]
word = sys.argv[2]
model = Word2Vec.load('python_search/model')
cz_freqs = pd.read_csv('python_search/cz_freqs.csv')
en_freqs = pd.read_csv('python_search/en_freqs.csv')
print(search_nearest_translations(model, word, lang, en_freqs, cz_freqs))
