from flask import Flask, request, jsonify, render_template
import time
from tdoa import localize_event

app = Flask(__name__)

# Hardcoded sensor positions for the simulation
# Nodes are at the corners of a 100x100 meter square, plus a central node
SENSOR_POSITIONS = {
    0: [0.0, 0.0],
    1: [100.0, 0.0],
    2: [100.0, 100.0],
    3: [0.0, 100.0],
    4: [50.0, 50.0]
}

# In-memory store for incoming sensor data
# { "event_id": { "node_0": timestamp, "node_1": timestamp, ... } }
pending_events = {}

# In-memory store for completed, localized events
# [{ "event_id": id, "x": x, "y": y, "t_emit": t, "timestamp": unix_time }]
localized_events = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    if not data or 'event_id' not in data or 'node_id' not in data or 'timestamp' not in data:
        return jsonify({"error": "Invalid payload"}), 400
        
    event_id = data['event_id']
    node_id = int(data['node_id'])
    timestamp = float(data['timestamp'])
    
    if event_id not in pending_events:
        pending_events[event_id] = {}
        
    pending_events[event_id][node_id] = timestamp
    
    # Check if we have all 5 node readings for this event
    if len(pending_events[event_id]) == 5:
        # We have all 5! Correlate and localize
        readings = pending_events[event_id]
        
        # Ensure we pass the positions and times in the same order
        positions = []
        times = []
        for i in range(5):
            positions.append(SENSOR_POSITIONS[i])
            times.append(readings[i])
            
        result = localize_event(positions, times)
        
        if result['success']:
            event_record = {
                "event_id": event_id,
                "x": result['x'],
                "y": result['y'],
                "t_emit": result['t_emit'],
                "received_at": time.time(),
                "error_cost": result['cost']
            }
            localized_events.append(event_record)
            
            # Keep only the last 50 events to avoid memory leak
            if len(localized_events) > 50:
                localized_events.pop(0)
                
            print(f"[LOCALIZED] Event {event_id} at ({result['x']:.2f}, {result['y']:.2f})")
            
        # Clean up pending
        del pending_events[event_id]
        
    return jsonify({"status": "received"}), 200

@app.route('/api/events', methods=['GET'])
def get_events():
    return jsonify({
        "events": localized_events,
        "nodes": SENSOR_POSITIONS
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
