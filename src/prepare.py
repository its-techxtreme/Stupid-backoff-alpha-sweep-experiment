# Turn the two novels into a list of tokens.
# A token is a word, or one punctuation mark on its own.

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data"

# The Gutenberg file keeps the license, then a contents list and the
# illustrations. Counting should start at the first sentence of the novel.
BOOKS = {
    "pride": (
        "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
        "It is a truth universally acknowledged",
    ),
    "emma": (
        "https://www.gutenberg.org/cache/epub/158/pg158.txt",
        "Emma Woodhouse, handsome, clever, and rich",
    ),
}

# a word may keep an apostrophe (don't). a number stays whole.
# anything else that isn't a space becomes its own token.
TOKEN = re.compile(r"[a-z]+(?:'[a-z]+)?|[0-9]+|[^a-z0-9\s]", re.I)


def novel_body(text, first_line):
    start = text.find("*** START OF")
    end = text.find("*** END OF")
    if start < 0 or end < 0:
        raise SystemExit("could not find the gutenberg start and end marks")
    body = text[start:end]
    at = body.find(first_line)
    if at < 0:
        raise SystemExit("could not find the first sentence: " + first_line)
    return body[at:]


def tokenize(text, first_line):
    body = novel_body(text, first_line).replace("_", "")
    return [t.lower() for t in TOKEN.findall(body)]


def fetch(name):
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / (name + ".txt")
    if not path.exists():
        print("downloading", name)
        urllib.request.urlretrieve(BOOKS[name][0], path)
    text = path.read_text(encoding="utf-8-sig")
    toks = tokenize(text, BOOKS[name][1])
    (OUT / (name + ".tokens")).write_text("\n".join(toks) + "\n", encoding="utf-8")
    print(name, len(toks), "tokens. first ones:", " ".join(toks[:12]))
    return toks


if __name__ == "__main__":
    for name in BOOKS:
        fetch(name)
