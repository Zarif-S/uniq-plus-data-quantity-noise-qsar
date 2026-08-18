"""Descriptor-level feature selection for the rdmoldes 50-descriptor / 316-feature set.

`rdmoldes()` (src/features) expands 50 named descriptors into 316 numeric features —
44 scalar descriptors (1 feature each) plus 6 vector descriptors (e.g. AUTOCORR2D -> 192
features). Selection here operates at the descriptor level: a vector descriptor is kept or
dropped as a whole, never split across its own features.

Pipeline (see notebooks/01.8_feature_selection.ipynb for the full run):
    1. drop_constant_descriptors    - remove degenerate (near-zero-variance) descriptors
    2. descriptor_component_matrix  - reduce each descriptor to its top principal components
    3. mutual_info_per_descriptor   - MI(descriptor, endpoint), max'd across endpoints
    4. correlation_prune            - drop redundant near-duplicate descriptors (MI tiebreak)
    5. vif_prune                    - drop multicollinear descriptors (MI tiebreak)
    6. run_descriptor_rfe           - LightGBM-based recursive descriptor elimination, with
                                       a per-step CV score trace for the caller to inspect
"""

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.cross_decomposition import CCA
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_regression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

from src.hyperparams import n_jobs_model, n_jobs_cv

# (descriptor_name, n_features), in the exact order rdmoldes() concatenates them.
RDMOLDES_DESCRIPTORS = [
    ("CalcTPSA", 1), ("CalcFractionCSP3", 1), ("CalcNumAliphaticCarbocycles", 1),
    ("CalcNumAliphaticHeterocycles", 1), ("CalcNumAliphaticRings", 1), ("CalcNumAmideBonds", 1),
    ("CalcNumAromaticCarbocycles", 1), ("CalcNumAromaticHeterocycles", 1), ("CalcNumAromaticRings", 1),
    ("CalcNumLipinskiHBA", 1), ("CalcNumLipinskiHBD", 1), ("CalcNumHeteroatoms", 1),
    ("CalcNumRings", 1), ("CalcNumRotatableBonds", 1), ("CalcNumSaturatedCarbocycles", 1),
    ("CalcNumSaturatedHeterocycles", 1), ("CalcNumSaturatedRings", 1), ("CalcHallKierAlpha", 1),
    ("CalcKappa1", 1), ("CalcKappa2", 1), ("CalcKappa3", 1),
    ("CalcChi0n", 1), ("CalcChi0v", 1), ("CalcChi1n", 1), ("CalcChi1v", 1),
    ("CalcChi2n", 1), ("CalcChi2v", 1), ("CalcChi3n", 1), ("CalcChi3v", 1),
    ("CalcChi4n", 1), ("CalcChi4v", 1),
    ("CalcAsphericity", 1), ("CalcEccentricity", 1), ("CalcInertialShapeFactor", 1),
    ("CalcExactMolWt", 1), ("CalcPBF", 1), ("CalcPMI1", 1), ("CalcPMI2", 1), ("CalcPMI3", 1),
    ("CalcRadiusOfGyration", 1), ("CalcSpherocityIndex", 1), ("CalcLabuteASA", 1),
    ("CalcNPR1", 1), ("CalcNPR2", 1),
    ("PEOE_VSA", 14), ("SMR_VSA", 10), ("SlogP_VSA", 12),
    ("MQNs", 42), ("CrippenDescriptors", 2), ("AUTOCORR2D", 192),
]


def rdmoldes_descriptor_map():
    """Return {descriptor_name: [feature indices]} for the 316-feature rdmoldes() output, in order."""
    descriptor_map = {}
    start = 0
    for name, n_features in RDMOLDES_DESCRIPTORS:
        descriptor_map[name] = list(range(start, start + n_features))
        start += n_features
    return descriptor_map


def drop_constant_descriptors(X, descriptor_map, threshold=1e-8):
    """Return (kept_descriptor_map, dropped_names) after removing descriptors constant across all rows.

    A descriptor is dropped only if every one of its features has variance <= threshold —
    a descriptor with even one informative feature is kept whole.
    """
    dropped = []
    kept = {}
    for name, features in descriptor_map.items():
        variances = np.var(X[:, features], axis=0)
        if np.all(variances <= threshold):
            dropped.append(name)
        else:
            kept[name] = features
    return kept, dropped


def descriptor_component_matrix(X, descriptor_map, n_components=5, random_state=42):
    """Reduce each descriptor to its top principal components (z-scored beforehand).

    A descriptor with fewer features than n_components uses all of them (e.g. the 44
    scalar descriptors always reduce to 1 component, their own z-scored value). Used for
    MI and correlation-pruning, which need to judge a multi-feature descriptor (e.g.
    AUTOCORR2D, 192 features) by more than just its single dominant axis — collapsing
    straight to PC1 would judge a descriptor's relevance/redundancy on one coincidental
    axis and could discard real signal living in its other components.

    Returns {descriptor_name: np.ndarray (n_rows, k)}.
    """
    components = {}
    for name, features in descriptor_map.items():
        block_X = StandardScaler().fit_transform(X[:, features])
        k = min(n_components, block_X.shape[1])
        components[name] = PCA(n_components=k, random_state=random_state).fit_transform(block_X)
    return components


def descriptor_pc1_matrix(component_map):
    """First component of each descriptor as a single DataFrame — used for VIF.

    VIF is inherently a single-variable-vs-the-rest statistic (R² of one variable
    regressed on all others), so unlike MI/correlation it can't be generalised to a
    descriptor's full component set without changing what VIF means; PC1 is deliberately
    kept here rather than extended.
    """
    return pd.DataFrame({name: comps[:, 0] for name, comps in component_map.items()})


def _canonical_correlation(A, B):
    """First canonical correlation coefficient between two (possibly multi-feature) descriptors.

    Known limitation: CCA only finds the strongest *linear* combination correlation
    between the two component sets, so purely nonlinear (but real) dependence between two
    descriptors would be missed here and the pair could survive correlation_prune as
    "not redundant" when it actually is. A distance-correlation-style measure (dCor= 0 iff
    truly independent, linear or not) would close this gap, at the cost of a new
    dependency and O(n^2) compute. Not adopted here since VIF and the RFE/R^2 audit
    downstream both re-check whatever this step decides against real model performance,
    so a wrong call here isn't silently trusted.
    """
    k = min(A.shape[1], B.shape[1])
    cca = CCA(n_components=k)
    A_c, B_c = cca.fit_transform(A, B)
    return abs(np.corrcoef(A_c[:, 0], B_c[:, 0])[0, 1])


def mutual_info_per_descriptor(component_map, y_by_endpoint, random_state=42):
    """MI(descriptor, endpoint), using the max MI across a descriptor's own top components,
    then the max across endpoints.

    y_by_endpoint: {endpoint_name: pd.Series} — each Series' index is that endpoint's own
    non-NaN rows, positionally aligned to the rows used to build component_map (a subset
    of range(n_rows)). A descriptor is scored by whichever (component, endpoint) pair it
    is most informative for — so a descriptor isn't underrated just because its dominant
    component (PC1) happens to be uninformative while a later component isn't.

    Returns (mi_max: pd.Series indexed by descriptor name, mi_table: pd.DataFrame descriptor x endpoint).
    """
    names = list(component_map.keys())
    mi_by_endpoint = {}
    for endpoint, y in y_by_endpoint.items():
        idx = y.index.values
        scores = {}
        for name in names:
            mi_vals = mutual_info_regression(component_map[name][idx], y.values, random_state=random_state)
            scores[name] = mi_vals.max()
        mi_by_endpoint[endpoint] = pd.Series(scores)
    mi_table = pd.DataFrame(mi_by_endpoint)
    return mi_table.max(axis=1), mi_table


def correlation_prune(component_map, mi_scores, threshold=0.9):
    """Drop one descriptor from each near-duplicate pair, keeping the higher-MI descriptor.

    Redundancy between two descriptors is judged by the first canonical correlation
    between their top-component sets (not a single PC1-to-PC1 Pearson r) — a multi-feature
    descriptor like AUTOCORR2D isn't judged redundant just because its dominant axis
    happens to correlate with another descriptor's dominant axis.

    Returns (kept_descriptor_names, dropped_records) where dropped_records is a list of
    dicts {dropped, kept_instead, canonical_corr} for transparency.

    Known limitation: canonical correlation only captures linear association; see
    _canonical_correlation's docstring for why that's an acceptable tradeoff here.
    """
    names = list(component_map.keys())
    alive = set(names)
    dropped_records = []

    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            r = _canonical_correlation(component_map[a], component_map[b])
            if r > threshold:
                pairs.append((r, a, b))
    pairs.sort(reverse=True)  # most-correlated pairs decided first

    for r, a, b in pairs:
        if a not in alive or b not in alive:
            continue
        loser, winner = (a, b) if mi_scores[a] < mi_scores[b] else (b, a)
        alive.discard(loser)
        dropped_records.append({"dropped": loser, "kept_instead": winner, "canonical_corr": r})

    return [n for n in names if n in alive], dropped_records


def vif_prune(pc1_df, mi_scores, threshold=5.0, tie_margin=0.05):
    """Iteratively drop the highest-VIF descriptor until all remaining are <= threshold.

    On each iteration, descriptors within `tie_margin` (relative) of the max VIF are
    treated as tied, and the lowest-MI one among them is dropped — MI breaks the tie, VIF
    alone does not decide it.

    Returns (kept_descriptor_names, trace) where trace is a list of dicts
    {dropped, vif, mi, remaining} logging each removal.
    """
    remaining = list(pc1_df.columns)
    trace = []
    while len(remaining) > 1:
        X = pc1_df[remaining].values
        vifs = pd.Series(
            [variance_inflation_factor(X, i) for i in range(X.shape[1])],
            index=remaining,
        )
        max_vif = vifs.max()
        if max_vif <= threshold:
            break
        candidates = vifs[vifs >= max_vif * (1 - tie_margin)].index
        to_drop = mi_scores[candidates].idxmin()
        trace.append({
            "dropped": to_drop,
            "vif": vifs[to_drop],
            "mi": mi_scores[to_drop],
            "remaining": len(remaining) - 1,
        })
        remaining.remove(to_drop)
    return remaining, trace


def vif_mi_table(pc1_df, mi_scores):
    """Diagnostic table combining VIF and MI for every descriptor currently in pc1_df, side by side.

    Unlike vif_prune (which only ever reports the descriptor it's about to drop, one at a
    time), this computes VIF for the *whole* surviving set at once so MI and VIF can be
    eyeballed together before any elimination happens — same idea as manually
    cross-referencing "high VIF" against "high importance" before deciding what to cut.

    Returns a DataFrame indexed by descriptor name, columns [mi, mi_rank, vif, vif_elim_rank],
    sorted by mi_rank (most important first). vif_elim_rank=1 is the descriptor that would
    be eliminated first (highest VIF).
    """
    names = list(pc1_df.columns)
    X = pc1_df.values
    vif = pd.Series(
        [variance_inflation_factor(X, i) for i in range(X.shape[1])],
        index=names,
    )
    table = pd.DataFrame({"mi": mi_scores[names], "vif": vif})
    table["mi_rank"] = table["mi"].rank(ascending=False)
    table["vif_elim_rank"] = table["vif"].rank(ascending=False)
    return table.sort_values("mi_rank")


def evaluate_descriptor_set(X_by_endpoint, y_by_endpoint, descriptor_map, descriptors, cv=5, random_state=42, estimator_factory=None):
    """Mean (and per-endpoint) CV R² for a given descriptor subset's real features.

    Used to audit how much each pruning stage actually costs in downstream model
    performance — descriptor/feature counts alone don't say whether a stage removed
    mostly redundant signal or something that mattered.
    """
    if estimator_factory is None:
        estimator_factory = lambda: LGBMRegressor(n_estimators=200, random_state=random_state, verbose=-1, n_jobs=n_jobs_model)
    features = sorted(f for name in descriptors for f in descriptor_map[name])
    kf = KFold(n_splits=cv, shuffle=True, random_state=random_state)
    X_sub_by_endpoint = {ep: X[:, features] for ep, X in X_by_endpoint.items()}
    scores = _cv_score_by_endpoint(X_sub_by_endpoint, y_by_endpoint, estimator_factory, kf, "r2")
    scores["mean"] = float(np.mean(list(scores.values())))
    return scores


def _cv_score_by_endpoint(X_by_endpoint, y_by_endpoint, estimator_factory, cv, scoring):
    # n_jobs=n_jobs_cv (1): the estimator itself owns all cores (n_jobs_model=-1 in the
    # factories above) -- one parallelism layer only, per src/hyperparams's oversubscription note.
    scores = {}
    for endpoint, X in X_by_endpoint.items():
        y = y_by_endpoint[endpoint]
        scores[endpoint] = cross_val_score(
            estimator_factory(), X, y, cv=cv, scoring=scoring, n_jobs=n_jobs_cv
        ).mean()
    return scores


def run_descriptor_rfe(
    X_by_endpoint,
    y_by_endpoint,
    descriptor_map,
    min_descriptors=5,
    cv=5,
    scoring="r2",
    random_state=42,
    estimator_factory=None,
):
    """Recursive descriptor elimination: drop the least-useful descriptor one at a time, tracking CV score.

    At each step, fits one LightGBM per endpoint on the currently-included features (full
    features of surviving descriptors, not PC1), takes each descriptor's SUMMED feature
    gain-importance per endpoint (total loss reduction credited to the descriptor's whole
    column block, not just its single best-performing column), then the max across
    endpoints as that descriptor's overall importance for this step (a descriptor is
    "useful" if useful for any endpoint) — and eliminates the lowest-scoring descriptor.
    CV score (mean across endpoints) is recorded before each removal so the caller can
    inspect the score-vs-n_descriptors trace and pick a cutoff, rather than this function
    silently deciding a fixed target size.

    Why sum(), not max(), across a descriptor's own columns: an earlier version used
    max(), which credits a wide descriptor (e.g. PEOE_VSA, 14 columns) only for its single
    best-performing column, while a scalar descriptor's entire gain is concentrated
    (undivided) in its one column. When a wide descriptor's real signal is spread across
    several correlated columns, max() structurally underrates the whole block relative to
    a scalar — this was empirically confirmed to be exactly what happened here: with
    max(), RFE's own tail-end trace (N<=5) eliminated PEOE_VSA/SlogP_VSA — the two
    strongest descriptors in the entire candidate pool by standalone R² — before weaker
    scalars, producing a spurious N=2 floor (R^2=0.066, barely above noise). Switching to
    sum() makes RFE's own trace converge directly on {PEOE_VSA, SlogP_VSA} at N=2
    (R^2=0.346) with a flat, noise-floor-only decline from N=5 to N=2 and a single real
    elbow at N=2->1 — matching what a separate standalone-ranking workaround
    (notebooks/01.8_feature_selection.ipynb §8b) previously had to be built to recover.
    See src/feature_selection/CLAUDE.md for the full max-vs-sum trace comparison.

    X_by_endpoint / y_by_endpoint: {endpoint_name: array/Series}, one X per endpoint since
    each endpoint has its own non-NaN row subset. All X arrays must have the full
    316-feature layout described by `descriptor_map`.

    Returns trace: list of dicts, one per step (including the starting full-descriptor
    step), each {n_descriptors, descriptors, cv_score_by_endpoint, cv_score_mean,
    dropped}. `dropped` is None on the first (no-elimination-yet) row.
    """
    if estimator_factory is None:
        # importance_type='gain' -- LGBMRegressor defaults to 'split' (raw split counts),
        # which is not what the elimination step below or its docstring describe.
        estimator_factory = lambda: LGBMRegressor(n_estimators=200, random_state=random_state, verbose=-1, importance_type='gain', n_jobs=n_jobs_model)

    remaining = list(descriptor_map.keys())
    kf = KFold(n_splits=cv, shuffle=True, random_state=random_state)
    trace = []
    dropped_name = None

    while True:
        features = sorted(f for name in remaining for f in descriptor_map[name])
        X_sub_by_endpoint = {ep: X[:, features] for ep, X in X_by_endpoint.items()}
        cv_scores = _cv_score_by_endpoint(X_sub_by_endpoint, y_by_endpoint, estimator_factory, kf, scoring)
        trace.append({
            "n_descriptors": len(remaining),
            "descriptors": list(remaining),
            "cv_score_by_endpoint": cv_scores,
            "cv_score_mean": float(np.mean(list(cv_scores.values()))),
            "dropped": dropped_name,
        })

        if len(remaining) <= min_descriptors:
            break

        # Descriptor importance for this step: summed feature gain per endpoint (total
        # loss reduction credited to the whole descriptor block), then max across endpoints.
        importance = pd.Series(0.0, index=remaining)
        for endpoint, X in X_sub_by_endpoint.items():
            model = estimator_factory()
            model.fit(X, y_by_endpoint[endpoint])
            gains = pd.Series(model.feature_importances_, index=features)
            for name in remaining:
                gain = gains[descriptor_map[name]].sum()
                importance[name] = max(importance[name], gain)

        dropped_name = importance.idxmin()
        remaining = [n for n in remaining if n != dropped_name]

    return trace
