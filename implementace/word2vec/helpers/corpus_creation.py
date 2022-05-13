import pandas as pd
import json
from random import randint

# ----------------------------------------------------------------------------------------------------------------------
# Vocabulary creation
# ----------------------------------------------------------------------------------------------------------------------


def build_vocab(df: pd.DataFrame) -> dict:
    """
    Creates vocabulary of unique words from input dataframe of tokens
    :param df: Dataframe with tokenized english and czech sentences
    :return: Built vocabulary
    """
    return {'en': list(pd.unique(df.explode('EN_tokens')['EN_tokens'])),
            'cz': list(pd.unique(df.explode('CZ_tokens')['CZ_tokens']))}


def save_vocab(vocab: dict, corpus_path: str) -> None:
    """
    Saves vocabulary into json file
    :param vocab: Vocabulary to save
    :param corpus_path: Path to corpus root folder
    """
    with open(corpus_path + "vocab.json", "w") as file:
        file.write(json.dumps(vocab))


def print_corpus_stats(df: pd.DataFrame, vocab: dict) -> None:
    """
    Print statistics about the corpus including word counts, unique words and paragraphs counts
    :param df: DataFrame containing english and czech tokens
    :param vocab: Vocabulary of unique words
    """
    en_count = sum(map(len, df['EN_tokens']))
    cz_count = sum(map(len, df['CZ_tokens']))
    pars_count = len(df)
    print("Paragraphs counts:", pars_count)
    print("CZ tokens counts:", cz_count)
    print("EN tokens counts:", en_count)
    print("Unique CZ tokens counts:", len(vocab['cz']))
    print("Unique EN tokens counts:", len(vocab['en']))

# ----------------------------------------------------------------------------------------------------------------------
# Merging techniques
# ----------------------------------------------------------------------------------------------------------------------


def interleave_words(sent1: list[str], sent2: list[str]) -> list[list]:
    """
    Method for sequential interleaving of two sentences
    :param sent1: List of tokens in the first sentence
    :param sent2: List of tokens in the second sentence
    :return: List of interleaved sentences
    """
    if len(sent1) > len(sent2):
        long = sent1
        short = sent2
    else:
        long = sent2
        short = sent1

    res = []
    times = len(long) - len(short)
    if times == 0:
        times = 1
    for start_pos in range(times):
        sent = []
        for i, token in enumerate(long):
            sent.append(token)
            if (i < len(short) + start_pos) and i >= start_pos:
                sent.append(short[i - start_pos])
        res.append(sent)
    return res


def interleave_tokens(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes corpus dataframe and interleaves each pair of sentences using sequential interleaving algorithm
    :param df: Dataframe containing individual czech and english tokens
    :return: Dataframe with sequentially interleaved tokens
    """
    return df.apply(lambda x: interleave_words(x['EN_tokens'], x['CZ_tokens']), axis=1).explode('data')


def simple_join_tokens(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes corpus dataframe and joins pairs of czech and english sentences beside each other
    :param df: Dataframe containing individual czech and english tokens
    :return:Dataframe with simple joined tokens
    """
    return df.apply(lambda x: x['EN_tokens'] + x['CZ_tokens'], axis=1)
