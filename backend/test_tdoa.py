import unittest
import math
import random
from tdoa import localize_event, SPEED_OF_SOUND

class TestTDOA(unittest.TestCase):
    def test_localization_perfect_data(self):
        sensor_positions = [
            [0.0, 0.0],
            [100.0, 0.0],
            [100.0, 100.0],
            [0.0, 100.0]
        ]
        
        true_x, true_y = 35.0, 75.0
        true_t = 10.0
        
        arrival_times = []
        for sx, sy in sensor_positions:
            dist = math.hypot(true_x - sx, true_y - sy)
            arrival_times.append(true_t + (dist / SPEED_OF_SOUND))
            
        result = localize_event(sensor_positions, arrival_times)
        
        self.assertTrue(result['success'])
        # The solver checks at 1m resolution, so it should be exact if the target is on grid
        self.assertAlmostEqual(result['x'], true_x, places=2)
        self.assertAlmostEqual(result['y'], true_y, places=2)
        self.assertAlmostEqual(result['t_emit'], true_t, places=3)
        
    def test_localization_with_noise(self):
        sensor_positions = [
            [0.0, 0.0],
            [100.0, 0.0],
            [100.0, 100.0],
            [0.0, 100.0]
        ]
        
        true_x, true_y = 35.0, 75.0
        true_t = 10.0
        
        arrival_times = []
        random.seed(42) # For reproducibility
        for sx, sy in sensor_positions:
            dist = math.hypot(true_x - sx, true_y - sy)
            noise = random.gauss(0, 0.0005) # ~0.5 ms jitter
            arrival_times.append(true_t + (dist / SPEED_OF_SOUND) + noise)
            
        result = localize_event(sensor_positions, arrival_times)
        
        self.assertTrue(result['success'])
        # The solver outputs a grid point, check if it's within 2 meters (due to 1m grid + noise)
        dist_error = math.hypot(result['x'] - true_x, result['y'] - true_y)
        self.assertLess(dist_error, 2.0)
        
if __name__ == '__main__':
    unittest.main()
