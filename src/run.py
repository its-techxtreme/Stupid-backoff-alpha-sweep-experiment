# Score alpha on the development slice, then score the frozen test slice.
# The test slice is never used to pick alpha.

import csv
from pathlib import Path

from model import apply_vocab, counts, perplexity, vocabulary
from make_fig1 import main as make_figure

ROOT = Path(__file__).resolve().parent.parent
ALPHAS = [0.1, 0.2, 0.4, 0.6, 0.8]
SIZES = [2000, 10000, 50000]
DEV_AT = 50000
DEV_N = 2000
TEST_N = 2000


def load(name):
    path = ROOT / "data" / (name + ".tokens")
    return path.read_text(encoding="utf-8").split()


def pairs_from(tokens, start, n):
    # the history of the first scored token is the token just before the slice
    out = []
    for i in range(start, start + n):
        out.append((tokens[i - 1], tokens[i]))
    return out


def one_book(name):
    toks = load(name)
    need = DEV_AT + DEV_N + TEST_N
    if len(toks) < need:
        raise SystemExit("%s has %d tokens, need %d" % (name, len(toks), need))
    rows = []
    for size in SIZES:
        train_raw = toks[:size]
        vocab = vocabulary(train_raw)
        # map the whole book with this training vocabulary, then slice
        mapped = apply_vocab(toks, vocab)
        train = mapped[:size]
        uni, followers, hist = counts(train)
        dev_pairs = pairs_from(mapped, DEV_AT, DEV_N)
        test_pairs = pairs_from(mapped, DEV_AT + DEV_N, TEST_N)
        unk_dev = sum(1 for h, w in dev_pairs if w == "UNK") / len(dev_pairs)
        unk_test = sum(1 for h, w in test_pairs if w == "UNK") / len(test_pairs)
        for alpha in ALPHAS:
            dev_pp, dev_seen = perplexity(dev_pairs, uni, followers, hist, len(train), alpha)
            test_pp, test_seen = perplexity(test_pairs, uni, followers, hist, len(train), alpha)
            rows.append({
                "book": name,
                "train_tokens": size,
                "alpha": alpha,
                "vocab": len(vocab),
                "dev_pp": round(dev_pp, 4),
                "test_pp": round(test_pp, 4),
                "dev_unk": round(unk_dev, 4),
                "test_unk": round(unk_test, 4),
                "dev_seen_hist": round(dev_seen, 4),
                "test_seen_hist": round(test_seen, 4),
            })
            print("%s train %5d alpha %.1f  dev %.2f  test %.2f  vocab %d" % (
                name, size, alpha, dev_pp, test_pp, len(vocab)))
    return rows


def chosen(rows):
    # lowest development perplexity at each book and training size.
    # 0.4 is kept even when it loses.
    out = []
    keys = {(r["book"], r["train_tokens"]) for r in rows}
    for book, size in sorted(keys):
        group = [r for r in rows if r["book"] == book and r["train_tokens"] == size]
        winner = min(group, key=lambda r: (r["dev_pp"], r["alpha"]))
        fixed = [r for r in group if r["alpha"] == 0.4][0]
        out.append({
            "book": book,
            "train_tokens": size,
            "chosen_alpha": winner["alpha"],
            "chosen_dev_pp": winner["dev_pp"],
            "chosen_test_pp": winner["test_pp"],
            "alpha_0_4_dev_pp": fixed["dev_pp"],
            "alpha_0_4_test_pp": fixed["test_pp"],
            "test_unk": fixed["test_unk"],
            "test_seen_hist": fixed["test_seen_hist"],
            "vocab": fixed["vocab"],
        })
    return out


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    rows = []
    for name in ("pride", "emma"):
        rows.extend(one_book(name))
    write_csv(ROOT / "results" / "sweep.csv", rows)
    picks = chosen(rows)
    write_csv(ROOT / "results" / "chosen.csv", picks)
    for r in picks:
        print("chosen", r["book"], r["train_tokens"], "alpha", r["chosen_alpha"],
              "test", r["chosen_test_pp"], "0.4 test", r["alpha_0_4_test_pp"])
    make_figure()


if __name__ == "__main__":
    main()
