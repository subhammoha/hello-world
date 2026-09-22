async function fetchReadings(kind) {
  const res = await fetch(`/api/readings?kind=${encodeURIComponent(kind)}`);
  return res.json();
}

async function fetchSleepSummary() {
  const res = await fetch("/api/sleep_summary");
  return res.json();
}

function formatLabel(unixSeconds) {
  return new Date(unixSeconds * 1000).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function renderLineCharts() {
  const canvases = document.querySelectorAll(".reading-chart");
  for (const canvas of canvases) {
    const kind = canvas.dataset.kind;
    const rows = await fetchReadings(kind);
    new Chart(canvas, {
      type: "line",
      data: {
        labels: rows.map((r) => formatLabel(r.captured_unix)),
        datasets: [
          {
            label: kind,
            data: rows.map((r) => r.value),
            borderColor: "#3b82f6",
            tension: 0.2,
            pointRadius: 0,
          },
        ],
      },
      options: {
        scales: {
          x: { ticks: { maxTicksLimit: 8 } },
        },
      },
    });
  }
}

async function renderSleepChart() {
  const el = document.getElementById("sleep-chart");
  if (!el) return;
  const summary = await fetchSleepSummary();
  new Chart(el, {
    type: "bar",
    data: {
      labels: Object.keys(summary),
      datasets: [{ label: "epochs", data: Object.values(summary), backgroundColor: "#10b981" }],
    },
  });
}

renderLineCharts();
renderSleepChart();
