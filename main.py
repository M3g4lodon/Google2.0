import os

script_dir = os.getcwd()
relative_location="/Data/CACM/cacm.all"
file_location = script_dir+relative_location

class Document:

    def __init__(self,id):
        self.id=id

    def set_title(self,title):
        self.title=title

    def set_summary(self, summary):
        self.summary=summary

    def set_keywords(self,keywords):
        self.keywords=keywords


def input_lines():
    file=open(file_location,"r")
    input_lines=file.read().split("\n") # on crée une liste des lignes du document
    file.close()
    return input_lines

def extract_documents(input_lines):
    collections=[]
    iter_lines=iter(input_lines)
    line = next(iter_lines)
    try:

        while True:
            # Cas ligne identifiant
            if line[:2]==".I":
                # Cas particulier de la première itération
                if 'doc' in dir():
                    collections.append(doc)
                #Nouveau document à rajouter
                doc_id = int(line[2:])
                doc=Document(doc_id)
                line = next(iter_lines)

            # Cas ligne titre
            elif line==".T":
                line=next(iter_lines)
                # Suppression des espaces en début de ligne
                doc.title=line.lstrip()

            # Cas ligne résumé
            elif line == ".W":
                doc.summary=""
                line = next(iter_lines)
                while "."!= line[0]:
                    #Suppressioon des espaces en début de ligne
                    doc.summary+=line.lstrip()
                    line = next(iter_lines)

            # Cas ligne mots clés
            elif line == ".K":
                doc.keywords=[]
                line = next(iter_lines)
                while "."!= line[0]:
                    doc.keywords+=map(lambda x:x.replace(', ',''),line.split(', '))
                    line = next(iter_lines)

            # Cas ligne quelconque
            else:
                line = next(iter_lines)
    except StopIteration:
        #On rajoute dernier document à la 'main'
        collections.append(doc)

    return collections



if __name__=="__main__":
    print(extract_documents(input_lines())[3203].__dict__)
