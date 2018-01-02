from III_Index_Inverse import *


###################################################################
def give_title(docID_list, dict_title):
    title_list = []
    for docID in docID_list:
        title_list += [dict_title[docID]]
    return title_list


def boolean_search(query, index, dict_title):
    word_list_query = re.split("\W+|\d+", query)
    operator_list = ['and', 'or', 'not']
    i = 0
    result = set()
    last_bool = 'or'
    while i < len(word_list_query):
        word = word_list_query[i].lower()
        if word in operator_list:
            if i == 0:
                result = set(dict_title.keys())
            if word == 'and':
                last_bool = 'and'
            elif word == 'or':
                last_bool = 'or'
            else:  # word == 'NOT':
                last_bool = 'not'
        else:
            word = stemmer.stem(word)
            subset=set(index[word]['tf'])
            if word in index:
                if last_bool == 'and':
                    result = result.intersection(subset)
                elif last_bool == 'or':
                    result = result.union(subset)
                elif last_bool == 'not':
                    result = result.difference(subset)
        i += 1

    return result


##Pour le and --> il faut qu'il y ait les deux mots dans les documents !

if __name__ == "__main__":
    reversed_index, dic_doc = read_CS276_index()
    print(len(give_title(boolean_search('not Stanford', reversed_index, dic_doc), dic_doc)))
