from collections import OrderedDict
from nltk.stem.snowball import SnowballStemmer

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
        dic_documents[doc.id] = doc  # on remplit le dictionnaire de documents
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

    return sorted(posting_list, key=lambda x: x[0])


def construction_index(collection):
    posting_list = create_posting_list(collection)
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
    return posting_list, reversed_index


if __name__ == "__main__":
    documents = extract_documents_CACM()
    # documents = extract_documents_CS276()
    posting_list, reversed_index = construction_index(documents)
    print(reversed_index[stemmer.stem('system')]['tf'][92])  # Should be equal to 2
