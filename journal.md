# Lab notes

12 November 2026

The only question is whether alpha = 0.4 is still the best Stupid Backoff constant, by held-out perplexity, when the training text is 2,000, 10,000, or 50,000 tokens. The model is a bigram. Alpha is chosen on a development slice. The test slice is scored after that and is not used to change the choice.

## What I did not reuse

I already had an n-gram program that adds a constant to every count and then mixes the unigram, the bigram, and the trigram with weights. That is interpolation, not Stupid Backoff, and it throws punctuation away. A character-level transformer does not have an alpha of this kind at all. Neither one can answer the question, so the counts in this folder were written from scratch.

## The text

Pride and Prejudice is Gutenberg 1342. Emma is Gutenberg 158. The license and the contents list are cut. Counting starts at "It is a truth universally acknowledged" and at "Emma Woodhouse, handsome, clever, and rich". Words are lowercased. An apostrophe inside a word stays, so "don't" is one token. Commas, periods, and quotation marks are their own tokens. A run of 50,000 tokens is not 50,000 dictionary words.

The first 2,000, the first 10,000, and the first 50,000 tokens are the three training sets. Development is tokens 50,000 through 51,999. Test is tokens 52,000 through 53,999. The same two slices are used for every training size, so a small model is scored on later chapters it has not seen.

A word needs count at least 2 in that training prefix or it becomes UNK. The vocabulary is rebuilt for each prefix. Perplexities at different training sizes use different vocabularies, so a bigger perplexity at 50,000 tokens is not evidence that the model got worse.

## The formula, checked

On the toy sentence a b a b a b, with alpha 0.4, the only word that follows a is b.

P(b|a) = 0.8333 and P(a|a) = 0.1667. They add to 1. The raw ratio for b is 1, because b followed a every time. a never followed a, so its raw score is 0.4 times 3/6 = 0.2. The normalizer is 1.2.

If the history itself was never seen, alpha is on every next word and cancels. P(b|z) came out 0.5, which is just the unigram.

On the first 2,000 tokens of Pride and Prejudice, the history "truth" occurs twice. Once the next token is "is". Once it is UNK. Each has raw score 0.5. An exclamation mark never follows "truth" there. Its raw score is 0.0014, and after dividing by z = 1.3394 its probability is about 0.00105.

## The numbers

Alpha grid: 0.1, 0.2, 0.4, 0.6, 0.8. The full grid is in results/sweep.csv. The choice, which is the lowest development perplexity, is in results/chosen.csv. The plot is results/test_perplexity.svg. The dashed line on the plot is 0.4.

| Book | Training tokens | Chosen on dev | Chosen test pp | 0.4 test pp | Test UNK rate | Vocab |
| --- | --- | --- | --- | --- | --- | --- |
| Pride and Prejudice | 2,000 | 0.6 | 34.19 | 34.60 | 0.307 | 212 |
| Pride and Prejudice | 10,000 | 0.6 | 73.59 | 75.31 | 0.153 | 732 |
| Pride and Prejudice | 50,000 | 0.6 | 109.80 | 110.47 | 0.055 | 2182 |
| Emma | 2,000 | 0.8 | 34.16 | 34.83 | 0.321 | 233 |
| Emma | 10,000 | 0.6 | 72.18 | 73.79 | 0.181 | 749 |
| Emma | 50,000 | 0.4 | 126.02 | 126.02 | 0.080 | 2029 |

0.1 is the worst alpha in every row. The curve bottoms near 0.6, not at 0.1 and not by a huge gap above 0.4.

0.4 wins the development slice in only one cell: Emma at 50,000 tokens, where its development perplexity is 99.48 and 0.6 is 99.69. On the test slice of that same cell, 0.6 is actually a bit lower (124.12 against 126.02). I am not switching the choice. The rule was to pick on development.

On Emma at 2,000 tokens the development slice picks 0.8. The test slice likes 0.6 by a hair, 34.09 against 34.16. Same rule. The choice stays 0.8.

The gaps between 0.4 and the chosen alpha are small. On Pride and Prejudice at 2,000 tokens the test perplexities are 34.60 and 34.19, about 1 percent. Chen and Goodman treat a change of about 0.014 bits, roughly 1 percent of perplexity, as the scale where a difference starts to matter. Several of these gaps are around that size. They are not a collapse of 0.4.

## What would be easy to misread

Every test history was "seen", in all six runs. That does not mean the model knew the previous word as a real word. Rare previous words were mapped to UNK, and UNK does occur in training, so the history count is positive. Alpha does not cancel on these slices. It would cancel only for a history token that, even after the UNK mapping, had never been followed by anything.

The perplexity goes up as the training prefix gets longer because the vocabulary goes up with it, from about 200 types to about 2,000. Brants et al. warn that perplexities are not comparable across vocabularies. I will not write that the 50,000-token model is worse.

The test slice of Emma at 50,000 tokens is harder than its development slice (about 126 against about 99, at the chosen alpha). Pride and Prejudice moves less (about 110 against about 102). I do not have an explanation yet beyond "the next 2,000 tokens are a different stretch of the book."

## What I will not claim

This does not beat Kneser-Ney. It does not say 0.4 was a mistake at web scale. Brants et al. used 5-grams from 13 million tokens up, and they scored BLEU. The only claim these tables support is that, for these two novels and this bigram setup, 0.4 is not the development winner at the two smaller sizes, and at 50,000 tokens it wins once and loses once.
