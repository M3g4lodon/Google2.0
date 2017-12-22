from III_Index_Inverse  import *

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

if __name__=="__main__":
    documents = extract_documents_CACM()
    reversed_index, dic_doc = construction_index_one_block(documents)
    print(give_title(boolean_search('Subtractions and Digital', reversed_index), dic_doc))