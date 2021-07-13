"""
Generate the main experimental results.
"""

# Author: Joao Fonseca <jpmrfonseca@gmail.com>
# License: MIT

import os
from os.path import join
from zipfile import ZipFile
from sklearn.base import SamplerMixin
from skleran.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from research.utils import (
    generate_paths,
    load_datasets
)
from research.metrics import (
    data_utilization_rate,
    ALScorer,
    SCORERS
)

DATA_PATH, RESULTS_PATH, ANALYSIS_PATH = generate_paths(__file__)
TEST_SIZE = 0.2
RANDOM_SEED = 42


# setup data utilization rate for each threshold
def make_dur(threshold):
    def dur(test_scores, data_utilization):
        return data_utilization_rate(
            test_scores,
            data_utilization,
            threshold=threshold
        )
    return dur


for i in range(60, 100, 5):
    SCORERS[f'dur_{i}'] = ALScorer(make_dur(i/100))


class remove_test(SamplerMixin):
    """
    Used to ensure the data used to train classifiers with and without AL
    is the same. This method replicates the split method in the ALWrapper
    object.
    """
    def __init__(self, test_size=.2):
        self.test_size = test_size

    def _fit_resample(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=RANDOM_SEED
        )
        return X_train, y_train

    def fit_resample(self, X, y):
        return self._fit_resample(X, y)


# Experiment setup - Non-AL specific configurations
CONFIG = {
    'remove_test': [
        ('remove_test', remove_test(TEST_SIZE), {})
    ],
    'classifiers': [
        ('RF', RandomForestClassifier(), {})  # INCOMPLETE
    ],
    'scoring': ['accuracy', 'f1_macro', 'geometric_mean_score_macro'],
    'n_splits': 5,
    'n_runs': 3,
    'rnd_seed': 42,
    'n_jobs': -1,
    'verbose': 1
}

# Experiment setup - AL specific configurations
CONFIG_AL = {
    'generator': [
        ('NONE', None, {}),
        ('SMOTE', ClusterOverSampler(SMOTE(k_neighbors=5), n_jobs=1), {}),
        ('G-SMOTE', ClusterOverSampler(GeometricSMOTE(
            k_neighbors=5, deformation_factor=.5, truncation_factor=.5
        ), n_jobs=1), {})
    ],
    'wrapper': (
        'AL',
        ALWrapper(
            n_initial=15,
            increment=15,
            max_iter=49,
            test_size=TEST_SIZE,
            random_state=42
        ), {
            'evaluation_metric': ['accuracy', 'f1_macro',
                                  'geometric_mean_score_macro'],
            'selection_strategy': ['random', 'entropy', 'breaking_ties']
        }
    ),
    'scoring': [
        'accuracy',
        'f1_macro',
        'geometric_mean_score_macro',
        'area_under_learning_curve',
    ] + [f'dur_{i}' for i in range(60, 100, 5)]
}


if __name__ == '__main__':

    # extract and load datasets
    ZipFile(join(DATA_PATH, 'active_learning_augmentation.db.zip'), 'r')\
        .extract('active_learning_augmentation.db', path=DATA_PATH)

    datasets = load_datasets(data_dir=DATA_PATH)

    # remove uncompressed database file
    os.remove(join(DATA_PATH, 'active_learning_augmentation.db'))
