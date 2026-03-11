import math

SPEED_OF_SOUND = 343.0  # m/s

def localize_event(sensor_positions, arrival_times, grid_size=100.0, resolution=1.0):
    """
    Solves for the emission (x,y) and time given 4 sensor coordinate pairs and arrival times.
    Uses a pure-Python grid search approach across the area to avoid Numpy/SciPy dependency complications
    on Windows while maintaining 1-meter deterministic localization accuracy.
    """
    min_time = min(arrival_times)
    ref_idx = arrival_times.index(min_time)
    
    observed_tdoa = [t - min_time for t in arrival_times]
    
    best_cost = float('inf')
    best_x, best_y = 0.0, 0.0
    
    # Grid search (0 to grid_size by resolution steps)
    steps = int(grid_size / resolution) + 1
    
    for xi in range(steps):
        for yi in range(steps):
            px = float(xi) * resolution
            py = float(yi) * resolution
            
            dists = [math.hypot(px - sx, py - sy) for sx, sy in sensor_positions]
            
            cost = 0.0
            for i in range(len(sensor_positions)):
                theo_tdoa = (dists[i] - dists[ref_idx]) / SPEED_OF_SOUND
                diff = theo_tdoa - observed_tdoa[i]
                cost += diff * diff
                
            if cost < best_cost:
                best_cost = cost
                best_x = px
                best_y = py
                
    ref_dist = math.hypot(best_x - sensor_positions[ref_idx][0], best_y - sensor_positions[ref_idx][1])
    best_t_emit = min_time - (ref_dist / SPEED_OF_SOUND)
    
    return {
        "x": best_x,
        "y": best_y,
        "t_emit": best_t_emit,
        "success": True,
        "cost": best_cost
    }
