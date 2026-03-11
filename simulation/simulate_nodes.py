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

# Node definitions
NODES = {
    0: (0.0, 0.0),
    1: (GRID_SIZE, 0.0),
    2: (GRID_SIZE, GRID_SIZE),
    3: (0.0, GRID_SIZE),
    4: (GRID_SIZE / 2, GRID_SIZE / 2) # Central Node
}

class SimulatedNode:
    def __init__(self, node_id, position):
        self.node_id = node_id
        self.position = position
        self.clock_drift = random.uniform(-0.001, 0.001) # constant clock offset
        
        # Simulating Moving Average DSP behavior:
        # Instead of feeding raw audio, we simulate the output of the DSP pipeline.
        # A moving average filter will smooth out high-frequency noise but add a slight
        # group delay and some residual jitter to the threshold-crossing timestamp.
        self.dsp_residual_jitter_std = 0.0005 # 0.5 ms jitter ~ 17cm error

    def sense_and_transmit(self, event_id, target_x, target_y, target_t_emit):
        # 1. Physical propagation delay
        dist = math.hypot(target_x - self.position[0], target_y - self.position[1])
        true_arrival_time = target_t_emit + (dist / SPEED_OF_SOUND)
        
        # 2. Simulate DSP and clock errors
        # Apply the static clock drift + random residual jitter from the DSP filter
        measured_time = true_arrival_time + self.clock_drift + random.gauss(0, self.dsp_residual_jitter_std)
        
        # 3. Transmit JSON payload via HTTP
        payload = {
            "event_id": event_id,
            "node_id": self.node_id,
            "timestamp": measured_time
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
            # Generate a random acoustic anomaly in the physical environment
            target_x = random.uniform(10.0, GRID_SIZE - 10.0)
            target_y = random.uniform(10.0, GRID_SIZE - 10.0)
            target_t_emit = time.time()
            event_id = str(uuid.uuid4())[:8] # Short UUID
            
            print(f"\n--- [ENVIRONMENT] Anomaly spawned at ({target_x:.2f}, {target_y:.2f}) ---")
            
            # Fire the sensors concurrently to simulate isolated embedded devices
            threads = []
            for node in nodes:
                t = threading.Thread(target=node.sense_and_transmit, args=(event_id, target_x, target_y, target_t_emit))
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
