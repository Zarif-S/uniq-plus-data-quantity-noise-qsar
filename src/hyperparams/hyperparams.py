############################################
# set up Hyperparameter search space, based off ADME_ML_public.py
############################################

# Estimator-level parallelism. -1 = the estimator owns all cores; the outer GridSearchCV /
# cross_val_score runs ONE fit at a time (n_jobs_cv=1 per-notebook). One parallelism layer only —
# never nest two parallel layers (that oversubscribes: ~64 threads on 8 cores). This layout (Option
# B) is the chosen one; see ADR-008's 2026-08-02 update for the head-to-head benchmark: it is ~2.1x
# FASTER than the inverse (outer=-1, estimator=1) on the tree-heavy grid, because forests parallelise
# within a fit better than across folds. (It also uses LESS peak RAM — 610 vs 1324 MB measured — but
# RAM was never the deciding factor: the ~98 GB scare was swap from a stale overlapping run + sleep,
# not the layout.) Never affects results — a fidelity-neutral wall-clock knob. If a notebook ever
# sets n_jobs_cv=-1, this MUST become 1 in the same change (the oversubscription trap).
n_jobs_model = -1

# Outer-CV / GridSearchCV parallelism. This is the SINGLE SOURCE OF TRUTH for both parallelism knobs
# (n_jobs_model + n_jobs_cv) — the notebook imports these rather than redefining them, so the two can
# never drift out of sync. Option B requires n_jobs_cv=1 whenever n_jobs_model=-1: the estimator owns
# all cores and the outer loop runs serially = one parallelism layer only. If you ever flip to
# n_jobs_cv=-1, n_jobs_model MUST become 1 in the same change (the oversubscription trap).
n_jobs_cv = 1

# set up Random Forest parameters

# oob_score=False: tuning selects on CV R2 and eval reports Pearson r; .oob_score_ is never read
# anywhere, so computing it only adds a redundant out-of-bag prediction pass to every forest fit.
param_base_RF = {'n_estimators': 500, 'oob_score': False, 'n_jobs': n_jobs_model}
param_search_RF = {'n_estimators': [100, 250, 500, 750, 1000],
                 'max_features':['sqrt',0.33,0.67, None],
                 'max_depth': [15, 25, 40, None]} # 5*4*4 =80

# set up SVM parameters
param_base_SVM ={'gamma':'scale'}
param_search_SVM = {'C':[0.1, 1, 5, 10, 20, 50],
                  'epsilon':[1e-2, 1e-1, 0.3,0.5],
                  'gamma':['scale','auto']} # 48 total

# set up XGBoost parameters (5+15+3+25+25=73)
param_base_XGB = {'n_estimators': 500, 'subsample':0.8, 'colsample_bytree':0.8, 'n_jobs':n_jobs_model}
param_search1_XGB = {'n_estimators':[100, 250, 500, 750, 1000]} # 5
param_search2_XGB ={'max_depth':[3,4,5,6,7],'min_child_weight': [1,2,3]} # 5*3 =15
param_search3_XGB = {'gamma':[0, 0.05, 0.1]} # 3
param_search4_XGB = {'subsample':[0.6, 0.7, 0.8, 0.9, 1.0],'colsample_bytree':[0.6, 0.7, 0.8, 0.9, 1.0]} # 5*5 =25
param_search5_XGB = {'reg_alpha':[0, 0.1, 0.2, 0.3, 0.4], 'reg_lambda':[1, 1.1, 1.2, 1.3, 1.4]} # 5*5 =25

param_search_XGB = {'n_estimators':[100, 250, 500, 750, 1000],
                    'max_depth':[3,4,5,6,7],'min_child_weight': [1,2,3],
                    'gamma':[0, 0.05, 0.1],
                    'subsample':[0.6, 0.7, 0.8, 0.9, 1.0],'colsample_bytree':[0.6, 0.7, 0.8, 0.9, 1.0],
                    'reg_alpha':[0, 0.1, 0.2, 0.3, 0.4], 'reg_lambda':[1, 1.1, 1.2, 1.3, 1.4]}

# Confirmed by reading the paper's ADME_ML_public.py 'optimization' workflow directly:
# param_search1_XGB..5_XGB (and param_search1_LGB..4_LGB below) are the paper's REAL sequential
# tuning stages — each is a separate GridSearchCV(cv=5, scoring='r2') call on one parameter
# group, with model.set_params(**best_params_) locking in the winner before the next stage runs
# (classic greedy/staged XGBoost tuning: n_estimators, then max_depth+min_child_weight, then
# gamma, then sampling params, then regularization). param_search_XGB (this combined dict) is
# NEVER referenced anywhere in the paper's script — it appears to be dead code left over from an
# earlier, simpler (all-at-once) tuning approach that was superseded by the staged strategy and
# never removed. We don't use it for tuning either; kept only for reference.

# set up LightGBM parameters (5+20+100+16 =141)
# n_jobs=n_jobs_model (1): LightGBM's default (n_jobs=None) uses all cores, so without this it would
# oversubscribe exactly like RF/XGB when nested inside GridSearchCV/cross_val_score (n_jobs_cv=-1).
param_base_LGB = {'n_estimators': 500, 'subsample': 0.8, 'colsample_bytree': 0.8, 'subsample_freq': 1, 'n_jobs': n_jobs_model}
param_search1_LGB = {'n_estimators':[100, 250, 500, 750, 1000]} # 5
param_search2_LGB = {'num_leaves':[15, 31, 45, 60, 75],'min_child_samples':[10, 20, 30, 40]}  # 5* 4 = 20
param_search3_LGB = {'subsample':[0.6, 0.7, 0.8, 0.9, 1.0], 'colsample_bytree':[0.6, 0.7, 0.8, 0.9, 1.0], 'subsample_freq': [0,1,3,5]} # 5*5*4 =100
param_search4_LGB = {'reg_alpha':[0, 0.2, 0.5, 0.8], 'reg_lambda':[0, 0.2, 0.5, 0.8]}  # 4*4 = 16

param_search_LGB = {'n_estimators':[100, 250, 500, 750, 1000],
                     'num_leaves':[15, 31, 45, 60, 75],'min_child_samples':[10, 20, 30, 40],
                     'subsample':[0.6, 0.7, 0.8, 0.9, 1.0],'colsample_bytree':[0.6, 0.7, 0.8, 0.9, 1.0],'subsample_freq': [0,1,3,5],
                     'reg_alpha':[0, 0.2, 0.5, 0.8], 'reg_lambda':[0, 0.2, 0.5, 0.8]}
# param_search_LGB (combined) is likewise never referenced in the paper's script — same dead-code
# situation as param_search_XGB above; param_search1_LGB..4_LGB are the real staged grids used.

# set up Lasso parameters (9)
param_base_Lasso = {'alpha': 0.1}
param_search_Lasso = {'alpha':[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5]}  # 9

# Ordered sequential tuning stages per model, consumed by src.models.tune_paper_model.
# RF/SVM/Lasso tune in a single GridSearchCV pass; XGBoost/LightGBM tune in staged passes,
# each stage locking in its best_params_ before the next stage runs (matches the paper exactly).

param_base_BayesianRidge = {}

param_base_MPNN = {'hidden_size': 300, 'depth': 3, 'dropout': 0.0, 'ffn_num_layers': 2}

# 'beta1': the paper's Adam "alpha" (0.9) == first-moment/momentum decay (beta1); beta2 left at
# DeepChem's 0.999 default. 'batch_norm' is recorded for fidelity but unsupported by DeepChem's
# MultitaskRegressor (ignored with a warning — see src/models/fcnn.py).
param_base_FCNN = {'hidden_layers': [512, 256, 64], 'dropout': [0.25, 0.25, 0.10], 'lr': 0.001, 'optimizer': 'adam', 'beta1': 0.9, 'batch_norm': True, 'weight_decay': 0.0004, 'batch_size': 128, 'activation': 'relu', 'epochs': 50, 'weight_init_stddevs': [0.02]}

# did i implement weight_init_stddevs correctly?

# MPNN hyperparameters: They used chemprops default hyperopts search space as MPNN S14 matches exactly with the defaults
# Below not required
# param_search1_MPNN = {'hidden_size':[300, 400, ...., 2400]} # ?
# param_search2_MPNN = {'depth':[2, 3, 4, 5, 6]}  # ? * 5 = ?
# param_search3_MPNN = {'FFN_number_of_layers':[1, 2, 3]} # ?*5*3 = ?
# param_search4_MPNN = {'dropout':[0, 0.05, ..., 0.4]}  # ?*5*3* = ?

FCNN_ARCHITECTURES = {1: ([512,256,64], [0.25,0.25,0.10]), 2: ([1000,500], [0.25,0.10]), 3: ([2000,1000], [0.25,0.10]), 4: ([200,100,50], [0.25,0.25,0.10]), 5: ([4000,2000,1000,1000], [0.25,0.25,0.25,0.10])}

PARAM_GRID_STAGES = {
    "RF":       [param_search_RF],
    "SVM":      [param_search_SVM],
    "XGBoost":  [param_search1_XGB, param_search2_XGB, param_search3_XGB, param_search4_XGB, param_search5_XGB],
    "LightGBM": [param_search1_LGB, param_search2_LGB, param_search3_LGB, param_search4_LGB],
    "Lasso":    [param_search_Lasso],
}

# MPNN hyperparams: chemprop defaults: hidden_size=300, depth=3, dropout=0.0, ffn_num_layers=2
# 
