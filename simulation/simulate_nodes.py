import time
import math
import random
import uuid
import requests
import threading

# Configuration
API_URL = "http://127.0.0.1:5000/api/data"
SPEED_OF_SOUND = 343.0 # m/s
GRID_SIZE = 100.0

# Node definitions (X, Y, Z coordinates in meters)
NODES = {
    0: (0.0, 0.0, 3.0),         # Corner
    1: (GRID_SIZE, 0.0, 3.0),   # Corner
    2: (GRID_SIZE, GRID_SIZE, 3.0), # Corner
    3: (0.0, GRID_SIZE, 3.0),   # Corner
    4: (GRID_SIZE / 2, GRID_SIZE / 2, 12.0) # Central Node, Elevated
}

def calc_speed_of_sound(temp_celsius):
    return 331.3 + (0.606 * temp_celsius)

class SimulatedNode:
    def __init__(self, node_id, position):
        self.node_id = node_id
        self.position = position # (X, Y, Z)
        self.clock_drift = random.uniform(-0.001, 0.001)
        self.dsp_residual_jitter_std = 0.0005 

    def get_telemetry(self):
        """Simulates reading from environmental I2C sensors (BME280/INMP441/ADC)"""
        # Base temperature around 22C, varying slightly per node
        base_temp = 22.0 + random.uniform(-1.0, 1.0) 
        
        # Base background noise ~40dB, varying
        noise_floor_db = 40.0 + random.uniform(-5.0, 5.0)
        
        # Battery discharging slowly over time (simulated via random bounds for now)
        battery_v = random.uniform(3.4, 4.2)
        
        return {
            "temp_c": round(base_temp, 2),
            "noise_db": round(noise_floor_db, 1),
            "battery_v": round(battery_v, 2)
        }

    def sense_and_transmit(self, event_id, target_x, target_y, target_z, target_t_emit):
        telemetry = self.get_telemetry()
        sos = calc_speed_of_sound(telemetry['temp_c'])
        
        # 1. 3D Physical propagation delay
        dist = math.sqrt((target_x - self.position[0])**2 + (target_y - self.position[1])**2 + (target_z - self.position[2])**2)
        true_arrival_time = target_t_emit + (dist / sos)
        
        # 2. Simulate DSP and clock errors
        measured_time = true_arrival_time + self.clock_drift + random.gauss(0, self.dsp_residual_jitter_std)
        
        # 3. Transmit JSON payload via HTTP
        payload = {
            "event_id": event_id,
            "node_id": self.node_id,
            "timestamp": measured_time,
            "telemetry": telemetry
        }
        
        # Simulate network transmission delay variations
        time.sleep(random.uniform(0.01, 0.1))
        
        try:
            response = requests.post(API_URL, json=payload, timeout=2)
            if response.status_code == 200:
                pass # success
            else:
                print(f"[Node {self.node_id}] Failed to send data: {response.text}")
        except Exception as e:
            print(f"[Node {self.node_id}] Network error: {e}")

def simulate_environment():
    print("Starting TDOA ESP32 Simulation Environment...")
    print("Press Ctrl+C to stop.")
    
    nodes = [SimulatedNode(i, pos) for i, pos in NODES.items()]
    
    try:
        while True:
            # Generate a random acoustic anomaly in the 3D physical environment
            target_x = random.uniform(10.0, GRID_SIZE - 10.0)
            target_y = random.uniform(10.0, GRID_SIZE - 10.0)
            target_z = random.uniform(0.0, 5.0) # Z between 0m (ground) and 5m
            target_t_emit = time.time()
            event_id = str(uuid.uuid4())[:8] # Short UUID
            
            print(f"\n--- [ENVIRONMENT] Anomaly spawned at ({target_x:.2f}, {target_y:.2f}, {target_z:.2f}) ---")
            
            # Fire the sensors concurrently to simulate isolated embedded devices
            threads = []
            for node in nodes:
                t = threading.Thread(target=node.sense_and_transmit, args=(event_id, target_x, target_y, target_z, target_t_emit))
                t.start()
                threads.append(t)
                
            for t in threads:
                t.join()
                
            # Wait 5 seconds before the next event
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nSimulation stopped.")

if __name__ == "__main__":
    simulate_environment()
