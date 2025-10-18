"""Unit tests for the tennis prediction CLI helpers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tennis_prediction as tp


def make_player(
    name: str,
    *,
    ranking: int = 1,
    serve: float = 0.65,
    ret: float = 0.42,
    surface: float = 0.75,
    form: float = 0.80,
) -> tp.PlayerStats:
    return tp.PlayerStats(
        name=name,
        ranking=ranking,
        serve_points_won=serve,
        return_points_won=ret,
        surface_win_pct=surface,
        recent_form=form,
    )


def test_quality_score_increases_with_better_stats() -> None:
    base = make_player("Base")
    improved = make_player("Improved", serve=0.70, ret=0.48)
    assert improved.quality_score() > base.quality_score()


def test_win_probability_balances_to_one() -> None:
    p1 = make_player("Player 1", ranking=5)
    p2 = make_player("Player 2", ranking=20)
    prob1, prob2 = tp.win_probability(p1, p2)
    assert pytest.approx(prob1 + prob2, rel=1e-9) == 1.0
    assert prob1 > prob2


def test_predict_from_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "matches.csv"
    csv_path.write_text(
        """player_one_name,player_one_ranking,player_one_serve,player_one_return,player_one_surface,player_one_form,player_two_name,player_two_ranking,player_two_serve,player_two_return,player_two_surface,player_two_form
Player A,8,0.63,0.41,0.70,0.82,Player B,14,0.59,0.38,0.68,0.74
""",
        encoding="utf8",
    )

    predictions = tp.predict_from_csv(csv_path)
    assert len(predictions) == 1
    prediction = predictions[0]
    assert prediction.player_one.name == "Player A"
    assert 0 <= prediction.probability_one <= 1


def test_manual_mode_validation() -> None:
    parser = tp.build_parser()
    namespace = parser.parse_args(
        [
            "--player_one-name",
            "Alice",
            "--player_one-ranking",
            "2",
            "--player_one-serve",
            "0.64",
            "--player_one-return",
            "0.45",
            "--player_one-surface",
            "0.78",
            "--player_one-form",
            "0.81",
            "--player_two-name",
            "Bob",
            "--player_two-ranking",
            "18",
            "--player_two-serve",
            "0.58",
            "--player_two-return",
            "0.38",
            "--player_two-surface",
            "0.69",
            "--player_two-form",
            "0.72",
        ]
    )

    # Should not raise SystemExit for valid inputs
    tp._validate_manual_mode(namespace)


def test_manual_mode_validation_failure() -> None:
    parser = tp.build_parser()
    namespace = argparse.Namespace(
        player_one_name="Alice",
        player_one_ranking=0,
        player_one_serve=0.65,
        player_one_return=0.45,
        player_one_surface=0.78,
        player_one_form=0.81,
        player_two_name="Bob",
        player_two_ranking=10,
        player_two_serve=0.55,
        player_two_return=0.36,
        player_two_surface=0.67,
        player_two_form=0.70,
        matches_file=None,
        output=None,
        show_scores=False,
    )

    with pytest.raises(SystemExit):
        tp._validate_manual_mode(namespace)
