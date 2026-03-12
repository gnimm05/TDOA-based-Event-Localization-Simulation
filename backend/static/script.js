const canvas = document.getElementById('localizationCanvas');
const ctx = canvas.getContext('2d');
const alertTbody = document.getElementById('alert-tbody');
const anomalyCountEl = document.getElementById('anomaly-count');
const telemetryContainer = document.getElementById('telemetry-container');

// Canvas dimensions and mapping
const WIDTH = canvas.width;
const HEIGHT = canvas.height;
const GRID_SIZE = 100; // Physical meters
const SCALE = WIDTH / Math.max(GRID_SIZE, 1); // Pixels per meter

let knownNodes = {};
let latestTelemetry = {};

function drawGrid() {
    ctx.clearRect(0, 0, WIDTH, HEIGHT);
    
    // Draw subtle grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for(let i = 0; i <= GRID_SIZE; i += 10) {
        let pos = i * SCALE;
        ctx.beginPath();
        ctx.moveTo(pos, 0);
        ctx.lineTo(pos, HEIGHT);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(0, pos);
        ctx.lineTo(WIDTH, pos);
        ctx.stroke();
    }
}

function drawNodes() {
    // #2ea043
    ctx.fillStyle = '#2ea043';
    ctx.strokeStyle = '#2ea043';
    ctx.lineWidth = 2;
    
    for (let id in knownNodes) {
        let pos = knownNodes[id];
        let cx = pos[0] * SCALE;
        let cy = (GRID_SIZE - pos[1]) * SCALE; // Invert Y for cartesian
        let z = pos[2];
        
        // Node size scales slightly with height
        let r = 6 + (z * 0.3);
        
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.fill();
        
        // Glow
        ctx.beginPath();
        ctx.arc(cx, cy, r + 8, 0, Math.PI * 2);
        ctx.stroke();
        
        ctx.fillStyle = '#fff';
        ctx.font = '12px Inter';
        ctx.fillText(`Node ${id} (z:${z.toFixed(0)}m)`, cx + 15, cy - 10);
        ctx.fillStyle = '#2ea043';
    }
}

function drawEvents(events) {
    ctx.fillStyle = '#ff7b72'; // accent-red
    
    events.forEach(ev => {
        let cx = ev.x * SCALE;
        let cy = (GRID_SIZE - ev.y) * SCALE;
        let r = 5 + (ev.z * 0.5); // Larger circle if higher up
        
        // Pulse ring based on recency
        let age = (Date.now() / 1000) - ev.received_at;
        
        if (age < 2.0) {
            let radius = r * 2 + (age * 30);
            let alpha = Math.max(0, 1.0 - (age / 2.0));
            ctx.strokeStyle = `rgba(255, 123, 114, ${alpha})`;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(cx, cy, radius, 0, Math.PI * 2);
            ctx.stroke();
        }
        
        // Core point
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw Z text
        ctx.fillStyle = '#ff7b72';
        ctx.font = '10px monospace';
        ctx.fillText(`Z: ${ev.z.toFixed(1)}m`, cx + 10, cy + 15);
    });
}

function renderTelemetry() {
    telemetryContainer.innerHTML = '';
    
    // Convert to array and sort by node ID
    let keys = Object.keys(latestTelemetry).sort((a,b) => parseInt(a) - parseInt(b));
    let systemSos = 0;
    
    keys.forEach(k => {
        let t = latestTelemetry[k];
        let age = (Date.now() / 1000) - t.last_seen;
        
        // If haven't seen in 10s, mark stale
        let isStale = age > 10;
        let statusColor = isStale ? 'var(--text-secondary)' : 'var(--text-primary)';
        
        let html = `
            <div class="node-stats" style="color: ${statusColor}">
                <div class="node-id-badge">${k}</div>
                <div class="stat-group">
                    <div class="stat-item">
                        <span class="val">${t.temp_c.toFixed(1)}°C</span>
                        <span class="lbl">Temp</span>
                    </div>
                    <div class="stat-item">
                        <span class="val">${t.noise_db.toFixed(1)} dB</span>
                        <span class="lbl">Noise</span>
                    </div>
                    <div class="stat-item">
                        <span class="val">${t.battery_v.toFixed(2)}v</span>
                        <span class="lbl">Batt</span>
                    </div>
                </div>
            </div>
        `;
        telemetryContainer.innerHTML += html;
    });
}

function formatTime(unixTime) {
    let d = new Date(unixTime * 1000);
    return d.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' });
}

function updateTable(events) {
    alertTbody.innerHTML = '';
    // Reverse events to show newest first
    let reversed = [...events].reverse();
    
    // Extract the dynamic SOS from the latest event to show in the UI if we want to
    let lastSos = reversed.length > 0 ? reversed[0].dynamic_sos : 343.0;
    
    reversed.forEach(ev => {
        let tr = document.createElement('tr');
        
        // Flash new rows
        let age = (Date.now() / 1000) - ev.received_at;
        if (age < 2.0) {
            tr.style.backgroundColor = 'rgba(255, 123, 114, 0.15)';
            setTimeout(() => {
                tr.style.transition = 'background-color 2s';
                tr.style.backgroundColor = 'transparent';
            }, 50);
        }
        
        tr.innerHTML = `
            <td>${formatTime(ev.received_at)}</td>
            <td><span class="event-id">${ev.event_id}</span></td>
            <td class="coord">(${ev.x.toFixed(1)}, ${ev.y.toFixed(1)}, ${ev.z.toFixed(1)})</td>
        `;
        alertTbody.appendChild(tr);
    });
    
    // Could optionally append SOS to the telemetry container bottom
    if(reversed.length > 0) {
        let sosDiv = document.getElementById('system-sos');
        if(!sosDiv) {
            sosDiv = document.createElement('div');
            sosDiv.id = 'system-sos';
            sosDiv.className = 'sos-indicator';
            telemetryContainer.appendChild(sosDiv);
        }
        sosDiv.innerHTML = `Dynamic V<sub>sound</sub>: ${lastSos.toFixed(2)} m/s`;
    }
}

function fetchState() {
    fetch('/api/events')
        .then(res => res.json())
        .then(data => {
            if(data.nodes) knownNodes = data.nodes;
            if(data.telemetry) latestTelemetry = data.telemetry;
            
            drawGrid();
            drawNodes();
            renderTelemetry();
            
            if(data.events) {
                drawEvents(data.events);
                updateTable(data.events);
                anomalyCountEl.textContent = data.events.length;
            }
        })
        .catch(err => console.error("Polling error:", err));
}

// Initial draw
drawGrid();

// Render loop for smooth animations and data fetching
setInterval(() => {
    fetchState();
}, 500);
