
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
import demoji
from nltk import bigrams
import numpy as np 
import os
import spacy
import toml

# project imports 
import utils


# ~~~ Logging and type aliases~~~

Counts = list[int]
SentenceSpan = tuple[int,int]
Vocab = tuple[str]

def feature_logger(filename, writable):
    
    if not os.path.exists("logs"):
        os.mkdir("logs")
               
    with open(f"logs/{filename}.log", "a") as fout: 
        fout.write(writable)
    
# ~~~ Static vocabularies ~~~
pos_unigram_vocab:Vocab    = utils.load_vocab("vocab/static/pos_unigrams.txt")
function_words_vocab:Vocab = utils.load_vocab("vocab/static/function_words.txt")
dep_labels_vocab:Vocab     = utils.load_vocab("vocab/static/dep_labels.txt")
punc_marks_vocab:Vocab     = utils.load_vocab("vocab/static/punc_marks.txt")
letters_vocab:Vocab        = utils.load_vocab("vocab/static/letters.txt")
common_emojis_vocab:Vocab  = utils.load_vocab("vocab/static/common_emojis.txt")

# ~~~ Non-static vocabularies ~~~
#NOTE: the path needs to change be manually changed to matched appropriate dataset
pos_bigrams_vocab:Vocab = utils.load_pkl("vocab/non_static/pos_bigrams/pan/pos_bigrams.pkl")
mixed_bigrams_vocab:Vocab = utils.load_pkl("vocab/non_static/mixed_bigrams/pan/mixed_bigrams.pkl")

@dataclass
class Document:
    """
    Class representing elements from a spaCy Doc object
        :param raw_text: text before being processed by spaCy
        :param doc: spaCy's document object
        :param tokens = list of tokens
        :param pos_tags: list of pos tags
        :param dep_labels: list of dependency parse labels
        :param sentences: list of spaCy-sentencized sentences
    Note: instances should only be created using the 'make_document' function 
"""
    raw_text   :str
    doc        :spacy.tokens.doc.Doc
    tokens     :list[str]
    pos_tags   :list[str]
    dep_labels :list[str]
    sentences  :list[spacy.tokens.span.Span]
    
    def __repr__(self):
        return f"Document({self.tokens[0:10]}..)"
    
def make_document(text:str, nlp) -> Document:
    """Converts raw text into a Document object"""
    raw_text   = deepcopy(text)
    doc        = nlp(demojify_text(text)) # dep parser hates emojis
    tokens     = [token.text for token in doc]
    pos_tags   = [token.pos_ for token in doc]
    dep_labels = [token.dep_ for token in doc]
    sentences  = list(doc.sents)
    return Document(raw_text, doc, tokens, pos_tags, dep_labels, sentences)

class CountBasedFeaturizer:
    
    def __init__(self, name:str, vocab:tuple, counter):
        self.name = name
        self.vocab = vocab
        self.counter = counter
        
    def __repr__(self):
        return self.name
        
    def _add_zero_vocab_counts(self, counted_doc_features:Counter) -> dict:
        """
        Combines vocab and counted_document_features into one dictionary such that
        any feature in vocab counted 0 times in counted_document_features is preserved in the feature vector. 
        
        :param document_counts: features counted from document
        :returns: counts of every element in vocab with 0 counts preserved
        :rtype: dict
        
        Example:
                >> self.vocab = ("a", "b", "c", "d")
                
                >> counted_doc_features = Counter({"a":5, "c":2})
                
                >> self._get_all_feature_counts(vocab, counted_doc_features)
                
                    '{"a": 5, "b" : 0, "c" : 2, "d" : 0}'
        """
        count_dict = {}
        for feature in self.vocab:
            if feature in counted_doc_features:
                count = counted_doc_features[feature] 
            else:
                count = 0
            count_dict[feature] = count
        return count_dict
        
    def get_all_feature_counts(self, document:Document) -> dict:
        """
        Applies counter function to get document counts and 
        combines the result with 0 count vocab entries
        
        :param document: document to extract counts from
        :returns: dictionary of counts
        """
        counted_doc_features = self.counter(document)
        return self._add_zero_vocab_counts(counted_doc_features)

    def vectorize(self, document:Document) -> np.array:
        """"""
        counts = self.get_all_feature_counts(document).values()
        return np.array(counts)
    
# ~~~ Helper functions ~~~

def demojify_text(text:str):
    return demoji.replace(text, "") # dep parser hates emojis 

def get_sentence_spans(doc:Document) -> list[SentenceSpan]:
    return [(sent.start, sent.end) for sent in doc.sentences]
   
def insert_pos_sentence_boundaries(doc:Document) -> list[str]:
    """Inserts sentence boundaries into a list of POS tags"""
    spans = get_sentence_spans(doc)
    new_tokens = []
    
    for i, item in enumerate(doc.pos_tags):
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
    OPEN_CLASS = ["ADJ", "ADV", "NOUN", "VERB", "INTJ"]
    tokens = deepcopy(tokens)
    for i in range(len(tokens)):
        if pos[i] in OPEN_CLASS:
            tokens[i] = pos[i]
    return tokens

   
# ~~~ Counter functions ~~~
# These functions are used to count certain text elements from documents

def count_pos_unigrams(doc:Document) -> Counter:
    return Counter(doc.pos_tags)

def count_pos_bigrams(doc:Document) -> Counter:
    pos_tags_with_boundaries = insert_pos_sentence_boundaries(doc)
    counter = Counter(bigrams(pos_tags_with_boundaries))
    try:
        del counter[("EOS","BOS")] # removes artificial bigram
    except: pass
    
    return counter

def count_func_words(doc:Document) -> Counter:
    return Counter([token for token in doc.tokens if token in function_words_vocab])

def count_punctuation(doc:Document) -> Counter:
    return Counter([punc for token in doc.tokens for punc in token.text if punc in punc_marks_vocab])

def count_letters(doc:Document) -> Counter:
    return Counter([letter for token in doc.tokens for letter in token.text if letter in letters_vocab])

def count_emojis(doc:Document) -> Counter:
    extract_emojis = demoji.findall_list(doc.text, desc=False)
    return Counter(filter(lambda x: x in common_emojis_vocab, extract_emojis))

def count_dep_labels(doc:Document) -> Counter:
    return Counter([dep for dep in doc.dep_labels])

def count_mixed_bigrams(doc:Document) -> Counter:
    return Counter(bigrams(replace_openclass(doc.tokens, doc.pos_tags)))

# ~~~ Featurizers ~~~

pos_unigrams = CountBasedFeaturizer(
    name="pos_unigrams",
    vocab=pos_unigram_vocab,
    counter=count_pos_unigrams
)

pos_bigrams = CountBasedFeaturizer(
    name="pos_bigrams",
    vocab=pos_bigrams_vocab,
    counter=count_pos_bigrams
)

func_words = CountBasedFeaturizer(
    name="func_words",
    vocab=function_words_vocab,
    counter=count_func_words
)

punc = CountBasedFeaturizer(
    name="punc",
    vocab=punc_marks_vocab,
    counter=count_punctuation
)

letters = CountBasedFeaturizer(
    name="letters",
    vocab=letters_vocab,
    counter=count_letters
)

common_emojis = CountBasedFeaturizer(
    name="common_emojis",
    vocab=common_emojis_vocab,
    counter=count_emojis
)

dep_labels = CountBasedFeaturizer(
    name="dep_labels",
    vocab=dep_labels_vocab,
    counter=count_dep_labels
)

mixed_bigrams = CountBasedFeaturizer(
    name = "mixed_bigrams",
    vocab = mixed_bigrams_vocab,
    counter=count_mixed_bigrams
    )

# ~~~ Featurizers end ~~~

class FeatureVector:
    """
    Each feature vector object should have access to :
        - all individual feature vectors, as well as the concatenated one

    """
    def __init__(self,):
        pass 
    
    def __add__(self, other):
        pass
    
    


def config(path_to_config:str):
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