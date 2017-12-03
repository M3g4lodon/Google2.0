import os
import re
from nltk.stem.snowball import SnowballStemmer

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
    iter_lines = iter(
        input_data)  # ca transforme une liste en itérable, next passe à, l'élément suivant de la liste, si c'est la fin ca raise l'exception stopiteration
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
                    # Suppression des espaces en début de ligne
                    doc.summary += line.lstrip()
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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def question_1(collection):
    COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)
    nb_token = 0
    for doc in collection:
        doc2 = doc.title.replace("-",' ').replace('(',' ').replace(')',' ').replace(',',' ').replace('[',' ').replace(']',' ')
        for word in doc2.split(' '):
            if word.lower() not in COMMON_WORDS:
                nb_token += 1
        for word in doc.keywords:
            if word.lower() not in COMMON_WORDS:
                nb_token += 1
        if doc.summary is not None:
            sanitized_summary = doc.summary.replace("-",' ').replace('(',' ').replace(')',' ').replace(',',' ').replace('[',' ').replace(']',' ')
            for word in sanitized_summary.split(' '):
                if word.lower() not in COMMON_WORDS:
                    nb_token += 1


    return(nb_token)

def question_2(collection):
    COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)
    nb_token = 0
    words = []
    for doc in collection:
        doc2 = doc.title.replace("-",' ').replace('(',' ').replace(')',' ').replace(',',' ').replace('[',' ').replace(']',' ')
        for word in doc2.split(' '):
            if word.lower() not in COMMON_WORDS:
                nb_token += 1
                if word.lower() not in words:
                    words = words +[word.lower()]
        for word in doc.keywords:
            if word.lower() not in COMMON_WORDS:
                nb_token += 1
                if word.lower() not in words:
                    words = words +[word.lower()]
        if doc.summary is not None:
            sanitized_summary = doc.summary.replace("-",' ').replace('(',' ').replace(')',' ').replace(',',' ').replace('[',' ').replace(']',' ')
            for word in sanitized_summary.split(' '):
                if word.lower() not in COMMON_WORDS:
                    nb_token += 1
                    if word.lower() not in words:
                        words = words + [word.lower()]


    return(nb_token,words)


def question_2_bis(collection):
    COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)
    nb_token = 0
    words = []
    for doc in collection:
        doc2 = doc.title.replace("-",' ').replace('(',' ').replace(')',' ').replace(',',' ').replace('[',' ').replace(']',' ').replace('.',' ')
        for word in doc2.split(' '):
            stemmed_word = stemmer.stem(word)
            if stemmed_word not in COMMON_WORDS and not is_number(stemmed_word):
                nb_token += 1
                if stemmed_word not in words:
                    words = words +[stemmed_word]
        for word in doc.keywords:
            stemmed_word = stemmer.stem(word)
            if stemmed_word not in COMMON_WORDS and not is_number(stemmed_word):
                nb_token += 1
                if stemmed_word not in words:
                    words = words +[stemmed_word]
        if doc.summary is not None:
            sanitized_summary = doc.summary.replace("-",' ').replace('(',' ').replace(')',' ').replace(',',' ').replace('[',' ').replace(']',' ').replace('.',' ')
            for word in sanitized_summary.split(' '):
                stemmed_word = stemmer.stem(word)
                if stemmed_word not in COMMON_WORDS and not is_number(stemmed_word):
                    nb_token += 1
                    if stemmed_word not in words:
                        words = words + [stemmed_word]


    return(nb_token,len(words))

def question_3(collection):
    COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)
    nb_token = 0
    words = []
    for doc in collection:
        if doc.id < 1602:
            doc2 = doc.title.replace("-",' ').replace('(',' ').replace(')',' ').replace(',',' ').replace('[',' ').replace(']',' ').replace('.',' ')
            for word in doc2.split(' '):
                stemmed_word = stemmer.stem(word)
                if stemmed_word not in COMMON_WORDS and not is_number(stemmed_word):
                    nb_token += 1
                    if stemmed_word not in words:
                        words = words +[stemmed_word]
            for word in doc.keywords:
                stemmed_word = stemmer.stem(word)
                if stemmed_word not in COMMON_WORDS and not is_number(stemmed_word):
                    nb_token += 1
                    if stemmed_word not in words:
                        words = words +[stemmed_word]
            if doc.summary is not None:
                sanitized_summary = doc.summary.replace("-",' ').replace('(',' ').replace(')',' ').replace(',',' ').replace('[',' ').replace(']',' ').replace('.',' ')
                for word in sanitized_summary.split(' '):
                    stemmed_word = stemmer.stem(word)
                    if stemmed_word not in COMMON_WORDS and not is_number(stemmed_word):
                        nb_token += 1
                        if stemmed_word not in words:
                            words = words + [stemmed_word]


    return(nb_token,len(words))

# Question 3: on obtient (103151, 16925) et (30107, 5395), on a donc
if __name__ == "__main__":
    documents = extract_documents(read_to_list(script_dir + cacm_relative_location))
    print(documents[1664].__dict__)
    print(question_3(documents))
