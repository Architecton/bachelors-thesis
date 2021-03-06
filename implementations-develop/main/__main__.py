import os
import sys
from importlib import import_module
from clint.arguments import Args
from clint.textui import puts, colored, indent
from functools import partial
import numpy as np

## Classifier imports ###
from sklearn.svm import SVC  # 1
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier  # 2, 3
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

from sklearn.model_selection import cross_val_score, KFold
from sklearn.preprocessing import StandardScaler

import pdb


"""
Script that provides a simple user interface for exploring various versions of RELIEF based
algorithms.

Author: Jernej Vivod

"""


quit = False  # If true at end of script, it will not restart.


### Previous cross validation result ###
prev_cv_res = None
###

while True:
    ### User choice values ###

    # --- 
    usr_alg_choices = {1, 2, 3, 4, 5}  # Algorithm choices
    usr_alg_choice = None        # User's algorithm choice
    # ---
    usr_aug_choices = {1, 2, 3, 4}  # Algorithm augmentation choices
    usr_aug_choice = None           # User's augmentation choice
    # ---
    usr_metric_choices = {1, 2}     # Metric learning type choices
    usr_metric_choice = None        # User's metric learning type choice
    # --
    usr_dataset_choices = dict()  # Populated later
    usr_dataset_choice = None     # User's dataset choice
    # ---
    usr_run_classifier = None     # Run classifier or not
    # ---
    usr_classifier_type_choices = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}  # User's classifier type choices
    usr_classifier_type_choice = None  # User's classifier type choice
    # ---
    usr_thresh_choice = None      # Threshold choice
    # ---
    usr_sel_type = None           # Select features using weight threshold or number of best to keep
    # ---
    usr_num_feat_keep = None      # Number of best features to keep



    ### Parsing algorithm to use from user ###

    while True:
        os.system('clear')
        puts(colored.blue('Select algorithm to use:')) 
        with indent(4, quote=colored.blue('>>>')):
            puts(colored.green('Basic RELIEF (1)'))
            puts(colored.green('RELIEFF (2)'))
            puts(colored.green('Iterative RELIEF (3)'))
            puts(colored.green('I-RELIEF (4)'))
            puts(colored.green('random feature weighting (5)'))
        alg_usr = input()
        if alg_usr.isdigit() and int(alg_usr) in usr_alg_choices:
            usr_alg_choice = int(alg_usr)
            break



    ### Parsing algorithm augmentation from user ###

    while True:
        os.system('clear')
        puts(colored.blue('Select algorithm augmentation:'))
        with indent(4, quote=colored.blue('>>>')):
            puts(colored.green('None (1)'))
            puts(colored.green('Metric learning (2)'))
            puts(colored.green('me-dissimilarity (3)'))
            puts(colored.green('mp-dissimilarity (4)'))

        aug_usr = input()
        if aug_usr.isdigit() and int(aug_usr) in usr_aug_choices:
            usr_aug_choice = int(aug_usr)
            break

    

    ### If user chose metric learning augmentation, ###
    ### parse type of metric learning to use from user ###
    
    if usr_aug_choice == 2:
        while True:
            os.system('clear')
            puts(colored.blue('Select type of metric learning to use:'))
            with indent(4, quote=colored.blue('>>>')):
                puts(colored.green('Covariance (1)'))
                puts(colored.green('PCA (2)'))

            metric_usr = input()
            if metric_usr.isdigit() and int(metric_usr) in usr_metric_choices:
                usr_metric_choice = int(metric_usr)
                break

    ### Parse dataset to use from user ###

    while True:
        os.system('clear')
        puts(colored.blue('Select dataset to use: '))
        with indent(4, quote=colored.blue('>>>')):
            idx = 1
            for dataset_name in os.listdir(sys.path[0] + '/datasets'):
                if not (dataset_name.endswith('.py') or dataset_name.endswith('__')):
                    usr_dataset_choices[idx] = dataset_name
                    puts(colored.green('{0} ({1})'.format(dataset_name, idx)))
                    idx += 1
        dataset_usr = input()

        if dataset_usr.isdigit() and int(dataset_usr) in usr_dataset_choices.keys():
            usr_dataset_choice = int(dataset_usr)
            break


    ### Importing dataset ###

    import datasets.load_dataset as load_dataset
    data = load_dataset.load(usr_dataset_choices[usr_dataset_choice], 'data')
    data = StandardScaler().fit_transform(data)
    target = load_dataset.load(usr_dataset_choices[usr_dataset_choice], 'target')
    target = np.ravel(target).astype(np.float)

    ### Basic algorithm initialization  ###
    if usr_aug_choice == 3:
        from augmentations.me_dissim import MeDissimilarity
        me = MeDissimilarity(data)
        dist_func = me.get_dissim_func(num_itrees=10)
    else:
        dist_func = lambda x1, x2: np.sum(np.abs(x1-x2)**2, 1)**(1/2)

    # TODO: All keyword args
    if usr_alg_choice == 1:
        from algorithms.relief import relief  # Partially pass parameters
        alg = partial(relief, data, target, data.shape[0], dist_func)
    elif usr_alg_choice == 2:
        from algorithms.relieff import relieff # Partially pass parameters
        alg = partial(relieff, data, target, data.shape[0], 5, dist_func)
    elif usr_alg_choice == 3:
        from algorithms.iterative_relief import iterative_relief
        alg = partial(iterative_relief, data, target, data.shape[0], 1, lambda x1, x2, w: np.sum(np.abs(w*(x1 - x2))**2, 1)**(1/2), max_iter=100)
    elif usr_alg_choice == 4:
        from algorithms.irelief import irelief
        # Takes a weighted distance function - override previous dist_func.
        alg = partial(irelief, data, target, lambda w, x1, x2: np.sum(np.abs(w*(x1 - x2))**2)**(1/2), max_iter=100, k_width=2.0, conv_condition=0.0, initial_w_div=data.shape[1])
    elif usr_alg_choice == 5:
        from algorithms.random_sel import rand_sel
        alg = partial(rand_sel, data)


    ## Augmented metric function initialization ##
    if usr_aug_choice == 1:
        os.system('clear')
    elif usr_aug_choice == 2:
        if usr_metric_choice == 1:
            from augmentations.covariance import get_dist_func
            try:
                learned_metric = get_dist_func(data, target)
                alg = partial(alg, learned_metric_func=learned_metric)
                os.system('clear')
            except np.linalg.LinAlgError as e:
                os.system('clear')
                print(colored.red('Could not apply augmentation - matrix singular or not positive definite.'))
        if usr_metric_choice == 2:
            pass
    elif usr_aug_choice == 3:
        pass  # Already handled when setting distance function.


    ### Prompt user to press ENTER to start computations. ###
    puts(colored.yellow('Press ENTER to start'))
    input()

    ### Call and time initialize algorithm ###
    rank, weights = alg()



    ### Display Results ###

    os.system('clear')
    puts(colored.yellow('Results:'))
    print('Feature ranks: {0}'.format(rank))
    print('Feature weights: {0}'.format(weights))
    print()


    ### Ask user if they want to run a classifier on the data ###
    while True:
        puts(colored.blue('Do you want to run a classifier on the preprocessed dataset? (y/n) '))
        run_classifier_usr = input()
        os.system('clear')
        if run_classifier_usr == 'y':
            usr_run_classifier = True
            break
        elif run_classifier_usr == 'n':
            usr_run_classifier = False
            break
        else:
            pass


    ### Ask user which classifier to use ###
    if usr_run_classifier:
        while True:
            os.system('clear')
            puts(colored.blue('Select classifier to use:'))
            with indent(4, quote=colored.blue('>>>')):
                puts(colored.green('Support vector machine (1)'))
                puts(colored.green('Random forest (2)'))
            classifier_type_usr = input()
            if classifier_type_usr.isdigit() and int(classifier_type_usr) in usr_classifier_type_choices:
                usr_classifier_type_choice = int(classifier_type_usr)
                break



    ### Ask user to set feature threshold ###
    if usr_run_classifier:
        os.system('clear')
        feat_sel_set = False
        
        while True:
            puts(colored.blue('Select weight threshold (1) or number of best features to keep (2)?'))
            sel_type_usr = input()
            os.system('clear')
            if sel_type_usr.isdigit() and int(sel_type_usr) in {1, 2}:
                usr_sel_type = int(sel_type_usr)
                break
            else:
                pass
        
        if usr_sel_type == 1:
            while True:
                print(colored.blue('Select a feature weight threshold from '), end="")
                print(colored.yellow('[{0:.5f}, {1:.5f}]'.format(np.min(weights), np.max(weights))))
                thresh_usr = input()
                os.system('clear')
                try:
                    usr_thresh_choice = float(thresh_usr)
                    remaining_feat = np.sum(weights >= usr_thresh_choice)
                    if remaining_feat >= 1:
                        while True:
                            print(colored.blue('This threshold selection will keep '), end="")
                            print(colored.yellow('{0}/{1} '.format(remaining_feat, len(weights))), end="")
                            print(colored.blue('features. Continue? (y/n)'))
                            cont = input()
                            if cont == 'y':
                                feat_sel_set = True
                                break
                            else:
                                break
                    else:
                        puts(colored.red("At least one feature's weight must be above or equal to the threshold."))
                    
                    if feat_sel_set:
                        break
                except ValueError:
                    pass
        else:
            while True:
                print(colored.blue('Select number of best features to keep (integer from '), end="")
                print(colored.yellow('[{0}, {1}]'.format(1, np.max(rank))), end="")
                print(colored.blue('): '))
                num_feat_keep_usr = input()
                os.system('clear')
                if num_feat_keep_usr.isdigit() and int(num_feat_keep_usr) in range(1, np.max(rank)+1):
                    usr_num_feat_keep = int(num_feat_keep_usr)
                    break

    
    if usr_run_classifier:
        ### Performing actual feature selection ###
        if usr_sel_type == 1:  # Selection by weight threshold
            msk = weights >= usr_thresh_choice
            data_proc = data[:, msk]
        elif usr_sel_type == 2:  # selection by number of best to keep
            msk = rank <= usr_num_feat_keep
            data_proc = data[:, msk]

    ### Run classifier on data and display metrics ###
    if usr_run_classifier:
        if usr_classifier_type_choice == 1:
            clf = SVC(kernel='rbf', gamma='auto')
            cv = KFold(n_splits=data_proc.shape[0], shuffle=True)
            scores = cross_val_score(clf, data_proc, target, cv=cv, n_jobs=-1)
            os.system('clear')
            print(colored.yellow('Cross-validataion result: '), end="")
            print(colored.cyan('{0:5f}'.format(np.mean(scores))))
        elif usr_classifier_type_choice == 2:
            clf = RandomForestClassifier(n_estimators=100, n_jobs=-1)
            cv = KFold(n_splits=data_proc.shape[0], shuffle=True)
            scores = cross_val_score(clf, data_proc, target, cv=cv, n_jobs=-1)
            os.system('clear')
            print(colored.yellow('Cross-validataion result: '), end="")
            print(colored.cyan('{0:5f}'.format(np.mean(scores))))
        if prev_cv_res:
            print('(previous Cross-validation result: ', end="")
            print(colored.cyan('{0:5f}'.format(prev_cv_res)), end="")
            print(')')
            prev_cv_res = np.mean(scores)
        else:
            prev_cv_res = np.mean(scores)


    ### Ask user if they want to restart the program ###

    while True:
        restart = input(colored.yellow('Restart? (y/n) '))
        os.system('clear')
        if restart == 'y':
            break
        if restart == 'n':
            quit = True
            break
        else:
            pass

    if quit:
        break
    else:
        pass

