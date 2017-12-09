from import_data import *
#from partie_1 import *
from partie_2 import *

if __name__ == "__main__":
    documents = extract_documents_CACM()
    print(construction_index(documents)[0])
    print(construction_index(documents)[1])
    # print(documents.pop().__dict__)
    # print(construction_index(documents))
    # print(tri_termID(construction_index(documents)))
    # print(tri_docID(construction_index(documents)))
