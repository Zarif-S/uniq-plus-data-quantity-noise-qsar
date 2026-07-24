############################################
# set up Hyperparameter search space, based off ADME_ML_public.py
############################################

# n_jobs_cv (CV/GridSearchCV parallelism) is set per-notebook instead
n_jobs_model = -1

# set up Random Forest parameters

param_base_RF ={'n_estimators': 500, 'oob_score':True,'n_jobs':n_jobs_model}
param_search_RF = {'n_estimators': [100, 250, 500, 750, 1000],
                 'max_features':['sqrt',0.33,0.67, None],
                 'max_depth': [15, 25, 40, None]} # 5*4*4 =80

# set up SVM parameters
param_base_SVM ={'gamma':'scale'}
param_search_SVM = {'C':[0.1, 1, 5, 10, 20, 50],
                  'epsilon':[1e-2, 1e-1, 0.3,0.5],
                  'gamma':['scale','auto']} # 6*5 = 30

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
param_base_LGB = {'n_estimators': 500, 'subsample':0.8, 'colsample_bytree':0.8,'subsample_freq':1}
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
PARAM_GRID_STAGES = {
    "RF":       [param_search_RF],
    "SVM":      [param_search_SVM],
    "XGBoost":  [param_search1_XGB, param_search2_XGB, param_search3_XGB, param_search4_XGB, param_search5_XGB],
    "LightGBM": [param_search1_LGB, param_search2_LGB, param_search3_LGB, param_search4_LGB],
    "Lasso":    [param_search_Lasso],
}

# Need to incude MPNN and FCNN, note could not find MPNN hyperparams, MPNN, could find but doesnt quite match up with code and S15 table and /FCNN_public.py
