Projet Recherche Information Web
============================================================================================================================

Par Solène Duchamp & Mathieu Seris
Prérequis :

•	Cloner le repository : https://github.com/M3g4lodon/Google2.0

•   Enregistrer la collection CS276 dans le dossier ./Data/CS276

# Détails des différents dossiers:

•	Le dossier Buffer contient pour les deux collections :
    - les dictionnaires de correspondance titre de document et id de document
    - les indexs inversés

•	Le dossier Data contient les données initiales fournies

•	Le dossier Results contient les réponses aux questions de la partie 2.3

•	Dans le dossier racine, les fichiers sont nommés explicitement

# Rapport du projet

## I Traitements linguistiques

Les modules nécessaires pour cette partie sont : *I_Importations_Données.py* pour ouvrir les données, et *II_Traitement_Linguistique.py*
qui contient à proprement parler les fonctions de traitements linguistiques 

Question 1 : Nombre de tokens dans les collections 
- CACM : 107 508 tokens 
- CS276 : 17 803 941 tokens 

Question 2 : Taille du vocabulaire dans les collections
- CACM : 9741 mots 
- CS276 : 297 746 mots 

Question 3 :  Nombre de tokens et taille du vocabulaire su rla moitié de la collection
- CACM : 53 356 tokens et 3 773 mots
- CS276 : 8 729 267 tokens et 184 722 mots 

Paramètres k et b de la loi de Heap :
- CACM : k = 47.93 et b = 0.4494
- CS276 : k = 4.713 et b = 0.6621

La différence de valeur entre les deux collections peut s'expliquer par le fait que la collection CS276 a été pré-stremmée, 
contrairement à la collection CACM.

Question 4 : Estimation de la taille du vocabulaire pour des collections à 1 000 000 tokens
- CACM : 23 812 mots
- CS276 : 44 430 mots

Question 5 : Graphe Rang / Fréquence et LogRang / LogFréquence
Vous trouverez ces 4 graphes (2 par collection) dans le dossier Results avec des noms explicites.

## II Indexation

### Création des indexs inversés

A partir des données importées par le module *I_Importation_Donnees.py*, le module 
*III_Index_Inverse.py* contient les fonctions pour créer un index inversé à partir de nos collections.

La première partie du module contient les fonctions nécessaires au BSBI : 
 - ```create_posting_list``` crée une "posting list" ou liste terme-document à partir d'une collection de documents
 - ```construction_index_one_block``` crée à partir d'une collection de documents un index inversé 
 - ```write_in_buffer``` écrit un sous-index inversé et un sous-dictionnaire de correspondance titre-id de document, dans le dossier ./Buffer/Buffer
 - ```read_in_buffer``` lit les fichiers écrits sur le disque par la fonction précédente
 - ```process_block``` est la fonction utilisée par les "workers" ("Pool" en "multiprocess") lors de la parallélisation des calculs
 - ```BSBI_Index_construction_CS276``` crée un index inversé et un dictionnaire de correspondance titre/id de document pour la collection CS276,
 en utilisant la technique du BSBI. Lors de la phase de fusion des résultats intermédiaires, on charge un sous index inversé à la fois
 que l'on fusionne avec notre grand index inversé recherché.
 
 La deuxième partie du module contient des fonctions pour la construction d'un index inversé, en s'inspirant
 du paradigme MapReduce :
 - ```Map_reduced_Index``` est la fonction principale qui génère l'index inversé à partir d'une collection de documents.
 Afin d'utiliser au mieux les fonctions map, reduce et filter de python , nous avons créé deux autres fonctions :
 - ```concat_dict``` fusionne deux dictionnaires (utilisé pour la création du dictionnaire de correspondance titre/id de document
 dans un reduce)
 - ```create_reversed_index``` crée avec la bonne forme un index inversé à partir d'une posting list dans un reduce

La dernière partie du module, intitulée "Tools" répertorie plusieurs outils qui nous ont été très utiles pour les développements
suivants du projet. 
- Les fonctions ```update_Xxx``` permettent de créer ou écraser une ancienne version de nos index inversés.
- Les fonctions ```read_Xxx``` permettent de lire les index inversés écrits sur le disque dans le dossier Buffer.

Ainsi, nous avons construit des index inversés pour les deux collections de documents. Les écrire sur le disque, nous a permis
de pouvoir les utiliser très rapidement, plutôt que de devoir attendre 5 minutes dans le cas de CS276.

NB : Nous avons créé une classe spéciale héritée de dictionnaires pour l'index inversé dans le module *III_bis_Classes.py*. Il s'agit de la classe InvertedIndex.
C'est un dictionnaire avec valeur par défaut, ordonné, avec la forme définie pour ce projet. Il nous est apparu utile de créer
cette classe pour la phase de recherche, où nous manipulons énormément l'index inversé.


### Recherches booléennes et vectorielles

A partir des données extraites depuis le module *I_Importation_Donnees.py*, avec les indexs inversés du module *III_Index_Inverse.py*,
nous manipulons ces indexs inversés pour réaliser des recherches dans le module *IV_Recherches.py*.

Nous effectuons une recherche booléenne avec la fonction ```boolean_search```. Cette fonction prend en argument, la requête en chaine de caractères
( de la forme "Stanford", ou "Computer not Stanford"). Nous utilisons des opérations ensemblistes avec la classe set de Python pour 
réaliser cette recherche booléenne.

La deuxième partie du module comporte les fonctions utilisées pour la recherche vectorielle.
La fonction principale ici est ```vectorial_search```. Elle a pour arguments l'index inversé d'une collection de documents, 
son dictionnaire de correspondance titre/id de documents, une requête sous la forme d'une chaine de caractères, deux fonctions de pondérations
pour la requête et pour la collection de documents, et la collection de documents.

La fin du module contient plusieurs fonctions de pondérations.

### Evaluations 

#### Performances

##### Temps de calcul pour l'indexation
Temps de calcul sur notre machine : 4.94s pour l'indexation de CACM
Pour afficher le temps de calcul sur votre machine : ```print(temps_calcul_indexation())```
(Temps exprimé en secondes)


##### Temps de réponse à une requête
 - Recherche booléenne
 Temps de calcul sur notre machine : 0.28 ms
 Pour afficher le temps de calcul sur votre machine : ```print(temps_calcul_boolean_query())```
 (Temps exprimé en secondes)
 
 - Recherche vectorielle
 Temps de calcul sur notre machine : 17 ms
Pour afficher le temps de calcul sur votre machine : ```print(temps_calcul_vector_query())```
(Temps exprimé en secondes)

##### Occupation de l'espace disque par les différents indexs.
Ces informations s'afficheront dans la console après l'évocation de la fonction ```occupation_espace_disque()``` :
```text
CACM
Memory : 192.9 KB
Disk : 902.9 KB
CS276
Memory : 11.6 MB
Disk : 123.7 MB
```
#### Pertinence
Pour les fonctions de pondérations définies dans le module ```IV_Recherches.py```, nous avons tracé plusieurs graphes précision/rappel,
E-measure, F-measure, R-precision et Mean Average Precision dans le dossier ./Results. 

Auteurs : Solène Duchamp | Mathieu Seris
