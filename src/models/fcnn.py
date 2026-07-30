"""sklearn-compatible FCNN regressor wrapping DeepChem's MultitaskRegressor (single task).

Reproduces the paper's FCNN (FCNN_public.py) on the tabular molecular featuresets
(fcfp4 / rdmoldes / hybrid, RobustScaler'd), so it drops straight into get_paper_models() +
model_validation() alongside the classical models.

batch_norm caveat: param_base_FCNN sets batch_norm=True, but DeepChem 2.8.0's MultitaskRegressor
has NO batch-normalization support — its torch module is a plain Linear/dropout/activation stack.
Per the 2026-07-29 decision, batch_norm is accepted for config fidelity but IGNORED at fit time
with a warning (option A: thin wrapper, FCNN is a lower-rigor secondary model).

DeepChem/torch are imported lazily inside fit/predict — importing this class is cheap and does not
trigger DeepChem's noisy optional-dependency warnings.
"""

import multiprocessing
import warnings

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin

# fit() runs once per CV fold; with n_jobs=-1 each fold fits in a separate loky worker, so a plain
# warnings.warn fires ~16x per key (15 folds + 1 final fit) x every key. Emit only in the MAIN
# process (parent_process() is None there, non-None in workers) and only once per message, so a
# config-fidelity notice like batch_norm-ignored prints just once for the whole run.
_WARNED_ONCE = set()


def _warn_once(msg):
    if multiprocessing.parent_process() is None and msg not in _WARNED_ONCE:
        _WARNED_ONCE.add(msg)
        warnings.warn(msg, stacklevel=3)


class FCNN(BaseEstimator, RegressorMixin):
    """Feed-forward net matching the paper's FCNN, backed by DeepChem MultitaskRegressor.

    Hyperparameter names mirror param_base_FCNN so FCNN(**param_base_FCNN) works directly; they are
    mapped to MultitaskRegressor's argument names inside fit().
    """

    def __init__(self, hidden_layers=(512, 256, 64), dropout=(0.25, 0.25, 0.10),
                 lr=0.001, optimizer="adam", beta1=0.9, batch_norm=True, weight_decay=0.0004,
                 batch_size=128, activation="relu", epochs=50,
                 weight_init_stddevs=(0.02,), bias_init_consts=1.0, random_state=42):
        self.hidden_layers = hidden_layers
        self.dropout = dropout
        self.lr = lr
        self.optimizer = optimizer
        self.beta1 = beta1               # paper's Adam "alpha" == first-moment decay (beta1)
        self.batch_norm = batch_norm
        self.weight_decay = weight_decay
        self.batch_size = batch_size
        self.activation = activation
        self.epochs = epochs
        self.weight_init_stddevs = weight_init_stddevs
        self.bias_init_consts = bias_init_consts
        self.random_state = random_state

    def _weight_init_stddevs(self):
        # MultitaskRegressor wants a scalar or a length-(n_layers+1) list. The paper stores a
        # 1-element list [0.02] meaning "same value for every layer" — passing it verbatim would
        # collapse the network to a single layer (the internal zip stops at the shortest sequence),
        # so a 1-element list is flattened to the scalar.
        s = self.weight_init_stddevs
        if isinstance(s, (list, tuple, np.ndarray)):
            vals = [float(v) for v in s]
            return vals[0] if len(vals) == 1 else vals
        return float(s)

    def fit(self, X, y):
        import deepchem as dc
        import torch

        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32).reshape(-1, 1)

        if self.optimizer != "adam":
            _warn_once(f"FCNN: optimizer={self.optimizer!r} ignored; DeepChem's default (Adam) is used.")
        if self.batch_norm:
            _warn_once(
                "FCNN: batch_norm=True is ignored — DeepChem 2.8.0 MultitaskRegressor has no "
                "batch-normalization support (plain Linear/dropout/activation stack)."
            )

        np.random.seed(self.random_state)
        torch.manual_seed(self.random_state)

        # Build Adam explicitly so beta1 (the paper's "alpha") is set, not left implicit. weight
        # decay stays as MultitaskRegressor's L2 weight_decay_penalty (below), so Adam's own
        # weight_decay is left at 0 to avoid applying the penalty twice.
        adam = dc.models.optimizers.Adam(learning_rate=self.lr, beta1=self.beta1)
        self.n_features_in_ = X.shape[1]
        self.model_ = dc.models.MultitaskRegressor(
            n_tasks=1,
            n_features=self.n_features_in_,
            layer_sizes=list(self.hidden_layers),
            dropouts=list(self.dropout),
            activation_fns=self.activation,
            weight_init_stddevs=self._weight_init_stddevs(),
            bias_init_consts=self.bias_init_consts,
            weight_decay_penalty=self.weight_decay,
            weight_decay_penalty_type="l2",
            batch_size=self.batch_size,
            optimizer=adam,
        )
        self.model_.fit(dc.data.NumpyDataset(X=X, y=y), nb_epoch=self.epochs)
        return self

    def predict(self, X):
        import deepchem as dc

        X = np.asarray(X, dtype=np.float32)
        preds = self.model_.predict(dc.data.NumpyDataset(X=X))  # (n, n_tasks, 1)
        return np.asarray(preds).reshape(-1)
