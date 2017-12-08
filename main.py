from import_data import *
from partie_1 import *
from partie_2 import *

if __name__ == "__main__":
    documents = extract_documents(read_to_list(script_dir + cacm_relative_location))
    question_5(documents)
    # print(documents[1664].__dict__)
    # print(construction_index(documents))
    # print(tri_termID(construction_index(documents)))
    # print(tri_docID(construction_index(documents)))
