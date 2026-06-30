const previousReba = new Map();
const rebaHistory = []; // session-only trend data, derived purely from live /worker_status polls
const MAX_HISTORY_POINTS = 24;

const summaryIds = {
    total: "total-workers",
    safe: "safe-workers",
    monitoring: "monitoring-workers",
    warning: "warning-workers",
    alert: "alert-workers",
    highest: "highest-reba",
    average: "average-reba",
    accuracy: "system-accuracy",
};

let riskChart = null;
let trendChart = null;

function numberValue(value, digits = 1) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
        return "-";
    }

    return Number(value).toFixed(digits);
}

function normalizeKey(value) {
    return String(value || "safe")
        .trim()
        .toLowerCase()
        .replace(/\s+/g, "-");
}

function riskKey(worker) {
    const status = String(worker.status || "").toUpperCase();
    const risk = String(worker.risk || "SAFE").toUpperCase();

    if (status === "ALERT" || risk === "ALERT" || risk === "VERY HIGH") {
        return "alert";
    }

    if (risk === "HIGH") {
        return "high";
    }

    if (risk === "MEDIUM") {
        return "medium";
    }

    if (risk === "LOW") {
        return "low";
    }

    return "safe";
}

function trendFor(worker) {
    const current = Number(worker.reba || 0);
    const previous = previousReba.get(worker.id);

    previousReba.set(worker.id, current);

    if (previous === undefined || current === previous) {
        return { label: "Stable", icon: "bi-dash-lg", className: "trend-flat" };
    }

    if (current > previous) {
        return { label: "Rising", icon: "bi-arrow-up-short", className: "trend-up" };
    }

    return { label: "Improving", icon: "bi-arrow-down-short", className: "trend-down" };
}

function setText(id, value) {
    const element = document.getElementById(id);

    if (!element) {
        return;
    }

    if (element.textContent !== String(value)) {
        element.textContent = value;
        element.classList.remove("flash");
        // restart flash animation on change
        void element.offsetWidth;
        element.classList.add("flash");
    }
}

function avatarInitial(workerId) {
    return `W${workerId}`;
}

function updateSummary(workers) {
    const counts = {
        safe: 0,
        monitoring: 0,
        warning: 0,
        alert: 0,
    };

    let highest = 0;
    let totalReba = 0;
    let totalAccuracy = 0;
    let accuracyCount = 0;

    workers.forEach((worker) => {
        const status = String(worker.status || "SAFE").toUpperCase();
        const reba = Number(worker.reba || 0);
        const accuracy = Number(worker.accuracy);

        if (status === "ALERT") {
            counts.alert += 1;
        } else if (status === "WARNING" || status === "HIGH RISK") {
            counts.warning += 1;
        } else if (status === "MONITORING") {
            counts.monitoring += 1;
        } else {
            counts.safe += 1;
        }

        highest = Math.max(highest, reba);
        totalReba += reba;

        if (!Number.isNaN(accuracy) && accuracy > 0) {
            totalAccuracy += accuracy;
            accuracyCount += 1;
        }
    });

    setText(summaryIds.total, workers.length);
    setText(summaryIds.safe, counts.safe);
    setText(summaryIds.monitoring, counts.monitoring);
    setText(summaryIds.warning, counts.warning);
    setText(summaryIds.alert, counts.alert);
    setText(summaryIds.highest, highest);
    setText(summaryIds.average, workers.length ? (totalReba / workers.length).toFixed(1) : "0.0");
    setText(summaryIds.accuracy, accuracyCount ? `${(totalAccuracy / accuracyCount).toFixed(1)}%` : "--");

    return { counts, highest, average: workers.length ? totalReba / workers.length : 0 };
}

function renderTable(workers) {
    const tbody = document.getElementById("worker-table-body");

    if (!tbody) {
        return;
    }

    if (!workers.length) {
        tbody.innerHTML = '<tr><td colspan="13" class="empty-table">Waiting for worker data</td></tr>';
        return;
    }

    tbody.innerHTML = workers
        .slice()
        .sort((a, b) => Number(a.id) - Number(b.id))
        .map((worker) => {
            const risk = riskKey(worker);
            const trend = trendFor(worker);
            const statusKey = normalizeKey(worker.status);

            return `
                <tr class="row-${risk}">
                    <td>
                        <div class="worker-id-cell">
                            <span class="worker-avatar" aria-hidden="true">${avatarInitial(worker.id)}</span>
                            <strong>Worker ${worker.id}</strong>
                        </div>
                    </td>
                    <td class="mono">${numberValue(worker.back)}&deg;</td>
                    <td class="mono">${numberValue(worker.neck)}&deg;</td>
                    <td class="mono">${numberValue(worker.knee)}&deg;</td>
                    <td class="mono">${numberValue(worker.lua)}&deg;</td>
                    <td class="mono">${numberValue(worker.rua)}&deg;</td>
                    <td class="mono">${numberValue(worker.lla)}&deg;</td>
                    <td class="mono">${numberValue(worker.rla)}&deg;</td>
                    <td class="mono"><strong>${worker.reba || 0}</strong></td>
                    <td><span class="risk-badge risk-${risk}">${worker.risk || "SAFE"}</span></td>
                    <td class="mono">${numberValue(worker.unsafe_time)}s</td>
                    <td><span class="status-badge status-${statusKey}">${worker.status || "SAFE"}</span></td>
                    <td><span class="trend ${trend.className}"><i class="bi ${trend.icon}"></i>${trend.label}</span></td>
                </tr>
            `;
        })
        .join("");
}

function recommendationFor(worker) {
    const reba = Number(worker.reba || 0);

    if (reba >= 10) {
        return "Immediate ergonomic inspection recommended.";
    }

    return "Review posture, work pace, and task rotation immediately.";
}

function renderAlerts(workers) {
    const panel = document.getElementById("alerts-panel");

    if (!panel) {
        return;
    }

    const alerts = workers.filter((worker) => String(worker.status || "").toUpperCase() === "ALERT");

    if (!alerts.length) {
        panel.innerHTML = '<div class="empty-alert"><i class="bi bi-shield-check"></i>No Active Alerts</div>';
        return;
    }

    panel.innerHTML = alerts
        .map((worker) => `
            <article class="alert-item">
                <h3><i class="bi bi-exclamation-octagon-fill"></i>Worker ID ${worker.id}</h3>
                <p><strong>REBA Score:</strong> ${worker.reba || 0}</p>
                <p><strong>Unsafe Time:</strong> ${numberValue(worker.unsafe_time)} s</p>
                <p><strong>Status:</strong> ${worker.status}</p>
                <p><strong>Recommendation:</strong><br>${recommendationFor(worker)}</p>
            </article>
        `)
        .join("");
}

/* ==========================================================================
   Analytics charts — built entirely from data already returned by
   /worker_status. No backend changes, no fabricated figures.
   ========================================================================== */

function getCssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function buildRiskChart(counts) {
    const canvas = document.getElementById("risk-distribution-chart");

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    const data = [counts.safe, counts.monitoring, counts.warning, counts.alert];
    const colors = [getCssVar("--success"), getCssVar("--accent"), getCssVar("--warning"), getCssVar("--danger")];

    if (riskChart) {
        riskChart.data.datasets[0].data = data;
        riskChart.update();
        return;
    }

    riskChart = new Chart(canvas.getContext("2d"), {
        type: "doughnut",
        data: {
            labels: ["Safe", "Monitoring", "Warning", "Alert"],
            datasets: [{
                data,
                backgroundColor: colors,
                borderColor: "rgba(11,18,32,0.9)",
                borderWidth: 3,
                hoverOffset: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "68%",
            animation: { animateRotate: true, duration: 700 },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "#121826",
                    borderColor: "rgba(255,255,255,0.08)",
                    borderWidth: 1,
                    titleColor: "#F8FAFC",
                    bodyColor: "#94A3B8",
                },
            },
        },
    });
}

function buildTrendChart() {
    const canvas = document.getElementById("reba-trend-chart");

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    const labels = rebaHistory.map((point) => point.label);
    const avgData = rebaHistory.map((point) => point.average);
    const highData = rebaHistory.map((point) => point.highest);

    if (trendChart) {
        trendChart.data.labels = labels;
        trendChart.data.datasets[0].data = avgData;
        trendChart.data.datasets[1].data = highData;
        trendChart.update("none");
        return;
    }

    const ctx = canvas.getContext("2d");
    const accentGradient = ctx.createLinearGradient(0, 0, 0, 220);
    accentGradient.addColorStop(0, "rgba(37, 99, 235, 0.35)");
    accentGradient.addColorStop(1, "rgba(37, 99, 235, 0)");

    trendChart = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "Average REBA",
                    data: avgData,
                    borderColor: getCssVar("--primary"),
                    backgroundColor: accentGradient,
                    fill: true,
                    tension: 0.35,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    borderWidth: 2,
                },
                {
                    label: "Highest REBA",
                    data: highData,
                    borderColor: getCssVar("--danger"),
                    backgroundColor: "transparent",
                    fill: false,
                    tension: 0.35,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    borderWidth: 2,
                    borderDash: [4, 4],
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 400 },
            interaction: { mode: "index", intersect: false },
            scales: {
                x: {
                    ticks: { color: "#94A3B8", font: { family: "JetBrains Mono", size: 10 }, maxRotation: 0 },
                    grid: { color: "rgba(255,255,255,0.05)" },
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: "#94A3B8", font: { family: "JetBrains Mono", size: 10 } },
                    grid: { color: "rgba(255,255,255,0.05)" },
                },
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "#121826",
                    borderColor: "rgba(255,255,255,0.08)",
                    borderWidth: 1,
                    titleColor: "#F8FAFC",
                    bodyColor: "#94A3B8",
                },
            },
        },
    });
}

function updateCharts(workers, summary) {
    buildRiskChart(summary.counts);

    const now = new Date();
    const label = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });

    rebaHistory.push({ label, average: Number(summary.average.toFixed(1)), highest: summary.highest });

    if (rebaHistory.length > MAX_HISTORY_POINTS) {
        rebaHistory.shift();
    }

    buildTrendChart();
}

async function refreshDashboard() {
    try {
        const response = await fetch("/worker_status", { cache: "no-store" });

        if (!response.ok) {
            throw new Error("Unable to load worker status");
        }

        const workers = await response.json();

        const summary = updateSummary(workers);
        renderTable(workers);
        renderAlerts(workers);
        updateCharts(workers, summary);
    } catch (error) {
        console.error(error);
    }
}

async function clearWorkers() {
    const button = document.getElementById("clear-workers-btn");

    if (button) {
        button.disabled = true;
        button.textContent = "Clearing...";
    }

    try {
        const response = await fetch("/clear_workers", {
            method: "POST",
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error("Unable to clear worker data");
        }

        previousReba.clear();
        rebaHistory.length = 0;
        const summary = updateSummary([]);
        renderTable([]);
        renderAlerts([]);
        updateCharts([], summary);
    } catch (error) {
        console.error(error);
    } finally {
        if (button) {
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-trash3"></i> Clear Workers';
        }
    }
}

function showStoppedStream() {
    const streamState = document.getElementById("stream-state");
    const streamImage = document.getElementById("stream-image");
    const videoFrame = streamImage ? streamImage.closest(".video-frame") : null;

    if (streamState) {
        streamState.textContent = "Stopped";
        streamState.classList.add("stopped");
    }

    if (streamImage) {
        streamImage.removeAttribute("src");
    }

    if (videoFrame) {
        videoFrame.innerHTML = `
            <div class="empty-video">
                <i class="bi bi-camera-video-off"></i>
                <strong>Stream stopped</strong>
                <span>Start a new stream to resume monitoring.</span>
            </div>
        `;
    }
}

async function stopStream() {
    const button = document.getElementById("stop-stream-btn");

    if (button) {
        button.disabled = true;
        button.textContent = "Stopping...";
    }

    showStoppedStream();

    try {
        const response = await fetch("/stop_stream", {
            method: "POST",
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error("Unable to stop stream");
        }
    } catch (error) {
        console.error(error);

        if (button) {
            button.disabled = false;
            button.textContent = "Stop";
        }
    }
}

/* Lightweight ripple position tracking for .btn (pure CSS handles the effect) */
document.addEventListener("click", (event) => {
    const button = event.target.closest(".btn");

    if (!button) {
        return;
    }

    const rect = button.getBoundingClientRect();
    button.style.setProperty("--rx", `${event.clientX - rect.left}px`);
    button.style.setProperty("--ry", `${event.clientY - rect.top}px`);
});

const clearButton = document.getElementById("clear-workers-btn");
const stopButton = document.getElementById("stop-stream-btn");

if (clearButton) {
    clearButton.addEventListener("click", clearWorkers);
}

if (stopButton) {
    stopButton.addEventListener("click", stopStream);
}

refreshDashboard();
setInterval(refreshDashboard, 1000);
