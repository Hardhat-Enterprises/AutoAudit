export const normalizeEvidenceItems = (evidence: string | string[] | null | undefined): string[] => {
  if (!evidence) return [];

  const parts = Array.isArray(evidence)
    ? evidence
    : String(evidence)
        .split(/[\n;]+/)
        .map((item) => item.trim());

  return parts
    .map((item) => item.replace(/^[\s#*+\-•]+/, '').trim())
    .filter(Boolean);
};

export const formatEvidenceList = (evidence: string | string[] | null | undefined): string[] => normalizeEvidenceItems(evidence);

type ApiError = {
  message?: string;
  code?: string | number;
}

type ApiResponse = {
  errors?: ApiError[];
  has_errors?: boolean;
  detail?: string;
  message?: string;
  code?: string | number;
}

type ParsedError = {
  message: string;
  code: string | number | null;
  errors: ApiError[];
  hasErrors: boolean;
}

export const parseApiError = async (res: Response, fallback: string = 'Request failed'): Promise<ParsedError> => {
  try {
    const clone = res.clone();
    const data = (await clone.json()) as ApiResponse;
    const errors = Array.isArray(data?.errors) ? data.errors : [];
    const hasErrors = data?.has_errors ?? errors.length > 0;
    const message =
      errors[0]?.message ||
      data?.detail ||
      data?.message ||
      fallback;
    const code = data?.code || errors[0]?.code;
    return { message: message || fallback, code: code ?? null, errors, hasErrors };
  } catch (err) {
    try {
      const text = await res.text();
      return { message: text || fallback, code: null, errors: [], hasErrors: false };
    } catch (_) {
      return { message: fallback, code: null, errors: [], hasErrors: false };
    }
  }
};