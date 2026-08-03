"""FCNN CPU-vs-MPS benchmark: does the M4 GPU help the one DNN that can reach it?

Builds the paper's FCNN architecture (param_base_FCNN) as a DeepChem MultitaskRegressor and
fits it on the real RLM|rdkit scaled matrix once per device, timing each. This is the tractable
GPU test (the ChemProp MPNN cannot reach MPS on 1.6.1). Reports wall-clock per device and a
prediction sanity check so we know MPS isn't silently producing garbage.
"""
import sys, time
import joblib
import numpy as np

sys.path.insert(0, "/Users/zarif/Documents/Projects/uniq-plus-data-quantity-noise-qsar")
from src.hyperparams import param_base_FCNN

SPLITS = "/Users/zarif/Documents/Projects/uniq-plus-data-quantity-noise-qsar/data/processed/section4_splits.pkl"


def build_and_fit(X, y, device_str, epochs):
    import deepchem as dc
    import torch

    np.random.seed(42)
    torch.manual_seed(42)
    p = param_base_FCNN
    adam = dc.models.optimizers.Adam(learning_rate=p["lr"], beta1=p["beta1"])
    kwargs = dict(
        n_tasks=1, n_features=X.shape[1],
        layer_sizes=list(p["hidden_layers"]), dropouts=list(p["dropout"]),
        activation_fns=p["activation"],
        weight_init_stddevs=float(p["weight_init_stddevs"][0]),
        bias_init_consts=1.0,
        weight_decay_penalty=p["weight_decay"], weight_decay_penalty_type="l2",
        batch_size=p["batch_size"], optimizer=adam,
    )
    if device_str is not None:
        kwargs["device"] = torch.device(device_str)
    model = dc.models.MultitaskRegressor(**kwargs)
    ds = dc.data.NumpyDataset(X=X, y=y)
    t0 = time.perf_counter()
    model.fit(ds, nb_epoch=epochs)
    dt = time.perf_counter() - t0
    # report the device the model actually landed on
    actual = str(getattr(model, "device", "unknown"))
    preds = np.asarray(model.predict(dc.data.NumpyDataset(X=X))).reshape(-1)
    return dt, actual, preds


def main():
    epochs = int(sys.argv[1]) if len(sys.argv) > 1 else param_base_FCNN["epochs"]
    d = joblib.load(SPLITS)[("RLM", "rdkit")]
    X = np.asarray(d["X_train_scaled"], dtype=np.float32)
    y = np.asarray(d["y_train"], dtype=np.float32).reshape(-1, 1)
    print(f"X {X.shape} {X.dtype} | epochs={epochs} | arch={param_base_FCNN['hidden_layers']}", flush=True)

    results = {}
    for label, dev in [("cpu", "cpu"), ("mps", "mps")]:
        try:
            dt, actual, preds = build_and_fit(X, y, dev, epochs)
            results[label] = {"seconds": round(dt, 1), "device": actual,
                              "pred_mean": float(np.mean(preds)), "pred_std": float(np.std(preds))}
            print(f"[{label}] {dt:7.1f}s  device={actual}  pred mean={np.mean(preds):.3f} std={np.std(preds):.3f}", flush=True)
        except Exception as e:
            results[label] = {"error": f"{type(e).__name__}: {e}"}
            print(f"[{label}] FAILED  {type(e).__name__}: {e}", flush=True)

    if "cpu" in results and "seconds" in results["cpu"] and "mps" in results and "seconds" in results["mps"]:
        sp = results["cpu"]["seconds"] / results["mps"]["seconds"]
        print(f"\nMPS speedup vs CPU: {sp:.2f}x", flush=True)
        # prediction agreement (same seed/arch; devices should give near-identical preds)
        print("pred agreement: cpu_mean=%.3f mps_mean=%.3f" % (results["cpu"]["pred_mean"], results["mps"]["pred_mean"]), flush=True)
    import json
    print("RESULT_JSON " + json.dumps(results), flush=True)


if __name__ == "__main__":
    main()
