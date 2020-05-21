import numpy as np
from scipy.stats import kurtosis


def extract_features(xy, unique_from=46, unique_to=1006,
                     unique_granularity=1, unique_deltas=[0,46,1005], to_withdraw=[]): # dataset is {'xs': [packet1, packet2,...], 'ys': [packet1, packet2,...]} where x is time and y is size
    """
    From a time series of packet length, extract statiscal features as explained
    in the Master Project: "Traffic Analysis of Smartwatches".

    Args:
        xy : dct[xs, ys] -> [int, ], [int, ]. Contains the packet length serie and the timing.
        unique_from : int. Staring packet length from which to be taken into account.
        unique_to : int. Stopping packet length until which to be taken into account.
        unique_granularity : int. bins length for unique packet length features.
        unique_deltas : [int, ]. packet lengths from which timing features have to be expanded.
        to_withdraw : [str, ]. List of features to be withdraw.

    Return:
        dict[feature] -> float. Dictionnary of feature's name and their value.
    """

    xs = xy['xs']
    ys = xy['ys']
    f = dict()
    bins = np.arange(0, 1000, step = unique_granularity)
    def extract_bins(x):

        if x > bins[-1]:
            b = bins[-1] + 10
        else:
            b = bins[np.digitize(x, bins, right = True)]
        return b

    def take(arr, n=30):
        if len(arr) > n:
            return arr[:30]
        return arr

    def stats(key, data):
        if len(data) == 0:
            data=[-1]
        f['min_'+key] = np.min(data)
        f['mean_'+key] = np.mean(data)
        f['max_'+key] = np.max(data)
        f['count_'+key] = len(data)
        f['std_'+key] = np.std(data)
        f['kurtosis_'+key] = kurtosis(data)



    # general statistics
    stats("non_null", [abs(y) for y in ys if abs(y) < unique_from])
    stats("outgoing", [abs(y) for y in ys if y > unique_from])
    stats("incoming", [abs(y) for y in ys if y < -unique_from])

    # unique packet lengths [Liberatore and Levine; Herrmann et al.]
    lengths = dict()
    for i in range(unique_from, unique_to):
        lengths[str(i)] = 0
    for y in ys:
        if str(abs(y)) in lengths:
            lengths[str(abs(y))] += 1

    lengths_array = list(lengths.values())
    stats("unique_lengths", lengths_array)

    # global stats about len
    for l in lengths:
        f['unique_lengths_'+str(l)] = extract_bins(lengths[l])


    # statistics about timings
    for u in unique_deltas:
        xs_filtered = [xs[i] for i, y in enumerate(ys) if abs(y) > u]
        x_deltas = []
        i=0
        while i<len(xs_filtered):
            x_deltas.append(xs_filtered[i]-xs_filtered[i-1])
            i += 1
        stats("x_deltas_"+str(u), x_deltas)
    for feature in to_withdraw:
        if feature in f:
            del f[feature]

    return f
