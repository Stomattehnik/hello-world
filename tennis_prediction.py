#!/usr/bin/env python3
"""Utilities for producing simple tennis match win probabilities.

The script can work in two modes:

* single match mode – accept statistics for two players via CLI flags;
* batch mode – read a CSV file with many matches and optionally write the
  predictions to another CSV file.

The goal is not to be an accurate betting engine, but to provide a transparent
calculation that blends a handful of intuitive statistics into a probability
forecast.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple


def _positive_float(value: str) -> float:
    """Return a positive float parsed from ``value``."""

    try:
        float_value = float(value)
    except ValueError as exc:  # pragma: no cover - defensive programming
        raise argparse.ArgumentTypeError(str(exc)) from exc

    if float_value < 0:
        raise argparse.ArgumentTypeError("value must be positive")

    return float_value


def _bounded_float(value: str) -> float:
    """Return a float in the ``[0, 1]`` range parsed from ``value``."""

    float_value = _positive_float(value)
    if float_value > 1:
        raise argparse.ArgumentTypeError("value must not exceed 1.0")

    return float_value


@dataclass(slots=True)
class PlayerStats:
    """Container for the statistics used by the prediction model."""

    name: str
    ranking: int
    serve_points_won: float
    return_points_won: float
    surface_win_pct: float
    recent_form: float

    def quality_score(self) -> float:
        """Collapse individual statistics into a single skill score.

        The values are scaled to fall within ``[0, 1]`` so a simple weighted
        blend can be used. The weights were chosen to emphasise the more
        predictive serve/return stats without discarding ranking, surface and
        recent form information entirely.
        """

        ranking_score = max(0.0, 300 - min(self.ranking, 300)) / 300
        serve_score = self.serve_points_won
        return_score = self.return_points_won
        surface_score = self.surface_win_pct
        form_score = self.recent_form

        return (
            0.30 * ranking_score
            + 0.30 * serve_score
            + 0.20 * return_score
            + 0.10 * surface_score
            + 0.10 * form_score
        )


@dataclass(slots=True)
class MatchPrediction:
    """Result of a single match probability forecast."""

    player_one: PlayerStats
    player_two: PlayerStats
    probability_one: float
    probability_two: float


def win_probability(player_one: PlayerStats, player_two: PlayerStats) -> Tuple[float, float]:
    """Return the win probability for ``player_one`` and ``player_two``."""

    score_one = player_one.quality_score()
    score_two = player_two.quality_score()

    # Logistic curve scaled to produce a sensible spread.  A higher ``scale``
    # makes the curve steeper (i.e. large score gaps translate to near-certain
    # results), while a lower value keeps matches closer to 50/50.
    scale = 6.5
    diff = (score_one - score_two) * scale
    player_one_prob = 1.0 / (1.0 + math.exp(-diff))
    player_two_prob = 1.0 - player_one_prob
    return player_one_prob, player_two_prob


def _build_player(namespace: argparse.Namespace, prefix: str) -> PlayerStats:
    return PlayerStats(
        name=getattr(namespace, f"{prefix}_name"),
        ranking=getattr(namespace, f"{prefix}_ranking"),
        serve_points_won=getattr(namespace, f"{prefix}_serve"),
        return_points_won=getattr(namespace, f"{prefix}_return"),
        surface_win_pct=getattr(namespace, f"{prefix}_surface"),
        recent_form=getattr(namespace, f"{prefix}_form"),
    )


def _parse_player_from_row(row: dict[str, str], prefix: str) -> PlayerStats:
    try:
        name = row[f"{prefix}_name"]
        ranking = int(row[f"{prefix}_ranking"])
        serve = float(row[f"{prefix}_serve"])
        ret = float(row[f"{prefix}_return"])
        surface = float(row[f"{prefix}_surface"])
        form = float(row[f"{prefix}_form"])
    except KeyError as exc:
        missing = exc.args[0]
        raise ValueError(f"missing '{missing}' column in CSV") from exc

    if ranking <= 0:
        raise ValueError("ranking must be positive")
    for stat_name, stat_value in (
        ("serve", serve),
        ("return", ret),
        ("surface", surface),
        ("form", form),
    ):
        if not 0 <= stat_value <= 1:
            raise ValueError(f"{prefix}_{stat_name} must be between 0 and 1")

    return PlayerStats(
        name=name,
        ranking=ranking,
        serve_points_won=serve,
        return_points_won=ret,
        surface_win_pct=surface,
        recent_form=form,
    )


def predict_match(player_one: PlayerStats, player_two: PlayerStats) -> MatchPrediction:
    probability_one, probability_two = win_probability(player_one, player_two)
    return MatchPrediction(player_one, player_two, probability_one, probability_two)


def predict_from_csv(path: Path) -> List[MatchPrediction]:
    """Load matches from ``path`` and return predictions for all rows."""

    with path.open(newline="", encoding="utf8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file must contain a header row")

        predictions: List[MatchPrediction] = []
        for idx, row in enumerate(reader, start=1):
            try:
                player_one = _parse_player_from_row(row, "player_one")
                player_two = _parse_player_from_row(row, "player_two")
            except ValueError as exc:
                raise ValueError(f"row {idx}: {exc}") from exc

            predictions.append(predict_match(player_one, player_two))

    return predictions


def _write_predictions_csv(predictions: Sequence[MatchPrediction], path: Path) -> None:
    with path.open("w", newline="", encoding="utf8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "player_one",
                "player_two",
                "player_one_probability",
                "player_two_probability",
            ]
        )
        for prediction in predictions:
            writer.writerow(
                [
                    prediction.player_one.name,
                    prediction.player_two.name,
                    f"{prediction.probability_one:.4f}",
                    f"{prediction.probability_two:.4f}",
                ]
            )


def _format_prediction(prediction: MatchPrediction, show_scores: bool) -> str:
    base = (
        f"{prediction.player_one.name}: {prediction.probability_one:.2%}\n"
        f"{prediction.player_two.name}: {prediction.probability_two:.2%}"
    )
    if not show_scores:
        return base

    return (
        f"{base}\n"
        f"  quality {prediction.player_one.name}: {prediction.player_one.quality_score():.3f}\n"
        f"  quality {prediction.player_two.name}: {prediction.player_two.quality_score():.3f}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Estimate tennis match win probabilities based on per-player statistics. "
            "Rates must be expressed as fractions between 0 and 1. The CLI can also "
            "process CSV files with many matches."
        )
    )

    parser.add_argument(
        "--matches-file",
        type=Path,
        help=(
            "CSV file containing match rows with columns like "
            "'player_one_name', 'player_one_ranking', ..."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write predictions as CSV (batch mode only)",
    )
    parser.add_argument(
        "--show-scores",
        action="store_true",
        help="Show intermediate quality scores alongside probabilities",
    )

    for prefix in ("player_one", "player_two"):
        group = parser.add_argument_group(f"{prefix.replace('_', ' ').title()} stats")
        group.add_argument(f"--{prefix}-name", help="Player name")
        group.add_argument(
            f"--{prefix}-ranking",
            type=int,
            help="ATP/WTA ranking (lower is better)",
        )
        group.add_argument(
            f"--{prefix}-serve",
            type=_bounded_float,
            help="Fraction of serve points won (0-1)",
        )
        group.add_argument(
            f"--{prefix}-return",
            type=_bounded_float,
            help="Fraction of return points won (0-1)",
        )
        group.add_argument(
            f"--{prefix}-surface",
            type=_bounded_float,
            help="Surface-specific win percentage (0-1)",
        )
        group.add_argument(
            f"--{prefix}-form",
            type=_bounded_float,
            help="Recent form score (0-1)",
        )

    return parser


def _validate_manual_mode(namespace: argparse.Namespace) -> None:
    missing = [
        name
        for name in (
            "player_one_name",
            "player_one_ranking",
            "player_one_serve",
            "player_one_return",
            "player_one_surface",
            "player_one_form",
            "player_two_name",
            "player_two_ranking",
            "player_two_serve",
            "player_two_return",
            "player_two_surface",
            "player_two_form",
        )
        if getattr(namespace, name) is None
    ]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(
            "Manual mode requires all player statistics. Missing options: " + joined
        )

    for prefix in ("player_one", "player_two"):
        ranking = getattr(namespace, f"{prefix}_ranking")
        if ranking <= 0:
            raise SystemExit(f"--{prefix}-ranking must be positive")

        for stat in ("serve", "return", "surface", "form"):
            value = getattr(namespace, f"{prefix}_{stat}")
            if not 0 <= value <= 1:
                raise SystemExit(f"--{prefix}-{stat} must be between 0 and 1")


def _run_manual_mode(namespace: argparse.Namespace) -> None:
    _validate_manual_mode(namespace)
    player_one = _build_player(namespace, "player_one")
    player_two = _build_player(namespace, "player_two")
    prediction = predict_match(player_one, player_two)
    print(_format_prediction(prediction, namespace.show_scores))


def _run_batch_mode(namespace: argparse.Namespace) -> None:
    if namespace.matches_file is None:
        raise SystemExit("Batch mode requires --matches-file option")

    predictions = predict_from_csv(namespace.matches_file)
    if namespace.output:
        _write_predictions_csv(predictions, namespace.output)

    for prediction in predictions:
        print(_format_prediction(prediction, namespace.show_scores))
        print("-")


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    namespace = parser.parse_args(argv)

    if namespace.matches_file:
        _run_batch_mode(namespace)
    else:
        _run_manual_mode(namespace)


if __name__ == "__main__":
    main()
