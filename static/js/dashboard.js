const previousReba = new Map();

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
        return { label: "→ Stable", className: "trend-flat" };
    }

    if (current > previous) {
        return { label: "↑ Increasing", className: "trend-up" };
    }

    return { label: "↓ Improving", className: "trend-down" };
}

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
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
                    <td><strong>${worker.id}</strong></td>
                    <td>${numberValue(worker.back)}</td>
                    <td>${numberValue(worker.neck)}</td>
                    <td>${numberValue(worker.knee)}</td>
                    <td>${numberValue(worker.lua)}</td>
                    <td>${numberValue(worker.rua)}</td>
                    <td>${numberValue(worker.lla)}</td>
                    <td>${numberValue(worker.rla)}</td>
                    <td><strong>${worker.reba || 0}</strong></td>
                    <td><span class="risk-badge risk-${risk}">${worker.risk || "SAFE"}</span></td>
                    <td>${numberValue(worker.unsafe_time)} s</td>
                    <td><span class="status-badge status-${statusKey}">${worker.status || "SAFE"}</span></td>
                    <td><span class="trend ${trend.className}">${trend.label}</span></td>
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
        panel.innerHTML = '<div class="empty-alert">No Active Alerts</div>';
        return;
    }

    panel.innerHTML = alerts
        .map((worker) => `
            <article class="alert-item">
                <h3>Worker ID ${worker.id}</h3>
                <p><strong>REBA Score:</strong> ${worker.reba || 0}</p>
                <p><strong>Unsafe Time:</strong> ${numberValue(worker.unsafe_time)} s</p>
                <p><strong>Status:</strong> ${worker.status}</p>
                <p><strong>Recommendation:</strong><br>${recommendationFor(worker)}</p>
            </article>
        `)
        .join("");
}

async function refreshDashboard() {
    try {
        const response = await fetch("/worker_status", { cache: "no-store" });

        if (!response.ok) {
            throw new Error("Unable to load worker status");
        }

        const workers = await response.json();

        updateSummary(workers);
        renderTable(workers);
        renderAlerts(workers);
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
        updateSummary([]);
        renderTable([]);
        renderAlerts([]);
    } catch (error) {
        console.error(error);
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = "Clear Workers";
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
