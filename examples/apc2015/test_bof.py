#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cPickle as pickle
import gzip

import numpy as np
from scipy.misc import imread
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import normalize

import apc2015
import fcn.util

from imagesift import get_sift_keypoints


class BoFClassifier(object):

    def __init__(self):
        with gzip.open('bof_trained_data/apc2015_bof.pkl.gz', 'rb') as f:
            self.bof = pickle.load(f)
            if 'n_jobs' not in self.bof.nn.__dict__:
                self.bof.nn.n_jobs = 1

        with gzip.open('bof_trained_data/apc2015_lgr.pkl.gz', 'rb') as f:
            self.lgr = pickle.load(f)

    def extract(self, rgb):
        gray = rgb.mean(axis=-1).astype(np.uint8)
        frames, desc = get_sift_keypoints(gray)
        if desc.size == 0:
            return None
        X = self.bof.transform([desc])
        normalize(X, copy=False)
        return X

    def predict_proba(self, X):
        y_proba = self.lgr.predict_proba(X)
        return y_proba


if __name__ == '__main__':
    dataset = apc2015.APC2015('leveldb')
    clf = BoFClassifier()

    y_true = []
    y_pred = []
    for index in dataset.test:
        # data -> feature
        rgb = imread(dataset.img_files[index], mode='RGB')
        if dataset.mask_files[index] is not None:
            mask = imread(dataset.mask_files[index], mode='L')
            rgb = fcn.util.apply_mask(rgb, mask, crop=True)
        X = clf.extract(rgb)
        if X is None:
            continue

        # for inserted 'background' label at index 0
        y_true.append(dataset.target[index] - 1)

        y_proba = clf.predict_proba(X)
        assert len(y_proba[0]) == len(dataset.target_names[1:])
        y_pred.append(np.argmax(y_proba[0]))

    acc = accuracy_score(y_true, y_pred)
    print('Mean Accuracy: {0}'.format(acc))
