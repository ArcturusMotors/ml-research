"""
Wrapper for cluster-based initialization methods and random initialization.
"""
import numpy as np
# from scipy.special import softmax
from ._selection_methods import UNCERTAINTY_FUNCTIONS


def init_strategy(
    X,
    y,
    n_initial,
    clusterer=None,
    selection_method=None,
    random_state=None
):
    """
    Defaults to random.

    Selection method is only relevant if a clusterer object is passed.
    Possible selection methods:
    - None (default): defaults to edge selection
    - centroid: Gets observations close to the centroids of
      the clusters.
    - edge: Gets observations close to the clusters' decision borders
    - hybrid: Some close to the centroid, others far
    """

    unlabeled_ids = np.indices(X.shape[:1]).squeeze()
    rng = np.random.RandomState(random_state)

    # Random selection
    if clusterer is None or selection_method in ['random', None]:
        ids = rng.choice(unlabeled_ids, n_initial, replace=False)
        # There must be at least 2 different initial classes
        if len(np.unique(y[ids])) == 1:
            ids[-1] = rng.choice(unlabeled_ids[y != y[ids][0]], 1, replace=False)

        return None, ids

    # Cluster-based selection
    clusterer.fit(X)

    if hasattr(clusterer, 'predict_proba'):
        # Use probabilities to compute uncertainty
        probs = clusterer.predict_proba(X)
    else:
        # Use cluster distances to compute probabilities
        dist = clusterer.transform(X)

        # The first one is another possible alternative
        dist_inv = 1 - (dist / np.expand_dims(dist.max(1), 1))
        # dist_inv = (np.expand_dims(dist.max(1), 1) / dist) - 1
        # probs = softmax(dist_inv, axis=1)
        probs = dist_inv / np.expand_dims(dist_inv.sum(1), 1)

    # Some strategies don't deal well with zero values
    probs = np.where(probs == 0., 1e-10, probs)
    uncertainty = UNCERTAINTY_FUNCTIONS[selection_method](probs)

    if selection_method == 'edge' or selection_method is None:
        ids = unlabeled_ids[np.argsort(uncertainty)[::-1][:n_initial]]

    elif selection_method == 'centroid':  # This will have to be refactored later
        ids = unlabeled_ids[np.argsort(-uncertainty)[::-1][:n_initial]]

    elif selection_method == 'hybrid':
        ids_edge = unlabeled_ids[np.argsort(uncertainty)[::-1][:n_initial]]
        ids_centroid = unlabeled_ids[np.argsort(-uncertainty)[::-1][:n_initial]]
        ids = rng.choice(np.concatenate([ids_edge, ids_centroid]), n_initial)

    return clusterer, ids
