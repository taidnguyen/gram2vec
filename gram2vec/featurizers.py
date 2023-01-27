
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
import demoji
from nltk import bigrams
import numpy as np 
import os
import spacy
import toml
from typing import Iterable

# project imports 
import utils

# ~~~ Logging and global variables ~~~

def feature_logger(filename, writable):
    
    if not os.path.exists("logs"):
        os.mkdir("logs")
               
    with open(f"logs/{filename}.log", "a") as fout: 
        fout.write(writable)
      

OPEN_CLASS = ["ADJ", "ADV", "NOUN", "VERB", "INTJ"]

# ~~~ Type aliases ~~~

Counts = list[int]
SentenceSpan = tuple[int,int]

# ~~~ Document representation ~~~

@dataclass
class Document:
    """
    Class representing certain elements from a spaCy Doc object

        @param raw_text: text data before being processed by spaCy
        @param doc: spaCy's document object
        @param tokens = list of tokens
        @param pos_tags: list of pos tags
        @param dep_labels: list of dependency parse labels
        @param sentences: list of spaCy-sentencized sentences   
"""
    raw_text   :str
    doc        :spacy.tokens.doc.Doc
    tokens     :list[str]
    pos_tags   :list[str]
    dep_labels :list[str]
    sentences  :list[spacy.tokens.span.Span]
    
def make_document(text:str, nlp) -> Document:
    """Converts raw text into a Document object"""
    raw_text   = deepcopy(text)
    doc        = nlp(demojify_text(text)) # dep parser hates emojis
    tokens     = [token.text for token in doc]
    pos_tags   = [token.pos_ for token in doc]
    dep_labels = [token.dep_ for token in doc]
    sentences  = list(doc.sents)
    return Document(raw_text, doc, tokens, pos_tags, dep_labels, sentences)
    
# ~~~ Helper functions ~~~

def demojify_text(text:str):
    return demoji.replace(text, "") # dep parser hates emojis 

def get_counts(vocab:list, doc_features:list) -> Counts:
    """
    Counts the frequency of items in 'sample_space' that occur in 'features'.
    When 'feat_dict' and 'count_doc_features' are merged, the 0 counts in 'feat_dict' 
    get overwritten by the counts in 'doc_features'. When features are not found in 'doc_features', 
    the 0 count in 'feat_dict' is preserved, indicating that the feature is absent in the current document
    
    Params:
        feature_space(list) = list of features to count. Each feature is initially mapped to 0
        features(list) = list of features from a document to count. 
    Returns:
        list: list of feature counts
    
    """
    vocab_to_zero_dict = {feat:0 for feat in vocab}
    
    count_dict = {}
    for feature in vocab_to_zero_dict.keys():
        if feature in doc_features:
            count = doc_features[feature] # retrieve count from document feature count if it exists
        else:
            count = vocab_to_zero_dict[feature] # retrieve 0 count
        
        count_dict[feature] = count
        
    return count_dict
   
def get_sentence_spans(doc:Document) -> list[SentenceSpan]:
    return [(sent.start, sent.end) for sent in doc.sentences]
   
def insert_pos_sentence_boundaries(doc:Document) -> list[str]:
    """Inserts sentence boundaries into a list of POS tags extracted from a spacey document"""
    spans = get_sentence_spans(doc)
    new_tokens = []
    
    for i, item in enumerate(doc.tokens):
        for start, end in spans:
            if i == start:
                new_tokens.append("BOS")
            elif i == end:
                new_tokens.append("EOS")    
        new_tokens.append(item)
    new_tokens.append("EOS")  
        
    return new_tokens

def replace_openclass(tokens:list[str], pos:list[str]) -> list[str]:
    """Replaces all open class tokens with corresponding POS tags"""
    tokens = deepcopy(tokens)
    for i in range(len(tokens)):
        if pos[i] in OPEN_CLASS:
            tokens[i] = pos[i]
    return tokens

   
# ~~~ Counter functions ~~~

def count_document_pos_unigrams(doc:Document) -> Counter:
    return Counter(doc.pos_tags)

def count_document_pos_bigrams(doc:Document) -> Counter:
    pos_tags_with_boundaries = insert_pos_sentence_boundaries(doc)
    counter = Counter(bigrams(pos_tags_with_boundaries))
    try:
        del counter[("EOS","BOS")] # removes artificial bigram
    except: pass
    
    return counter

def count_document_func_words(doc:Document, vocab):
    return 

def count_document_punctuation(doc:Document):
    return 

def count_document_letters(doc:Document):
    return 

def count_document_emojis(doc:Document):
    return

def count_document_dep_labels(doc:Document):
    return 

def count_document_mixed_bigrams(doc:Document) -> Counter:
    mixed_bigrams = list(bigrams(replace_openclass(doc.tokens, doc.pos_tags)))
    return Counter(mixed_bigrams)
    


# ~~~ Featurizers ~~~

def pos_unigrams(document) -> np.ndarray: 
    
    
    tags = {"ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X", "SPACE"}
    
    doc_pos_tags = [token.pos_ for token in document]   
    
    counts, doc_features = get_counts(tags, doc_pos_tags)
    
    result = np.array(counts) #/ len(document.pos_tags)
    assert len(tags) == len(counts)
    
    return result, doc_features

def pos_bigrams(document) -> np.ndarray : # len = 50

    vocab = utils.load_vocab("vocab/pan_pos_bigrams_vocab.pkl") # path will need to change per dataset 
    
    doc_pos_bigrams = get_pos_bigrams(document)
    
    counts, doc_features = get_counts(vocab, doc_pos_bigrams)
    
    result = np.array(counts) #/ len(document.pos_tags)
    assert len(vocab) == len(counts)
    
    return result, doc_features


def func_words(document) -> np.ndarray:
    
    # modified NLTK stopwords set
    #! use pkl file for vocab
    with open ("vocab/function_words.txt", "r") as fin:
        function_words = set(map(lambda x: x.strip("\n"), fin.readlines()))

    tokens = [token.text for token in document] 
    doc_func_words = [token for token in tokens if token in function_words]
    
    counts, doc_features = get_counts(function_words, doc_func_words)
    result = np.array(counts) #/ len(document.tokens)
    assert len(function_words) == len(counts)
    
    return result, doc_features


def punc(document) -> np.ndarray:
    
    punc_marks = {".", ",", ":", ";", "\'", "\"", "?", "!", "`", "*", "&", "_", "-", "%", "(", ")", "–", "‘", "’"}
    
    doc_punc_marks = [punc for token in document 
                           for punc in token.text
                           if punc in punc_marks]
    
    counts, doc_features = get_counts(punc_marks, doc_punc_marks)
    
    result = np.array(counts) #/ len(document.tokens) 
    assert len(punc_marks) == len(counts)
    
    return result, doc_features


def letters(document) -> np.ndarray: 

    letters = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
               "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
               "à", "è", "ì", "ò", "ù", "á", "é", "í", "ó", "ú", "ý"}
    
    doc_letters = [letter for token in document
                          for letter in token.text 
                          if letter in letters]
    
    counts, doc_features = get_counts(letters, doc_letters)
    result = np.array(counts) #/ len(doc_letters)
    assert len(letters) == len(counts)
    
    return result, doc_features


def common_emojis(document):
    
    vocab = {"😅", "😂", "😊", "❤️", "😭", "👍", "👌", "😍", "💕", "🥰"}
    
    extract_emojis = demoji.findall_list(document.text, desc=False)
    emojis = list(filter(lambda x: x in vocab, extract_emojis))
    
    counts, doc_features = get_counts(vocab, emojis)
    result = np.array(counts) #/ len(document.tokens)
    
    return result, doc_features

def doc_vector(document):
    result = document.doc.vector
    return result, None
    
    
def dep_labels(document):
    
    labels = {'ROOT', 'acl', 'acomp', 'advcl', 'advmod', 'agent', 'amod', 'appos', 'attr', 'aux', 'auxpass', 'case', 'cc', 'ccomp', 'compound', 
              'conj', 'csubj', 'csubjpass', 'dative', 'dep', 'det', 'dobj', 'expl', 'intj', 'mark', 'meta', 'neg', 'nmod', 'npadvmod', 'nsubj', 
              'nsubjpass', 'nummod', 'oprd', 'parataxis', 'pcomp', 'pobj', 'poss', 'preconj', 'predet', 'prep', 'prt', 'punct', 'quantmod', 'relcl', 'xcomp'}
    
    document_dep_labels = [token.dep_ for token in document]
    
    counts, doc_features = get_counts(labels, document_dep_labels)
    
    result = np.array(counts) / len(document_dep_labels)
    assert len(counts) == len(labels)
    
    return result, doc_features


def mixed_bigrams(document):
    
    vocab = utils.load_pkl("vocab/pan_mixed_bigrams_vocab.pkl")
    
    doc_mixed_bigrams = get_mixed_bigrams(document)
    
    counts, doc_features = get_counts(vocab, doc_mixed_bigrams)
    result = np.array(counts) 
    assert len(vocab) == len(counts)
    
    return result, doc_features


# ~~~ Featurizers end ~~~
   


    


class CountBasedFeaturizer:
    
    def __init__(self, name:str, vocab:Iterable, counter):
        self.name = name
        self.vocab = vocab
        self.counter = counter
    
    def apply(self, document) -> np.ndarray:
    
        document_counts = self.counter(document)

        




mixed_bigrams = CountBasedFeaturizer(
     name = "mixed_bigrams",
     vocab = [("hi", "NOUN")],
     counter=count_document_mixed_bigrams
 )





class FeatureVector:
    """
    Each feature vector object should have access to :
        - all individual feature vectors, as well as the concatenated one
        - the raw text
        - author?
    """
    def __init__(self, text:str):
        pass 
    
   
   

    
class GrammarVectorizer:
    """This class houses all featurizers"""
    
    def __init__(self, data_path, logging=False):
        self.nlp = utils.load_spacy("en_core_web_md")
        self.logging = logging
        self.featurizers = {
            "pos_unigrams"  :pos_unigrams,
            "pos_bigrams"   :pos_bigrams,
            "func_words"    :func_words, 
            "punc"          :punc,
            "letters"       :letters,
            "common_emojis" :common_emojis,
            "doc_vector"    :doc_vector,
            "dep_labels"    :dep_labels,
            "mixed_bigrams" :mixed_bigrams}
        
        self._generate_vocab(data_path)
        
    def _config(self):
        """Reads 'config.toml' to retrieve which features to apply. 0 = deactivated, 1 = activated"""
        toml_config = toml.load("config.toml")["Features"]
        config = []
        for name, feat in self.featurizers.items():
            try:
                if toml_config[name] == 1:
                    config.append(feat)
            except KeyError:
                raise KeyError(f"Feature '{name}' does not exist in config.toml")
        return config
    

    def _generate_vocab(self, data_path):
        """
        Generates vocab files required by some featurizers. Assumes the following input data format:
                            {
                             author_id : [doc1, doc2,...docn],
                             author_id : [...]
                             }
        """
        data = utils.load_json(data_path)
        dataset = "pan" if "pan" in data_path else "mud" # will need to be changed based on data set
        counters = {
            "pos_bigrams"   : [],
            "mixed_bigrams" : []
        } 
        
        all_text_docs = [entry for id in data.keys() for entry in data[id]]
        for feature, counter_list in counters.items():
            out_path = f"vocab/{dataset}_{feature}_vocab.pkl"
            
            if not os.path.exists(out_path):
                for text in all_text_docs:
                    doc = self.nlp(text)
                    
                    pos_counts = get_pos_bigrams(doc)
                    counters["pos_bigrams"].append(pos_counts)
                
                    mixed_bigrams = get_mixed_bigrams(doc)
                    counters["mixed_bigrams"].append(mixed_bigrams)
        
                # this line condenses all the counters into one dict, getting the 50 most common elements
                most_common = dict(sum(counter_list, Counter()).most_common(50)) # most common returns list of tuples, gets converted back to dict
                utils.save_pkl(set(most_common.keys()), out_path)
        
        
    
    def vectorize(self, text:str) -> np.ndarray:
        """Applies featurizers to an input text. Returns a 1-D array."""
        
        doc = make_document(text, self.nlp)
        
        vectors = []
        for feat in self._config():
            
            vector, doc_features = feat(doc)
            assert not np.isnan(vector).any() 
            vectors.append(vector)
            
            if self.logging:
                feature_logger(f"{feat.__name__}", f"{doc_features}\n{vector}\n\n")
                    
        return np.concatenate(vectors)
    
    
# debugging
if __name__ == "__main__":
    pass