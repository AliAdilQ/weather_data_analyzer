(() => {
  const node = document.getElementById('chart-data');
  if (!node || typeof Chart === 'undefined') return;
  const colors = ['#237b68', '#79b5a4', '#edb86b', '#829cc7', '#ca8f92', '#b1a0c7', '#7ac4cc', '#abb76b'];
  Chart.defaults.font.family = 'Inter, Segoe UI, sans-serif';
  Chart.defaults.color = '#73817c';
  Object.entries(JSON.parse(node.textContent)).forEach(([id, data]) => {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const round = ['condition', 'source'].includes(id);
    const trend = ['temperature', 'humidity', 'wind_speed'].includes(id);
    new Chart(canvas, {
      type: round ? 'doughnut' : trend ? 'line' : 'bar',
      data: { labels: data.labels, datasets: [{
        label: {temperature: 'Temperature (°C)', humidity: 'Humidity (%)', wind_speed: 'Wind (m/s)', comparison: 'Temperature (°C)'}[id] || 'Count',
        data: data.values, borderColor: trend ? colors[0] : 'transparent',
        backgroundColor: trend ? '#237b6815' : colors, fill: trend,
        tension: 0.35, pointRadius: 3, borderWidth: 2, borderRadius: 6
      }] },
      options: { responsive: true, maintainAspectRatio: false, animation: false,
        plugins: { legend: { display: round, position: 'bottom', labels: {usePointStyle: true, padding: 20} } },
        ...(round ? {cutout: '72%'} : {scales: {
          x: {grid: {display: false}, ticks: {maxTicksLimit: 7, maxRotation: 0}},
          y: {beginAtZero: !trend, grid: {color: '#edf1ee'}, border: {display: false}}
        }})
      }
    });
  });
})();
