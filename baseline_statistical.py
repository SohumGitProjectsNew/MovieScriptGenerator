# SYSTEM IMPORTS
from collections.abc import Sequence
from typing import Tuple
from pprint import pprint
import argparse as ap
import numpy as np
import os
import sys
import json  # Add this import for JSON parsing
import spacy
import re


nlp = spacy.load("en_core_web_sm")

# make sure the directory that contains this file is in sys.path
_cd_: str = os.path.abspath(os.path.dirname(__file__))
if _cd_ not in sys.path:
    sys.path.append(_cd_)
del _cd_


# PYTHON PROJECT IMPORTS
from models.ngram.unigram import Unigram
from vocab import START_TOKEN, END_TOKEN

def split_script_into_sentences(script):
    script = script.replace("\r", "").replace("\n", " ").replace("\t", "")
    
    script = re.sub(r"<b>.*?</b>", "", script)

    sentences = re.split(r"(?<=[.!?])\s+", script)
    
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def load_scripts_from_json(file_path: str) -> Sequence[Sequence[str]]:
    
    with open(file_path, "r", encoding="utf-8") as file:
        jsons = json.load(file)

        scripts = [entry["script"] for entry in jsons]

        sentences = [split_script_into_sentences(script) for script in scripts]

        sentences = [sentence for sublist in sentences for sentence in sublist]

        # include punctatoin as own words (currently results in only predicting . even after smoothing and cut off.
        # sentences_as_words = [re.findall(r"\w+|[^\w\s]", sentence) for sentence in sentences]

        sentences_as_words = [re.sub(r"[^\w\s]", "", sentence).split() for sentence in sentences]

        return(sentences_as_words)


def train_unigram(train) -> Unigram:
    print("training")
    # Load scripts from the JSON file
    #train_data: Sequence[Sequence[str]] = load_scripts_from_json("./data/baseline_train.txt")
    u = Unigram(1.0, train)

    #words = [u.vocab.denumberize(i) for i in range(len(u.vocab))]
    #prob_distribution = np.exp(u.logprob)

    """
    words = [u.vocab.denumberize(i) for i in range(100)]
    prob_distribution = np.exp(u.logprob[:100])

    
    for word, prob in zip(words, prob_distribution):
        print(f"{word}: {prob}")

    #assert(False)

    """
    return u


def dev_unigram(m: Unigram, test) -> Tuple[int, int]:
    print("comparing")
    # Load scripts from the JSON file
    #dev_data: Sequence[Sequence[str]] = load_scripts_from_json("./data/baseline_test.txt")

    dev_data = test
    
    num_correct: int = 0
    num_correct_type: int = 0
    total: int = 0
    count = 1
    for dev_line in dev_data:

        q = m.start()  # get the initial state of the model
        print("sentence: " + str(count) + "/" + str(len(dev_data)))

        for c_input, c_actual in zip([START_TOKEN] + dev_line,  # read in string w/ <BOS> prepended
                                     dev_line + [END_TOKEN]):  # check against string incl. <EOS>
            q, p = m.step(q, m.vocab.numberize(c_input))
            #c_predicted = m.vocab.denumberize(np.argmax(p))
            p = np.nan_to_num(p, nan=1e-8)
            p = p / p.sum()  

            if np.sum(p) == 0 or np.isnan(np.sum(p)):
                p = np.ones(len(p)) / len(p) 
            else:
                p /= np.sum(p)
                     
            c_predicted = m.vocab.denumberize(np.random.choice(len(p), p=p))
            

            predicted_pos = nlp(c_predicted)[0].pos_
            actual_pos = nlp(c_actual)[0].pos_

            num_correct += int(c_predicted == c_actual)
            num_correct_type += int(predicted_pos == actual_pos)

            """
            print(c_predicted)
            print(predicted_pos)
            print(c_actual)
            print(actual_pos)
            print("-----------")
            """

            total += 1

        print("done sentence")
        count = count + 1

    return num_correct, num_correct_type, total


def main() -> None:
    input = load_scripts_from_json("data/first_three_genre.txt")
    train = input[:int(len(input) * 0.8)]
    test = input[:int(len(input) * 0.2)]

    #print(input[-1])
    #print(len(train))
    #print(len(test))

    m: Unigram = train_unigram(train)
    print(len(m.vocab))
    num_correct, num_correct_pos, total = dev_unigram(m,test)
    print("word accuracy: " + str(num_correct / total))
    print("pos accuracy: " + str(num_correct_pos / total))



if __name__ == "__main__":
    main()