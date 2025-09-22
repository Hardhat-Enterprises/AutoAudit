-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tenants table (company being audited)
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    domain VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Runs (each scan instance)
CREATE TABLE audit_runs (
    id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES tenants(id) ON DELETE CASCADE,
    run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'in_progress'
);

-- Audit Findings (issues found in each run)
CREATE TABLE audit_findings (
    id SERIAL PRIMARY KEY,
    audit_run_id INT REFERENCES audit_runs(id) ON DELETE CASCADE,
    check_name VARCHAR(200),
    result VARCHAR(50), -- e.g. PASS/FAIL
    severity VARCHAR(50),
    details TEXT
);

-- Reports (summary of each run)
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    audit_run_id INT REFERENCES audit_runs(id) ON DELETE CASCADE,
    compliance_score INT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ===== Compliance DB: scans, issues, rules =====
CREATE TABLE IF NOT EXISTS tenants (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  external_tenant_id TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO tenants (name)
SELECT 'Default Tenant'
WHERE NOT EXISTS (SELECT 1 FROM tenants WHERE name='Default Tenant');

CREATE TABLE IF NOT EXISTS rules (
  id SERIAL PRIMARY KEY,
  framework VARCHAR(100) NOT NULL,    -- e.g. CIS_M365
  control_key VARCHAR(100) NOT NULL,   -- e.g. CIS-1.1
  title TEXT NOT NULL,
  severity VARCHAR(20),
  description TEXT,
  UNIQUE (framework, control_key)
);

CREATE TABLE IF NOT EXISTS scans (
  id SERIAL PRIMARY KEY,
  tenant_id INT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  started_at TIMESTAMP DEFAULT NOW(),
  finished_at TIMESTAMP,
  status VARCHAR(30) DEFAULT 'running',  -- running/completed/failed
  compliance_score NUMERIC(5,2),
  total_controls INT DEFAULT 0,
  passed_count INT DEFAULT 0,
  failed_count INT DEFAULT 0,
  not_tested_count INT DEFAULT 0,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS issues (
  id SERIAL PRIMARY KEY,
  scan_id INT NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
  rule_id INT REFERENCES rules(id) ON DELETE SET NULL,
  priority VARCHAR(20), -- high/medium/low
  title TEXT,
  description TEXT,
  result VARCHAR(20), -- pass/fail/error
  evidence JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
