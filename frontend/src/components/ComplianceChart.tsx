import Chart from "react-apexcharts";
import type { ApexOptions } from "apexcharts";

type ChartType = "doughnut" | "pie" | "bar";

type ComplianceChartProps = {
  isDarkMode: boolean;
  sidebarWidth?: number;
  chartType: ChartType;
  labels: string[];
  values: number[];
};

export default function ComplianceChart({
  isDarkMode,
  chartType,
  labels,
  values,
}: ComplianceChartProps) {
  const safeLabels = labels.length > 0 ? labels : ["No data"];
  const safeValues = values.length > 0 ? values : [0];

  if (chartType === "bar") {
    const options: ApexOptions = {
      chart: {
        type: "bar",
        background: "transparent",
        toolbar: { show: false },
      },
      xaxis: {
        categories: safeLabels,
      },
      yaxis: {
        min: 0,
        max: 100,
      },
      theme: {
        mode: isDarkMode ? "dark" : "light",
      },
    };

    return (
      <Chart
        key="bar-chart"
        options={options}
        series={[{ name: "Compliance %", data: safeValues }]}
        type="bar"
        height={320}
      />
    );
  }

  const pieType = chartType === "doughnut" ? "donut" : "pie";

  const options: ApexOptions = {
    chart: {
      type: pieType,
      background: "transparent",
      toolbar: { show: false },
    },
    labels: safeLabels,
    theme: {
      mode: isDarkMode ? "dark" : "light",
    },
  };

  return (
    <Chart
      key={`${pieType}-chart`}
      options={options}
      series={safeValues}
      type={pieType}
      height={320}
    />
  );
}
