import unittest
import os

from nltk.stem.snowball import SnowballStemmer

from I_Importation_Donnees import *
from III_bis_Classes import InvertedIndex, DocumentDict
from III_Index_Inverse import *
from IV_Recherches import *

stemmer = SnowballStemmer("english")

NB_DOCS_CS276 = 98998
NB_DOCS_CACM = 3204


class ReadDocuments(unittest.TestCase):
    def test_CACM_number_documents(self):
        docs = extract_documents_CACM()
        self.assertEqual(len(docs), 3204)

    def test_CACM_number_queries(self):
        queries = extract_queries_CACM()
        self.assertEqual(len(queries), 64)

    def test_read_a_document(self):
        doc = extract_documents_CS276(
            files_location=[os.getcwd() + "/Data/CS276/5/simula.stanford.edu_sedcl_people.html"]).pop()
        self.assertEqual(doc.title, "simula.stanford.edu_sedcl_people.html")
        self.assertEqual(doc.word_lists, ['stanford',
                                          'experimental',
                                          'data',
                                          'center',
                                          'laboratory',
                                          'faculty',
                                          'director',
                                          'mendel',
                                          'rosenblum',
                                          'administrator',
                                          'denise',
                                          'murphy',
                                          'home',
                                          'about',
                                          'people',
                                          'research',
                                          'affiliates',
                                          'contact',
                                          'students',
                                          'networking',
                                          'berk',
                                          'atikoglu',
                                          'mohammadreza',
                                          'alizadeh',
                                          'attar',
                                          'vimalkumar',
                                          'jeyakumar',
                                          'jianying',
                                          'luo',
                                          'shuang',
                                          'yang',
                                          'tom',
                                          'yue',
                                          'ramcloud',
                                          'asaf',
                                          'cidon',
                                          'mario',
                                          'flajslik',
                                          'ankita',
                                          'kejriwal',
                                          'ali',
                                          'mashtizadeh',
                                          'alex',
                                          'mordkovich',
                                          'diego',
                                          'ongaro',
                                          'steve',
                                          'rumble',
                                          'ryan',
                                          'stutsman',
                                          'data',
                                          'center',
                                          'architectures',
                                          'jacob',
                                          'leverich',
                                          'christina',
                                          'delimitrou',
                                          'krishna',
                                          'teja',
                                          'malladi',
                                          'david',
                                          'lo',
                                          'adam',
                                          'belay',
                                          'faculty',
                                          'mendel',
                                          'rosenblum',
                                          'john',
                                          'ousterhout',
                                          'balaji',
                                          'prabhakar',
                                          'bill',
                                          'dally',
                                          'christos',
                                          'kozyrakis',
                                          'administrator',
                                          'denise',
                                          'murphy',
                                          'copyright',
                                          '2010',
                                          'stanford',
                                          'experimental',
                                          'data',
                                          'center',
                                          'laboratory'])

    def test_read_a_query(self):
        queries = extract_queries_CACM()
        query_5 = [qr for qr in queries if qr.id == 5][0]
        self.assertEqual(query_5.linked_docs, [756, 1307, 1502, 2035, 2299, 2399, 2501, 2820])


class InvertedIndex(unittest.TestCase):
    def test_CACM(self):
        """Test index construction with one block"""
        docs = extract_documents_CACM()
        rvrsd_index, _ = construction_index_one_block(docs)
        self.assertEqual(rvrsd_index[stemmer.stem('system')]['tf'][92], 2)

    def test_CS276(self):
        """Test BSBI result"""
        reversed_index, dic_doc = read_CS276_index()
        self.assertEqual(len(dic_doc), NB_DOCS_CS276)
        self.assertEqual(reversed_index['stanford']['idf'], len(reversed_index['stanford']['tf']))


class Queries(unittest.TestCase):
    def test_boolean_search_CS276(self):
        reversed_index, dic_doc = read_CS276_index()
        self.assertEqual(len(reversed_index['stanford']['tf']),
                         len(boolean_search('Stanford', reversed_index, dic_doc)))
        self.assertEqual(
            len(boolean_search('Stanford', reversed_index, dic_doc)) + len(
                boolean_search('not Stanford', reversed_index, dic_doc)),
            NB_DOCS_CS276)
        self.assertEqual(len(boolean_search('Student not Student', reversed_index, dic_doc)), 0)

    def test_boolean_search_CACM(self):
        reversed_index, dic_doc = read_CACM_index()
        self.assertEqual(len(reversed_index['system']['tf']),
                         len(boolean_search('System', reversed_index, dic_doc)))
        self.assertEqual(
            len(boolean_search('system', reversed_index, dic_doc)) + len(
                boolean_search('not System', reversed_index, dic_doc)),
            NB_DOCS_CACM)
        self.assertEqual(len(boolean_search('Programming not Programming', reversed_index, dic_doc)), 0)


if __name__ == '__main__':
    unittest.main()
