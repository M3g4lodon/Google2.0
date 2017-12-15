from collections import OrderedDict
from nltk.stem.snowball import SnowballStemmer
import re
from import_data import *

stemmer = SnowballStemmer("english")
COMMON_WORDS = read_to_list(script_dir + common_words_relative_location)


###############################################################################
# ================================  PARTIE 2  =============================== #
###############################################################################

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


if __name__ == "__main__":
    # documents = extract_documents_CACM()

    # Test Reverse Index
    # print(reversed_index[stemmer.stem('system')]['tf'][92])  # Should be equal to 2

    # test Write + Read in Buffer
    # reversed_index = construction_index_one_block(documents)
    # write_in_buffer(0, reversed_index)
    # RI1 = read_in_buffer(0)
    # print(reversed_index == RI1)

    # Index construction on CS276
    # reversed_index_BSBI, _ = BSBI_Index_construction_CS276()
    documents = extract_documents_CS276(0)
    reversed_index, _ = construction_index_one_block(documents)
    print(terms_max(reversed_index))
