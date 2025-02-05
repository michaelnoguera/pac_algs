from sklearn.utils import shuffle
from sklearn import svm
import numpy as np
import pickle
import os
import pandas as pd
import scipy
from scipy.optimize import linear_sum_assignment
from scipy.spatial import distance
from sklearn.datasets import make_blobs
import math
import argparse
import copy
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from ucimlrepo import fetch_ucirepo 
from collections import Counter
from scipy.stats import entropy
from sklearn import tree
from sklearn import preprocessing
from itertools import product
from algs_lib import *
import sys

# max_val = int(sys.argv[1])
test_vals = list(range(13, 100))

train_x, train_y, test_x, test_y, num_classes, train_len = gen_iris(normalize=True)

num_features = len(train_x[0])

subsample_rate = int(0.5*train_len)
noise_dicts = {4.0: 0.021146445928720614, 1.0: 0.08654120411176264, 0.25: 0.3934787912544739, 0.0625: 1.4441306392548816, 0.015625: 5.626512931760365}

num_models = 5000 # num shadow models (256)

for trial_ind in test_vals:
    for mi in noise_dicts:
        false_dists = []
        print(f'trial number {trial_ind}')
        test_ind = trial_ind

        # create false dists
        for model_i in range(num_models):
            if model_i % 100 == 0:
                print(f'model {model_i}')
            other_x = np.delete(train_x, test_ind, 0)
            # print(other_x)
            other_y = np.delete(train_y, test_ind, 0)

            other_x = copy.deepcopy(other_x)
            other_y = copy.deepcopy(other_y)

            shuffled_x1, shuffled_y1 = shuffle(other_x, other_y)

            shuffled_x1, shuffled_y1 = get_samples_safe(shuffled_x1, shuffled_y1, num_classes, subsample_rate)
            
            model, cluster_centers = run_kmeans(shuffled_x1, shuffled_y1, num_clusters=num_classes, seed=None)

            cluster_centers = np.array(cluster_centers).reshape((num_classes, -1))
            # add noise
            for ind in range(len(cluster_centers)):
                c = np.random.normal(0, scale=noise_dicts[mi])
                cluster_centers[ind] += c
            new_centers = np.reshape(cluster_centers, (num_classes, num_features))
            model.cluster_centers_ = new_centers

            cluster_id = model.predict([train_x[test_ind]])[0]

            all_dists = []
            num_clusters = len(cluster_centers)
            for cid in range(num_clusters):

                all_dists.append(np.linalg.norm(train_x[test_ind] - cluster_centers[cid]))
            norm_factor = sum(all_dists)
            all_dists = [k/norm_factor for k in all_dists]
            conf = 1-min(all_dists)
            false_dists.append(conf)

        with open(f'test_lr_noise/models/iris_kmeans_ind_{trial_ind}_mi={mi}_noised_dist.pkl', 'wb') as f:
            pickle.dump(false_dists, f)
