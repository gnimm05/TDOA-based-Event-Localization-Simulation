const canvas = document.getElementById('localizationCanvas');
const ctx = canvas.getContext('2d');
const alertTbody = document.getElementById('alert-tbody');
const anomalyCountEl = document.getElementById('anomaly-count');

// Canvas dimensions and mapping
const WIDTH = canvas.width;
const HEIGHT = canvas.height;
const GRID_SIZE = 100; // Physical meters
const SCALE = WIDTH / Math.max(GRID_SIZE, 1); // Pixels per meter

let knownNodes = {};
let previousEventCount = 0;

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
        
        ctx.beginPath();
        ctx.arc(cx, cy, 6, 0, Math.PI * 2);
        ctx.fill();
        
        // Glow
        ctx.beginPath();
        ctx.arc(cx, cy, 14, 0, Math.PI * 2);
        ctx.stroke();
        
        ctx.fillStyle = '#fff';
        ctx.font = '12px Inter';
        ctx.fillText(`Node ${id}`, cx + 15, cy - 10);
        ctx.fillStyle = '#2ea043';
    }
}

function drawEvents(events) {
    ctx.fillStyle = '#ff7b72'; // accent-red
    
    events.forEach(ev => {
        let cx = ev.x * SCALE;
        let cy = (GRID_SIZE - ev.y) * SCALE;
        
        // Pulse ring based on recency
        let age = (Date.now() / 1000) - ev.received_at;
        
        if (age < 2.0) {
            let radius = 10 + (age * 30);
            let alpha = Math.max(0, 1.0 - (age / 2.0));
            ctx.strokeStyle = `rgba(255, 123, 114, ${alpha})`;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(cx, cy, radius, 0, Math.PI * 2);
            ctx.stroke();
        }
        
        // Core point
        ctx.beginPath();
        ctx.arc(cx, cy, 5, 0, Math.PI * 2);
        ctx.fill();
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
            <td class="coord">(${ev.x.toFixed(1)}m, ${ev.y.toFixed(1)}m)</td>
        `;
        alertTbody.appendChild(tr);
    });
}

function fetchState() {
    fetch('/api/events')
        .then(res => res.json())
        .then(data => {
            if(data.nodes) knownNodes = data.nodes;
            
            drawGrid();
            drawNodes();
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
}, 500); // 2 FPS polling is plenty fast for UI responsiveness
