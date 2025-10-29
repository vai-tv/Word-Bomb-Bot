# How to Use *Word Bomb Bot*

## `auto.py`

1. Run the script and full-screen Word Bomb once dots start appearing in the console.
    * The dots appear every time the script checks whose turn it is.
2. Once it is your turn, the bot will read the screen and send keystrokes to submit a word that fits within the combination.

You may also provide the `-d` parameter to see debug messages.

## `manual.py`

1. In the command line, specify `-c` and `-n` parameters.
    * `-c` is the combination that Word Bomb requests.
    * `-n` is the number of words you wish to receive back.
2. Once the script has run, a series of words, sorted by complexity, will appear in the format: `WORD      [LENGTH] [COMPLEXITY]`.
    * Complexity is arbritrarily scored based on the frequency of the letters in the word. 
        * For example, *Bezzazzes* has a high complexity as it features a lot of uncommon letters, especially *z*.
        * On the contrary, *Huggable* has a lower complexity as it features more common letters, such as *a*, *e*, and *l*.
    * The words that appear will always be as complex as possible, i.e. the last `n` words are selected from a wordlist sorted by complexity in ascending order.
3. Once the words appear, you may select a word and manually input it into Word Bomb.