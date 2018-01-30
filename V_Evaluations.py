import timeit
import sys
import os
import matplotlib.pyplot as plt
import numpy as np

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
def precision_rappel(search_function):
    queries = [qr for qr in extract_queries_CACM() if len(qr.linked_docs) > 0]
    doc_coll = extract_documents_CACM()
    n_doc = len(doc_coll)
    rev_ind, dic_doc = read_CACM_index()
    recalls = []
    precisions = []
    for query in queries:
        results = search_function(rev_ind, dic_doc, query, doc_coll)
        qr_recall = []
        qr_precision = []
        nb_relevant_doc = len(query.linked_docs)
        for k in range(1, n_doc + 1):
            TP = len(set(results[:k]) & set(query.linked_docs))
            qr_recall.append(TP / k)
            qr_precision.append(TP / nb_relevant_doc)
        i = n_doc - 2
        while i >= 0:
            if qr_precision[i + 1] > qr_precision[i]:
                qr_precision[i] = qr_precision[i + 1]
            i -= 1
        recalls.append(qr_recall)
        precisions.append(qr_precision)

    # Moyenne recalls et précision
    moy_recalls, moy_precisions = average_curve_Precision_Recall(recalls, precisions)

    # Plot
    for i in range(n_doc - 1):
        plt.plot((moy_recalls[i], moy_recalls[i]), (moy_precisions[i], moy_precisions[i + 1]), 'k-', label='',
                 color='red')  # vertical
        plt.plot((moy_recalls[i], moy_recalls[i + 1]), (moy_precisions[i + 1], moy_precisions[i + 1]), 'k-', label='',
                 color='red')  # horizontal
    plt.xlabel("Précision")
    plt.ylabel("Rappel")
    plt.show()


def average_curve_Precision_Recall(recalls, precisions):
    recall_points = sorted(set(recall_point for recall_query in recalls for recall_point in recall_query) | {0})
    precisions_points = [1]
    n_queries = len(recalls)
    current_indices = [0 for _ in range(n_queries)]
    for recall_point in recall_points:
        sum = 0
        # Mise à jour des indices de lecture
        for i in range(n_queries):
            while recalls[i][current_indices[i] + 1] < recall_point and current_indices[i] < n_queries - 1:
                current_indices[i] += 1
            sum += precisions[i][current_indices[i]]

        # Calcul de la moyenne
        sum /= n_queries
        precisions_points.append(sum)
    return recall_points, precisions_points


# F-measure, E-measure, R-measure


# Mean-Average Precision


if __name__ == "__main__":
    precision_rappel()
