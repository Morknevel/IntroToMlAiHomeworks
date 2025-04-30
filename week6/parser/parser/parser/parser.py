import nltk
import sys
import re

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | NP VP Conj VP

NP -> N | Det N | Det AdjP N | NP PP | AdjP NP | Det AdjP AdjP N | Det AdjP AdjP AdjP N
AdjP -> Adj
PP -> P NP

VP -> V | V NP | V NP PP | V PP | Adv VP | VP Adv | VP PP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    else:
        s = input("Sentence: ")

    s = preprocess(s)

    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    sentence = sentence.lower()
    

    for char in '.,;:!?"()[]{}':
        sentence = sentence.replace(char, ' ')
    
    words = sentence.split()
    
    words = [word for word in words if re.search('[a-zA-Z]', word)]
    
    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunks = []
    
    def contains_np(subtree):
        if subtree.height() <= 2: 
            return False
        
        for child in subtree:
            if isinstance(child, nltk.Tree) and child.label() == "NP":
                return True
            
            if isinstance(child, nltk.Tree) and contains_np(child):
                return True
        
        return False
    
    def find_chunks(subtree):
        if subtree.label() == "NP" and not contains_np(subtree):
            chunks.append(subtree)
        
        for child in subtree:
            if isinstance(child, nltk.Tree):
                find_chunks(child)
    
    find_chunks(tree)
    return chunks


if __name__ == "__main__":
    main()