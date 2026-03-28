type WebVitalMetric = {
  name: string;
  value: number;
  id: string;
};

type ReportHandler = (metric: WebVitalMetric) => void;

const reportWebVitals = (onPerfEntry?: ReportHandler): void => {
  if (typeof onPerfEntry !== "function") return;

  import("web-vitals")
    .then((webVitals) => {
      const wv = webVitals as Record<string, unknown>;

      const onCLS = wv.onCLS as ((cb: ReportHandler) => void) | undefined;
      const onINP = wv.onINP as ((cb: ReportHandler) => void) | undefined;
      const onFCP = wv.onFCP as ((cb: ReportHandler) => void) | undefined;
      const onLCP = wv.onLCP as ((cb: ReportHandler) => void) | undefined;
      const onTTFB = wv.onTTFB as ((cb: ReportHandler) => void) | undefined;

      const getCLS = wv.getCLS as ((cb: ReportHandler) => void) | undefined;
      const getFID = wv.getFID as ((cb: ReportHandler) => void) | undefined;
      const getFCP = wv.getFCP as ((cb: ReportHandler) => void) | undefined;
      const getLCP = wv.getLCP as ((cb: ReportHandler) => void) | undefined;
      const getTTFB = wv.getTTFB as ((cb: ReportHandler) => void) | undefined;

      (onCLS ?? getCLS)?.(onPerfEntry);
      (onINP ?? getFID)?.(onPerfEntry);
      (onFCP ?? getFCP)?.(onPerfEntry);
      (onLCP ?? getLCP)?.(onPerfEntry);
      (onTTFB ?? getTTFB)?.(onPerfEntry);
    })
    .catch(() => {
      // no-op
    });
};

export default reportWebVitals;