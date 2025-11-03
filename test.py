import numpy as np
from scipy.optimize import least_squares


nodes = np.array([
    [0.0, 0.0],   # Node 1
    [10.0, 0.0],  # Node 2
    [5.0, 8.0]    # Node 3
])

v = 343.0  # Propagation speed (m/s), e.g., sound


event_true = np.array([4.0, 3.0])  # True event location

def distance(p1, p2):
    return np.linalg.norm(p1 - p2)

toa = np.array([distance(event_true, node) / v for node in nodes])

# Compute TDOA relative to Node 1
tdoa = toa[1:] - toa[0]  # [t2 - t1, t3 - t1]


def tdoa_residuals(p, nodes, tdoa, v):
    x, y = p
    res = []
    # Node 2 relative to Node 1
    res.append(distance([x, y], nodes[1]) - distance([x, y], nodes[0]) - tdoa[0]*v)
    # Node 3 relative to Node 1
    res.append(distance([x, y], nodes[2]) - distance([x, y], nodes[0]) - tdoa[1]*v)
    return res


x0 = np.mean(nodes, axis=0)

result = least_squares(tdoa_residuals, x0, args=(nodes, tdoa, v))
event_est = result.x

print(f"True event location: {event_true}")
print(f"Estimated event location: {event_est}")
