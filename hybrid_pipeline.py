"""Hybrid gradient boosting + neural network pipeline with minimal dependencies."""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def _logit(probability: float) -> float:
    clipped = min(max(probability, 1e-6), 1.0 - 1e-6)
    return math.log(clipped / (1.0 - clipped))


def _relu(value: float) -> float:
    return value if value > 0.0 else 0.0


def _relu_derivative(value: float) -> float:
    return 1.0 if value > 0.0 else 0.0


def _vector_dot(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(l * r for l, r in zip(left, right))


@dataclass
class FeatureScaler:
    """Simple standard scaler for numeric features."""

    means: List[float] = field(default_factory=list)
    stds: List[float] = field(default_factory=list)

    def fit(self, samples: Sequence[Sequence[float]]) -> None:
        if not samples:
            raise ValueError("cannot fit scaler on empty data")

        dimension = len(samples[0])
        sums = [0.0] * dimension
        squared_sums = [0.0] * dimension

        for row in samples:
            for idx, value in enumerate(row):
                sums[idx] += value
                squared_sums[idx] += value * value

        count = float(len(samples))
        self.means = [total / count for total in sums]
        self.stds = []
        for idx in range(dimension):
            mean = self.means[idx]
            variance = max(squared_sums[idx] / count - mean * mean, 1e-8)
            self.stds.append(math.sqrt(variance))

    def transform(self, samples: Sequence[Sequence[float]]) -> List[List[float]]:
        if not self.means or not self.stds:
            raise RuntimeError("scaler has not been fitted")

        transformed: List[List[float]] = []
        for row in samples:
            transformed_row = [
                (value - mean) / std for value, mean, std in zip(row, self.means, self.stds)
            ]
            transformed.append(transformed_row)
        return transformed

    def to_dict(self) -> Dict[str, List[float]]:
        return {"means": self.means, "stds": self.stds}

    @classmethod
    def from_dict(cls, payload: Mapping[str, Iterable[float]]) -> "FeatureScaler":
        instance = cls()
        instance.means = list(payload["means"])
        instance.stds = list(payload["stds"])
        return instance


@dataclass
class DecisionStump:
    feature_index: int
    threshold: float
    left_value: float
    right_value: float

    def predict(self, features: Sequence[float]) -> float:
        if features[self.feature_index] <= self.threshold:
            return self.left_value
        return self.right_value

    def to_dict(self) -> Dict[str, float]:
        return {
            "feature_index": self.feature_index,
            "threshold": self.threshold,
            "left_value": self.left_value,
            "right_value": self.right_value,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, float]) -> "DecisionStump":
        return cls(
            feature_index=int(payload["feature_index"]),
            threshold=float(payload["threshold"]),
            left_value=float(payload["left_value"]),
            right_value=float(payload["right_value"]),
        )


class GradientBoostingBinaryClassifier:
    """Tiny gradient boosting model based on decision stumps."""

    def __init__(self, n_estimators: int = 50, learning_rate: float = 0.1, random_state: int | None = None):
        if n_estimators <= 0:
            raise ValueError("n_estimators must be positive")
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.initial_prediction: float = 0.0
        self.stumps: List[DecisionStump] = []

    def fit(self, features: Sequence[Sequence[float]], targets: Sequence[int]) -> None:
        if not features:
            raise ValueError("cannot train on empty dataset")
        positives = sum(targets)
        self.initial_prediction = _logit(positives / len(targets))
        self.stumps = []
        raw_scores = [self.initial_prediction for _ in range(len(features))]

        for _ in range(self.n_estimators):
            residuals = [target - _sigmoid(score) for target, score in zip(targets, raw_scores)]
            stump = self._fit_stump(features, residuals)
            self.stumps.append(stump)
            for idx, row in enumerate(features):
                raw_scores[idx] += self.learning_rate * stump.predict(row)

    def _fit_stump(self, features: Sequence[Sequence[float]], residuals: Sequence[float]) -> DecisionStump:
        best_error = float("inf")
        best_stump: DecisionStump | None = None
        feature_count = len(features[0])
        for feature_idx in range(feature_count):
            sorted_indices = sorted(range(len(features)), key=lambda idx: features[idx][feature_idx])
            sorted_values = [features[idx][feature_idx] for idx in sorted_indices]
            sorted_residuals = [residuals[idx] for idx in sorted_indices]
            prefix_sum = [0.0]
            prefix_sq = [0.0]
            for value in sorted_residuals:
                prefix_sum.append(prefix_sum[-1] + value)
                prefix_sq.append(prefix_sq[-1] + value * value)

            total_sum = prefix_sum[-1]
            total_sq = prefix_sq[-1]

            for split in range(1, len(sorted_indices)):
                if sorted_values[split] == sorted_values[split - 1]:
                    continue

                left_count = split
                right_count = len(sorted_indices) - split
                left_sum = prefix_sum[split]
                right_sum = total_sum - left_sum
                left_sq = prefix_sq[split]
                right_sq = total_sq - left_sq
                left_mean = left_sum / left_count
                right_mean = right_sum / right_count
                left_error = left_sq - left_sum * left_mean
                right_error = right_sq - right_sum * right_mean
                error = left_error + right_error
                if error < best_error:
                    threshold = (sorted_values[split] + sorted_values[split - 1]) / 2.0
                    best_error = error
                    best_stump = DecisionStump(feature_idx, threshold, left_mean, right_mean)

        if best_stump is None:
            mean_residual = sum(residuals) / len(residuals)
            best_stump = DecisionStump(0, 0.0, mean_residual, mean_residual)

        return best_stump

    def predict_positive(self, features: Sequence[Sequence[float]]) -> List[float]:
        probabilities = []
        for row in features:
            score = self.initial_prediction
            for stump in self.stumps:
                score += self.learning_rate * stump.predict(row)
            probabilities.append(_sigmoid(score))
        return probabilities

    def predict_proba(self, features: Sequence[Sequence[float]]) -> List[Tuple[float, float]]:
        probabilities = self.predict_positive(features)
        return [(1.0 - prob, prob) for prob in probabilities]

    def to_dict(self) -> Dict[str, object]:
        return {
            "n_estimators": self.n_estimators,
            "learning_rate": self.learning_rate,
            "initial_prediction": self.initial_prediction,
            "stumps": [stump.to_dict() for stump in self.stumps],
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "GradientBoostingBinaryClassifier":
        instance = cls(
            n_estimators=int(payload["n_estimators"]),
            learning_rate=float(payload["learning_rate"]),
        )
        instance.initial_prediction = float(payload["initial_prediction"])
        instance.stumps = [DecisionStump.from_dict(stump) for stump in payload["stumps"]]
        return instance


class StackingNeuralNetwork:
    """Small neural network with a single hidden layer and sigmoid output."""

    def __init__(
        self,
        input_dim: int,
        hidden_size: int = 32,
        learning_rate: float = 0.05,
        epochs: int = 200,
        random_state: int | None = None,
    ) -> None:
        if hidden_size <= 0:
            raise ValueError("hidden_size must be positive")
        self.input_dim = input_dim
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.random_state = random_state
        rng = random.Random(random_state)
        self.weights_input_hidden = [
            [rng.uniform(-0.5, 0.5) for _ in range(input_dim)]
            for _ in range(hidden_size)
        ]
        self.bias_hidden = [0.0 for _ in range(hidden_size)]
        self.weights_hidden_output = [rng.uniform(-0.5, 0.5) for _ in range(hidden_size)]
        self.bias_output = 0.0

    def _forward(self, features: Sequence[float]) -> Tuple[List[List[float]], List[List[float]]]:
        activations: List[List[float]] = [list(features)]
        pre_activations: List[List[float]] = []

        hidden_pre = []
        hidden_act = []
        for neuron_idx in range(self.hidden_size):
            z_value = _vector_dot(self.weights_input_hidden[neuron_idx], features) + self.bias_hidden[neuron_idx]
            hidden_pre.append(z_value)
            hidden_act.append(_relu(z_value))
        pre_activations.append(hidden_pre)
        activations.append(hidden_act)

        output_pre = _vector_dot(self.weights_hidden_output, hidden_act) + self.bias_output
        pre_activations.append([output_pre])
        activations.append([_sigmoid(output_pre)])
        return activations, pre_activations

    def predict_positive(self, features: Sequence[Sequence[float]]) -> List[float]:
        probabilities = []
        for row in features:
            _, pre_activations = self._forward(row)
            probabilities.append(_sigmoid(pre_activations[-1][0]))
        return probabilities

    def predict_proba(self, features: Sequence[Sequence[float]]) -> List[Tuple[float, float]]:
        probabilities = self.predict_positive(features)
        return [(1.0 - prob, prob) for prob in probabilities]

    def fit(self, features: Sequence[Sequence[float]], targets: Sequence[int]) -> None:
        rng = random.Random(self.random_state)
        indices = list(range(len(features)))
        for _ in range(self.epochs):
            rng.shuffle(indices)
            for idx in indices:
                row = features[idx]
                target = targets[idx]
                activations, pre_activations = self._forward(row)
                hidden_activations = activations[1]
                output_pre = pre_activations[-1][0]
                prediction = _sigmoid(output_pre)
                delta_output = prediction - target

                hidden_snapshot = list(self.weights_hidden_output)
                for j in range(self.hidden_size):
                    gradient = delta_output * hidden_activations[j]
                    self.weights_hidden_output[j] -= self.learning_rate * gradient
                self.bias_output -= self.learning_rate * delta_output

                hidden_deltas: List[float] = []
                for j in range(self.hidden_size):
                    derivative = _relu_derivative(pre_activations[0][j])
                    hidden_deltas.append(hidden_snapshot[j] * delta_output * derivative)

                input_activation = activations[0]
                for neuron_idx in range(self.hidden_size):
                    delta = hidden_deltas[neuron_idx]
                    for weight_idx in range(self.input_dim):
                        gradient = delta * input_activation[weight_idx]
                        self.weights_input_hidden[neuron_idx][weight_idx] -= self.learning_rate * gradient
                    self.bias_hidden[neuron_idx] -= self.learning_rate * delta

    def to_dict(self) -> Dict[str, object]:
        return {
            "input_dim": self.input_dim,
            "hidden_size": self.hidden_size,
            "learning_rate": self.learning_rate,
            "epochs": self.epochs,
            "weights_input_hidden": self.weights_input_hidden,
            "bias_hidden": self.bias_hidden,
            "weights_hidden_output": self.weights_hidden_output,
            "bias_output": self.bias_output,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "StackingNeuralNetwork":
        instance = cls(
            input_dim=int(payload["input_dim"]),
            hidden_size=int(payload["hidden_size"]),
            learning_rate=float(payload["learning_rate"]),
            epochs=int(payload["epochs"]),
        )
        instance.weights_input_hidden = [list(map(float, row)) for row in payload["weights_input_hidden"]]
        instance.bias_hidden = [float(value) for value in payload["bias_hidden"]]
        instance.weights_hidden_output = [float(value) for value in payload["weights_hidden_output"]]
        instance.bias_output = float(payload["bias_output"])
        return instance


def _is_dataframe(candidate: object) -> bool:
    return hasattr(candidate, "iloc") and hasattr(candidate, "columns")


def _extract_features(
    data: Sequence[Mapping[str, float]] | "DataFrameLike",
    feature_columns: Sequence[str],
) -> List[List[float]]:
    if _is_dataframe(data):
        rows = []
        length = len(data)  # type: ignore[arg-type]
        for idx in range(length):
            row = [float(data[column].iloc[idx]) for column in feature_columns]  # type: ignore[index]
            rows.append(row)
        return rows

    rows = []
    for entry in data:
        rows.append([float(entry[column]) for column in feature_columns])
    return rows


def _extract_targets(
    data: Sequence[Mapping[str, float]] | "DataFrameLike",
    target_column: str,
) -> List[int]:
    if _is_dataframe(data):
        length = len(data)  # type: ignore[arg-type]
        return [int(data[target_column].iloc[idx]) for idx in range(length)]  # type: ignore[index]

    return [int(entry[target_column]) for entry in data]


def _roc_auc_score(targets: Sequence[int], probabilities: Sequence[float]) -> float:
    positives = sum(targets)
    negatives = len(targets) - positives
    if positives == 0 or negatives == 0:
        return 0.5

    ranked = sorted(zip(probabilities, targets))
    rank_sum = 0.0
    index = 0
    while index < len(ranked):
        tie_start = index
        tie_value, _ = ranked[index]
        while index < len(ranked) and ranked[index][0] == tie_value:
            index += 1
        tie_end = index  # exclusive
        average_rank = (tie_start + 1 + tie_end) / 2.0
        for tie_index in range(tie_start, tie_end):
            if ranked[tie_index][1] == 1:
                rank_sum += average_rank

    auc = (rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)
    return float(auc)


def _log_loss(targets: Sequence[int], probabilities: Sequence[float]) -> float:
    losses = []
    for target, probability in zip(targets, probabilities):
        clipped = min(max(probability, 1e-6), 1.0 - 1e-6)
        losses.append(-(target * math.log(clipped) + (1 - target) * math.log(1 - clipped)))
    return sum(losses) / len(losses)


def _brier_score(targets: Sequence[int], probabilities: Sequence[float]) -> float:
    return sum((prob - target) ** 2 for prob, target in zip(probabilities, targets)) / len(targets)


def _accuracy(targets: Sequence[int], probabilities: Sequence[float]) -> float:
    predictions = [1 if prob >= 0.5 else 0 for prob in probabilities]
    correct = sum(pred == target for pred, target in zip(predictions, targets))
    return correct / len(targets)


@dataclass
class HybridPipelineConfig:
    target_column: str
    numeric_features: Sequence[str]
    n_splits: int = 4
    boosting_estimators: int = 50
    boosting_learning_rate: float = 0.1
    hidden_size: int = 32
    nn_learning_rate: float = 0.05
    nn_epochs: int = 200
    random_state: int | None = 42

    def __post_init__(self) -> None:
        if not self.numeric_features:
            raise ValueError("at least one feature must be provided")
        if self.n_splits < 2:
            raise ValueError("n_splits must be at least 2")


class HybridWinProbabilityPipeline:
    """Offline stacking pipeline combining gradient boosting and an MLP."""

    def __init__(self, config: HybridPipelineConfig):
        self.config = config
        self.scaler = FeatureScaler()
        self.boosting = GradientBoostingBinaryClassifier(
            n_estimators=config.boosting_estimators,
            learning_rate=config.boosting_learning_rate,
            random_state=config.random_state,
        )
        self.neural_network: StackingNeuralNetwork | None = None
        self._is_fitted = False

    def _split_indices(self, size: int) -> List[List[int]]:
        indices = list(range(size))
        rng = random.Random(self.config.random_state)
        rng.shuffle(indices)
        base_size = size // self.config.n_splits
        remainder = size % self.config.n_splits
        folds: List[List[int]] = []
        start = 0
        for fold_idx in range(self.config.n_splits):
            fold_size = base_size + (1 if fold_idx < remainder else 0)
            folds.append(indices[start : start + fold_size])
            start += fold_size
        return folds

    def fit(self, data: Sequence[Mapping[str, float]] | "DataFrameLike") -> None:
        features = _extract_features(data, self.config.numeric_features)
        targets = _extract_targets(data, self.config.target_column)
        self.scaler.fit(features)
        scaled_features = self.scaler.transform(features)

        oof_predictions = [0.0 for _ in scaled_features]
        folds = self._split_indices(len(scaled_features))
        for fold_idx, validation_indices in enumerate(folds):
            if not validation_indices:
                continue
            validation_set = set(validation_indices)
            train_indices = [idx for idx in range(len(scaled_features)) if idx not in validation_set]
            boosting_model = GradientBoostingBinaryClassifier(
                n_estimators=self.config.boosting_estimators,
                learning_rate=self.config.boosting_learning_rate,
                random_state=(self.config.random_state or 0) + fold_idx,
            )
            train_features = [scaled_features[idx] for idx in train_indices]
            train_targets = [targets[idx] for idx in train_indices]
            boosting_model.fit(train_features, train_targets)
            fold_features = [scaled_features[idx] for idx in validation_indices]
            predictions = boosting_model.predict_positive(fold_features)
            for local_idx, global_idx in enumerate(validation_indices):
                oof_predictions[global_idx] = predictions[local_idx]

        self.boosting.fit(scaled_features, targets)
        stacked_features = [row + [oof_predictions[idx]] for idx, row in enumerate(scaled_features)]
        self.neural_network = StackingNeuralNetwork(
            input_dim=len(stacked_features[0]),
            hidden_size=self.config.hidden_size,
            learning_rate=self.config.nn_learning_rate,
            epochs=self.config.nn_epochs,
            random_state=self.config.random_state,
        )
        self.neural_network.fit(stacked_features, targets)
        self._is_fitted = True

    def predict_proba(self, data: Sequence[Mapping[str, float]] | "DataFrameLike") -> List[Tuple[float, float]]:
        if not self._is_fitted or self.neural_network is None:
            raise RuntimeError("pipeline must be fitted before predicting")
        features = _extract_features(data, self.config.numeric_features)
        scaled_features = self.scaler.transform(features)
        boosting_predictions = self.boosting.predict_positive(scaled_features)
        stacked_features = [row + [boosting_predictions[idx]] for idx, row in enumerate(scaled_features)]
        return self.neural_network.predict_proba(stacked_features)

    def evaluate(self, data: Sequence[Mapping[str, float]] | "DataFrameLike") -> Dict[str, float]:
        probabilities = self.predict_proba(data)
        positive_probabilities = [prob[1] for prob in probabilities]
        targets = _extract_targets(data, self.config.target_column)
        return {
            "roc_auc": _roc_auc_score(targets, positive_probabilities),
            "log_loss": _log_loss(targets, positive_probabilities),
            "brier_score": _brier_score(targets, positive_probabilities),
            "accuracy": _accuracy(targets, positive_probabilities),
        }

    def save(self, path: Path | str) -> None:
        if not self._is_fitted or self.neural_network is None:
            raise RuntimeError("pipeline must be fitted before saving")
        payload = {
            "config": {
                "target_column": self.config.target_column,
                "numeric_features": list(self.config.numeric_features),
                "n_splits": self.config.n_splits,
                "boosting_estimators": self.config.boosting_estimators,
                "boosting_learning_rate": self.config.boosting_learning_rate,
                "hidden_size": self.config.hidden_size,
                "nn_learning_rate": self.config.nn_learning_rate,
                "nn_epochs": self.config.nn_epochs,
                "random_state": self.config.random_state,
            },
            "scaler": self.scaler.to_dict(),
            "boosting": self.boosting.to_dict(),
            "neural_network": self.neural_network.to_dict(),
        }
        Path(path).write_text(json.dumps(payload))

    @classmethod
    def load(cls, path: Path | str) -> "HybridWinProbabilityPipeline":
        payload = json.loads(Path(path).read_text())
        config = HybridPipelineConfig(**payload["config"])
        instance = cls(config)
        instance.scaler = FeatureScaler.from_dict(payload["scaler"])
        instance.boosting = GradientBoostingBinaryClassifier.from_dict(payload["boosting"])
        instance.neural_network = StackingNeuralNetwork.from_dict(payload["neural_network"])
        instance._is_fitted = True
        return instance


__all__ = ["HybridPipelineConfig", "HybridWinProbabilityPipeline"]

