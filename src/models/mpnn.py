"""sklearn-compatible ChemProp D-MPNN regressor wrapping ChemProp 1.6.1's Python API.

One class, two configurations via `use_features`:
  MPNN1 (use_features=False): graph only.
  MPNN2 (use_features=True):  graph + external precomputed features — our scaled rmoldes (316),
                              passed via --features_path with --no_features_scaling (they are
                              already RobustScaler'd upstream). This reuses the 'rdkit' featureset
                              and deviates from the paper's rdkit_2d_normalized generator
                              (2026-07-29 decision).

Validation: the paper's MPNN_public.py did a single split / no CV. We instead run this wrapper
through the project's model_validation() so MPNN gets a CV distribution like the other models —
Full (5x3) or Sample (3x1) selected by the notebook's MPNN_CV flag (which just sets
model_validation's n_splits/n_repeats). Each fit() is ONE ChemProp training (num_folds=1, with
ChemProp's own internal train/val split for early stopping).

X encoding — so sklearn cross_val_score can row-split it while keeping SMILES aligned with features:
  use_features=False: X is (n, 1),   column 0 = SMILES.
  use_features=True:  X is (n, 1+F) object array; column 0 = SMILES, columns 1: = float features.

ChemProp/torch are imported lazily inside fit/predict so importing this class is cheap and quiet.
"""

import csv
import os
import shutil
import tempfile

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin


class ChempropRegressor(BaseEstimator, RegressorMixin):
    """ChemProp D-MPNN as a scikit-learn regressor. Hyperparameter names mirror param_base_MPNN."""

    def __init__(self, hidden_size=300, depth=3, dropout=0.0, ffn_num_layers=2,
                 epochs=30, use_features=False, metric="r2", random_state=42):
        self.hidden_size = hidden_size
        self.depth = depth
        self.dropout = dropout
        self.ffn_num_layers = ffn_num_layers
        self.epochs = epochs
        self.use_features = use_features
        self.metric = metric
        self.random_state = random_state

    def _split_X(self, X):
        X = np.asarray(X, dtype=object)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        smiles = [str(s) for s in X[:, 0]]
        feats = X[:, 1:].astype(np.float64) if self.use_features else None
        return smiles, feats

    @staticmethod
    def _write_data_csv(path, smiles, y=None):
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["smiles", "target"] if y is not None else ["smiles"])
            if y is not None:
                for smi, yi in zip(smiles, y):
                    w.writerow([smi, float(yi)])
            else:
                for smi in smiles:
                    w.writerow([smi])

    def fit(self, X, y):
        from chemprop.args import TrainArgs
        from chemprop.train import cross_validate, run_training

        smiles, feats = self._split_X(X)
        y = np.asarray(y, dtype=float)

        self.save_dir_ = tempfile.mkdtemp(prefix="chemprop_fit_")
        train_csv = os.path.join(self.save_dir_, "train.csv")
        self._write_data_csv(train_csv, smiles, y)

        args = [
            "--data_path", train_csv,
            "--dataset_type", "regression",
            "--save_dir", self.save_dir_,
            "--hidden_size", str(self.hidden_size),
            "--depth", str(self.depth),
            "--dropout", str(self.dropout),
            "--ffn_num_layers", str(self.ffn_num_layers),
            "--epochs", str(self.epochs),
            "--metric", self.metric,
            "--num_folds", "1",
            "--seed", str(self.random_state),
            "--pytorch_seed", str(self.random_state),
            # num_workers=0: no DataLoader worker processes. Required — worker spawn breaks under
            # Jupyter / stdin and would nest inside sklearn CV's own joblib parallelism.
            "--num_workers", "0",
            "--quiet",
        ]
        if self.use_features:
            feats_path = os.path.join(self.save_dir_, "train_feats.npz")
            np.savez(feats_path, features=feats)
            args += ["--features_path", feats_path, "--no_features_scaling"]

        cross_validate(args=TrainArgs().parse_args(args), train_func=run_training)
        return self

    def predict(self, X):
        from chemprop.args import PredictArgs
        from chemprop.train import make_predictions

        smiles, feats = self._split_X(X)
        pred_dir = tempfile.mkdtemp(prefix="chemprop_pred_")
        try:
            test_csv = os.path.join(pred_dir, "test.csv")
            preds_csv = os.path.join(pred_dir, "preds.csv")
            self._write_data_csv(test_csv, smiles)

            args = [
                "--test_path", test_csv,
                "--preds_path", preds_csv,
                "--checkpoint_dir", self.save_dir_,
                "--num_workers", "0",
            ]
            if self.use_features:
                feats_path = os.path.join(pred_dir, "test_feats.npz")
                np.savez(feats_path, features=feats)
                args += ["--features_path", feats_path, "--no_features_scaling"]

            raw = make_predictions(args=PredictArgs().parse_args(args))
            # make_predictions returns one list per molecule; invalid SMILES yield the string
            # 'Invalid SMILES' — the ADME set is pre-cleaned, so we expect all floats.
            return np.array([p[0] for p in raw], dtype=float)
        finally:
            shutil.rmtree(pred_dir, ignore_errors=True)

    def __del__(self):
        # best-effort cleanup of the fitted-model temp dir (bounded disk use across CV folds)
        shutil.rmtree(getattr(self, "save_dir_", ""), ignore_errors=True)
