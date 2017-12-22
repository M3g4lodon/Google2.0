from collections import OrderedDict, Counter
from functools import reduce
from nltk.stem.snowball import SnowballStemmer
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
    for term in reversed_index:
        line = "term : " + term + ", "
        line += "idf : " + str(reversed_index[term]['idf']) + ", "
        line += "tf : {"
        for doc_ID in reversed_index[term]['tf']:
            line += str(doc_ID) + " : " + str(reversed_index[term]['tf'][doc_ID]) + ", "
        line = line[:-2]  # Delete the last ','
        line += "}\n"
        file.write(line)
    file.close()

    # Write Documents Dictionnary
    file = open(os.getcwd() + "/Buffer/" + "Dict_Documents_" + str(block_index), "w")
    for doc_id in dic_documents:
        line = "id : " + str(doc_id)
        line += ", title : " + dic_documents[doc_id] + "\n"
        file.write(line)
    file.close()


def read_in_buffer(block_index):
    # Read Reversed Index
    reversed_index = OrderedDict()
    file = open(os.getcwd() + "/Buffer/" + "ReversedIndex_" + str(block_index), "r")
    lines = file.readlines()
    file.close()
    for line in lines:
        term = re.search(r"term : (.+), idf", line)[1]
        idf = int(re.search(r"idf : (\w+)", line)[1])
        reversed_index[term] = {'idf': idf, 'tf': {}}
        tfs = re.search(r'tf : {(.+)}', line)[1]
        for key_val in tfs.split(','):
            doc_id, tf = key_val.split(':')
            reversed_index[term]['tf'][int(doc_id)] = int(tf)

    # Read Dictionnary of documents
    dic_documents = {}
    file = open(os.getcwd() + "/Buffer/" + "Dict_Documents_" + str(block_index), "r")
    lines = file.readlines()
    file.close()
    for line in lines:
        doc_id = re.search(r"id : (\w+), title", line)[1]
        title = re.search(r'title : (.+)', line)[1]
        dic_documents[doc_id] = title
    return reversed_index, dic_documents


def BSBI_Index_construction_CS276():
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
            reversed_index[word]['tf'][doc_id] +=1
        else:
            reversed_index[word]['idf'] +=1
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
    reversed_index=reduce(create_reversed_index,[{}]+posting_list)
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
    reversed_index,_ = construction_index_one_block(documents)
    # print(reversed_index)
    # write_in_buffer(0, reversed_index)
    # RI1 = read_in_buffer(0)
    # print(reversed_index == RI1)

    # Index construction on CS276
    # reversed_index_BSBI, _ = BSBI_Index_construction_CS276()
    # documents = extract_documents_CS276(0)
    # reversed_index, _ = construction_index_one_block(documents)
    print(terms_max(reversed_index))
    #documents = extract_documents_CS276(0)
    #reversed_index, _ = construction_index_one_block(documents)
    print(give_title(boolean_search('Subtractions and Digital', reversed_index), dic_doc))

    # Map Reduce Construction
    # print(Map_Reduced_Index(documents))

    # TODO test unitaire
