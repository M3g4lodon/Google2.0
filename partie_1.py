import math
from nltk.stem.snowball import SnowballStemmer
import matplotlib.pyplot as plt

from import_data import *

stemmer = SnowballStemmer("english")
COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)


###############################################################################
# ================================  PARTIE 1  =============================== #
###############################################################################


def question_1(collection):
    nb_token = 0
    for doc in collection:
        for word in doc.word_lists:
            if word.lower() not in COMMON_WORDS:
                nb_token += 1
    return nb_token


# Answer [CACM] 107508 tokens (sans stemmer)
# Answer [CS276] 17,803,941 tokens

def question_2(collection):
    nb_token = 0
    words = set()
    for doc in collection:
        for word in doc.word_lists:
            if word.lower() not in COMMON_WORDS:
                nb_token += 1
                words.add(stemmer.stem(word))
    return len(words), nb_token


# Answer [CACM]     8741 mots (taille de vocabulaire) (sans stemmer)
# Answer [CS276]    297746 mots (taille du vocabulaire)

def question_2_half(collection):
    nb_token = 0
    words = set()
    n = len(collection)
    i = 0
    while i < n / 2:
        doc = collection.pop()
        for word in doc.word_lists:
            if word.lower() not in COMMON_WORDS:
                nb_token += 1
                words.add(words.add(stemmer.stem(word)))
        i += 1

    return len(words), nb_token


# [CS276] result (184722, 8729267)

def question_3(collection):
    M_full, T_full = question_2(collection)
    M_half, T_half = question_2_half(collection)
    k = math.log(M_full) / math.log(T_full)
    k -= math.log(M_half) / math.log(T_half)
    k = k / ((1.0 / math.log(T_full)) - (1.0 / math.log(T_half)))
    k = math.exp(k)
    b = (math.log(M_full) - math.log(k)) / math.log(T_full)

    # Vérification
    eps = math.pow(10, -9)
    if abs(M_full - k * math.pow(T_full, b)) > eps or abs(M_half - k * math.pow(T_half, b)) > eps:
        print("Question 3 : Error on k and b")
    return k, b


# Answer [CACM]  k=47.9277363421892  b = 0.44936913708084 (sans stemmer)
# Answer [CS276] k=4.713488927858546 b = 0.6620912701354705)

def question_4(collection):
    k, b = question_3(collection)
    t = 1000000.0
    return int(k * math.pow(t, b))


# Question 4 : [CACM]  Pour 1 000 000 de tokens, on a une taille de vocabulaire de 23812
# Question 4 : [CS276] Pour 1 000 000 de tokens, on a une taille de vocabulaire de 44430

def question_5(collection):
    word_list = []
    for doc in collection:
        word_list += doc.word_lists
    words_frequence = dict()
    for word in word_list:
        if word.lower() not in COMMON_WORDS:
            if word.lower() not in words_frequence:
                words_frequence[word.lower()] = 1
            else:
                words_frequence[word.lower()] = words_frequence[word.lower()] + 1

    sorted_words = sorted(words_frequence, key=words_frequence.get, reverse=True)
    frequences = [words_frequence[word] for word in sorted_words]
    ranks = [1]
    for rank in range(1, len(frequences)):
        if frequences[rank - 1] == frequences[rank]:
            ranks.append(ranks[-1])
        else:
            ranks.append(rank)

    # Plot : Rang vs Frequence
    plt.plot(ranks, frequences)
    plt.xlabel("Rang(f)")
    plt.ylabel("Frequence(f)")
    plt.show()

    # Plot : LogRang vs LogFrequence
    log_frequences = list(map(lambda x: math.log(x), frequences))
    log_ranks = list(map(lambda x: math.log(x), ranks))
    plt.plot(log_ranks, log_frequences)
    plt.xlabel("LogRang(f)")
    plt.ylabel("LogFrequence(f)")
    plt.show()


if __name__ == "__main__":
    documents = extract_documents_CACM()
    # documents = extract_documents_CS276()
    # print(question_1(documents))
    # print(question_2(documents))
    # print(question_2_half(documents))
    # print(question_3(documents))
    # print(question_4(documents))
    question_5(documents)
