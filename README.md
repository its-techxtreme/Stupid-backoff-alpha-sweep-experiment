# Stupid Backoff at small sizes

Does alpha 0.4 still give the lowest held-out perplexity for a bigram Stupid Backoff model when the training text is only a few thousand tokens?

The books are Pride and Prejudice and Emma. Punctuation is its own token. A word seen once in a training prefix becomes UNK. Alpha is chosen on tokens 50000 to 51999 and scored on tokens 52000 to 53999.

```text
python prepare.py
python check_row.py
python run.py
```

`check_row.py` has to print `toy row ok` before the sweep is worth reading. The numbers it is checking are written out in `journal.md`. The sweep itself is `results/sweep.csv`, and the alpha picked on the development slice is `results/chosen.csv`.
