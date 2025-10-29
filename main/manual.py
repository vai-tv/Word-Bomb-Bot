"""
please note that this is old code and is probably a bit yucky :/
"""

# default modules
import argparse
import os

from typing import Iterable


####################################################################################################

# Argument Parser
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find words that match a given combination of letters.')
    parser.add_argument('-c', '--combination', type=str, help='The combination of letters to match.', required=True)
    parser.add_argument('-n', '--number', type=int, default=10, help='The number of valid words to return.')
    args = parser.parse_args()

LENGTH_RANGE = range(8, 25)

ALPHABET_BY_FREQ = "etaonihsrlducmwyfgpbvkjxqz"

mc = "\033[1;31m"
w = "\033[0m"


###################################################################################################


def complexity(word: str) -> float:
    """Get the complexity of a word."""
    try:
        return sum(ALPHABET_BY_FREQ.index(char.lower()) ** 2 for char in word) / len(word)
    except ValueError:
        return float('inf')

def process_words():
    """Process words."""

    with open(os.path.dirname(__file__) + '/words.txt', "r") as f:
        words = [line.strip() for line in f]
    filtered_words = [word.lower() for word in words if word.isalpha() and len(word) in LENGTH_RANGE]
    return sorted(filtered_words, key=complexity, reverse=True)


WORDS = process_words()


###################################################################################################


def n_valid_words(n: int, comb: str) -> Iterable[str]:
    """Return n valid words that match the given combination.

    Args:
        n (int): The number of valid words to return.
        comb (str): The combination of letters to match.

    Returns:
        Iterable[str]: An iterable of valid words that match the given combination.
    """

    found = 0

    for word in WORDS:
        if not all(char.isalpha() for char in word):
            continue
        if found >= n:
            return
        if comb in word.lower() and len(word) in LENGTH_RANGE:
            found += 1
            yield word


def format_words(words: list[str]) -> str:
    """Format words for printing.

    Args:
        words (list[str]): The words to format.

    Returns:
        str: The formatted words.
    """

    s = ''
    for i, word in enumerate(sorted(words, key=lambda word: complexity(word))):
        if i % 3 == 0:
            s += '\n'

        s += f"{mc}{word.title()}{w}".ljust(30 + LENGTH_RANGE[-1], ' ') 
        s += f"[{len(word)}]".ljust(5, ' ')
        s += f"[{complexity(word):.1f}]".ljust(15, ' ')

    return s


###################################################################################################


def main() -> None:
    """The main program."""

    

    comb = args.combination

    words = list(n_valid_words(args.number, comb))
    print(f"Found {mc}{len(words)}{w} valid words that match {mc}{comb}{w}.\n")
    print(f"WORD\t\t[LENGTH] [COMPLEXITY]")
    print(format_words(words),'\n\n')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\nGoodbye!")