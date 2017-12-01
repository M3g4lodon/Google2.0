import os

script_dir = os.getcwd()
cacm_relative_location = "/Data/CACM/cacm.all"
common_words_relative_location = "/Data/CACM/common_words"
file_location = script_dir + cacm_relative_location


class Document:
    def __init__(self, id):
        self.id = id
        self.title = None
        self.summary = None
        self.keywords = []


def input_lines():
    """
    Open, read the inputs of CACM, a list of lines
    :return: list
    """
    file = open(file_location, "r")
    res = file.read().split("\n")  # on crée une liste des lignes du document
    file.close()
    return res


def extract_documents(input_data):
    """
    Read inputs and create documents
    :param input_data: list of lines of input
    :return: list of documents
    """
    collections = []
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
                line = next(iter_lines)
                # Suppression des espaces en début de ligne
                doc.title = line.lstrip()

            # Cas ligne résumé
            elif line == ".W":
                doc.summary = ""
                line = next(iter_lines)
                while "." != line[0]:
                    # Suppressioon des espaces en début de ligne
                    doc.summary += line.lstrip()
                    line = next(iter_lines)

            # Cas ligne mots clés
            elif line == ".K":
                doc.keywords = []
                line = next(iter_lines)
                while "." != line[0]:
                    doc.keywords += map(lambda x: x.replace(', ', ''), line.split(', '))
                    line = next(iter_lines)

            # Cas ligne quelconque
            else:
                line = next(iter_lines)
    except StopIteration:
        # On rajoute dernier document à la 'main'
        collections.append(doc)

    return collections

def question_1(collection):
    pass


if __name__ == "__main__":
    documents=extract_documents(input_lines())
