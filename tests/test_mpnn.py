"""Sanity tests for the ChemProp MPNN wrapper. The two end-to-end fits are tiny (2 epochs)."""

import warnings

import numpy as np
from sklearn.base import clone

from src.hyperparams import param_base_MPNN
from src.models import ChempropRegressor

# A small set of valid drug-like SMILES, enough for ChemProp's internal train/val/test split.
_SMILES = [
    "CCO", "CCN", "CCC", "c1ccccc1", "CC(=O)O", "CCOCC", "CC(C)O", "c1ccncc1",
    "CCCl", "CCBr", "CC(=O)N", "c1ccc(O)cc1", "CCCCO", "CN(C)C", "CC(=O)C",
    "c1ccc(N)cc1", "OCC(O)CO", "CC(C)(C)O", "c1ccc(F)cc1", "CCS", "CCC(=O)O",
    "c1ccc(Cl)cc1", "CCCN", "CC#N",
]


def _xy(use_features=False, seed=0):
    rng = np.random.default_rng(seed)
    smi = np.array(_SMILES, dtype=object)
    y = rng.random(len(smi))
    if use_features:
        feats = rng.random((len(smi), 5))
        X = np.column_stack([smi, feats]).astype(object)
    else:
        X = smi.reshape(-1, 1)
    return X, y


def test_split_x_graph_only():
    m = ChempropRegressor(use_features=False)
    X, _ = _xy(use_features=False)
    smiles, feats = m._split_X(X)
    assert smiles[:2] == ["CCO", "CCN"]
    assert feats is None


def test_split_x_with_features():
    m = ChempropRegressor(use_features=True)
    X, _ = _xy(use_features=True)
    smiles, feats = m._split_X(X)
    assert smiles[0] == "CCO"
    assert feats.shape == (len(_SMILES), 5)
    assert feats.dtype == np.float64


def test_split_x_accepts_1d():
    m = ChempropRegressor(use_features=False)
    smiles, feats = m._split_X(np.array(_SMILES, dtype=object))  # 1D
    assert len(smiles) == len(_SMILES)
    assert feats is None


def test_clone_preserves_params():
    m = ChempropRegressor(hidden_size=200, depth=4, use_features=True, epochs=7, random_state=1)
    p = clone(m).get_params()
    assert p["hidden_size"] == 200 and p["depth"] == 4
    assert p["use_features"] is True and p["epochs"] == 7


def test_defaults_match_param_base_mpnn():
    m = ChempropRegressor()
    for k, v in param_base_MPNN.items():
        assert getattr(m, k) == v


def test_mpnn1_fit_predict_end_to_end():
    X, y = _xy(use_features=False)
    m = ChempropRegressor(use_features=False, epochs=2, random_state=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(X, y)
        pred = m.predict(X)
    assert pred.shape == (len(_SMILES),)
    assert np.isfinite(pred).all()


def test_mpnn2_fit_predict_with_features_end_to_end():
    X, y = _xy(use_features=True)
    m = ChempropRegressor(use_features=True, epochs=2, random_state=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(X, y)
        pred = m.predict(X)
    assert pred.shape == (len(_SMILES),)
    assert np.isfinite(pred).all()


def test_mpnn3_fit_predict_with_features_generator_end_to_end():
    # MPNN2: SMILES-only X, ChemProp generates rdkit_2d_normalized descriptors internally.
    X, y = _xy(use_features=False)
    m = ChempropRegressor(features_generator="rdkit_2d_normalized", epochs=2, random_state=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(X, y)
        pred = m.predict(X)
    assert pred.shape == (len(_SMILES),)
    assert np.isfinite(pred).all()


def test_mpnn3_feature_modes_mutually_exclusive():
    import pytest
    X, y = _xy(use_features=True)
    m = ChempropRegressor(use_features=True, features_generator="rdkit_2d_normalized")
    with pytest.raises(ValueError, match="mutually exclusive"):
        m.fit(X, y)


def test_tune_mpnn_hyperopt_returns_config():
    from src.models import tune_mpnn_hyperopt
    X, y = _xy(use_features=False)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        best = tune_mpnn_hyperopt(X, y, use_features=False, num_iters=2, epochs=1, random_state=0)
    assert set(best) == {"hidden_size", "depth", "dropout", "ffn_num_layers"}
    assert isinstance(best["hidden_size"], int) and isinstance(best["ffn_num_layers"], int)
    assert isinstance(best["dropout"], float)
    # a returned config must be directly usable to build the estimator
    ChempropRegressor(**best, use_features=False)
