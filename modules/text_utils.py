import re
from collections import Counter
from pathlib import Path
from typing import List, Set, Tuple

try:
    import jieba
except ImportError:
    jieba = None


STOPWORDS_PATH = Path(__file__).resolve().parents[1] / "assets" / "stopwords.txt"


def clean_text(text: str) -> str:
    text = str(text or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def load_stopwords() -> Set[str]:
    if not STOPWORDS_PATH.exists():
        return set()
    return {
        line.strip()
        for line in STOPWORDS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def tokenize(text: str) -> List[str]:
    stopwords = load_stopwords()
    cleaned = clean_text(text)
    words = jieba.lcut(cleaned) if jieba else re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z]{2,}", cleaned)
    result = []
    for word in words:
        word = word.strip()
        if len(word) <= 1:
            continue
        if word in stopwords:
            continue
        if re.fullmatch(r"[\W_]+", word):
            continue
        result.append(word)
    return result


def top_keywords(texts: List[str], limit: int = 20) -> List[Tuple[str, int]]:
    counter = Counter()
    for text in texts:
        counter.update(tokenize(text))
    return counter.most_common(limit)
