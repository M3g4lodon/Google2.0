from collections import OrderedDict
from functools import reduce
from nltk.stem.snowball import SnowballStemmer
import json
import re
from import_data import *

stemmer = SnowballStemmer("english")
COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)


###############################################################################
# ================================  PARTIE 2  =============================== #
###############################################################################


###############################################################################
#                           Block Sorted Based Index

def create_posting_list(collection):
    dic_terms = {}
    dic_documents = {}
    posting_list = []
    j = 1  # identifiant de terme
    for doc in collection:
        dic_documents[doc.id] = doc.title  # on remplit le dictionnaire de documents
        for word in doc.word_lists:
            stemmed_word = stemmer.stem(word)
            if word.lower() not in COMMON_WORDS:
                if stemmed_word not in dic_terms:
                    dic_terms[stemmed_word] = j
                    posting_list += [
                        (stemmed_word, doc.id)]  # on construit la posting list avec les termes et pas leur ID
                    j += 1
                else:  # on prend en compte les différentes occurrences
                    posting_list += [(stemmed_word, doc.id)]

    return sorted(posting_list, key=lambda x: x[0]), dic_documents


def construction_index_one_block(collection):
    posting_list, dic_documents = create_posting_list(collection)
    reversed_index = OrderedDict()
    for term, doc_ID in posting_list:
        if term in reversed_index:
            if doc_ID in reversed_index[term]['tf']:
                reversed_index[term]['tf'][doc_ID] += 1
            else:
                reversed_index[term]['tf'][doc_ID] = 1
                reversed_index[term]['idf'] += 1
        else:
            reversed_index[term] = {'idf': 1, 'tf': {doc_ID: 1}}
    return reversed_index, dic_documents


def write_in_buffer(block_index, reversed_index, dic_documents):
    # Write Reversed Index
    file = open(os.getcwd() + "/Buffer/" + "ReversedIndex_" + str(block_index), "w")
    json.dump(reversed_index, file)
    file.close()

    # Write Documents Dictionnary
    file = open(os.getcwd() + "/Buffer/" + "Dict_Documents_" + str(block_index), "w")
    json.dump(dic_documents, file)
    file.close()


def read_in_buffer(block_index):
    # Read Reversed Index
    file = open(os.getcwd() + "/Buffer/" + "ReversedIndex_" + str(block_index), "r")
    reversed_index = OrderedDict(json.load(file))
    file.close()

    # Read Dictionnary of documents
    file = open(os.getcwd() + "/Buffer/" + "Dict_Documents_" + str(block_index), "r")
    dic_documents = json.load(file)
    file.close()
    return reversed_index, dic_documents


def BSBI_Index_construction_CS276():
    """CS276 only"""
    reversed_index = OrderedDict()
    dic_documents = {}
    block_nb = 10
    for i in range(block_nb):
        # Read a block
        block_documents = extract_documents_CS276(i)
        # Construct a block reversed index
        block_index, dic_doc_blocks = construction_index_one_block(block_documents)
        # Write the block reversed index on the disk
        write_in_buffer(i, block_index, dic_doc_blocks)

    # Merge the block inversed indexes
    block_doc_to_doc = {}  # dictionnaire de passage
    for i in range(block_nb):
        reversed_index_block, dic_doc_blocks = read_in_buffer(i)
        block_doc_to_doc[i] = {}
        if not dic_documents:  # If it's empty
            dic_documents = dic_doc_blocks
        else:
            for doc_id_b in dic_doc_blocks:
                if doc_id_b in dic_documents:
                    new_id = max(dic_documents.keys()) + 1
                    dic_documents[new_id] = dic_doc_blocks[doc_id_b]
                    block_doc_to_doc[i][doc_id_b] = new_id
                else:
                    dic_documents[doc_id_b] = dic_documents[doc_id_b]
        for term in reversed_index_block:
            reversed_index[term] = {}
            reversed_index[term]['idf'] = reversed_index_block[term]['idf']
            reversed_index[term]['tf'] = {}
            for doc_id_b in reversed_index_block[term]['tf']:
                if doc_id_b in block_doc_to_doc[i]:
                    doc_id = block_doc_to_doc[i][doc_id_b]
                else:
                    doc_id = doc_id_b
                reversed_index[term]['tf'][doc_id] = reversed_index_block[term]['tf'][doc_id_b]
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
    pre_dic_documents = list(map(lambda doc: {doc.id: doc}, collection))
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
    trms_max = []
    max_idf = 0
    for term in reversed_index:
        if max_idf < reversed_index[term]['idf']:
            trms_max = [term]
            max_idf = reversed_index[term]['idf']
        elif max_idf == reversed_index[term]['idf']:
            trms_max.append(term)

    return trms_max

def boolean_search(query, index):
    word_list_query = re.split("\W+|\d+", query)
    operator_list = ['and', 'or', 'not']
    i = 0
    doc_set_and, doc_set_or, doc_set_not = set(), set(), set()
    last_bool = 'or'
    while i < len(word_list_query):
        word = word_list_query[i].lower()
        if word in operator_list:
            if word == 'and':
                last_bool = 'and'
                i +=1
            elif word == 'or':
                last_bool = 'or'
                i += 1
            else: #word == 'NOT':
                last_bool = 'not'
                i += 1
        else:
            word = stemmer.stem(word)
            if word in index:
                if last_bool == 'and':
                    for key in index[word]['tf']:
                        doc_set_and.add(key)
                elif last_bool == 'or':
                    for key in index[word]['tf']:
                        doc_set_or.add(key)
                elif last_bool == 'not':
                    for key in index[word]['tf']:
                        doc_set_not.add(key)
                else:
                    raise EnvironmentError
            i+=1
    if doc_set_and == set():
        return doc_set_or.difference(doc_set_not)
    else:
        return doc_set_and.intersection(doc_set_or).difference(doc_set_not)
##Pour le and --> il faut qu'il y ait les deux mots dans les documents !


def give_title(docID_list, dict_title):
    title_list = []
    for docID in docID_list:
        title_list += [dict_title[docID]]
    return title_list


if __name__ == "__main__":
    documents = extract_documents_CACM()
    # documents = extract_documents_CS276()

    # Test Reverse Index
    # print(reversed_index[stemmer.stem('system')]['tf'][92])  # Should be equal to 2

    # Test Write + Read in Buffer
    reversed_index, index_document = construction_index_one_block(documents)
    # print(reversed_index)
    write_in_buffer(0, reversed_index, index_document)
    RI1, ID1 = read_in_buffer(0)
    # print(index_document)
    # print(ID1)
    # print(reversed_index == RI1)
    # print(index_document == ID1)

    # Index construction on CS276
    # reversed_index_BSBI, _ = BSBI_Index_construction_CS276()
    # documents = extract_documents_CS276(0)
    # reversed_index, _ = construction_index_one_block(documents)
    # print(terms_max(reversed_index))
    #documents = extract_documents_CS276(0)
    #reversed_index, _ = construction_index_one_block(documents)
    print(give_title(boolean_search('Subtractions and Digital', reversed_index), dic_doc))

    # Map Reduce Construction
    # inverted_index,_= Map_Reduced_Index(documents)
    # cProfile.run("inverted_index,_= Map_Reduced_Index(documents)")


    # TODO test unitaire,
    # TODO stocker les résultats intermédiaires en mémoire,
    # TODO multihtreader les blocs,
    # TODO pouvoir avoir plus de 10 blocs

"""documents = extract_documents_CACM()

cProfile.run("reversed_index,_ = construction_index_one_block(documents)")

         13246135 function calls in 7.371 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.012    0.012    7.371    7.371 <string>:1(<module>)
        1    1.433    1.433    7.298    7.298 partie_2.py:19(create_posting_list)
   107508    0.011    0.000    0.011    0.000 partie_2.py:37(<lambda>)
        1    0.061    0.061    7.359    7.359 partie_2.py:40(construction_index_one_block)
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
   107508    0.167    0.000    0.167    0.000 partie_2.py:148(create_reversed_index)
     3203    0.001    0.000    0.002    0.000 partie_2.py:163(concat_dict)
        1    0.006    0.006    8.378    8.378 partie_2.py:168(Map_Reduced_Index)
     3204    0.001    0.000    0.001    0.000 partie_2.py:169(<lambda>)
     3204    0.114    0.000    6.608    0.002 partie_2.py:172(<lambda>)
   107508    0.092    0.000    4.985    0.000 partie_2.py:173(<lambda>)
   208440    1.467    0.000    1.509    0.000 partie_2.py:174(<lambda>)
     3203    0.806    0.000    0.806    0.000 partie_2.py:177(<lambda>)
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
