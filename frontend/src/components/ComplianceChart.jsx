//This component establishes a chart to display the number of scan items which returned as passed, requiring attention, or failed
//Last updated 18 September 2025
//Recomended next changes:
//  -add a switch case for more chart types besides just pie and doughnot. Some of the chart types have slightly different syntax to each other so a little more work is needed on this. 
// - the legend is functional but the text doesn't look amazing. Played around with font settings and layout but can't get it to look quite right. Worth reviewing!

//Note: no css for this component as this is purely javascript (no JSX) and the libary in use (charts.js) has its own parameters for styling  

//To render this component:
//import ComplianceChart from './components/ComplianceChart';
//<ComplianceChart chartType={selectedChartType} dataInput = {[array of three numbers]}></ComplianceChart>
//'doughnut' and 'pie' are current options for selectedChartType

import React, { useRef, useEffect } from 'react';

// Imports only the minimum required components below
import {
  Chart as ChartJS,
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title,
  DoughnutController,
} from 'chart.js';

// Plugin: draw center text for doughnut charts (e.g. "40%" / "COMPLIANCE")
const CenterTextPlugin = {
  id: 'centerText',
  beforeDraw(chart, _args, options) {
    const opts = options || {};
    if (!opts.display) return;
    if (!chart || !chart.ctx) return;
    const { ctx, chartArea } = chart;
    if (!chartArea) return;

    const text = String(opts.text || '').trim();
    const subtext = String(opts.subtext || '').trim();
    if (!text && !subtext) return;

    const cx = (chartArea.left + chartArea.right) / 2;
    const cy = (chartArea.top + chartArea.bottom) / 2;

    ctx.save();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Main text
    if (text) {
      ctx.fillStyle = opts.color || '#ffffff';
      ctx.font = `700 ${opts.fontSize || 34}px "League Spartan", system-ui, -apple-system, "Segoe UI", Arial`;
      ctx.fillText(text, cx, cy - (subtext ? 8 : 0));
    }

    // Subtext
    if (subtext) {
      ctx.fillStyle = opts.subColor || 'rgba(148,163,184,0.95)';
      ctx.font = `600 ${opts.subFontSize || 12}px system-ui, -apple-system, "Segoe UI", Arial`;
      ctx.fillText(subtext.toUpperCase(), cx, cy + (text ? 18 : 0));
    }

    ctx.restore();
  },
};

// Plugin: draw a uniform background behind the chart within the canvas.
// This reduces visible aliasing/noise on arc edges when the UI behind the canvas is a gradient / blurred surface.
const CanvasBackgroundPlugin = {
  id: 'canvasBackground',
  beforeDraw(chart, _args, options) {
    const color = options?.color;
    if (!color) return;
    const { ctx, width, height } = chart;
    if (!ctx || !width || !height) return;
    ctx.save();
    // Draw behind everything already drawn.
    ctx.globalCompositeOperation = 'destination-over';
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, width, height);
    ctx.restore();
  },
};


ChartJS.register(
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  DoughnutController,
  Title,
  CenterTextPlugin,
  CanvasBackgroundPlugin
);

//Accepts chartType and dataInput as parameters. ChartType currently supports doughnut and pie chart, more to be added later.
//Also needs to be provided with isDarkMode to copy theming from parent.
//dataInput can be:
// - [issues, pass] (preferred)
//This should be made more robust in future. For now, since the graph is only used for one very consistent thing, this is functional. 
//Fallback to 1,1,1 as array if error in data.
// For bar charts:
// - Provide `labelsInput` (x-axis labels) and `dataInput` (numbers).
const ComplianceChart = ({ chartType = 'doughnut', dataInput = [1, 1], labelsInput = [], isDarkMode = true }) => {
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);

  const getTextColor = (darkMode) => {
    return darkMode ? '#ffffff' : '#1e293b';
  };

  useEffect(() => {
    if (!chartRef.current) return;
    const ctx = chartRef.current.getContext('2d');
    const textColor = getTextColor(isDarkMode);
    const mutedText = isDarkMode ? 'rgba(160,165,175,0.95)' : 'rgba(71,85,105,0.95)';
    // Match the dashboard "card" surface so canvas edges blend consistently.
    const canvasBg = isDarkMode ? 'rgba(255, 255, 255, 0.03)' : '#ffffff';
   
    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy();
    }

    const normalized = Array.isArray(dataInput) ? dataInput.map(n => Number(n || 0)) : [1, 1];

    const isBar = chartType === 'bar';

    // -------------------------
    // Doughnut / Pie (2 slices: Issues vs Pass)
    // -------------------------
    const pieLabels = ['Issues', 'Pass'];
    const pieColors = ['#ef4444', '#10b981'];
    const pieValues = normalized.length >= 2 ? [normalized[0], normalized[1]] : [1, 1];

    // Handle "no data" (avoid empty chart / NaN %)
    const sum = (isBar ? normalized : pieValues).reduce((a, b) => a + b, 0);
    const hasData = sum > 0;
    const safePieValues = hasData ? pieValues : [1, 0];
    const safePieLabels = hasData ? pieLabels : ['No data', ''];
    const safePieColors = hasData ? pieColors : [isDarkMode ? 'rgba(148,163,184,0.25)' : 'rgba(71,85,105,0.25)', 'rgba(0,0,0,0)'];

    // Center text: show compliance % for 2-slice (issues/pass) view
    const pass = Number(pieValues[1] || 0);
    const totalForPct = Number(pieValues[0] || 0) + Number(pieValues[1] || 0);
    const pct = totalForPct > 0 ? Math.round((pass / totalForPct) * 100) : null;
    const centerText = pct === null ? '—' : `${pct}%`;
    const centerSubtext = 'compliance';

    // -------------------------
    // Data blocks (pie vs bar)
    // -------------------------
    const pieData = {
      labels: safePieLabels,
      datasets: [{
        data: safePieValues,
        backgroundColor: safePieColors,
        // Use a subtle border in the same color as the canvas background.
        borderColor: canvasBg,
        borderWidth: chartType === 'doughnut' ? 3 : 2,
        hoverOffset: 0,
        spacing: chartType === 'doughnut' ? 2 : 0,
        borderRadius: chartType === 'doughnut' ? 10 : 0,
      }]
    };

    const barLabels = Array.isArray(labelsInput) && labelsInput.length > 0
      ? labelsInput.map(x => String(x))
      : normalized.map((_, i) => `#${i + 1}`);

    const barData = {
      labels: barLabels,
      datasets: [{
        label: 'Compliance %',
        data: hasData ? normalized : [0],
        backgroundColor: 'rgba(16,185,129,0.55)',
        borderColor: 'rgba(16,185,129,0.95)',
        borderWidth: 1,
        borderRadius: 10,
        maxBarThickness: 44,
      }]
    };

    //CONFIG AREA
    //Main chart area config
    const commonPlugins = {
      canvasBackground: {
        color: canvasBg,
      },
      tooltip: {
        position: 'nearest',
        backgroundColor: isDarkMode ? 'rgba(2, 6, 23, 0.92)' : 'rgba(255, 255, 255, 0.92)',
        titleColor: textColor,
        bodyColor: textColor,
        borderColor: isDarkMode ? 'rgba(59,130,246,0.25)' : 'rgba(15,23,42,0.15)',
        borderWidth: 1,
        padding: 10,
      },
      legend: {
        display: true,
        position: 'bottom',
        align: 'center',
        labels: {
          padding: 18,
          color: mutedText,
          usePointStyle: true,
          pointStyle: 'circle',
          boxWidth: 10,
          boxHeight: 10,
          font: {
            size: 12,
            weight: '600',
          },
        }
      },
    };

    const config = isBar ? {
      type: 'bar',
      data: barData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        devicePixelRatio: (typeof window !== 'undefined' && window.devicePixelRatio) ? window.devicePixelRatio : 1,
        layout: {
          padding: { top: 18, bottom: 14, left: 18, right: 18 }
        },
        scales: {
          x: {
            ticks: { color: mutedText, font: { size: 12, weight: '600' } },
            grid: { color: isDarkMode ? 'rgba(148,163,184,0.12)' : 'rgba(15,23,42,0.08)' },
          },
          y: {
            min: 0,
            max: 100,
            ticks: { color: mutedText, font: { size: 12, weight: '600' }, stepSize: 10 },
            grid: { color: isDarkMode ? 'rgba(148,163,184,0.12)' : 'rgba(15,23,42,0.08)' },
          },
        },
        plugins: {
          ...commonPlugins,
        },
        animation: { duration: 650 },
      }
    } : {
      type: 'doughnut',
      data: pieData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        devicePixelRatio: (typeof window !== 'undefined' && window.devicePixelRatio) ? window.devicePixelRatio : 1,
        cutout: chartType === 'doughnut' ? '70%' : '0%',
        radius: '92%',
        layout: {
          padding: { top: 18, bottom: 14, left: 18, right: 18 }
        },
        plugins: {
          ...commonPlugins,
          centerText: {
            display: chartType === 'doughnut',
            text: hasData ? centerText : '—',
            subtext: hasData ? centerSubtext : 'no results',
            color: textColor,
            subColor: mutedText,
            fontSize: 34,
            subFontSize: 12,
          },
          tooltip: {
            ...commonPlugins.tooltip,
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const value = context.parsed;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0.0';
                if (!label) return '';
                return ` ${label}: ${value} (${percentage}%)`;
              }
            }
          }
        },
        animation: {
          animateScale: true,
          animateRotate: true
        }
      }
    };




    //Instantiate the chart
    chartInstanceRef.current = new ChartJS(ctx, config);

    //Destroy the existing chart (if any) 
    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }
    };
  }, [chartType, dataInput, labelsInput, isDarkMode]); //Re-render if the chartType or data is changed 

  //Scale to fit the max size provided with the card
  return (
    <div style={{ width: '100%', height: '100%', padding: '0px' }}> 
      <canvas ref={chartRef} style={{ width: '100%', height: '100%' }}></canvas>
    </div>
  );
};

export default ComplianceChart;