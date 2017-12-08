import os
import re


script_dir = os.getcwd()
# donne la localisation actuelle de ton dossier projet
cacm_relative_location = "/Data/CACM/cacm.all"
cs276_relative_location= ["/Data/CS276/"+str(i) for i in range(10)]
common_words_relative_location = "/Data/CACM/common_words"


class Document:
    def __init__(self, id):
        self.id = id  # .I
        self.title = None  # .T
        self.summary = None  # .W
        self.keywords = []  # .K
        self.word_lists= list()

def open_folder(folders_root):
    for folder in folders_root:
        for file_location in os.listdir(os.getcwd()+folder):
            pass


def read_to_list(file_location):
    """
    Open, read a file in file_location and return the list of lines of the document
    :return: list
    """
    file = open(file_location, "r")
    res = file.read().split("\n")  # on crée une liste des lignes du document, split découpe une chaine de caractère
    file.close()
    return res


def extract_documents(input_data):
    """
    Read inputs and create documents
    :param input_data: list of lines of input
    :return: list of documents
    """

    collections = []
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
                    collections.append(doc)
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
                    doc.word_lists+=re.split("\W+|\d+",line.lstrip())
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
        collections.append(doc)

    return collections

if __name__ =="__main__":
    documents = extract_documents(read_to_list(script_dir + cacm_relative_location))
    print(documents[2000].__dict__)