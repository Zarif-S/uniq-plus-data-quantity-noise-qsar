"""Sanity tests for src/feature_selection."""

import numpy as np
import pandas as pd
import pytest
from src.feature_selection import (
    RDMOLDES_DESCRIPTORS,
    correlation_prune,
    descriptor_component_matrix,
    descriptor_pc1_matrix,
    drop_constant_descriptors,
    evaluate_descriptor_set,
    mutual_info_per_descriptor,
    rdmoldes_descriptor_map,
    run_descriptor_rfe,
    vif_mi_table,
    vif_prune,
)


# ── rdmoldes_descriptor_map ───────────────────────────────────────────────

def test_rdmoldes_descriptor_map_covers_all_316_features_once():
    descriptor_map = rdmoldes_descriptor_map()
    all_indices = sorted(i for features in descriptor_map.values() for i in features)
    assert all_indices == list(range(316))


def test_rdmoldes_descriptor_map_matches_declared_names_and_sizes():
    descriptor_map = rdmoldes_descriptor_map()
    assert set(descriptor_map.keys()) == {name for name, _ in RDMOLDES_DESCRIPTORS}
    for name, n_features in RDMOLDES_DESCRIPTORS:
        assert len(descriptor_map[name]) == n_features


def test_rdmoldes_descriptor_map_is_contiguous_in_declared_order():
    descriptor_map = rdmoldes_descriptor_map()
    start = 0
    for name, n_features in RDMOLDES_DESCRIPTORS:
        assert descriptor_map[name] == list(range(start, start + n_features))
        start += n_features


# ── drop_constant_descriptors ─────────────────────────────────────────────

@pytest.fixture
def constant_map_data():
    rng = np.random.RandomState(0)
    X = np.column_stack([
        np.full(20, 5.0),          # "const" - zero variance
        rng.normal(size=20),       # "varying" - informative
        np.column_stack([np.full(20, 1.0), rng.normal(size=20)]),  # "mixed" - one const, one varying feature
    ])
    descriptor_map = {"const": [0], "varying": [1], "mixed": [2, 3]}
    return X, descriptor_map


def test_drop_constant_descriptors_drops_all_zero_variance(constant_map_data):
    X, descriptor_map = constant_map_data
    kept, dropped = drop_constant_descriptors(X, descriptor_map)
    assert dropped == ["const"]
    assert set(kept.keys()) == {"varying", "mixed"}


def test_drop_constant_descriptors_keeps_descriptor_if_any_feature_varies(constant_map_data):
    X, descriptor_map = constant_map_data
    kept, dropped = drop_constant_descriptors(X, descriptor_map)
    assert "mixed" in kept
    assert kept["mixed"] == [2, 3]


def test_drop_constant_descriptors_no_mutation(constant_map_data):
    X, descriptor_map = constant_map_data
    original_map = {k: list(v) for k, v in descriptor_map.items()}
    drop_constant_descriptors(X, descriptor_map)
    assert descriptor_map == original_map


# ── descriptor_component_matrix / descriptor_pc1_matrix ──────────────────

@pytest.fixture
def component_test_data():
    rng = np.random.RandomState(42)
    n = 50
    scalar = rng.normal(size=(n, 1))
    vector = rng.normal(size=(n, 4))
    X = np.column_stack([scalar, vector])
    descriptor_map = {"scalar_desc": [0], "vector_desc": [1, 2, 3, 4]}
    return X, descriptor_map


def test_descriptor_component_matrix_scalar_descriptor_has_one_component(component_test_data):
    X, descriptor_map = component_test_data
    components = descriptor_component_matrix(X, descriptor_map, n_components=5)
    assert components["scalar_desc"].shape == (X.shape[0], 1)


def test_descriptor_component_matrix_caps_k_at_n_features(component_test_data):
    X, descriptor_map = component_test_data
    components = descriptor_component_matrix(X, descriptor_map, n_components=5)
    assert components["vector_desc"].shape == (X.shape[0], 4)


def test_descriptor_pc1_matrix_returns_dataframe_of_first_components(component_test_data):
    X, descriptor_map = component_test_data
    components = descriptor_component_matrix(X, descriptor_map, n_components=5)
    pc1_df = descriptor_pc1_matrix(components)
    assert isinstance(pc1_df, pd.DataFrame)
    assert list(pc1_df.columns) == ["scalar_desc", "vector_desc"]
    assert len(pc1_df) == X.shape[0]
    np.testing.assert_array_equal(pc1_df["vector_desc"].values, components["vector_desc"][:, 0])


# ── mutual_info_per_descriptor ────────────────────────────────────────────

def test_mutual_info_per_descriptor_ranks_informative_descriptor_higher():
    rng = np.random.RandomState(0)
    n = 200
    informative = rng.normal(size=n)
    noise = rng.normal(size=n)
    y = informative * 3 + rng.normal(scale=0.1, size=n)

    component_map = {
        "informative": informative.reshape(-1, 1),
        "noise": noise.reshape(-1, 1),
    }
    y_by_endpoint = {"ep1": pd.Series(y, index=range(n))}

    mi_max, mi_table = mutual_info_per_descriptor(component_map, y_by_endpoint, random_state=0)
    assert mi_max["informative"] > mi_max["noise"]
    assert list(mi_table.columns) == ["ep1"]


def test_mutual_info_per_descriptor_uses_max_across_endpoints():
    rng = np.random.RandomState(0)
    n = 100
    x = rng.normal(size=n)
    y_useful = x * 3 + rng.normal(scale=0.1, size=n)
    y_useless = rng.normal(size=n)

    component_map = {"desc": x.reshape(-1, 1)}
    y_by_endpoint = {
        "ep_useless": pd.Series(y_useless, index=range(n)),
        "ep_useful": pd.Series(y_useful, index=range(n)),
    }

    mi_max, mi_table = mutual_info_per_descriptor(component_map, y_by_endpoint, random_state=0)
    assert mi_max["desc"] == mi_table.loc["desc"].max()
    assert mi_max["desc"] == mi_table.loc["desc", "ep_useful"]


# ── correlation_prune ─────────────────────────────────────────────────────

def test_correlation_prune_drops_the_lower_mi_of_a_duplicate_pair():
    rng = np.random.RandomState(0)
    n = 100
    base = rng.normal(size=n)
    component_map = {
        "a": base.reshape(-1, 1),
        "b": (base + rng.normal(scale=1e-6, size=n)).reshape(-1, 1),  # near-identical to "a"
        "independent": rng.normal(size=n).reshape(-1, 1),
    }
    mi_scores = pd.Series({"a": 0.5, "b": 0.2, "independent": 0.1})

    kept, dropped_records = correlation_prune(component_map, mi_scores, threshold=0.9)

    assert "b" not in kept
    assert "a" in kept
    assert "independent" in kept
    assert dropped_records[0]["dropped"] == "b"
    assert dropped_records[0]["kept_instead"] == "a"


def test_correlation_prune_keeps_uncorrelated_descriptors():
    rng = np.random.RandomState(0)
    n = 100
    component_map = {
        "a": rng.normal(size=n).reshape(-1, 1),
        "b": rng.normal(size=n).reshape(-1, 1),
    }
    mi_scores = pd.Series({"a": 0.5, "b": 0.5})

    kept, dropped_records = correlation_prune(component_map, mi_scores, threshold=0.9)
    assert set(kept) == {"a", "b"}
    assert dropped_records == []


# ── vif_prune / vif_mi_table ──────────────────────────────────────────────

def test_vif_prune_drops_exact_linear_combination_as_inf_vif():
    rng = np.random.RandomState(0)
    n = 100
    a = rng.normal(size=n)
    b = rng.normal(size=n)
    c = a + b  # exact accounting identity, like CalcNumAromaticRings = carbo + hetero
    pc1_df = pd.DataFrame({"a": a, "b": b, "c": c})
    mi_scores = pd.Series({"a": 0.5, "b": 0.5, "c": 0.1})

    kept, trace = vif_prune(pc1_df, mi_scores, threshold=5.0)

    assert "c" not in kept
    assert trace[0]["dropped"] == "c"
    assert np.isinf(trace[0]["vif"])


def test_vif_prune_keeps_independent_descriptors():
    rng = np.random.RandomState(0)
    n = 100
    pc1_df = pd.DataFrame({
        "a": rng.normal(size=n),
        "b": rng.normal(size=n),
        "c": rng.normal(size=n),
    })
    mi_scores = pd.Series({"a": 0.5, "b": 0.5, "c": 0.5})

    kept, trace = vif_prune(pc1_df, mi_scores, threshold=5.0)
    assert set(kept) == {"a", "b", "c"}
    assert trace == []


def test_vif_prune_tiebreak_drops_lower_mi_descriptor():
    rng = np.random.RandomState(1)
    n = 200
    a = rng.normal(size=n)
    b = rng.normal(size=n)
    # both "c" and "d" ~equally collinear with a+b (tie_margin should catch them together)
    c = a + b + rng.normal(scale=0.05, size=n)
    d = a + b + rng.normal(scale=0.05, size=n)
    pc1_df = pd.DataFrame({"a": a, "b": b, "c": c, "d": d})
    mi_scores = pd.Series({"a": 0.5, "b": 0.5, "c": 0.1, "d": 0.9})

    kept, trace = vif_prune(pc1_df, mi_scores, threshold=5.0, tie_margin=0.2)
    # "c" has lower MI than "d", so among near-tied high-VIF candidates it should go first
    assert trace[0]["dropped"] == "c"


def test_vif_mi_table_has_expected_columns_and_ranks():
    rng = np.random.RandomState(0)
    n = 100
    pc1_df = pd.DataFrame({
        "a": rng.normal(size=n),
        "b": rng.normal(size=n),
    })
    mi_scores = pd.Series({"a": 0.9, "b": 0.1})

    table = vif_mi_table(pc1_df, mi_scores)
    assert set(table.columns) == {"mi", "vif", "mi_rank", "vif_elim_rank"}
    assert table.index[0] == "a"  # highest MI first


# ── evaluate_descriptor_set ────────────────────────────────────────────────

def _constant_predictor_factory():
    class _Const:
        def fit(self, X, y):
            self._mean = np.mean(y)
            return self

        def predict(self, X):
            return np.full(len(X), self._mean)

        def get_params(self, deep=True):
            return {}

        def set_params(self, **params):
            return self

    return _Const()


def test_evaluate_descriptor_set_returns_mean_and_per_endpoint_scores():
    rng = np.random.RandomState(0)
    n = 60
    X = rng.normal(size=(n, 4))
    descriptor_map = {"d1": [0, 1], "d2": [2, 3]}
    y_by_endpoint = {
        "ep1": pd.Series(rng.normal(size=n)),
        "ep2": pd.Series(rng.normal(size=n)),
    }
    X_by_endpoint = {"ep1": X, "ep2": X}

    scores = evaluate_descriptor_set(
        X_by_endpoint, y_by_endpoint, descriptor_map, ["d1", "d2"], cv=3,
        estimator_factory=_constant_predictor_factory,
    )

    assert set(scores.keys()) == {"ep1", "ep2", "mean"}
    assert scores["mean"] == pytest.approx(np.mean([scores["ep1"], scores["ep2"]]))


# ── run_descriptor_rfe ──────────────────────────────────────────────────────

def test_run_descriptor_rfe_eliminates_down_to_min_descriptors():
    rng = np.random.RandomState(0)
    n = 80
    X = rng.normal(size=(n, 8))
    descriptor_map = {f"d{i}": [i] for i in range(8)}
    y_by_endpoint = {"ep1": pd.Series(X[:, 0] * 2 + rng.normal(scale=0.1, size=n))}
    X_by_endpoint = {"ep1": X}

    trace = run_descriptor_rfe(
        X_by_endpoint, y_by_endpoint, descriptor_map, min_descriptors=3, cv=3,
    )

    assert trace[0]["n_descriptors"] == 8
    assert trace[0]["dropped"] is None
    assert trace[-1]["n_descriptors"] == 3
    # each step drops exactly one descriptor from the previous step's set
    for prev, cur in zip(trace, trace[1:]):
        assert cur["n_descriptors"] == prev["n_descriptors"] - 1
        assert cur["dropped"] not in cur["descriptors"]
        assert set(cur["descriptors"]) == set(prev["descriptors"]) - {cur["dropped"]}


def test_run_descriptor_rfe_protects_the_only_informative_descriptor():
    # Regression test for a real bug: run_descriptor_rfe used to eliminate on
    # LGBMRegressor's *default* feature_importances_ (split-count), not the gain-based
    # importance its own docstring described. Under split-count, a single strongly
    # informative descriptor could still get dropped mid-trace (noise descriptors racking
    # up split counts deep in the trees), only for its removal to show up as the trace's
    # biggest score drop. With importance_type='gain' (the fix), the informative
    # descriptor should never be judged least-important, and should survive every
    # elimination step -- see src/feature_selection/CLAUDE.md's split-vs-gain note.
    rng = np.random.RandomState(0)
    n = 100
    X = rng.normal(size=(n, 6))
    descriptor_map = {f"d{i}": [i] for i in range(6)}
    # only d0 is informative; the rest are pure noise
    y_by_endpoint = {"ep1": pd.Series(X[:, 0] * 5 + rng.normal(scale=0.05, size=n))}
    X_by_endpoint = {"ep1": X}

    trace = run_descriptor_rfe(
        X_by_endpoint, y_by_endpoint, descriptor_map, min_descriptors=1, cv=3,
    )

    dropped_names = {row["dropped"] for row in trace if row["dropped"] is not None}
    assert "d0" not in dropped_names
    assert trace[-1]["descriptors"] == ["d0"]
