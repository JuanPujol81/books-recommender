from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Recommendation:
    book: object
    score: int
    reasons: list[str]


def tokenize(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9]+", value.lower())
        if len(token) > 2
    }


def score_book(book: object, query: str) -> Recommendation:
    query_tokens = tokenize(query)

    if not query_tokens:
        return Recommendation(book=book, score=0, reasons=[])

    title = getattr(book, "title", "")
    author = getattr(book, "author", "")
    genre = getattr(book, "genre", "")
    description = getattr(book, "description", "")
    reasons: list[str] = []
    score = 0

    title_matches = query_tokens & tokenize(title)
    author_matches = query_tokens & tokenize(author)
    genre_matches = query_tokens & tokenize(genre)
    description_matches = query_tokens & tokenize(description)

    if title_matches:
        score += len(title_matches) * 5
        reasons.append("title match")

    if author_matches:
        score += len(author_matches) * 4
        reasons.append("author match")

    if genre_matches:
        score += len(genre_matches) * 3
        reasons.append("genre match")

    if description_matches:
        score += len(description_matches)
        reasons.append("description match")

    return Recommendation(book=book, score=score, reasons=reasons)


def recommend_books(
    books: Iterable[object], query: str, limit: int = 5
) -> list[Recommendation]:
    recommendations = [
        recommendation
        for recommendation in (score_book(book, query) for book in books)
        if recommendation.score > 0
    ]

    return sorted(
        recommendations,
        key=lambda recommendation: (
            -recommendation.score,
            getattr(recommendation.book, "title", "").lower(),
        ),
    )[:limit]
