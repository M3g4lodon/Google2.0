import os
import re
import math
from functools import reduce

from nltk.stem.snowball import SnowballStemmer
import matplotlib.pyplot as plt

script_dir = os.getcwd()
# donne la localisation actuelle de ton dossier projet
cacm_relative_location = "/Data/CACM/cacm.all"
common_words_relative_location = "/Data/CACM/common_words"
stemmer = SnowballStemmer("english")


class Document:
    def __init__(self, id):
        self.id = id  # .I
        self.title = None  # .T
        self.summary = None  # .W
        self.keywords = []  # .K


def read_to_list(file_location):
    """
    Open, read a file in file_location and return the list of lines of the document
    :return: list
    """
    file = open(file_location, "r")
    res = file.read().split("\n")  # on crée une liste des lignes du document, split découpe une chaine de caractère
    file.close()
    return res


def extract_documents(input_data):
    """
    Read inputs and create documents
    :param input_data: list of lines of input
    :return: list of documents
    """
    collections = []
    # Transforme une liste en itérable,
    # next passe à l'élément suivant de la liste,
    # si c'est la fin ca raise l'exception StopIteration
    iter_lines = iter(input_data)
    line = next(iter_lines)
    try:

        while True:
            # Cas ligne identifiant
            if line[:2] == ".I":
                # Cas particulier de la première itération
                if 'doc' in dir():
                    collections.append(doc)
                # Nouveau document à rajouter
                doc_id = int(line[2:])
                doc = Document(doc_id)
                line = next(iter_lines)

            # Cas ligne titre
            elif line == ".T":
                doc.title = ""
                line = next(iter_lines)
                while "." != line[0]:
                    if doc.title == "":
                        doc.title += line.lstrip()  # lstrip supprime des espaces en début de ligne
                    else:
                        doc.title += " " + line.lstrip()  # ajoute un espace si ce n'est pas la première ligne
                    line = next(iter_lines)


            # Cas ligne résumé
            elif line == ".W":
                doc.summary = ""
                line = next(iter_lines)
                while "." != line[0]:
                    if doc.summary == "":
                        doc.summary += line.lstrip()  # lstrip supprime des espaces en début de ligne
                    else:
                        doc.summary += " " + line.lstrip()  # ajoute un espace si ce n'est pas la première ligne
                    line = next(iter_lines)

            # Cas ligne mots clés
            elif line == ".K":
                doc.keywords = []
                line = next(iter_lines)
                while "." != line[0]:
                    doc.keywords += map(lambda x: x.replace(', ', ''), line.split(', '))
                    line = next(iter_lines)

            # Cas ligne quelconque
            else:
                line = next(iter_lines)
    except StopIteration:
        # On rajoute dernier document à la 'main'
        collections.append(doc)

    return collections


###############################################################################
# ================================  PARTIE 1  =============================== #
###############################################################################

def question_1(collection):
    COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)
    nb_token = 0
    for doc in collection:
        for word in re.split("\W+|\d+", doc.title):
            if word.lower() not in COMMON_WORDS:
                nb_token += 1
        for keywords in doc.keywords:
            for word in re.split("\W+|\d+", keywords):
                if word.lower() not in COMMON_WORDS:
                    nb_token += 1

        if doc.summary is not None:
            for word in re.split("\W+|\d+", doc.summary):
                if word.lower() not in COMMON_WORDS:
                    nb_token += 1
    return nb_token


def question_2(collection):
    COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)
    nb_token = 0
    words = []
    for doc in collection:
        for word in re.split("\W+|\d+", doc.title):
            if word.lower() not in COMMON_WORDS:
                nb_token += 1
                if word.lower() not in words:
                    words = words + [word.lower()]
        for keywords in doc.keywords:
            for word in re.split("\W+|\d+", keywords):
                if word.lower() not in COMMON_WORDS:
                    nb_token += 1
                    if word.lower() not in words:
                        words = words + [word.lower()]
        if doc.summary is not None:
            for word in re.split("\W+|\d+", doc.summary):
                if word.lower() not in COMMON_WORDS:
                    nb_token += 1
                    if word.lower() not in words:
                        words = words + [word.lower()]

    return len(words), nb_token


# Answer CACM --> (8741, 107508)

# Pour l'autre bibliothèque : stemmed_word = stemmer.stem(word)

def question_2_half(collection):
    COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)
    nb_token = 0
    words = []
    for doc in collection:
        if doc.id < 1602:
            for word in re.split("\W+|\d+", doc.title):
                if word.lower() not in COMMON_WORDS:
                    nb_token += 1
                    if word.lower() not in words:
                        words = words + [word.lower()]
            for keywords in doc.keywords:
                for word in re.split("\W+|\d+", keywords):
                    if word.lower() not in COMMON_WORDS:
                        nb_token += 1
                        if word.lower() not in words:
                            words = words + [word.lower()]
            if doc.summary is not None:
                for word in re.split("\W+|\d+", doc.summary):
                    if word.lower() not in COMMON_WORDS:
                        nb_token += 1
                        if word.lower() not in words:
                            words = words + [word.lower()]

    return len(words), nb_token


def question_3(collection):
    M_full, T_full = question_2(collection)
    M_half, T_half = question_2_half(collection)
    k = math.log(M_full) / math.log(T_full)
    k -= math.log(M_half) / math.log(T_half)
    k = k / ((1.0 / math.log(T_full)) - (1.0 / math.log(T_half)))
    k = math.exp(k)
    b = (math.log(M_full) - math.log(k)) / math.log(T_full)

    # Vérification
    eps = math.pow(10, -10)
    if abs(M_full - k * math.pow(T_full, b)) > eps or abs(M_half - k * math.pow(T_half, b)) > eps:
        print("Error")
    else:
        return k, b


# Question 3 : on obtient pour CACM(103151, 16925) et (30107, 5395),
# on a donc k=47.9277363421892 et b =0.44936913708084

def question_4(collection):
    k, b = question_3(collection)
    print(k, b)
    t = 1000000.0
    return int(k * math.pow(t, b))


# Question 4 : [CACM] Pour 1 000 000 de tokens, on a une taille de vocabulaire de 23812

def question_5(collection):
    COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)
    word_list = []
    for doc in collection:
        word_list += re.split("\W+|\d+", doc.title)
        if doc.summary is not None:
            word_list += re.split("\W+|\d+", doc.summary)
        if doc.keywords:
            word_list += reduce((lambda x, y: x + y), list(map(lambda x: re.split("\W+|\d+", x), doc.keywords)))
    words_frequence = dict()
    for word in word_list:
        if word.lower() not in COMMON_WORDS:
            if word.lower() not in words_frequence:
                words_frequence[word.lower()] = 1
            else:
                words_frequence[word.lower()] = words_frequence[word.lower()] + 1

    ranks = sorted(words_frequence, key=words_frequence.get, reverse=True)
    frequences = [words_frequence[word] for word in ranks]

    # Plot : Rang vs Frequence
    plt.plot(range(len(words_frequence)), frequences)
    plt.xlabel("Rang(f)")
    plt.ylabel("Frequence(f)")
    plt.show()

    # Plot : LogRang vs LogFrequence
    log_frequences = list(map(lambda x: math.log(x), frequences))
    log_ranks = list(map(lambda x: math.log(x + 1), range(len(words_frequence))))
    plt.plot(log_ranks, log_frequences)
    plt.xlabel("LogRang(f)")
    plt.ylabel("LogFrequence(f)")
    plt.show()


###############################################################################
# ================================  PARTIE 2  =============================== #
###############################################################################

def construction_index(collection):
    COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)
    dic_terms = {}
    dic_documents = {}
    posting_list = []
    j = 1  # identifiant de terme
    for doc in collection:
        dic_documents[doc.id] = doc  # on remplit le dictionnaire de documents
        word_list = re.split("\W+|\d+", doc.title)
        if doc.summary is not None:
            word_list += re.split("\W+|\d+", doc.summary)
        if doc.keywords:
            word_list += reduce((lambda x, y: x + y), list(map(lambda x: re.split("\W+|\d+", x), doc.keywords)))
        for word in word_list:
            stemmed_word = word.lower()
            if stemmed_word not in COMMON_WORDS:
                if stemmed_word not in dic_terms:
                    dic_terms[stemmed_word] = j
                    posting_list += [(j, doc.id)]
                    j += 1
                else:  # on prend en compte les différentes occurrences
                    posting_list += [(dic_terms[stemmed_word], doc.id)]

    return len(posting_list)


def tri_termID(liste):
    L = [liste[0]]
    for k in range(1, len(liste)):
        if liste[k][0] > L[k - 1][0]:
            L = L + [liste[k]]
        else:
            j = 1
            while j < k and liste[k][0] > L[j - 1][0]:
                j += 1
            L = L[:j - 1] + [liste[k]] + L[j - 1:]
    return L


def tri_docID(list):
    L = [list[1]]
    for k in range(1, len(list)):
        if list[k][1] > L[k - 1][1]:
            L = L + [list[k]]
        else:
            j = 1
            while j < k and list[k][1] > L[j - 1][1]:
                j += 1
            L = L[:j - 1] + [list[k]] + L[j - 1:]
    return (L)


if __name__ == "__main__":
    documents = extract_documents(read_to_list(script_dir + cacm_relative_location))
    question_5(documents)
    # print(documents[1664].__dict__)
    # print(construction_index(documents))
    # print(tri_termID(construction_index(documents)))
    # print(tri_docID(construction_index(documents)))
