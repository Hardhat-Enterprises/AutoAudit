import React, { useMemo } from 'react';
import Chart from 'react-apexcharts';
import type { ApexOptions } from 'apexcharts';

export type ComplianceChartType = 'doughnut' | 'pie' | 'bar';

export type ComplianceChartProps = {
  chartType: ComplianceChartType;
  labels: string[];
  values: number[];
  isDarkMode?: boolean;
  /** Reserved for responsive layout; chart fills its container width. */
  sidebarWidth?: number;
};

function colorForOutcomeLabel(label: string): string {
  const u = label.toLowerCase();
  if (u.includes('pass')) return 'rgb(16, 185, 129)';
  if (u.includes('fail')) return 'rgb(239, 68, 68)';
  if (u.includes('error')) return 'rgb(249, 115, 22)';
  if (u.includes('skip')) return 'rgb(100, 116, 139)';
  return 'rgb(148, 163, 184)';
}

function useChartConfig(
  chartType: ComplianceChartType,
  labels: string[],
  values: number[],
  isDarkMode: boolean
): { options: ApexOptions; series: number[] | { name: string; data: number[] }[]; apexType: 'donut' | 'pie' | 'bar' } {
  const foreColor = isDarkMode ? 'rgb(226, 232, 240)' : 'rgb(11, 18, 32)';
  const muted = isDarkMode ? 'rgb(148, 163, 184)' : 'rgb(71, 85, 105)';

  return useMemo(() => {
    const baseChart: ApexOptions['chart'] = {
      background: 'transparent',
      toolbar: { show: false },
      animations: { enabled: true },
      fontFamily: 'Segoe UI, ui-sans-serif, system-ui, sans-serif',
    };

    const legend: ApexOptions['legend'] = {
      position: 'bottom',
      fontSize: '13px',
      labels: { colors: foreColor },
      markers: { size: 10 },
    };

    const dataLabels: ApexOptions['dataLabels'] = {
      enabled: chartType !== 'bar',
      style: { fontSize: '12px', colors: [foreColor] },
      dropShadow: { enabled: false },
    };

    const tooltip: ApexOptions['tooltip'] = {
      theme: isDarkMode ? 'dark' : 'light',
      y: {
        formatter: (val: number) => (chartType === 'bar' ? `${val}%` : String(val)),
      },
    };

    if (chartType === 'bar') {
      const options: ApexOptions = {
        chart: { ...baseChart, type: 'bar' },
        theme: { mode: isDarkMode ? 'dark' : 'light' },
        colors: ['rgb(100, 223, 223)'],
        plotOptions: {
          bar: {
            borderRadius: 6,
            columnWidth: '55%',
            dataLabels: { position: 'top' },
          },
        },
        dataLabels: {
          enabled: true,
          offsetY: -22,
          style: { fontSize: '12px', colors: [foreColor] },
          formatter: (val: number) => `${val}%`,
        },
        xaxis: {
          categories: labels,
          labels: {
            style: { colors: muted, fontSize: '11px' },
          },
          axisBorder: { show: false },
          axisTicks: { show: false },
        },
        yaxis: {
          max: 100,
          tickAmount: 5,
          labels: {
            style: { colors: muted, fontSize: '11px' },
            formatter: (val: number) => `${Math.round(val)}%`,
          },
        },
        grid: {
          borderColor: isDarkMode ? 'rgba(148, 163, 184, 0.12)' : 'rgba(71, 85, 105, 0.15)',
          strokeDashArray: 4,
        },
        legend: { show: false },
        tooltip,
      };

      return {
        options,
        series: [{ name: 'Compliance', data: values }],
        apexType: 'bar',
      };
    }

    const sliceColors = labels.map((l) => colorForOutcomeLabel(l));

    const options: ApexOptions = {
      chart: { ...baseChart, type: chartType === 'doughnut' ? 'donut' : 'pie' },
      theme: { mode: isDarkMode ? 'dark' : 'light' },
      labels,
      colors: sliceColors,
      legend,
      dataLabels: {
        ...dataLabels,
        formatter: (_val: string | number, opts: { seriesIndex: number }) => {
          const v = opts != null ? Number(values[opts.seriesIndex] ?? 0) : 0;
          return v > 0 ? String(v) : '';
        },
      },
      plotOptions: {
        pie: {
          expandOnClick: false,
          donut: {
            size: chartType === 'doughnut' ? '68%' : '0%',
            labels: {
              show: chartType === 'doughnut',
              name: { color: foreColor },
              value: { color: foreColor, fontSize: '22px', fontWeight: 600 },
              total: {
                show: true,
                label: 'Total',
                color: muted,
                formatter: () => {
                  const sum = values.reduce((a, b) => a + b, 0);
                  return String(sum);
                },
              },
            },
          },
        },
      },
      stroke: { width: chartType === 'doughnut' ? 2 : 1, colors: ['transparent'] },
      tooltip,
    };

    return {
      options,
      series: values,
      apexType: chartType === 'doughnut' ? 'donut' : 'pie',
    };
  }, [chartType, foreColor, isDarkMode, labels, muted, values]);
}

export default function ComplianceChart({
  chartType,
  labels,
  values,
  isDarkMode = true,
}: ComplianceChartProps) {
  const { options, series, apexType } = useChartConfig(chartType, labels, values, isDarkMode);

  const isBarEmpty = chartType === 'bar' && labels.length === 0;
  const showRingEmpty =
    chartType !== 'bar' && labels.length > 0 && values.every((v) => v === 0);

  if (isBarEmpty) {
    return (
      <div
        className="compliance-chart chart-bar flex h-full min-h-[280px] w-full flex-col items-center justify-center gap-2 rounded-[var(--radius-2)] border border-dashed border-subtle/50 bg-surface-2/40 px-4 text-center text-sm text-muted"
        role="status"
        aria-live="polite"
      >
        <span className="font-medium text-text-strong">No trend data yet</span>
        <span className="max-w-xs text-muted">Complete at least one scan to see compliance over recent runs.</span>
      </div>
    );
  }

  if (showRingEmpty) {
    return (
      <div
        className="compliance-chart flex h-full min-h-[280px] w-full flex-col items-center justify-center gap-2 rounded-[var(--radius-2)] border border-dashed border-subtle/50 bg-surface-2/40 px-4 text-center text-sm text-muted"
        role="status"
        aria-live="polite"
      >
        <span className="font-medium text-text-strong">No control results</span>
        <span className="max-w-xs text-muted">Run a completed scan to populate this chart.</span>
      </div>
    );
  }

  return (
    <div
      className={`compliance-chart h-full w-full min-h-[280px] ${chartType === 'bar' ? 'chart-bar' : ''}`}
    >
      <Chart
        key={`${chartType}-${labels.join('|')}`}
        options={options}
        series={series}
        type={apexType}
        width="100%"
        height={340}
      />
    </div>
  );
}
