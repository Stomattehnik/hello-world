import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from betting_data import MatchOdds, build_training_rows, parse_betting_text


RAW_FEED = """
ВТАWTA Finals
Сьогодні, 16:30

Соболенко, Арина

Паоліні, Жасмін
Переможець
1
1.29
2
3.4

АТПATP Афіни, Греція
Сьогодні, 20:00

Попирін, Олексій

Корда, Себастьян
Переможець
1
2.45
2
1.55

Лайв
ІТФ ЖінкиITF Irapuato, Mexico Women
2-ий сет

Калієва, Ельвіна

Мандлік, Елізабет
4
1
0
0
1
0
Переможець
1
1.02
2
9.0
"""


def test_parse_betting_text_extracts_matches():
    matches = parse_betting_text(RAW_FEED)
    assert len(matches) == 3

    first = matches[0]
    assert first.tournament == "ВТАWTA Finals"
    assert first.schedule == "Сьогодні, 16:30"
    assert first.player_one == "Соболенко, Арина"
    assert first.player_two == "Паоліні, Жасмін"
    assert math.isclose(first.odds_one, 1.29)
    assert math.isclose(first.odds_two, 3.4)

    live_match = matches[-1]
    assert live_match.tournament == "ІТФ ЖінкиITF Irapuato, Mexico Women"
    # Live sections can have status strings instead of precise times.
    assert live_match.schedule == "2-ий сет"
    assert live_match.player_one == "Калієва, Ельвіна"
    assert live_match.player_two == "Мандлік, Елізабет"


def test_parse_betting_text_deduplicates_repeated_blocks():
    duplicated_feed = RAW_FEED + "\n" + RAW_FEED
    matches = parse_betting_text(duplicated_feed)
    assert len(matches) == 3


def test_build_training_rows_creates_ml_ready_payload():
    matches = parse_betting_text(RAW_FEED)
    rows = build_training_rows(matches)
    assert len(rows) == len(matches)

    row = rows[0]
    assert row["favourite_is_player_one"] == 1
    assert math.isclose(row["implied_prob_one"] + row["implied_prob_two"], 1.0)
    assert row["odds_margin"] > 0
    assert "tournament" in row and row["tournament"] == matches[0].tournament


def test_match_odds_margin_matches_manual_calculation():
    match = MatchOdds(
        tournament="Test",
        schedule="Сьогодні, 10:00",
        player_one="Player One",
        player_two="Player Two",
        odds_one=1.5,
        odds_two=2.5,
    )
    expected_margin = (1.0 / 1.5 + 1.0 / 2.5) - 1.0
    assert math.isclose(match.bookmaker_margin(), expected_margin)

