# One made-up sentence, checked against a hand calculation, then one real row.
# The made-up one has to match before the novels are scored.

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from model import apply_vocab, context_mass, counts, probability, vocabulary

# a b a b a b
# unigrams a=3 b=3, N=6
# pairs: (a,b) three times, (b,a) two times
toy = ["a", "b", "a", "b", "a", "b"]
vocab = vocabulary(toy, min_count=2)
mapped = apply_vocab(toy, vocab)
uni, followers, hist = counts(mapped)
n = len(mapped)
alpha = 0.4

# after a, the only next word ever seen is b, so b keeps ratio 1
# a itself never followed a, so it is backed off: 0.4 * (3/6) = 0.2
z, seen = context_mass("a", uni, followers, hist, n, alpha)
assert abs(z - 1.2) < 1e-9, z
assert abs(seen["b"] - 1.0) < 1e-9
pb = probability("b", "a", uni, followers, hist, n, alpha)
pa = probability("a", "a", uni, followers, hist, n, alpha)
assert abs(pb - (1.0 / 1.2)) < 1e-9, pb
assert abs(pa - (0.2 / 1.2)) < 1e-9, pa
assert abs(pb + pa - 1.0) < 1e-9
print("toy row ok")
print("  history a, alpha 0.4")
print("  P(b|a) = %.4f   P(a|a) = %.4f   sum = %.4f" % (pb, pa, pb + pa))

# a history the toy never saw. alpha should cancel and leave the unigram.
pu = probability("b", "z", uni, followers, hist, n, alpha)
assert abs(pu - 0.5) < 1e-9, pu
print("  unseen history z: P(b|z) = %.4f (unigram, alpha dropped out)" % pu)


def first_real_row(path):
    toks = open(path, encoding="utf-8").read().split()
    train = toks[:2000]
    vocab = vocabulary(train)
    mapped = apply_vocab(train, vocab)
    uni, followers, hist = counts(mapped)
    # a short history with a few different next words, so the split is visible
    best = None
    for h, c in hist.items():
        kinds = len(followers[h])
        if 2 <= kinds <= 4 and (best is None or c < best[0]):
            best = (c, h, kinds)
    h = best[1]
    print()
    print("real row from", path, "first 2000 tokens")
    print("  history %r appeared before a next word %d times" % (h, hist[h]))
    z, seen = context_mass(h, uni, followers, hist, len(mapped), 0.4)
    print("  seen next words:")
    for w, raw in sorted(seen.items(), key=lambda kv: -kv[1]):
        print("    %-12s raw %.4f   P %.4f" % (w, raw, raw / z))
    missed = None
    for w in sorted(vocab):
        if w not in seen and uni[w] > 0:
            missed = w
            break
    raw = 0.4 * (uni[missed] / len(mapped))
    print("  unseen next %r  raw %.6f   P %.6f" % (missed, raw, raw / z))
    print("  normalizer z = %.4f" % z)


if __name__ == "__main__":
    first_real_row(str(ROOT / "data" / "pride.tokens"))
