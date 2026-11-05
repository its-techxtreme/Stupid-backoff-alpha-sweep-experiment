# Bigram Stupid Backoff.
# A seen next word keeps its raw pair ratio.
# An unseen next word gets alpha times its unigram.
# Those scores are then divided by their sum, so one context adds up to 1.

from collections import Counter, defaultdict
import math


def vocabulary(tokens, min_count=2):
    freq = Counter(tokens)
    keep = {w for w, c in freq.items() if c >= min_count}
    keep.add("UNK")
    return keep


def apply_vocab(tokens, vocab):
    return [t if t in vocab else "UNK" for t in tokens]


def counts(tokens):
    # tokens are already mapped through the vocabulary
    uni = Counter(tokens)
    followers = defaultdict(Counter)
    for h, w in zip(tokens, tokens[1:]):
        followers[h][w] += 1
    hist = {h: sum(bag.values()) for h, bag in followers.items()}
    return uni, followers, hist


def context_mass(history, uni, followers, hist, n_tokens, alpha):
    """z is the sum of the raw scores. seen maps a next word to its pair ratio."""
    hcount = hist.get(history, 0)
    if hcount == 0:
        # every next word is backed off, so alpha is a common factor
        return alpha, {}
    seen = {}
    seen_uni = 0.0
    for w, c in followers[history].items():
        seen[w] = c / hcount
        seen_uni += uni[w] / n_tokens
    # the seen ratios add to 1, and we never discount them.
    # the leftover unigram mass is what alpha scales.
    z = 1.0 + alpha * (1.0 - seen_uni)
    return z, seen


def probability(word, history, uni, followers, hist, n_tokens, alpha):
    z, seen = context_mass(history, uni, followers, hist, n_tokens, alpha)
    if word in seen:
        raw = seen[word]
    else:
        raw = alpha * (uni[word] / n_tokens)
    return raw / z


def perplexity(pairs, uni, followers, hist, n_tokens, alpha):
    # pairs are (history, word). the first token of a book has no history, so it is left out.
    if not pairs:
        return float("inf"), 0.0
    # one context is reused for every alpha, so remember the mass
    cache = {}
    log_sum = 0.0
    seen_hist = 0
    for h, w in pairs:
        if h not in cache:
            cache[h] = context_mass(h, uni, followers, hist, n_tokens, alpha)
        z, seen = cache[h]
        if hist.get(h, 0) > 0:
            seen_hist += 1
        if w in seen:
            raw = seen[w]
        else:
            raw = alpha * (uni[w] / n_tokens)
        p = raw / z
        if p <= 0.0:
            return float("inf"), seen_hist / len(pairs)
        log_sum += math.log2(p)
    pp = 2 ** (-log_sum / len(pairs))
    return pp, seen_hist / len(pairs)
