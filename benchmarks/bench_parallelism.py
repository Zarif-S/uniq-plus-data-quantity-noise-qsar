"""A/B benchmark: single-layer parallelism layouts for paper-recreation tuning.

Runs the REAL tune_paper_model path on the worst-case unit (RLM | rdkit) for three
representative models and reports wall-clock per model + peak RAM across the whole
loky process tree. Both knobs are passed explicitly so hyperparams.py is never touched:

  Option A: --n-jobs-model 1  --n-jobs-cv 3   (outer owns cores, estimators serial)
  Option B: --n-jobs-model -1 --n-jobs-cv 1   (estimator owns cores, serial outer)

Usage:
  python bench_parallelism.py --n-jobs-model 1 --n-jobs-cv 3 --label A
"""
import argparse, json, os, sys, threading, time
from pathlib import Path

import joblib
import numpy as np
import psutil
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.linear_model import Lasso

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from src.models.paper_models import tune_paper_model
from src.hyperparams import param_base_RF, param_search_SVM, param_base_SVM, param_search_Lasso, param_base_Lasso

SPLITS = str(REPO_ROOT / "data/processed/section4_splits.pkl")

# RF: reduced grid that still contains the RAM-heavy corner (n_estimators=1000,
# max_features=None, max_depth=None). 8 combos x 5-fold = 40 fits.
RF_GRID = {"n_estimators": [250, 1000], "max_features": ["sqrt", None], "max_depth": [25, None]}


class PeakRAM:
    """Sample total RSS of this process + all descendants; track the max (MB)."""
    def __init__(self, interval=0.1):
        self.interval = interval
        self.peak = 0.0
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._run, daemon=True)

    def _sample(self):
        me = psutil.Process()
        procs = [me] + me.children(recursive=True)
        total = 0
        for p in procs:
            try:
                total += p.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return total / (1024 ** 2)

    def _run(self):
        while not self._stop.is_set():
            self.peak = max(self.peak, self._sample())
            time.sleep(self.interval)

    def __enter__(self):
        self._t.start(); return self

    def __exit__(self, *a):
        self._stop.set(); self._t.join()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-jobs-model", type=int, required=True)
    ap.add_argument("--n-jobs-cv", type=int, required=True)
    ap.add_argument("--label", required=True)
    args = ap.parse_args()

    d = joblib.load(SPLITS)[("RLM", "rdkit")]
    X, y = d["X_train"], d["y_train"]
    Xs = d["X_train_scaled"]  # SVM/Lasso want scaled features

    # RF params minus the file's n_jobs, so we set it explicitly per-run.
    rf_base = {k: v for k, v in param_base_RF.items() if k != "n_jobs"}

    jobs = [
        ("RF",    RandomForestRegressor(**rf_base, n_jobs=args.n_jobs_model, random_state=42), RF_GRID,          X,  y),
        ("SVM",   SVR(**param_base_SVM),                                                       param_search_SVM, Xs, y),
        ("Lasso", Lasso(**param_base_Lasso, random_state=42),                                  param_search_Lasso, Xs, y),
    ]

    results = {}
    for name, model, grid, Xin, yin in jobs:
        n_combos = int(np.prod([len(v) for v in grid.values()]))
        with PeakRAM() as ram:
            t0 = time.perf_counter()
            tune_paper_model(model, Xin, yin, stages=[grid], n_jobs_cv=args.n_jobs_cv, cv=5)
            dt = time.perf_counter() - t0
        results[name] = {"seconds": round(dt, 1), "peak_ram_mb": round(ram.peak), "combos": n_combos, "fits": n_combos * 5}
        print(f"[{args.label}] {name:6s} {dt:7.1f}s  peak {ram.peak:6.0f} MB  ({n_combos} combos x5)", flush=True)

    total_s = round(sum(r["seconds"] for r in results.values()), 1)
    overall_peak = max(r["peak_ram_mb"] for r in results.values())
    summary = {"label": args.label, "n_jobs_model": args.n_jobs_model, "n_jobs_cv": args.n_jobs_cv,
               "total_seconds": total_s, "overall_peak_ram_mb": overall_peak, "per_model": results}
    print("RESULT_JSON " + json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
