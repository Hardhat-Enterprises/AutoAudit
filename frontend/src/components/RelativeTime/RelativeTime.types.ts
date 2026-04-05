import type { RelativeTimeLocale } from './relativeTimeFormat';

export type RelativeTimeProps = {
  value: string | number | Date | null | undefined;
  className?: string;
  /** How often to refresh the label (e.g. so “5 minutes ago” advances). */
  tickMs?: number;
  /** Passed to `Intl.RelativeTimeFormat` (defaults to runtime locale). */
  locale?: RelativeTimeLocale;
};
