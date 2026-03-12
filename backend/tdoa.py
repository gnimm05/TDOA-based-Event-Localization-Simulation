import math

# Formula for speed of sound based on temperature in Celsius
def calc_speed_of_sound(temp_celsius):
    return 331.3 + (0.606 * temp_celsius)

def localize_event(sensor_positions, arrival_times, avg_temp_celsius=20.0, grid_size=100.0, height_size=20.0, resolution=1.0):
    """
    Solves for the emission (x,y,z) and time given 5 sensor 3D coordinate vectors and arrival times.
    Uses a 3D volume search.
    sensor_positions: list of [x, y, z] arrays
    avg_temp_celsius: Used to dynamically calculate the speed of sound.
    """
    speed_of_sound = calc_speed_of_sound(avg_temp_celsius)
    
    min_time = min(arrival_times)
    ref_idx = arrival_times.index(min_time)
    
    observed_tdoa = [t - min_time for t in arrival_times]
    
    best_cost = float('inf')
    best_x, best_y, best_z = 0.0, 0.0, 0.0
    
    # Volume search (X: 0 to grid_size, Y: 0 to grid_size, Z: 0 to height_size)
    x_steps = int(grid_size / resolution) + 1
    y_steps = int(grid_size / resolution) + 1
    z_steps = int(height_size / resolution) + 1
    
    # To avoid massive loops blocking the main thread for too long in python,
    # we use a rough grid search first, then can refine (or just keep 1m resolution)
    # 100 * 100 * 20 = 200,000 checks, pure math in python takes ~1 second.
    for xi in range(x_steps):
        for yi in range(y_steps):
            for zi in range(z_steps):
                px = float(xi) * resolution
                py = float(yi) * resolution
                pz = float(zi) * resolution
                
                # Calculate 3D Euclidean distances
                dists = [math.sqrt((px - sx)**2 + (py - sy)**2 + (pz - sz)**2) for sx, sy, sz in sensor_positions]
                
                cost = 0.0
                for i in range(len(sensor_positions)):
                    theo_tdoa = (dists[i] - dists[ref_idx]) / speed_of_sound
                    diff = theo_tdoa - observed_tdoa[i]
                    cost += diff * diff
                    
                if cost < best_cost:
                    best_cost = cost
                    best_x = px
                    best_y = py
                    best_z = pz
                    
    ref_dist = math.sqrt((best_x - sensor_positions[ref_idx][0])**2 + (best_y - sensor_positions[ref_idx][1])**2 + (best_z - sensor_positions[ref_idx][2])**2)
    best_t_emit = min_time - (ref_dist / speed_of_sound)
    
    return {
        "x": best_x,
        "y": best_y,
        "z": best_z,
        "t_emit": best_t_emit,
        "temp_c": avg_temp_celsius,
        "dynamic_sos": speed_of_sound,
        "success": True,
        "cost": best_cost
    }

