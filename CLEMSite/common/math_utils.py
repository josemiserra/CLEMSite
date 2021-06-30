import numpy as np

def vec_dist(x, y):
    if (x[0] == np.inf or x[1] == np.inf or y[0] == np.inf or y[1] == np.inf):
        return np.inf
    else:
        return np.sqrt(np.sum((x - y) ** 2))

def calculateMaxDistance(in_array):
    distances = []
    for el1 in in_array:
        for el2 in in_array:
            vec1 = el1[0:2]
            vec2 = el2[0:2]
            distances.append(vec_dist(vec1,vec2))

    distances = np.sort(np.array(distances,dtype=np.float32))
    return distances[-1]


def calculateMinDistance(in_array):
    distances = []
    for el1 in in_array:
        for el2 in in_array:
            vec1 = el1[0:2]
            vec2 = el2[0:2]
            distances.append(vec_dist(vec1, vec2))

    distances = np.sort(distances)
    distances = np.trim_zeros(np.array(distances, dtype=np.float32))
    # Remove all zeros
    if np.any(distances):
        return distances[0]
    else:
        return 0.0