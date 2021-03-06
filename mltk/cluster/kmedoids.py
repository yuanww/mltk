import random
import numpy.matlib as ml
from numpy import array, ndarray, zeros, inf

__docformat__ = 'restructuredtext'
__all__ = ['kmedoids']

def kmedoids(distmat, k, threshold=1e-15, ntry=5,
        seeds=None, verbose=False):
    """\
    k-medoids clustering algorithm.

    :type distmat: ndarray
    :param distmat: a N-by-N dissimilarity matrix.
    :type k: int
    :param k: number of clusters.
    :type threshold: float
    :param threshold: the threshold to stop the iteration.
    :type ntry: int
    :param ntry: number of times to run k-medoids, useful to avoid accidentally
        trapped in local maximum. If ``seeds`` is given, the algorithm will run
        only once because the result is always the same with the same seeds.
    :type seeds: ndarray
    :param seeds: a length-k int array of index (into ``distmat``) representing
        the initial selection of medoids.
    :type verbose: bool
    :param verbose: if ``True``, print progress to standard output. Useful for
        debugging.

    :return: a length-k array of index indicating the medoids and a length-N
        array the final label for each point.
    """
    minJ = inf
    min_imedoids = None
    min_labels = None

    if seeds is None:
        N = len(distmat)
        for i in range(ntry):
            # initialize medoids
            seeds = random.sample(range(N), k)
            imedoids, labels, J = \
                    _kmedoids(distmat, threshold, seeds, verbose)
            if J < minJ:
                minJ = J
                min_imedoids = imedoids
                min_labels = labels
    else:
        if seeds.shape != (k,):
            raise ValueError('seeds should be a length-%d array' % k)
        min_imedoids, min_labels, minJ = \
                _kmedoids(distmat, threshold, seeds, verbose)
    return min_imedoids, min_labels


def _kmedoids(distmat, threshold, imedoids, verbose):
    """\
    The *raw* version of k-medoids.
    """
    # initialize J
    Jprev = inf
    # initialize iteration count
    iter = 0

    # iterations
    while True:
        # distance from medoids to all other points
        dist = distmat[imedoids]
        # assign x to nearst medoid
        labels = dist.argmin(axis=0)
        J = 0
        # re-choose each medoids
        for j in range(len(imedoids)):
            idx_j = (labels == j).nonzero()[0]
            distj = distmat[idx_j][:, idx_j]
            distsum = ml.sum(distj, axis=1)
            idxmin = distsum.argmin()
            imedoids[j] = idx_j[idxmin]
            J += distsum[idxmin]

        iter += 1
        if verbose:
            print '[kmedoids] iter %d (J=%.4f)' % (iter, J)

        if Jprev-J < threshold:
            break
        Jprev = J

    return imedoids, labels, J
