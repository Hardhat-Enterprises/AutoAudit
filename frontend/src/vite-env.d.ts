/// <reference types="vite/client" />

type ImportMetaEnv = {
  readonly VITE_API_URL?: string;
  readonly VITE_EVIDENCE_API_BASE?: string;
  readonly VITE_EVIDENCE_API?: string;
}

type ImportMeta = {
  readonly env: ImportMetaEnv;
}
