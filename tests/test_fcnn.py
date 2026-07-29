"""Sanity tests for the FCNN wrapper (DeepChem MultitaskRegressor). Fits are kept tiny."""

import warnings

import numpy as np
from sklearn.base import clone

from src.hyperparams import param_base_FCNN
from src.models import FCNN


def _tiny_xy(n=60, d=12, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.random((n, d)).astype(np.float32)
    y = X @ rng.random(d) + rng.normal(scale=0.02, size=n)
    return X, y


def test_fcnn_clone_preserves_params_before_fit():
    m = FCNN(hidden_layers=(16, 8), dropout=(0.1, 0.1), epochs=3, beta1=0.9, random_state=0)
    m2 = clone(m)   # sklearn clone relies on get_params/set_params + unmodified attrs
    assert m2.get_params()["hidden_layers"] == (16, 8)
    assert m2.get_params()["beta1"] == 0.9


def test_fcnn_fit_predict_shape_and_finite():
    X, y = _tiny_xy()
    m = FCNN(hidden_layers=(16,), dropout=(0.1,), epochs=5, random_state=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(X, y)
        pred = m.predict(X)
    assert pred.shape == (X.shape[0],)
    assert np.isfinite(pred).all()
    assert m.n_features_in_ == X.shape[1]


def test_fcnn_batch_norm_true_warns_and_false_does_not():
    X, y = _tiny_xy()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        FCNN(hidden_layers=(8,), dropout=(0.0,), epochs=2, batch_norm=True, random_state=0).fit(X, y)
    assert any("batch_norm" in str(x.message) for x in w)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        FCNN(hidden_layers=(8,), dropout=(0.0,), epochs=2, batch_norm=False, random_state=0).fit(X, y)
    assert not any("batch_norm" in str(x.message) for x in w)


def test_fcnn_beta1_is_wired_into_the_adam_optimizer():
    X, y = _tiny_xy()
    m = FCNN(hidden_layers=(8,), dropout=(0.0,), epochs=2, lr=0.001, beta1=0.9, random_state=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(X, y)
    opt = m.model_.optimizer
    assert type(opt).__name__ == "Adam"
    assert opt.learning_rate == 0.001
    assert opt.beta1 == 0.9


def test_fcnn_one_element_weight_init_stddevs_collapses_to_scalar():
    # A 1-element list means "same value for every layer"; it must NOT be passed verbatim (that
    # would collapse the DeepChem net to a single layer). _weight_init_stddevs() returns a scalar.
    m = FCNN(hidden_layers=(16, 8, 4), weight_init_stddevs=(0.02,))
    assert m._weight_init_stddevs() == 0.02
    # a genuine per-layer list is preserved
    m2 = FCNN(hidden_layers=(16, 8), weight_init_stddevs=(0.01, 0.02, 0.03))
    assert m2._weight_init_stddevs() == [0.01, 0.02, 0.03]


def test_fcnn_constructs_from_param_base_fcnn():
    m = FCNN(**param_base_FCNN, random_state=42)
    assert m.hidden_layers == [512, 256, 64]
    assert m.beta1 == 0.9
    assert m.epochs == 50
