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



# def weight_freq_norm(term,query, inverted_index, nb_docs, doc_id="0"):
#     if term in inverted_index:
#         tf_td = reversed_index[term]['tf'][doc_id]
#         max_tj=tf_td
#
#         for term_i in extract_terms(query):
#             if term_i in reversed_index:
#                 # TODO
#                 pass
#
#     else:
#         return 0
#
# # TODO recherche booléenne pour ne sélectionner que les documents ayant au moins un des termes de la requête




##Pour le and --> il faut qu'il y ait les deux mots dans les documents !



def norm_factor(collection, doc_id):
    norm_factor_doc = 0
    doc_id = int(doc_id)
    for doc in collection:
        if doc.id == doc_id:
            for word in doc.word_lists:
                if word.lower() not in COMMON_WORDS:
                    norm_factor_doc += 1
            return norm_factor_doc


def vectorial_search(reversed_index, dic_documents, query, weight_tf_idf_query, weight_tf_idf_doc):
    nb_docs = len(dic_documents)  # nombre de documents dans la collection
    nq = 0  # représente la somme des poids au carré des termes de la query par rapport au document query
    nd = defaultdict(int) # facteur de normalisation de chaque documents
    # s est le vecteur similarité s[j] est la similarité du doc j avec la query,
    # s est appelé aussi score
    s = [0 for _ in range(nb_docs + 1)]
    word_list_query = re.split("\W+|\d+", query)
    reversed_index_query = construction_index_query(query) # Index inversé sur la requête
    for token in word_list_query:  # on parcourt les mots de la query
        term = stemmer.stem(token)
        wq = weight_tf_idf_query(term, reversed_index_query, reversed_index, nb_docs)
        nq += wq ** 2
        for doc_id in reversed_index[term]['tf']:
            wt = weight_tf_idf_doc(term, doc_id, reversed_index, nb_docs)
            doc_id = int(doc_id)
            nd[doc_id] += wt ** 2
            s[doc_id] += wt * wq
    for j in range(nb_docs+1):
        if s[j] != 0:
            s[j] = s[j] / (sqrt(nq)*sqrt(nd[j]))
    return ordered_score(s)


def ordered_score(s):
    return sorted(enumerate(s), key=lambda x: -x[1])


def weight_tf_idf_query1(term, reversed_index_query, reversed_index, nb_docs):
    if term in reversed_index:  # si le terme n'est dans aucun document, on ne le considerera pas pour la suite
        tf_td = reversed_index_query[term]['tf']
        df_t = reversed_index[term]['idf']
        return (1 + log(tf_td)) * log(nb_docs / df_t)
    else:
        return 0


def weight_tf_idf_doc1(term, doc_id, reversed_index, nb_docs):
    tf_td = reversed_index[term]['tf'][doc_id]
    df_t = reversed_index[term]['idf']
    return (1 + log(tf_td)) * log(nb_docs / df_t)


if __name__ == "__main__":
    reversed_index, dic_doc = read_CACM_index()
    #reversed_index, dic_doc = read_CS276_index()
    #print(len(give_title(boolean_search('not Stanford', reversed_index, dic_doc), dic_doc)))
    collection = extract_documents_CACM()
    print(vectorial_search(reversed_index, dic_doc,"Systems in which variable time-lags are present are of common occurrence in biology.  Variable  flow rates are a common cause of these variable lags. At present no extensive body of knowledge exists  concerning the effects which these variable lags can cause.  Shown here is a method of reducing some  differential-difference equations to ordinary differential equations which can then be studied numerically  with ease.  Subsequent study will deal with situations in which multiple-lags and lags dependent on the  solution itself are present.",weight_tf_idf_query1, weight_tf_idf_doc1))
