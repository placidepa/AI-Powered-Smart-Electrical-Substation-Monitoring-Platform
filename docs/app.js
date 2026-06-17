// Initialize variables for the chart
let timeArray = [];
let voltageArray = [];
let currentArray = [];
let anomalyCount = 0;

// Populate initial dummy data
let currentTime = new Date();
for(let i = -100; i <= 0; i++) {
    let t = new Date(currentTime.getTime() + i * 1000);
    timeArray.push(t);
    voltageArray.push(110 + (Math.random() - 0.5));
    currentArray.push((400 + (Math.random() - 0.5) * 20) / 4); // Scaled current
}

// Plotly layout config
const layout = {
    template: 'plotly_dark',
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { l: 40, r: 20, t: 20, b: 40 },
    xaxis: { type: 'date' },
    yaxis: { title: 'Value' },
    legend: { orientation: 'h', y: 1.1 }
};

// Initial Plot
Plotly.newPlot('telemetry-chart', [
    { x: timeArray, y: voltageArray, name: 'Voltage (kV)', line: {color: '#00FFFF', width: 2} },
    { x: timeArray, y: currentArray, name: 'Current (A/4 scaled)', line: {color: '#FFD700', width: 2} }
], layout, {responsive: true});

// Simulate real-time data ingestion every 1 second
setInterval(() => {
    let now = new Date();
    
    // Simulate an anomaly (2% chance)
    let isAnomaly = Math.random() > 0.98;
    let newVolt = 110 + (Math.random() - 0.5);
    let newCurr = (400 + (Math.random() - 0.5) * 20) / 4;

    if (isAnomaly) {
        newVolt = newVolt * 0.7; // Voltage Sag
        newCurr = newCurr * 3.0; // Current Spike
        anomalyCount++;
        
        // Update UI Alerts
        document.getElementById('anomaly-count').innerText = anomalyCount;
        document.getElementById('anomaly-count').className = 'text-warning';
        document.getElementById('status').innerText = 'ANOMALY DETECTED';
        document.getElementById('status').className = 'text-danger';
        document.getElementById('health-score').innerText = '82.1 / 100';
        document.getElementById('health-score').className = 'text-warning';
    } else {
        document.getElementById('status').innerText = 'STABLE';
        document.getElementById('status').className = 'text-success';
    }

    // Extend plot data
    let update = {
        x: [[now], [now]],
        y: [[newVolt], [newCurr]]
    };

    // Slide the window (keep last 100 points)
    Plotly.extendTraces('telemetry-chart', update, [0, 1], 100);

}, 1000);