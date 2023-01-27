#!/usr/bin/env python3

import argparse
from collections import Counter
import featurizers as feats
import os
import utils
from pathlib import Path

# ~~~ Helper functions ~~~




# ~~~ STATIC VOCABULARIES ~~~
# Static: non-changing sets of elements to count
POS_TAGS   = {"ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X", "SPACE"}
PUNC_MARKS = {".", ",", ":", ";", "\'", "\"", "?", "!", "`", "*", "&", "_", "-", "%", "(", ")", "–", "‘", "’"}
LETTERS    = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "à", "è", "ì", "ò", "ù", "á", "é", "í", "ó", "ú", "ý"}
EMOJIS     = {"😅", "😂", "😊", "❤️", "😭", "👍", "👌", "😍", "💕", "🥰"}
DEP_LABELS = {'ROOT', 'acl', 'acomp', 'advcl', 'advmod', 'agent', 'amod', 'appos', 'attr', 'aux', 'auxpass', 'case', 'cc', 'ccomp', 'compound', 'conj', 'csubj', 'csubjpass', 'dative', 'dep', 'det', 'dobj', 'expl', 'intj', 'mark', 'meta', 'neg', 'nmod', 'npadvmod', 'nsubj', 'nsubjpass', 'nummod', 'oprd', 'parataxis', 'pcomp', 'pobj', 'poss', 'preconj', 'predet', 'prep', 'prt', 'punct', 'quantmod', 'relcl', 'xcomp'}

# ~~~ NON-STATIC VOCABULARIES ~~~
# Non-static: sets of elements that change depending on the dataset

def generate_most_common_POS_bigrams_vocab(documents:list[str]) -> set:
    pass
    


def generate_most_common_mixed_bigrams_vocab(documents:list[str]) -> set:
    pass


def write_vocab_to_pickle():
    pass


def write_vocab_to_txt_file():
    pass


def get_dataset_name(train_path:str) -> str:
    pass

def generate_dataset_directory(dataset_name:str) -> None:
    pass

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
    
    
    

def main():
    
    parser = argparse.ArgumentParser()
    
    # NOTE: the train path will need to be altered when this code is integrated into Delip's system
    parser.add_argument("-train",
                        "--train_path",
                        type=str,
                        help="Path to train data",
                        default="data/pan/train_dev_test/train.json")# set this to whatever you want
    
    
    
if __name__ == "__main__":
    main()