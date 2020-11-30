"""
A wrapper to allow an automated Active Learning procedure for an
experimental environment.
"""

# Author: Joao Fonseca <jpmrfonseca@gmail.com>
# License: MIT

import numpy as np
from sklearn.base import clone
from sklearn.base import ClassifierMixin, BaseEstimator
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from ..metrics import SCORERS
from ._selection_methods import SELECTION_CRITERIA


class ALWrapper(ClassifierMixin, BaseEstimator):
    def __init__(
        self,
        classifier=None,
        max_iter=1000,
        selection_strategy='entropy',
        n_initial=100,
        increment=50,
        save_classifiers=False,
        save_test_scores=True,
        auto_load=True,
        test_size=.1,
        evaluation_metric=None,
        random_state=None
    ):
        """
        A wrapper to allow an automated Active Learning procedure for an
        experimental environment.
        """
        self.classifier = classifier
        self.max_iter = max_iter
        self.selection_strategy = selection_strategy
        self.n_initial = n_initial
        self.increment = increment
        self.random_state = random_state

        # For finding the optimal classifier purposes
        self.auto_load = auto_load
        self.test_size = test_size
        self.save_classifiers = save_classifiers
        self.save_test_scores = save_test_scores
        self.evaluation_metric = evaluation_metric

    def _check(self, X, y):

        if self.evaluation_metric is None:
            self.evaluation_metric_ = SCORERS['accuracy']
        elif type(self.evaluation_metric) == str:
            self.evaluation_metric_ = SCORERS[self.evaluation_metric]
        else:
            self.evaluation_metric_ = self.evaluation_metric

        if self.classifier is None:
            self._classifier = RandomForestClassifier()

        if type(self.selection_strategy) == str:
            self.selection_strategy_ = SELECTION_CRITERIA[
                self.selection_strategy
            ]
        else:
            self.selection_strategy_ = self.selection_strategy

        if self.save_classifiers or self.save_test_scores:
            self.data_utilization_ = []

        if self.save_classifiers:
            self.classifiers_ = []

        if self.save_test_scores:
            self.test_scores_ = []

        if self.auto_load:
            self.classifier_ = None
            self._top_score = 0
            X, X_test, y, y_test = train_test_split(
                X, y,
                test_size=self.test_size,
                random_state=self.random_state,
                stratify=y
            )
        else:
            X_test, y_test = (None, None)

        self.increment_ = self.increment
        return X, X_test, y, y_test

    def fit(self, X, y):

        X, X_test, y, y_test = self._check(X, y)

        iter_n = 0
        selection = np.zeros(shape=(X.shape[0])).astype(bool)
        probabs = None

        while iter_n < self.max_iter:

            classifier = clone(self._classifier)

            # add new samples to dataset
            unlabeled_ids = np.argwhere(~selection).squeeze()
            ids = (
                # new samples
                self.selection_strategy_(
                    probabilities=probabs,
                    unlabeled_ids=unlabeled_ids,
                    increment=self.increment_,
                    random_state=self.random_state
                )
                if iter_n != 0
                else
                # random initialization
                SELECTION_CRITERIA['random'](
                    unlabeled_ids=unlabeled_ids,
                    increment=self.n_initial,
                    random_state=self.random_state
                )
            )
            selection[ids] = True

            # train classifier and get probabilities
            classifier.fit(X[selection], y[selection])

            # get score for current iteration
            if self.save_test_scores or self.auto_load:
                score = self.evaluation_metric_(
                    classifier,
                    X_test,
                    y_test
                )
                self.data_utilization_.append(
                    (selection.sum(), selection.sum()/selection.shape[0])
                )

            # save classifier
            if self.save_classifiers:
                self.classifiers_.append(classifier)

            # save test scores
            if self.save_test_scores:
                self.test_scores_.append(score)

            # Replace top classifier
            if self.auto_load:
                if score > self._top_score:
                    self._top_score = score
                    self.classifier_ = classifier
                    self.top_score_iter_ = iter_n

            # keep track of iter_n
            if self.max_iter is not None:
                iter_n += 1

            # stop if all examples have been included
            if selection.all():
                break
            elif selection.sum()+self.increment_ > y.shape[0]:
                self.increment_ = y.shape[0] - selection.sum()

            probabs = classifier.predict_proba(X[~selection])

            # some selection strategies can't deal with 0. values
            probabs = np.where(probabs == 0., 1e-10, probabs)

        return self

    def load_best_classifier(self, X, y):
        scores = []
        for classifier in self.classifiers_:
            scores.append(
                self.evaluation_metric_(classifier, X, y)
            )

        self.classifier_ = self.classifiers_[np.argmax(scores)]
        return self

    def predict(self, X):
        return self.classifier_.predict(X)
