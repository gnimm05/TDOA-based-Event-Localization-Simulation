# TDOA-based Event Localization Simulation (3D)

![3D Localization Simulation](https://img.shields.io/badge/Status-Active-brightgreen)
![Python 3.x](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey)

## Overview
This project is a 3D Time Difference of Arrival (TDOA) based acoustic event localization simulation. It models an environment with simulated embedded sensor nodes (e.g., ESP32 equipped with BME280/INMP441 sensors) that detect acoustic anomalies. These nodes transmit timestamped data via HTTP to a central Flask API, which correlates the signals and calculates the 3D position (X, Y, Z) and emission time of the event.

### Key Features
- **3D Localization**: Accurately calculates the exact X, Y, and Z coordinates of acoustic events using a volumetric grid search algorithm based on TDOA.
- **Dynamic Speed of Sound Compensation**: Continuously adjusts the speed of sound calculation by taking real-time simulated telemetry (ambient temperature) into account.
- **Simulated IoT Telemetry**: Sensor nodes report environmental metrics such as temperature, noise floor (dB), and battery voltage alongside their acoustic timestamps.
- **Robust Flask REST API**: A backend server capable of receiving multi-node asynchronous data, holding pending events, and performing full localization when all required node data is received.

## Project Structure
```text
TDOA-based-Event-Localization-Simulation/
│
├── backend/
│   ├── app.py             # Main Flask API for receiving sensor telemetry & serving localized data
│   ├── tdoa.py            # Core logic: 3D volumetric search & TDOA math
│   ├── test_tdoa.py       # Unit tests verifying the TDOA localization algorithm
│   └── templates/
│       └── index.html     # Frontend dashboard for visualizing localized events
│
├── simulation/
│   └── simulate_nodes.py  # Python script simulating 5 independent IoT sensors firing acoustic events
│
└── test.py                # Additional top-level test script
```

## Algorithm Details
The core localization mechanism (`tdoa.py`) determines the 3D origin of an acoustic sound by observing the time delay of its arrival across 5 strategically placed nodes. 
It searches for the smallest overall alignment cost using a 3D grid volume search, and compensates dynamically for temperature changes which alter the absolute speed of sound according to the formula: 
`c = 331.3 + (0.606 * T)` where `T` is average ambient temperature in Celsius.

## Getting Started

### Prerequisites
- Python 3.x
- Flask (`pip install Flask`)
- Requests (`pip install requests`)

### Running the Application

1. **Start the Backend server:**
   Navigate into the `backend` directory and run the API server. This will host the API endpoint and the dashboard.
   ```bash
   cd backend
   python app.py
   ```
   The backend will start processing on `http://127.0.0.1:5000`.

2. **Start the Sensor Simulation:**
   In another terminal, navigate to the `simulation` directory and run the simulation script. It will constantly spawn new simulated acoustic events and send mock telemetry to the backend, mimicking real-world clock drift, DSP noise, and network latency.
   ```bash
   cd simulation
   python simulate_nodes.py
   ```

3. **View the Dashboard:**
   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser to view the localized events in real-time.

## License
MIT License.
