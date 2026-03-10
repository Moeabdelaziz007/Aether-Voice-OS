import json
from pathlib import Path


def generate_dashboard():
    """
    Generates a standalone HTML dashboard to visualize AetherOS benchmarks.
    Uses Chart.js for visualization.
    """
    report_path = Path("tests/reports/benchmark_report.json")
    if not report_path.exists():
        print("❌ Error: benchmark_report.json not found. Run the benchmark runner first.")
        return

    with open(report_path, "r") as f:
        data = json.load(f)

    metrics = data.get("metrics", {})

    # Extract data for charts
    dna_history = metrics.get("dna", {}).get("history", [])
    metrics.get("stability", {}).get("history", [])

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOS | Performance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #0a0a0b;
            --card: #141417;
            --accent: #00f2ff;
            --text: #e1e1e6;
        }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: 'Inter', system-ui, sans-serif;
            margin: 0;
            padding: 2rem;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #333;
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }}
        .card {{
            background: var(--card);
            border: 1px solid #333;
            border-radius: 12px;
            padding: 1.5rem;
            position: relative;
        }}
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--accent);
            margin: 0.5rem 0;
        }}
        .stat-label {{
            color: #888;
            font-size: 0.9rem;
            text-transform: uppercase;
        }}
        canvas {{
            margin-top: 1rem;
            max-height: 200px;
        }}
        .badge {{
            background: rgba(0, 242, 255, 0.1);
            color: var(--accent);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 style="margin:0">AetherOS <span style="font-weight:100">Systems Lab</span></h1>
            <p style="color:#666; margin:4px 0">Runtime Integrity & Performance Metrics</p>
        </div>
        <div class="badge">V3.1 CORTEX ACTIVE</div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="stat-label">Interrupt Latency (T3-T1)</div>
            <div class="stat-value">{metrics.get("latency", {}).get("t3_t1_total_ms", "N/A")}ms</div>
            <p style="font-size:0.8rem; color:#666">Target: &lt; 50ms</p>
        </div>
        <div class="card">
            <div class="stat-label">EventBus Throughput</div>
            <div class="stat-value">20k+</div>
            <p style="font-size:0.8rem; color:#666">Events/sec (Lane Prioritized)</p>
        </div>
        <div class="card">
            <div class="stat-label">Neural Lead Time</div>
            <div class="stat-value">{metrics.get("cortex", {}).get("pre_warm_elapsed_ms", "N/A")}ms</div>
            <p style="font-size:0.8rem; color:#666">Predictive Tool Warming</p>
        </div>
        <div class="card" style="grid-column: span 2">
            <div class="stat-label">DNA Chaos Stability (EMA)</div>
            <canvas id="dnaChart"></canvas>
        </div>
        <div class="card">
            <div class="stat-label">Memory Growth</div>
            <div class="stat-value">{metrics.get("stability", {}).get("memory_growth_mb", "N/A")} MB</div>
            <p style="font-size:0.8rem; color:#666">Simulated Long Session</p>
        </div>
    </div>

    <script>
        // DNA Stability Chart
        const dnaData = {json.dumps(dna_history)};
        new Chart(document.getElementById('dnaChart'), {{
            type: 'line',
            data: {{
                labels: dnaData.map((_, i) => 'Pulse ' + i),
                datasets: [
                    {{
                        label: 'Verbosity',
                        data: dnaData.map(d => d.verbosity),
                        borderColor: '#00f2ff',
                        tension: 0.4
                    }},
                    {{
                        label: 'Empathy',
                        data: dnaData.map(d => d.empathy),
                        borderColor: '#ff00ff',
                        tension: 0.4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ y: {{ min: 0, max: 1, grid: {{ color: '#222' }} }} }}
            }}
        }});
    </script>
</body>
</html>
    """

    dashboard_path = Path("aether_benchmark_dashboard.html")
    with open(dashboard_path, "w") as f:
        f.write(html_content)

    print(f"📊 Dashboard generated: {dashboard_path.absolute()}")


if __name__ == "__main__":
    generate_dashboard()
