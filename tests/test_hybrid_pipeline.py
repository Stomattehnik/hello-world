from __future__ import annotations

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hybrid_pipeline import HybridPipelineConfig, HybridWinProbabilityPipeline


def _make_dataset(samples: int = 240) -> list[dict[str, float]]:
    rng = random.Random(2024)
    data: list[dict[str, float]] = []
    for _ in range(samples):
        p1_rank = rng.uniform(0, 1)
        p2_rank = rng.uniform(0, 1)
        form_gap = rng.uniform(-1, 1)
        surface = rng.uniform(0, 1)
        experience = rng.uniform(0, 1)
        opponent_matchup = rng.uniform(-0.5, 0.5)

        linear_score = (
            1.6 * (p2_rank - p1_rank)
            + 1.1 * form_gap
            + 0.7 * (surface - 0.4)
            + 0.6 * (experience - 0.5)
            + 0.9 * opponent_matchup
        )
        probability = 1.0 / (1.0 + math.exp(-linear_score))
        label = 1 if rng.random() < probability else 0

        data.append(
            {
                "player_one_rank": p1_rank,
                "player_two_rank": p2_rank,
                "form_gap": form_gap,
                "surface_rating": surface,
                "player_one_experience": experience,
                "opponent_matchup": opponent_matchup,
                "winner": float(label),
            }
        )
    return data


def test_hybrid_pipeline_stack(tmp_path: Path) -> None:
    dataset = _make_dataset()
    config = HybridPipelineConfig(
        target_column="winner",
        numeric_features=[
            "player_one_rank",
            "player_two_rank",
            "form_gap",
            "surface_rating",
            "player_one_experience",
            "opponent_matchup",
        ],
        n_splits=4,
        boosting_estimators=60,
        boosting_learning_rate=0.15,
        hidden_size=24,
        nn_learning_rate=0.03,
        nn_epochs=120,
        random_state=17,
    )

    pipeline = HybridWinProbabilityPipeline(config)
    pipeline.fit(dataset)

    metrics = pipeline.evaluate(dataset)
    assert metrics["roc_auc"] > 0.7
    assert metrics["log_loss"] < 0.7

    sample = dataset[:5]
    probabilities = pipeline.predict_proba(sample)
    assert len(probabilities) == 5
    for prob in probabilities:
        assert math.isclose(prob[0] + prob[1], 1.0, rel_tol=1e-6)

    model_path = tmp_path / "hybrid_model.json"
    pipeline.save(model_path)
    restored = HybridWinProbabilityPipeline.load(model_path)
    restored_probs = restored.predict_proba(sample)
    for original, recovered in zip(probabilities, restored_probs):
        assert math.isclose(original[1], recovered[1], rel_tol=1e-6)


def test_roc_auc_tie_handling() -> None:
    # Two identical probability scores should yield an AUC of 0.5 when
    # the labels contain both classes. The previous implementation assigned
    # different ranks to ties, inflating the metric.
    from hybrid_pipeline import _roc_auc_score

    probabilities = [0.5, 0.5]
    targets = [0, 1]
    assert math.isclose(_roc_auc_score(targets, probabilities), 0.5)
