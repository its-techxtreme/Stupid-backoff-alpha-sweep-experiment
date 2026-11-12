# Lab notes

## 18–24 August 2026

We started by looking for papers on how a language model handles a word pair it has never seen. The one we kept coming back to was Brants, Popat, Xu, Och, and Dean (2007). They score a seen pair by its relative frequency, with no discount. An unseen pair gets a constant, alpha, times the score of the shorter history. They set alpha to 0.4. A footnote says that value came from earlier experiments. They do not derive it, and they do not say it is the best constant at every training size.

Their learning curve starts at about 13 million tokens and goes up to web scale. They could not report perplexity for Stupid Backoff, because the score is not a probability. They used 5-gram coverage instead, and even at 13 million tokens most test 5-grams were unseen. On the news text, Stupid Backoff with alpha 0.4 sat a little behind Kneser-Ney, and at the large end that gap was small.

We wrote down two things we did not want to lose. First, 0.4 is a fixed choice, not a law. Second, their plot never shows what happens when the training text is only a few thousand words.

## 25–28 August 2026

Chen and Goodman (1996) was the next paper. They compare smoothing methods and the winner changes when the training set gets smaller, and it changes again when the model goes from bigram to trigram. A gap of about 0.014 bits is about a 1 percent change in perplexity, which gave us a scale for later. They also say a parameter picked at the wrong training size can wipe out the gain, so if we sweep alpha we have to pick it on development data at that same size.

Brants points to their 1998 technical report for the backoff scheme itself. We read that part as the general picture, then went back to the 2007 formula, which is simpler. A seen bigram keeps its relative frequency. An unseen one is alpha times the unigram. There is no fall-through to a uniform 1 over the vocabulary. A word with count 0 would score 0, which is why rare words have to be mapped to one UNK token.

## 29–31 August 2026

Chelba et al. (2014) is where perplexity becomes legal for this score. For the numbers in their Table 1 they divide each context's scores by the sum of S over the whole vocabulary. After that division, alpha is still in the formula. A seen next word keeps its raw pair ratio. An unseen next word is alpha times its unigram. If the history word itself was never seen, every next word backs off, alpha is a common factor, and it cancels. So alpha can only move the perplexity on test words whose previous word was seen.

Their table is a 5-gram on about 0.8 billion words. The 0.4 in that row is training time in hours, not the backoff constant. They do not say which alpha they used. We are not going to invent one. Their smallest suggested subset is still about 10 million words, so a result on our books does not transfer to that benchmark.

By the end of August we had the question. Is 0.4 still the best Stupid Backoff constant, by held-out perplexity, when the training text is 2,000, 10,000, or 50,000 tokens? We will sweep 0.1, 0.2, 0.4, 0.6, and 0.8, pick the value on a development slice, and score a frozen test slice. The 0.4 row stays in the table even if another value wins. We will stay with a bigram, so there is one backoff step. A 5-gram on a few thousand tokens would be almost pure backoff, which is what Brants's coverage number already suggested.

## 1–2 September 2026

We picked two novels, both long enough for a 50,000-token prefix plus two slices after it, and different enough that one book is not the whole story. Pride and Prejudice is Gutenberg 1342. Emma is Gutenberg 158. Emma is the replication, not a second question.

The split has to stay in order. We will not shuffle sentences, and we will not tune alpha on the test slice. Development and test should be smaller than the training prefix. That fails for the 2,000-token run if we put both slices after the 50,000-token mark, and we decided to live with that and say so. Using the same later chapters for every size means a small model is scored on text it has not seen. Chen and Goodman had development sets around 50,000 words and called that unrealistic for a small training set. Ours are 2,000 tokens, which is still large next to a 2,000-token training prefix.

## 3–8 September 2026

We started the counts at the first sentence of each novel. The Gutenberg license and the contents list are cut. Counting begins at "It is a truth universally acknowledged" and at "Emma Woodhouse, handsome, clever, and rich". Words are lowercased. An apostrophe inside a word stays, so "don't" is one token. Commas, periods, and quotation marks are their own tokens. A run of 50,000 tokens is not 50,000 dictionary words.

The three training sets are the first 2,000 tokens, the first 10,000, and the first 50,000. Development is the next 2,000 tokens after that first 50,000, and test is the 2,000 after development. From the first token of the novel, those are tokens 50,001–52,000 and 52,001–54,000.

A word needs count at least 2 in that training prefix, or it becomes UNK. Brants used a cutoff of 2 on the smaller sets. We rebuild the vocabulary on each prefix. Brants et al. warn that perplexities are not comparable across vocabularies, because a fixed cutoff grows the vocabulary as the data grows and that alone raises perplexity. We will have to remember that when the 50,000-token perplexity comes out higher.

The token files were in place by 8 September.

## 9–16 September 2026

We did not score the novels until a six-word sentence matched a hand calculation.

The sentence is a b a b a b, and alpha is 0.4. The only word that follows a is b. P(b|a) = 0.8333 and P(a|a) = 0.1667. They add to 1. The raw ratio for b is 1, because b followed a every time. a never followed a, so its raw score is 0.4 times 3/6 = 0.2. The normalizer is 1.2.

If the history itself was never seen, alpha sits on every next word and cancels. P(b|z) came out 0.5, which is just the unigram.

Then we tried a real history. On the first 2,000 tokens of Pride and Prejudice, "truth" occurs twice. Once the next token is "is". Once it is UNK. Each has raw score 0.5. An exclamation mark never follows "truth" there. Its raw score is 0.0014, and after we divide by z = 1.3394 its probability is about 0.00105.

`check_row.py` has to print `toy row ok` before the sweep is worth reading. That check was holding by 16 September, and the bigram scorer was the same code we were about to run on the books.

## 17–22 September 2026

We ran the grid on both books. Alpha is chosen on the development slice at that training size. The test slice is scored after the choice and does not change it. Each book is one contiguous prefix, so we do not have ten random splits and we are not going to pretend a single split is a significance test.

The full grid is in results/sweep.csv. The choice is in results/chosen.csv. The figure is results/fig1_perplexity.png, where the dashed line is 0.4. The runs finished on 18 September. We spent the next few days checking that the 0.4 row was still in every cell and that the UNK rate sat next to the perplexity.

| Book | Training tokens | Chosen on dev | Chosen test pp | 0.4 test pp | Test UNK rate | Vocab |
| --- | --- | --- | --- | --- | --- | --- |
| Pride and Prejudice | 2,000 | 0.6 | 34.19 | 34.60 | 0.307 | 212 |
| Pride and Prejudice | 10,000 | 0.6 | 73.59 | 75.31 | 0.153 | 732 |
| Pride and Prejudice | 50,000 | 0.6 | 109.80 | 110.47 | 0.055 | 2182 |
| Emma | 2,000 | 0.8 | 34.16 | 34.83 | 0.321 | 233 |
| Emma | 10,000 | 0.6 | 72.18 | 73.79 | 0.181 | 749 |
| Emma | 50,000 | 0.4 | 126.02 | 126.02 | 0.080 | 2029 |

0.1 is the worst alpha in every row. The curve bottoms near 0.6. The gap above 0.4 is small.

0.4 wins the development slice in one cell: Emma at 50,000 tokens. There its development perplexity is 99.48 and 0.6 is 99.69. On the test slice of that same cell, 0.6 is a bit lower, 124.12 against 126.02. We still keep 0.4. The rule was to pick on development.

On Emma at 2,000 tokens the development slice picks 0.8. The test slice likes 0.6 by a hair, 34.09 against 34.16. Same rule. The choice stays 0.8.

On Pride and Prejudice at 2,000 tokens the test perplexities are 34.60 for 0.4 and 34.19 for 0.6, about 1 percent. That is the Chen and Goodman scale. Several of our gaps sit around it. 0.4 does not fall apart.

Every test history was seen, in all six runs. Some of those histories are rare words mapped to UNK. UNK occurs in training, so the history count is positive and alpha does not cancel on these slices. It would cancel only for a history token that, even after the UNK mapping, had never been followed by anything. We recorded that fraction as 1.0 so a flat curve would have an explanation. The curves are not flat.

Perplexity goes up as the prefix gets longer because the vocabulary goes from about 200 types to about 2,000. That is the warning from Brants et al. The 50,000-token model is not "worse" just because its perplexity is higher.

The test slice of Emma at 50,000 tokens is harder than its development slice, about 126 against about 99 at the chosen alpha. Pride and Prejudice moves less, about 110 against about 102. The next 2,000 tokens are a different stretch of the book. We do not have a better account of that yet.

## 23 September 2026

We wrote these notes from the csv. The claim we are willing to make is narrow. For these two novels and this bigram setup, 0.4 is not the development winner at 2,000 or 10,000 tokens. At 50,000 tokens it wins on Emma and loses on Pride and Prejudice. Brants et al. used 5-grams from 13 million tokens up, and they scored BLEU. Our numbers do not speak to that setting, and they do not say anything about Kneser-Ney.
