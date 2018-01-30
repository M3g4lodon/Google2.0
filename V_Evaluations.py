import timeit
import sys
import os
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

if __name__ == "__main__":
    print(temps_calcul_boolean_query())
    occupation_espace_disque()
