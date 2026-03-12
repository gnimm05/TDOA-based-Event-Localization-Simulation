import unittest
import math
import random
from tdoa import localize_event, calc_speed_of_sound

class TestTDOA3D(unittest.TestCase):
    def test_localization_perfect_data_3d(self):
        # 5 Nodes in a 3D Volume (Corners are low, center is elevated)
        sensor_positions = [
            [0.0, 0.0, 2.0],        # Node 0
            [100.0, 0.0, 2.0],      # Node 1
            [100.0, 100.0, 2.0],    # Node 2
            [0.0, 100.0, 2.0],      # Node 3
            [50.0, 50.0, 15.0]      # Node 4 (Elevated Center)
        ]
        
        # Environmental factors
        temp_c = 30.0 # Hot day
        sos = calc_speed_of_sound(temp_c)
        
        # Simulated event at (35, 75, 5) exactly at t=10.0
        true_x, true_y, true_z = 35.0, 75.0, 5.0
        true_t = 10.0
        
        arrival_times = []
        for sx, sy, sz in sensor_positions:
            dist = math.sqrt((true_x - sx)**2 + (true_y - sy)**2 + (true_z - sz)**2)
            arrival_times.append(true_t + (dist / sos))
            
        result = localize_event(sensor_positions, arrival_times, avg_temp_celsius=temp_c)
        
        self.assertTrue(result['success'])
        # Target was explicitly on the 1m resolution grid, so expect near-perfect accuracy
        self.assertAlmostEqual(result['x'], true_x, places=2)
        self.assertAlmostEqual(result['y'], true_y, places=2)
        self.assertAlmostEqual(result['z'], true_z, places=2)
        self.assertAlmostEqual(result['t_emit'], true_t, places=3)
        self.assertEqual(result['temp_c'], 30.0)
        
    def test_localization_with_noise_3d(self):
        sensor_positions = [
            [0.0, 0.0, 0.0],
            [100.0, 0.0, 0.0],
            [100.0, 100.0, 0.0],
            [0.0, 100.0, 0.0],
            [50.0, 50.0, 10.0]
        ]
        
        true_x, true_y, true_z = 40.0, 60.0, 3.0
        true_t = 10.0
        
        temp_c = -5.0 # Cold day
        sos = calc_speed_of_sound(temp_c)
        
        arrival_times = []
        random.seed(42)
        for sx, sy, sz in sensor_positions:
            dist = math.sqrt((true_x - sx)**2 + (true_y - sy)**2 + (true_z - sz)**2)
            noise = random.gauss(0, 0.0002) # Jitter
            arrival_times.append(true_t + (dist / sos) + noise)
            
        result = localize_event(sensor_positions, arrival_times, avg_temp_celsius=temp_c)
        
        self.assertTrue(result['success'])
        # Accuracy expectation: within 3 meters in 3D Euclidean distance due to the compounding volume search noise
        dist_error = math.sqrt((result['x'] - true_x)**2 + (result['y'] - true_y)**2 + (result['z'] - true_z)**2)
        self.assertLess(dist_error, 3.0)
        
if __name__ == '__main__':
    unittest.main()
