import math
import random
from collections import Counter, defaultdict, deque
from itertools import islice

import spacy


def sliding_window(iterable, n):
    """
    Collect data into overlapping fixed-length chunks or blocks.
    From the itertools cookbook
    """
    # sliding_window('ABCDEFG', 3) → ABC BCD CDE DEF EFG
    iterator = iter(iterable)
    window = deque(islice(iterator, n - 1), maxlen=n)
    for x in iterator:
        window.append(x)
        yield tuple(window)

def is_ripe(token):
    text = token.text # to make it all a string so no errors occur with string only functions
    if text[0] == "’": # no ’s or ’d or something
        return False
    return any(char.isalpha() for char in text)
    # checks if there are any real letters to remove garbage (still keeps o'er)

# creates match dictionary of center word and context words
cooccurrence = defaultdict(Counter)
freqs = Counter()
total_words = sum(freqs.values())
total_pairs = sum(sum(n.values()) for n in cooccurrence.values())

def pmi(w, c) -> float | None:
    w, c = w.lower(), c.lower()
    if cooccurrence[w][c] == 0:
        return None
    p_wc = cooccurrence[w][c] / total_pairs
    p_w = freqs[w] / total_words
    p_c = freqs[c] / total_words
    result = math.log2(p_wc / (p_w * math.pow(p_c, .75)))
    return None if result < 0 else float(result)

def get_close_words(word) -> list[tuple[str, float]]:
    closest_words = []
    for tok in cooccurrence[word]:
        closeness = pmi(word, tok)
        if closeness:
            closest_words.append((closeness, tok))
    closest_words.sort(reverse=True)
    return [(tok, closeness) for closeness, tok in closest_words[:10]]

def app():
    with open('data/pg100-clean.txt') as p:
        # replace em-dashes so spacy can tokenize properly
        shakespeare = p.read().replace("—", " — ")
    
    nlp = spacy.load("en_core_web_md")
    nlp.max_length = 10_000_000
    doc = nlp(shakespeare)
    shopping_list = {'VERB', 'NOUN', 'ADJ', 'ADV'} # POS(part of sentence) filter
    
    # gets good words using the filter
    goodies = [
        token.text.lower() for token in doc
            if token.pos_ in shopping_list and is_ripe(token)
    ]

    windows = list(sliding_window(goodies, 11)) # makes windows
    for words in windows:
        center = int(len(words)/2)
        # words = {token.text.lower() for token in window} # gets all words per window
        center_word = words[center]
        for index, context in enumerate(words):
            if index == center:
                continue
            cooccurrence[center_word][context] += 1

    global freqs, total_pairs, total_words
    freqs = Counter(goodies)  # gets total count of each wo)
    total_words = sum(freqs.values())
    total_pairs = sum(sum(n.values()) for n in cooccurrence.values())

    goodesties = [word for word in goodies if freqs[word] >= 5]
    word_lineup = random.sample(goodesties, k=10)

    while True:
        # Print the lineup
        # get the word selection
        # draw 10 similar words for next lineup
        # loop
        print()
        for (index, word) in enumerate(word_lineup):
            print(f"{index + 1}. {word}")

        print()
        choice = input("Choose a word by typing its number: ")
        if not choice.isdigit():
            print("Please enter a number")
            continue

        chosen_word = word_lineup[int(choice) - 1]

        # print(f"Chose: {chosen_word}")
        new_lineup = get_close_words(chosen_word)
        # print(f"New words: {new_lineup}")
        word_lineup = [word for (word, similarity) in new_lineup]



if __name__ == '__main__':
    app()
