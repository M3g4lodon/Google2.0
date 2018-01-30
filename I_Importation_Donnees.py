import os
import re
from itertools import islice

script_dir = os.getcwd()
# donne la localisation actuelle de ton dossier projet
CACM_ALL = "/Data/CACM/cacm.all"
CACM_QUERIES = "/Data/CACM/query.text"
CACM_QRELS = "/Data/CACM/qrels.text"
cs276_relative_location = ["/Data/CS276/" + str(i) for i in range(10)]
common_words_relative_location = "/Data/CACM/common_words"


class Document:
    __ID = 0

    def __init__(self, id=None):
        if id is None:
            self.id = Document.__ID
            Document.__ID += 1
        else:
            self.id = id  # .I
        self.title = None  # .T
        self.summary = None  # .W
        self.keywords = list()  # .K
        self.word_lists = list()
        self.linked_docs = list()  # Used for queries, filled with the good results (doc.id)

    def __repr__(self):

        res = "Id : " + str(self.id) + "\n"
        if self.title is not None:
            res += "Title : " + str(self.title) + "\n"
        if self.summary is not None:
            res += "Summary : " + str(self.summary) + "\n"
        if self.keywords:
            res += "Keywords : " + str(self.keywords) + "\n"
        if self.word_lists:
            res += "Words  : " + str(self.word_lists) + "\n"
        if self.linked_docs:
            res += "Related Documents : " + str(self.linked_docs)
        return res


def files_location_CS276():
    """Return all the files locations of CS276 collections"""
    files_set = set()
    for folder in cs276_relative_location:
        for file_name in os.listdir(script_dir + folder):
            files_set.add((script_dir + folder + '/' + file_name))
    return files_set


def files_part(i, n):
    """Return the ith part of the files set sliced in n parts"""
    files_set = files_location_CS276()
    files_nb = len(files_set)
    return islice(files_set, i * files_nb // n, (i + 1) * files_nb // n, 1)


def extract_documents_CS276(files_location=None):
    folders_root = cs276_relative_location
    collections = set()
    # Read all blocks
    if files_location is None:
        for folder in folders_root:
            for file_name in os.listdir(script_dir + folder):
                file = open(script_dir + folder + '/' + file_name, 'r')
                res = file.read()
                file.close()
                doc = Document()
                doc.title = file_name
                doc.word_lists = res.split()
                collections.add(doc)

    else:
        for file_location in files_location:
            file = open(file_location, 'r')
            res = file.read()
            file.close()
            doc = Document()
            doc.title = file_location.split('/')[-1]
            doc.word_lists = res.split()
            collections.add(doc)

    return collections


def read_to_list(file_location):
    """
    Open, read a file in file_location and return the list of lines of the document
    :param file_location :string
    :return: list
    """
    file = open(file_location, "r")
    res = file.read().split("\n")  # on crée une liste des lignes du document, split découpe une chaine de caractère
    file.close()
    return res


def read_CACM(file_path):
    """
    Read a file and create documents
    :return: list of documents CACM
    """
    input_data = read_to_list(script_dir + file_path)
    collections = set()
    # Transforme une liste en itérable,
    # next passe à l'élément suivant de la liste,
    # si c'est la fin ca raise l'exception StopIteration
    iter_lines = iter(input_data)
    line = next(iter_lines)
    try:

        while True:
            # Cas ligne identifiant
            if line[:2] == ".I":
                # Cas particulier de la première itération
                if 'doc' in dir():
                    collections.add(doc)
                # Nouveau document à rajouter
                doc_id = int(line[2:])
                doc = Document(doc_id)
                line = next(iter_lines)

            # Cas ligne titre
            elif line == ".T":
                doc.title = ""
                line = next(iter_lines)
                while "." != line[0]:
                    if doc.title == "":
                        doc.title += line.lstrip()  # lstrip supprime des espaces en début de ligne
                    else:
                        doc.title += " " + line.lstrip()  # ajoute un espace si ce n'est pas la première ligne
                    doc.word_lists += re.split("\W+|\d+", line.lstrip())
                    line = next(iter_lines)

            # Cas ligne résumé
            elif line == ".W":
                doc.summary = ""
                line = next(iter_lines)
                while "." != line[0]:
                    if doc.summary == "":
                        doc.summary += line.lstrip()  # lstrip supprime des espaces en début de ligne
                    else:
                        doc.summary += " " + line.lstrip()  # ajoute un espace si ce n'est pas la première ligne
                    doc.word_lists += re.split("\W+|\d+", line.lstrip())
                    line = next(iter_lines)

            # Cas ligne mots clés
            elif line == ".K":
                doc.keywords = []
                line = next(iter_lines)
                while "." != line[0]:
                    doc.keywords += map(lambda x: x.replace(', ', ''), line.split(', '))
                    doc.word_lists += re.split("\W+|\d+", line)
                    line = next(iter_lines)

            # Cas ligne quelconque
            else:
                line = next(iter_lines)
    except StopIteration:
        # On rajoute dernier document à la 'main'
        collections.add(doc)

    return collections


def extract_documents_CACM():
    return read_CACM(CACM_ALL)


def extract_queries_CACM():
    queries_collection = read_CACM(CACM_QUERIES)
    qrels = read_to_list(script_dir + CACM_QRELS)
    if '' in qrels:
        qrels.remove('')
    for qrel in qrels:
        query_id, doc_id = tuple(qrel.split(' ')[:2])
        query = [qr for qr in queries_collection if qr.id == int(query_id)][0]
        query.linked_docs.append(int(doc_id))
    return queries_collection


if __name__ == "__main__":
    print([doc for doc in extract_queries_CACM()][0])

"""cProfile.run("CACM_documents = extract_documents_CACM()")

262655 function calls (262644 primitive calls) in 0.318 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.002    0.002    0.318    0.318 <string>:1(<module>)
        1    0.000    0.000    0.000    0.000 _bootlocale.py:11(getpreferredencoding)
        1    0.000    0.000    0.000    0.000 codecs.py:259(__init__)
        1    0.000    0.000    0.005    0.005 cp1252.py:22(decode)
        4    0.000    0.000    0.000    0.000 enum.py:265(__call__)
        4    0.000    0.000    0.000    0.000 enum.py:515(__new__)
        2    0.000    0.000    0.000    0.000 enum.py:801(__and__)
     9507    0.003    0.000    0.006    0.000 I_Importation_Donnees.py:136(<lambda>)
     3204    0.005    0.000    0.005    0.000 I_Importation_Donnees.py:14(__init__)
        1    0.000    0.000    0.014    0.014 I_Importation_Donnees.py:70(read_to_list)
        1    0.103    0.103    0.316    0.316 I_Importation_Donnees.py:82(extract_documents_CACM)
    25793    0.015    0.000    0.163    0.000 re.py:204(split)
    25793    0.012    0.000    0.012    0.000 re.py:286(_compile)
        2    0.000    0.000    0.000    0.000 sre_compile.py:223(_compile_charset)
        2    0.000    0.000    0.000    0.000 sre_compile.py:250(_optimize_charset)
        2    0.000    0.000    0.000    0.000 sre_compile.py:388(_simple)
        1    0.000    0.000    0.000    0.000 sre_compile.py:414(_get_literal_prefix)
        1    0.000    0.000    0.000    0.000 sre_compile.py:441(_get_charset_prefix)
        1    0.000    0.000    0.000    0.000 sre_compile.py:482(_compile_info)
        2    0.000    0.000    0.000    0.000 sre_compile.py:539(isstring)
        1    0.000    0.000    0.000    0.000 sre_compile.py:542(_code)
        1    0.000    0.000    0.000    0.000 sre_compile.py:557(compile)
      5/1    0.000    0.000    0.000    0.000 sre_compile.py:64(_compile)
        5    0.000    0.000    0.000    0.000 sre_parse.py:111(__init__)
       10    0.000    0.000    0.000    0.000 sre_parse.py:159(__len__)
       20    0.000    0.000    0.000    0.000 sre_parse.py:163(__getitem__)
        2    0.000    0.000    0.000    0.000 sre_parse.py:167(__setitem__)
        3    0.000    0.000    0.000    0.000 sre_parse.py:171(append)
      7/3    0.000    0.000    0.000    0.000 sre_parse.py:173(getwidth)
        1    0.000    0.000    0.000    0.000 sre_parse.py:223(__init__)
        6    0.000    0.000    0.000    0.000 sre_parse.py:232(__next)
        4    0.000    0.000    0.000    0.000 sre_parse.py:248(match)
        4    0.000    0.000    0.000    0.000 sre_parse.py:253(get)
        3    0.000    0.000    0.000    0.000 sre_parse.py:285(tell)
        2    0.000    0.000    0.000    0.000 sre_parse.py:342(_escape)
        1    0.000    0.000    0.000    0.000 sre_parse.py:407(_parse_sub)
        2    0.000    0.000    0.000    0.000 sre_parse.py:470(_parse)
        1    0.000    0.000    0.000    0.000 sre_parse.py:76(__init__)
        2    0.000    0.000    0.000    0.000 sre_parse.py:81(groups)
        1    0.000    0.000    0.000    0.000 sre_parse.py:828(fix_flags)
        1    0.000    0.000    0.000    0.000 sre_parse.py:844(parse)
        1    0.005    0.005    0.005    0.005 {built-in method _codecs.charmap_decode}
        1    0.000    0.000    0.000    0.000 {built-in method _locale._getdefaultlocale}
        1    0.000    0.000    0.000    0.000 {built-in method _sre.compile}
     3204    0.003    0.000    0.003    0.000 {built-in method builtins.dir}
        1    0.000    0.000    0.318    0.318 {built-in method builtins.exec}
       27    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
        1    0.000    0.000    0.000    0.000 {built-in method builtins.iter}
    42/39    0.000    0.000    0.000    0.000 {built-in method builtins.len}
        2    0.000    0.000    0.000    0.000 {built-in method builtins.max}
       13    0.000    0.000    0.000    0.000 {built-in method builtins.min}
   108086    0.014    0.000    0.014    0.000 {built-in method builtins.next}
        1    0.000    0.000    0.000    0.000 {built-in method io.open}
     3247    0.001    0.000    0.001    0.000 {method 'append' of 'list' objects}
        1    0.000    0.000    0.000    0.000 {method 'close' of '_io.TextIOWrapper' objects}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        2    0.000    0.000    0.000    0.000 {method 'find' of 'bytearray' objects}
        2    0.000    0.000    0.000    0.000 {method 'get' of 'dict' objects}
        1    0.000    0.000    0.000    0.000 {method 'items' of 'dict' objects}
    45040    0.005    0.000    0.005    0.000 {method 'lstrip' of 'str' objects}
        1    0.002    0.002    0.007    0.007 {method 'read' of '_io.TextIOWrapper' objects}
     9507    0.003    0.000    0.003    0.000 {method 'replace' of 'str' objects}
    25793    0.137    0.000    0.137    0.000 {method 'split' of '_sre.SRE_Pattern' objects}
     3274    0.009    0.000    0.009    0.000 {method 'split' of 'str' objects}
"""
"""cProfile.run("CACM_documents = extract_documents_CS276()")
         1088992 function calls in 775.998 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000  775.998  775.998 <string>:1(<module>)
    98998    0.411    0.000    1.263    0.000 _bootlocale.py:11(getpreferredencoding)
    98998    0.169    0.000    0.169    0.000 codecs.py:259(__init__)
    98998    0.278    0.000    1.383    0.000 cp1252.py:22(decode)
    98998    1.024    0.000    1.024    0.000 I_Importation_Donnees.py:14(__init__)
        1    2.316    2.316  775.998  775.998 I_Importation_Donnees.py:39(extract_documents_CS276)
    98998    1.105    0.000    1.105    0.000 {built-in method _codecs.charmap_decode}
    98998    0.852    0.000    0.852    0.000 {built-in method _locale._getdefaultlocale}
        1    0.000    0.000  775.998  775.998 {built-in method builtins.exec}
    98998  753.194    0.008  754.626    0.008 {built-in method io.open}
       10    0.309    0.031    0.309    0.031 {built-in method nt.listdir}
    98998    0.127    0.000    0.127    0.000 {method 'add' of 'set' objects}
    98998    3.630    0.000    3.630    0.000 {method 'close' of '_io.TextIOWrapper' objects}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
    98998    8.097    0.000    9.480    0.000 {method 'read' of '_io.TextIOWrapper' objects}
    98998    4.486    0.000    4.486    0.000 {method 'split' of 'str' objects}"""
