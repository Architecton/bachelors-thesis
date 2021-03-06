import numpy as np
from sklearn.pipeline import Pipeline
from algorithms.relief import Relief
from algorithms.relieff import Relieff
from algorithms.iterative_relief import IterativeRelief
from algorithms.irelief import IRelief
from algorithms.multiSURF import MultiSURF
from algorithms.random_selection import RandomSelection
from augmentations import covariance, me_dissim
import augmentations.LDA_custom as lda
import augmentations.PCA_custom as pca
import augmentations.NCA as nca
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from joblib import dump

import os

from sklearn.model_selection import StratifiedKFold

from collections import namedtuple

import scipy.io as sio

import pdb


### LOADING DATASET ######

data = sio.loadmat('datasets/non-noisy/basic-artificial-1/data.mat')['data']
target = np.ravel(sio.loadmat('datasets/non-noisy/basic-artificial-1/target.mat')['target'])

##########################

### METRIC FUNTIONS ############

manhattan = lambda x1, x2 : np.sum(np.abs(x1-x2), 1)
manhattan.kind = "Manhattan"

euclidean = lambda x1, x2 : np.sum(np.abs(x1-x2)**2, 1)**(1.0/2.0)
euclidean.kind = 'Euclidean'

manhattan_s = lambda x1, x2 : np.sum(np.abs(x1-x2))
manhattan_s.kind = "Manhattan"

euclidean_s = lambda x1, x2 : np.sum(np.abs(x1-x2)**2)**(1.0/2.0)
euclidean_s.kind = 'Euclidean'

manhattan_w = lambda w, x1, x2 : np.sum(np.abs(w*(x1-x2)), 1)
manhattan_w.kind = "Manhattan (weighted)"

euclidean_w = lambda w, x1, x2: np.sum(np.abs(w*(x1-x2))**2, 1)**(1.0/2.0)
euclidean_w.kind = 'Euclidean (weighted)'

manhattan_w_s = lambda w, x1, x2 : np.sum(np.abs(w*(x1-x2)))
manhattan_w_s.kind = "Manhattan (weighted)"

euclidean_w_s = lambda w, x1, x2: np.sum(np.abs(w*(x1-x2))**2)**(1.0/2.0)
euclidean_w_s.kind = 'Euclidean (weighted)'

################################


### LEARNED METRIC FUNCTIONS ###

# covariance/Mahalanobis distance
#covariance_dist_func = covariance.get_dist_func(data, target)
#covariance_dist_func.kind = "Mahalanobis distance"

lda_dist_func = lda.get_dist_func(data, target, n=1)
lda_dist_func.kind = "LDA"

nca_dist_func = nca.get_dist_func(data, target)
nca_dist_func.kind = "NCA"

#pca_dist_func = pca.get_dist_func(data)  # TODO: test
#pca_dist_func.kind = "PCA"

# Mass based dissimilarity
from julia import Julia
jl = Julia(compiled_modules=False)
script_path = os.path.abspath(__file__)
get_dissim_func = jl.include(script_path[:script_path.rfind('/')] + "/augmentations/me_dissim.jl")
NUM_ITREES = 10
dissim_func = get_dissim_func(NUM_ITREES, data)
me_dissim_dist_func = lambda _, i1, i2: dissim_func(i1, i2)
me_dissim_dist_func.kind = "Mass based dissimilarity"

#################################


# Initialize cross validation strategy.
cv_startegy = StratifiedKFold(n_splits=5)


### PIPELINES #############

# Initialize pipeline for Relief algorithm
pipeline_relief = Pipeline([('scale', StandardScaler()), 
    ('relief', Relief()), 
    ('classify', SVC(gamma='auto'))])

pipeline_relieff = Pipeline([('scale', StandardScaler()), 
    ('relieff', Relieff()), 
    ('classify', SVC(gamma='auto'))])

pipeline_iterative_relief = Pipeline([('scale', StandardScaler()), 
    ('iterative_relief', IterativeRelief()), 
    ('classify', SVC(gamma='auto'))])

pipeline_irelief = Pipeline([('scale', StandardScaler()), 
    ('irelief', IRelief()),
    ('classify', SVC(gamma='auto'))])

pipeline_multiSURF = Pipeline([('scale', StandardScaler()), 
    ('multiSURF', MultiSURF()),
    ('classify', SVC(gamma='auto'))])

pipeline_random_selection = Pipeline([('scale', StandardScaler()), 
    ('random_selection', RandomSelection()),
    ('classify', SVC(gamma='auto'))])

##########################



### GRID SEARCH ##########


# Define parameters grid for grid search.
param_grid_relief = {
    'relief__n_features_to_select': np.arange(1, data.shape[1]+1),
    'relief__dist_func': [manhattan, euclidean],
    'relief__learned_metric_func' : [None, me_dissim_dist_func, nca_dist_func, lda_dist_func],
    'classify__kernel' : ['linear', 'poly', 'rbf', 'sigmoid'],
}

param_grid_relieff = {
    'relieff__n_features_to_select': np.arange(1, data.shape[1]+1),
    'relieff__dist_func': [manhattan, euclidean],
    'relieff__learned_metric_func' : [None, me_dissim_dist_func, nca_dist_func, lda_dist_func],
    'classify__kernel' : ['linear', 'poly', 'rbf', 'sigmoid'],
}

param_grid_iterative_relief = {
    'iterative_relief__n_features_to_select': np.arange(1, data.shape[1]+1),
    'iterative_relief__dist_func' : [manhattan_w, euclidean_w],
    'iterative_relief__min_incl' : [3], #np.arange(1, 10),
    'iterative_relief__learned_metric_func' : [None, me_dissim_dist_func, nca_dist_func, lda_dist_func],
    'classify__kernel' : ['linear', 'poly', 'rbf', 'sigmoid'],
}

param_grid_irelief = {
    'irelief__n_features_to_select': np.arange(1, data.shape[1]+1),
    'irelief__dist_func' : [manhattan_w_s, euclidean_w_s],
    'irelief__learned_metric_func' : [None, me_dissim_dist_func, nca_dist_func, lda_dist_func],
    'classify__kernel' : ['linear', 'poly', 'rbf', 'sigmoid'],
}

param_grid_multiSURF = {
    'multiSURF__n_features_to_select' : np.arange(1, data.shape[1]+1),
    'multiSURF__dist_func' : [manhattan_s, euclidean_s],
    'multiSURF__learned_metric_func' : [None, me_dissim_dist_func, nca_dist_func, lda_dist_func],
    'classify__kernel' : ['linear', 'poly', 'rbf', 'sigmoid'],
}

param_grid_random_selection = {
    'random_selection__n_features_to_select': np.arange(1, data.shape[1]+1),
    'classify__kernel' : ['linear', 'poly', 'rbf', 'sigmoid'],
}


# Initialize grid search.
searches = {
    'grid_search_relief' : GridSearchCV(pipeline_relief, param_grid=param_grid_relief, cv=cv_startegy, verbose=True, iid=False),
    'grid_search_relieff' : GridSearchCV(pipeline_relieff, param_grid=param_grid_relieff, cv=cv_startegy, verbose=True, iid=False),
    'grid_search_iterative_relief' : GridSearchCV(pipeline_iterative_relief, param_grid=param_grid_iterative_relief, cv=cv_startegy, verbose=True, iid=False),
    'grid_search_irelief' : GridSearchCV(pipeline_irelief, param_grid=param_grid_irelief, cv=cv_startegy, verbose=True, iid=False),
    'grid_search_multiSURF' : GridSearchCV(pipeline_multiSURF, param_grid=param_grid_multiSURF, cv=cv_startegy, verbose=True, n_jobs=-1)
    'grid_search_random_selection' : GridSearchCV(pipeline_random_selection, param_grid=param_grid_random_selection, cv=cv_startegy, verbose=True, iid=False)
}

# Define named tuple used to store algorithm name, result pair.
resTuple = namedtuple('resTuple', 'name result')
results = set()  # Define set for storing results.

# Perform grid search for all algorithms.
for key in searches.keys():
    results.add(resTuple(key, searches[key].fit(data, target)))

# Save results to file.
dump(results, 'results.joblib')

