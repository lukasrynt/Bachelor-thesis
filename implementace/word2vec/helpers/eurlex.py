import json
import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

from helpers.text_preprocessing import cz_tokenize, en_tokenize

CORPUS_PATH = "corpus/eurlex/"

# ----------------------------------------------------------------------------------------------------------------------
# Source extraction
# ----------------------------------------------------------------------------------------------------------------------


def download_page(url: str):
    """
    Downloads page from the specified URL
    :param url: URL of the page
    :return: Page content if the download was successful
    """
    page = requests.get(url)
    if page.status_code == 200:
        print("Download successful: " + url)
        return page.content
    else:
        print("Download failed: " + url)


def get_main_content(content):
    """
    Retrieves the main content from HTML
    :param content: Downloaded page content
    :return: Main content
    """
    soup = BeautifulSoup(content, 'html.parser')
    return soup.html.body


# ----------------------------------------------------------------------------------------------------------------------
# Text preprocessing
# ----------------------------------------------------------------------------------------------------------------------


def clean_text(text: str) -> str:
    """
    Removes redundant symbols and sequences from text to make it clean, namely:
    - remove integer numbered lists
    - remove text numbered lists
    - remove roman number lists
    - remove some redundant contents
    - removes any additional whitespaces
    :param text: Text to be cleaned
    :return: Cleaned text
    """

    regex = "\d+\. |^\d+\.|^\d+\)| \d+\)|\(\d+\)|" \
            "^[A-Za-z]\)|\([A-Za-z]\)|" \
            "^[ivx]+\)|\([ivx]+\)|" \
            "—|^\d+$|" \
            "\d+/[A-Z]+|\d+/\d+|" \
            "\[…\]|\(…\)"

    result = re.sub(regex, ' ', text)
    return result.strip()


def get_unformatted_paragraphs(main) -> list[str]:
    """
    Retrieves paragraphs from the HTML main content
    :param main: Main content of the page
    :return: List of paragraphs
    """
    paragraphs = []
    for p in main.select("p"):
        classes = p.get("class")
        if classes and ('normal' in classes or 'sti-art' in classes):
            par = p.get_text()
            par.replace("\xa0", " ")
            cleaned = clean_text(par)
            if cleaned and len(cleaned) > 20:
                paragraphs.append(clean_text(par))
    return paragraphs


# ----------------------------------------------------------------------------------------------------------------------
# Corpus creation
# ----------------------------------------------------------------------------------------------------------------------


def process_pages(cz_url: str, en_url: str, name: str) -> [list[list[str]], list[list[str]]]:
    """
    Downloads and processes czech and english text from given page. Creates directory structure specified by it
    :param cz_url: URL of the english text
    :param en_url: URL of the czech text
    :param name: Name of the resulting directory
    :return: Czech and English tokens
    """
    cz_content = download_page(cz_url)
    en_content = download_page(en_url)
    if not cz_content or not en_content:
        return

    cz_main = get_main_content(cz_content)
    en_main = get_main_content(en_content)

    cz_pars = get_unformatted_paragraphs(cz_main)
    en_pars = get_unformatted_paragraphs(en_main)

    # don't work with articles that don't have the same length
    if len(cz_pars) != len(en_pars) or len(cz_pars) == 0:
        return

    # create directory
    if not os.path.exists(CORPUS_PATH + name):
        os.makedirs(CORPUS_PATH + name)

    # textual representation
    with open(CORPUS_PATH + name + '/en.txt', 'w') as f:
        f.write('\n'.join(en_pars))
    with open(CORPUS_PATH + name + '/cz.txt', 'w') as f:
        f.write('\n'.join(cz_pars))

    # parsing and saving tokens
    cz_tokens = [cz_tokenize(par) for par in cz_pars]
    en_tokens = [en_tokenize(par) for par in en_pars]

    with open(CORPUS_PATH + name + '/en_tokens.json', 'w') as f:
        f.write(json.dumps(en_tokens))
    with open(CORPUS_PATH + name + '/cz_tokens.json', 'w') as f:
        f.write(json.dumps(cz_tokens))

    # calculate lengths for stats
    cz_len = 0
    en_len = 0
    for tokens in cz_tokens:
        cz_len += len(tokens)
    for tokens in en_tokens:
        en_len += len(tokens)
    return cz_tokens, en_tokens


def load_tokens_from_processed_files() -> pd.DataFrame:
    """
    Loads the folders structure created using the `process_pages` method in order to prevent redundant downloads
    :return: Dataframe with individual tokens
    """
    all_tokens = {'EN_tokens': [], 'CZ_tokens': []}
    from pathlib import Path
    for path in Path('corpus/eurlex').glob('[0-9]*-C[0-9]*'):
        with open(os.path.join(path, 'en_tokens.json')) as f:
            all_tokens['EN_tokens'] += json.load(f)
        with open(os.path.join(path, 'cz_tokens.json')) as f:
            all_tokens['CZ_tokens'] += json.load(f)
    return pd.DataFrame(all_tokens)
