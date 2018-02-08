import math

from I_Importation_Donnees import *
from III_Index_Inverse import *
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer("english")
COMMON_WORDS = set(stemmer.stem(word) for word in read_to_list(script_dir + common_words_relative_location))


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


def boolean_search_for_evaluation(index, dict_title, query, doc_coll):
    filtered_query = [stemmer.stem(word) for word in query.word_lists if stemmer.stem(word) not in COMMON_WORDS]
    string_query = " and ".join(filtered_query)
    retreived_doc_ids = boolean_search(string_query, index, dict_title)
    not_retreived_do_ids = set(dict_title.keys()) - retreived_doc_ids
    result = []
    for doc_id in retreived_doc_ids:
        result.append((doc_id, 1))
    for doc_id in not_retreived_do_ids:
        result.append((doc_id, 0))
    return result


def extract_terms(query):
    for word in filter(lambda w: w not in COMMON_WORDS, query.split()):
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


def vectorial_search(reversed_index, dic_documents, query, weight_tf_idf_query, weight_tf_idf_doc, collection):
    nb_docs = len(dic_documents)  # nombre de documents dans la collection
    nq = 0  # représente la somme des poids au carré des termes de la query par rapport au document query
    nd = defaultdict(int)  # facteur de normalisation de chaque document
    # s est le vecteur similarité s[j] est la similarité du doc j avec la query,
    # s est appelé aussi score
    s = [0 for _ in range(nb_docs + 1)]
    term_list_query = [stemmer.stem(word) for word in re.split("\W+|\d+", query) if
                       stemmer.stem(word) not in COMMON_WORDS]
    reversed_index_query = construction_index_query(query)  # Index inversé sur la requête
    for term in term_list_query:  # on parcourt les mots de la query
        wq = weight_tf_idf_query(term, reversed_index_query, reversed_index, nb_docs, term_list_query)
        nq += wq ** 2
        for doc_id in reversed_index[term]['tf']:
            wt = weight_tf_idf_doc(term, doc_id, reversed_index, nb_docs, collection)
            doc_id = int(doc_id)
            nd[doc_id] += wt ** 2
            s[doc_id] += wt * wq
    for j in range(nb_docs + 1):
        if s[j] != 0:
            s[j] = s[j] / (sqrt(nq) * sqrt(nd[j]))
    return sorted(enumerate(s), key=lambda x: -x[1])

#Diverses fonctions de poids...

#1 (celui de la page 95)
def weight_tf_idf_query1(term, reversed_index_query, reversed_index, nb_docs, term_list_query):
    if term in reversed_index:  # si le terme n'est dans aucun document, on ne le considerera pas pour la suite
        tf_td = reversed_index_query[term]['tf']
        df_t = reversed_index[term]['idf']
        return (1 + log(tf_td)) * log(nb_docs / df_t)
    else:
        return 0

def weight_tf_idf_doc1(term, doc_id, reversed_index, nb_docs, collection):
    tf_td = reversed_index[term]['tf'][doc_id]
    df_t = reversed_index[term]['idf']
    return (1 + log(tf_td)) * log(nb_docs / df_t)

#2 (Première ligne)
def weight_tf_idf_query2(term, reversed_index_query, reversed_index, nb_docs, term_list_query):
    if term in reversed_index:  # si le terme n'est dans aucun document, on ne le considerera pas pour la suite
        tf_td = reversed_index_query[term]['tf']
        return tf_td
    else:
        return 0

def weight_tf_idf_doc2(term, doc_id, reversed_index, nb_docs, collection):
    tf_td = reversed_index[term]['tf'][doc_id]
    return tf_td

#3 (Deuxième ligne)
def weight_tf_idf_query3(term, reversed_index_query, reversed_index, nb_docs, term_list_query):
    weight_sum = 0
    moy_tf = 0
    if term in reversed_index:  # si le terme n'est dans aucun document, on ne le considerera pas pour la suite
        for word in term_list_query:
            tf = reversed_index_query[word]['tf']
            df = reversed_index_query[word]['idf']
            weight_sum += (1+log(tf))*df
            moy_tf += tf
        moy_tf = moy_tf/len(term_list_query)
        weight_sum = weight_sum/(1+log(moy_tf))
        tf_td = reversed_index_query[term]['tf']
        df_t = reversed_index[term]['idf']
        return (1 + log(tf_td))*df_t/(1+log(moy_tf))/weight_sum
    else:
        return 0

def weight_tf_idf_doc3(term, doc_id, reversed_index, nb_docs, collection):
    nd = 0
    sum_weight = 0
    moy_tf = 0

    tf_td = reversed_index[term]['tf'][doc_id]
    df_t = reversed_index[term]['idf']
    list_of_terms = list_of_words(doc_id, collection)
    if len(list_of_terms) != 0:
        for word in list_of_terms:
            moy_tf += reversed_index[word]['tf'][doc_id]
            sum_weight += small_weight_tf_idf_doc3(word, doc_id, list_of_terms)
        moy_tf = moy_tf/len(list_of_terms)
        nd = 1/sqrt(sum_weight)
        return (1 + log(tf_td))/(1+log(moy_tf)) * df_t * nd
    return 0

def small_weight_tf_idf_doc3(term, doc_id, list_of_terms):
    moy_tf = 0
    tf_td = reversed_index[term]['tf'][doc_id]
    df_t = reversed_index[term]['idf']
    for word in list_of_terms:
        moy_tf += reversed_index[word]['tf'][doc_id]
    moy_tf = moy_tf / len(list_of_terms)
    return (1 + log(tf_td)) / (1 + log(moy_tf)) * df_t


def list_of_words(id_doc, collection):
    list_of_stemmed_words = []
    for document in collection:
        if document.id == id_doc:
            list_of_words = document.word_lists
            for word in list_of_words:
                stemmed_word = stemmer.stem(word)
                if stemmed_word not in COMMON_WORDS:
                    list_of_stemmed_words += [stemmed_word]
    return list_of_stemmed_words


if __name__ == "__main__":
    reversed_index, dic_doc = read_CACM_index()
    # reversed_index, dic_doc = read_CS276_index()
    # print(len(give_title(boolean_search('not Stanford', reversed_index, dic_doc), dic_doc)))
    collection = extract_documents_CACM()
    query_40 = """ List all articles dealing with data types in the following languages:
Pascal, CLU, Alphard, Russell, Ada, ALGOL 68, EL1.  List any other languages
that are referenced frequently in papers on the above languages (e.g. catch
any languages with interesting type structures that I might have missed)."""

    query_60 = """Hardware and software relating to database management systems.
Database packages, back end computers, special associative hardware
with microcomputers attached to disk heads or things like RAP, 
relational or network (CODASYL) or hierarchical models, systems
like SYSTEM R, IMS, ADABAS, TOTAL, etc."""

   # print(reversed_index['algorithm'])
    #print(list_of_words(1989,reversed_index, collection))
    #result = vectorial_search(reversed_index, dic_doc, query_60, weight_tf_idf_query1, weight_tf_idf_doc1, collection)
    #result2 = vectorial_search(reversed_index, dic_doc, query_60, weight_tf_idf_query2, weight_tf_idf_doc2, collection)
    result3 = vectorial_search(reversed_index, dic_doc, query_60, weight_tf_idf_query3, weight_tf_idf_doc3, collection)
    #print([res[0] for res in result[:10]])
    #print([res[0] for res in result2[:10]])
    print([res for res in result3[:10]])
