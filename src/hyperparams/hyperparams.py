############################################
# set up Hyperparameter search space, based off ADME_ML_public.py
############################################
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

# Note not sure why param_search1_XGB, param_search2_XGB etc is duplicated with param_search_XGB, 
# but keeping both for now to avoid breaking anything, might be just to initialise the models, 
# noticed some deafults missing from table s14 for the models but likely not an issue.

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

# set up Lasso parameters (9)
param_base_Lasso = {'alpha': 0.1}
param_search_Lasso = {'alpha':[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5]}  # 9


# Need to incude MPNN and FCNN, note could not find MPNN hyperparams, MPNN, could find but doesnt quite match up with code and S15 table and /FCNN_public.py
