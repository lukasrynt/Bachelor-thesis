from gensim.models import Word2Vec
import pandas as pd
import numpy as np
import json
import re
import math
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from scipy.spatial import distance
import plotly.express as px


# ----------------------------------------------------------------------------------------------------------------------
# JSON processing and model training
# ----------------------------------------------------------------------------------------------------------------------
def series_to_arr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts given dataframe with json values to dataframe containing individual tokens
    :param df: Dataframe with json values
    :return: Converted dataframes where row contains list of tokens
    """
    return df.apply(lambda x: json.loads(re.sub("\'", "\"", x['0'])), axis=1)


def full_train_model(model: Word2Vec, df: pd.DataFrame) -> None:
    """
    Trains the model on the dataset through series of iterations
    :param model: W2V model
    :param df: Dataframe with training data - contains lists of tokens
    """
    split_by_iteration = 100000
    iterations = math.ceil(len(df) / split_by_iteration)
    for i in range(iterations):
        print("Iteration {:d}/{:d}".format(i, iterations))
        continual_train_model(model, df, i)


def continual_train_model(model: Word2Vec, df: pd.DataFrame,
                          iteration: int = 0, split_per_iteration: int = 100000) -> None:
    """
    Takes the whole dataframe and trains the model on multiple iterations. This can be repeated with different parts
    :param model: W2V model to be trained
    :param df: Dataframe with training data - contains lists of tokens
    :param iteration: Number of iterations to be performed on the training data
    :param split_per_iteration: Number of sentences taken in one iteration
    """
    if iteration == 0:
        update = False
    else:
        update = True
    reduced_df = df.iloc[iteration*split_per_iteration:(iteration + 1)*split_per_iteration]
    batch_train_model(model, reduced_df, update)


def batch_train_model(model: Word2Vec, df: pd.DataFrame, update: bool = False) -> None:
    """
    Trains W2V model in multiple batches
    :param model: W2V model to be trained
    :param df: Dataframe with training data - contains lists of tokens
    :param update: Set to False if this is the first iteration of training
    :return:
    """
    model.build_vocab(series_to_arr(df), update=update)
    batch_size = 1000
    for g, partial_df in df.groupby(np.arange(len(df)) // batch_size):
        model.train(series_to_arr(partial_df), total_examples=model.corpus_count, epochs=model.epochs)


# ----------------------------------------------------------------------------------------------------------------------
# Getting vector representation of tokens
# ----------------------------------------------------------------------------------------------------------------------
def get_vector_representations(model: Word2Vec) -> pd.DataFrame:
    """
    Takes W2V model learned representations and transforms them into dataset
    :param model: W2V model from which we want to extract the representations
    :return: Learned representations from the given model
    """
    tokens = pd.DataFrame({'token': model.wv.index_to_key})
    values = tokens.apply(lambda x: model.wv[x['token']], axis=1)
    values = pd.DataFrame(values.to_list(), columns=list(range(1, model.vector_size + 1)))
    return pd.concat([tokens, values], axis=1)


def reduce_words(df: pd.DataFrame, en_words: list, cz_words: list) -> pd.DataFrame:
    """
    Reduce tokens present in learned representations taken from W2V model by provided lists of tokens
    :param df: Learned representations of individual tokens taken from W2V model
    :param en_words: List of english words
    :param cz_words: List of czech words
    :return: Reduced dataset containing only the words in the provided lists
    """
    words_df = pd.DataFrame({'word': en_words + cz_words,
                             'language': ['en'] * len(en_words) + ['cz'] * len(cz_words)})
    words_repr = df.loc[df['token'].isin(words_df['word'])]
    reduced = words_repr.merge(words_df, left_on='token', right_on='word')
    reduced.drop(columns=['word'], inplace=True)
    return reduced


def reduced_representations(model: Word2Vec, en_words: list, cz_words: list) -> pd.DataFrame:
    """
    Creates representations from the given W2V model reduced by provided list of tokens
    :param model: W2V model
    :param en_words: List of english words
    :param cz_words: List of czech words
    :return: Reduced dataset containing only the words in the provided lists
    """
    df = get_vector_representations(model)
    return reduce_words(df, en_words, cz_words)


def most_frequent_representations(model: Word2Vec, en_freqs: pd.DataFrame, cz_freqs: pd.DataFrame, limit: int = 1000):
    """
    Creates representations from the given W2V model reduced by the most frequent tokens in the collection
    :param model: W2V model
    :param en_freqs: English tokens mapped to collection frequencies
    :param cz_freqs: Czech tokens mapped to collection frequencies
    :param limit: Number of tokens take from each language
    :return: Reduced learned representations by the most frequent tokens in the collection
    """
    df = get_vector_representations(model)
    cz_words = cz_freqs['Unnamed: 0'].head(limit).tolist()
    en_words = en_freqs['Unnamed: 0'].head(limit).tolist()
    return reduce_words(df, en_words, cz_words)


# ----------------------------------------------------------------------------------------------------------------------
# Visualization
# ----------------------------------------------------------------------------------------------------------------------
def pca_reduce(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reduces the dataset into 2 dimensions using PCA dimensionality reduction
    :param df: Dataset of learned representations
    :return: Learned representations reduced to 2 dimensions
    """
    feature_cols = [x for x in df.columns if isinstance(x, int)]
    x = df.loc[:, feature_cols]
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(x)
    cols = [f"PCA axe {col + 1}" for col in range(2)]
    principal_df = pd.DataFrame(data=principal_components, columns=cols)
    return pd.concat([principal_df, df[['token', 'language']]], axis=1)


def tsne_reduce(df: pd.DataFrame, perplexity: int = 30) -> pd.DataFrame:
    """
    Reduces the dataset into 2 dimensions using t-SNE dimensionality reduction
    :param perplexity: Perplexity of t-SNE dimensionality reduction
    :param df: Dataset of learned representations
    :return: Learned representations reduced to 2 dimensions
    """
    feature_cols = [x for x in df.columns if isinstance(x, int)]
    x = df.loc[:, feature_cols]
    tsne = TSNE(n_components=2, perplexity=perplexity, learning_rate=200, square_distances=True,
                init='random', metric=lambda x, y: cosine_distance(x, y))
    tsne_results = tsne.fit_transform(x)
    cols = [f"t-SNE axe {col + 1}" for col in range(2)]
    tsne_df = pd.DataFrame(data=tsne_results, columns=cols)
    return pd.concat([tsne_df, df[['token', 'language']]], axis=1)


def visualize_most_frequent(model: Word2Vec, en_freqs: pd.DataFrame, cz_freqs: pd.DataFrame,
                            technique: str = "t-SNE", limit: int = 1000, perplexity: int = 30):
    """
    Visualize the model representation reduced by the most frequent words in the corpus
    :param perplexity: Perplexity of t-SNE dimensionality reduction
    :param model: W2V model
    :param en_freqs: English tokens mapped to collection frequencies
    :param cz_freqs: Czech tokens mapped to collection frequencies
    :param technique: Dimensionality reduction technique used - can be either 'PCA' or 't-SNE'
    :param limit: Number of tokens take from each language
    """
    reduced_df = most_frequent_representations(model, en_freqs, cz_freqs, limit)
    if technique == 'PCA':
        representations = pca_reduce(reduced_df)
    elif technique == 't-SNE':
        representations = tsne_reduce(reduced_df, perplexity)
    else:
        raise ValueError("Dimensionality reduction technique not supported")
    visualize(representations, "{:s} axe 1".format(technique), "{:s} axe 2".format(technique))


def visualize_words(model: Word2Vec, en_words: list, cz_words: list, technique: str = "t-SNE", perplexity: int = 30):
    """
    Visualize the model representation reduced by the given list of tokens
    :param perplexity: Perplexity of t-SNE dimensionality reduction
    :param model: W2V model
    :param en_words: List of english tokens
    :param cz_words: List of czech tokens
    :param technique: Dimensionality reduction technique used - can be either 'PCA' or 't-SNE'
    """
    reduced_df = reduced_representations(model, en_words, cz_words)
    if technique == 'PCA':
        representations = pca_reduce(reduced_df)
    elif technique == 't-SNE':
        representations = tsne_reduce(reduced_df, perplexity)
    else:
        raise ValueError("Dimensionality reduction technique not supported")
    visualize(representations, "{:s} axe 1".format(technique), "{:s} axe 2".format(technique))


def visualize(representations: pd.DataFrame, x_col: str, y_col: str):
    """
    Creates a visual representation of the given dataset
    :param representations: Representation to be visualized
    :param x_col: name of the column that should be represented by the x-axis
    :param y_col: name of the column that should be represented by the y-axis
    """
    fig = px.scatter(representations, x=x_col, y=y_col, text="token", color="language")
    fig.update_traces(textposition='top center')
    fig.update_layout(
        height=800,
        title_text='Tokens in dataset'
    )
    fig.show()


# ----------------------------------------------------------------------------------------------------------------------
# Model evaluation
# ----------------------------------------------------------------------------------------------------------------------
def get_single_representation(model: Word2Vec, token: str) -> list[float]:
    """
    Get vector representation for single token
    :param model: W2V model
    :param token: Word for which we want the representation
    :return: List of features describing the token
    """
    return model.wv[token].tolist()


def cosine_distance(vector1: list[float], vector2: list[float]) -> float:
    """
    Calculates cosine distance between two vectors
    :param vector1: First vector representation
    :param vector2: Second vector representation
    :return: Calculated distance
    """
    return distance.cosine(vector1, vector2)


def k_nearest_words(df: pd.DataFrame, word_repr: list[float], freqs: pd.DataFrame, k: int = 5) -> list:
    """
    Gets k nearest words for the given word repr in the opposite language
    :param df: Dataframe with learned vector representations of individual tokens
    :param word_repr: Word representation of the word for which we seek the nearest neighbors
    :param freqs: Words in the opposite language mapped to their frequencies
    :param k: Number of the nearest neighbors to be returned
    :return: k nearest words to given word in the opposite language
    """
    all_for_lang = freqs['Unnamed: 0'].values.tolist()
    lang_representations = df.loc[df['token'].isin(all_for_lang)]
    distances = lang_representations.apply(lambda x: cosine_distance(x[list(range(1, 101))].tolist(), word_repr),
                                           axis=1)
    distances.rename('distances', inplace=True)
    merged = pd.concat([distances, lang_representations], axis=1)
    return merged.nsmallest(k, 'distances')['token'].tolist()


def distance_sum_metric(model: Word2Vec, en_words: list[str], cz_words: list[str], en_freqs: pd.DataFrame) -> float:
    """
    Calculates sum of cosine distances normed by max distances over the words provided in lists,
    assumes that both lists have the same length
    :param model: W2V model
    :param en_words: List of english tokens
    :param cz_words: List of czech tokens
    :return: Measured sum of distances over all words
    """
    distance_sum = 0
    df = get_vector_representations(model)
    all_en_words = en_freqs['Unnamed: 0'].values.tolist()
    en_representations = df.loc[df['token'].isin(all_en_words)]
    for i in range(len(en_words)):
        cz_repr = get_single_representation(model, cz_words[i])
        en_repr = get_single_representation(model, en_words[i])
        distances = en_representations\
            .apply(lambda x: cosine_distance(x[list(range(1, model.vector_size + 1))].tolist(), cz_repr), axis=1)
        largest_dist = distances.max()
        distance_sum += cosine_distance(en_repr, cz_repr) / largest_dist
    return distance_sum


def p_at_k_metric(model: Word2Vec, en_words: list[str], cz_words: list[str],
                  en_freqs: pd.DataFrame, k: int = 5) -> float:
    """
    Simplified P@k metric for measuring success of the model. For each word pair checks if the translation is within the
    top k neighbours. If it is - adds this to success counter. The resulting score is then calculated by dividing this
    success counter by the number of word pairs. In contrast to the classical definition, this score is binary for each
    word pair
    :param model:
    :param en_words:
    :param cz_words:o
    :param en_freqs:
    :param k:
    :return:
    """
    success_count = 0
    df = get_vector_representations(model)
    all_en_words = en_freqs['Unnamed: 0'].values.tolist()
    en_representations = df.loc[df['token'].isin(all_en_words)]
    for i in range(len(en_words)):
        cz_repr = get_single_representation(model, cz_words[i])
        distances = en_representations\
            .apply(lambda x: cosine_distance(x[list(range(1, model.vector_size + 1))].tolist(), cz_repr), axis=1)
        distances.rename('distances', inplace=True)
        merged = pd.concat([distances, en_representations], axis=1)
        n_neighbors = merged.nsmallest(k, 'distances')['token'].tolist()
        if en_words[i] in n_neighbors:
            success_count += 1
    return success_count / len(en_words)
