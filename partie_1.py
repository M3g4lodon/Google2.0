import os
import re
import math
from functools import reduce


import matplotlib.pyplot as plt
from import_data import *



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

    sorted_words = sorted(words_frequence, key=words_frequence.get, reverse=True)
    frequences = [words_frequence[word] for word in sorted_words]
    ranks=[1]
    for rank in range(1,len(frequences)):
        if frequences[rank-1]==frequences[rank]:
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
    documents = extract_documents(read_to_list(script_dir + cacm_relative_location))
    question_5(documents)