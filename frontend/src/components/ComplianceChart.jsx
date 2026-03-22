import React, { useMemo } from 'react';
import ReactApexChart from 'react-apexcharts';

const normalizeNumbers = (arr, fallback = []) => {
  if (!Array.isArray(arr)) return fallback;
  return arr.map((n) => {
    const num = Number(n);
    return Number.isFinite(num) ? num : 0;
  });
};

const colorForLabel = (label, isDarkMode) => {
      const key = String(label || '').toLowerCase();
      if (key.includes('pass')) return '#10b981';
      if (key.includes('fail')) return '#ef4444';
      if (key.includes('error') || key.includes('err')) return '#f59e0b';
      if (key.includes('skip')) return isDarkMode ? 'rgba(148,163,184,0.55)' : 'rgba(71,85,105,0.45)';
      return isDarkMode ? 'rgba(148,163,184,0.55)' : 'rgba(71,85,105,0.45)';
    };

// ApexCharts-backed replacement for the old Chart.js component.
// Keeps the same props API used by Dashboard.jsx:
// - chartType: 'doughnut' | 'pie' | 'bar'
// - labelsInput: string[]
// - dataInput: number[]
// - isDarkMode: boolean
const ComplianceChart = ({ chartType = 'doughnut', dataInput = [1, 1], labelsInput = [], isDarkMode = true }) => {
  const isBar = chartType === 'bar';

  const {
    series,
    options,
    height,
  } = useMemo(() => {
    const textColor = isDarkMode ? '#ffffff' : '#1e293b';
    const mutedText = isDarkMode ? 'rgba(160,165,175,0.95)' : 'rgba(71,85,105,0.95)';
    const grid = isDarkMode ? 'rgba(148,163,184,0.12)' : 'rgba(15,23,42,0.08)';
    const tooltipTheme = isDarkMode ? 'dark' : 'light';
    const fontFamily = '"League Spartan", "Inter", system-ui, -apple-system, "Segoe UI", Arial';

    const normalized = normalizeNumbers(dataInput, [1, 1]);

    if (isBar) {
      const categories = Array.isArray(labelsInput) && labelsInput.length > 0
        ? labelsInput.map((x) => String(x))
      : normalized.map((_, i) => `#${i + 1}`);

      const values = normalized;
        const avg = values.length > 0 ? (values.reduce((a, b) => a + b, 0) / values.length) : 0;

      return {
        series: [
          {
            name: 'Compliance %',
            type: 'column',
            data: values,
          },
          {
            name: 'Trend',
            type: 'line',
            data: values.map(() => Math.round(avg * 10) / 10),
          },
        ],
        height: '100%',
        options: {
          chart: {
            type: 'line',
            stacked: false,
            toolbar: { show: false },
            zoom: { enabled: false },
            background: 'transparent',
            fontFamily,
            animations: { enabled: true, easing: 'easeinout', speed: 650 },
            foreColor: mutedText,
          },
          theme: { mode: isDarkMode ? 'dark' : 'light' },
          grid: {
            borderColor: grid,
            strokeDashArray: 3,
            padding: { top: 12, right: 14, bottom: 6, left: 12 },
          },
          xaxis: {
            categories,
            labels: { style: { colors: mutedText, fontWeight: 600 } },
            axisBorder: { show: false },
            axisTicks: { show: false },
            tooltip: { enabled: false },
          },
          yaxis: {
            min: 0,
            max: 100,
            tickAmount: 5,
            labels: {
              formatter: (v) => `${Math.round(v)}`,
              style: { colors: mutedText, fontWeight: 600 },
            },
          },
          legend: {
            show: true,
            position: 'bottom',
            fontSize: '12px',
            labels: { colors: mutedText },
            markers: { radius: 12, width: 8, height: 8 },
            itemMargin: { horizontal: 10, vertical: 6 },
          },
          tooltip: {
            theme: tooltipTheme,
            fillSeriesColor: false,
            marker: { show: false },
            style: { fontSize: '12px', fontFamily },
            x: { show: true },
            y: { formatter: (v) => `${Math.round(v)}%` },
          },
          stroke: {
            width: [0, 2.5],
            curve: 'straight',
          },
          markers: {
            size: 0,
            strokeWidth: 0,
          },
          colors: ['rgba(16,185,129,0.55)', 'rgba(16,185,129,0.95)'],
          plotOptions: {
            bar: {
              borderRadius: 10,
              columnWidth: '42%',
            },
          },
          dataLabels: { enabled: false },
        },
      };
    }

    // Pie / Donut
    const defaultLabels = ['Pass', 'Fail'];
    const rawLabels = Array.isArray(labelsInput) && labelsInput.length > 0 ? labelsInput : defaultLabels;
    const labels = rawLabels.map((x) => String(x));
    const values = labels.map((_, i) => Number(normalized[i] || 0));

    const sum = values.reduce((a, b) => a + b, 0);
    const hasData = sum > 0;

    const safeLabels = hasData ? labels : ['No data'];
    const safeValues = hasData ? values : [1];
    const colors = hasData
      ? safeLabels.map((l) => colorForLabel(l, isDarkMode))
      : [isDarkMode ? 'rgba(148,163,184,0.25)' : 'rgba(71,85,105,0.25)'];

    const passIdx = safeLabels.findIndex((l) => String(l).toLowerCase().includes('pass'));
    const failIdx = safeLabels.findIndex((l) => String(l).toLowerCase().includes('fail'));
    const pass = passIdx >= 0 ? Number(safeValues[passIdx] || 0) : 0;
    const fail = failIdx >= 0 ? Number(safeValues[failIdx] || 0) : 0;
    const denom = pass + fail;
    const compliancePct = denom > 0 ? Math.round((pass / denom) * 100) : null;
    const centerText = hasData ? (compliancePct === null ? '—' : `${compliancePct}%`) : '—';
    const centerSub = hasData ? 'COMPLIANCE' : 'NO RESULTS';

    const apexType = chartType === 'pie' ? 'pie' : 'donut';

    return {
      series: safeValues,
      height: '100%',
      options: {
        chart: {
          type: apexType,
          toolbar: { show: false },
          background: 'transparent',
          fontFamily,
          animations: { enabled: true, easing: 'easeinout', speed: 650 },
          foreColor: mutedText,
        },
        theme: { mode: isDarkMode ? 'dark' : 'light' },
        labels: safeLabels,
        colors,
        legend: {
          show: true,
          position: 'bottom',
          fontSize: '12px',
          labels: { colors: mutedText },
          markers: { radius: 12, width: 8, height: 8 },
          itemMargin: { horizontal: 10, vertical: 6 },
        },
        stroke: {
          show: false,
          width: 0,
        },
        dataLabels: {
          enabled: false,
        },
        tooltip: {
          theme: tooltipTheme,
          fillSeriesColor: false,
          marker: { show: false },
          style: { fontSize: '12px', fontFamily },
          y: {
            formatter: (value) => {
              if (!hasData) return `${value}`;
              const total = safeValues.reduce((a, b) => a + b, 0);
              const pct = total > 0 ? ((Number(value || 0) / total) * 100).toFixed(1) : '0.0';
              return `${value} (${pct}%)`;
            },
          },
        },
        plotOptions: {
          pie: {
            expandOnClick: false,
            donut: {
              size: chartType === 'doughnut' ? '70%' : '0%',
              labels: {
                show: chartType === 'doughnut',
                name: {
                  show: true,
                  offsetY: 22,
                  color: mutedText,
                  fontSize: '12px',
                  fontWeight: 600,
                  formatter: () => centerSub,
                },
                value: {
                  show: true,
                  offsetY: -6,
                  color: textColor,
                  fontSize: '34px',
                  fontWeight: 700,
                  formatter: () => centerText,
                },
              },
            },
          },
        },
        responsive: [
          {
            breakpoint: 480,
            options: {
              legend: { fontSize: '11px' },
            },
          },
        ],
      },
    };
  }, [chartType, dataInput, labelsInput, isDarkMode, isBar]);

  const type = isBar ? 'line' : (chartType === 'pie' ? 'pie' : 'donut');

  // Fill parent container (Dashboard controls height via CSS).
  return (
    <div className={`compliance-chart ${isBar ? 'chart-bar' : 'chart-pie'}`} style={{ width: '100%', height: '100%' }}>
      <ReactApexChart options={options} series={series} type={type} height={height} />
    </div>
  );
};

export default ComplianceChart;