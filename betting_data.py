"""Utilities for turning scraped bookmaker odds into ML-ready rows.

The raw text shared by the user in the prompt is essentially a copy/paste
from a betting feed in Ukrainian.  The feed is verbose: it mixes tournament
headers, schedule/status strings, scoreboards for live matches and finally the
actual decimal odds for every player.  In order to use those odds inside a
machine-learning workflow we first need a reliable parser that can distil the
signal (players, tournaments and prices) from the noise.

This module provides two building blocks:

``parse_betting_text``
    Normalises the feed into a list of :class:`MatchOdds`.  The parser relies on
    lightweight heuristics – no external dependencies – so it can operate
    inside the constrained execution environment used for the exercises.

``build_training_rows``
    Converts the matches into dictionaries with numeric features that can be fed
    into models such as :class:`hybrid_pipeline.HybridWinProbabilityPipeline`.
    Since the pasted feed does not contain historic results we cannot derive the
    true winner, therefore a *proxy* target is generated: the favourite is the
    player with the lower decimal odd.  This is often used as a warm start for
    calibration models where the bookmaker odds act as soft labels.

The implementation focuses on clarity.  The heuristics are deliberately
transparent and the transformation into features is documented so that the
resulting dataset can be inspected and, if necessary, refined later on.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

# Markers that appear in tournament headers.  They help the parser differentiate
# competition names from player strings.
_TOURNAMENT_MARKERS = (
    "ATP",
    "WTA",
    "ВТА",  # Cyrillic spelling present in the provided data
    "ITF",
    "Челленджер",
    "Challenger",
    "eTennis",
)

# The feed includes utility strings such as "Лайв" (Live) or "Найближчі"
# (Upcoming).  They provide context for a human reader but they do not carry
# structured information for the parser, therefore we can drop them.
_NOISE_TOKENS = {
    "Лайв",
    "Найближчі",
    "Перейти до всіх парі",
}

# Schedules and status strings usually contain these prefixes.  They are stored
# for readability (the parser simply keeps the last seen schedule/status).
_SCHEDULE_PREFIXES = (
    "Сьогодні",
    "Завтра",
    "Післязавтра",
    "Закінчено",
    "Розпочався",
    "1-ий сет",
    "2-ий сет",
    "3-ий сет",
)


@dataclass(slots=True)
class MatchOdds:
    """Structured representation of the odds for a single match."""

    tournament: str
    schedule: str | None
    player_one: str
    player_two: str
    odds_one: float
    odds_two: float

    def implied_probabilities(self) -> tuple[float, float]:
        """Return bookmaker-implied probabilities normalised to sum to one."""

        inverse_one = 1.0 / self.odds_one
        inverse_two = 1.0 / self.odds_two
        denominator = inverse_one + inverse_two
        return inverse_one / denominator, inverse_two / denominator

    def bookmaker_margin(self) -> float:
        """Return the overround implied by the decimal odds."""

        return (1.0 / self.odds_one + 1.0 / self.odds_two) - 1.0

    def favourite_is_player_one(self) -> int:
        """Proxy target used when historic outcomes are missing."""

        return 1 if self.odds_one <= self.odds_two else 0


def _normalise_lines(raw_text: str) -> List[str]:
    """Split ``raw_text`` into meaningful tokens and drop empty lines."""

    return [line.strip() for line in raw_text.splitlines() if line.strip()]


_DIGITS_ONLY = re.compile(r"^[0-9]+$")


def _looks_like_schedule(token: str) -> bool:
    if any(token.startswith(prefix) for prefix in _SCHEDULE_PREFIXES):
        return True
    # Schedules frequently contain a comma/colon separating date and time and
    # always include at least one digit (hour/minute or day number).
    if ("," in token or ":" in token) and any(ch.isdigit() for ch in token):
        return True
    return False


def _looks_like_player(token: str) -> bool:
    """Return ``True`` if ``token`` plausibly represents a player name."""

    if token in _NOISE_TOKENS or token == "Переможець":
        return False
    if any(marker in token for marker in _TOURNAMENT_MARKERS):
        return False
    lower = token.lower()
    if "сет" in lower:  # scoreboard/status string for live matches
        return False
    if _DIGITS_ONLY.fullmatch(lower.replace("/", "")):
        return False
    if all(not ch.isalpha() for ch in token):
        return False
    # Player strings typically contain either a comma ("Surname, Name"), a slash
    # for doubles, or at least a space separating two tokens.
    return "," in token or "/" in token or " " in token


def _extract_players(tokens: Sequence[str], start_index: int) -> tuple[str, str] | None:
    """Back-track from ``start_index`` and return the two latest player names."""

    players: List[str] = []
    cursor = start_index - 1
    while cursor >= 0 and len(players) < 2:
        candidate = tokens[cursor]
        if _looks_like_player(candidate):
            players.append(candidate)
        cursor -= 1
    if len(players) < 2:
        return None
    players.reverse()
    return players[0], players[1]


def parse_betting_text(raw_text: str) -> List[MatchOdds]:
    """Parse the provided betting feed into :class:`MatchOdds` instances."""

    tokens = _normalise_lines(raw_text)
    matches: List[MatchOdds] = []
    seen: set[tuple[str | None, str | None, str, str, float, float]] = set()
    current_event: str | None = None
    current_schedule: str | None = None

    idx = 0
    while idx < len(tokens):
        token = tokens[idx]
        if token in _NOISE_TOKENS:
            idx += 1
            continue

        if token == "Переможець":
            players = _extract_players(tokens, idx)
            if players is None or idx + 4 >= len(tokens):
                idx += 1
                continue
            label_one, odds_one_str, label_two, odds_two_str = (
                tokens[idx + 1],
                tokens[idx + 2],
                tokens[idx + 3],
                tokens[idx + 4],
            )
            if label_one != "1" or label_two != "2":
                idx += 1
                continue
            try:
                odds_one = float(odds_one_str)
                odds_two = float(odds_two_str)
            except ValueError:
                idx += 1
                continue
            if current_event is None:
                # If we never encountered a tournament header we skip the entry –
                # it would be impossible to contextualise it downstream.
                idx += 5
                continue
            key = (
                current_event,
                current_schedule,
                players[0],
                players[1],
                odds_one,
                odds_two,
            )
            if key not in seen:
                seen.add(key)
                matches.append(
                    MatchOdds(
                        tournament=current_event,
                        schedule=current_schedule,
                        player_one=players[0],
                        player_two=players[1],
                        odds_one=odds_one,
                        odds_two=odds_two,
                    )
                )
            idx += 5
            continue

        if any(marker in token for marker in _TOURNAMENT_MARKERS):
            current_event = token
            current_schedule = None
            idx += 1
            continue

        if _looks_like_schedule(token):
            current_schedule = token
            idx += 1
            continue

        idx += 1

    return matches


def build_training_rows(matches: Iterable[MatchOdds]) -> List[Dict[str, float | int | str | None]]:
    """Convert ``matches`` into feature rows ready for model training."""

    rows: List[Dict[str, float | int | str | None]] = []
    for match in matches:
        implied_one, implied_two = match.implied_probabilities()
        margin = match.bookmaker_margin()
        rows.append(
            {
                "tournament": match.tournament,
                "schedule": match.schedule,
                "player_one": match.player_one,
                "player_two": match.player_two,
                "odds_one": match.odds_one,
                "odds_two": match.odds_two,
                "implied_prob_one": implied_one,
                "implied_prob_two": implied_two,
                "odds_margin": margin,
                "log_odds_ratio": math.log(match.odds_two / match.odds_one),
                "favourite_is_player_one": match.favourite_is_player_one(),
            }
        )
    return rows


__all__ = ["MatchOdds", "parse_betting_text", "build_training_rows"]

