import timeit
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from functools import partial

from I_Importation_Donnees import *
from II_Traitement_Linguistique import *
from III_Index_Inverse import *
from IV_Recherches import *


###############################################################################
# ==========================  Mesure de Performance  ======================== #
###############################################################################

# temps de calcul pour l’indexation

def temps_calcul_indexation():
    return timeit.timeit("reversed_index, dic_document = construction_index_one_block(extract_documents_CACM())",
                         number=1,
                         setup="from III_Index_Inverse import construction_index_one_block;"
                               "from I_Importation_Donnees import extract_documents_CACM")


# temps de réponse à une requête

def temps_calcul_boolean_query():
    return timeit.timeit("give_title(boolean_search('computer not Stanford', reversed_index, dic_doc),dic_doc)",
                         number=1, setup="from III_Index_Inverse import read_CACM_index;"
                                         "from IV_Recherches import give_title, boolean_search;"
                                         "reversed_index, dic_doc = read_CACM_index()")


def temps_calcul_vector_query():
    pass


# occupation de l’espace disque par les différents index.

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def occupation_espace_disque():
    print('CACM')
    reversed_index, _ = read_CACM_index()
    size_memory_CACM = sys.getsizeof(reversed_index)
    print(convert_bytes(size_memory_CACM))
    reversed_index, _ = read_CACM_index()
    CACM_file = os.getcwd() + "/Buffer/" + "Reversed_Index_CACM.json"
    size_disk_CACM = os.stat(CACM_file).st_size
    print(convert_bytes(size_disk_CACM))

    print('CS276')
    reversed_index, _ = read_CS276_index()
    size_memory_CS276 = sys.getsizeof(reversed_index)
    print(convert_bytes(size_memory_CS276))
    reversed_index, _ = read_CACM_index()
    CS276_file = os.getcwd() + "/Buffer/" + "Reversed_Index_CS276.json"
    size_disk_CS276 = os.stat(CS276_file).st_size
    print(convert_bytes(size_disk_CS276))


###############################################################################
# ==========================  Mesure de Pertinence  ========================= #
###############################################################################

# Précision / Rappel

def precision_rappel(search_function, weight_tf_idf_query, weight_tf_idf_doc, print=False):
    """ Calcule la courbe rappel-précision pour une fonction de recherche donnée sur nos requêtes

    :param search_function: fonction de recherche à tester
    :param weight_tf_idf_query: fonction de pondération de la requête
    :param weight_tf_idf_doc: fonction de pondération de la collection de document
    :param print: booléen pour afficher ou non la courbe rappel-précision
    :return: les points de la courbe moyenne rappel-précision
    """
    # Toutes les requêtes avec au moins un document pertinent
    queries = [qr for qr in extract_queries_CACM() if len(qr.linked_docs) > 0]

    # Collection des documents CACM
    doc_coll = extract_documents_CACM()

    # Nombre de documents de la collection
    n_doc = len(doc_coll)

    # Index inversé et dictionnaire des documents
    rev_ind, dic_doc = read_CACM_index()

    # les couples de points rappel précision
    recall_precision_queries = []

    for query in queries:
        search_results = search_function(rev_ind, dic_doc, query.summary, weight_tf_idf_query, weight_tf_idf_doc)
        qr_points = []
        nb_relevant_doc = len(query.linked_docs)
        for k in range(1, n_doc + 1):
            n_true_positive = len(set(doc_id for doc_id, score in search_results[:k]) & set(query.linked_docs))
            qr_points.append([(n_true_positive / k), (n_true_positive / nb_relevant_doc)])
        qr_points.sort(key=lambda x: x[0])
        i = n_doc - 2
        while i >= 0:
            if qr_points[i][1] < qr_points[i + 1][1]:
                qr_points[i][1] = qr_points[i + 1][1]
            i -= 1

        recall_precision_queries.append(qr_points)

    # Moyenne recalls et précision
    recalls_precisions = average_curve_Precision_Recall(recall_precision_queries)

    # Plot
    if print:
        plt.plot(*recalls_precisions)
        plt.xlabel("Rappel")
        plt.ylabel("Précision")
        plt.show()

    return recalls_precisions


def average_curve_Precision_Recall(points):
    """ Calcule la moyenne des courbes rappel-précision de chaque requête

    :param points: liste, pour chaque requête, contient les coordonnées des points des courbes rappel-précision
    :return: liste des rappels et liste des précisions moyennes correspondantes
    """
    # Liste ordonnée des rappels (abcisses) possibles sur lesquelles on veut retrouver leur précision
    recall_points = sorted(set(recall_point for qr_point in points for recall_point, precision_point in qr_point))

    # Liste des précisions à calculer
    precisions_points = []

    # Nombre de requêtes
    n_queries = len(points)

    # Indice des lecture des précisions pour chaque requête
    precisions_current_indices = [0 for _ in range(n_queries)]

    for recall_point in recall_points:
        sum = 0

        # Mise à jour des indices de lecture
        for i in range(n_queries):
            while points[i][precisions_current_indices[i] + 1][0] <= recall_point \
                    and precisions_current_indices[i] < len(points[i]) - 2:
                precisions_current_indices[i] += 1

            # Somme la précision de chaque requête correspondante
            sum += points[i][precisions_current_indices[i]][1]

        # Calcul de la moyenne
        sum /= n_queries
        precisions_points.append(sum)

    return recall_points, precisions_points


# F-measure, E-measure, R-precision

# E-measure
ALPHA = 1
RANK = 100


def E_measure(search_function, weight_tf_idf_query, weight_tf_idf_doc, print_graph=False):
    """

    :param search_function:
    :param weight_tf_idf_query:
    :param weight_tf_idf_doc:
    :param print:
    :return:
    """

    e_measures = []

    # Toutes les requêtes avec au moins un document pertinent
    queries = [qr for qr in extract_queries_CACM() if len(qr.linked_docs) > 0]

    # Collection des documents CACM
    doc_coll = extract_documents_CACM()

    # Nombre de documents de la collection
    n_doc = len(doc_coll)

    # Index inversé et dictionnaire des documents
    rev_ind, dic_doc = read_CACM_index()

    # parcours des requêtes
    for query in queries:

        search_results = search_function(rev_ind, dic_doc, query.summary, weight_tf_idf_query, weight_tf_idf_doc)

        nb_relevant_doc = len(query.linked_docs)
        n_true_positive = len(set(doc_id for doc_id, score in search_results[:RANK]) & set(query.linked_docs))
        recall = n_true_positive / RANK
        precision = n_true_positive / nb_relevant_doc

        if precision != 0 and recall != 0:
            e_measure = 1 - 1 / ((ALPHA / precision) + (1 - ALPHA) * (1 / recall))
            e_measures.append(e_measure)

    if print_graph:
        plt.hist(e_measures, bins=20)
        plt.show()

    return sum(e_measures) / len(e_measures)


def F_measure(search_function, weight_tf_idf_query, weight_tf_idf_doc, print_graph):
    f_measures = []

    # Toutes les requêtes avec au moins un document pertinent
    queries = [qr for qr in extract_queries_CACM() if len(qr.linked_docs) > 0]

    # Collection des documents CACM
    doc_coll = extract_documents_CACM()

    # Nombre de documents de la collection
    n_doc = len(doc_coll)

    # Index inversé et dictionnaire des documents
    rev_ind, dic_doc = read_CACM_index()

    # parcours des requêtes
    for query in queries:

        search_results = search_function(rev_ind, dic_doc, query.summary, weight_tf_idf_query, weight_tf_idf_doc)

        nb_relevant_doc = len(query.linked_docs)
        n_true_positive = len(set(doc_id for doc_id, score in search_results[:RANK]) & set(query.linked_docs))
        recall = n_true_positive / RANK
        precision = n_true_positive / nb_relevant_doc

        if precision != 0 and recall != 0:
            f_measure = 1 / ((ALPHA / precision) + (1 - ALPHA) * (1 / recall))
            f_measures.append(f_measure)

    if print_graph:
        plt.hist(f_measures, bins=20)
        plt.show()

    return sum(f_measures) / len(f_measures)


def R_precision(search_function, weight_tf_idf_query, weight_tf_idf_doc, print_graph):
    r_precisions = []

    # Toutes les requêtes avec au moins un document pertinent
    queries = [qr for qr in extract_queries_CACM() if len(qr.linked_docs) > 0]

    # Collection des documents CACM
    doc_coll = extract_documents_CACM()

    # Nombre de documents de la collection
    n_doc = len(doc_coll)

    # Index inversé et dictionnaire des documents
    rev_ind, dic_doc = read_CACM_index()

    # parcours des requêtes
    for query in queries:
        search_results = search_function(rev_ind, dic_doc, query.summary, weight_tf_idf_query, weight_tf_idf_doc)

        nb_relevant_doc = len(query.linked_docs)
        n_true_positive = len(
            set(doc_id for doc_id, score in search_results[:nb_relevant_doc]) & set(query.linked_docs))
        r_precision = n_true_positive / nb_relevant_doc

        r_precisions.append(r_precision)
    if print_graph:
        plt.hist(r_precisions, bins=20)
        plt.show()

    return sum(r_precisions) / len(r_precisions)


# Mean-Average Precision

def precision_moyenne():
    pass # en cours

if __name__ == "__main__":
    # precision_rappel(vectorial_search, weight_tf_idf_query1, weight_tf_idf_doc1, print=True)
    print(E_measure(vectorial_search, weight_tf_idf_query1, weight_tf_idf_doc1, print_graph=True))
    print(F_measure(vectorial_search, weight_tf_idf_query1, weight_tf_idf_doc1, print_graph=True))
    print(R_precision(vectorial_search, weight_tf_idf_query1, weight_tf_idf_doc1, print_graph=True))
