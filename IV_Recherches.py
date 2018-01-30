import math

from I_Importation_Donnees import *
from III_Index_Inverse import *
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer("english")
COMMON_WORDS = set( stemmer.stem(word) for word in read_to_list(script_dir + common_words_relative_location))


###################################################################
def give_title(docID_list, dict_title):
    return [dict_title[docID] for docID in docID_list]


def boolean_search(query, index, dict_title):
    word_list_query = re.split("\W+|\d+", query)
    operator_list = ['and', 'or', 'not']
    i = 0
    result = set()
    last_bool = 'or'
    while i < len(word_list_query):
        word = word_list_query[i].lower()
        if word in operator_list:
            if i == 0 and word != 'or':
                result = set(dict_title.keys())
            if word == 'and':
                last_bool = 'and'
            elif word == 'or':
                last_bool = 'or'
            else:  # word == 'NOT':
                last_bool = 'not'
        else:
            word = stemmer.stem(word)
            subset = set(index[word]['tf'])
            if word in index:
                if last_bool == 'and':
                    result = result.intersection(subset)
                elif last_bool == 'or':
                    result = result.union(subset)
                elif last_bool == 'not':
                    result = result.difference(subset)
        i += 1
    return result

def boolean_search_for_evaluation(index,dict_title,query,doc_coll):
    filtered_query=[stemmer.stem(word) for word in query.word_lists if stemmer.stem(word) not in COMMON_WORDS]
    string_query=" and ".join(filtered_query)
    retreived_doc_ids=boolean_search(string_query,index,dict_title)
    not_retreived_do_ids= set(dict_title.keys()) - retreived_doc_ids
    result=[]
    for doc_id in retreived_doc_ids:
        result.append((doc_id,1))
    for doc_id in not_retreived_do_ids:
        result.append((doc_id,0))
    return result


def extract_terms(query):
    for word in filter(lambda w: w not in COMMON_WORDS,query.split()):
        yield stemmer.stem(word)


def weight_tf_idf(term,query, inverted_index, nb_docs, doc_id="0"):
    if term in inverted_index:
        tf_td = reversed_index[term]['tf'][doc_id]
        df_t = reversed_index[term]['idf']
        return (1 + math.log(tf_td)) * math.log(nb_docs / df_t)
    else:
        return 0


def weight_tf_idf_norm(term,query, inverted_index, nb_docs, doc_id="0"):
    if term in inverted_index:
        tf_td = reversed_index[term]['tf'][doc_id]
        df_t = reversed_index[term]['idf']
        return (1 + math.log(tf_td)) * math.log(nb_docs / df_t)*norm
    else:
        return 0


def weight_freq_norm(term,query, inverted_index, nb_docs, doc_id="0"):
    if term in inverted_index:
        tf_td = reversed_index[term]['tf'][doc_id]
        max_tj=tf_td

        for term_i in extract_terms(query):
            if term_i in reversed_index:
                # TODO
                pass

    else:
        return 0


def vector_search(weight_function, query, index, dict_title):
    nb_docs = len(dict_title)
    result = [0] * nb_docs
    query_index = {}
    for term in extract_terms(query):
        if query_index[term]['tf']:
            query_index[term]['tf']["0"] += 1
        else:
            query_index[term]['tf']["0"] = 1
            query_index[term] = {'idf': 1}
    # TODO recherche booléenne pour ne sélectionner que les documents ayant au moins un des termes de la requête

    for term in extract_terms(query):
        pass
    return result


##Pour le and --> il faut qu'il y ait les deux mots dans les documents !

if __name__ == "__main__":
    reversed_index, dic_doc = read_CACM_index()
    #reversed_index, dic_doc = read_CS276_index()
    print(give_title(boolean_search('analysi', reversed_index, dic_doc),dic_doc))
