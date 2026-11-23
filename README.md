# Stupid Backoff at small sizes

Does alpha 0.4 still give the lowest held-out perplexity for a bigram Stupid Backoff model when the training text is only a few thousand tokens?

The books are *Pride and Prejudice* and *Emma* from Project Gutenberg. Punctuation is its own token. A word seen once in a training prefix becomes UNK. Alpha is chosen on tokens 50,001 to 52,000 and scored on the frozen test slice, tokens 52,001 to 54,000. Training prefixes hold the first 2,000, 10,000, or 50,000 tokens.

## Layout

```text
paper/     manuscript PDF, named after the paper
src/       experiment scripts and the figure script
data/      raw books, tokenized books, and source URLs
results/   frozen sweep, development choices, and figures
journal.md lab notes written from the sweep
```

## Reproduce

From the project root, with Python 3:

```text
python src/prepare.py
python src/check_row.py
python src/run.py
python src/make_fig1.py
```

`prepare.py` downloads the Gutenberg texts only if `data/raw/` is empty, then writes the token files. `check_row.py` must print `toy row ok` before the sweep is worth reading. `run.py` writes `results/sweep.csv`, `results/chosen.csv`, and `results/fig1_perplexity.png` (it needs matplotlib for the figure). `make_fig1.py` can regenerate the figure on its own from the CSVs.

The numbers behind the paper are frozen in `results/sweep.csv` and `results/chosen.csv`. `results/fig1_perplexity.png` plots test perplexity for each book and training size in its own panel, with the published alpha marked by a dashed line and the development choice marked by an open circle. `journal.md` records the observations made while running the sweep. The manuscript itself is in `paper/Is-0.4-Still-the-Best-Backoff-Constant.pdf`.
