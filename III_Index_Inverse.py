from collections import OrderedDict
from functools import reduce, partial
import json
from concurrent.futures import ProcessPoolExecutor as c_pool
from nltk.stem.snowball import SnowballStemmer

from I_Importation_Donnees import *
from III_bis_Classes import InvertedIndex, DocumentDict

stemmer = SnowballStemmer("english")
COMMON_WORDS = set( stemmer.stem(word) for word in read_to_list(script_dir + common_words_relative_location))


###############################################################################
# ================================  PARTIE 2  =============================== #
###############################################################################


###############################################################################
#                           Block Sorted Based Index

def create_posting_list(collection):
    dic_documents = {}
    posting_list = []
    for doc in collection:
        dic_documents[doc.id] = doc.title  # on remplit le dictionnaire de documents
        for word in doc.word_lists:
            if word.lower() not in COMMON_WORDS:
                posting_list += [(stemmer.stem(word), doc.id)]

    return sorted(posting_list, key=lambda x: x[0]), dic_documents


def construction_index_one_block(collection):
    posting_list, dic_documents = create_posting_list(collection)
    reversed_index = OrderedDict()
    for term, doc_id in posting_list:
        if term in reversed_index:
            if doc_id in reversed_index[term]['tf']:
                reversed_index[term]['tf'][doc_id] += 1
            else:
                reversed_index[term]['tf'][doc_id] = 1
                reversed_index[term]['idf'] += 1
        else:
            reversed_index[term] = {'idf': 1, 'tf': {doc_id: 1}}
    return reversed_index, dic_documents


def write_in_buffer(block_index, reversed_index, dic_documents):
    # Write Reversed Index
    file = open(os.getcwd() + "/Buffer/Buffer/" + "ReversedIndex_" + str(block_index) + ".json", "w")
    json.dump(reversed_index, file)
    file.close()

    # Write Documents Dictionnary
    file = open(os.getcwd() + "/Buffer/Buffer/" + "Dict_Documents_" + str(block_index) + ".json", "w")
    json.dump(dic_documents, file)
    file.close()


def read_in_buffer(block_index):
    # Read Reversed Index
    file = open(os.getcwd() + "/Buffer/Buffer/" + "ReversedIndex_" + str(block_index) + ".json", "r")
    reversed_index = OrderedDict(json.load(file))
    file.close()

    # Read Dictionnary of documents
    file = open(os.getcwd() + "/Buffer/Buffer/" + "Dict_Documents_" + str(block_index) + ".json", "r")
    dic_documents = json.load(file)
    file.close()
    return reversed_index, dic_documents


def process_block(i, block_nb):
    # Read a block
    block_documents = extract_documents_CS276(files_part(i, block_nb))
    # Construct a block reversed index
    block_index, dic_doc_block = construction_index_one_block(block_documents)
    # Write the block reversed index on the disk
    write_in_buffer(i, block_index, dic_doc_block)


def BSBI_Index_construction_CS276():
    """CS276 only"""
    reversed_index = OrderedDict()
    dic_documents = {}
    block_nb = 100

    with c_pool() as p:
        p.map(partial(process_block, block_nb=block_nb), range(block_nb))

    # Merge the block inversed indexes
    block_doc_to_doc = {}  # table de correspondance entre les doc_id d'un bloc et le doc_id global
    for i in range(block_nb):
        reversed_index_block, dic_doc_block = read_in_buffer(i)
        block_doc_to_doc[i] = {}
        if not dic_documents:  # If it's empty
            dic_documents = dict(dic_doc_block)
        else:
            for doc_id_b in dic_doc_block:
                if doc_id_b in dic_documents:
                    new_id = str(len(dic_documents) + 1)
                    dic_documents[new_id] = dic_doc_block[doc_id_b]
                    block_doc_to_doc[i][doc_id_b] = new_id
                else:
                    dic_documents[doc_id_b] = dic_doc_block[doc_id_b]
        for term in reversed_index_block:
            if term in reversed_index:
                reversed_index[term]['idf'] += reversed_index_block[term]['idf']
                for doc_id_b in reversed_index_block[term]['tf']:
                    if doc_id_b in block_doc_to_doc[i]:
                        doc_id = block_doc_to_doc[i][doc_id_b]
                    else:
                        doc_id = doc_id_b
                    reversed_index[term]['tf'][doc_id] = reversed_index_block[term]['tf'][doc_id_b]
            else:
                reversed_index[term] = {}
                reversed_index[term]['idf'] = reversed_index_block[term]['idf']
                reversed_index[term]['tf'] = {}
                for doc_id_b in reversed_index_block[term]['tf']:
                    if doc_id_b in block_doc_to_doc[i]:
                        doc_id = block_doc_to_doc[i][doc_id_b]
                    else:
                        doc_id = doc_id_b
                    reversed_index[term]['tf'][doc_id] = reversed_index_block[term]['tf'][doc_id_b]
    reversed_index = OrderedDict(sorted(reversed_index.items(), key=lambda t: t[0]))
    return reversed_index, dic_documents


###############################################################################
#                                Map Reduce

def create_reversed_index(reversed_index, element):
    doc_id, word = element
    if word in reversed_index:
        if doc_id in reversed_index[word]['tf']:
            reversed_index[word]['tf'][doc_id] += 1
        else:
            reversed_index[word]['idf'] += 1
            reversed_index[word]['tf'][doc_id] = 1
    else:
        reversed_index[word] = {}
        reversed_index[word]['idf'] = 1
        reversed_index[word]['tf'] = {doc_id: 1}
    return reversed_index


def concat_dict(x, y):
    x.update(y)
    return x


def Map_Reduced_Index(collection):
    pre_dic_documents = list(map(lambda doc: {doc.id: doc.title}, collection))
    dic_documents = reduce(concat_dict, pre_dic_documents)

    pre_posting_list = list(map(lambda doc:
                                list(map(lambda word: (doc.id, stemmer.stem(word)),
                                         filter(lambda x: not x.lower() in COMMON_WORDS, doc.word_lists)
                                         )), collection))

    posting_list = reduce(lambda x, y: x + y, pre_posting_list)
    reversed_index = reduce(create_reversed_index, [{}] + posting_list)
    return reversed_index, dic_documents


###############################################################################
#                                      Tools

def terms_max(reversed_index):
    term_nb = 10
    trms_max = list(reversed_index.keys())[:term_nb]
    threshold = min([reversed_index[term]['idf'] for term in trms_max])
    for term in reversed_index:
        cur_idf = reversed_index[term]['idf']
        if threshold < cur_idf:
            new_pos = 0
            while reversed_index[trms_max[new_pos]]['idf'] > cur_idf:
                new_pos += 1
            trms_max.insert(new_pos, term)
            trms_max.remove(trms_max[-1])
            threshold = min([reversed_index[term]['idf'] for term in trms_max])
    return trms_max


def update_CACM_index():
    documents = extract_documents_CACM()
    reversed_index, dic_document = construction_index_one_block(documents)

    # Write Reversed Index
    file = open(os.getcwd() + "/Buffer/" + "Reversed_Index_CACM.json", "w")
    json.dump(reversed_index, file)
    file.close()

    # Write Documents Dictionnary
    file = open(os.getcwd() + "/Buffer/" + "Dict_Documents_CACM.json", "w")
    json.dump(dic_document, file)
    file.close()


def read_CACM_index():
    if not os.path.isfile(os.getcwd() + "/Buffer/" + "Reversed_Index_CACM.json"):
        update_CACM_index()

    # Read Reversed Index
    file = open(os.getcwd() + "/Buffer/" + "Reversed_Index_CACM.json", "r")
    reversed_index = InvertedIndex(json.load(file))
    file.close()

    if not os.path.isfile(os.getcwd() + "/Buffer/" + "Dict_Documents_CACM.json"):
        update_CACM_index()

    # Read Dictionnary of documents
    file = open(os.getcwd() + "/Buffer/" + "Dict_Documents_CACM.json", "r")
    dic_documents = json.load(file)
    file.close()
    return reversed_index, dic_documents


def update_CS276_index():
    reversed_index, dic_document = BSBI_Index_construction_CS276()

    # Write Reversed Index
    file = open(os.getcwd() + "/Buffer/" + "Reversed_Index_CS276.json", "w")
    json.dump(reversed_index, file)
    file.close()

    # Write Documents Dictionnary
    file = open(os.getcwd() + "/Buffer/" + "Dict_Documents_CS276.json", "w")
    json.dump(dic_document, file)
    file.close()


def read_CS276_index():
    if not os.path.isfile(os.getcwd() + "/Buffer/" + "Reversed_Index_CS276.json"):
        update_CS276_index()
    # Read Reversed Index
    file = open(os.getcwd() + "/Buffer/" + "Reversed_Index_CS276.json", "r")
    reversed_index = InvertedIndex(json.load(file))
    file.close()

    if not os.path.isfile(os.getcwd() + "/Buffer/" + "Dict_Documents_CS276.json"):
        update_CS276_index()
    # Read Dictionnary of documents
    file = open(os.getcwd() + "/Buffer/" + "Dict_Documents_CS276.json", "r")
    dic_documents = json.load(file)
    file.close()
    return reversed_index, dic_documents


if __name__ == "__main__":
    # Update written indexes
    # update_CACM_index()
    # update_CS276_index()
    reversed_index, _ = read_CACM_index()
    print("Top 10 CACM : ", terms_max(reversed_index))

    reversed_index, _ = read_CS276_index()
    print("Top 10 CS276 : ", terms_max(reversed_index))

"""documents = extract_documents_CACM()

cProfile.run("reversed_index,_ = construction_index_one_block(documents)")

         13246135 function calls in 7.371 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.012    0.012    7.371    7.371 <string>:1(<module>)
        1    1.433    1.433    7.298    7.298 III_Index_Inverse.py:19(create_posting_list)
   107508    0.011    0.000    0.011    0.000 III_Index_Inverse.py:37(<lambda>)
        1    0.061    0.061    7.359    7.359 III_Index_Inverse.py:40(construction_index_one_block)
   208440    2.994    0.000    5.739    0.000 snowball.py:1197(stem)
   150848    0.328    0.000    0.364    0.000 snowball.py:213(_r1r2_standard)
    29074    0.022    0.000    0.025    0.000 util.py:8(suffix_replace)
        1    0.000    0.000    7.371    7.371 {built-in method builtins.exec}
  1060064    0.126    0.000    0.126    0.000 {built-in method builtins.len}
        1    0.082    0.082    0.093    0.093 {built-in method builtins.sorted}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
 10181381    1.973    0.000    1.973    0.000 {method 'endswith' of 'str' objects}
    27774    0.007    0.000    0.007    0.000 {method 'join' of 'str' objects}
   416880    0.068    0.000    0.068    0.000 {method 'lower' of 'str' objects}
   607504    0.140    0.000    0.140    0.000 {method 'replace' of 'str' objects}
   456656    0.115    0.000    0.115    0.000 {method 'startswith' of 'str' objects}

    
cProfile.run("inverted_index,_= Map_Reduced_Index(documents)")

         9614755 function calls in 8.388 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.010    0.010    8.388    8.388 <string>:1(<module>)
   107508    0.167    0.000    0.167    0.000 III_Index_Inverse.py:148(create_reversed_index)
     3203    0.001    0.000    0.002    0.000 III_Index_Inverse.py:163(concat_dict)
        1    0.006    0.006    8.378    8.378 III_Index_Inverse.py:168(Map_Reduced_Index)
     3204    0.001    0.000    0.001    0.000 III_Index_Inverse.py:169(<lambda>)
     3204    0.114    0.000    6.608    0.002 III_Index_Inverse.py:172(<lambda>)
   107508    0.092    0.000    4.985    0.000 III_Index_Inverse.py:173(<lambda>)
   208440    1.467    0.000    1.509    0.000 III_Index_Inverse.py:174(<lambda>)
     3203    0.806    0.000    0.806    0.000 III_Index_Inverse.py:177(<lambda>)
   107508    2.553    0.000    4.893    0.000 snowball.py:1197(stem)
   105897    0.302    0.000    0.333    0.000 snowball.py:213(_r1r2_standard)
    28594    0.021    0.000    0.024    0.000 util.py:8(suffix_replace)
        3    0.788    0.263    1.763    0.588 {built-in method _functools.reduce}
        1    0.000    0.000    8.388    8.388 {built-in method builtins.exec}
   757723    0.108    0.000    0.108    0.000 {built-in method builtins.len}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
  7086030    1.660    0.000    1.660    0.000 {method 'endswith' of 'str' objects}
    24072    0.007    0.000    0.007    0.000 {method 'join' of 'str' objects}
   315948    0.063    0.000    0.063    0.000 {method 'lower' of 'str' objects}
   427700    0.122    0.000    0.122    0.000 {method 'replace' of 'str' objects}
   321803    0.098    0.000    0.098    0.000 {method 'startswith' of 'str' objects}
     3203    0.001    0.000    0.001    0.000 {method 'update' of 'dict' objects}
"""

""" cProfile.run("test_mp()") # Multiprocessing

2527 function calls (2496 primitive calls) in 372.860 seconds
"""

"""
cProfile.run("test_conc()") # Concurrent
5436 function calls (5416 primitive calls) in 330.018 seconds"""

"""
Temps d'éxécution en fonction du Nombre de blocs
 10     -->     407s
 100    -->     374s
 1000   -->     1742s
 """

"""test document read as yield or set on CS276 full inverted index creation
yield -->   532s
set   -->   461s
"""
